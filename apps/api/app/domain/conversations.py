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
from collections.abc import Sequence
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Protocol

from .contracts import MessageInput


def _utcnow() -> datetime:
    """Return a timezone-aware UTC datetime."""
    return datetime.now(UTC)


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


def _bound_pairs(messages: Sequence[StoredMessage], max_turns: int) -> list[StoredMessage]:
    """Return the most recent ``max_turns`` complete user/assistant pairs.

    The bound is applied to PAIRS, not individual messages, so truncation
    never leaves a dangling user message without its assistant reply (or
    vice versa). If the history ends with a single user turn (because the
    assistant turn has not been appended yet, which happens during a
    request), that trailing user turn is preserved on top of the bounded
    pair window.

    Parameters
    ----------
    messages
        The full ordered history (oldest first). Only ``"user"`` and
        ``"assistant"`` roles are expected here.
    max_turns
        Maximum number of complete user/assistant pairs to keep. Must be
        ``>= 0``. ``0`` means "no pairs returned" (the trailing unpaired
        user turn, if any, is still preserved so the current request can
        be sent).
    """
    if max_turns < 0:
        raise ValueError("max_turns must be >= 0")
    if not messages:
        return []

    # Walk the message list and split it into (user, assistant) pairs +
    # an optional trailing unpaired user message.
    pairs: list[tuple[StoredMessage, StoredMessage]] = []
    trailing_user: StoredMessage | None = None
    i = 0
    while i < len(messages):
        msg = messages[i]
        if msg.role == "user":
            # Look ahead for a paired assistant message.
            if i + 1 < len(messages) and messages[i + 1].role == "assistant":
                pairs.append((msg, messages[i + 1]))
                i += 2
                continue
            # No paired assistant → this is the trailing user turn of an
            # in-flight request. Preserve it so the current request can
            # still include the just-appended user message.
            trailing_user = msg
            i += 1
        elif msg.role == "assistant":
            # An assistant message without a preceding user (shouldn't
            # happen given the append order, but be defensive). Skip it
            # — incomplete pair, can't form context.
            i += 1
        else:
            # Unknown role. Defensive skip.
            i += 1

    # Apply the bound to the PAIRS only.
    if max_turns == 0:
        kept_pairs: list[tuple[StoredMessage, StoredMessage]] = []
    else:
        kept_pairs = pairs[-max_turns:]

    out: list[StoredMessage] = []
    for u, a in kept_pairs:
        out.append(u)
        out.append(a)
    if trailing_user is not None:
        # Always keep the in-flight user turn even when max_turns=0 so
        # the current request can be sent (Issue #5: "first message
        # stores user turn, sends [system, user]").
        out.append(trailing_user)
    return out


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
        self._locks: dict[ConversationScopeKey, asyncio.Lock] = {}

    def _lock_for(self, scope: ConversationScopeKey) -> asyncio.Lock:
        # Lazily create one lock per scope. Dict access is atomic under
        # the GIL for a single event loop, so this is safe for the
        # in-process prototype.
        lock = self._locks.get(scope)
        if lock is None:
            lock = asyncio.Lock()
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
                # Drop the lock too so the dict doesn't grow forever.
                self._locks.pop(scope, None)
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
                return True
            return False


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
