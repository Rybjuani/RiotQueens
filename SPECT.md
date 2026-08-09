# RiotQueens.ai — SPECT canónico

**Versión:** 0.2

**Fecha:** 2026-08-09

**Estado:** fundamento operativo; sustituye como autoridad a la documentación de Companion Studio

## 1. Autoridad y canon

El owner define producto, prioridades, canon y aceptación final.

Los dos landings mandan conjuntamente:

1. `Riotqueens-Ai-Landing-Mock.html` es autoridad de identidad, voz, composición y dirección visual.
2. `Reiniciando-chat-anterior.html` es autoridad de continuidad, interacción y flujo desde los controles del primer landing.

Ninguno es un boceto descartable ni puede ser reemplazado por un rediseño genérico. La expansión debe crecer desde ambos. Si entre ellos aparece una contradicción material, no se resuelve por preferencia del agente: se documenta y decide el owner.

Huellas verificadas de las copias locales designadas como canon:

| Archivo | SHA-256 |
|---|---|
| `Riotqueens-Ai-Landing-Mock.html` | `5307742d62016fe0f3691ccaf1b57955e3dffe105dcf0c773da53531fb68750e` |
| `Reiniciando-chat-anterior.html` | `246ce2e0d893f793e8effd268c2a5a00d29b7dc385f071e422bdb25d4bcdc68b` |

Los HTML crudos permanecen fuera del repositorio porque contienen bundles, datos embebidos y lenguaje histórico no publicable. Sus composiciones y contratos de interacción fueron auditados y trasladados al frontend Next.js; las huellas se conservan para comprobar fidelidad sin convertir los snapshots en runtime.

Logo oficial bloqueado:

| Archivo fuente | Copia web | SHA-256 |
|---|---|---|
| `RiotQueens_logo_design_202608082344.jpeg` | `apps/web/public/brand/riotqueens-logo.jpeg` | `e47df47761cdee8da0b7674b0bdb8f35a71086c24474a33d2b496de67ad3e3b1` |

La copia web es idéntica byte por byte. No se redibuja, reinterpreta ni reemplaza sin decisión expresa del owner.

Orden de autoridad restante:

1. Este SPECT gobierna producto y arquitectura funcional.
2. Los ADR vigentes gobiernan decisiones técnicas concretas, sin contradecir los landings ni este SPECT.
3. Código y pruebas verifican lo que está implementado; no convierten una limitación accidental en decisión de producto.
4. `docs/legacy/` conserva procedencia histórica y no es autoridad vigente.

Frase rectora:

> **LANDINGS MANDAN. PRODUCTO DEBAJO. COMPLEJIDAD ESCONDIDA. QUEEN AL FRENTE.**

Principio de experiencia:

> **Caótica en personaje. Coherente en memoria. Premium en imagen.**

## 2. Identidad de producto

RiotQueens.ai es una simulación conversacional `+18` con personajes virtuales ficticios y originales creados desde cero por el owner. Combina conversación, memoria, presencia narrativa, biblioteca audiovisual curada y, por etapas, capacidades de agente y generación personalizada. A nivel producto comunica claramente que los personajes son generados mediante IA; dentro del chat evita repetir explicaciones que rompan la experiencia.

ADN:

- riot-grrrl y punk-glam;
- goth editorial y brutalismo;
- negro profundo, magenta neón y cyan eléctrico;
- under argentino;
- fotografía editorial de alto impacto;
- pocas Queens con identidad, continuidad y densidad.

No convertir el producto en un catálogo genérico ni en una interfaz corporativa. La complejidad vive detrás del producto, no en la cabeza del usuario.

La marca pública utiliza `+18` como señal legal y de elegibilidad. No agrega aclaraciones defensivas sobre actividades que el producto no ofrece.

Las decisiones recuperadas y su estado se conservan en [`docs/DECISION_REGISTER.md`](docs/DECISION_REGISTER.md).

## 3. Voz y experiencia

La Queen tiene personalidad; no intenta demostrarla.

Debe sostener:

- lenguaje natural y timing;
- humor, contradicción e iniciativa;
- memoria y continuidad contextual;
- progresión gradual de confianza;
- capacidad de pasar de conversación a una tarea real sin romper identidad.

Debe evitar:

- bios sobreescritas;
- teatralidad automática;
- acotaciones escénicas repetitivas;
- frases genéricas de personalidad;
- respuestas que prioricen mantener una pose por encima de comprender al usuario.

El onboarding debe ser corto, llevar temprano al chat y entregar valor visible pronto. La configuración avanzada aparece de forma progresiva y comprensible.

La configuración inicial puede elegir un preset simple de relación —cercana, cómplice, filosa o adaptación libre— sin reemplazar la personalidad canónica. El cliente envía un ID controlado; prompts, instrucciones y límites permanecen server-owned.

Toda voz tiene dueño:

