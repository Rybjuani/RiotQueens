import asyncio
import os
from collections.abc import Mapping
from time import perf_counter
from typing import Protocol

from .contracts import ModelRequest, ModelResponse, Route, Usage
from .providers.errors import (
    ProviderNonRetryableError,
    ProviderRetryableError,
    ProviderTimeoutError,
)
from .validation import OutputValidator

SAFE_FALLBACK_CONTENT = "No pude responder con seguridad esta vez. Probemos de nuevo."


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
        self.max_retries = max(0, max_retries)

    async def generate(self, request: ModelRequest) -> ModelResponse:
        provider = self.providers[request.route]
        started = perf_counter()
        last_response: ModelResponse | None = None

        for retry in range(self.max_retries + 1):
            try:
                response = await asyncio.wait_for(
                    provider.generate(request), timeout=self.timeout_seconds
                )
            except ProviderNonRetryableError:
                raise
            except ProviderRetryableError:
                if retry >= self.max_retries:
                    raise
                continue
            except TimeoutError:
                error = ProviderTimeoutError()
                if retry >= self.max_retries:
                    raise error from None
                continue
            except Exception:
                error = ProviderRetryableError()
                if retry >= self.max_retries:
                    raise error from None
                continue

            response.validation = self.validator.validate(response.content)
            response.retry_count = retry
            response.latency_ms = round((perf_counter() - started) * 1000)
            last_response = response
            if response.validation.is_valid:
                return response

        # This branch is only for repeated OutputValidator rejection. Transport,
        # provider-auth, rate-limit and upstream failures are raised above and
        # mapped to clean HTTP errors by FastAPI.
        assert last_response is not None
        last_response.content = SAFE_FALLBACK_CONTENT
        last_response.validation = self.validator.validate(last_response.content)
        last_response.retry_count = self.max_retries
        last_response.latency_ms = round((perf_counter() - started) * 1000)
        return last_response


# ---------------------------------------------------------------------- #
# Runtime configuration & provider selection
# ---------------------------------------------------------------------- #


def _env(name: str, default: str = "") -> str:
    return os.environ.get(name, default)


def _env_float(name: str, default: float) -> float:
    raw = _env(name)
    if not raw:
        return default
    try:
        return float(raw)
    except ValueError:
        return default


def _env_int(name: str, default: int) -> int:
    raw = _env(name)
    if not raw:
        return default
    try:
        return int(raw)
    except ValueError:
        return default


def build_router() -> ModelRouter:
    """Construct the canonical ModelRouter from server-side env vars."""
    provider_kind = _env("COMPANION_MODEL_PROVIDER", "mock").strip().lower()
    timeout = _env_float("COMPANION_MODEL_TIMEOUT_SECONDS", 5.0)
    retries = _env_int("COMPANION_MODEL_MAX_RETRIES", 1)

    if provider_kind == "openai":
        base_url = _env("COMPANION_MODEL_BASE_URL")
        api_key = _env("COMPANION_MODEL_API_KEY")
        model_name = _env("COMPANION_MODEL_NAME", "companion-chat-v1")
        if base_url and api_key:
            from app.domain.providers.openai_compatible import OpenAICompatibleProvider

            adapter = OpenAICompatibleProvider(
                base_url=base_url,
                api_key=api_key,
                model=model_name,
                timeout_seconds=timeout,
            )
            providers: Mapping[Route, ModelProvider] = {route: adapter for route in Route}
            return ModelRouter(
                providers=providers,
                timeout_seconds=timeout,
                max_retries=retries,
            )

    return ModelRouter(timeout_seconds=timeout, max_retries=retries)


def runtime_status(router: ModelRouter) -> dict[str, object]:
    """Return safe provider diagnostics without credentials or upstream URLs."""
    sample = router.providers.get(Route.FAST_CHAT)
    if sample is None:
        return {
            "provider": "unknown",
            "model": "unknown",
            "configured": False,
            "mode": "mock",
        }
    is_openai = getattr(sample, "name", "") == "openai-compatible"
    return {
        "provider": sample.name,
        "model": sample.model,
        "configured": is_openai,
        "mode": "real" if is_openai else "mock",
        "timeout_seconds": router.timeout_seconds,
        "max_retries": router.max_retries,
    }
