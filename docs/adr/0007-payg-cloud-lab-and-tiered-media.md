# ADR 0007: Cloud Lab pay-as-you-go y media por tier

- **Estado:** aceptado como dirección futura, no implementado
- **Fecha:** 2026-08-15
- **Decisores:** owner del producto

## Contexto

La propuesta externa de Cloud Lab describe producción visual con ComfyUI en una GPU cloud efímera, con referencias de identidad, pose y upscale. También contempla que usuarios con beneficios avanzados adjunten fotos y reciban media generada. El VPS actual no tiene GPU y no debe convertirse en un host de inferencia pesada por anticipación.

## Decisión

RiotQueens mantendrá el VPS como plano de control CPU y tratará RunPod/Vast u otro proveedor equivalente como adaptador opcional de GPU bajo demanda. La producción inicial será `library-first`. La generación bajo demanda, las cargas de fotos y la entrega de derivados sólo podrán habilitarse en tiers como T2/T3 después de implementar autenticación, entitlements, consentimiento, storage privado, política de contenido, ledger de costos, límites y URLs firmadas.

Cloud Lab produce contenido; RiotQueens lo selecciona, contextualiza y entrega. La generación no crea canon automáticamente y el proveedor nunca define identidad, permisos ni continuidad de una Queen.

## Consecuencias

- se puede experimentar con capacidad visual sin pagar una GPU 24/7 ni acoplar el dominio a un proveedor;
- los trabajos pueden detener el pod al terminar y registrar costo, modelo, workflow y procedencia;
- la experiencia de adjuntar y compartir fotos exige un contrato de media separado del chat;
- T2/T3 no se anuncian ni cobran por esta capacidad hasta que exista una implementación verificable;
- habrá trabajo adicional de storage, seguridad, moderación, retención, colas y observabilidad.

## No decidido todavía

Proveedor, región, presupuesto máximo, modelo/checkpoint, workflow productivo, política de retención, integración de pagos y fecha de activación. Las cifras de las capturas de la propuesta son variables y no son un presupuesto aprobado.
