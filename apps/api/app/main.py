import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .domain.companions import get_system_prompt
from .domain.contracts import (
    CharacterCreateRequest,
    ChatRequest,
    ChatResponse,
    MessageInput,
    MockMedia,
    ModelRequest,
    ModelResponse,
    ProfileOnboardingRequest,
)
from .domain.router import build_router, runtime_status
from .domain.validation import OutputValidator

app = FastAPI(title="Companion Studio API", version="0.2.0")

# ---------------------------------------------------------------------- #
# CORS — dev origin only, not wildcard (Issue #3 #7).
# ---------------------------------------------------------------------- #
_cors_env = os.environ.get("COMPANION_CORS_ORIGINS", "http://localhost:3000")
_cors_origins = [o.strip() for o in _cors_env.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Canonical router: env-driven provider selection (mock by default).
router = build_router()
state: dict[str, object] = {}

# Safe fallback used when the router raises (e.g. timeout after retries)
# or when a provider error escapes. Spanish, passes OutputValidator.
_SAFE_FALLBACK_CONTENT = "No pude responder con seguridad esta vez. Probemos de nuevo."
_validator = OutputValidator()


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "companion-studio-api"}


@app.get("/v1/runtime/status")
async def get_runtime_status() -> dict[str, object]:
    """Safe runtime/provider diagnostics.

    Reports configured provider, model, mode (mock/real), timeout and
    retries. Never returns API keys, Authorization headers, full provider
    URLs with sensitive query, or internal stacks.
    """
    return runtime_status(router)


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
    # Server-owned canonical system prompt (Issue #3 #6). The client
    # never supplies a system prompt; the handler resolves it from the
    # canonical character_id and prepends it as a system MessageInput.
    messages: list[MessageInput] = []
    system_prompt = get_system_prompt(payload.character_id)
    if system_prompt:
        messages.append(MessageInput(role="system", content=system_prompt))
    messages.append(MessageInput(role="user", content=payload.message))

    request = ModelRequest(
        route=payload.route,
        character_id=payload.character_id,
        user_id=payload.user_id,
        conversation_id=payload.conversation_id,
        messages=messages,
    )

    try:
        response = await router.generate(request)
    except RuntimeError:
        # Router raises RuntimeError("model_provider_timeout") after
        # exhausting retries. Degrade to a safe Spanish response instead
        # of leaking a 500 stack trace.
        response = ModelResponse(
            provider="router",
            model="safe-fallback",
            content=_SAFE_FALLBACK_CONTENT,
        )
        response.validation = _validator.validate(response.content)

    return ChatResponse(response=response)


@app.get("/v1/media/mock", response_model=MockMedia)
async def mock_media() -> MockMedia:
    return MockMedia(
        id="placeholder-video-001",
        kind="video",
        label="Video de prueba — placeholder, no generado en vivo",
    )
