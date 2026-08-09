"""OpenAI-compatible HTTP model provider adapter.

The adapter owns HTTP details and translates transport/upstream failures into
sanitized typed ProviderError exceptions. It never hides a provider outage as
a successful ModelResponse. Retry policy belongs to ModelRouter; HTTP mapping
belongs to FastAPI.
"""

from __future__ import annotations

from typing import Any

import httpx

from app.domain.contracts import ModelRequest, ModelResponse, Usage
from app.domain.providers.errors import (
    ProviderAuthError,
    ProviderConnectError,
    ProviderContentBlockedError,
    ProviderInvalidResponseError,
    ProviderRateLimitError,
    ProviderRequestError,
    ProviderServerError,
    ProviderTimeoutError,
)


class OpenAICompatibleProvider:
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
        payload = self._build_payload(request)
        try:
            response = await self._client.post("/chat/completions", json=payload)
        except httpx.TimeoutException:
            raise ProviderTimeoutError() from None
        except httpx.RequestError:
            raise ProviderConnectError() from None

        status = response.status_code
        if status == 400 and self._response_reports_content_block(response):
            raise ProviderContentBlockedError() from None
        if status in (401, 403):
            raise ProviderAuthError() from None
        if status == 429:
            raise ProviderRateLimitError() from None
        if status >= 500:
            raise ProviderServerError() from None
        if 400 <= status < 500:
            raise ProviderRequestError() from None
        if status < 200 or status >= 300:
            raise ProviderInvalidResponseError() from None

        try:
            data = response.json()
        except ValueError:
            raise ProviderInvalidResponseError() from None
        if not isinstance(data, dict):
            raise ProviderInvalidResponseError() from None
        if self._payload_reports_content_block(data):
            raise ProviderContentBlockedError() from None

        content = self._extract_content(data)
        if not content:
            raise ProviderInvalidResponseError() from None

        return ModelResponse(
            provider=self.name,
            model=self.model,
            content=content,
            usage=self._extract_usage(data),
        )

    async def aclose(self) -> None:
        await self._client.aclose()

    def _build_payload(self, request: ModelRequest) -> dict[str, Any]:
        return {
            "model": self.model,
            "messages": [
                {"role": message.role, "content": message.content} for message in request.messages
            ],
            "temperature": 0.8,
            "stream": False,
        }

    def _extract_content(self, data: dict[str, Any]) -> str:
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
        return content.strip() if isinstance(content, str) else ""

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

    def _response_reports_content_block(self, response: httpx.Response) -> bool:
        try:
            data = response.json()
        except ValueError:
            return False
        return isinstance(data, dict) and self._payload_reports_content_block(data)

    @staticmethod
    def _payload_reports_content_block(data: dict[str, Any]) -> bool:
        blocked_reasons = {
            "BLOCKED",
            "BLOCKLIST",
            "CONTENT_FILTER",
            "PROHIBITED_CONTENT",
            "SAFETY",
        }

        prompt_feedback = data.get("promptFeedback") or data.get("prompt_feedback")
        if isinstance(prompt_feedback, dict):
            reason = prompt_feedback.get("blockReason") or prompt_feedback.get("block_reason")
            if isinstance(reason, str) and reason.upper() in blocked_reasons:
                return True

        choices = data.get("choices")
        if isinstance(choices, list):
            for choice in choices:
                if not isinstance(choice, dict):
                    continue
                reason = choice.get("finish_reason") or choice.get("finishReason")
                if isinstance(reason, str) and reason.upper() in blocked_reasons:
                    return True

        error = data.get("error")
        if isinstance(error, dict):
            reason = error.get("reason") or error.get("status")
            if isinstance(reason, str) and reason.upper() in blocked_reasons:
                return True
        return False
