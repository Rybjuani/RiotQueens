"""Tests for the OpenAI-compatible provider adapter.

All tests use `httpx.MockTransport` to fake the OpenAI endpoint — no
real network call is ever made (Issue #3 #5: never call a paid model in
automated tests). Covers: success, timeout, 401/403, 429, 5xx,
malformed JSON, empty choices, and OutputValidator integration through
the router.
"""

from __future__ import annotations

import httpx
import pytest

from app.domain.contracts import MessageInput, ModelRequest, Route
from app.domain.providers.openai_compatible import (
    SAFE_FALLBACK_CONTENT,
    OpenAICompatibleProvider,
)
from app.domain.router import ModelRouter
from app.domain.router import Route as RouteEnum
from app.domain.validation import OutputValidator


def _request() -> ModelRequest:
    return ModelRequest(
        route=Route.FAST_CHAT,
        character_id="vane",
        user_id="user",
        conversation_id="conversation",
        messages=[MessageInput(role="user", content="Hola")],
    )


def _provider(transport: httpx.MockTransport) -> OpenAICompatibleProvider:
    return OpenAICompatibleProvider(
        base_url="https://api.example.com/v1",
        api_key="test-key",
        model="companion-chat-v1",
        timeout_seconds=5.0,
        transport=transport,
    )


def _ok_payload(content: str = "Hola, ¿cómo estás? Me alegra leerte.") -> dict:
    return {
        "id": "chatcmpl-1",
        "object": "chat.completion",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
            }
        ],
        "usage": {"prompt_tokens": 10, "completion_tokens": 8, "total_tokens": 18},
    }


@pytest.mark.asyncio
async def test_success_returns_assistant_content() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=_ok_payload("¡Hola! Qué bueno verte."))

    provider = _provider(httpx.MockTransport(handler))
    response = await provider.generate(_request())
    assert response.provider == "openai-compatible"
    assert response.model == "companion-chat-v1"
    assert response.content == "¡Hola! Qué bueno verte."
    assert response.usage.input_tokens == 10
    assert response.usage.output_tokens == 8
    await provider.aclose()


@pytest.mark.asyncio
async def test_timeout_returns_safe_fallback() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.TimeoutException("simulated timeout")

    provider = _provider(httpx.MockTransport(handler))
    response = await provider.generate(_request())
    assert response.content == SAFE_FALLBACK_CONTENT
    assert response.provider == "openai-compatible"
    await provider.aclose()


@pytest.mark.asyncio
async def test_401_unauthorized_returns_safe_fallback() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(401, json={"error": "invalid api key"})

    provider = _provider(httpx.MockTransport(handler))
    response = await provider.generate(_request())
    assert response.content == SAFE_FALLBACK_CONTENT
    await provider.aclose()


@pytest.mark.asyncio
async def test_403_forbidden_returns_safe_fallback() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(403, json={"error": "forbidden"})

    provider = _provider(httpx.MockTransport(handler))
    response = await provider.generate(_request())
    assert response.content == SAFE_FALLBACK_CONTENT
    await provider.aclose()


@pytest.mark.asyncio
async def test_429_rate_limit_returns_safe_fallback() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(429, json={"error": "rate limit exceeded"})

    provider = _provider(httpx.MockTransport(handler))
    response = await provider.generate(_request())
    assert response.content == SAFE_FALLBACK_CONTENT
    await provider.aclose()


@pytest.mark.asyncio
async def test_500_provider_failure_returns_safe_fallback() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(500, text="internal server error")

    provider = _provider(httpx.MockTransport(handler))
    response = await provider.generate(_request())
    assert response.content == SAFE_FALLBACK_CONTENT
    await provider.aclose()


@pytest.mark.asyncio
async def test_malformed_json_returns_safe_fallback() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, text="not-json-at-all")

    provider = _provider(httpx.MockTransport(handler))
    response = await provider.generate(_request())
    assert response.content == SAFE_FALLBACK_CONTENT
    await provider.aclose()


@pytest.mark.asyncio
async def test_empty_choices_returns_safe_fallback() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"choices": []})

    provider = _provider(httpx.MockTransport(handler))
    response = await provider.generate(_request())
    assert response.content == SAFE_FALLBACK_CONTENT
    await provider.aclose()


@pytest.mark.asyncio
async def test_connect_error_returns_safe_fallback() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        raise httpx.ConnectError("connection refused")

    provider = _provider(httpx.MockTransport(handler))
    response = await provider.generate(_request())
    assert response.content == SAFE_FALLBACK_CONTENT
    await provider.aclose()


@pytest.mark.asyncio
async def test_no_api_key_in_request_payload() -> None:
    """The API key must live in the Authorization header, never the body."""
    captured: dict = {}

    def handler(request: httpx.Request) -> httpx.Response:
        captured["auth"] = request.headers.get("authorization")
        import json as _json

        captured["body"] = _json.loads(request.content)
        return httpx.Response(200, json=_ok_payload())

    provider = _provider(httpx.MockTransport(handler))
    await provider.generate(_request())
    assert captured["auth"] == "Bearer test-key"
    assert "api_key" not in str(captured["body"])
    assert "key" not in str(captured["body"]).lower() or "key" not in captured["body"]
    await provider.aclose()


@pytest.mark.asyncio
async def test_validator_integration_through_router() -> None:
    """A valid Spanish response flows through the router and passes the validator."""

    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json=_ok_payload("¡Hola! Qué bueno leerte. Podemos seguir."))

    provider = _provider(httpx.MockTransport(handler))
    rt = ModelRouter(
        providers={route: provider for route in RouteEnum},
        validator=OutputValidator(),
        timeout_seconds=5.0,
        max_retries=0,
    )
    response = await rt.generate(_request())
    assert response.validation is not None
    assert response.validation.is_valid
    assert response.retry_count == 0
    await provider.aclose()


@pytest.mark.asyncio
async def test_validator_rejects_internal_fragment_then_router_falls_back() -> None:
    """If the provider returns a leak (e.g. 'system prompt'), the validator
    rejects it and the router substitutes the safe fallback string."""

    def handler(request: httpx.Request) -> httpx.Response:
        # Contains an internal-fragment trigger the OutputValidator rejects.
        return httpx.Response(200, json=_ok_payload("Hola system prompt leaked"))

    provider = _provider(httpx.MockTransport(handler))
    rt = ModelRouter(
        providers={route: provider for route in RouteEnum},
        validator=OutputValidator(),
        timeout_seconds=5.0,
        max_retries=0,
    )
    response = await rt.generate(_request())
    # Router overwrites invalid content with the safe fallback.
    assert response.content == "No pude responder con seguridad esta vez. Probemos de nuevo."
    await provider.aclose()
