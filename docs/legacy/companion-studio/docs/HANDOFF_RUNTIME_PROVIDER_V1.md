# HANDOFF — Runtime Provider v1

**Branch:** `feat/provider-runtime-v1`  
**Base:** `chore/bootstrap-architecture`  
**Date:** 2026-08-07  
**Issue:** #3 — Runtime provider foundation: real FastAPI model adapter + browser E2E  
**PR:** #4

## Resumen

Companion Studio ya tiene una base de runtime real detrás del backend FastAPI:

- `MockModelProvider` sigue siendo el default local determinista.
- `OpenAICompatibleProvider` implementa un provider HTTP real detrás del `ModelProvider` Protocol.
- Vane y su system prompt canónico viven del lado server.
- El frontend usa un `conversation_id` por sesión de browser.
- `/v1/runtime/status` expone diagnostics seguros sin secretos.
- Los errores de provider son typed + sanitized.
- El adapter NO convierte outages/rate limits/timeouts en respuestas HTTP 200.
- `ModelRouter` es dueño del retry policy.
- FastAPI es dueño del HTTP error mapping.
- El safe content fallback queda reservado para rechazo final de `OutputValidator`.

## Arquitectura final

```text
Next.js browser
  -> POST FastAPI /v1/chat
  -> server resolves canonical Vane context
  -> ModelRouter
  -> MockModelProvider OR OpenAICompatibleProvider
  -> typed ProviderError on upstream/runtime failure
  -> bounded retry in ModelRouter
  -> OutputValidator on successful model content
  -> ChatResponse OR safe FastAPI 5xx error
```

No existe un segundo core backend en Next.js.

## Provider selection

Server-side env vars:

```text
COMPANION_MODEL_PROVIDER=mock|openai
COMPANION_MODEL_BASE_URL=
COMPANION_MODEL_API_KEY=
COMPANION_MODEL_NAME=companion-chat-v1
COMPANION_MODEL_TIMEOUT_SECONDS=5.0
COMPANION_MODEL_MAX_RETRIES=1
COMPANION_CORS_ORIGINS=http://localhost:3000
```

Comportamiento:

- `mock` -> `MockModelProvider`.
- `openai` + base URL + API key -> `OpenAICompatibleProvider`.
- `openai` sin credenciales -> fallback local a mock.
- API keys nunca salen del backend.
- `.env.example` contiene placeholders solamente.

## Server-owned Vane

`app/domain/companions.py` es la fuente server-side del system prompt canónico de Vane.

`/v1/chat` resuelve `character_id="vane"` y prepende un `MessageInput(role="system")` antes del mensaje del usuario.

El cliente no puede enviar un arbitrary system prompt.

La personalidad mantiene la dirección SPECT: adulta, caótica, espontánea, divertida, creativa, curiosa, afectuosa sin sumisión automática, sensual no explícita, transparente sobre ser una companion IA cuando se le pregunta directamente.

## Typed provider errors

Archivo: `app/domain/providers/errors.py`.

Jerarquía relevante:

```text
ProviderError
├── ProviderRetryableError
│   ├── ProviderTimeoutError
│   ├── ProviderConnectError
│   ├── ProviderRateLimitError
│   ├── ProviderServerError
│   └── ProviderInvalidResponseError
└── ProviderNonRetryableError
    ├── ProviderAuthError
    └── ProviderRequestError
```

Los errores llevan solamente `code` + `safe_message` controlados. No contienen raw upstream body, API key, Authorization header, provider URL sensible ni stack interno.

## Retry semantics

`ModelRouter` aplica `COMPANION_MODEL_MAX_RETRIES` realmente sobre fallas de provider.

### Retryable

- timeout
- connection / request transport failure
- upstream HTTP 429
- upstream HTTP 5xx
- malformed JSON
- non-dict upstream JSON
- empty / invalid `choices`
- missing/invalid `message.content`
- defensive unknown provider exception

### Non-retryable

- upstream HTTP 401
- upstream HTTP 403
- other upstream 4xx request/config failures

Upstream 401/403 nunca se exponen al browser como user-auth 401/403.

### Recovery example

Con `max_retries=1`:

```text
attempt 0 -> provider 429
attempt 1 -> provider 200 valid content
result    -> real assistant content, retry_count=1
```

El mismo patrón está testeado para upstream 5xx -> 200.

## HTTP mapping

Provider/runtime failure agotada se expresa como error HTTP, no como fake success.

| Failure | HTTP | Safe code |
|---|---:|---|
| timeout exhausted | 504 | `provider_timeout` |
| connect/network exhausted | 503 | `provider_connect_failed` |
| upstream 429 exhausted | 503 | `provider_rate_limited` |
| upstream 5xx exhausted | 503 | `provider_server_error` |
| upstream 401/403 | 503 | `provider_config_error` |
| other upstream 4xx | 503 | `provider_config_error` |
| malformed/invalid upstream response exhausted | 502 | `provider_invalid_response` |
| unknown retryable provider failure exhausted | 503 | `provider_unavailable` |

