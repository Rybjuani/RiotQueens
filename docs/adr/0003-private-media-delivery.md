# ADR 0003 — Entrega privada de media

**Estado:** aceptado

**Fecha:** 2026-08-09

## Contexto

Todo archivo enviado al navegador puede inspeccionarse y copiarse. Detectar la apertura de DevTools no es confiable y un ban por esa señal produciría falsos positivos. El control debe ocurrir antes de entregar bytes.

## Decisión

- `apps/web/public/` contiene únicamente marca y previews deliberadamente públicos, registrados por ruta y SHA-256.
- CI falla si aparece allí un raster no registrado, un hash cambia o una entrada se clasifica como premium.
- Masters, originales y media premium vivirán en object storage privado.
- Un endpoint autenticado validará usuario, entitlement, tier y asset antes de emitir una URL firmada breve o transmitir el archivo.
- Las claves de objeto no serán predecibles ni enumerables y el frontend nunca decidirá permisos.
- Rate limits, detección de scraping, revocación, ban y watermark individual son controles secundarios.

## Consecuencias

- Un visitante anónimo solo puede descargar previews que ya fueron declarados públicos.
- Un usuario no autorizado nunca recibe la URL ni los bytes premium.
- Un usuario autorizado aún puede guardar lo que ve; watermark, trazabilidad y términos permiten atribuir abuso, no impedir físicamente toda copia.
- No se subirá media premium hasta implementar auth, entitlements y el gateway privado.
