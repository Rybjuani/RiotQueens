"""Server-side conversation history store (in-process prototype).

This module owns the in-process conversation state for Companion Studio.
It is intentionally NOT a database; it is a prototype store suitable for
single-process FastAPI runtimes. The Protocol-based interface
(`ConversationStore`) is designed so a future PostgreSQL / Redis backend
can be swapped in without changing the chat handler or the router.

Hard scope rules (Issue #5)
---------------------------
1. A conversation is identified by the tuple
   ``(user_id, character_id, conversation_id)``. The store MUST NOT mix
   messages across different users, characters, or conversation ids.
2. The canonical Vane system prompt is NEVER stored here. It is prepended
   to every model request from `app/domain/companions.py` at request time.
3. Only validated assistant content actually returned to the user may be
   stored as an assistant turn. Provider failures (timeout, 429, 5xx,
   auth/config, connect, malformed, empty) MUST NOT append a fake turn.
4. History is bounded deterministically by `max_turns`
   (`COMPANION_CONVERSATION_MAX_TURNS`). The bound is applied to complete
   user/assistant pairs; truncation never leaves a half-pair.
5. Concurrent requests MUST NOT corrupt ordering. The in-process
   implementation uses an `asyncio.Lock` per scope key.
"""

from __future__ import annotations

import asyncio
import uuid
from collections.abc import AsyncIterator, Sequence
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Protocol

from .contracts import MessageInput


def _utcnow() -> datetime:
    """Return a timezone-aware UTC datetime."""
    return datetime.now(UTC)


class _ReentrantAsyncLock:
    """Small task-reentrant wrapper around ``asyncio.Lock``.

    The chat handler can hold one scope lock for the whole turn while
    store methods safely re-acquire the same lock inside that transaction.
    """

    def __init__(self) -> None:
        self._lock = asyncio.Lock()
        self._owner: asyncio.Task[object] | None = None
        self._depth = 0

    async def acquire(self) -> None:
        task = asyncio.current_task()
        if self._owner is task:
            self._depth += 1
            return
        await self._lock.acquire()
        self._owner = task
        self._depth = 1

    def release(self) -> None:
        task = asyncio.current_task()
        if self._owner is not task:
            raise RuntimeError("release() called by a task that does not own the lock")
        self._depth -= 1
        if self._depth == 0:
            self._owner = None
            self._lock.release()

    async def __aenter__(self) -> "_ReentrantAsyncLock":
        await self.acquire()
        return self

    async def __aexit__(self, *args: object) -> None:
        self.release()

    @property
    def is_locked(self) -> bool:
        return self._lock.locked()


@dataclass(frozen=True)
class ConversationScopeKey:
    """The triple that isolates one conversation from every other.

    Equality and hashing are based on the full tuple so the same
    ``(user_id, character_id, conversation_id)`` always maps to the same
    in-process entry. Different users / characters / conversation ids
    always map to different entries — there is no possibility of
    cross-scope mixing.
    """

    user_id: str
    character_id: str
    conversation_id: str


@dataclass
class StoredMessage:
    """A single persisted message in a conversation history.

    Only ``role`` values ``"user"`` and ``"assistant"`` are stored here.
    System prompts are never persisted — they are always re-prepended at
    request time from `companions.py`.
    """

    id: str
    role: str  # "user" | "assistant"
    content: str
    created_at: datetime = field(default_factory=_utcnow)


@dataclass
class ConversationRecord:
    """A full conversation snapshot, scoped by (user, character, conversation)."""

    user_id: str
    character_id: str
    conversation_id: str
    messages: list[StoredMessage] = field(default_factory=list)
    created_at: datetime = field(default_factory=_utcnow)
    updated_at: datetime = field(default_factory=_utcnow)


