# MISIÓN 001 — Bootstrap arquitectónico de Companion Studio

Estás operando dentro del repositorio local:

`/home/rybjuani/Escritorio/Companion Studio/`

Repositorio remoto:

`Rybjuani/Companion-Studio`

## Contexto

El repositorio contiene el documento `SPECT.md` o una variante equivalente con la especificación de producto de Companion Studio.

Companion Studio es una plataforma de compañeras virtuales adultas con:

- onboarding conversacional mediante una anfitriona;
- perfil global reutilizable del usuario;
- personajes configurables;
- memoria persistente;
- conversación mediante proveedores LLM intercambiables;
- biblioteca audiovisual reactiva;
- validación de salidas;
- capacidades futuras de agente y entregables.

Tu función en esta misión es actuar como arquitecta principal del código.

## Restricción de presupuesto

Hay poco presupuesto de cómputo disponible. Priorizá decisiones de alto valor, contratos estables y un esqueleto ejecutable. No gastes tiempo perfeccionando diseño visual ni implementando funciones fuera del alcance.

No hagas preguntas salvo que exista un bloqueo real e imposible de resolver inspeccionando el repositorio. Tomá decisiones razonables, documentá las suposiciones y avanzá.

---

# Objetivo

Dejar un monorepo limpio, ejecutable y preparado para que otros agentes puedan continuar sin reinterpretar el producto ni acoplarlo a un proveedor específico.

La misión debe entregar:

1. arquitectura documentada;
2. reglas para futuros agentes;
3. estructura del monorepo;
4. contratos del dominio;
5. abstracción de proveedores LLM;
6. un corte vertical mínimo funcionando;
7. pruebas básicas;
8. instrucciones reproducibles;
9. commits claros.

---

# Paso 1 — Inspección y preservación

1. Inspeccioná el repositorio y leé completamente el SPECT.
2. No reescribas ni reduzcas su contenido.
3. Si está en la raíz, podés conservarlo allí o copiarlo a `docs/SPECT.md`, dejando una referencia clara desde el README.
4. Confirmá el estado de Git y el remoto.
5. Creá una rama:

```bash
git checkout -b chore/bootstrap-architecture
```

6. No hagas force push.
7. No agregues secretos, API keys, archivos `.env`, material audiovisual real ni contenido privado.

El repositorio es público. Tratá todo lo commiteado como material visible para cualquiera.

---

# Paso 2 — Decisiones tecnológicas

Usá este stack inicial, salvo incompatibilidad real demostrable:

## Monorepo

- pnpm workspaces;
- estructura simple, sin Turborepo salvo que sea estrictamente necesario;
- comandos raíz consistentes.

## Frontend

- Next.js;
- TypeScript estricto;
- Tailwind CSS;
- interfaz inicial en español;
- componentes accesibles;
- diseño mobile-first.

## Backend

- Python 3.12;
- FastAPI;
- Pydantic;
- SQLAlchemy;
- Alembic;
- PostgreSQL;
- Redis preparado para cola/caché, aunque el MVP use poco.

## Desarrollo

- Docker Compose;
- Ruff;
- Pytest;
- ESLint;
- Prettier;
- pruebas frontend ligeras;
- GitHub Actions para lint y tests.

## Inferencia

No integres todavía ningún proveedor real.

Creá interfaces y un `MockModelProvider`. La futura integración con OpenRouter, Groq, modelos propios u otros proveedores debe ocurrir mediante adaptadores.

---

# Paso 3 — Estructura esperada

Creá una estructura equivalente a:

```text
Companion-Studio/
├── AGENTS.md
├── README.md
├── Makefile
├── .editorconfig
├── .gitignore
├── .env.example
├── docker-compose.yml
├── pnpm-workspace.yaml
├── package.json
├── apps/
│   ├── web/
│   └── api/
├── packages/
│   ├── ui/
│   └── config/
├── docs/
│   ├── SPECT.md
│   ├── ARCHITECTURE.md
│   ├── DOMAIN_MODEL.md
│   ├── API_CONTRACT.md
│   ├── ROADMAP.md
│   ├── HANDOFF.md
│   └── adr/
│       ├── 0001-monorepo-and-stack.md
│       ├── 0002-model-router.md
│       ├── 0003-memory-layers.md
│       ├── 0004-media-library.md
│       └── 0005-output-validation.md
└── .github/
    └── workflows/
        └── ci.yml
```

Podés ajustar nombres menores si mejoran claridad, pero mantené la separación de responsabilidades.

---

# Paso 4 — AGENTS.md

Creá un `AGENTS.md` breve pero firme para todos los agentes futuros.

Debe exigir:

