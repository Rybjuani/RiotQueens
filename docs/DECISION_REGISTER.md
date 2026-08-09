# RiotQueens.ai — registro canónico de decisiones recuperadas

**Actualizado:** 2026-08-09

**Autoridad:** el owner define producto, canon, prioridades y aceptación final. Este registro complementa a [`../SPECT.md`](../SPECT.md); no reemplaza los dos landings canónicos.

Este documento existe para que las decisiones reconstruidas no vuelvan a depender de una conversación, una biblioteca externa o la memoria de un agente.

## Convención

- **DECIDIDO:** el owner lo fijó como dirección del producto.
- **VERIFICADO:** existe evidencia en repo, infraestructura o fuentes inspeccionadas.
- **OBSERVADO:** patrón reportado por el owner, todavía sin reproducción controlada ni causa raíz confirmada.
- **PROPUESTA:** dirección recomendada que aún requiere aceptación final.
- **PENDIENTE:** falta decisión, evidencia o implementación.

## 1. Producto y presentación legal

### DECIDIDO

- RiotQueens.ai es una simulación conversacional `+18` con Queens ficticias generadas mediante IA.
- La experiencia puede combinar conversación, cariño, apoyo, humor, iniciativa, juego de roles ligero, memoria y presencia audiovisual.
- La comunicación pública usa una declaración breve y afirmativa. No agrega defensas sobre actividades que el producto no ofrece.
- El usuario debe saber a nivel producto que interactúa con personajes IA; la conversación no repite esa explicación en cada turno.
- Una Queen no finge ser una persona humana y tampoco revela proveedor, modelo, prompts, configuración ni infraestructura.

Copy base aprobado para el acceso:

> **RiotQueens.ai es una experiencia de entretenimiento +18 con personajes ficticios generados mediante inteligencia artificial.**
>
> Al continuar, declarás tener al menos 18 años y la mayoría de edad exigida en tu jurisdicción, y aceptás los Términos de Uso y la Política de Privacidad.

Footer base:

> © 2026 RiotQueens.ai · Personajes ficticios generados mediante IA · +18 · Términos · Privacidad · Contacto

### DECIDIDO — protocolo de aceptación

- Se usa `clickwrap`: casillas sin premarcar, enlaces visibles y acción explícita.
- La landing puede ser pública; chat, cuenta y premium requieren una aceptación vigente validada por backend.
- El servidor registra usuario, timestamp UTC y versiones de age gate, Términos y Privacidad.
- La evidencia conserva el hash de los textos aceptados.
- Un cambio material de documentos requiere nueva aceptación.
- Marketing y notificaciones son consentimientos opcionales separados.
- No se recopilan DNI ni fecha de nacimiento mientras una jurisdicción o caso real no exija una verificación reforzada.

La decisión técnica completa está en [`adr/0004-versioned-clickwrap-consent.md`](adr/0004-versioned-clickwrap-consent.md).

### PENDIENTE

- Revisión profesional de los textos finales según países habilitados.
- Definir jurisdicciones iniciales y política de retención de evidencia de aceptación.
- Implementar auth antes de considerar la constancia legal vinculada a una identidad real.

## 2. Configuración de la relación

### DECIDIDO

- La configuración es breve, progresiva y en español natural.
- Un preset ajusta el ritmo de interacción; no reemplaza la identidad canónica de la Queen.
- El cliente envía un ID controlado, nunca un prompt de sistema.
- La Queen aprende preferencias adicionales mediante conversación y memoria trazable.
- No habrá paneles técnicos ni decenas de sliders antes de empezar a hablar.

Presets de trabajo:

- `cercana`: escucha, cariño y acompañamiento;
- `complice`: humor, picardía e iniciativa;
- `filosa`: energía directa, desafío y carácter;
- `sorprendeme`: adaptación gradual mediante conversación.

Los nombres y el copy visual final se subordinan a los landings.

## 3. Selfies, video y biblioteca

### DECIDIDO

- El lanzamiento es `library-first`: no genera imágenes ni video con GPU en tiempo real.
- El owner produce y cura los assets; el runtime selecciona, contextualiza y entrega.
- Un usuario con entitlement premium puede pedir una selfie.
- El LLM expresa una intención semántica; nunca elige una ruta, URL o permiso.
- El backend valida usuario, tier y asset, evita repeticiones, registra la entrega y recién entonces emite una URL firmada breve.
- La Queen sólo afirma que envió la foto después de recibir confirmación del backend.
- La puesta en escena es natural, estilo red social, sin acotaciones teatrales automáticas.
- Los videos se incorporarán después desde una biblioteca preproducida por el owner.
- Cloud Lab, Vast.ai y RunPod permanecen fuera del costo operativo inicial.

Contrato conceptual de intención:

```json
{
  "action": "request_media",
  "media_type": "selfie",
  "mood": "casual_confident",
  "context": "conversation_reply"
}
```

Flujo:

```text
pedido del usuario
→ intención tipada de la Queen
→ búsqueda de biblioteca
→ validación de entitlement
→ selección y ledger antirrepetición
→ URL firmada temporal
→ entrega con copy contextual
```