class ConversationStore(Protocol):
    """Swappable conversation persistence interface.

    The in-process implementation lives below; a future PostgreSQL or
    Redis-backed implementation can replace it without touching the chat
    handler or the router.
    """

    def transaction(self, scope: ConversationScopeKey) -> AsyncIterator[object]: ...

    async def append_user_message(
        self, scope: ConversationScopeKey, content: str
    ) -> StoredMessage: ...

    async def append_assistant_message(
        self, scope: ConversationScopeKey, content: str
    ) -> StoredMessage: ...

    async def get_history(self, scope: ConversationScopeKey) -> list[StoredMessage]: ...

    async def get_conversation(self, scope: ConversationScopeKey) -> ConversationRecord | None: ...

    async def delete_conversation(self, scope: ConversationScopeKey) -> bool: ...

    async def pop_last_user_message_if_match(
        self, scope: ConversationScopeKey, content: str
    ) -> bool: ...


def _split_pairs(
    messages: Sequence[StoredMessage],
) -> tuple[list[tuple[StoredMessage, StoredMessage]], StoredMessage | None]:
    pairs: list[tuple[StoredMessage, StoredMessage]] = []
    trailing_user: StoredMessage | None = None
    i = 0
    while i < len(messages):
        msg = messages[i]
        if msg.role == "user":
            if i + 1 < len(messages) and messages[i + 1].role == "assistant":
                pairs.append((msg, messages[i + 1]))
                i += 2
                continue
            trailing_user = msg
        i += 1
    return pairs, trailing_user


def _bound_pairs(messages: Sequence[StoredMessage], max_turns: int) -> list[StoredMessage]:
    """Return the last complete pairs plus an optional in-flight user turn."""
    if max_turns < 0:
        raise ValueError("max_turns must be >= 0")
    pairs, trailing_user = _split_pairs(messages)
    kept_pairs = [] if max_turns == 0 else pairs[-max_turns:]
    out: list[StoredMessage] = []
    for user, assistant in kept_pairs:
        out.extend((user, assistant))
    if trailing_user is not None:
        out.append(trailing_user)
    return out


def _prune_record(record: ConversationRecord, max_turns: int) -> None:
    """Bound the stored record itself, not only provider context."""
    bounded = _bound_pairs(record.messages, max_turns)
    if len(bounded) < len(record.messages):
        record.messages = bounded
        record.updated_at = _utcnow()


