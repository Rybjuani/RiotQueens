# ADR 0001 — Queen inicial y routing de lanzamiento

**Estado:** aceptado
**Fecha:** 2026-08-08
**Enmendado:** 2026-08-10

## Contexto

El runtime recuperado usa `vane` como identificador y conserva una dirección pública anterior. El owner fijó RiotQueens.ai como marca y ratificó cinco Queens canónicas: Bardera, Tóxica Consciente, Gede, Rocha y Chela. Bardera es la Queen inicial y la única implementada actualmente.

Los landings conservan autoridad visual, compositiva y de ADN de diseño, pero sus asociaciones históricas Queen↔Tier no gobiernan el producto: no reactivan a La Rota ni congelan nombres, copy, pricing o claims superados.

## Decisión

- `bardera` es el `character_id` canónico del lanzamiento.
- `vane` queda como alias temporal de compatibilidad y resuelve al mismo prompt server-owned.
- El frontend nuevo envía `bardera`.
- El flujo objetivo es landing → experiencia T0/free con Bardera → progresión independiente a tiers pagos cuando estén implementados.
- Ninguna Queen pertenece a un tier. La misma Queen puede continuar desde T0 hasta T3 sin cambiar su identidad básica.
- Web y API se publican bajo un único origen. Caddy enruta `/api/*` hacia FastAPI y el resto hacia Next.js.
- PostgreSQL y Redis no se ejecutan en producción hasta tener adaptadores reales que los consuman.

## Consecuencias

- No se rompen sesiones de prototipo que todavía usen `vane`.
- La marca pública y el runtime convergen sin migración destructiva.
- Bardera no equivale a T1; Tóxica Consciente, Gede, Rocha y Chela pueden incorporarse después sin asignarlas a tiers propios.
- El primer deploy es honesto: conversación y memoria siguen siendo estado en proceso.
- El alias `vane` debe retirarse mediante otro ADR después de contar con auth y migración de scopes.
