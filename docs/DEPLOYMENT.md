# Despliegue inicial

**Última verificación:** 2026-08-17

## Estado verificado

- VPS OVH activo en `148.113.167.121`, Ubuntu 24.04, 4 vCPU, 8 GB RAM y 75 GB de disco.
- acceso administrativo por clave pública con usuario `ubuntu`;
- login SSH por contraseña y login de root deshabilitados;
- UFW activo: entrada denegada por defecto y solo `22/tcp`, `80/tcp`, `443/tcp` y `443/udp` permitidos;
- Docker y Compose activos;
- release `7448898` activa desde `/opt/riotqueens/releases/7448898` (commit completo en `RELEASE_SHA`);
- servicios `postgres`, `api`, `web` y `caddy` healthy; Caddy publica HTTP en `148.113.167.121`;
- runtime compartido en `/opt/riotqueens/shared/runtime.env` (modo `0600`) con prefijo `RIOTQUEENS_*`;
- casting de voz Bardera **cerrado** (2026-08-17): primario configurado Gemini 3.1 Flash Lite; fallback de lab Euryale 70B vía OpenRouter; no reabrir Dolphin ni nueva matriz de casting;
- al momento del deploy de `7448898`, `/api/v1/runtime/status` reportó `mode=mock` porque el `runtime.env` del VPS aún no tenía el provider real activado; la siguiente acción operativa es activar el runtime real y verificar un turno de Bardera;
- smoke HTTP por IP superados para `/`, `/legal`, `/privacy`, `/api/health` y `/api/v1/runtime/status`;
- con `RIOTQUEENS_AUTH_ENABLED=false`, `/api/v1/chat` requiere `user_id` en el body (modo pre-auth) y devuelve solo `response.content` con `Cache-Control: no-store`;
- Queens no registradas responden `404 queen_not_found`;
- el logo entregado por HTTP conserva el SHA-256 oficial `e47df47761cdee8da0b7674b0bdb8f35a71086c24474a33d2b496de67ad3e3b1`;
- `/.env` y `/.ssh/authorized_keys` responden `404`;
- no hay registro `A`/`AAAA` resolviendo para `riotqueens.ai` ni `www.riotqueens.ai`;
- HTTPS queda pendiente hasta que el dominio resuelva al VPS.

## Contrato

- el código vive bajo `/opt/riotqueens/releases/<git-sha>`;
- la configuración runtime vive fuera de la release, en `/opt/riotqueens/shared/runtime.env`, con modo `0600`;
- Caddy es el único proceso publicado;
- `/api/*` se reescribe hacia FastAPI y las demás rutas hacia Next.js;
- provider primario de producto: Gemini 3.1 Flash Lite; fallback de lab: Euryale 70B (OpenRouter); conversación/memoria siguen en proceso;
- no se sirven `/home`, `.git`, `.env`, masters ni biblioteca privada.

## Activación controlada

1. Construir y validar Compose desde una release identificada por commit.
2. Levantar `api`, `web` y `caddy` combinando configuración no sensible y secretos:

   ```bash
   docker compose \
     --env-file .env \
     --env-file /opt/riotqueens/shared/runtime.env \
     up -d
   ```

   El primer archivo conserva los defaults y parámetros no sensibles del release;
   el segundo aporta las claves server-side. No copiar secretos dentro de la
   release ni usar el archivo runtime externo como única fuente, porque los
   defaults de Compose volverían silenciosamente al proveedor `mock`.

3. Verificar healthchecks, logs y puertos locales.
4. Probar `/`, `/legal`, `/privacy`, `/api/health` y un turno de `/api/v1/chat` por IP.
5. Crear el registro `A` de `riotqueens.ai` hacia `148.113.167.121` y decidir el alias `www`.
6. Cambiar `SITE_ADDRESS` al dominio y recrear Caddy para emitir TLS.
7. Repetir smoke tests por HTTPS y comprobar redirección HTTP → HTTPS.

No declarar producción lista mientras DNS/TLS o el smoke test externo estén pendientes.
