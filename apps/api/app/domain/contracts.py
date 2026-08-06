from datetime import datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class ResponseStyle(StrEnum):
    NATURAL = "natural"
    PLAYFUL = "playful"
    CALM = "calm"


class Level(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Route(StrEnum):
    FAST_CHAT = "fast_chat"
    CREATIVE_CHAT = "creative_chat"
    DEEP_REASONING = "deep_reasoning"
    VISION = "vision"
    AGENT_TASK = "agent_task"
    MEMORY = "memory"


class MessageInput(BaseModel):
    role: str = Field(pattern="^(system|user|assistant|tool)$")
    content: str = Field(min_length=1, max_length=20_000)


class UserPreferenceProfile(BaseModel):
    language: str = "es"
    locale: str = "es-AR"
    response_style: ResponseStyle = ResponseStyle.NATURAL
    verbosity: Level = Level.MEDIUM
    stage_directions: bool = False
    translation_overlay: bool = False
    humor_style: str = "cálido"
    initiative_level: Level = Level.MEDIUM
    romantic_intensity: Level = Level.MEDIUM
    sensual_intensity: Level = Level.LOW
    notification_preferences: dict[str, Any] = Field(default_factory=dict)
    visual_preferences: dict[str, Any] = Field(default_factory=dict)
    agent_interests: list[str] = Field(default_factory=list)


class ProfileOnboardingRequest(BaseModel):
    profile: UserPreferenceProfile


class CharacterConfig(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    identity: str = Field(min_length=1, max_length=500)
    personality_traits: list[str] = Field(min_length=1, max_length=12)
    relationship_dynamic: str
    speech_style: str
    initiative_level: Level = Level.MEDIUM
    sensual_intensity: Level = Level.LOW
    boundaries: list[str] = Field(default_factory=list)
    capabilities: list[str] = Field(default_factory=list)
    visual_style: str
    voice_style: str = "conversacional"


class CharacterCreateRequest(BaseModel):
    user_id: str = "demo-user"
    config: CharacterConfig


class SessionOverride(BaseModel):
    scope: str = Field(pattern="^(session|conversation|character|global)$")
    starts_at: datetime
    expires_at: datetime | None = None
    overrides: dict[str, Any]
    reason: str = Field(min_length=1, max_length=300)


class ModelRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    route: Route
    character_id: str
    user_id: str
    conversation_id: str
    messages: list[MessageInput] = Field(min_length=1)
    memories: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)
    metadata: dict[str, Any] = Field(default_factory=dict)


class Usage(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0


class OutputValidationResult(BaseModel):
    is_valid: bool
    language_ok: bool
    encoding_ok: bool
    not_truncated: bool
    not_repetitive: bool
    no_internal_leak: bool
    character_consistent: bool
    reasons: list[str] = Field(default_factory=list)


class ModelResponse(BaseModel):
    provider: str
    model: str
    content: str
    usage: Usage = Field(default_factory=Usage)
    latency_ms: int = 0
    validation: OutputValidationResult | None = None
    retry_count: int = 0


class ChatRequest(BaseModel):
    user_id: str = "demo-user"
    character_id: str = "host"
    conversation_id: str = "demo-conversation"
    message: str = Field(min_length=1, max_length=4_000)
    route: Route = Route.FAST_CHAT


class ChatResponse(BaseModel):
    response: ModelResponse


class MockMedia(BaseModel):
    id: str
    kind: str
    label: str
    is_placeholder: bool = True
    generated_in_realtime: bool = False
