# ADR 0002 — Router de modelos

El dominio depende de `ModelProvider`, no de SDKs. Las rutas semánticas (`fast_chat`, `creative_chat`, `deep_reasoning`, `vision`, `agent_task`, `memory`) se asignan a proveedores por configuración. El bootstrap usa mock y retry acotado.
