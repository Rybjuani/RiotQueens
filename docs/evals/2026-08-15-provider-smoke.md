# Provider smoke — 2026-08-15

**Queen:** La Bardera
**Batería:** `glosariomodismos` / 12 turnos
**Código:** branch `chore/recover-riotqueens-canon`, evidencia local ignorada en `artifacts/evals/`
**Estado:** Bardera tiene un candidato de runtime; no es aprobación transversal de Queens ni despliegue de producción.

| Proveedor | Modelo | Resultado | Evidencia resumida |
|---|---|---|---|
| Google AI Studio | `gemini-2.5-flash` | `INFRA_FAILURE` | tres corridas: 5 turnos y timeout en T6; 6 turnos sin hard-fail y error HTTP en T7; sin few-shot, 2 turnos sin hard-fail y HTTP 429 en T3 |
| Google AI Studio | `gemini-3.1-flash-lite` | `CANDIDATE_RUNTIME_PASS_HEURISTIC` | direct: 2×12/12 (con/sin few-shot); API RiotQueens: 12/12, 0 hard-fails, 0 truncaciones, 0 claims de adjuntos, 14 hits léxicos únicos |
| Google AI Studio | `gemma-4-31b-it` | `INFRA_FAILURE` | 10 turnos procesados, 4 hard-fails; HTTP 429 en T11 y etiquetas `<thought>` visibles |
| Hugging Face Router | `openai/gpt-oss-120b:ovhcloud` | `INFRA_FAILURE` | 9 turnos procesados; 5 hard-fails; HTTP 402 en T10 |
| OpenRouter | `meta-llama/llama-3.3-70b-instruct` | `FAIL` | 12 turnos procesados; 4 hard-fails; sin fallo de infraestructura |

Notas:

- Gemini requirió omitir `frequency_penalty`, porque su capa OpenAI-compatible respondió HTTP 400 con ese parámetro. La repetición con `gemini-2.5-flash`, glosario, few-shot, `temperature=0.9` y `max_tokens=256` llegó a T6 sin hard-fail y terminó en `HTTPStatusError` en T7. La corrida equivalente sin few-shot llegó a T2 sin hard-fail y recibió HTTP 429 en T3. Sigue siendo `INFRA_FAILURE`, no un `PASS`; no se deben extraer conclusiones de voz ni consumir más cuota hasta resolver disponibilidad.
- La configuración candidata de Bardera es Google AI Studio OpenAI-compatible + `gemini-3.1-flash-lite`, `temperature=0.9`, sin `frequency_penalty`, timeout server-owned de 90 s y cero retries durante la prueba. La cuota de 15 RPM se respetó espaciando 4.1 s. La corrida por API usó el prompt server-owned, no los few-shot del harness; el artifact consulta `/v1/runtime/status`, por lo que registra el modelo que realmente atendió. Una salida lenta durante la repetición agotó el timeout sin falsear la evidencia: la corrida terminada posterior completó los 12 turnos.
- Gemma remoto respondió desde el VPS, pero emitió etiquetas `<thought>` en el contenido y no puede entrar al runtime sin un filtro/adapter que garantice que no se exponga razonamiento interno.
- `gemini-3.1-flash-lite` queda sólo como candidato Bardera de pre-release: antes de VPS/producción debe medirse latencia y cuota con tráfico real, configurar fallback y completar el gate de release. No habilita Gemma, multimodalidad ni otra Queen.
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
