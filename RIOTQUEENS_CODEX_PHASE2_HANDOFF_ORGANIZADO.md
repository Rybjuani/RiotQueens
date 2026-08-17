# RiotQueens — handoff operativo canónico

**Actualizado:** 2026-08-17
**Repositorio canónico:** `/home/rybjuani/Escritorio/RiotQueens-worktree`
**Fuente funcional:** `SPECT.md` · **decisiones:** `docs/DECISION_REGISTER.md` · **reglas:** `AGENTS.md`

## Estado actual verificado

- El worktree es el único código, runtime y documentación vigente. El patrimonio
  creativo seleccionado está en `assets/private/selected/`; no existe un segundo
  repo necesario.
- Las cinco Queens son canónicas; sólo Bardera está implementada en runtime.
- **Casting de voz Bardera cerrado** (2026-08-17, glosario): no reabrir matriz ni
  promover Dolphin Venice (falla de identidad/dossier pese a PASS heurístico).
- **Primario de producto:** Gemini 3.1 Flash Lite (OpenAI-compatible AI Studio).
- **Fallback de lab:** Euryale 70B vía OpenRouter (`sao10k/l3.3-euryale-70b`).
- **UI preprod:** diseño Qwen transplantado a Next.js (hero “NO TE CLAVA EL VISTO”,
  Archivo Black / JetBrains Mono, rosa/cyan/bone).
- **Preprod HTTP por IP:** `http://148.113.167.121` — runtime real Gemini + fallback.
- **Persistencia durable:** migraciones `0002` (conversaciones/mensajes/memorias) y
  `0003` (clickwrap append-only). Con `DATABASE_URL`, la API usa
  `PostgresConversationStore` / `PostgresMemoryStore`.
- **Clickwrap +18 (ADR 0004):** UI + `GET/POST /v1/consent/*`; gate de chat cuando
  auth está habilitada. Paquete de versiones baseline `2026-08-09`.
- Flow y Mage son fuentes externas de producción visual del owner. La biblioteca
  pública actual contiene sólo previews allowlisted y hasheados; no hay media
  privada, uploads, pagos ni generación publicada.

## Hecho hoy (2026-08-17) — corte operativo

1. Docs alineados al casting cerrado y preprod real (Gemini/Euryale).
2. Runtime real activado en VPS (de `mock` → `mode=real`).
3. UI Qwen transplantada y desplegada.
4. Stores durables Postgres + clickwrap versionado en código y migraciones.
5. Usuario de prueba Auth0 creado vía Database Connection signup
   (`test.preprod+rq@example.com`) — password solo en canal operador, no en Git.
6. M2M client_credentials contra audience API **OK**; Management API **sin scopes**
   (no se pueden editar Application callbacks ni crear users vía Management).
7. **DNS/TLS no hechos:** `riotqueens.ai` está **disponible / no registrado**.

## C3 — identidad durable / Auth0

### Implementado en HEAD

- `riotqueens_user_id` es `users.id` UUID propio y durable.
- `external_identities(provider, provider_subject)` vincula `Auth0 sub` con el
  UUID interno y exige unicidad; email, browser ID y `sub` no son PK de dominio.
- FastAPI valida access tokens con JWKS, RS256, issuer, audience, `exp` e `iat`;
  falla cerrado y resuelve el Principal antes de autorización de dominio.
- Tras el login, el Principal carga la última aceptación clickwrap vigente.
- Auth0 contiene sólo IAM/sesión. Clickwrap +18, conversaciones, memoria, tiers,
  entitlements, media, preferencias sensibles y estado de Queen quedan propios.
- Migraciones: `0001_identity.sql`, `0002_conversations_memories.sql`,
  `0003_clickwrap_acceptances.sql`.
- Web usa `@auth0/nextjs-auth0` v4 con `/auth/*`; Caddy conserva `/api/*` para
  FastAPI y el resto para Next.js. El token de sesión se entrega por `/api/token`
  sólo al navegador ya autenticado.

### Tenant no productivo verificado

- tenant: `riotqueens-ai-ca`
- región: Canadá (`CA`)
- dominio: `riotqueens-ai-ca.ca.auth0.com`
- entorno: Development
- aplicación: `riotqueens-ai`, Regular Web Application / Next.js
- Custom API audience: `https://api.riotqueens.ai`

### Gates pendientes (Auth0 / DNS)

1. **Registrar** `riotqueens.ai` y crear `A` → `148.113.167.121` (+ `www` si aplica).
2. En Auth0 Application, configurar Callback / Logout / Web Origins para IP y dominio.
3. En VPS `runtime.env`: Auth0 secrets + `RIOTQUEENS_AUTH_ENABLED=true` +
   `NEXT_PUBLIC_AUTH_ENABLED=true` (rebuild web) + `APP_BASE_URL` coherente.
4. Smoke browser: Universal Login → clickwrap → chat Bardera.
5. Confirmación escrita de Auth0 sobre admisibilidad +18 ficticio antes de producción.
6. Media privada, pagos y tiers comerciales siguen fuera de este corte.

## Configuración Auth0 acordada

- Application Origin prod objetivo: `https://riotqueens.ai`
- Next dev (`APP_BASE_URL`): `http://localhost:3000`
- preprod IP: `http://148.113.167.121` (hasta DNS)
- Custom API identifier/audience: `https://api.riotqueens.ai`
- issuer: `https://riotqueens-ai-ca.ca.auth0.com/`
- JWKS: `https://riotqueens-ai-ca.ca.auth0.com/.well-known/jwks.json`

Los valores secretos jamás se incluyen en Git, handoffs, logs ni chat.

## Reglas de continuidad

- Antes de cambiar canon, leer `AGENTS.md`, `SPECT.md`, este archivo y ADRs.
- No reducir personalidad de una Queen para acomodar refusals de un provider;
  el provider es reemplazable. Repetir el benchmark completo tras cada cambio.
- No importes el pool creativo por completitud. Migrar sólo código/configuración
  vigente, assets autorizados con procedencia o evidencia imprescindible.
- El único `.env` operativo es el de la raíz del worktree; nunca copiar ni
  commitear variantes históricas o secretos.

## Próxima acción operativa única

**Owner:** registrar `riotqueens.ai` y configurar Auth0 Application URLs.  
**Ops (después):** `SITE_ADDRESS=riotqueens.ai`, TLS Caddy, flip auth flags en VPS,
smoke HTTPS + login + clickwrap + chat durable.
