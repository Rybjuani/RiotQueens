# Companion Studio

Plataforma en construcción de compañeras virtuales adultas con memoria, presencia audiovisual y capacidades de agente. Esta misión entrega un esqueleto ejecutable: onboarding en español, contratos de dominio, API FastAPI, router desacoplado con mock, validador de salidas y chat de prueba.

Estado: bootstrap arquitectónico. No hay proveedores LLM reales, pagos ni medios reales.

## Inicio rápido

Requisitos: Python 3.12+, Node 20+, pnpm 9+, Docker Compose.

```bash
cp .env.example .env
make setup
make dev
```

Web: http://localhost:3000 · API: http://localhost:8000/docs · salud: http://localhost:8000/health

Comandos: `make test`, `make lint`, `make format`, `make down`.

## Arquitectura

Next.js consume una API FastAPI. El dominio define contratos Pydantic y protocolos; la infraestructura provee repositorios en memoria y un `MockModelProvider`. PostgreSQL y Redis están preparados en Compose, pero el corte vertical no depende todavía de ellos.

Ver [arquitectura](docs/ARCHITECTURE.md), [dominio](docs/DOMAIN_MODEL.md), [contrato API](docs/API_CONTRACT.md), [roadmap](docs/ROADMAP.md), [handoff](docs/HANDOFF.md) y [ADRs](docs/adr/0001-monorepo-and-stack.md). La especificación completa está en [SPECT](docs/SPECT.md).

## Seguridad pública

No commitear `.env`, claves, datos personales, archivos multimedia ni originales. Los placeholders audiovisuales son texto/metadata y no implican generación en vivo. El MVP excluye pornografía explícita.
