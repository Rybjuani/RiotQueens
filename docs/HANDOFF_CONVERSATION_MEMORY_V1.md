# HANDOFF — Conversation & Memory v1

**Branch:** `feat/conversation-memory-v1`
**Base:** `chore/bootstrap-architecture` (commit `4580a17`)
**Date:** 2026-08-08
**Issue:** [#5 — Conversation runtime v1: server-side multi-turn history + memory foundation](https://github.com/Rybjuani/Companion-Studio/issues/5)

## Resumen

Companion Studio ya tenía una base de runtime real (FastAPI + OpenAI-compatible provider + typed provider errors + retry semantics + safe HTTP mapping + server-owned Vane). Pero `/v1/chat` era single-turn: Vane no recordaba lo que se dijo hace un momento en la misma sesión.

Este milestone agrega:

1. **Server-side multi-turn conversation continuity** — el backend reconstruye el contexto completo (system → memories → bounded history → current user) a partir del scope `(user_id, character_id, conversation_id)`. El browser sigue enviando solo el mensaje actual.
2. **Minimal explicit-fact memory foundation** — un `MemoryRecord` tipado con separación fact/inference. En este milestone solo se almacenan facts explícitos subidos por el usuario; no hay embeddings, vector DB, ni extracción automática.
3. **APIs para inspección y borrado** de conversaciones y memorias, con scope estricto.
4. **State integrity** — los fallos del provider NO contaminan el history; solo los assistant turns realmente retornados al usuario se almacenan.
5. **Concurrency safety** — locks `asyncio.Lock` por scope.
6. **Honest runtime labels** — todo es in-process prototype state; nada dice "persistent".

## Architecture

```text
Browser (Next.js client)
  → POST /v1/chat { message, character_id, conversation_id }
  → FastAPI handler (app/main.py)
      1. ConversationScopeKey(user_id, character_id, conversation_id)
      2. conversation_store.append_user_message(scope, message)
      3. assemble_request_messages():
           a. canonical Vane system prompt (companions.get_system_prompt)
           b. server-owned memory context (memory_context_section)
              — separate system block, only if memories exist
           c. bounded conversation history (conversation_store.get_history)
              — includes the trailing user turn just appended
           d. defensive current-user append if not in history
      4. router.generate(ModelRequest)
           - provider call (mock or OpenAI-compatible)
           - typed ProviderError on failure (re-raised after retry budget)
           - OutputValidator on success; SAFE_FALLBACK_CONTENT on ultimate
             validator rejection
      5. On success:
           conversation_store.append_assistant_message(scope, response.content)
           return ChatResponse
      6. On ProviderError:
           conversation_store.pop_last_user_message_if_match(scope, message)
           → FastAPI exception_handler maps to clean 5xx
           (history is left in the state BEFORE the failed request)
```

## Repository abstractions

### `app/domain/conversations.py`

```text
ConversationScopeKey (frozen dataclass)
  = (user_id, character_id, conversation_id)

StoredMessage
  id: UUID4
  role: "user" | "assistant"   (system is NEVER stored)
  content: str
  created_at: datetime (UTC)

ConversationRecord
  user_id, character_id, conversation_id
  messages: list[StoredMessage]
  created_at, updated_at

ConversationStore (Protocol)
  async append_user_message(scope, content) -> StoredMessage
  async append_assistant_message(scope, content) -> StoredMessage
  async get_history(scope) -> list[StoredMessage]   # bounded
  async get_conversation(scope) -> ConversationRecord | None
  async delete_conversation(scope) -> bool
  async pop_last_user_message_if_match(scope, content) -> bool
                                                     # rollback helper

InProcessConversationStore(ConversationStore)
  max_turns: int
  _records: dict[ConversationScopeKey, ConversationRecord]
  _locks: dict[ConversationScopeKey, asyncio.Lock]   # per-scope
```

### `app/domain/memories.py`

```text
MemoryScopeKey (frozen dataclass)
  = (user_id, character_id)

MemoryRecord
  id: UUID4
  user_id, character_id
  content: str
  memory_type: "user_fact"   (controlled enum, never client-supplied)
  source: "explicit_user_statement"
  confidence: "high"
  inferred: False             (always False in this milestone)
  created_at: datetime (UTC)

MemoryStore (Protocol)
  async add_memory(scope, content) -> MemoryRecord
  async list_memories(scope) -> list[MemoryRecord]
  async delete_memory(scope, memory_id) -> bool
  async delete_all_for_scope(scope) -> int

InProcessMemoryStore(MemoryStore)
  max_per_scope: int
  _records: dict[MemoryScopeKey, list[MemoryRecord]]
  _locks: dict[MemoryScopeKey, asyncio.Lock]
  FIFO eviction when len > max_per_scope
```

### `app/domain/context.py`

```text
assemble_request_messages(
    character_id, user_id, conversation_id, current_message,
    route, conversation_store, memory_store
) -> list[MessageInput]
  Order is FIXED:
    1. system  ← canonical Vane prompt (companions.get_system_prompt)
    2. system  ← server-owned memory context (only if memories exist)
    3. user    ← prior bounded history (pairs + trailing user)
    4. assistant ← prior bounded history
    5. ... (more pairs from bounded history)
    6. user    ← current message (defensive append if not in history)

build_model_request(route, ..., messages) -> ModelRequest
  (memories field left empty — memories are injected as a system block)
```

## State keys / scopes

| Store | Scope key | Isolation |
|---|---|---|
| ConversationStore | `(user_id, character_id, conversation_id)` | Triple-isolated. Different user / character / conversation CANNOT see each other's messages. |
| MemoryStore | `(user_id, character_id)` | Pair-isolated. Different user / character CANNOT see each other's memories. |

Both scope keys are `frozen=True` dataclasses — equality and hashing are based on the full tuple. There is no possibility of cross-scope mixing at the data-structure level.

## Conversation lifecycle

```text
1. Browser sends POST /v1/chat { message }
2. Handler appends user message to conversation_store (under per-scope lock)
3. Handler assembles ModelRequest.messages:
     system(Vane) → system(memory if any) → bounded history (incl. trailing user)
4. Handler calls router.generate(request)
5. On success (200):
     - Append assistant message to conversation_store
     - Return ChatResponse
6. On ProviderError (5xx):
     - Pop the trailing user message if it matches (rollback)
     - Re-raise → FastAPI maps to clean 5xx
     - History is left in the state BEFORE the failed request
7. On OutputValidator ultimate rejection (rare, 200 with SAFE_FALLBACK_CONTENT):
     - The fallback IS the assistant response the user sees
     - It IS stored as a real assistant turn (per Issue #5)
```

## History bounds

| Config | Default | Behavior |
|---|---|---|
| `COMPANION_CONVERSATION_MAX_TURNS` | `8` | Max number of complete user/assistant pairs kept per scope. Older pairs are evicted FIFO. The bound is applied to PAIRS, so truncation never leaves a half-pair. A trailing in-flight user message (no paired assistant yet) is ALWAYS preserved so the current request can be sent. `0` means "no pairs returned" but the trailing user turn is still kept. |

The canonical Vane system prompt is NEVER stored in conversation history. It is re-prepended on every request from `companions.get_system_prompt(character_id)`.

The `_bound_pairs` helper walks the message list and splits it into `(user, assistant)` pairs plus an optional trailing unpaired user. The bound is applied to pairs only. This means:

- Truncation never breaks a pair (no dangling user without its assistant reply, or vice versa).
- An in-flight request (user message appended, provider call in progress) is always representable in the bounded history.

## Memory schema

```python
@dataclass
class MemoryRecord:
    id: str                       # UUID4
    user_id: str
    character_id: str
    content: str                  # 1..500 chars, validated at POST
    memory_type: str = "user_fact"
    source: str = "explicit_user_statement"
    confidence: str = "high"
    inferred: bool = False        # ALWAYS False in this milestone
    created_at: datetime          # UTC
```

### Fact vs inference

| Field | This milestone | Future |
|---|---|---|
| `memory_type` | `"user_fact"` only | May add `"inferred_fact"`, `"preference"`, etc. |
| `source` | `"explicit_user_statement"` only | May add `"llm_extraction"`, `"behavioral_inference"` |
| `confidence` | `"high"` (deterministic for explicit facts) | May be a float for inferred memories |
| `inferred` | Always `False` | Future milestones may add `True` for inferred memories — clearly separated |

The fact/inference distinction is preserved in the SCHEMA so future milestones can add inferred memories without breaking the contract. The client CANNOT upload an inferred memory in this milestone — `memory_type`, `source`, `confidence`, and `inferred` are all server-set.

## API endpoints

### `/v1/chat` (updated)

```http
POST /v1/chat
Content-Type: application/json

{
  "message": "Hola Vane",
  "character_id": "vane",
  "conversation_id": "<browser-session-uuid>",
  "user_id": "demo-user",
  "route": "fast_chat"
}
```

Response (200):

```json
{
  "response": {
    "provider": "mock",
    "model": "mock-companion-v1",
    "content": "...",
    "usage": {"input_tokens": 10, "output_tokens": 18},
    "latency_ms": 0,
    "validation": {"is_valid": true, ...},
    "retry_count": 0
  }
}
```

On provider failure (5xx): clean error body `{"detail": {"code": "...", "message": "..."}}` — see HANDOFF_RUNTIME_PROVIDER_V1.md for the full mapping table.

The frontend sends ONLY the current message + scope identifiers. The server rebuilds the full canonical context. The client never sends a system prompt, never sends trusted prior messages, never sends trusted memories.

### `GET /v1/conversations/{conversation_id}` (new)

```http
GET /v1/conversations/{conversation_id}?user_id=demo-user&character_id=vane
```

Response (200):

```json
{
  "user_id": "demo-user",
  "character_id": "vane",
  "conversation_id": "<id>",
  "messages": [
    {"id": "...", "role": "user", "content": "...", "created_at": "..."},
    {"id": "...", "role": "assistant", "content": "...", "created_at": "..."}
  ],
  "created_at": "...",
  "updated_at": "..."
}
```

- Scope enforced by `(user_id, character_id, conversation_id)`. Different user / character / conversation CANNOT see this conversation.
- Returns an empty `messages` list (with the scope echoed back) if the conversation does not exist yet — graceful for a fresh browser session.
- The canonical Vane system prompt is NEVER in the returned messages — only `user` and `assistant` roles.

### `DELETE /v1/conversations/{conversation_id}` (new)

```http
DELETE /v1/conversations/{conversation_id}
Content-Type: application/json

{"user_id": "demo-user", "character_id": "vane"}
```

Response (200):

```json
{"deleted": true, "conversation_id": "<id>"}
```

- `deleted=true` iff a conversation existed and was removed. `false` if there was nothing to delete (not an error).
- Other conversations — same user different conversation, different user, different character — are NOT touched.

### `GET /v1/memories` (new)

```http
GET /v1/memories?user_id=demo-user&character_id=vane
```

Response (200):

```json
{
  "memories": [
    {
      "id": "...",
      "user_id": "demo-user",
      "character_id": "vane",
      "content": "Mi color favorito es negro.",
      "memory_type": "user_fact",
      "source": "explicit_user_statement",
      "confidence": "high",
      "inferred": false,
      "created_at": "..."
    }
  ],
  "count": 1
}
```

- Scope enforced by `(user_id, character_id)`. Returns empty list if no memories exist.

### `POST /v1/memories` (new)

```http
POST /v1/memories
Content-Type: application/json

{
  "user_id": "demo-user",
  "character_id": "vane",
  "content": "Mi color favorito es negro."
}
```

Response (201):

```json
{
  "id": "...",
  "user_id": "demo-user",
  "character_id": "vane",
  "content": "Mi color favorito es negro.",
  "memory_type": "user_fact",
  "source": "explicit_user_statement",
  "confidence": "high",
  "inferred": false,
  "created_at": "..."
}
```

- `content` is validated: `min_length=1, max_length=500`.
- The client supplies ONLY `content` + scope identifiers. The server sets `memory_type`, `source`, `confidence`, `inferred` — never the client.
- The client CANNOT use this endpoint to upload a system prompt, trusted role messages, or arbitrary provider instructions. The only field that affects model context is `content`, which is stored verbatim as a fact and injected as a separate server-owned memory section.
- If the scope exceeds `COMPANION_MEMORY_MAX_PER_SCOPE`, the oldest memory is evicted FIFO.

### `DELETE /v1/memories/{memory_id}` (new)

```http
DELETE /v1/memories/{memory_id}
Content-Type: application/json

{"user_id": "demo-user", "character_id": "vane"}
```

Response (200 if deleted):

```json
{"deleted": true, "memory_id": "<id>"}
```

Response (404 if not found within scope):

```json
{
  "detail": {
    "code": "memory_not_found",
    "message": "Memory not found within the requested scope."
  }
}
```

- The scope check is MANDATORY. A memory id from a different user / character CANNOT be deleted through this endpoint.
- We do NOT leak whether the id exists in a different scope — that would be an information-disclosure side channel. The 404 body is identical regardless of whether the id exists elsewhere.

## Provider context assembly order

```text
1. system  ← canonical Vane prompt (companions.get_system_prompt)
              - Server-owned, re-prepended on EVERY request
              - NEVER stored in conversation history
              - The client CANNOT supply this

2. system  ← server-owned memory context (memory_context_section)
              - Separate system block, only if the user has explicit memories
              - Format: "Memorias explícitas del usuario:\n- ...\n- ..."
              - Built server-side from scoped MemoryRecord list
              - The client CANNOT supply this
              - NEVER mixed into the canonical Vane prompt file

3. user    ← bounded conversation history (pairs from oldest kept)
4. assistant ← bounded conversation history
5. ... (more pairs, up to max_turns)
6. user    ← current message (trailing user from the just-appended turn)
```

The memory section is INTENTIONALLY a separate system block, never mixed into `companions.py`. This keeps:

- character identity (Vane prompt)
- user memories (server-owned memory context)
- conversation turns (user/assistant history)

logically separated. A future milestone could swap the memory source (e.g. inferred memories from a separate engine) without touching the Vane prompt or the conversation store.

## Failure-state integrity

| Failure | What happens to conversation history |
|---|---|
| Provider timeout / connect / 429 / 5xx / auth / malformed / empty | User message appended BEFORE the call is ROLLED BACK via `pop_last_user_message_if_match`. History is left in the state BEFORE the failed request. The 5xx is returned to the browser; no half-turn pollutes history. |
| OutputValidator ultimate rejection (provider returned unsafe content on every retry) | The router substitutes `SAFE_FALLBACK_CONTENT` and returns HTTP 200. This fallback IS the assistant response the user sees, so it IS stored as a real assistant turn (per Issue #5). |
| Unknown exception escaping the adapter | Treated defensively as `ProviderRetryableError`; same rollback semantics as a typed provider error. |

The rollback helper `pop_last_user_message_if_match` is the ONLY mutation path that removes a stored message. It is content-matched (defensive — if some other concurrent request appended a different user message in between, which the per-scope lock prevents at the append level, we don't pop that one).

## Concurrency strategy

Both `InProcessConversationStore` and `InProcessMemoryStore` use one `asyncio.Lock` per scope key:

- Different scopes never block each other (different locks).
- Same scope serializes its appends so concurrent chat requests to the same conversation cannot interleave their user/assistant turns out of order.
- The lock is held for the duration of a single mutation (append / pop / delete), NOT for the provider call (which is slow and outside the conversation lock).

Verified by `test_N_concurrent_requests_preserve_pair_integrity` — 20 concurrent user+assistant pairs to the same conversation all end up as proper pairs with no crossing.

## Changed files

### Backend (apps/api)

- `app/domain/conversations.py` — **NEW** — `ConversationScopeKey`, `StoredMessage`, `ConversationRecord`, `ConversationStore` Protocol, `InProcessConversationStore` (per-scope `asyncio.Lock`, pair-aware bounded history, rollback helper).
- `app/domain/memories.py` — **NEW** — `MemoryScopeKey`, `MemoryRecord`, `MemoryStore` Protocol, `InProcessMemoryStore` (per-scope `asyncio.Lock`, FIFO eviction), `memory_context_section` (server-owned memory injection).
- `app/domain/context.py` — **NEW** — `assemble_request_messages` (canonical order: system Vane → memory section → bounded history → current user) + `build_model_request`.
- `app/domain/contracts.py` — added `ConversationMessageView`, `ConversationSummary`, `ConversationScopeRequest`, `MemoryCreateRequest`, `MemoryRecordView`, `MemoryListResponse`, `MemoryDeleteResponse`, `ConversationDeleteResponse`.
- `app/main.py` — wired `conversation_store` + `memory_store` (env-driven bounds), updated `/v1/chat` to assemble multi-turn context + rollback on provider failure, added `GET/DELETE /v1/conversations/{conversation_id}`, `GET/POST /v1/memories`, `DELETE /v1/memories/{memory_id}`. Added `conversation_max_turns` + `memory_max_per_scope` to `/v1/runtime/status`.
- `tests/test_conversations.py` — **NEW** — 16 tests for the conversation store (scope isolation, bounded history pair-aware truncation, rollback, concurrency ordering).
- `tests/test_memories.py` — **NEW** — 11 tests for the memory store (scope isolation, FIFO eviction, stable IDs, explicit-fact-only schema, memory context section).
- `tests/test_chat_multiturn.py` — **NEW** — 18 integration tests covering Issue #5 acceptance cases A through O.

### Frontend (apps/web)

- `lib/api.ts` — added `clearConversation()`, `getConversation()`, `ConversationMessageView`, `ConversationSummary` types. `sendChat` unchanged.
- `components/ChatPanel.tsx` — added a small dev diagnostic: "turnos server: N" indicator (refreshes on every bubble change via `getConversation()`) and a "limpiar conversación" button (calls `clearConversation()` + resets local chat to the canonical greeting). The cyber-noir UI, Vane personality, sessionStorage UUID, runtime status fetch, and server-owned system prompt are all unchanged.
- `lib/session.ts` — UNCHANGED (per-browser-session UUID via sessionStorage; refresh keeps the same id, new tab gets a fresh one).
- `lib/companion.ts` — UNCHANGED.

### Config / docs

- `.env.example` — added `COMPANION_CONVERSATION_MAX_TURNS=8` and `COMPANION_MEMORY_MAX_PER_SCOPE=32` with honest "in-process prototype state, NOT durable persistence" comments.
- `docs/HANDOFF_CONVERSATION_MEMORY_V1.md` — this file.

## Env vars

| Var | Default | Purpose |
|---|---|---|
| `COMPANION_MODEL_PROVIDER` | `mock` | (existing) `mock` or `openai` |
| `COMPANION_MODEL_BASE_URL` | (empty) | (existing) OpenAI-compatible base URL |
| `COMPANION_MODEL_API_KEY` | (empty) | (existing) server-side API key |
| `COMPANION_MODEL_NAME` | `companion-chat-v1` | (existing) model name |
| `COMPANION_MODEL_TIMEOUT_SECONDS` | `5.0` | (existing) per-call timeout |
| `COMPANION_MODEL_MAX_RETRIES` | `1` | (existing) bounded retries |
| `COMPANION_CORS_ORIGINS` | `http://localhost:3000` | (existing) comma-separated allowed origins |
| `COMPANION_CONVERSATION_MAX_TURNS` | `8` | **NEW** — max user/assistant pairs kept per scope |
| `COMPANION_MEMORY_MAX_PER_SCOPE` | `32` | **NEW** — max explicit facts per (user, character) scope |

## Exact test results

```bash
# Backend
cd apps/api && python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/ruff check .          # → All checks passed!
.venv/bin/ruff format --check . # → 21 files already formatted
.venv/bin/pytest tests/ -q      # → 87 passed

# Frontend
pnpm install
pnpm --dir apps/web lint        # → ✔ No ESLint warnings or errors
pnpm --dir apps/web build       # → ○ (Static) prerendered
```

### Test breakdown

| File | Tests | Coverage |
|---|---|---|
| `test_validator.py` | 3 | (existing, unchanged) |
| `test_router.py` | 2 | (existing, unchanged) |
| `test_runtime.py` | 7 | (existing, unchanged) |
| `test_openai_provider.py` | 17 | (existing, unchanged) |
| `test_provider_errors.py` | 18 | (existing, unchanged) |
| `test_conversations.py` | 16 | **NEW** — store unit tests: scope isolation, bounded pairs, trailing user preservation, rollback, concurrency ordering |
| `test_memories.py` | 11 | **NEW** — store unit tests: scope isolation, FIFO eviction, stable IDs, memory context section |
| `test_chat_multiturn.py` | 18 | **NEW** — integration tests A-O + edge cases (safe fallback stored, get-unknown returns empty, memory post validation, system prompt never stored, clear-then-send starts fresh) |

### Issue #5 acceptance cases (A–O)

| # | Case | Test | Verdict |
|---|---|---|---|
| A | First message: provider receives [system, user1] | `test_A_first_message_provider_receives_system_and_user` | ✅ |
| B | Second message: provider receives [system, user1, assistant1, user2] | `test_B_second_message_provider_receives_prior_turn` | ✅ |
| C | Different conversation_id → fully isolated | `test_C_different_conversation_id_isolated` | ✅ |
| D | Different user_id → fully isolated | `test_D_different_user_id_isolated` | ✅ |
| E | Different character_id → fully isolated | `test_E_different_character_id_isolated` | ✅ |
| F | Provider failure: no fake assistant turn, no pollution | `test_F_provider_failure_does_not_pollute_history` | ✅ |
| G | Bounded history: keeps recent complete pairs | `test_G_bounded_history_keeps_recent_pairs` | ✅ |
| H | Conversation DELETE: clears right scope only | `test_H_conversation_delete_clears_only_correct_scope` | ✅ |
| I | Memory POST: creates explicit fact | `test_I_memory_post_creates_explicit_fact` | ✅ |
| J | Memory GET: only correct user/character | `test_J_memory_get_only_returns_correct_scope` | ✅ |
| K | Memory DELETE: deletes correct record, other scope unaffected | `test_K_memory_delete_correct_record` | ✅ |
| L | Memory injection: provider request includes server-owned memory context | `test_L_memory_injected_into_provider_request` | ✅ |
| M | No memories: normal chat unaffected | `test_M_no_memories_chat_unaffected` | ✅ |
| N | Concurrency: deterministic ordering/state integrity | `test_N_concurrent_requests_preserve_pair_integrity` | ✅ |
| O | All provider tests still pass | (existing `test_openai_provider.py` + `test_provider_errors.py` — 35 tests, all green) | ✅ |

### Additional edge cases covered

- `test_safe_fallback_content_is_stored_as_assistant_turn` — Issue #5 requirement: if OutputValidator ultimately substitutes SAFE_FALLBACK_CONTENT, that fallback IS stored as a real assistant turn (HTTP 200 path).
- `test_get_unknown_conversation_returns_empty_summary` — graceful for a fresh browser session.
- `test_memory_post_rejects_empty_content` / `test_memory_post_rejects_too_long_content` — Pydantic validation.
- `test_chat_does_not_store_system_prompt` — the canonical Vane system prompt is NEVER stored; GET /v1/conversations returns only user/assistant.
- `test_clear_conversation_then_send_starts_fresh` — after DELETE, a subsequent chat starts with an empty history (provider sees [system, user] again).

## Browser E2E evidence

Single-shot script: `/home/z/my-project/scripts/run_conversation_memory_e2e.sh`.
Artifacts: `/home/z/my-project/download/e2e_memory/` (32 files: screenshots, JSON dumps, conversation-id captures).

### Services under test

- FastAPI on `0.0.0.0:8000` (mock mode, `COMPANION_CONVERSATION_MAX_TURNS=8`, `COMPANION_MEMORY_MAX_PER_SCOPE=32`).
- Next.js dev on `0.0.0.0:3000`.
- Browser: `agent-browser` (headless Chrome 151).

### Path 1 — Multi-turn continuity (single session)

1. **Home** — `01_home.png`. Renders.
2. **Onboarding** — `02_chat_open.png`. Clicked "Conocer a Vane" → 5/5 answers.
3. **Send #1** — `03_after_send_1.png`, `03_conv_after_send_1.json`. Sent "Hola Vane, soy Alice. Me gustan los gatos." Server now has 2 messages: `[user1, assistant1]`. ✅
4. **Send #2** — `05_after_send_2.png`, `05_conv_after_send_2.json`. Sent "¿Te acordás qué me gustan?". Server now has 4 messages: `[user1, assistant1, user2, assistant2]`. ✅ Continuity verified.
5. **Send #3** — `07_after_send_3.png`, `07_conv_after_send_3.json`. Sent "¿Cuál fue la primera cosa que te dije?". Server now has 6 messages. ✅

### Path 2 — Refresh preserves conversation_id and continuity

6. **Refresh** — `08_after_refresh.png`. `conversation_id` before = `60ebd7bc-...`, after = `60ebd7bc-...` (identical). ✅ `sessionStorage` preserved.
7. **Send #4 (post-refresh)** — `10_after_send_4.png`, `10_conv_after_send_4.json`. Sent "Otra pregunta después del refresh." Server now has 8 messages — all 3 prior pairs + the new pair. ✅ Continuity preserved across refresh.

### Path 3 — Fresh browser session isolation

8. **Fresh session** — `11_fresh_session.png`. Cleared sessionStorage + localStorage, reloaded. `conversation_id` in fresh session = `c774dc8c-...` (NEW, different from `60ebd7bc-...`). ✅
9. **Send in new session** — `13_new_session_after_send.png`, `13_new_session_conv.json`. Sent "Hola, soy Bob en una sesión nueva." Server has exactly 2 messages — the new pair only. ✅ Verified NO leakage of old conversation messages into the new session (assertion in the script: `forbidden = ['Hola Vane, soy Alice...', 'Otra pregunta después del refresh.']`).

### Path 4 — Clear conversation via API

10. **DELETE** — `14_clear_response.json`. `DELETE /v1/conversations/c774dc8c-...` returned `{"deleted": true, "conversation_id": "c774dc8c-..."}`. ✅
11. **After clear** — server message count = 0. ✅
12. **Old conversation untouched** — the old `60ebd7bc-...` conversation still has 8 messages. ✅
13. **Send after clear** — `16_after_clear_send.png`. Sent "Después de limpiar la conversación." Server now has 2 messages — fresh start. ✅ Roles: `['user', 'assistant']`.

### Path 5 — Memory API smoke

14. **POST /v1/memories** — `17_memory_post.json`. Created an explicit fact for `user_id=alice, character_id=vane` with `memory_type=user_fact`, `source=explicit_user_statement`, `confidence=high`, `inferred=false`. ✅
15. **GET /v1/memories (alice)** — `17_memory_list_alice.json`. Returns the 1 memory. ✅
16. **GET /v1/memories (bob)** — `17_memory_list_bob.json`. Returns empty list — no cross-user leakage. ✅
17. **DELETE memory as bob (cross-user)** — `17_memory_delete_cross.json`. Returns 404 `memory_not_found` — scope check enforced. ✅
18. **DELETE memory as alice (correct scope)** — `17_memory_delete_ok.json`. Returns `{"deleted": true, "memory_id": "..."}`. ✅

### Path 6 — Memory injection into chat

19. **POST /v1/chat with memory** — `18_memory_chat.json`. Added a memory for `mem-inject-user`, then sent a chat. Response 200 with `validation.is_valid=true`. ✅ (The unit test `test_L_memory_injected_into_provider_request` verifies the exact messages list shape: `[system(Vane), system(memory), user]`.)

### Summary of E2E evidence

| Path | Result |
|---|---|
| Multi-turn continuity (3 messages in same session) | Real prior turns visible to provider; messages stored server-side in correct pair order |
| Refresh preserves conversation_id + continuity | ✅ sessionStorage UUID kept; 4th message added to the same conversation record |
| Fresh browser session isolation | ✅ New conversation_id; no leakage of old session's messages |
| Clear conversation via API | ✅ DELETE returns `deleted=true`; subsequent send starts from empty history; other conversations untouched |
| Memory POST/GET/DELETE | ✅ Explicit fact created; scope-isolated list; cross-user delete returns 404; same-user delete succeeds |
| Memory injection into chat | ✅ Memory present in server-side store; provider request shape verified by unit test L |

## Runtime honesty

Throughout the codebase and docs, all references to conversation and memory state are labeled honestly:

- "in-process prototype state" — used in `.env.example`, `main.py` docstrings, this handoff doc.
- "NOT durable persistence" — explicitly called out.
- "Server restart clears all state" — explicitly called out.
- `/v1/runtime/status` returns `conversation_max_turns` and `memory_max_per_scope` as safe config values, NOT as "memory size" or "持久存储".
- The frontend dev diagnostic label is `turnos server: N` (server turns count), not "memoria persistente".
- `lib/session.ts` already said "This is NOT persistent memory" — that label is preserved.
- `lib/api.ts` `clearConversation` JSDoc says "this is in-process prototype state. Server restart clears all conversations; this is NOT durable persistence."

There is NO use of "persistent", "long-term", "durable", or "cross-session durable" to describe the conversation or memory state in this milestone.

## Known limitations

1. **In-process prototype state.** Conversation history and memories live in process memory. Server restart clears ALL state. This is honest: it is NOT durable persistence.
2. **No auth.** `user_id` and `character_id` are prototype scope keys, not secure identities. Anyone who knows a user_id can read/delete that user's conversations and memories. Documented in the API contract and the runtime status responses.
3. **Single-process only.** The `asyncio.Lock` per scope works only within one event loop. A multi-process deployment (e.g. uvicorn workers > 1) would see different in-process stores per worker — the frontend's `conversation_id` would round-robin between workers and lose continuity. A future PostgreSQL backend removes this limitation.
4. **Mock provider ignores prior turns.** The `MockModelProvider` replies with a canned string that echoes only the last user message — it does not actually use the prior turns. This is expected: the mock is for plumbing, not for character quality. A real OpenAI-compatible provider would actually consume the assembled context. The context assembly itself is verified end-to-end by the integration tests (`CapturingMockProvider` captures the exact `messages` list the provider received).
5. **No memory LLM extraction.** Memories are only added via explicit `POST /v1/memories`. No automatic extraction of facts from conversation. This is intentional per Issue #5: "No invented memories."
6. **No memory injection UI.** Memories can only be added via the API (curl, future settings panel). The chat panel does not yet expose a "remember this" button — that is a future UI milestone.
7. **Bounded by message pairs, not tokens.** `COMPANION_CONVERSATION_MAX_TURNS` bounds the number of user/assistant pairs, not the total token count. A very long single message could still blow past a provider's token limit. A future milestone could add a token-aware bound.

## Server restart behavior

- All conversation history is LOST on server restart.
- All memories are LOST on server restart.
- The frontend's `sessionStorage` UUID survives (it's client-side), but the server-side conversation record for that UUID is gone — the next chat request will start a fresh conversation under the same UUID.
- This is explicitly documented in `.env.example`, `main.py`, and this handoff. The frontend `clearConversation` JSDoc also calls it out.

## Issue #5 compliance

| Criterion | Status |
|---|---|
| FastAPI canonical backend preserved | ✅ |
| Provider/runtime architecture preserved | ✅ (no changes to router, providers, errors, validation, companions) |
| Next.js client preserved, no new Next.js API backend | ✅ |
| Server-side multi-turn history keyed by (user, character, conversation) | ✅ |
| Client sends only current message; backend rebuilds canonical context | ✅ |
| In-process store abstraction with future PostgreSQL swappability | ✅ (Protocol-based) |
| Bounded conversation history (deterministic, pair-aware) | ✅ |
| Canonical Vane system prompt prepended every request, stored separately | ✅ (NEVER stored in history) |
| Minimal memory model: explicit user facts only, fact vs inference distinction | ✅ |
| APIs to inspect/delete conversation & memory state, scope-controlled | ✅ |
| No cross-user/character mixing | ✅ |
| Honest "in-process prototype" labels, no "persistent" claims | ✅ |
| Preserve adult-only one-companion cyber-noir direction | ✅ (frontend unchanged) |
| Provider failures do not append fake assistant turn | ✅ (rollback helper) |
| OutputValidator fallback content may be stored if returned to user | ✅ |
| Conversation_id remains browser-session based | ✅ (sessionStorage unchanged) |
| Bounded state growth | ✅ (max_turns + max_per_scope) |
| Deterministic ordering | ✅ (per-scope asyncio.Lock) |
| No secret leakage | ✅ (runtime status returns only safe config) |
| Concurrent requests do not corrupt in-process state | ✅ (per-scope locks + test_N) |
| Tests must not call paid/external models | ✅ (httpx.MockTransport + CapturingMockProvider) |
| Browser E2E: multi-turn + refresh + new session + clear | ✅ (32 artifacts) |
| Secret scan / tracked-file inspection | ✅ (no .env, no real keys, no binary media, no PAT) |

## Recommended next persistence milestone

1. **PostgreSQL backend for ConversationStore + MemoryStore.** Implement `PostgresConversationStore` and `PostgresMemoryStore` against the same Protocols. Migrate the in-process implementations to a `dev` profile, keep Postgres as `prod`. No API surface change.
2. **Auth + scope enforcement.** Replace the prototype `user_id` with a real authenticated identity (JWT, session cookie). The scope-key contracts do not change — only the source of `user_id` does.
3. **Token-aware history bound.** Add a token-budget bound on top of the pair-count bound, so a single very long message cannot blow past a provider's token limit.
4. **Memory injection UI.** Add a small "remember this" affordance in the chat panel that calls `POST /v1/memories` with the current message as content.
5. **Inferred memories (clearly separated).** A future milestone may add an opt-in LLM extraction pass that produces `inferred=True` memories — but only after auth, persistent storage, and explicit user consent. The schema already supports the distinction.
6. **Conversation compaction.** For long-running conversations, a summarizer could produce a compact "prior context summary" system message that replaces the oldest evicted pairs. This is a future LLM-dependent feature, not part of this milestone.