- leer `docs/SPECT.md` antes de modificar producto;
- no cambiar arquitectura sin ADR;
- no acoplar dominio a un proveedor LLM;
- no guardar secretos;
- no commitear medios reales;
- no modificar originales en herramientas de archivos;
- trabajar en ramas;
- ejecutar pruebas antes de commit;
- usar commits convencionales;
- mantener interfaz en español y código/identificadores en inglés;
- documentar supuestos;
- evitar sobreingeniería;
- no implementar pornografía explícita en el MVP;
- no afirmar generación en tiempo real para archivos precargados;
- preservar trazabilidad de memoria, configuración, créditos y medios.

---

# Paso 5 — Modelo de dominio

Definí y documentá como mínimo estas entidades:

- `User`
- `UserPreferenceProfile`
- `Character`
- `CharacterPreset`
- `Conversation`
- `Message`
- `Memory`
- `SessionOverride`
- `MediaAsset`
- `MediaDelivery`
- `ModelRequest`
- `ModelResponse`
- `OutputValidationResult`
- `ToolExecution`
- `CreditLedgerEntry`

Para cada entidad indicá:

- propósito;
- campos esenciales;
- relaciones;
- datos sensibles;
- ciclo de vida;
- qué queda fuera del MVP.

No hace falta implementar todas las tablas. Sí deben quedar definidos los límites.

---

# Paso 6 — Contratos imprescindibles

Implementá contratos Pydantic para:

## Perfil global

```text
language
locale
response_style
verbosity
stage_directions
translation_overlay
humor_style
initiative_level
romantic_intensity
sensual_intensity
notification_preferences
visual_preferences
agent_interests
```

## Configuración por personaje

```text
name
identity
personality_traits
relationship_dynamic
speech_style
initiative_level
sensual_intensity
boundaries
capabilities
visual_style
voice_style
```

## Ajustes temporales

```text
scope
starts_at
expires_at
overrides
reason
```

## Petición al router

```text
route
character_id
user_id
conversation_id
messages
memories
tools
metadata
```

## Respuesta del router

```text
provider
model
content
usage
latency_ms
validation
retry_count
```

## Resultado de validación

```text
is_valid
language_ok
encoding_ok
not_truncated
not_repetitive
no_internal_leak
character_consistent
reasons
```

Generá OpenAPI desde FastAPI. No dupliques manualmente contratos en TypeScript si pueden obtenerse de OpenAPI; documentá cómo generar el cliente en una misión futura.

---

# Paso 7 — Router de modelos

Definí una interfaz clara:

```python
class ModelProvider(Protocol):
    async def generate(self, request: ModelRequest) -> ModelResponse:
        ...
```

Definí rutas:

- `fast_chat`
- `creative_chat`
- `deep_reasoning`
- `vision`
- `agent_task`
- `memory`

Implementá:

- `ModelRouter`;
- `MockModelProvider`;
- selección de proveedor por ruta;
- timeout;
- manejo de error;
- metadatos de latencia;
- retry limitado;
- ningún fallback infinito.

No integres APIs reales. Dejá adaptadores futuros documentados.

---

# Paso 8 — Pasarela de validación

Implementá un validador mínimo y determinista para detectar:

- respuesta vacía;
- caracteres de control;
- exceso anormal de símbolos;
- mezcla accidental de múltiples escrituras/idiomas;
- truncamiento evidente;
- repetición excesiva;
- fragmentos internos típicos;
- longitud fuera de rango.

No pretendas resolver semántica perfecta.

Flujo obligatorio:

```text
provider
→ buffer
→ validator
→ accept | retry once | fallback
```

Una salida inválida:

- no debe guardarse como mensaje válido;
- no debe entrar en memoria;
- debe marcarse como no facturable;
- debe quedar registrada para diagnóstico.

Incluí pruebas unitarias con ejemplos normales y un ejemplo de salida multilingüe corrupta.

---

# Paso 9 — Corte vertical mínimo

Construí una experiencia mínima, fea pero funcional.

## Pantalla 1: bienvenida

Una anfitriona presenta la experiencia y guía cinco decisiones:

1. estilo de personalidad;
2. dinámica de relación;
3. nivel de iniciativa;
4. intensidad romántica/sensual no explícita;
5. estilo visual.

No uses un robot ni formularios técnicos.

## Pantalla 2: resumen

Mostrar:

- perfil inferido;
- personaje inicial;
- cambios editables;
- botón confirmar;
- botón volver.

## Pantalla 3: chat de prueba

- UI básica de chat;
- mensaje del usuario;
- respuesta del `MockModelProvider`;
- indicador del proveedor;
- resultado de validación visible solo en modo desarrollo;
- tarjeta de “video enviado” usando un placeholder, no un medio real.

## Backend mínimo

