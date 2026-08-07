"""OpenAI-compatible HTTP model provider adapter.

Implements the `ModelProvider` Protocol against any endpoint that speaks
the OpenAI Chat Completions API (`POST /v1/chat/completions`). The domain
layer imports no SDK; this adapter owns its `httpx.AsyncClient` and
translates every failure (HTTP errors, timeouts, malformed JSON, empty
choices) into a safe `ModelResponse` carrying the canonical Spanish
fallback string. The adapter never raises to the router, so no stack
trace or secret can leak through the API surface.

Selection is server-side, env-driven (see `app.domain.router.build_router`):
the adapter is only constructed when `COMPANION_MODEL_PROVIDER=openai` and
a base URL + API key are configured. `mock` remains the default.
"""

from __future__ import annotations

from typing import Any

import httpx

from app.domain.contracts import ModelRequest, ModelResponse, Usage

# Canonical safe fallback. Spanish, ends with a period, passes OutputValidator.
SAFE_FALLBACK_CONTENT = "No pude responder con seguridad esta vez. Probemos de nuevo."


class OpenAICompatibleProvider:
    """Async provider against an OpenAI-compatible `/v1/chat/completions` endpoint.

    Attributes
    ----------
    name : str
        Static identifier reported in `ModelResponse.provider` and the
        runtime status endpoint. Always ``"openai-compatible"``.
    model : str
        Model name to request (e.g. ``"gpt-4o-mini"``). Reported in
        `ModelResponse.model` and diagnostics.
    """

    name = "openai-compatible"

    def __init__(
        self,
        base_url: str,
        api_key: str,
        model: str,
        *,
        timeout_seconds: float = 5.0,
        transport: httpx.AsyncBaseTransport | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.model = model
        self._timeout = timeout_seconds
        # `transport` is injected by tests via httpx.MockTransport; in
        # production it is None so httpx uses the default transport.
        self._client = httpx.AsyncClient(
            base_url=self.base_url,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            timeout=timeout_seconds,
            transport=transport,
        )

    async def generate(self, request: ModelRequest) -> ModelResponse:
        """Generate a completion, translating every failure into a safe response.

        The adapter never raises. On any error (network, HTTP status,
        malformed JSON, empty choices, timeout) it returns a
        `ModelResponse` with `SAFE_FALLBACK_CONTENT` so the router and
        the API layer can never leak a stack trace or a secret.
        """
        payload = self._build_payload(request)
        try:
            resp = await self._client.post("/chat/completions", json=payload)
            resp.raise_for_status()
            data = resp.json()
        except Exception:
            # Covers httpx.TimeoutException, httpx.HTTPStatusError,
            # httpx.ConnectError, json.JSONDecodeError, KeyError, etc.
            return self._safe_response()

        content = self._extract_content(data)
        if not content:
            return self._safe_response()

        usage = self._extract_usage(data)
        return ModelResponse(
            provider=self.name,
            model=self.model,
            content=content,
            usage=usage,
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    # ------------------------------------------------------------------ #
    # Internal helpers
    # ------------------------------------------------------------------ #

    def _build_payload(self, request: ModelRequest) -> dict[str, Any]:
        """Map a `ModelRequest` to an OpenAI chat completions request body."""
        messages = [{"role": m.role, "content": m.content} for m in request.messages]
        return {
            "model": self.model,
            "messages": messages,
            "temperature": 0.8,
            "stream": False,
        }

    def _extract_content(self, data: dict[str, Any]) -> str:
        """Extract the assistant text from an OpenAI-format response.

        Returns an empty string on any structural problem so the caller
        can substitute the safe fallback.
        """
        choices = data.get("choices")
        if not isinstance(choices, list) or not choices:
            return ""
        first = choices[0]
        if not isinstance(first, dict):
            return ""
        message = first.get("message")
        if not isinstance(message, dict):
            return ""
        content = message.get("content")
        if not isinstance(content, str):
            return ""
        return content.strip()

    def _extract_usage(self, data: dict[str, Any]) -> Usage:
        usage = data.get("usage")
        if not isinstance(usage, dict):
            return Usage()
        try:
            return Usage(
                input_tokens=int(usage.get("prompt_tokens", 0)),
                output_tokens=int(usage.get("completion_tokens", 0)),
            )
        except (TypeError, ValueError):
            return Usage()

    def _safe_response(self) -> ModelResponse:
        return ModelResponse(
            provider=self.name,
            model=self.model,
            content=SAFE_FALLBACK_CONTENT,
        )
