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
    character_id: str = "bardera"
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


# ---------------------------------------------------------------------- #
# Conversation & memory API contracts (Issue #5)
# ---------------------------------------------------------------------- #
#
# These contracts back the /v1/conversations and /v1/memories endpoints.
# They are intentionally small and explicit. There is NO auth in this
# milestone — `user_id` and `character_id` are prototype scope keys,
# not secure identities. The handoff doc records this limitation
# honestly.


class ConversationMessageView(BaseModel):
    """API view of a single stored conversation message.

    Only ``user`` and ``assistant`` roles are ever stored; the canonical
    Queen system prompt is NEVER persisted and is never returned here.
    """

    id: str
    role: str = Field(pattern="^(user|assistant)$")
    content: str
    created_at: datetime


class ConversationSummary(BaseModel):
    """API view of a full conversation, scoped by (user, character, conversation).

    Returned by `GET /v1/conversations/{conversation_id}`. The
    `messages` list is ordered oldest-first. System prompts are never
    included.
    """

    user_id: str
    character_id: str
    conversation_id: str
    messages: list[ConversationMessageView] = Field(default_factory=list)
    created_at: datetime
    updated_at: datetime


class ConversationScopeRequest(BaseModel):
    """Body for scope-keyed conversation endpoints.

    `user_id` defaults to the same prototype value `ChatRequest` uses
    so the chat flow stays consistent without auth. `character_id`
    defaults to ``"bardera"`` to match the canonical Queen.
    """

    user_id: str = "demo-user"
    character_id: str = "bardera"


class MemoryCreateRequest(BaseModel):
    """Body for `POST /v1/memories` — add an explicit user fact.

    The client supplies only ``content`` plus the scope identifiers.
    The server sets ``memory_type``, ``source``, ``confidence`` and
    ``inferred`` — never the client.

    The client CANNOT use this endpoint to upload a system prompt,
    trusted role messages, or arbitrary provider instructions. The
    only field that affects model context is ``content``, which is
    stored verbatim as a fact and injected as a separate system-owned
    memory section.
    """

    user_id: str = "demo-user"
    character_id: str = "bardera"
    content: str = Field(min_length=1, max_length=500)


class MemoryRecordView(BaseModel):
    """API view of a single stored memory record."""

    id: str
    user_id: str
    character_id: str
    content: str
    memory_type: str
    source: str
    confidence: str
    inferred: bool
    created_at: datetime


class MemoryListResponse(BaseModel):
    """Response for `GET /v1/memories`."""

    memories: list[MemoryRecordView]
    count: int


class MemoryDeleteResponse(BaseModel):
    """Response for `DELETE /v1/memories/{memory_id}`."""

    deleted: bool
    memory_id: str


class ConversationDeleteResponse(BaseModel):
    """Response for `DELETE /v1/conversations/{conversation_id}`."""

    deleted: bool
    conversation_id: str
