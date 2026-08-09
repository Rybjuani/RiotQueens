# ADR 0005 — Validación de salida

Toda respuesta cruza buffer y validador antes de mostrarse o persistirse. Si falla, se reintenta una sola vez; luego se usa recuperación segura. Las salidas inválidas no son válidas, no entran en memoria y no se facturan.
