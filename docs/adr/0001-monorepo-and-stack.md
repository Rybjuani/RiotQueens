# ADR 0001 — Monorepo y stack

Usamos pnpm workspaces para web/paquetes y Python 3.12 + FastAPI para API. Docker Compose incluye PostgreSQL y Redis. El objetivo es reducir acoplamiento y permitir que cada agente ejecute comandos raíz consistentes.
