import asyncio
import os
from collections.abc import Mapping, Sequence
from time import perf_counter
from typing import Protocol

from .companions import get_continuity_fallback
from .contracts import ModelRequest, ModelResponse, Route, Usage
from .providers.errors import (
    ProviderContentBlockedError,
    ProviderError,
    ProviderNonRetryableError,
    ProviderRetryableError,
    ProviderTimeoutError,
)
from .validation import OutputValidator

SAFE_FALLBACK_CONTENT = get_continuity_fallback("bardera")


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
        fallback_providers: Mapping[Route, Sequence[ModelProvider]] | None = None,
        validator: OutputValidator | None = None,
        timeout_seconds: float = 5.0,
        max_retries: int = 1,
    ) -> None:
        self.providers = dict(providers or {route: MockModelProvider() for route in Route})
        self.fallback_providers = {
            route: tuple(route_providers)
            for route, route_providers in (fallback_providers or {}).items()
        }
        self.validator = validator or OutputValidator()
        self.timeout_seconds = timeout_seconds
        self.max_retries = max(0, max_retries)

    async def generate(self, request: ModelRequest) -> ModelResponse:
        started = perf_counter()
        last_response: ModelResponse | None = None
        last_error: ProviderError | None = None
        content_was_blocked = False
        attempts = 0
        providers = (
            self.providers[request.route],
            *self.fallback_providers.get(request.route, ()),
        )

        for provider in providers:
            for retry in range(self.max_retries + 1):
                attempts += 1
                try:
                    response = await asyncio.wait_for(
                        provider.generate(request), timeout=self.timeout_seconds
                    )
                except ProviderContentBlockedError as error:
                    content_was_blocked = True
                    last_error = error
                    break
                except ProviderNonRetryableError as error:
                    last_error = error
                    break
                except ProviderRetryableError as error:
                    last_error = error
                    if retry < self.max_retries:
                        continue
                    break
                except TimeoutError:
                    last_error = ProviderTimeoutError()
                    if retry < self.max_retries:
                        continue
                    break
                except Exception:
                    last_error = ProviderRetryableError()
                    if retry < self.max_retries:
                        continue
                    break

                response.validation = self.validator.validate(response.content)
                response.retry_count = attempts - 1
                response.latency_ms = round((perf_counter() - started) * 1000)
                last_response = response
                if response.validation.is_valid:
                    return response
                if retry < self.max_retries:
                    continue
                break

        if last_response is not None or content_was_blocked:
            content = get_continuity_fallback(request.character_id)
            return ModelResponse(
                provider="server-fallback",
                model="server-owned-continuity",
                content=content,
                validation=self.validator.validate(content),
                retry_count=max(attempts - 1, 0),
                latency_ms=round((perf_counter() - started) * 1000),
            )

        assert last_error is not None
        raise last_error


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
            fallback_providers: Mapping[Route, Sequence[ModelProvider]] = {}
            fallback_kind = _env("COMPANION_FALLBACK_MODEL_PROVIDER").strip().lower()
            fallback_base_url = _env("COMPANION_FALLBACK_MODEL_BASE_URL")
            fallback_api_key = _env("COMPANION_FALLBACK_MODEL_API_KEY")
            fallback_model = _env("COMPANION_FALLBACK_MODEL_NAME")
            if (
                fallback_kind == "openai"
                and fallback_base_url
                and fallback_api_key
                and fallback_model
            ):
                fallback_adapter = OpenAICompatibleProvider(
                    base_url=fallback_base_url,
                    api_key=fallback_api_key,
                    model=fallback_model,
                    timeout_seconds=timeout,
                )
                fallback_providers = {route: (fallback_adapter,) for route in Route}
            return ModelRouter(
                providers=providers,
                fallback_providers=fallback_providers,
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
    fallbacks = router.fallback_providers.get(Route.FAST_CHAT, ())
    return {
        "provider": sample.name,
        "model": sample.model,
        "configured": is_openai,
        "mode": "real" if is_openai else "mock",
        "timeout_seconds": router.timeout_seconds,
        "max_retries": router.max_retries,
        "fallback_configured": bool(fallbacks),
        "fallback_model": fallbacks[0].model if fallbacks else None,
    }
