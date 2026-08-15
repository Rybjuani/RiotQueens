# Provider Lab: Google AI Studio, Gemma y proveedores compatibles

**Estado:** PROPUESTA / EXPERIMENTO CONTROLADO.

El producto no depende de un proveedor. El laboratorio compara configuraciones para identidad, modismos, falso positivo, multimodalidad, latencia y costo. El runtime sólo consume adaptadores aprobados y mantiene prompts, scopes, fallback e identidad del lado servidor.

La propuesta de GPU cloud para producción visual está separada de este laboratorio de modelos y se documenta en [`docs/CLOUD_LAB.md`](CLOUD_LAB.md). El VPS sigue siendo el orquestador CPU; una GPU pay-as-you-go sólo se levanta para un trabajo autorizado y medido.

## Google AI Studio

`GEMINI_API_KEY` queda reservado para Google AI Studio como proveedor de laboratorio y posible ruta multimodal. Las corridas controladas del 2026-08-15 con `gemini-2.5-flash` respondieron hasta seis turnos del glosario sin hard-fail, pero terminaron por infraestructura antes de completar la batería (timeout en T6; `HTTPStatusError` en T7; nueva corrida sin few-shot con HTTP 429 en T3). Todavía falta una batería de voz completa y una prueba multimodal reproducible. La credencial detectada en `.env_final(1)` no se copia ni se versiona. No hay evidencia de que haya sido publicada o commiteada; la rotación sólo corresponde si aparece evidencia de exposición efectiva, un log compartido o una instrucción del owner. También hay que comprobar cuota, modelo habilitado, región y términos de la cuenta. La API de Google Developers que el owner todavía debe obtener es una dependencia distinta y queda `PENDIENTE`.

## Gemma local

La propuesta recuperada del material de Google/Qwen es un laboratorio híbrido: Ollama persistente para pruebas de bajo volumen, Gemma pequeña para composición de prompts y Gemma mayor para evaluación, con llama.cpp/OpenAI-compatible como alternativa. La documentación oficial de Gemma 4 describe soporte multimodal, rol de sistema y contexto largo; la integración oficial de Ollama expone `localhost:11434/api/generate` y variantes `gemma4:e2b`, `gemma4:e4b`, `gemma4:26b` y `gemma4:31b`.

Esto no autoriza a agregar GPU, Ollama o almacenamiento persistente al producto antes de medir el caso. Primero se prueba fuera del runtime y se registra evidencia.

## Matriz mínima de prueba

| Candidato | Uso | Estado | Criterio de salida |
|---|---|---|---|
| OpenRouter/Llama | baseline de conversación Bardera | FAIL: 12 turnos, 4 hard-fails | recalibrar prompt/modelo o reemplazar |
| Hugging Face Router | fallback compatible | INFRA/PERSONALIDAD: HTTP 200 inicial, 5 hard-fails y HTTP 402 en T10 | resolver cuota/pago y repetir batería |
| Google AI Studio | laboratorio multimodal / comparación | INFRA: 5 turnos sin hard-fail, timeout en T6 | resolver latencia y repetir batería |
| Google AI Studio + Gemma | benchmark alternativo de personalidad | FAIL/INFRA: 10 turnos, 4 hard-fails, HTTP 429 y `<thought>` visible | limitar pensamiento, resolver cuota y repetir |
| Gemma vía Ollama | laboratorio local de bajo volumen | PROPUESTA | reproducibilidad, VRAM/latencia y benchmark |

La matriz no decide un ganador por reputación. `PASS` requiere el benchmark de la Queen, revisión de salidas, límites de seguridad intactos y registro reproducible. Un modelo puede pasar Bardera y fallar otra Queen.

## Contrato de secretos

El único `.env` operativo local vive en la raíz del repo canónico y está ignorado. `.env.example` es el contrato versionado. En VPS se usa un archivo de secretos fuera del repo junto con `.env` de defaults; nunca se sirve desde web ni se incluye en imágenes públicas. Las claves de OpenRouter, Hugging Face, Google AI Studio y cualquier futuro proveedor se rotan si aparecen en Git, una superficie pública o logs compartidos; el almacenamiento local protegido no equivale por sí solo a exposición.
