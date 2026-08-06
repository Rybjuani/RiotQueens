from fastapi import FastAPI

from .domain.contracts import (
    CharacterCreateRequest,
    ChatRequest,
    ChatResponse,
    MockMedia,
    ModelRequest,
    ProfileOnboardingRequest,
)
from .domain.router import ModelRouter

app = FastAPI(title="Companion Studio API", version="0.1.0")
router = ModelRouter()
state: dict[str, object] = {}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "service": "companion-studio-api"}


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
    request = ModelRequest(
        route=payload.route,
        character_id=payload.character_id,
        user_id=payload.user_id,
        conversation_id=payload.conversation_id,
        messages=[{"role": "user", "content": payload.message}],
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
