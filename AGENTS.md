# Companion Studio — reglas para agentes

Antes de modificar producto, leer `docs/SPECT.md` y el contexto de la tarea. La interfaz es en español natural; el código, identificadores y contratos internos usan inglés.

- No cambiar arquitectura sin agregar o actualizar un ADR.
- Mantener el dominio independiente de proveedores LLM; usar adaptadores e interfaces.
- Nunca guardar secretos, datos personales reales, medios reales ni nombres/imágenes de personas reales en fixtures.
- No implementar pornografía explícita en el MVP ni afirmar generación en tiempo real para archivos precargados.
- No modificar originales en herramientas de archivos: trabajar con copias, previews y confirmaciones.
- Preservar trazabilidad de memoria, configuración, créditos y medios.
- Trabajar siempre en una rama; usar commits convencionales; ejecutar pruebas y lint antes de commitear.
- Documentar supuestos, evitar sobreingeniería y mantener los límites entre dominio e infraestructura.

## Flujo recomendado

1. Leer el SPECT y la arquitectura relevante.
2. Agregar un ADR si la decisión cambia límites o contratos.
3. Implementar una pieza pequeña con pruebas.
4. Ejecutar `make test` y `make lint`.
5. Actualizar documentación y registrar limitaciones.
