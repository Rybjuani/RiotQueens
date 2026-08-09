# Arquitectura

## Límites

`apps/web` es una interfaz Next.js mobile-first. `apps/api` contiene contratos, casos de uso HTTP y adaptadores. El dominio no importa SDKs de proveedores. PostgreSQL será la persistencia durable; Redis queda reservado para caché, colas y estado temporal. El corte vertical usa repositorios en memoria detrás de protocolos.

## Flujo de chat

HTTP → contrato `ChatRequest` → `ModelRouter` → proveedor → buffer → `OutputValidator` → respuesta validada. Una salida inválida no se guarda ni factura; se permite un retry y luego una recuperación segura.

## Medios

`GET /v1/media/mock` devuelve metadata de placeholder. No hay archivos reales ni afirmación de generación en vivo. La siguiente misión puede conectar almacenamiento de objetos y URLs temporales mediante un puerto.

## Futuro puente local

Un agente local trabajará sobre copias autorizadas, siempre con preview, trazabilidad y confirmación para acciones destructivas. Nunca debe tocar originales.

## Decisiones pendientes

Persistencia SQL, autenticación, contratos de cliente generados desde OpenAPI, moderación y proveedores reales quedan fuera del bootstrap.
