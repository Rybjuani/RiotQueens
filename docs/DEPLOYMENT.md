# Despliegue inicial

**Última verificación:** 2026-08-11

## Estado verificado

- VPS OVH activo en `148.113.167.121`, Ubuntu 24.04, 4 vCPU, 8 GB RAM y 75 GB de disco.
- acceso administrativo por clave pública con usuario `ubuntu`;
- login SSH por contraseña y login de root deshabilitados;
- UFW activo: entrada denegada por defecto y solo `22/tcp`, `80/tcp`, `443/tcp` y `443/udp` permitidos;
- Docker y Compose activos;
- release `c782b7b` activa desde `/opt/riotqueens/releases/c782b7b`;
- `api` y `web` healthy; Caddy publica HTTP en `148.113.167.121`;
- runtime compartido en `/opt/riotqueens/shared/runtime.env` (modo `0600`) migrado al prefijo `RIOTQUEENS_*`;
- smoke tests externos superados para `/`, `/legal`, `/privacy`, `/api/health`, `/api/v1/runtime/status` y `/api/v1/chat`;
- `/v1/chat` devuelve solo `response.content` y `Cache-Control: no-store`;
- Queens no registradas responden `404 queen_not_found`;
- endpoints WIP retirados (`/v1/onboarding/profile`, `/v1/characters`, `/v1/media/mock`) responden `404`;
- el logo entregado por HTTP conserva el SHA-256 oficial `e47df47761cdee8da0b7674b0bdb8f35a71086c24474a33d2b496de67ad3e3b1`;
- `/.env` y `/.ssh/authorized_keys` responden `404`;
- no hay registro `A`/`AAAA` resolviendo para `riotqueens.ai` ni `www.riotqueens.ai`;
- HTTPS queda pendiente hasta que el dominio resuelva al VPS.

## Contrato

- el código vive bajo `/opt/riotqueens/releases/<git-sha>`;
- la configuración runtime vive fuera de la release, en `/opt/riotqueens/shared/runtime.env`, con modo `0600`;
- Caddy es el único proceso publicado;
- `/api/*` se reescribe hacia FastAPI y las demás rutas hacia Next.js;
- el corte actual usa el proveedor `mock` y estado conversacional en proceso;
- no se sirven `/home`, `.git`, `.env`, masters ni biblioteca privada.

## Activación controlada

1. Construir y validar Compose desde una release identificada por commit.
2. Levantar `api`, `web` y `caddy` con el archivo runtime externo.
3. Verificar healthchecks, logs y puertos locales.
4. Probar `/`, `/legal`, `/privacy`, `/api/health` y un turno de `/api/v1/chat` por IP.
5. Crear el registro `A` de `riotqueens.ai` hacia `148.113.167.121` y decidir el alias `www`.
6. Cambiar `SITE_ADDRESS` al dominio y recrear Caddy para emitir TLS.
7. Repetir smoke tests por HTTPS y comprobar redirección HTTP → HTTPS.

No declarar producción lista mientras DNS/TLS o el smoke test externo estén pendientes.
