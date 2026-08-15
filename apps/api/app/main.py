import os
from contextlib import asynccontextmanager
from datetime import UTC
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from .domain.authorization import Principal
from .domain.context import assemble_request_messages, build_model_request
from .domain.contracts import (
    ChatAssistantResponse,
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
    QueenIdentifier,
    Route,
    ScopeIdentifier,
)
from .domain.conversations import (
    ConversationScopeKey,
    InProcessConversationStore,
)
from .domain.identity import (
    PostgresIdentityRepository,
    auth_is_required,
    require_principal,
)
from .domain.memories import (
    InProcessMemoryStore,
    MemoryScopeKey,
)
from .domain.providers.errors import (
    ProviderAuthError,
    ProviderConnectError,
    ProviderContentBlockedError,
    ProviderError,
    ProviderInvalidResponseError,
    ProviderRateLimitError,
    ProviderRequestError,
    ProviderServerError,
    ProviderTimeoutError,
)
from .domain.queens import is_registered_queen
from .domain.router import build_router, runtime_status


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Connect the durable identity map only for the protected runtime."""

    if auth_is_required():
        database_url = os.environ.get("DATABASE_URL")
        if database_url:
            import asyncpg

            # SQLAlchemy-style URLs are accepted in the shared env contract.
            dsn = database_url.replace("postgresql+asyncpg://", "postgresql://", 1)
            pool = await asyncpg.create_pool(dsn)
            app.state.identity_pool = pool
            app.state.identity_repository = PostgresIdentityRepository(pool)
    yield
    pool = getattr(app.state, "identity_pool", None)
    if pool is not None:
        await pool.close()


app = FastAPI(title="RiotQueens API", version="0.4.0", lifespan=lifespan)


class NoStoreV1Middleware:
    """Prevent browsers and intermediaries from caching stateful API responses."""

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http" or not scope.get("path", "").startswith("/v1/"):
            await self.app(scope, receive, send)
            return

        async def send_no_store(message: Message) -> None:
            if message["type"] == "http.response.start":
                MutableHeaders(scope=message)["Cache-Control"] = "no-store"
            await send(message)

        await self.app(scope, receive, send_no_store)

_cors_env = os.environ.get("RIOTQUEENS_CORS_ORIGINS", "http://localhost:3000")
_cors_origins = [origin.strip() for origin in _cors_env.split(",") if origin.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(NoStoreV1Middleware)

router = build_router()


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

_CONVERSATION_MAX_TURNS = _env_int_optional("RIOTQUEENS_CONVERSATION_MAX_TURNS", 8)
_MEMORY_MAX_PER_SCOPE = _env_int_optional("RIOTQUEENS_MEMORY_MAX_PER_SCOPE", 32)

conversation_store = InProcessConversationStore(max_turns=_CONVERSATION_MAX_TURNS)
memory_store = InProcessMemoryStore(max_per_scope=_MEMORY_MAX_PER_SCOPE)


def _require_registered_queen(character_id: str) -> None:
    """Reject unknown Queens before allocating scope state or calling a provider."""

    if not is_registered_queen(character_id):
        raise HTTPException(
            status_code=404,
            detail={
                "code": "queen_not_found",
                "message": "Queen is not available.",
            },
        )


def _actor_user_id(principal: Principal | None, browser_user_id: str | None) -> str:
    """Return a token-derived actor identity; legacy test mode is explicit."""

    if auth_is_required():
        if principal is None:  # Defensive: dependency must already have failed closed.
            raise HTTPException(status_code=401, detail="Unauthorized")
        return principal.user_id
    if browser_user_id is None:
        raise HTTPException(status_code=401, detail="Unauthorized")
    return browser_user_id


_PROVIDER_HTTP_STATUS: dict[type[ProviderError], int] = {
    ProviderTimeoutError: 504,
    ProviderInvalidResponseError: 502,
    ProviderConnectError: 503,
    ProviderRateLimitError: 503,
    ProviderServerError: 503,
    ProviderAuthError: 503,
    ProviderRequestError: 503,
    ProviderContentBlockedError: 502,
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
    return {"status": "ok", "service": "riotqueens-api"}


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


@app.post("/v1/chat", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    principal: Annotated[Principal | None, Depends(require_principal)],
) -> ChatResponse:
    """Send a single chat message and rebuild canonical server context.

    The frontend sends ONLY the current user message plus the scope
    identifiers (`user_id`, `character_id`, `conversation_id`). The
    server, holding the per-scope transaction lock for the WHOLE turn
    lifecycle:

      1. Acquires the per-conversation transaction lock (reentrant).
         Two concurrent requests to the SAME conversation serialize
         completely — their append/context/provider/append mutations
         cannot interleave. Different conversations run in parallel.
      2. Appends the user message to the in-process conversation store
         (scoped by user + character + conversation).
      3. Assembles the canonical messages list:
         system Queen prompt → server-owned memory context → bounded
         conversation history (which now ends with the trailing user
         message) → defensive current-user append if needed.
      4. Calls the provider via the ModelRouter. Any exception or task
         cancellation after the user append attempts to roll that exact
         trailing message back, so no failed half-turn pollutes history.
         The original error is always re-raised; typed provider failures
         still reach FastAPI's sanitized exception handler.
      5. On success, appends the assistant's validated content as a new
         assistant turn. The stored record is then pruned to the bound
         so in-process state does not grow without limit. (If the
         router's `OutputValidator` ultimately substituted
         `SAFE_FALLBACK_CONTENT`, that fallback IS the assistant
         response the user sees — so it is stored as a real assistant
         turn, per Issue #5.)

    The client never sends a system prompt, never sends trusted prior
    messages, never sends trusted memories. The browser only sends the
    current message and the scope identifiers. Model routing is also
    server-owned: this public endpoint always uses ``FAST_CHAT``.
    """
    _require_registered_queen(payload.character_id)

    user_id = _actor_user_id(principal, payload.user_id)
    conversation_scope = ConversationScopeKey(
        user_id=user_id,
        character_id=payload.character_id,
        conversation_id=payload.conversation_id,
    )

    # Acquire the per-scope transaction lock for the WHOLE turn. This
    # serializes same-conversation requests end-to-end (append user →
    # provider call → append assistant / rollback). Different
    # conversations use different locks and run in parallel. A slow
    # provider in one conversation does NOT block other conversations.
    async with conversation_store.transaction(conversation_scope):
        # 1. Append the user message BEFORE calling the provider. This
        #    becomes the trailing user turn in the bounded history.
        await conversation_store.append_user_message(conversation_scope, payload.message)

        try:
            # 2. Assemble the canonical messages list and build the
            #    provider-independent internal request.
            messages = await assemble_request_messages(
                character_id=payload.character_id,
                user_id=user_id,
                conversation_id=payload.conversation_id,
                current_message=payload.message,
                route=Route.FAST_CHAT,
                conversation_store=conversation_store,
                memory_store=memory_store,
            )

            request = build_model_request(
                route=Route.FAST_CHAT,
                character_id=payload.character_id,
                user_id=user_id,
                conversation_id=payload.conversation_id,
                messages=messages,
            )

            # 3. Call the provider, then store exactly the validated
            #    content returned to the public response.
            response = await router.generate(request)
            await conversation_store.append_assistant_message(
                conversation_scope, response.content
            )
        except BaseException as error:
            # Cancellation inherits from BaseException, not Exception.
            # Rollback runs while this task still owns the reentrant turn
            # lock. Preserve the original failure even if the best-effort
            # rollback itself unexpectedly fails.
            try:
                await conversation_store.pop_last_user_message_if_match(
                    conversation_scope, payload.message
                )
            except BaseException as rollback_error:
                error.add_note(
                    "Failed to roll back the trailing user turn: "
                    f"{type(rollback_error).__name__}"
                )
            raise

    return ChatResponse(response=ChatAssistantResponse(content=response.content))


# ---------------------------------------------------------------------- #
# Conversation inspect / delete APIs (Issue #5 task 8)
# ---------------------------------------------------------------------- #


@app.get(
    "/v1/conversations/{conversation_id}",
    response_model=ConversationSummary,
)
async def get_conversation(
    conversation_id: ScopeIdentifier,
    character_id: Annotated[QueenIdentifier, Query()],
    user_id: Annotated[ScopeIdentifier | None, Query()] = None,
    principal: Annotated[Principal | None, Depends(require_principal)] = None,
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
    _require_registered_queen(character_id)

    actor_user_id = _actor_user_id(principal, user_id)
    scope = ConversationScopeKey(
        user_id=actor_user_id,
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
            user_id=actor_user_id,
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
    conversation_id: ScopeIdentifier,
    payload: ConversationScopeRequest,
    principal: Annotated[Principal | None, Depends(require_principal)],
) -> ConversationDeleteResponse:
    """Clear the in-process conversation state for one scope.

    Only the conversation matching the body's `user_id` +
    `character_id` + the path's `conversation_id` is deleted. Other
    conversations — same user different conversation, different user,
    different character — are NOT touched.

    Returns ``{"deleted": bool, "conversation_id": str}`` where
    ``deleted`` is True iff a conversation existed and was removed.
    """
    _require_registered_queen(payload.character_id)

    scope = ConversationScopeKey(
        user_id=_actor_user_id(principal, payload.user_id),
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
    character_id: Annotated[QueenIdentifier, Query()],
    user_id: Annotated[ScopeIdentifier | None, Query()] = None,
    principal: Annotated[Principal | None, Depends(require_principal)] = None,
) -> MemoryListResponse:
    """List the explicit user-fact memories for one scope.

    Scope is enforced by `(user_id, character_id)`. A different user or
    character CANNOT see this scope's memories. Returns an empty list
    if no memories exist yet.

    NOTE: there is no auth in this milestone. `user_id` and
    `character_id` are prototype scope keys, not secure identities.
    """
    _require_registered_queen(character_id)

    actor_user_id = _actor_user_id(principal, user_id)
    scope = MemoryScopeKey(user_id=actor_user_id, character_id=character_id)
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
async def create_memory(
    payload: MemoryCreateRequest,
    principal: Annotated[Principal | None, Depends(require_principal)],
) -> MemoryRecordView:
    """Add an explicit user-fact memory.

    The client supplies only `content` (1-500 chars) and the scope
    identifiers. The server sets `memory_type=user_fact`,
    `source=explicit_user_statement`, `confidence=high`, `inferred=False`.
    The client CANNOT use this endpoint to upload a system prompt,
    trusted role messages, or arbitrary provider instructions —
    `content` is stored verbatim as a fact and injected as a separate
    server-owned memory section in the model request.

    If the scope exceeds `RIOTQUEENS_MEMORY_MAX_PER_SCOPE`, the oldest
    memory is evicted (FIFO).
    """
    _require_registered_queen(payload.character_id)

    scope = MemoryScopeKey(
        user_id=_actor_user_id(principal, payload.user_id),
        character_id=payload.character_id,
    )
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
    memory_id: ScopeIdentifier,
    payload: ConversationScopeRequest,
    principal: Annotated[Principal | None, Depends(require_principal)],
) -> MemoryDeleteResponse:
    """Delete a single explicit user-fact memory by id within a scope.

    The scope check is MANDATORY: a memory id from a different user or
    character CANNOT be deleted through this endpoint. Returns 404
    (via `deleted=False`) if the memory id is unknown within the scope.

    NOTE: there is no auth in this milestone. `user_id` and
    `character_id` are prototype scope keys, not secure identities.
    """
    _require_registered_queen(payload.character_id)

    scope = MemoryScopeKey(
        user_id=_actor_user_id(principal, payload.user_id),
        character_id=payload.character_id,
    )
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
