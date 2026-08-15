# Provider smoke — 2026-08-15

**Queen:** La Bardera
**Batería:** `glosariomodismos` / 12 turnos
**Código:** branch `chore/recover-riotqueens-canon`, evidencia local ignorada en `artifacts/evals/`
**Estado:** `TECHNICAL_PRE_RELEASE_PASS` para Bardera texto; no es aprobación transversal de Queens ni despliegue de producción.

| Proveedor | Modelo | Resultado | Evidencia resumida |
|---|---|---|---|
| Google AI Studio | `gemini-2.5-flash` | `INFRA_FAILURE` | tres corridas: 5 turnos y timeout en T6; 6 turnos sin hard-fail y error HTTP en T7; sin few-shot, 2 turnos sin hard-fail y HTTP 429 en T3 |
| Google AI Studio | `gemini-3.1-flash-lite` | `TECHNICAL_PRE_RELEASE_PASS` | direct: 2×12/12 (con/sin few-shot); API RiotQueens: 2×12/12, 0 hard-fails, 0 truncaciones, 0 claims de adjuntos; la segunda corrida midió p50 2.12 s y p95 5.23 s |
| Google AI Studio | `gemma-4-31b-it` | `INFRA_FAILURE` | 10 turnos procesados, 4 hard-fails; HTTP 429 en T11 y etiquetas `<thought>` visibles |
| Hugging Face Router | `openai/gpt-oss-120b:ovhcloud` | `INFRA_FAILURE` | 9 turnos procesados; 5 hard-fails; HTTP 402 en T10 |
| OpenRouter | `meta-llama/llama-3.3-70b-instruct` | `FAIL` | 12 turnos procesados; 4 hard-fails; sin fallo de infraestructura |

Notas:

- Gemini requirió omitir `frequency_penalty`, porque su capa OpenAI-compatible respondió HTTP 400 con ese parámetro. La repetición con `gemini-2.5-flash`, glosario, few-shot, `temperature=0.9` y `max_tokens=256` llegó a T6 sin hard-fail y terminó en `HTTPStatusError` en T7. La corrida equivalente sin few-shot llegó a T2 sin hard-fail y recibió HTTP 429 en T3. Sigue siendo `INFRA_FAILURE`, no un `PASS`; no se deben extraer conclusiones de voz ni consumir más cuota hasta resolver disponibilidad.
- La configuración de pre-release de Bardera es Google AI Studio OpenAI-compatible + `gemini-3.1-flash-lite`, `temperature=0.9`, sin `frequency_penalty`, timeout server-owned de 90 s y cero retries durante la prueba. La cuota visible declarada por el owner es 15 RPM / 500 RPD; la batería de 12 requests se espació a 4.1 s para no sobrepasar RPM. La corrida por API usa el prompt server-owned, no los few-shot del harness, y el artifact consulta `/v1/runtime/status`, por lo que registra el modelo que realmente atendió.
- **Gate técnico repetido:** dos corridas API completas terminaron `PASS_HEURISTIC` con 12/12 turnos, cero `FALSE_POSITIVE / REFUSAL`, `VOICE_LOSS`, `UNSOLICITED_ESCALATION`, truncaciones o claims de adjuntos. La segunda (artifact local ignorado `modismo_results_20260815_133111.json`) midió latencia end-to-end mínima 1.75 s, p50 2.12 s, p95 5.23 s y máximo 22.83 s. Es una muestra de laboratorio, no una promesa de SLA.
- **Fallback verificado:** regresiones cubren contenido inválido o bloqueo explícito → continuidad server-owned de la Queen; timeout, rate limit y fallo de transporte → respuesta de sistema sanitizada, nunca una voz fingida de la Queen. Esta división respeta SPECT y evita convertir un problema de proveedor en personalidad artificial.
- Gemma remoto respondió desde el VPS, pero emitió etiquetas `<thought>` en el contenido y no puede entrar al runtime sin un filtro/adapter que garantice que no se exponga razonamiento interno.
- `gemini-3.1-flash-lite` pasa el gate técnico de pre-release únicamente para Bardera texto. Antes de VPS/producción quedan aceptación final del owner y el gate C7 de release identificada; no habilita Gemma, multimodalidad ni otra Queen.
- HF sí evidenció falso positivo corporativo en los turnos con archivos y modismos; además la cuota/pago interrumpió la corrida.
- Los JSON crudos están en `artifacts/evals/` local y no se publican.
- La selección se revisa con una corrida reproducible ante cambios de modelo, cuota o prompt; un `PASS_HEURISTIC` nunca reemplaza revisión humana de las muestras.
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