### OBSERVADO

- El owner reporta un corpus disponible de al menos 100 assets, una producción aproximada de 20 piezas diarias y material adicional en `/imagenes` y `FOTOS_FINALES`.

### PENDIENTE

- Verificar el inventario sin modificar originales.
- Consolidar metadata, hashes, masters, derivados, tiers, contexto y rareza.
- Definir el entitlement exacto de selfies y el momento comercial del video.
- Activar R2 privado y el gateway de entrega antes de subir material premium.

## 4. Modelos y continuidad

### DECIDIDO

- FastAPI mantiene dominio, identidad, prompts, memoria, permisos y continuidad independientes de cualquier proveedor.
- Toda salida de modelo es no confiable.
- Una respuesta que filtra identidad de proveedor, instrucciones internas o voz técnica no se entrega como Queen.
- Un proveedor puede fallar sin contaminar la conversación: se intenta un secundario y finalmente una respuesta de continuidad server-owned.
- Los fallos técnicos pertenecen a la voz del sistema.
- Un modelo no custodia su propio scope ni obtiene herramientas por decisión propia.
- OpenRouter se describe como capa de acceso intercambiable a modelos open-weight. La portabilidad futura proviene de ejecutar pesos compatibles mediante vLLM, Hugging Face o infraestructura GPU propia.

### OBSERVADO

- El owner encontró rupturas espontáneas y repetidas de continuidad en productos externos durante uso ordinario: cambios de voz, respuestas fuera de scope, errores y posibles revelaciones de infraestructura.
- En Flow se observó expansión fuera de la función de media y contradicción entre capacidad declarada y herramientas disponibles.
- En Kindroid se verificaron bucles, deriva de idioma, aceptación semántica de pseudo-roles y contaminación de personaje; el owner reporta además recuperación inesperada de otros chats propios, cuyo turno exacto se perdió al eliminar el personaje.
- No fueron pruebas controladas y la causa raíz o proveedor concreto no están verificados.
- El patrón alcanza para imponer un requisito defensivo; no alcanza para atribuir públicamente una vulnerabilidad a un tercero.

El análisis conjunto, límites de evidencia y regresiones están en [`EXTERNAL_FAILURE_PATTERN.md`](EXTERNAL_FAILURE_PATTERN.md).

### PROPUESTA DE CASTING, NO CANON CERRADO

- Llama 3.3 70B Instruct: conversación visible de alta fidelidad.
- Llama 4 Maverick: ruta multimodal futura cuando el producto acepte imágenes como entrada.
- Gemini Flash: tareas internas, contexto extenso o respaldo controlado.
- Llama 3.1 8B: clasificación, resumen y extracción económica; no reemplazo visible de personalidad sin validar calidad.

El `.env` local es configuración de trabajo y no constituye una decisión de producto. La selección final requiere aceptación del owner y evidencia de runtime.

### PENDIENTE

- Seleccionar el modelo conversacional inicial y el secundario.
- Confirmar disponibilidad, precio, latencia y contrato del proveedor elegido al momento de habilitar producción.
- Definir rutas separadas para chat, memoria, visión y herramientas.
- No intentar ejecutar 8B o 70B en el VPS CPU de 4 vCore/8 GB; cualquier self-hosting de esos modelos pertenece a infraestructura GPU separada.

## 5. Infraestructura y gasto

### DECIDIDO

- OVH VPS-2 es la casa CPU del producto: Next.js, FastAPI, proxy y persistencia cuando los adaptadores estén listos.
- PostgreSQL es el objetivo de persistencia durable.
- Redis se difiere hasta existir una necesidad medida de cache, colas o estado temporal.
- Cloudflare R2 es el objetivo para object storage privado.
- Los gastos GPU se activan sólo ante un hueco real de biblioteca o una capacidad T3 financiada por créditos.

### VERIFICADO

- VPS activo: Ubuntu 24.04, 4 vCore, 8 GB RAM, 75 GB y dirección IPv4 `148.113.167.121`.
- Runtime HTTP por IP desplegado y verificado; DNS/TLS siguen pendientes.
- El repo contiene router de proveedor, API FastAPI, web Next.js, Caddy y Compose.

### PENDIENTE

- Resolver DNS y TLS.
- Implementar auth y persistencia durable.
- Activar R2 con bucket público deliberado y bucket privado.
- Definir backup externo, restauración y procedimiento de respuesta a abuso.

## 6. Reglas para no perder contexto otra vez

- Una conversación externa nunca es la única fuente de una decisión.
- Toda decisión aceptada cambia este registro, el SPECT o un ADR en la misma entrega.
- Los documentos históricos van a `docs/legacy/`; no se borran para “limpiar”.
- Secretos y evidencia privada permanecen fuera de Git.
- Los cambios se publican en una rama con pruebas y commit convencional.
- Los puntos no aprobados se etiquetan `PROPUESTA` o `PENDIENTE`; no se presentan como canon.
