# ADR 0001 — Queen canónica y routing de lanzamiento

**Estado:** aceptado
**Fecha:** 2026-08-08

## Contexto

El runtime recuperado usa `vane` como identificador y conserva una dirección pública anterior. Los landings canónicos presentan a `La Bardera` y el owner fijó RiotQueens.ai como marca.

## Decisión

- `bardera` es el `character_id` canónico del lanzamiento.
- `vane` queda como alias temporal de compatibilidad y resuelve al mismo prompt server-owned.
- El frontend nuevo envía `bardera`.
- El flujo público es landing → chat T1; la configuración adicional no bloquea la primera conversación.
- Web y API se publican bajo un único origen. Caddy enruta `/api/*` hacia FastAPI y el resto hacia Next.js.
- PostgreSQL y Redis no se ejecutan en producción hasta tener adaptadores reales que los consuman.

## Consecuencias

- No se rompen sesiones de prototipo que todavía usen `vane`.
- La marca pública y el runtime convergen sin migración destructiva.
- El primer deploy es honesto: conversación y memoria siguen siendo estado en proceso.
- El alias `vane` debe retirarse mediante otro ADR después de contar con auth y migración de scopes.
