### Manual de Legado Técnico: Blueprint de Producción SPECT

> **Estado:** Documento de visión, dirección técnica y legado. **No normativo.**
> **Jerarquía:** `SPECT.md`, `docs/ARCHITECTURE.md`, `docs/API_CONTRACT.md`, `docs/DOMAIN_MODEL.md` y los ADRs vigentes prevalecen ante cualquier contradicción.
> **Producto:** Companion Studio. “SPECT” se usa aquí como nombre interno del sistema de especificación/visión.

#### 1\. Declaración de Misión y Principio Rector

##### El Manifiesto SPECT: Ingeniería de Guerrilla y Vibecoding

Escuchame bien, trainee: SPECT no es un chatbot servil ni un catálogo de imágenes genéricas. Es una pieza de  **Vibecoding multidisciplinario**  diseñada para superar la pasividad y genericidad de las experiencias conversacionales actuales. Aquí fusionamos el  *feeling*  de la alta costura con la robustez de un sistema  *full-stack* . El propósito es la interacción virtual persistente: un vínculo inmersivo donde la profundidad narrativa y la identidad visual premium no son negociables. Estamos construyendo una personalidad imperfecta, memorable y disruptiva que recuerda quién sos.

##### Mantra del Proyecto

"Caótica en personaje. Coherente en memoria. Premium en imagen. Simple de configurar. Confiable en cada salida y entregable."

##### Pilares de Valor

* **Memoria Persistente (Tiers 1-3):**  Diferenciación quirúrgica entre hechos e inferencias a través de capas episódicas, relacionales y de identidad.
* **Iniciativa de Personaje:**  El motor de caos. La IA propone, contradice y cambia de humor basándose en el contexto acumulado, evitando respuestas excesivamente serviciales, genéricas o complacientes.
* **Identidad Coherente (Identity Lock):**  Un sistema de anclas visuales inamovibles (DNA Anchors) que blindan la cara y el estilo contra la deriva generativa.
* **Capacidades de Agente:**  No solo habla; trabaja. Organiza sesiones, clasifica activos mediante lógica de metadatos y prepara entregables reales para el usuario creativo.

#### 2\. Arquitectura Core del Sistema

##### Stack Tecnológico de Élite

Priorizamos portabilidad, soberanía de datos y desacoplamiento de proveedores. El core web puede desplegarse en infraestructura remota, mientras las operaciones locales de activos permanecen separadas.| Componente | Tecnología | Función Principal || \------ | \------ | \------ || **Frontend** | Next.js | Interfaz reactiva de alta jerarquía visual; minimalismo pro. || **Backend** | FastAPI | Orquestación agéntica y procesamiento lógico de alta velocidad. || **Sidecar local opcional** | **Tauri 2.x + Rust** | FileGrove / Asset Operations. Complementa al producto web; no reemplaza el backend FastAPI. || **Base de Datos Core** | PostgreSQL | Persistencia del producto web: perfiles, personajes, sesiones y memoria. |
| **Base de Datos Local** | SQLite | Diario transaccional exclusivo de FileGrove / Asset Operations. || **Caché** | Redis | Gestión de sesiones activas y respuesta inmediata de memoria. || **Infraestructura** | VPS (Hostinger) / Cloudflare | Seguridad perimetral y soberanía de prompts local. |

##### FileGrove: El Motor de Organización Autónoma

> **Límite arquitectónico:** FileGrove es una herramienta local/sidecar de Asset Operations. No forma parte del core web requerido para el MVP y no sustituye Next.js + FastAPI + PostgreSQL + Redis.

FileGrove no es un explorador de archivos; es un cerebro logístico construido en  **Rust y Tauri 2.x** .

* **Capacidad:**  Gestión de bibliotecas masivas (13,000+ activos) con rendimiento nativo.
* **Lógica de Datos:**  Emplea  **Lógica AND**  sobre metadatos  **EXIF**  (lente, ISO, cámara) para automatizar el movimiento y clasificación de archivos a carpetas de "Nivel".
* **Soberanía:** FileGrove ejecuta operaciones de activos localmente y sin telemetría propia. El producto web conserva una política separada de despliegue, privacidad y proveedores.

##### Escalabilidad "Sin GPU Obligatoria"

Companion Studio utiliza un **Router de Proveedores**. Redirigimos la inferencia pesada a modelos de frontera (Flux, Kling, Veo) mediante APIs, permitiendo desarrollar en hardware estándar (como tu RX 550\) sin sacrificar salidas 8K o video premium.

#### 3\. Ingeniería de Interacción: Adaptación Semántica de Prompt

##### Terminología y Protocolo de Compatibilidad

Queda fuera del lenguaje canónico cualquier formulación de evasión de controles. Aplicamos **Adaptación Semántica de Prompt** y **Compatibilidad de Proveedores** para preservar la intención estética dentro de las capacidades y políticas vigentes de cada proveedor.

##### El Esquizopeña Engine: "The Dinner of Chaos"

Este motor se basa en el choque cultural: la irrupción de la autenticidad cruda de Fernando Peña en el living aristocrático de Mirtha Legrand.

* **Abstracción Estética:** describimos forma, material, época, composición y tensión visual con lenguaje de dirección de arte, sin convertir la reformulación en un mecanismo de evasión de políticas.
* **Tensión Visual:**  Forzamos el impacto mediante el contraste de alta costura con el underground de los 90\.
* **Dirección de Actitud:** etiquetas como *defiant gaze*, mirada fija a cámara y ruptura de cuarta pared orientan la pose hacia una actitud menos genérica y más editorial.

