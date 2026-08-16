import os
from datetime import UTC

from fastapi import FastAPI, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .domain.context import assemble_request_messages, build_model_request
from .domain.contracts import (
    CharacterCreateRequest,
    ChatRequest,
    ChatResponse,
    ConversationDeleteResponse,
    ConversationMessageView,
    ConversationScopeRequest,
    ConversationSummary,
    MemoryCreateRequest,
    MemoryDeleteResponse,
    MemoryListResponse,
    MemoryRecordView,
    MockMedia,
    ProfileOnboardingRequest,
)
from .domain.conversations import (
    ConversationScopeKey,
    InProcessConversationStore,
)
from .domain.memories import (
    InProcessMemoryStore,
    MemoryScopeKey,
)
from .domain.providers.errors import (
    ProviderAuthError,
    ProviderConnectError,
    ProviderError,
    ProviderInvalidResponseError,
    ProviderRateLimitError,
    ProviderRequestError,
    ProviderServerError,
    ProviderTimeoutError,
)
from .domain.router import build_router, runtime_status

app = FastAPI(title="Companion Studio API", version="0.3.0")

_cors_env = os.environ.get("COMPANION_CORS_ORIGINS", "http://localhost:3000")
_cors_origins = [origin.strip() for origin in _cors_env.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

router = build_router()
state: dict[str, object] = {}


def _env_int_optional(name: str, default: int) -> int:
    """Read an int env var, falling back to default on missing/invalid."""
    raw = os.environ.get(name)
    if not raw:
        return default
    try:
        value = int(raw)
    except ValueError:
        return default
    return value if value >= 0 else default


# ---------------------------------------------------------------------- #
# In-process conversation & memory stores (Issue #5).
# ---------------------------------------------------------------------- #
#
# These are intentionally in-process prototype state. Server restart
# clears them. The ConversationStore / MemoryStore Protocols are
# designed so a future PostgreSQL / Redis backend can replace these
# implementations without touching the chat handler, the router, or
# the API surface.

_CONVERSATION_MAX_TURNS = _env_int_optional("COMPANION_CONVERSATION_MAX_TURNS", 8)
_MEMORY_MAX_PER_SCOPE = _env_int_optional("COMPANION_MEMORY_MAX_PER_SCOPE", 32)

conversation_store = InProcessConversationStore(max_turns=_CONVERSATION_MAX_TURNS)
memory_store = InProcessMemoryStore(max_per_scope=_MEMORY_MAX_PER_SCOPE)


_PROVIDER_HTTP_STATUS: dict[type[ProviderError], int] = {
    ProviderTimeoutError: 504,
    ProviderInvalidResponseError: 502,
    ProviderConnectError: 503,
    ProviderRateLimitError: 503,
    ProviderServerError: 503,
    ProviderAuthError: 503,
    ProviderRequestError: 503,
}


@app.exception_handler(ProviderError)
async def provider_error_handler(_request: Request, exc: ProviderError) -> JSONResponse:
    """Map sanitized provider failures to stable 5xx responses.

    Upstream auth failures are intentionally NOT exposed as user-facing 401/403.
    The response contains only a stable code and controlled safe message.
    """
    status_code = 503
    for error_type, mapped_status in _PROVIDER_HTTP_STATUS.items():
        if isinstance(exc, error_type):
            status_code = mapped_status
            break
    return JSONResponse(
        status_code=status_code,
        content={
            "detail": {
                "code": exc.code,
                "message": exc.safe_message,
            }
        },
    )


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "companion-studio-api"}


@app.get("/v1/runtime/status")
async def get_runtime_status() -> dict[str, object]:
    """Safe provider diagnostics, plus prototype state-store config.

    The returned fields never include API keys, Authorization headers,
    URLs with sensitive query, or internal stacks. The
    ``conversation_max_turns`` and ``memory_max_per_scope`` fields are
    safe config values; the actual stored messages and memory contents
    are never surfaced here.
    """
    base = runtime_status(router)
    return {
        **base,
        "conversation_max_turns": conversation_store.max_turns,
        "memory_max_per_scope": memory_store.max_per_scope,
    }