Response shape:

```json
{
  "detail": {
    "code": "provider_connect_failed",
    "message": "Model provider temporarily unavailable."
  }
}
```

No raw provider error data se devuelve al browser.

## Safe fallback policy

`SAFE_FALLBACK_CONTENT` sigue existiendo:

```text
No pude responder con seguridad esta vez. Probemos de nuevo.
```

Se usa únicamente cuando el provider respondió con contenido y `OutputValidator` lo rechaza durante todo el retry budget.

No se usa para ocultar:

- timeout
- network failure
- provider outage
- rate limit
- provider auth/config failure
- malformed upstream protocol

## Runtime status

`GET /v1/runtime/status` devuelve información segura:

```json
{
  "provider": "mock",
  "model": "mock-companion-v1",
  "configured": false,
  "mode": "mock",
  "timeout_seconds": 5.0,
  "max_retries": 1
}
```

Con provider real configurado, `mode` pasa a `real`.

Nunca devuelve API key, Authorization, secretos, stack ni URL sensible.

## Browser session id

Frontend: `apps/web/lib/session.ts`.

- UUID por browser tab/session.
- guardado en `sessionStorage`.
- refresh mantiene la misma sesión.
- otra tab obtiene otra sesión.
- no se presenta como persistent memory.

## Browser E2E verificado por GLM antes del handoff del auditor fix

Normal path:

1. home render
2. onboarding 5/5
3. chat open
4. send message
5. Next.js -> FastAPI `/v1/chat`
6. response rendered in bubble
7. validation OK visible in dev
8. no CORS/page errors
9. mobile viewport OK

Error paths:

- API down -> graceful UI error.
- Broken configured provider -> FastAPI 503 + safe error body -> frontend `res.ok=false` -> graceful chat error state.

## Automated tests

CI on PR #4 after the auditor fix is green for both `api` and `web`.

Backend coverage includes:

- typed adapter classification for 401/403/429/5xx/timeouts/connect errors
- malformed/empty/invalid upstream responses
- API key stays in Authorization header, not payload
- 429 -> retry -> 200 recovery with `retry_count=1`
- 5xx -> retry -> 200 recovery with `retry_count=1`
- timeout exhaustion -> HTTP 504
- connection exhaustion -> HTTP 503
- auth/config errors -> no retry, HTTP 503
- invalid upstream response -> bounded retry, HTTP 502
- final OutputValidator rejection -> safe content fallback HTTP 200
- error bodies contain no secret/header/stack/upstream URL material

Frontend CI covers install, lint and build.

## Changed runtime files

Backend:

- `apps/api/app/domain/providers/errors.py`
- `apps/api/app/domain/providers/openai_compatible.py`
- `apps/api/app/domain/router.py`
- `apps/api/app/main.py`
- `apps/api/app/domain/companions.py`
- `apps/api/tests/test_openai_provider.py`
- `apps/api/tests/test_provider_errors.py`
- `apps/api/tests/test_runtime.py`
- `apps/api/pyproject.toml`

Frontend:

- `apps/web/lib/session.ts`
- `apps/web/lib/api.ts`
- `apps/web/components/ChatPanel.tsx`
- `apps/web/lib/companion.ts`

Docs/config:

- `.env.example`
- `docs/adr/0006-openai-compatible-provider.md`
- `docs/HANDOFF_RUNTIME_PROVIDER_V1.md`

## Secrets verification

Tracked source must contain:

- no `.env`
- no real model API key
- no private visual originals
- no GitHub PAT

Tests may use obviously fake sentinel strings only to verify they do not leak.

## Known limitations

1. Runtime defaults to mock until a real OpenAI-compatible endpoint is configured.
2. No persistent memory yet.
3. `/v1/chat` remains single-turn at the backend contract level.
4. Mock provider still uses its generic host-style canned reply.
5. No auth, payment, TTS, image/video generation or marketplace in this milestone.
6. No VPS deployment in this milestone.

## Recommended next staging milestone

After PR #4 is merged:

1. configure one real provider in a controlled staging runtime;
2. exercise Vane character quality against real responses;
3. add structured provider observability and basic rate limiting;
4. then prepare persistent conversation/history and memory architecture;
5. deploy staging only when the runtime provider path is actually being exercised outside local/CI.

## Issue #3 compliance

| Criterion | Status |
|---|---|
| FastAPI canonical backend | ✅ |
| Mock fallback | ✅ |
| Real provider behind Protocol | ✅ |
| Server-side secrets only | ✅ |
| No paid model in tests | ✅ |
| Server-owned Vane context | ✅ |
| Browser send flow | ✅ |
| Per-session conversation id | ✅ |
| Safe runtime diagnostics | ✅ |
| Typed provider errors | ✅ |
| Real bounded retry semantics | ✅ |
| Safe 5xx mappings | ✅ |
| No scope creep | ✅ |
