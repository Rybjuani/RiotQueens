# RiotQueens.ai

RiotQueens.ai está reconstruyendo su base canónica sobre una arquitectura útil ya existente. El objetivo inmediato es conectar dos landings autoritativos con una experiencia real de conversación, memoria y presencia audiovisual, sin ocultar las limitaciones actuales.

> **LANDINGS MANDAN. PRODUCTO DEBAJO. COMPLEJIDAD ESCONDIDA. QUEEN AL FRENTE.**

## Canon

- [`SPECT.md`](SPECT.md): producto, arquitectura, estado verificado y próximos cortes.
- [`AGENTS.md`](AGENTS.md): reglas operativas para cualquier agente o contribuidor.
- `Riotqueens-Ai-Landing-Mock.html`: autoridad visual y de marca.
- `Reiniciando-chat-anterior.html`: autoridad de continuidad e interacción.
- [`docs/legacy/`](docs/legacy/README.md): documentación histórica preservada, no normativa.

Las copias de los dos landings están identificadas localmente y registradas por SHA-256 en el SPECT. Todavía no fueron importadas al repo: primero deben auditarse sus assets y datos embebidos.

## Estado real

### Implementado

- monorepo `pnpm`;
- frontend Next.js;
- backend FastAPI;
- router desacoplado y proveedor OpenAI-compatible;
- mock para desarrollo y pruebas;
- prompt de sistema controlado por servidor;
- conversación multi-turn y memorias explícitas acotadas en proceso;
- retries, errores tipados, validación y tests.

### Todavía no implementado

- autenticación real;
- persistencia durable de conversaciones y memorias;
- integración de PostgreSQL y Redis con el dominio;
- storage privado, CDN y URLs firmadas;
- entitlements, créditos y pagos;
- entrega de media real;
- Cloud Lab conectado al producto;
- despliegue de producción validado.

Un reinicio de la API borra conversación y memoria actuales. El `user_id` es un scope de prototipo, no una identidad segura.

## Stack

- Next.js 14, React 18 y TypeScript
- FastAPI, Python 3.12, Pydantic y HTTPX
- PostgreSQL y Redis como objetivos de infraestructura
- Docker Compose para ejecución y despliegue
- proveedor de modelos desacoplado mediante adaptadores

## Repositorio

```text
apps/web/       frontend actual
apps/api/       API, dominio, proveedores y tests
docs/legacy/    documentación histórica de Companion Studio
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

El flujo `make dev` y los puertos de Docker deben validarse antes de considerarlos una receta de despliegue. No desplegar el Compose actual sin esa comprobación.

## Próximo objetivo

1. incorporar ambos landings después de auditar sus assets;
2. fijar el contrato de navegación V1 → V2 → aplicación;
3. medir baseline completo de web, API y contenedores;
4. corregir lenguaje público heredado;
5. resolver seguridad mínima del VPS y primer deploy controlado;
6. avanzar luego con auth, persistencia y media privada.
