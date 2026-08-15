# Provider smoke — 2026-08-15

**Queen:** La Bardera
**Batería:** `glosariomodismos` / 12 turnos
**Código:** `311c8d3` más el harness local de esta corrida
**Estado:** no aprobado para runtime

| Proveedor | Modelo | Resultado | Evidencia resumida |
|---|---|---|---|
| Google AI Studio | `gemini-2.5-flash` | `INFRA_FAILURE` | 5 turnos procesados, 0 hard-fails; timeout en T6 |
| Hugging Face Router | `openai/gpt-oss-120b:ovhcloud` | `INFRA_FAILURE` | 9 turnos procesados; 5 hard-fails; HTTP 402 en T10 |
| OpenRouter | `meta-llama/llama-3.3-70b-instruct` | `FAIL` | 12 turnos procesados; 4 hard-fails; sin fallo de infraestructura |

Notas:

- Gemini requirió omitir `frequency_penalty`, porque su capa OpenAI-compatible respondió HTTP 400 con ese parámetro.
- La respuesta inicial de Gemini mostró cobertura léxica de Bardera, pero la latencia impide declararlo `PASS`.
- HF sí evidenció falso positivo corporativo en los turnos con archivos y modismos; además la cuota/pago interrumpió la corrida.
- Los JSON crudos están en `artifacts/evals/` local y no se publican.
- Debe repetirse la batería con cuota válida, timeout medido y configuración fijada antes de seleccionar proveedor.
- OpenRouter queda como baseline estable de transporte, pero no como candidato aprobado para Bardera: reproduce falsos positivos y ruptura de voz en el corpus real.
