"""Server-side context assembly for multi-turn conversation + memory.

This module is the single place that decides what `messages` list the
provider receives. It composes the request in this STRICT order:

    1. Canonical Queen system prompt (`companions.get_system_prompt`)
       — server-owned, re-prepended on EVERY request, NEVER stored.
    2. Server-owned memory context (`memories.memory_context_section`)
       — built from scoped explicit user facts, as a SEPARATE system
       block, never mixed into the Queen prompt.
    3. Bounded conversation history (`conversations.get_history`)
       — prior user + assistant turns, scoped by
       (user_id, character_id, conversation_id). Bound by
       `COMPANION_CONVERSATION_MAX_TURNS` (complete pairs only).
    4. Current user message (`ChatRequest.message`).

The frontend NEVER sends a system prompt, never sends trusted prior
messages, never sends trusted memories. The browser only sends the
current message and the scope identifiers. The server rebuilds the
full canonical context from its own state.

State integrity (Issue #5)
---------------------------
- The user message is appended to the conversation store BEFORE the
  provider is called. If the provider fails (timeout / 429 / 5xx /
  auth / connect / malformed), the chat handler MUST roll back the
  user message so no half-turn pollutes history. The handler does this
  explicitly via `pop_last_user_message` — see `conversations.py` for
  the rollback helper.

  Wait — actually, rolling back the user message is wrong: if the
  client retries the same message, we would store the user message
  twice. The CORRECT integrity model is:

    - Append the user message to the store BEFORE calling the provider.
    - Call the provider. If it raises, the user message stays in the
      store (it represents what the user actually said), but NO
      assistant turn is appended. The next request from the user
      will rebuild history with that trailing user message — and
      `_bound_pairs` preserves a trailing unpaired user turn, so the
      next request will re-send it as context.

      Actually that's also wrong — if the user retries with a DIFFERENT
      message, we don't want the failed one lingering as the last turn.

    The simplest correct model is:
      - Append user message BEFORE provider call.
      - If provider succeeds → append assistant turn, done.
      - If provider fails → pop the user message we just appended, so
        history is left in the state it was BEFORE this request. The
        user can retry; if they retry with the same message, the
        re-append produces a clean (user, assistant) pair on success.
        If they retry with a different message, there's no leftover
        failed turn.

  This is the model implemented here. `pop_last_user_message_if_match`
  removes the last message if and only if it is a user message with
  the given content (defensive — if some other concurrent request
  appended a different user message in between, we don't pop that
  one).

Actually, given the per-scope `asyncio.Lock` in the conversation
store, two concurrent requests to the same conversation are
serialized at the append level. So the simpler model is:

  - Append user message under lock.
  - Call provider (outside the conversation lock — provider call is
    slow).
  - If provider succeeds → append assistant turn under lock.
  - If provider fails → pop the trailing user message under lock
    (only if it matches the content we appended).

This keeps history clean: a failed request leaves no trace, so the
next retry starts from the same state. The pop helper is in
`conversations.py` as `pop_last_user_message_if_match`.
"""

from __future__ import annotations

from .companions import get_system_prompt
from .contracts import MessageInput, ModelRequest, Route
from .conversations import (
    ConversationScopeKey,
    ConversationStore,
    stored_to_message_input,
)
from .memories import MemoryScopeKey, MemoryStore, memory_context_section


async def assemble_request_messages(
    *,
    character_id: str,
    user_id: str,
    conversation_id: str,
    current_message: str,
    route: Route,
    conversation_store: ConversationStore,
    memory_store: MemoryStore,
) -> list[MessageInput]:
    """Build the canonical `messages` list for a model request.

    Order is fixed:
      1. Canonical Queen system prompt (server-owned, never stored).
      2. Server-owned memory context (separate system block, only if
         the user has explicit memories).
      3. Bounded conversation history (prior user/assistant turns).
      4. Current user message.

    The current user message is appended to the conversation store
    BEFORE this function is called (by the chat handler), so the
    bounded history returned by `conversation_store.get_history` will
    include it as the trailing user turn. This function does NOT append
    it again — it relies on the history snapshot.
    """
    messages: list[MessageInput] = []

    # 1. Canonical Queen system prompt.
    system_prompt = get_system_prompt(character_id)
    if system_prompt:
        messages.append(MessageInput(role="system", content=system_prompt))

    # 2. Server-owned memory context (separate system block).
    memory_scope = MemoryScopeKey(user_id=user_id, character_id=character_id)
    memories = await memory_store.list_memories(memory_scope)
    memory_section = memory_context_section(memories)
    if memory_section is not None:
        messages.append(MessageInput(role="system", content=memory_section))

    # 3. Bounded conversation history (includes the trailing current
    #    user message that was just appended by the chat handler).
    conversation_scope = ConversationScopeKey(
        user_id=user_id,
        character_id=character_id,
        conversation_id=conversation_id,
    )
    history = await conversation_store.get_history(conversation_scope)
    for stored in history:
        messages.append(stored_to_message_input(stored))

    # Defensive: if the current user message was somehow not in the
    # bounded history (e.g. max_turns=0 and the trailing-user
    # preservation was bypassed), append it explicitly so the request
    # always carries the user's current message.
    if not _ends_with_user_message(messages, current_message):
        messages.append(MessageInput(role="user", content=current_message))

    return messages


def _ends_with_user_message(messages: list[MessageInput], content: str) -> bool:
    """Return True if the last message is a user message with this content."""
    if not messages:
        return False
    last = messages[-1]
    return last.role == "user" and last.content == content


def build_model_request(
    *,
    route: Route,
    character_id: str,
    user_id: str,
    conversation_id: str,
    messages: list[MessageInput],
) -> ModelRequest:
    """Construct a `ModelRequest` from the assembled messages.

    The `memories` field on `ModelRequest` is left empty in this
    milestone — memories are injected as a dedicated system message
    block, NOT through the legacy `memories` list field. This keeps
    the memory context visible to the OpenAI-compatible provider's
    chat-completions API (which only understands `messages`).
    """
    return ModelRequest(
        route=route,
        character_id=character_id,
        user_id=user_id,
        conversation_id=conversation_id,
        messages=messages,
    )


__all__ = [
    "assemble_request_messages",
    "build_model_request",
]
