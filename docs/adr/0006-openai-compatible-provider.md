# ADR 0006 — OpenAI-compatible model provider adapter

Date: 2026-08-07
Status: Proposed
Extends: ADR 0002 (Model Router)

## Context

The MVP slice merged in `integration/glm-v1` ships a `MockModelProvider`
that returns canned Spanish strings. To reach a production-ready runtime
foundation (Issue #3), Companion Studio needs a real, swappable model
provider behind the existing `ModelRouter` / `ModelProvider` Protocol —
without re-introducing a second backend (no Next.js `/api/chat` core),
without exposing API keys client-side, and without breaking the
deterministic local fallback that keeps install/lint/test/run free of
any paid dependency.

SPECT §11.3 explicitly endorses "API compatible con OpenAI como interfaz
interna" and "capacidad de sustituir proveedores." ADR 0002 already
mandates that the domain depends on `ModelProvider`, not on SDKs, and
that routes map to providers by configuration.

## Decision

Add one real provider adapter, `OpenAICompatibleProvider`, that:

1. Implements the existing `ModelProvider` Protocol (`name`, `model`,
   `async def generate(request) -> ModelResponse`) — no Protocol change.
2. Speaks the OpenAI Chat Completions wire format
   (`POST /v1/chat/completions`, `Authorization: Bearer <key>`) against
   any compatible endpoint. The domain layer imports no provider SDK;
   the adapter owns its `httpx.AsyncClient`.
3. Is selected by **server-side env only** (`COMPANION_MODEL_PROVIDER`,
   `COMPANION_MODEL_BASE_URL`, `COMPANION_MODEL_API_KEY`,
   `COMPANION_MODEL_NAME`). `mock` remains the default. When
   `provider=openai` but base URL or key is missing, the factory falls
   back to mock — so the project runs fully without credentials.
4. **Never raises to the router.** Every failure (network error, HTTP
   4xx/5xx, timeout, malformed JSON, empty `choices`) is translated into
   a safe `ModelResponse` carrying the canonical Spanish fallback string.
   This guarantees no stack trace or secret can leak through the API.
5. Is covered by unit tests using `httpx.MockTransport` — automated
   tests never call a paid model (success, timeout, 401, 403, 429, 5xx,
   malformed JSON, empty choices, connect error, validator integration).

Additionally:

- The **canonical Vane system prompt** is owned by the server
  (`app/domain/companions.py`), resolved from `character_id`. The
  `/v1/chat` handler prepends a `MessageInput(role="system")` to the
  `ModelRequest`. The client never supplies a system prompt.
  `ModelRequest` / `ChatRequest` contracts are unchanged.
- A safe `GET /v1/runtime/status` endpoint reports configured
  provider/model/mode/timeout/retries **without** exposing API keys,
  Authorization headers, full provider URLs with sensitive query, or
  internal stacks.
- CORS is added (`CORSMiddleware`) with a single dev origin
  (`COMPANION_CORS_ORIGINS`, default `http://localhost:3000`) — not a
  wildcard production config.
- The router's existing retry/timeout/validator logic is preserved
  unchanged. The handler wraps `router.generate()` in a `try/except
  RuntimeError` to convert the router's timeout-after-retries into a
  safe `ModelResponse` rather than a 500.

## Consequences

- **Positive:** Real LLM runtime is achievable by setting four env vars.
  Swapping providers (e.g. to a self-hosted vLLM, Together, OpenRouter)
  needs no code change — only env. The domain stays SDK-free. Local dev
  and CI remain free and deterministic (mock default).
- **Positive:** No stack trace or secret can leak: the adapter catches
  everything; the handler catches `RuntimeError`; the status endpoint
  publishes only non-secret fields.
- **Negative:** The OpenAI wire format is a coupling. If a future
  provider speaks a different protocol, a second adapter is needed
  (acceptable — that is the point of the Protocol abstraction).
- **Negative:** `httpx` becomes a runtime dependency of the adapter
  (it was already a dev dependency for tests). This is acceptable: it is
  a thin, well-maintained async HTTP client with no transitive SDK
  bloat. `httpx` is added to the `dependencies` (not just `dev`) of
  `apps/api/pyproject.toml`.

## Compliance with Issue #3

| Criterion | Met by |
|---|---|
| FastAPI stays canonical backend | No new Next.js API route; chat via `/v1/chat` |
| MockModelProvider default fallback | `build_router()` defaults to mock |
| One real provider behind Protocol | `OpenAICompatibleProvider` |
| No client-side API keys | All `COMPANION_MODEL_*` are server-only; `.env.example` placeholders |
| No paid model in tests | `httpx.MockTransport` fakes the endpoint |
| Server-owned Vane system prompt | `app/domain/companions.py` + handler injection |
| Browser send flow verified | CORS added; E2E in HANDOFF |
| Per-browser-session conversation_id | `lib/session.ts` (UUID + sessionStorage) |
| Safe runtime diagnostics | `GET /v1/runtime/status` (no secrets) |
| Preserve cyber-noir UI / one companion | No UI redesign; Vane only |