@app.post("/v1/onboarding/profile")
async def save_profile(payload: ProfileOnboardingRequest) -> dict[str, object]:
    state["profile"] = payload.profile
    return {"profile": payload.profile, "persisted": True}


@app.post("/v1/characters")
async def create_character(payload: CharacterCreateRequest) -> dict[str, object]:
    state["character"] = payload.config
    return {"character": payload.config, "persisted": True}


@app.post("/v1/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest) -> ChatResponse:
    """Send one chat message using canonical server-owned context.

    A per-scope transaction covers append user → context assembly → provider
    call → append assistant (or rollback). Concurrent turns in the same
    conversation therefore cannot interleave.
    """
    conversation_scope = ConversationScopeKey(
        user_id=payload.user_id,
        character_id=payload.character_id,
        conversation_id=payload.conversation_id,
    )

    async with conversation_store.transaction(conversation_scope):
        await conversation_store.append_user_message(conversation_scope, payload.message)

        messages = await assemble_request_messages(
            character_id=payload.character_id,
            user_id=payload.user_id,
            conversation_id=payload.conversation_id,
            current_message=payload.message,
            route=payload.route,
            conversation_store=conversation_store,
            memory_store=memory_store,
        )

        request = build_model_request(
            route=payload.route,
            character_id=payload.character_id,
            user_id=payload.user_id,
            conversation_id=payload.conversation_id,
            messages=messages,
        )

        try:
            response = await router.generate(request)
        except ProviderError:
            await conversation_store.pop_last_user_message_if_match(
                conversation_scope, payload.message
            )
            raise

        await conversation_store.append_assistant_message(
            conversation_scope, response.content
        )

    return ChatResponse(response=response)


# ---------------------------------------------------------------------- #
# Conversation inspect / delete APIs (Issue #5 task 8)
# ---------------------------------------------------------------------- #


@app.get(
    "/v1/conversations/{conversation_id}",
    response_model=ConversationSummary,
)
async def get_conversation(
    conversation_id: str,
    user_id: str = Query(default="demo-user"),
    character_id: str = Query(default="vane"),
) -> ConversationSummary:
    """Return the stored messages for one conversation scope.

    Scope is enforced by `(user_id, character_id, conversation_id)`. A
    different user / character / conversation id CANNOT see this
    conversation's messages. Returns an empty message list (with the
    scope identifiers echoed back) if the conversation does not exist
    yet — this is graceful for a fresh browser session.

    NOTE: there is no auth in this milestone. `user_id` and
    `character_id` are prototype scope keys, not secure identities.
    """
    scope = ConversationScopeKey(
        user_id=user_id,
        character_id=character_id,
        conversation_id=conversation_id,
    )
    record = await conversation_store.get_conversation(scope)
    if record is None:
        # Return an empty summary with the scope echoed back. Use a
        # stable created_at/updated_at = now so the response shape is
        # consistent.
        from datetime import datetime

        now = datetime.now(UTC)
        return ConversationSummary(
            user_id=user_id,
            character_id=character_id,
            conversation_id=conversation_id,
            messages=[],
            created_at=now,
            updated_at=now,
        )
    return ConversationSummary(
        user_id=record.user_id,
        character_id=record.character_id,
        conversation_id=record.conversation_id,
        messages=[
            ConversationMessageView(
                id=m.id, role=m.role, content=m.content, created_at=m.created_at
            )
            for m in record.messages
        ],
        created_at=record.created_at,
        updated_at=record.updated_at,
    )


@app.delete(
    "/v1/conversations/{conversation_id}",
    response_model=ConversationDeleteResponse,
)
async def delete_conversation(
    conversation_id: str,
    payload: ConversationScopeRequest,
) -> ConversationDeleteResponse:
    """Clear the in-process conversation state for one scope.

    Only the conversation matching the body's `user_id` +
    `character_id` + the path's `conversation_id` is deleted. Other
    conversations — same user different conversation, different user,
    different character — are NOT touched.

    Returns ``{"deleted": bool, "conversation_id": str}`` where
    ``deleted`` is True iff a conversation existed and was removed.
    """
    scope = ConversationScopeKey(
        user_id=payload.user_id,
        character_id=payload.character_id,
        conversation_id=conversation_id,
    )
    existed = await conversation_store.delete_conversation(scope)
    return ConversationDeleteResponse(deleted=existed, conversation_id=conversation_id)


# ---------------------------------------------------------------------- #
# Memory APIs (Issue #5 task 7)
# ---------------------------------------------------------------------- #


@app.get("/v1/memories", response_model=MemoryListResponse)
async def list_memories(
    user_id: str = Query(default="demo-user"),
    character_id: str = Query(default="vane"),
) -> MemoryListResponse:
    """List the explicit user-fact memories for one scope.

    Scope is enforced by `(user_id, character_id)`. A different user or
    character CANNOT see this scope's memories. Returns an empty list
    if no memories exist yet.

    NOTE: there is no auth in this milestone. `user_id` and
    `character_id` are prototype scope keys, not secure identities.
    """
    scope = MemoryScopeKey(user_id=user_id, character_id=character_id)
    records = await memory_store.list_memories(scope)
    return MemoryListResponse(
        memories=[
            MemoryRecordView(
                id=r.id,
                user_id=r.user_id,
                character_id=r.character_id,
                content=r.content,
                memory_type=r.memory_type,
                source=r.source,
                confidence=r.confidence,
                inferred=r.inferred,
                created_at=r.created_at,
            )
            for r in records
        ],
        count=len(records),
    )


@app.post("/v1/memories", response_model=MemoryRecordView, status_code=201)
async def create_memory(payload: MemoryCreateRequest) -> MemoryRecordView:
    """Add an explicit user-fact memory.

    The client supplies only `content` (1-500 chars) and the scope
    identifiers. The server sets `memory_type=user_fact`,
    `source=explicit_user_statement`, `confidence=high`, `inferred=False`.
    The client CANNOT use this endpoint to upload a system prompt,
    trusted role messages, or arbitrary provider instructions —
    `content` is stored verbatim as a fact and injected as a separate
    server-owned memory section in the model request.

    If the scope exceeds `COMPANION_MEMORY_MAX_PER_SCOPE`, the oldest
    memory is evicted (FIFO).
    """
    scope = MemoryScopeKey(user_id=payload.user_id, character_id=payload.character_id)
    record = await memory_store.add_memory(scope, payload.content)
    return MemoryRecordView(
        id=record.id,
        user_id=record.user_id,
        character_id=record.character_id,
        content=record.content,
        memory_type=record.memory_type,
        source=record.source,
        confidence=record.confidence,
        inferred=record.inferred,
        created_at=record.created_at,
    )


@app.delete("/v1/memories/{memory_id}", response_model=MemoryDeleteResponse)
async def delete_memory(
    memory_id: str,
    payload: ConversationScopeRequest,
) -> MemoryDeleteResponse:
    """Delete a single explicit user-fact memory by id within a scope.

    The scope check is MANDATORY: a memory id from a different user or
    character CANNOT be deleted through this endpoint. Returns 404
    (via `deleted=False`) if the memory id is unknown within the scope.

    NOTE: there is no auth in this milestone. `user_id` and
    `character_id` are prototype scope keys, not secure identities.
    """
    scope = MemoryScopeKey(user_id=payload.user_id, character_id=payload.character_id)
    deleted = await memory_store.delete_memory(scope, memory_id)
    if not deleted:
        # Clean 404 for unknown id within scope. We do NOT leak whether
        # the id exists in a different scope — that would be an
        # information-disclosure side channel.
        return JSONResponse(
            status_code=404,
            content={
                "detail": {
                    "code": "memory_not_found",
                    "message": "Memory not found within the requested scope.",
                }
            },
        )
    return MemoryDeleteResponse(deleted=True, memory_id=memory_id)


@app.get("/v1/media/mock", response_model=MockMedia)
async def mock_media() -> MockMedia:
    return MockMedia(
        id="placeholder-video-001",
        kind="video",
        label="Video de prueba — placeholder, no generado en vivo",
    )
