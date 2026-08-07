# HANDOFF — Runtime Provider v1

**Branch:** `feat/provider-runtime-v1`
**Base:** `chore/bootstrap-architecture`
**Date:** 2026-08-07
**Issue:** [#3 — Runtime provider foundation: real FastAPI model adapter + browser E2E](https://github.com/Rybjuani/Companion-Studio/issues/3)

## Resumen

Se construyó el runtime provider foundation: un adapter `OpenAICompatibleProvider`
real detrás del `ModelProvider` Protocol existente, selección de provider por
env vars server-side, sistema de companion Vane propiedad del server, CORS de
dev, endpoint de diagnósticos seguro, `conversation_id` por sesión de browser,
y E2E de browser real que envía un mensaje y renderiza la respuesta. El mock
sigue siendo el fallback local determinista por defecto.

## Architecture changes

### Nuevo: `OpenAICompatibleProvider` (`app/domain/providers/openai_compatible.py`)
- Implementa el `ModelProvider` Protocol (sin cambios al Protocol).
- Habla el wire format de OpenAI Chat Completions (`POST /chat/completions`,
  `Authorization: Bearer <key>`). El dominio no importa ningún SDK; el adapter
  es dueño de su `httpx.AsyncClient`.
- **Nunca levanta una excepción al router.** Toda falla (network, HTTP 4xx/5xx,
  timeout, JSON malformado, `choices` vacío, connect error) se traduce en un
  `ModelResponse` con el string seguro en español
  `"No pude responder con seguridad esta vez. Probemos de nuevo."`. Esto
  garantiza que ni stack trace ni secretos puedan filtrarse.

### Nuevo: `build_router()` factory (`app/domain/router.py`)
- Lee `COMPANION_MODEL_*` env vars en startup.
- `mock` (default) → `MockModelProvider` para todas las rutas.
- `openai` + `BASE_URL` + `API_KEY` presentes → `OpenAICompatibleProvider`
  para todas las rutas.
- `openai` sin credenciales → fallback a mock (install/lint/test/run nunca
  requieren key real).

### Nuevo: `runtime_status()` + `GET /v1/runtime/status`
- Retorna `{provider, model, configured, mode, timeout_seconds, max_retries}`.
- **No** retorna: API key, Authorization header, URL completa con query
  sensible, stack interno.

### Nuevo: Server-owned Vane system prompt (`app/domain/companions.py`)
- `get_system_prompt(character_id)` resuelve el system prompt canónico de Vane.
- El handler `/v1/chat` lo inyecta como `MessageInput(role="system")` al
  frente de `ModelRequest.messages`. El cliente **nunca** envía system prompt.
- `ModelRequest` / `ChatRequest` contracts sin cambios (`extra="forbid"` respetado).

### Nuevo: CORS (`app/main.py`)
- `CORSMiddleware` con `COMPANION_CORS_ORIGINS` (default `http://localhost:3000`).
- No es wildcard en producción; orígenes separados por coma.

### Handler robustez (`app/main.py`)
- `try/except RuntimeError` alrededor de `router.generate()` → si el router
  agota retries por timeout, devuelve `ModelResponse` seguro en vez de 500.

### Frontend
- `lib/session.ts`: `getConversationId()` — UUID + `sessionStorage`. Reemplaza
  el `conversation_id="web-session"` compartido. No es memoria persistente.
- `lib/api.ts`: usa `getConversationId()`.
- `components/ChatPanel.tsx`: fetch de `/v1/runtime/status` on mount; header
  muestra `provider: <name> · <mode>` dinámicamente (desde el response real).
- `lib/companion.ts`: `systemPrompt` **eliminado** del cliente. Solo campos
  display-only (name, greeting, quickPrompts, portrait, etc.).

### ADR
- `docs/adr/0006-openai-compatible-provider.md` — documenta la decisión.

## Changed files

### Backend (apps/api)
- `app/main.py` — CORS, build_router(), system prompt injection, /v1/runtime/status, try/except.
- `app/domain/router.py` — `build_router()` + `runtime_status()` factories.
- `app/domain/companions.py` — **nuevo** — Vane system prompt registry.
- `app/domain/providers/__init__.py` — **nuevo** — providers package.
- `app/domain/providers/openai_compatible.py` — **nuevo** — adapter.
- `pyproject.toml` — `httpx>=0.27` movido a runtime deps; version 0.2.0.
- `tests/test_openai_provider.py` — **nuevo** — 11 tests (mock HTTP).
- `tests/test_runtime.py` — **nuevo** — 10 tests (handler, status, build_router).

### Frontend (apps/web)
- `lib/session.ts` — **nuevo** — per-browser-session conversation_id.
- `lib/api.ts` — usa `getConversationId()`.
- `components/ChatPanel.tsx` — runtime status fetch + dynamic provider label.
- `lib/companion.ts` — `systemPrompt` removed (server-owned now).

### Docs / config
- `.env.example` — `COMPANION_MODEL_*` + `COMPANION_CORS_ORIGINS` placeholders.
- `docs/adr/0006-openai-compatible-provider.md` — **nuevo** ADR.

## Provider selection logic

```
COMPANION_MODEL_PROVIDER=mock (default)
  → MockModelProvider for all routes
  → mode: "mock", configured: false

COMPANION_MODEL_PROVIDER=openai
  + COMPANION_MODEL_BASE_URL set
  + COMPANION_MODEL_API_KEY set
    → OpenAICompatibleProvider for all routes
    → mode: "real", configured: true
  + missing base_url or api_key
    → fallback to MockModelProvider (graceful)
    → mode: "mock", configured: false
```

## Env vars

| Var | Default | Purpose |
|---|---|---|
| `COMPANION_MODEL_PROVIDER` | `mock` | `mock` or `openai` |
| `COMPANION_MODEL_BASE_URL` | (empty) | OpenAI-compatible base URL |
| `COMPANION_MODEL_API_KEY` | (empty) | Server-side API key (never client) |
| `COMPANION_MODEL_NAME` | `companion-chat-v1` | Model name to request |
| `COMPANION_MODEL_TIMEOUT_SECONDS` | `5.0` | Per-call timeout |
| `COMPANION_MODEL_MAX_RETRIES` | `1` | Bounded retries |
| `COMPANION_CORS_ORIGINS` | `http://localhost:3000` | Comma-separated allowed origins |

## Real vs Mock

| Componente | Estado |
|---|---|
| `OpenAICompatibleProvider` | Real (cuando se configura env) |
| `MockModelProvider` | Real (default, fallback determinista) |
| `build_router()` selection | Real (env-driven) |
| Server-side Vane system prompt | Real (injects `MessageInput(role="system")`) |
| `/v1/runtime/status` | Real (safe diagnostics) |
| CORS | Real (dev origin) |
| `conversation_id` per session | Real (UUID + sessionStorage) |
| Chat response rendering | Real (browser E2E verified) |
| Error state | Real (graceful fallback on API down) |

## Exact commands executed + results

```bash
# Backend
cd apps/api && python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"
.venv/bin/ruff check .          # → All checks passed!
.venv/bin/ruff format --check . # → 13 files already formatted
.venv/bin/pytest tests/ -q      # → 26 passed

# Frontend
pnpm install
pnpm --dir apps/web lint        # → ✔ No ESLint warnings or errors
pnpm --dir apps/web build       # → ○ (Static) prerendered

# API smoke
curl localhost:8000/v1/runtime/status
# → {"provider":"mock","model":"mock-companion-v1","configured":false,"mode":"mock",...}

curl -X POST localhost:8000/v1/chat -H "Content-Type: application/json" \
  -d '{"message":"hola vane","character_id":"vane"}'
# → provider: mock, content: "Te leo. Soy la anfitriona de prueba...", validation.is_valid: true
```

## Browser E2E evidence

Servicios: FastAPI en :8000, Next.js en :3000. Browser: agent-browser.

1. **Home** ✅ — renderiza, sin errores de consola.
2. **Onboarding** ✅ — click "Conocer a Vane" → 5 decisiones completadas.
3. **Chat view** ✅ — header muestra dinámicamente `provider: mock · mock`
   (fetcheado de `/v1/runtime/status`).
4. **Send message** ✅ — input "Hola Vane, contame algo" → click Enviar.
5. **Response rendered** ✅ — bubble: "Te leo. Soy la anfitriona de prueba
   y recibí: "Hola Vane, contame algo" ¿Seguimos desde ahí?"
6. **Dev validation** ✅ — "Desarrollo: validación de salida OK".
7. **Error state** ✅ — API detenida → send → bubble "No pude responder
   ahora. ¿Probamos de nuevo?" + "Error: Failed to fetch".
8. **Mobile** ✅ — viewport 390×844: hero + heading + button renderizan.
9. **CORS** ✅ — sin errores CORS en consola del browser.
10. **Console errors** ✅ — ninguna en todo el flujo.

## Runtime status behavior

`GET /v1/runtime/status` retorna solo campos seguros:

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

Con `COMPANION_MODEL_PROVIDER=openai` + credenciales:
```json
{
  "provider": "openai-compatible",
  "model": "companion-chat-v1",
  "configured": true,
  "mode": "real",
  "timeout_seconds": 5.0,
  "max_retries": 1
}
```

**Nunca** retorna: `api_key`, `authorization`, URL completa, stack.

## Timeout / retry behavior

- `ModelRouter.timeout_seconds` (default 5.0, override via env).
- `ModelRouter.max_retries` (default 1, override via env).
- El router envuelve `provider.generate()` en `asyncio.wait_for(timeout)`.
- Timeout → retry; tras agotar retries → `RuntimeError("model_provider_timeout")`.
- El handler atrapa `RuntimeError` → `ModelResponse` seguro (no 500).
- El adapter tiene su propio `httpx` timeout (mismo valor); atrapa
  `httpx.TimeoutException` internamente → `ModelResponse` seguro.

## Error mapping

| Provider failure | Result |
|---|---|
| httpx timeout | safe `ModelResponse` (adapter catches) |
| HTTP 401/403 | safe `ModelResponse` (adapter catches) |
| HTTP 429 | safe `ModelResponse` (adapter catches) |
| HTTP 5xx | safe `ModelResponse` (adapter catches) |
| Malformed JSON | safe `ModelResponse` (adapter catches) |
| Empty `choices` | safe `ModelResponse` (adapter catches) |
| Connect error | safe `ModelResponse` (adapter catches) |
| Router timeout after retries | handler catches `RuntimeError` → safe response |

En ningún caso se filtra stack trace o secreto.

## Secrets verification

```bash
# No .env tracked
git ls-files | grep -E "\.env$"   # → (empty)

# No API keys in tracked files
git grep -iE "sk-[a-z0-9]{20}|api_key.*=.*['\"][a-z0-9]{20}" -- '.env.example' ':!tests'
# → (no real keys; .env.example has empty COMPANION_MODEL_API_KEY=)

# Runtime status doesn't leak keys (verified by test_runtime_status_no_secret_leak_for_openai)
```

## Known limitations

1. **Chat es mock por defecto.** Para chat real LLM, setear
   `COMPANION_MODEL_PROVIDER=openai` + `BASE_URL` + `API_KEY` + `MODEL_NAME`.
2. **Sin memoria persistente.** `conversation_id` es por sesión de browser
   (sessionStorage); no sobrevive cierre de tab. No es memoria entre sesiones.
3. **El mock se identifica como "anfitriona"** sin importar `character_id` —
   el `MockModelProvider` ignora el system prompt. Un provider real sí lo
   usará. Corregible con un cambio mínimo al mock o con provider real.
4. **Sin multi-turno en el backend.** `/v1/chat` recibe un solo `message`;
   el router no mantiene historial. Multi-turno real requiere extensión del
   contract o estado de conversación server-side (futuro).
5. **Una sola companion (Vane).** No hay marketplace ni múltiples characters
   (per SPECT §4 y Issue #3 #10).

## Recommended next staging milestone

1. **Multi-turno server-side**: extender `ChatRequest` con `messages: list[MessageInput]`
   opcional, o mantener estado de conversación en backend (con `conversation_id`).
2. **Memoria persistente**: implementar las capas de memoria de SPECT §6.4
   (profile/character/temporal) sobre PostgreSQL.
3. **Provider real con LLM**: configurar `COMPANION_MODEL_*` con un endpoint
   OpenAI-compatible real y validar respuestas en personaje de Vane.
4. **Auth + rate limiting**: antes de producción.
5. **Observabilidad**: logging estructurado + métricas de provider latency/errores.

## Issue #3 compliance

| Criterio | Cumplido |
|---|---|
| FastAPI canonical backend | ✅ |
| MockModelProvider default fallback | ✅ |
| Real provider behind Protocol | ✅ `OpenAICompatibleProvider` |
| No client-side API keys | ✅ |
| No paid model in tests | ✅ `httpx.MockTransport` |
| Server-owned Vane system prompt | ✅ |
| Browser send flow verified + CORS | ✅ |
| Per-browser-session conversation_id | ✅ |
| Safe runtime diagnostics | ✅ `/v1/runtime/status` |
| Preserve cyber-noir UI / one companion | ✅ |
