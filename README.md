# RiotQueens.ai

RiotQueens.ai es una experiencia `+18` de personajes virtuales ficticios, originales y curados por el owner. La plataforma pone a cada Queen al frente y esconde la complejidad de modelos, memoria, proveedores y media detrás de una conversación coherente.

> **LANDINGS MANDAN. PRODUCTO DEBAJO. COMPLEJIDAD ESCONDIDA. QUEEN AL FRENTE.**

## Canon

- [`SPECT.md`](SPECT.md): producto, arquitectura, estado verificado y próximos cortes.
- [`AGENTS.md`](AGENTS.md): reglas operativas para cualquier agente o contribuidor.
- [`RIOTQUEENS_CODEX_PHASE2_HANDOFF_ORGANIZADO.md`](RIOTQUEENS_CODEX_PHASE2_HANDOFF_ORGANIZADO.md): estado operativo de la recuperación, evidencia auditada y continuidad para el siguiente agente.
- [`docs/DECISION_REGISTER.md`](docs/DECISION_REGISTER.md): decisiones recuperadas, estado y pendientes que no deben volver a depender de un chat.
- [`docs/EXTERNAL_FAILURE_PATTERN.md`](docs/EXTERNAL_FAILURE_PATTERN.md): patrón sanitizado de ruptura de scope, contexto y personaje observado en productos externos.
- [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md): contrato y evidencia del primer despliegue.
- `Riotqueens-Ai-Landing-Mock.html`: autoridad visual, compositiva y de ADN de diseño dentro del alcance reconocido por las fuentes vigentes.
- `Reiniciando-chat-anterior.html`: autoridad de continuidad e interacción.

`RiotQueens-worktree` es el único repo canónico porque contiene Git, CI, despliegue y el estado ejecutable. `/home/rybjuani/Escritorio/RiotQueens` es el pool creativo local de origen: no es otro producto ni otra autoridad, no se sirve desde el VPS y no se elimina automáticamente. Sus materiales sólo entran al repo como copias verificadas, derivados o registros de procedencia.

La documentación stale se elimina del HEAD y su respaldo de contingencia se guarda en `/home/rybjuani/Documentos/_scratch_trash/`; sólo puede recuperarse por decisión explícita actual del owner.

Las copias crudas de los landings están registradas por SHA-256 en el SPECT y permanecen fuera del runtime por sus bundles y datos embebidos. Su composición y su flujo ya fueron auditados y portados al frontend funcional. El logo oficial y los assets provisionales versionados conservan procedencia y hash en [`docs/ASSET_PROVENANCE.md`](docs/ASSET_PROVENANCE.md).

## Estado real

### Implementado

- monorepo `pnpm`;
- frontend Next.js alineado con los dos landings canon;
- backend FastAPI;
- router desacoplado y proveedor OpenAI-compatible;
- mock para desarrollo y pruebas;
- prompt de sistema controlado por servidor;
- salida LLM validada, fallback secundario opcional y continuidad server-owned;
- La Bardera como Queen canónica y única implementada en runtime;
- experiencia activa T0/free con Bardera, independiente de los tiers T1–T3 todavía no definidos;
- Queen registrada, routing y contexto validados del lado servidor; `/v1/chat` no acepta una ruta elegida por el cliente ni expone diagnósticos internos del provider;
- conversación multi-turn y memorias explícitas acotadas en proceso;
- historial visible recuperado al reabrir el chat para el mismo scope efímero mientras vive el proceso;
- identificadores aleatorios de prototipo por pestaña, explícitos y acotados, sin tratarlos como identidad autenticada;
- retries, errores tipados, validación y tests;
- flujo landing → chat, tiers, páginas legal/privacidad y responsive verificados localmente;
- Caddy como entrada única para web y `/api/*`;
- allowlist SHA-256 que impide incorporar media premium o no registrada a `public/`;
- primer despliegue HTTP por IP validado en el VPS.

### Todavía no implementado

- autenticación real;
- clickwrap +18 versionado y validado por backend;
- persistencia durable de conversaciones y memorias;
- integración de PostgreSQL y Redis con el dominio;
- storage privado, CDN y URLs firmadas;
- entitlements, créditos y pagos;
- entrega autorizada de media premium;
- Cloud Lab conectado al producto (dirección futura documentada; no disponible);
- dominio de producción y TLS validados.

