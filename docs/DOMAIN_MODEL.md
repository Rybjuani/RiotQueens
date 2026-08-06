# Modelo de dominio

| Entidad | Propósito y campos esenciales | Sensibles/relaciones | Ciclo de vida y fuera del MVP |
|---|---|---|---|
| User | identidad, locale, estado | PII; posee perfil y conversaciones | alta/pausa/borrado; auth fuera |
| UserPreferenceProfile | idioma, estilo, iniciativa, intensidades, notificaciones, visual | preferencias; pertenece a User | versionable; edición avanzada fuera |
| Character | identidad, personalidad, límites, capacidades | configuración propia; pertenece a User/tenant | draft/active/archived; marketplace fuera |
| CharacterPreset | preset editable y sus valores | referencia a Character | draft/published; catálogo fuera |
| Conversation | character_id, estado narrativo, timestamps | contexto sensible; contiene mensajes | open/closed; multi-personaje fuera |
| Message | role, content, provider, validation, billable | contenido sensible; pertenece a Conversation | pending/valid/rejected |
| Memory | tipo, hecho/inferencia, contenido, source, consent | dato sensible; aislada por usuario/personaje/proyecto | active/deleted/expired |
| SessionOverride | scope, overrides, starts/expires, reason | preferencias temporales | active/expired/reverted |
| MediaAsset | tags, origen, derechos, versión, intensidad | derechos y contenido adulto | catalogued/retired; archivos reales fuera |
| MediaDelivery | asset, contexto, reacción, timestamps | historial de consumo | delivered/seen; selector avanzado fuera |
| ModelRequest | route, ids, messages, memories, tools, metadata | prompt/contexto | created/sent |
| ModelResponse | provider, model, content, usage, latency, validation | salida del proveedor | received/validated |
| OutputValidationResult | checks, reasons, valid/billable | diagnóstico, no contenido de usuario | accepted/rejected |
| ToolExecution | herramienta, preview, inputs, outputs, actor | rutas de archivos | proposed/confirmed/completed |
| CreditLedgerEntry | delta, reason, reference, balance | facturación | posted/reversed; pagos fuera |

Los contratos iniciales se implementan en `apps/api/app/domain/contracts.py`. Las tablas SQL se agregarán cuando existan decisiones de autenticación, migraciones y retención.
