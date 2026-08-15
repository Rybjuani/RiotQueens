# Provider smoke — 2026-08-15

**Queen:** La Bardera
**Batería:** `glosariomodismos` / 12 turnos
**Código:** `311c8d3` más el harness local de esta corrida
**Estado:** no aprobado para runtime

| Proveedor | Modelo | Resultado | Evidencia resumida |
|---|---|---|---|
| Google AI Studio | `gemini-2.5-flash` | `INFRA_FAILURE` | 5 turnos procesados, 0 hard-fails; timeout en T6 |
| Google AI Studio | `gemma-4-31b-it` | `INFRA_FAILURE` | 10 turnos procesados, 4 hard-fails; HTTP 429 en T11 y etiquetas `<thought>` visibles |
| Hugging Face Router | `openai/gpt-oss-120b:ovhcloud` | `INFRA_FAILURE` | 9 turnos procesados; 5 hard-fails; HTTP 402 en T10 |
| OpenRouter | `meta-llama/llama-3.3-70b-instruct` | `FAIL` | 12 turnos procesados; 4 hard-fails; sin fallo de infraestructura |

Notas:

- Gemini requirió omitir `frequency_penalty`, porque su capa OpenAI-compatible respondió HTTP 400 con ese parámetro.
- Gemma remoto respondió desde el VPS, pero emitió etiquetas `<thought>` en el contenido y no puede entrar al runtime sin un filtro/adapter que garantice que no se exponga razonamiento interno.
- La respuesta inicial de Gemini mostró cobertura léxica de Bardera, pero la latencia impide declararlo `PASS`.
- HF sí evidenció falso positivo corporativo en los turnos con archivos y modismos; además la cuota/pago interrumpió la corrida.
- Los JSON crudos están en `artifacts/evals/` local y no se publican.
- Debe repetirse la batería con cuota válida, timeout medido y configuración fijada antes de seleccionar proveedor.
- OpenRouter queda como baseline estable de transporte, pero no como candidato aprobado para Bardera: reproduce falsos positivos y ruptura de voz en el corpus real.

## Evidencia recuperada de la sesión viva de Grok

La sesión `.grok` `019fecf9-66c0-74b2-b271-0a4e5899d7b1` (actualizada el 2026-08-11) estableció el criterio que gobierna esta tabla: el test soft no alcanza para casting. Sus corridas sobre `glosariomodismos.md` fueron:

| Configuración | Turnos | Hard fails | Resultado |
|---|---:|---:|---|
| Llama 3.3 70B, batería soft | 12 | 0 | `PASS_HEURISTIC`, no aprobación |
| Llama 3.3 70B, glosario real, baseline | 12 | 1 | `FAIL` |
| Llama 3.3 70B, glosario + inoculación + few-shot | 12 | 10 | `FAIL` |
| Llama 3.3 70B, glosario + inoculación, sin few-shot | 12 | 4 | `FAIL` |

La conclusión de Grok queda incorporada como regla vigente: `glosariomodismos.md` es el benchmark de voz de La Bardera; aprobar una batería genérica no habilita un modelo. Las salidas del glosario mostraron falsos positivos ante fotos/PDF/archivos y deriva a “asistente corporativo”, aun cuando el modelo toleraba `che`, `boludo`, `laburo` y `fernet` en el test soft. Esta evidencia es complementaria a la corrida del 2026-08-15 y no debe colapsarse en un único número.
