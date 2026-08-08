import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .domain.companions import get_system_prompt
from .domain.contracts import (
    CharacterCreateRequest,
    ChatRequest,
    ChatResponse,
    MessageInput,
    MockMedia,
    ModelRequest,
    ProfileOnboardingRequest,
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

app = FastAPI(title="Companion Studio API", version="0.2.0")

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
    response = await router.generate(request)
    return ChatResponse(response=response)


@app.get("/v1/media/mock", response_model=MockMedia)
async def mock_media() -> MockMedia:
    return MockMedia(
        id="placeholder-video-001",
        kind="video",
        label="Video de prueba — placeholder, no generado en vivo",
    )
