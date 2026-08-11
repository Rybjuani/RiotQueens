# Procedencia de assets web

Los archivos de esta tabla son copias de trabajo. Los originales externos al repo no fueron modificados.

La allowlist ejecutable está en [`../config/public-media.json`](../config/public-media.json). CI comprueba que las rutas y hashes coincidan y que ninguna entrada pública esté marcada como premium.

| Ruta web | Estado | Fuente curatorial | SHA-256 |
|---|---|---|---|
| `apps/web/public/brand/riotqueens-logo.jpeg` | `CANON / LOCKED` | `RiotQueens_logo_design_202608082344.jpeg` | `e47df47761cdee8da0b7674b0bdb8f35a71086c24474a33d2b496de67ad3e3b1` |
| `apps/web/public/queens/img-042-hero.jpg` | `PROVISIONAL / CONVERSATIONAL` | `LA BARDERA/T1ROOT.png` — presencia creativa / online | `98546f3a94a3dc794792e80e941f01a0353ed5c9eeb7aaff20c5961267623f95` |
| `apps/web/public/queens/img-065-reference.jpg` | `PROVISIONAL / CONVERSATIONAL` | `LA BARDERA/Woman_sitting_in_bedroom_2K_202608071951.jpeg` — identidad + cuarto | `08e0d8967f4c9bc74f104fe754e880a7141d5db6fb8ffc198c9c9a375703edbe` |
| `apps/web/public/queens/img-074-support.jpg` | `PROVISIONAL / CONVERSATIONAL` | `LA BARDERA/Woman_sitting_in_bedroom_2K_202608071956.jpeg` — presencia soporte | `41555333469e6b653ba4f44348f474ed7d3f4d1bba3cb9a34aee9bcc26e41e1a` |

## Criterio de selección (owner)

El producto prioriza **compañeras conversacionales** (humor, creatividad, chat) con fotos de **presencia e identidad**, no un catálogo spicy. Las previews públicas deben leerse como “ella está ahí / en su mundo”, no como delivery erótico.

Las tres fotos de queens son provisionales desde el pool curado `RiotQueens Seleccionadas/LA BARDERA`. Sustituirlas exige mantener la ruta o actualizar consumidores, registrar el nuevo hash y conservar el archivo anterior fuera del runtime si era un master.

Reemplazo 2026-08-11: se retiraron previews heredados del corpus spicy/editorial (IMG_042/065/074 del ranking antiguo) por copias del pool ordenado del owner.
