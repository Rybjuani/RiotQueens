import asyncio
from collections.abc import Mapping
from time import perf_counter
from typing import Protocol

from .contracts import ModelRequest, ModelResponse, Route, Usage
from .validation import OutputValidator


class ModelProvider(Protocol):
    name: str
    model: str

    async def generate(self, request: ModelRequest) -> ModelResponse: ...


class MockModelProvider:
    name = "mock"
    model = "mock-companion-v1"

    async def generate(self, request: ModelRequest) -> ModelResponse:
        prompt = request.messages[-1].content
        return ModelResponse(
            provider=self.name,
            model=self.model,
            content=(
                f"Te leo. Soy la anfitriona de prueba y recibí: “{prompt}” ¿Seguimos desde ahí?"
            ),
            usage=Usage(input_tokens=len(prompt.split()), output_tokens=18),
        )


class ModelRouter:
    def __init__(
        self,
        providers: Mapping[Route, ModelProvider] | None = None,
        validator: OutputValidator | None = None,
        timeout_seconds: float = 5.0,
        max_retries: int = 1,
    ) -> None:
        self.providers = dict(providers or {route: MockModelProvider() for route in Route})
        self.validator = validator or OutputValidator()
        self.timeout_seconds = timeout_seconds
        self.max_retries = max_retries

    async def generate(self, request: ModelRequest) -> ModelResponse:
        provider = self.providers[request.route]
        started = perf_counter()
        last: ModelResponse | None = None
        for retry in range(self.max_retries + 1):
            try:
                response = await asyncio.wait_for(
                    provider.generate(request), timeout=self.timeout_seconds
                )
            except TimeoutError as exc:
                if retry == self.max_retries:
                    raise RuntimeError("model_provider_timeout") from exc
                continue
            response.validation = self.validator.validate(response.content)
            response.retry_count = retry
            response.latency_ms = round((perf_counter() - started) * 1000)
            last = response
            if response.validation.is_valid:
                return response
        assert last is not None
        last.content = "No pude responder con seguridad esta vez. Probemos de nuevo."
        last.validation = self.validator.validate(last.content)
        return last