Endpoints sugeridos:

```text
GET  /health
POST /v1/onboarding/profile
POST /v1/characters
POST /v1/chat
GET  /v1/media/mock
```

La persistencia puede comenzar con PostgreSQL. Si el tiempo es insuficiente, dejá un repositorio en memoria detrás de una interfaz y documentá el reemplazo, pero Docker Compose debe incluir PostgreSQL para la siguiente misión.

---

# Paso 10 — Reglas de interfaz

- español natural;
- ningún término como temperatura, tokens, embedding o system prompt en onboarding;
- cinco decisiones principales como máximo;
- usable con teclado;
- contraste razonable;
- responsive;
- sin diseño final;
- sin assets sexuales reales;
- sin imágenes generadas;
- placeholders claramente identificados en código;
- no afirmar que un video fue generado en vivo.

Texto conceptual:

> Precisión profunda para quien la busca. Simplicidad absoluta para quien solo quiere empezar.

---

# Paso 11 — Documentación

## README.md

Debe incluir:

- qué es Companion Studio;
- estado del proyecto;
- arquitectura resumida;
- requisitos;
- inicio rápido;
- comandos;
- pruebas;
- estructura;
- seguridad de secretos;
- enlaces al SPECT y ADRs.

## ARCHITECTURE.md

Debe explicar:

- frontend;
- backend;
- persistencia;
- router;
- validación;
- medios;
- futuro puente local;
- límites entre dominio e infraestructura.

## ROADMAP.md

Dividir en:

- Fase 0: investigación;
- Fase 1: prototipo personal;
- Fase 2: MVP cerrado;
- Fase 3: beta;
- Fase 4: plataforma.

## HANDOFF.md

Explicar qué debe hacer después:

- Gemini CLI;
- un agente fullstack;
- un revisor fuerte;
- el responsable de producto.

Listar tareas mecánicas separadas de decisiones arquitectónicas.

---

# Paso 12 — Comandos de desarrollo

Proporcioná comandos simples, preferentemente:

```bash
make setup
make dev
make test
make lint
make format
make down
```

Si no usás Makefile, documentá equivalentes claros.

`make dev` debe permitir levantar la aplicación con el menor trabajo manual posible.

---

# Paso 13 — Seguridad y repositorio público

Obligatorio:

- `.env` ignorado;
- `.env.example` sin valores reales;
- archivos multimedia reales ignorados;
- claves ignoradas;
- base de datos local ignorada;
- logs sensibles ignorados;
- ningún token en historial;
- ningún dato personal real en fixtures;
- ningún nombre o imagen de persona real en placeholders;
- advertencia visible en README.

No subas archivos grandes.

---

# Paso 14 — Validación final

Antes de terminar:

1. instalá dependencias si el entorno lo permite;
2. ejecutá lint;
3. ejecutá tests;
4. levantá o compilá web y API;
5. verificá `/health`;
6. verificá el flujo onboarding → resumen → chat;
7. revisá `git status`;
8. eliminá basura generada;
9. documentá cualquier limitación real.

No declares que algo funciona si no lo probaste.

---

# Paso 15 — Commits

Hacé commits lógicos, por ejemplo:

```text
chore: bootstrap companion studio monorepo
docs: add architecture and domain decisions
feat: add model router and output validation
feat: add onboarding vertical slice
test: cover router and corrupted output validation
```

No mezcles todo en un único commit si el trabajo permite separación razonable.

No hagas merge a `main`.

Al terminar entregá:

- resumen;
- árbol de archivos;
- decisiones;
- comandos ejecutados;
- pruebas que pasaron;
- limitaciones;
- commits;
- próximos cinco pasos ordenados por prioridad.

---

# Criterios de aceptación

La misión queda aprobada cuando:

- el SPECT está preservado y referenciado;
- existe `AGENTS.md`;
- la arquitectura está documentada;
- el dominio básico está definido;
- el router no depende de proveedor;
- existe `MockModelProvider`;
- existe validación de salida con pruebas;
- hay un onboarding de cinco decisiones;
- el chat mínimo funciona con mock;
- los medios reales están excluidos;
- no hay secretos;
- los comandos están documentados;
- lint y tests pasan, o los bloqueos reales están explicados;
- los cambios están en `chore/bootstrap-architecture`;
- hay commits claros;
- no se hizo merge a `main`.

## Prioridad si falta presupuesto

Si no alcanza el tiempo o el presupuesto, completá en este orden:

1. `AGENTS.md` y documentación arquitectónica;
2. contratos del dominio;
3. router y validador con pruebas;
4. esqueleto de API;
5. esqueleto web;
6. corte vertical;
7. estilos.

Nunca sacrifiques contratos y pruebas para decorar la interfaz.
