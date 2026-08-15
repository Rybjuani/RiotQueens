# Procedencia de assets web

Los archivos de esta tabla son copias de trabajo. Los originales externos al repo no fueron modificados.

La allowlist ejecutable está en [`../config/public-media.json`](../config/public-media.json). CI comprueba que las rutas y hashes coincidan y que ninguna entrada pública esté marcada como premium.

## Criterio de selección (owner)

El producto prioriza **compañeras conversacionales** (humor, creatividad, chat) con fotos de **presencia e identidad**, no un catálogo spicy. Las previews públicas deben leerse como “ella está ahí / en su mundo”.

Cada Queen mantiene **memoria y conversación aisladas** en backend por `character_id`. Las grillas del roster son previews provisionales: el owner reordena al verlas en pantalla.

Pool fuente: `Escritorio/RiotQueens/RiotQueens Seleccionadas/` (no se sirve desde el VPS). Flow y Mage son ecosistemas canónicos externos del owner y contienen material ya producido; los assets de esos ecosistemas sólo se vuelven parte del repo mediante una copia/derivado con procedencia y hash.

## Brand

| Ruta web | Estado | Fuente | SHA-256 |
|---|---|---|---|
| `apps/web/public/brand/riotqueens-logo.jpeg` | `CANON / LOCKED` | logo oficial | `e47df47761cdee8da0b7674b0bdb8f35a71086c24474a33d2b496de67ad3e3b1` |

## Previews por Queen (provisional)

Rutas bajo `apps/web/public/queens/<id>/0N.jpg`. Hashes exactos en `config/public-media.json`.

| Queen | Slots | Runtime chat | Notas |
|---|---|---|---|
| `bardera` | 5 | **live** | 01–03 presencia/chat preferidas; 04–05 relleno provisional del pool de 7; reemplazo sólo mediante selección registrada desde fuentes canónicas |
| `toxica` | 5 | curación | presencia en cuarto |
| `gede` | 5 | curación | cuarto + retrato vertical |
| `rocha` | 2 | curación | pool chico; faltan 2–3 tomas |
| `chela` | 5 | curación | retrato + cuarto + escalera |

Sustituir un slot: reemplazar el archivo, actualizar hash en `public-media.json` y esta nota, y reordenar en `apps/web/lib/queen.ts` si cambia el rol.
