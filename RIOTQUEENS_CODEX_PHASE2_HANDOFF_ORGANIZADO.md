# RiotQueens — handoff operativo canónico

**Actualizado:** 2026-08-15
**Repositorio canónico:** `/home/rybjuani/Escritorio/RiotQueens-worktree`
**Fuente funcional:** `SPECT.md` · **decisiones:** `docs/DECISION_REGISTER.md` · **reglas:** `AGENTS.md`

## Estado actual verificado

- El worktree es el único código, runtime y documentación vigente. El directorio
  El patrimonio creativo seleccionado está dentro de
  `assets/private/selected/`; no existe un segundo repo necesario.
- Las cinco Queens son canónicas; sólo Bardera está implementada en runtime.
- Bardera texto tiene `TECHNICAL_PRE_RELEASE_PASS` con Gemini 3.1 Flash Lite:
  12/12 reproducible por API, sin hard-fails, truncaciones ni falsas promesas.
  Aún no es deploy público ni aprobación para otras Queens/capacidades.
- Flow y Mage son fuentes externas de producción visual del owner. La biblioteca
  pública actual contiene sólo previews allowlisted y hasheados; no hay media
  privada, uploads, pagos ni generación publicada.

## C3 — identidad durable / Auth0

### Implementado en HEAD

- `riotqueens_user_id` es `users.id` UUID propio y durable.
- `external_identities(provider, provider_subject)` vincula `Auth0 sub` con el
  UUID interno y exige unicidad; email, browser ID y `sub` no son PK de dominio.
- FastAPI valida access tokens con JWKS, RS256, issuer, audience, `exp` e `iat`;
  falla cerrado y resuelve el Principal antes de autorización de dominio.
- Auth0 contiene sólo IAM/sesión. Clickwrap +18, conversaciones, memoria, tiers,
  entitlements, media, preferencias sensibles y estado de Queen quedan propios.
- La migración de identidad es `ops/migrations/0001_identity.sql`.
- Web usa `@auth0/nextjs-auth0` v4 con `/auth/*`; Caddy conserva `/api/*` para
  FastAPI y el resto para Next.js. El token de sesión se entrega por `/api/token`
  sólo al navegador ya autenticado.

### Tenant no productivo verificado

- tenant: `riotqueens-ai-ca`
- región: Canadá (`CA`)
- dominio: `riotqueens-ai-ca.ca.auth0.com`
- entorno: Development
- aplicación: `riotqueens-ai`, Regular Web Application / Next.js

### Gates pendientes

1. Crear la Custom API/Auth0 Audience y cargar los valores no secretos/secretos
   únicamente en `.env` local; ejecutar la migración en PostgreSQL antes de
   activar auth para usuarios de prueba.
2. Producción continúa bloqueada hasta confirmación escrita de Auth0 sobre
   admisibilidad del producto +18 ficticio, subprocesadores/transferencias del
   tenant CA y mecanismo aplicable desde Argentina.
3. Clickwrap versionado, persistencia durable de conversación/memoria, media
   privada, pagos y tiers permanecen fuera de este corte.

## Configuración Auth0 acordada

- Application Origin: `https://riotqueens.ai`
- Next dev directo (`APP_BASE_URL`): `http://localhost:3000`
- entrada Caddy local integrada: `http://localhost`
- `https://riotqueens.ai` sólo se habilita como origen de despliegue cuando la
  release por dominio/TLS haya sido verificada; no se presenta aquí como
  despliegue ya validado.
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

Completar C3 no productivo: crear en Auth0 la Custom API `RiotQueens API` con
identifier `https://api.riotqueens.ai`, configurar URLs/orígenes acordados,
llenar `.env` local sin exponer secretos, ejecutar `0001_identity.sql` sobre
PostgreSQL y realizar smoke de login/token/API sin desplegar producción.
