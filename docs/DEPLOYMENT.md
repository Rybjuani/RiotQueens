# Despliegue inicial

**Última verificación:** 2026-08-09

## Estado verificado

- VPS OVH activo en `148.113.167.121`, Ubuntu 24.04, 4 vCPU, 8 GB RAM y 75 GB de disco.
- acceso administrativo por clave pública con usuario `ubuntu`;
- login SSH por contraseña y login de root deshabilitados;
- UFW activo: entrada denegada por defecto y solo `22/tcp`, `80/tcp`, `443/tcp` y `443/udp` permitidos;
- Docker `29.1.3` y Compose `2.40.3` activos;
- `docker compose config` y los builds de `api` y `web` completados en el VPS;
- no hay registro `A`/`AAAA` resolviendo para `riotqueens.ai` ni `www.riotqueens.ai`;
- la release candidata todavía no se publicó en los puertos públicos.

## Contrato

- el código vive bajo `/opt/riotqueens/releases/<git-sha>`;
- la configuración runtime vive fuera de la release, en `/opt/riotqueens/shared/runtime.env`, con modo `0600`;
- Caddy es el único proceso publicado;
- `/api/*` se reescribe hacia FastAPI y las demás rutas hacia Next.js;
- el primer corte usa el proveedor `mock` y estado conversacional en proceso;
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