class InProcessConversationStore:
    """In-process implementation of `ConversationStore`.

    Holds conversation state in a plain dict keyed by `ConversationScopeKey`.
    Suitable for a single-process FastAPI deployment. Server restart
    clears all state — this is intentionally honest: it is NOT durable
    persistence.

    Concurrency: each scope key has its own `asyncio.Lock`. Different
    scopes never block each other; the same scope serializes its appends
    so concurrent chat requests to the same conversation cannot interleave
    their user/assistant turns out of order.
    """

    def __init__(self, max_turns: int = 8) -> None:
        if max_turns < 0:
            raise ValueError("max_turns must be >= 0")
        self._max_turns = max_turns
        self._records: dict[ConversationScopeKey, ConversationRecord] = {}
        self._locks: dict[ConversationScopeKey, _ReentrantAsyncLock] = {}

    def _lock_for(self, scope: ConversationScopeKey) -> _ReentrantAsyncLock:
        # Lazily create one lock per scope. Dict access is atomic under
        # the GIL for a single event loop, so this is safe for the
        # in-process prototype.
        lock = self._locks.get(scope)
        if lock is None:
            lock = _ReentrantAsyncLock()
            self._locks[scope] = lock
        return lock

    def _record_for(self, scope: ConversationScopeKey) -> ConversationRecord:
        rec = self._records.get(scope)
        if rec is None:
            rec = ConversationRecord(
                user_id=scope.user_id,
                character_id=scope.character_id,
                conversation_id=scope.conversation_id,
            )
            self._records[scope] = rec
        return rec

    @property
    def max_turns(self) -> int:
        return self._max_turns

    @asynccontextmanager
    async def transaction(self, scope: ConversationScopeKey) -> AsyncIterator[None]:
        """Serialize one complete chat turn for a conversation scope."""
        async with self._lock_for(scope):
            yield

    async def append_user_message(self, scope: ConversationScopeKey, content: str) -> StoredMessage:
        async with self._lock_for(scope):
            rec = self._record_for(scope)
            msg = StoredMessage(id=str(uuid.uuid4()), role="user", content=content)
            rec.messages.append(msg)
            rec.updated_at = _utcnow()
            return msg

    async def append_assistant_message(
        self, scope: ConversationScopeKey, content: str
    ) -> StoredMessage:
        async with self._lock_for(scope):
            rec = self._record_for(scope)
            msg = StoredMessage(id=str(uuid.uuid4()), role="assistant", content=content)
            rec.messages.append(msg)
            rec.updated_at = _utcnow()
            _prune_record(rec, self._max_turns)
            return msg

    async def get_history(self, scope: ConversationScopeKey) -> list[StoredMessage]:
        """Return the bounded history for a scope.

        The returned list contains at most ``max_turns`` complete
        user/assistant pairs, plus an optional trailing unpaired user
        message if a request is currently in flight. The canonical
        system prompt is NEVER included here — it is re-prepended at
        request time by `assemble_request` in `context.py`.
        """
        async with self._lock_for(scope):
            rec = self._records.get(scope)
            if rec is None:
                return []
            # Copy the list under the lock so concurrent appends cannot
            # mutate it while we are slicing.
            snapshot = list(rec.messages)
        return _bound_pairs(snapshot, self._max_turns)

    async def get_conversation(self, scope: ConversationScopeKey) -> ConversationRecord | None:
        async with self._lock_for(scope):
            rec = self._records.get(scope)
            if rec is None:
                return None
            # Return a deep copy so external callers cannot mutate state.
            return ConversationRecord(
                user_id=rec.user_id,
                character_id=rec.character_id,
                conversation_id=rec.conversation_id,
                messages=list(rec.messages),
                created_at=rec.created_at,
                updated_at=rec.updated_at,
            )

    async def delete_conversation(self, scope: ConversationScopeKey) -> bool:
        """Delete a conversation by scope.

        Returns True if a conversation existed and was deleted, False if
        there was nothing to delete. Other conversations (different user /
        character / conversation_id) are NOT touched.
        """
        async with self._lock_for(scope):
            existed = scope in self._records
            if existed:
                del self._records[scope]
            return existed

    async def pop_last_user_message_if_match(
        self, scope: ConversationScopeKey, content: str
    ) -> bool:
        """Rollback helper for provider-failure state integrity (Issue #5).

        If the last stored message in this scope is a ``user`` message
        with the given ``content``, remove it and return True. Otherwise
        return False and leave the history untouched.

        This is the ONLY mutation path that removes a stored message.
        It is used by the chat handler when the provider raises a typed
        error: the user message we appended just before the call is
        popped so history is left in the state it was BEFORE the failed
        request. A subsequent retry re-appends the same user message
        and, if the provider succeeds, appends a clean assistant turn
        — producing a complete (user, assistant) pair with no leftover
        failed half-turn.

        The content match is defensive: if some other request appended
        a different user message in between (which the per-scope lock
        should prevent at the append level), we don't pop that one.
        """
        async with self._lock_for(scope):
            rec = self._records.get(scope)
            if rec is None or not rec.messages:
                return False
            last = rec.messages[-1]
            if last.role == "user" and last.content == content:
                rec.messages.pop()
                rec.updated_at = _utcnow()
                _prune_record(rec, self._max_turns)
                return True
            return False


    async def _raw_record(self, scope: ConversationScopeKey) -> ConversationRecord | None:
        """Test-only deep-copy view of the underlying bounded stored record."""
        async with self._lock_for(scope):
            rec = self._records.get(scope)
            if rec is None:
                return None
            return ConversationRecord(
                user_id=rec.user_id,
                character_id=rec.character_id,
                conversation_id=rec.conversation_id,
                messages=list(rec.messages),
                created_at=rec.created_at,
                updated_at=rec.updated_at,
            )


def stored_to_message_input(msg: StoredMessage) -> MessageInput:
    """Convert a `StoredMessage` to a `MessageInput` for the provider request.

    Only ``"user"`` and ``"assistant"`` roles are stored, so this is always
    safe. The MessageInput contract enforces the same role pattern.
    """
    return MessageInput(role=msg.role, content=msg.content)


__all__ = [
    "ConversationRecord",
    "ConversationScopeKey",
    "ConversationStore",
    "InProcessConversationStore",
    "StoredMessage",
    "stored_to_message_input",
]