- la Queen habla como Queen;
- el sistema habla como sistema;
- ninguna capa intermedia finge intimidad.

Las notificaciones e iniciativas deben poder silenciarse a nivel de producto.

## 4. Experiencia vertical

La expansión conjunta de los landings debe demostrar el producto, no enumerar una sección genérica de funcionalidades.

Flujo previsto:

1. entrada visual y narrativa;
2. acceso y progresión;
3. chat con presencia audiovisual;
4. memoria y continuidad;
5. pedidos de fotos, clips o entregables;
6. biblioteca, créditos y generación cuando corresponda;
7. llamada final a la acción;
8. cierre visual coherente con el canon.

## 5. Dos escalas diferentes

Los niveles visuales y los tiers comerciales no son la misma escala.

### Niveles de contexto visual

- **N0 — Presencia:** teaser y aparición inicial.
- **N1 — Proximidad:** escenas cercanas, cotidianas y contextuales.
- **N2 — Escenarios privados:** mayor intimidad narrativa y producción deliberada dentro de los límites del producto.

### Tiers de acceso y valor

- **T0 — Preview:** prueba suficiente para generar curiosidad sin agotar la progresión.
- **T1 — Acceso pago:** biblioteca abundante, contexto, variantes y pedidos simples definidos.
- **T2 — Premium:** mayor sofisticación visual, rareza, costo artesanal y continuidad.
- **T3 — Personalizado:** prioridad, pedidos específicos, generación bajo demanda y video cuando corresponda.

`Tier` define capacidad base. `Créditos` cubre costo variable. Antes de confirmar un consumo, la interfaz muestra saldo, costo e historial; no hay consumo automático oculto.

## 6. Medios y trazabilidad

Un asset difícil se administra como `MASTER ASSET` y puede producir una familia de derivados. Cada asset debe registrar, como mínimo:

1. temperatura visual;
2. costo de producción;
3. personalización;
4. rareza;
5. origen y linaje;
6. estado curatorial;
7. usos permitidos y derivados.

Estados iniciales: `SOURCE`, `CANDIDATE`, `SUPPORT`, `CANON`, `MASTER`, `HERO` y `REJECT`.

Nada premium viaja al navegador antes de que el backend valide autorización. Los originales, masters, referencias de identidad, workflows y materiales de laboratorio permanecen privados. El frontend refleja permisos; no los concede.

El lanzamiento es `library-first`. Ante un pedido de selfie, el LLM emite una intención tipada y el backend selecciona un asset autorizado, registra la entrega, evita repeticiones y emite una URL firmada. El modelo nunca recibe autoridad sobre rutas, permisos o archivos. Video se incorpora después desde biblioteca preproducida. No se activa GPU para reemplazar un corpus que el owner ya produce y cura.

## 7. Arquitectura

### Stack de base

- monorepo con `pnpm`;
- Next.js y TypeScript para la web;
- FastAPI, Python y Pydantic para la API;
- dominio independiente de proveedores mediante interfaces y adaptadores;
- PostgreSQL como persistencia durable objetivo;
- Redis para cache, colas y estado temporal cuando exista un caso medido;
- object storage privado, CDN y URLs firmadas para medios;
- Docker Compose en el VPS CPU;
- Cloud Lab GPU separado del runtime del producto.

### Estado verificado del código actual

- existen web Next.js y API FastAPI;
- el frontend porta la composición visual del primer landing y el flujo interactivo del segundo;
- `bardera` es el personaje canónico del lanzamiento y `vane` permanece como alias transitorio de compatibilidad;
- existe abstracción de proveedor y adaptador OpenAI-compatible;
- existen conversación multi-turn y memorias explícitas en proceso;
- existen locks por scope, errores tipados, retries y pruebas;
- PostgreSQL y Redis son objetivos, pero no se ejecutan hasta que adaptadores reales los consuman;
- Caddy publica web y API bajo un solo origen y enruta `/api/*` hacia FastAPI;
- no hay autenticación real;
- conversación y memoria se pierden al reiniciar el proceso;
- no hay todavía storage privado, entitlements, créditos ni pagos implementados;
- el logo oficial y tres fotos provisionales son copias verificadas con procedencia documentada;
- el flujo público, responsive, chat contra API y páginas legales pasaron QA local;
- las imágenes provisionales no constituyen entrega premium ni sustituyen autorización de media;
- el build de contenedores y el contrato Compose todavía requieren validación en el VPS.

No presentar capacidades objetivo como si ya estuvieran implementadas.

## 8. Proveedores y modelos

Ningún proveedor define el dominio. El backend conserva un router y adaptadores intercambiables. La elección de modelo se decide mediante evaluación de calidad, latencia, costo, estabilidad y cumplimiento, no por una conversación histórica.

Los prompts de sistema, scopes y autorizaciones son responsabilidad del servidor. El cliente no suministra instrucciones confiables ni decide permisos.

