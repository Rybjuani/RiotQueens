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
- **Preprod:** release `7448898` en `148.113.167.121` (HTTP por IP). Tras el
  deploy el status reportó `mode=mock` hasta activar keys reales en
  `/opt/riotqueens/shared/runtime.env`.
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
- El owner ya creó el tenant Auth0 CA; todavía falta configurar la aplicación
  y la Custom API en el dashboard.
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

1. Configurar la aplicación existente y crear la Custom API/Audience; completar
   los valores en el único archivo local
   /home/rybjuani/Escritorio/RiotQueens-worktree/.env. El archivo existe,
   está ignorado por Git y es visible para el operador local; nunca imprimir
   sus valores ni copiarlos a documentación. Ejecutar la migración PostgreSQL
   antes de activar auth para usuarios de prueba.
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

Activar el runtime real en preprod (`148.113.167.121`, release `7448898`):
configurar en `/opt/riotqueens/shared/runtime.env` Gemini 3.1 Flash Lite como
primario y Euryale 70B (OpenRouter) como fallback, recrear sólo los servicios
necesarios, y verificar `/api/health`, `/api/v1/runtime/status` (`mode=real`)
y un turno real de Bardera en `/api/v1/chat`. No DNS, no TLS, no Auth0, no
reabrir casting.