##### Orquestación de "Realismo Sucio"

Para matar el "AI plastic look" (esa estética de muñeca lisa de las IAs comerciales), inyectamos textura analógica obligatoria:

* raw direct flash look: Fotografía de guerrilla inmediata.
* grain and film texture: Imperfecciones orgánicas y poros reales.
* 35mm photography: Óptica cinematográfica con profundidad de campo técnica.

#### 4\. El Canon Visual V2: Anclas Visuales y DNA

##### DNA Anchor: La Plisada Amarilla

El rasgo físico y de vestuario es un  **Hard Constraint** . La  **pollera plisada amarilla (Yellow Plaid Skirt)**  es el ancla visual principal. Sin ella, la identidad V2 se diluye.

* **Rasgos Faciales:**  Identidad adulta ficticia, cabello oscuro largo y ondulado, mirada magnética locked.
* **Look Firma:**  Plisada amarilla \+ corset negro \+ hebillas/herrajes de cuero \+ medias de red.

##### Variante Narrativa: V2 Operator (Companion Studio HQ)

Subidentidad profesional vinculada al entorno  **CS-ENV-HQ-001** .

* **Contexto:**  Sentada en workstation premium, anteojos finos, energía de Directora Visual.
* **Ambiente:**  Setup oscuro, iluminación violeta/magenta, monitor con interfaz SPECT.

##### Matriz de Selección Hero Assets (Rank Tiers)

Estos cinco activos son los pilares de la consistencia. Cualquier render debe compararse contra este Top 5:| Rank | ID | Rol | Notas || \------ | \------ | \------ | \------ || **A1** | **IMG\_042** | Hero Cover | Máxima identidad; actitud alt-punk definitiva. || **A2** | **IMG\_027** | Narrative | Escena del elevador; pulido premium y luz editorial. || **A3** | **IMG\_019** | Energy | Iluminación púrpura; icónica y vibrante. || **A4** | **IMG\_057** | Sensual | Smoky black mesh; editorial de alta gama. || **A5** | **IMG\_074** | Atmosphere | Rooftop rear-view; silueta urbana y atmósfera. |

#### 5\. Gestión del Sistema Audiovisual y Niveles de Contenido

##### Clasificación por Niveles de Impacto

Nivel,Denominación,Descripción
0,Presencia,"Contenido cotidiano, luz natural, selfies. Genera cercanía humana."
1,Proximidad,"Atuendos alternativos (Plisada Amarilla), encuadres cerrados, actitud de confianza."
2,Escenarios Privados,"Estéticas de nicho, entornos cerrados, alta retención emocional (V2 Operator)."

##### Pipeline de Refinamiento Secuencial (Agnóstico)

No pedimos todo a una herramienta. Encadenamos para ganar.| Paso | Denominación | Acción Técnica || \------ | \------ | \------ || 1 | **Structure Pass** | Definición de pose, composición y outfit (plisada amarilla). || 2 | **Realism Pass** | Mejora de volumen, piel y materiales. || 3 | **Imperfection Pass** | Inyección de poros y textura; eliminación del look plástico. || 4 | **Identity Lock** | Bloqueo estricto de rasgos V2, iris y proporciones. || 5 | **Color Pass** | Grading final e integración con la paleta SPECT (Violeta/Magenta/Negro). |

#### 6\. Lógica de Memoria y Capacidades de Agente

##### El Motor de Memoria Tripartito

La IA procesa la información en tres capas para evitar el olvido y la inconsistencia:

1. **Memoria Episódica:**  Registro de eventos y charlas recientes (el "ayer").
2. **Memoria de Identidad:**  El núcleo del personaje (quién es ella y qué le gusta).
3. **Memoria Relacional:**  El vínculo con el usuario (qué sabe de vos).**Lógica de Datos:**  El sistema diferencia entre  **Hechos**  (datos provistos por el usuario) e  **Inferencias**  (conclusiones que la IA saca). Todo cambio es "visible, auditable y reversible".

##### Funciones del Agente Creativo

* **Asset Librarian:**  Clasificación automática en FileGrove basada en metadatos.
* **Prompt Master:**  Generación de instrucciones maestras basadas en Hero Assets para nuevas sesiones.
* **Continuity Director:**  Vigilancia automática de iris, accesorios y herrajes para evitar la deriva.

#### 7\. Protocolos de Seguridad y Legado Técnico

##### Soberanía y Blindaje

* **Soberanía de Datos:** los activos privados y originales permanecen fuera del repositorio público; el almacenamiento local y remoto se decide por sensibilidad, costo, disponibilidad y política de proveedor.
* **FileGrove Hard Cap:**  Límite estricto de escaneo de  **100,000 archivos**  para evitar el congelamiento de sistemas de archivos.
* **Prevención de Bucles:**  Los scripts de automatización tienen una huella digital (Ledger Check) para evitar ejecuciones repetidas e infinitas.

##### Mantenimiento del ADN Visual

Cualquier cambio en la arquitectura o en el canon debe ser documentado como un "salto cuántico". El legado SPECT reside en que la identidad de la compañera sea una pieza de ingeniería blindada contra el olvido. **Regla de legado:** mantené el código limpio, la arquitectura verificable y la visión visual coherente.
**"Caótica en personaje. Coherente en memoria. Premium en imagen."**