La salida de un proveedor también es no confiable. Antes de almacenarla, el servidor valida que no contenga identidad del proveedor, fragmentos internos ni una ruptura genérica de guardrail. Si falla, intenta el proveedor secundario configurado y finalmente usa un fallback de continuidad registrado para la Queen. Un fallo técnico se presenta como sistema, nunca como voz del personaje. La decisión está registrada en el ADR 0002.

La selección exacta sigue pendiente. El casting de trabajo considera Llama 3.3 70B para conversación, Llama 4 Maverick para una ruta multimodal futura, Gemini Flash para procesamiento interno o respaldo y Llama 3.1 8B para tareas económicas no visibles. Esta lista no es canon cerrado ni autoriza self-hosting en el VPS CPU.

## 9. Cloud Lab

Cloud Lab es infraestructura privada y separada para producción visual reproducible. Puede usar GPU bajo demanda, ComfyUI, Flux, FaceID/IPAdapter, ControlNet/OpenPose, LoRAs y upscale según el workflow validado.

Principio:

> Cloud Lab produce contenido. RiotQueens lo selecciona, contextualiza y entrega.

Secuencia inicial:

1. biblioteca preproducida y curada;
2. generación bajo demanda solo cuando tier, créditos y economía estén definidos;
3. enfoque híbrido `library-first` cuando exista un caso medido.

Para I2V, la prioridad es identidad facial estable por encima de animación compleja. Los workflows históricos son pistas de investigación y no se consideran ejecutables hasta validar nodos, modelos, versiones y conexiones.

## 10. Seguridad y operación

- secretos solo en variables o gestores de secretos;
- fixtures sin personas reales, datos personales ni medios privados;
- auth real antes de confiar en `user_id`;
- entitlements validados en backend;
- storage privado y URLs firmadas de vida corta;
- allowlist con SHA-256 para cada preview deliberadamente público;
- rate limiting como defensa secundaria;
- logs sin secretos ni contenido sensible innecesario;
- backups probados y restauración documentada;
- el VPS no sirve directorios personales ni archivos por un servidor improvisado;
- despliegue desde un directorio dedicado, detrás de proxy TLS y firewall mínimo.

### Acceso +18 y consentimiento

- el acceso protegido usa clickwrap versionado con casillas sin premarcar;
- chat, cuenta y premium requieren aceptación vigente validada por backend;
- el servidor registra timestamp UTC, versiones y hashes de los documentos aceptados;
- cambios materiales requieren nueva aceptación;
- marketing y notificaciones se consienten por separado;
- no se recopila identidad adicional para edad sin un requisito medido.

El contrato está registrado en el ADR 0004. La constancia es evidencia de aceptación, no reemplazo de privacidad, seguridad ni revisión legal por jurisdicción.

## 11. Forma de trabajo

Cada entrega distingue:

- **VERIFICADO:** evidencia observada con herramientas;
- **INFERENCIA:** conclusión razonable aún no confirmada;
- **PROPUESTA:** decisión sugerida para aprobación o implementación;
- **PENDIENTE:** dato o acción que todavía falta.

Antes de modificar:

1. inspeccionar branch, commit y estado real;
2. medir baseline;
3. revisar contratos afectados;
4. implementar una pieza acotada;
5. ejecutar lint, build y pruebas proporcionales al riesgo;
6. auditar diff, responsive y seguridad;
7. commitear y publicar evidencia;
8. desplegar de forma controlada y ejecutar smoke tests.

Las decisiones que cambien límites, contratos o arquitectura requieren ADR.

## 12. Próximos cortes

### Verificado

- repo remoto y branch arquitectónico recuperados;
- ambos landings canon identificados y hasheados;
- composición e interacción de ambos landings trasladadas al frontend funcional;
- logo oficial bloqueado incorporado como copia byte-idéntica;
- lenguaje público activo normalizado y páginas legal/privacidad creadas;
- frontend lint/build, backend lint/tests y QA responsive local superados;
- routing de lanzamiento documentado en ADR 0001;
- VPS activo y accesible por clave SSH;
- SSH endurecido, UFW activo y runtime Docker instalado;
- release `570ed7e` desplegada y smoke tests HTTP por IP superados;
- límite de identidad del proveedor y fallback server-owned cubiertos por regresiones;
- allowlist pública de media con prueba de CI deny-by-default;
- base frontend/backend y pruebas existentes recuperadas;
- manifiestos visuales y parte de la documentación histórica localizados.

### Pendiente

- resolver auth y persistencia durable;
- definir storage/CDN y autorización de media;
- cerrar pricing y economía de créditos;
- consolidar taxonomía y masters visuales;
- configurar el registro DNS y emitir TLS;
- definir observabilidad y restauración mínima;
- implementar auth y clickwrap versionado;
- inventariar `/imagenes` y `FOTOS_FINALES` trabajando sólo con copias;
- repetir smoke tests sobre el dominio por HTTPS.
