import asyncio
import os
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


# ---------------------------------------------------------------------- #
# Runtime configuration & provider selection
# ---------------------------------------------------------------------- #
#
# Provider selection is server-side and env-driven (ADR 0006). The mock
# provider remains the default local fallback; a real OpenAI-compatible
# adapter is constructed only when COMPANION_MODEL_PROVIDER=openai and a
# base URL + API key are present. The router never imports a provider
# SDK in the domain layer — the adapter owns its HTTP client.


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
    """Construct the canonical `ModelRouter` from server-side env vars.

    Env vars (see `.env.example`):
      - COMPANION_MODEL_PROVIDER: ``mock`` (default) or ``openai``.
      - COMPANION_MODEL_BASE_URL: OpenAI-compatible base URL.
      - COMPANION_MODEL_API_KEY: server-side API key (never client).
      - COMPANION_MODEL_NAME: model name to request.
      - COMPANION_MODEL_TIMEOUT_SECONDS: per-call timeout (default 5.0).
      - COMPANION_MODEL_MAX_RETRIES: bounded retries (default 1).

    When ``provider=openai`` but the base URL or API key is missing, the
    factory falls back to mock so the app still runs locally without
    credentials. This guarantees install/lint/test/run never require a
    real key (Issue #3 #2/#4).
    """
    provider_kind = _env("COMPANION_MODEL_PROVIDER", "mock").strip().lower()
    timeout = _env_float("COMPANION_MODEL_TIMEOUT_SECONDS", 5.0)
    retries = _env_int("COMPANION_MODEL_MAX_RETRIES", 1)

    if provider_kind == "openai":
        base_url = _env("COMPANION_MODEL_BASE_URL")
        api_key = _env("COMPANION_MODEL_API_KEY")
        model_name = _env("COMPANION_MODEL_NAME", "companion-chat-v1")
        if base_url and api_key:
            # Imported lazily so the domain layer has no hard dependency
            # on the adapter module at import time; mock-only installs
            # never touch httpx through this path.
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

    # Default: deterministic mock for every route.
    return ModelRouter(timeout_seconds=timeout, max_retries=retries)


def runtime_status(router: ModelRouter) -> dict[str, object]:
    """Return a safe diagnostics dict for the runtime status endpoint.

    Reports the configured provider/model and mode without revealing
    any secret: no API key, no Authorization header, no full provider
    URL with sensitive query string, no internal stack. The shape is
    stable and suitable for a public-ish dev diagnostics endpoint.
    """
    # Sample the provider wired to fast_chat as the representative one.
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