Un reinicio de la API borra conversación y memoria actuales. Los identificadores de usuario prototipo y conversación son scopes controlados por el navegador, no cuentas ni identidades seguras. La API rechaza Queens no registradas y ya no publica endpoints WIP de perfil, personajes configurables o media mock.

## Stack

- Next.js 14, React 18 y TypeScript
- FastAPI, Python 3.12, Pydantic y HTTPX
- PostgreSQL y Redis como objetivos de infraestructura
- Docker Compose para ejecución y despliegue
- proveedor de modelos desacoplado mediante adaptadores

## Cómo se construye una Queen

La esencia compartida de RiotQueens se combina con una identidad, voz, glosario y benchmark independientes por Queen. [`docs/QUEEN_CURATION_PIPELINE.md`](docs/QUEEN_CURATION_PIPELINE.md) documenta el flujo NotebookLM → informe estructurado → perfil versionado → prueba de modelo → registro de aprobación. Aprobar el benchmark de modismos de La Bardera es un criterio de casting para ese modelo y esa configuración; no convierte a Bardera en la voz de las demás.

`Qwen_html.html`, `MANIFIESTO_BARDI.pdf`, `barderainvernadero.png` y los manifiestos del owner fueron auditados como fuentes de diseño, misión, visión y curaduría. No se copian automáticamente al runtime: su clasificación y hashes están en [`docs/canon/QUEEN_SOURCE_REGISTER.md`](docs/canon/QUEEN_SOURCE_REGISTER.md).

## Proveedores y laboratorio

OpenRouter/Llama sigue siendo el proveedor primario configurado del entorno de prueba y Hugging Face es un fallback opcional ya validado en smoke. Google AI Studio (`GEMINI_API_KEY`) queda incorporado al roadmap como proveedor multimodal y de laboratorio; la API respondió en smoke, pero la batería de voz y la ruta multimodal todavía deben aprobarse. La propuesta Gemma + Ollama + llama.cpp se documenta en [`docs/PROVIDER_LAB.md`](docs/PROVIDER_LAB.md), sin prometer capacidad pública ni commitear credenciales.

## Repositorio

```text
apps/web/       frontend actual
apps/api/       API, dominio, proveedores y tests
ops/            proxy y contrato operativo
config/         políticas verificables, incluida la allowlist de media pública
SPECT.md        especificación canónica vigente
AGENTS.md       reglas de contribución y orquestación
```

## Desarrollo local

Requisitos: Python 3.12+, Node 20+, pnpm 9+ y Docker Compose.

```bash
cp .env.example .env
make setup
make lint
make test
```

El Compose de lanzamiento ejecuta `web`, `api` y `caddy`. PostgreSQL y Redis no se levantan todavía porque el dominio no tiene adaptadores que los consuman. El proveedor por defecto es `mock`: no se debe presentar esa respuesta como calidad conversacional final.

El primario OpenRouter/Llama se configura con `RIOTQUEENS_MODEL_*`. El fallback independiente de Hugging Face se registra con `RIOTQUEENS_FALLBACK_MODEL_*`. Google AI Studio y Ollama usan variables server-side documentadas en `.env.example`; ninguna clave se expone al frontend. El único archivo de configuración local es `.env` en la raíz de este repo, ignorado por Git. Nunca se copia `.env_final(1)` ni una clave real al repo.

## Próximo objetivo

1. elegir el mecanismo de autenticación y cerrar jurisdicciones, versiones legales y retención;
2. implementar auth y clickwrap antes de considerar protegido el acceso al chat;
3. conectar persistencia durable sin cambiar los scopes del dominio;
4. configurar DNS/TLS y repetir smoke tests sobre una release identificada;
5. avanzar con media privada y entitlements sólo después de definir autorización y oferta comercial.

Para retomar el trabajo, leer en este orden: `AGENTS.md`, `SPECT.md`, este README, el handoff operativo, `docs/DECISION_REGISTER.md` y el documento específico de la tarea. Cada cambio debe dejar evidencia, pruebas proporcionales y un commit convencional.
