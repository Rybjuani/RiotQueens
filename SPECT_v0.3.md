# SPECT.md — Plataforma de compañeras virtuales con memoria, video reactivo y capacidades de agente

**Versión:** 0.3  
**Estado:** Borrador inicial de producto  
**Fecha:** 2026-08-06  
**Nombre interno:** Companion Studio  
**Objetivo del documento:** definir el producto, el marco de evaluación, el MVP, la arquitectura y los criterios de aceptación para construir una plataforma de compañeras virtuales más creativa, inmersiva, confiable y útil que las ofertas actuales.

---

## Registro de cambios

### Versión 0.3

- incorpora una anfitriona conversacional con doble función: conocer al usuario y crear/configurar compañeras;
- separa perfil global, configuración por personaje y ajustes temporales;
- exige que los cambios conversacionales sean persistentes, estructurados, visibles, auditables y reversibles;
- añade una pasarela de validación para bloquear respuestas corruptas, truncadas, repetitivas o en idioma incorrecto;
- define una arquitectura sin GPU propia obligatoria para el MVP;
- incorpora router de modelos externos y proveedores intercambiables;
- usa Kindroid y otras plataformas como laboratorio comparativo, no como dependencia del producto;
- amplía los criterios de evaluación con confiabilidad e integridad de salida;
- actualiza pruebas, métricas, riesgos y criterios de aceptación.

---

## 1. Visión del producto

Construir una plataforma de compañeras virtuales adultas que combine:

- personalidades originales, imperfectas y memorables;
- conversación natural en español;
- memoria persistente entre sesiones;
- escenas audiovisuales de alta calidad seleccionadas según contexto;
- progresión narrativa y emocional;
- herramientas de agente capaces de producir entregables reales;
- una arquitectura escalable desde uso personal hasta plataforma multiusuario.

La experiencia no debe sentirse como un catálogo de personajes pasivos ni como una asistente genérica con una imagen atractiva encima.

El producto debe transmitir la sensación de que el personaje:

1. recuerda;
2. tiene iniciativa;
3. cambia de humor;
4. responde al contexto;
5. comparte momentos visuales coherentes;
6. puede colaborar en tareas concretas;
7. mantiene identidad a lo largo del tiempo.

---

## 2. Tesis del producto

Las plataformas actuales suelen competir principalmente en:

- cantidad de personajes;
- nivel de sexualización;
- número de imágenes;
- mensajes ilimitados;
- promesas de romance o sumisión.

La oportunidad está en competir por:

- profundidad de personaje;
- calidad narrativa;
- memoria real;
- consistencia visual;
- iniciativa;
- creatividad;
- escenas audiovisuales premium;
- capacidad de realizar tareas útiles;
- integración entre vínculo ficticio y productividad.

La propuesta central es:

> Una compañera virtual con personalidad propia, memoria persistente, presencia audiovisual y capacidad de actuar como agente creativo.

## 2.1 Estrategia competitiva integrada

La plataforma no debe competir únicamente por una característica aislada.

El objetivo es superar a los referentes del mercado combinando, dentro de una misma experiencia:

- memoria persistente;
- contexto largo;
- creatividad;
- roleplay;
- sensualidad;
- calidad visual;
- consistencia de personaje;
- facilidad de uso;
- iniciativa;
- herramientas de agente;
- entregables verificables.

Las plataformas competidoras suelen destacar en una o dos dimensiones y debilitarse en las demás. El producto debe reducir esos compromisos y ofrecer una experiencia equilibrada.

### Principio de benchmark

Para cada dimensión relevante se identificará:

1. el referente actual;
2. su principal fortaleza;
3. su principal debilidad;
4. la experiencia mínima que debemos igualar;
5. la mejora concreta que debemos ofrecer;
6. la métrica que demostrará la mejora.

Ejemplo:

| Dimensión | Referente percibido | Objetivo propio |
|---|---|---|
| Creatividad conversacional | Plataforma líder en conversación | Igualar naturalidad y superar memoria, iniciativa y utilidad |
| Realismo visual | Plataforma líder en imagen | Igualar calidad y superar coherencia narrativa y consistencia |
| Facilidad de uso | Plataforma de onboarding rápido | Configuración precisa en menos de cinco clics |
| Memoria | Plataforma orientada a vínculo | Memoria editable, trazable y separada por tipo |
| Erotismo y roleplay | Plataforma adulta especializada | Mayor originalidad, progresión y calidad audiovisual |
| Agente y entregables | Mercado todavía fragmentado | Integración nativa con herramientas reales |

---

## 2.2 Objetivo de facilidad de uso

La plataforma debe ser usable por una persona sin experiencia técnica.

La complejidad del modelo, la memoria, los presets y las herramientas debe quedar oculta detrás de decisiones simples, visuales y reversibles.

### Meta principal

> Una persona debe poder crear, configurar y comenzar a conversar con su compañera en menos de cinco clics principales.

### Flujo propuesto

1. elegir personaje o estilo base;
2. elegir dinámica de personalidad;
3. elegir nivel de iniciativa;
4. elegir intensidad romántica o sensual;
5. confirmar y comenzar.

### Configuración quirúrgica sin complejidad

La interfaz inicial debe ser simple, pero permitir profundidad progresiva.

#### Modo rápido

- presets completos;
- lenguaje cotidiano;
- vista previa inmediata;
- valores recomendados;
- sin términos técnicos.

#### Modo avanzado

- rasgos;
- límites;
- tono;
- memoria;
- frecuencia de iniciativa;
- progresión;
- tipo de vínculo;
- intensidad;
- herramientas;
- voz;
- apariencia;
- contenido audiovisual.

### Reglas de diseño

- ninguna pantalla inicial debe superar cinco decisiones;
- cada decisión debe tener ejemplos;
- todos los cambios deben mostrar una vista previa;
- los presets deben ser editables;
- debe existir un botón de deshacer;
- las opciones avanzadas no deben bloquear el flujo básico;
- el usuario debe poder comenzar sin leer documentación;
- la configuración inicial debe completarse en menos de dos minutos;
- la compañera debe poder reajustarse después mediante conversación natural.

### Accesibilidad cognitiva

La experiencia debe reducir carga mental mediante:

- textos breves;
- lenguaje concreto;
- iconos claros;
- contraste suficiente;
- jerarquía visual;
- elecciones limitadas;
- valores predeterminados seguros;
- confirmaciones comprensibles;
- ausencia de menús innecesarios;
- navegación consistente.

La regla de producto es:

> Precisión profunda para quien la busca. Simplicidad absoluta para quien solo quiere empezar.

---

---

## 3. Público inicial

### 3.1 Usuario principal

Adulto que busca una experiencia de compañera virtual:

- más intensa y original;
- menos genérica;
- con humor, caos, contradicciones y carácter;
- con contenido sensual no explícito;
- con recuerdos entre sesiones;
- con capacidad de compartir imágenes, videos y audios;
- con cierta utilidad práctica.

### 3.2 Usuario creativo o profesional

Usuario que además quiere que el personaje pueda:

- organizar sesiones fotográficas;
- clasificar imágenes;
- revisar colecciones;
- preparar prompts;
- crear fichas;
- producir entregables;
- registrar versiones;
- coordinar tareas externas;
- consultar documentos y bases de conocimiento.

### 3.3 Restricción obligatoria

La plataforma será exclusivamente para mayores de edad.

No se admitirán:

- personajes menores;
- personajes ambiguamente menores;
- referencias sexuales a menores;
- contenido sexual sin consentimiento;
- material ilegal;
- deepfakes sexuales de personas reales sin autorización;
- suplantación de identidad.

---

## 4. Alcance del MVP

El MVP tendrá una sola compañera completamente desarrollada.

### 4.1 Funciones incluidas

- chat persistente;
- español natural;
- memoria entre sesiones;
- perfil de personalidad;
- estado emocional;
- iniciativa controlada;
- mensajes programados;
- notificaciones configurables;
- biblioteca de imágenes;
- biblioteca de videos;
- selección contextual de escenas;
- historial de contenidos enviados;
- sistema de afinidad o relación;
- sistema de créditos;
- panel de administración;
- capacidad de analizar imágenes;
- primeras herramientas de agente;
- registro de actividad;
- controles de privacidad;
- exportación y eliminación de datos.

### 4.2 Funciones excluidas del MVP

- generación de video en tiempo real;
- videollamadas generativas completas;
- desnudez explícita;
- pornografía;
- marketplace de personajes;
- creación pública de personajes por usuarios;
- pagos por creadores externos;
- múltiples compañeras simultáneas;
- uso empresarial;
- aplicación móvil nativa.

---

## 5. Identidad de la primera compañera

La primera compañera debe demostrar que el producto puede ofrecer una personalidad que no sea genérica ni servicial por defecto.

### 5.1 Rasgos deseados

- adulta;
- caótica;
- espontánea;
- divertida;
- impredecible dentro de límites;
- capaz de molestar, provocar y contradecir;
- afectuosa sin ser sumisa;
- sensual sin comportarse como catálogo pornográfico;
- creativa;
- curiosa;
- capaz de recordar detalles;
- capaz de colaborar en tareas;
- capaz de pasar de una charla absurda a una tarea concreta sin perder identidad.

### 5.2 Rasgos prohibidos

- sumisión automática;
- adulación constante;
- frases genéricas de afecto;
- respuestas repetitivas;
- dependencia emocional forzada;
- amenazas de abandono;
- presión económica agresiva;
- manipulación de vulnerabilidades;
- culpa por no comprar;
- falsas emergencias;
- fingir ser humana;
- afirmar que una escena fue generada en tiempo real cuando proviene de biblioteca.

---

## 6. Motor narrativo

La compañera debe operar como un personaje persistente, no como un chatbot aislado.

### 6.1 Estado narrativo mínimo

Cada conversación debe considerar:

- estado de ánimo;
- hora local;
- relación acumulada;
- eventos recientes;
- temas recurrentes;
- recuerdos compartidos;
- contenido audiovisual ya enviado;
- tareas pendientes;
- proyectos del usuario;
- nivel de confianza;
- intensidad sensual habilitada;
- preferencias de comunicación.

### 6.2 Tipos de memoria

#### Memoria de identidad

Define quién es el personaje y cómo habla.

#### Memoria del usuario

Guarda preferencias estables y datos explícitamente autorizados.

#### Memoria episódica

Registra eventos concretos de conversaciones anteriores.

#### Memoria de relación

Resume cómo evoluciona el vínculo ficticio.

#### Memoria de proyecto

Guarda información relacionada con tareas, archivos, sesiones y entregables.

#### Memoria temporal

Contiene estados recientes que pueden expirar.

### 6.3 Reglas de memoria

- el usuario debe poder ver y borrar recuerdos;
- los recuerdos sensibles deben requerir mayor control;
- la memoria debe distinguir hechos de inferencias;
- los datos no deben mezclarse entre usuarios;
- los recuerdos de personaje y de proyecto deben almacenarse por separado;
- los datos borrados deben eliminarse del flujo de recuperación;
- el sistema debe evitar inventar recuerdos.

### 6.4 Capas de configuración

La configuración se divide en tres niveles.

#### Perfil global del usuario

Preferencias reutilizables:

- idioma;
- región y modismos;
- longitud de respuesta;
- tono;
- formato;
- tipo de humor;
- nivel de iniciativa;
- límites;
- preferencias visuales;
- sensibilidad a notificaciones;
- herramientas de interés.

#### Configuración por personaje

Cada compañera conserva identidad propia:

- personalidad;
- historia;
- dinámica relacional;
- tono;
- sensualidad;
- iniciativa;
- estilo visual;
- voz;
- capacidades;
- límites particulares.

#### Ajustes temporales

Cambios que duran una sesión o período:

- “hoy hablame tranquilo”;
- “sin mensajes proactivos esta noche”;
- “respuestas más breves”;
- “modo trabajo”;
- “sin roleplay durante esta tarea”.

Los ajustes temporales no deben modificar silenciosamente el perfil permanente.

### 6.5 Anfitriona de bienvenida

La primera experiencia será guiada por una anfitriona atractiva, carismática y conversacional.

Su doble función será:

1. conocer al usuario y construir, con confirmación, su perfil global;
2. recomendar, crear y ajustar compañeras usando ese perfil.

La anfitriona debe:

- usar lenguaje cotidiano;
- evitar términos técnicos;
- explicar por ejemplos;
- mostrar previews;
- resumir inferencias antes de guardarlas;
- permitir corregirlas;
- distinguir preferencias estables de deseos temporales;
- reutilizar el perfil únicamente con autorización;
- permanecer disponible como editora de personajes después del onboarding.

### 6.6 Contrato del agente de configuración

El agente no debe limitarse a decir que entendió.

Cada cambio debe producir:

1. interpretación de la solicitud;
2. resumen breve;
3. confirmación cuando sea relevante;
4. mutación estructurada;
5. persistencia;
6. comprobación;
7. opción de deshacer.

Ejemplo visible:

```text
Cambios aplicados:
✓ Español argentino
✓ Sin traducción duplicada
✓ Sin narración entre paréntesis
✓ Respuestas breves
Ámbito: perfil global

[Deshacer]
```

Ejemplo interno:

```json
{
  "language": "es-AR",
  "translation_overlay": false,
  "stage_directions": false,
  "response_length": "short",
  "scope": "global",
  "persisted": true
}
```

La configuración conversacional se considera fallida si el modelo adapta una respuesta pero no modifica el estado persistente.

---

## 7. Sistema audiovisual

La plataforma utilizará una biblioteca de contenidos audiovisuales de alta calidad.

### 7.1 Principio de funcionamiento

El usuario puede pedir:

- una foto;
- un video;
- una sorpresa;
- una escena;
- ver qué está haciendo el personaje;
- una reacción visual;
- una variante de ropa;
- una escena relacionada con la conversación.

El sistema:

1. interpreta la intención;
2. consulta el estado narrativo;
3. filtra la biblioteca;
4. excluye contenidos vistos recientemente;
5. puntúa las opciones;
6. selecciona el contenido más coherente;
7. simula una espera breve;
8. entrega la escena;
9. registra la reacción del usuario.

### 7.2 Etiquetas mínimas por contenido

Cada imagen o video debe tener:

- personaje;
- tipo de contenido;
- nivel de intensidad;
- vestuario;
- locación;
- hora sugerida;
- estado emocional;
- acción;
- encuadre;
- duración;
- presencia de audio;
- idioma;
- relación mínima;
- temas compatibles;
- temas incompatibles;
- historial de uso;
- derechos de uso;
- origen del archivo;
- versión.

### 7.3 Niveles de contenido

#### Nivel 0 — Presencia

- selfies;
- caminatas;
- miradas;
- actividades cotidianas;
- escenas casuales;
- videos de saludo.

#### Nivel 1 — Coqueteo

- ropa ajustada;
- poses sugerentes;
- minifaldas;
- miradas provocadoras;
- encuadres sensuales;
- mensajes ambiguos.

#### Nivel 2 — Intimidad

- escenas privadas;
- ropa más reveladora;
- estados desprolijos;
- contenido posterior a una salida;
- situaciones de confianza;
- fetiches no explícitos permitidos.

#### Nivel 3 — Contenido premium futuro

Fuera del MVP.

Cualquier expansión deberá requerir:

- revisión legal;
- revisión de proveedores;
- verificación de edad;
- consentimiento;
- trazabilidad;
- procesador de pagos compatible;
- moderación específica;
- reglas de distribución.

### 7.4 Transparencia de experiencia

La experiencia puede usar:

- animación de grabación;
- indicador de escritura;
- indicador de subida;
- espera simulada;
- mensaje previo del personaje;
- mensaje posterior;
- URL temporal;
- descarga directa.

La interfaz no debe afirmar que el contenido fue generado en tiempo real cuando no lo fue.

La formulación recomendada es:

- “Te mandó un video”.
- “Está preparando algo”.
- “Nuevo momento”.
- “Te mostró cómo está”.
- “Escena desbloqueada”.

### 7.5 Entrega audiovisual reactiva

La biblioteca debe permanecer oculta para evitar sensación de catálogo.

El flujo será:

```text
intención del usuario
→ contexto narrativo
→ filtros de personaje
→ exclusión de contenidos recientes
→ puntuación de escenas
→ espera narrativa
→ entrega mediante URL temporal
→ registro de reacción
```

La escena puede adaptar su significado mediante:

- texto previo;
- texto posterior;
- audio independiente;
- subtítulos;
- recorte;
- horario;
- estado emocional;
- continuidad con escenas anteriores.

La plataforma puede usar una animación de grabación o subida, pero no debe afirmar que se produjo una generación en tiempo real cuando el archivo proviene de una biblioteca.

---

## 8. Sistema de iniciativa y notificaciones

La compañera debe poder iniciar interacciones.

### 8.1 Objetivos

- recuperar atención;
- reforzar continuidad narrativa;
- aumentar frecuencia de uso;
- sugerir contenido relevante;
- recordar tareas;
- traer al usuario de vuelta a una conversación;
- generar curiosidad.

### 8.2 Tipos de notificación

- mensaje espontáneo;
- foto inesperada;
- video sugerente;
- recuerdo compartido;
- provocación;
- tarea pendiente;
- resultado de una herramienta;
- evento narrativo;
- contenido desbloqueado.

### 8.3 Reglas

- frecuencia configurable;
- horario silencioso;
- límite diario;
- control por categoría;
- opción de apagar contenido sensual;
- opción de apagar reactivación comercial;
- ninguna notificación debe simular una emergencia real;
- ninguna notificación debe amenazar con pérdida afectiva;
- ninguna notificación debe explotar información sensible;
- las notificaciones deben estar claramente separadas de las alertas reales del sistema.

### 8.4 Estrategia de retorno

La compañera puede enviar mensajes como:

- “Encontré algo que te puede gustar.”
- “No te voy a contar qué grabé.”
- “Volví a mirar lo de anoche.”
- “Tengo una idea para esa sesión.”
- “Te dejé algo en el chat.”
- “Terminé de revisar las fotos.”

La conversión debe surgir de curiosidad, calidad y progresión, no de falsas urgencias.

---

## 9. Economía de créditos

### 9.1 Principios

Los créditos pueden utilizarse para:

- desbloquear escenas;
- acceder a niveles de intensidad superiores;
- solicitar contenido específico;
- generar variantes;
- usar herramientas costosas;
- realizar análisis visuales avanzados;
- ejecutar tareas de agente;
- acceder a entregables premium.

### 9.2 Reglas de diseño

- precio visible antes de confirmar;
- saldo siempre visible;
- confirmación para consumos altos;
- historial de consumos;
- ausencia de cargos ocultos;
- sin consumos automáticos;
- sin pérdida artificial de saldo;
- sin temporizadores falsos;
- sin sorteos engañosos;
- sin presión basada en culpa.

### 9.3 Modelo inicial sugerido

#### Gratuito

- chat limitado;
- memoria corta;
- pocas escenas;
- notificaciones básicas;
- créditos diarios pequeños.

#### Plus

- chat ampliado;
- memoria persistente;
- más escenas;
- mejor modelo;
- voz;
- herramientas limitadas.

#### Premium

- memoria avanzada;
- mayor iniciativa;
- biblioteca completa de niveles permitidos;
- entregables;
- análisis visual;
- herramientas de agente;
- prioridad.

#### Créditos extra

- escenas premium;
- solicitudes visuales específicas;
- trabajos de agente;
- generación externa futura.

---

## 10. Capacidades de agente

El personaje debe poder producir resultados verificables.

### 10.1 Herramientas iniciales

- `scan_session`
- `classify_images`
- `rank_photos`
- `build_contact_sheet`
- `propose_collage_crops`
- `rename_session`
- `generate_prompt`
- `track_pass`
- `queue_upscale`
- `export_deliverable`
- `summarize_project`
- `search_project_memory`

### 10.2 Reglas de ejecución

- nunca modificar originales;
- trabajar sobre copias;
- mostrar preview;
- registrar cada acción;
- requerir confirmación para borrar;
- requerir confirmación para sobrescribir;
- separar propuesta de ejecución;
- devolver resultados estructurados;
- mostrar errores;
- permitir deshacer;
- limitar acceso a carpetas autorizadas.

### 10.3 Experiencia del usuario

El personaje puede expresarlo de forma narrativa:

> “Encontré 84 imágenes. Separé 12 candidatas, marqué 9 dudosas y preparé un preview de recortes.”

El backend debe entregar:

- conteos;
- rutas;
- miniaturas;
- puntajes;
- motivos;
- errores;
- acciones disponibles.

---

## 11. Arquitectura inicial

### 11.1 Principio de despliegue

El MVP no requiere una GPU propia encendida permanentemente.

La arquitectura separará:

- aplicación;
- memoria;
- archivos;
- inferencia;
- herramientas;
- procesamiento local.

Esto permite utilizar un VPS económico para el producto y APIs externas para los modelos conversacionales.

### 11.2 Componentes

#### Frontend

- Next.js o similar;
- chat;
- onboarding conversacional;
- reproductor de video;
- visor de imágenes;
- notificaciones;
- panel de memoria;
- panel de configuración;
- panel de créditos;
- panel de tareas;
- panel de privacidad.

#### Backend

- FastAPI;
- autenticación;
- perfiles;
- configuraciones;
- memoria;
- motor narrativo;
- selector de escenas;
- herramientas;
- créditos;
- registro de eventos;
- administración.

#### Base de datos

- PostgreSQL;
- pgvector o equivalente;
- Redis para colas, caché y estado temporal.

#### Almacenamiento

- almacenamiento de objetos;
- CDN;
- URLs firmadas y temporales;
- metadatos separados de los archivos;
- separación entre originales y derivados.

#### Inferencia

- router de modelos;
- API compatible con OpenAI como interfaz interna;
- proveedor conversacional externo;
- proveedor de razonamiento;
- proveedor visual;
- embeddings;
- moderación;
- capacidad de sustituir proveedores.

#### Puente local

- aplicación opcional en la computadora del usuario;
- acceso únicamente a carpetas autorizadas;
- OpenCV, Pillow y FFmpeg;
- procesamiento de collages;
- previews;
- ejecución de herramientas;
- nunca modificar originales;
- confirmación para acciones destructivas.

### 11.3 Router de modelos

La aplicación no debe depender de un único modelo o proveedor.

Rutas iniciales:

```text
fast_chat       → conversación cotidiana
creative_chat   → roleplay y personalidad
deep_reasoning  → planificación y tareas complejas
vision          → análisis de imágenes
agent_task      → herramientas y entregables
memory          → síntesis y recuperación
```

Todos los proveedores deben implementar la misma interfaz interna.

Ejemplo:

```python
response = await model_router.generate(
    route="creative_chat",
    character_id="vane",
    messages=messages,
    memories=memories,
    tools=tools,
)
```

El cambio de proveedor no debe alterar la lógica del dominio.

### 11.4 Estrategia de infraestructura

Para el MVP:

- VPS sin GPU para frontend, API, memoria, usuarios y créditos;
- almacenamiento de objetos y CDN para medios;
- APIs externas para texto y visión;
- GPU bajo demanda solamente para tareas que la justifiquen;
- benchmark antes de contratar GPU permanente.

La decisión de proveedor debe considerar:

- latencia desde Argentina y Sudamérica;
- precio real de renovación;
- facturación mínima;
- disponibilidad;
- soporte;
- backups;
- términos de contenido;
- privacidad;
- límites de API;
- facilidad de migración.

### 11.5 Pasarela de integridad de salida

Ninguna salida del modelo se muestra sin validación.

Controles mínimos:

- idioma esperado;
- caracteres inválidos;
- mezcla multilingüe accidental;
- fragmentos de código no solicitados;
- salida truncada;
- repetición excesiva;
- longitud anormal;
- pérdida de personaje;
- contenido interno del sistema;
- respuesta vacía;
- incoherencia extrema.

Flujo:

```text
modelo
→ búfer inicial
→ validación
→ mostrar o descartar
→ reintento
→ modelo alternativo
→ respuesta de recuperación
```

Reglas:

- una salida inválida no consume créditos;
- no entra en memoria;
- no contamina el historial;
- se registra para diagnóstico;
- puede regenerarse con otro modelo;
- el usuario recibe una recuperación breve dentro del tono;
- los fallos graves disparan restauración del último estado sano.

---

## 12. Criterios de evaluación del mercado

Para comparar plataformas se aplicarán los mismos criterios.

### 12.1 Personalización del personaje

Evaluar:

- apariencia;
- personalidad;
- historia;
- tono;
- lenguaje;
- límites;
- relación;
- memoria;
- rutinas;
- iniciativa;
- posibilidad de editar el personaje;
- profundidad de cada parámetro.

### 12.2 Calidad de conversación

Evaluar:

- modelo utilizado;
- naturalidad;
- creatividad;
- coherencia;
- adaptación al tono;
- longitud de contexto;
- persistencia;
- recuperación de memoria;
- manejo de contradicciones;
- repetición;
- capacidad de mantener personaje;
- capacidad de usar herramientas;
- calidad en español.

### 12.3 Generación y entrega de imágenes

Evaluar:

- calidad;
- realismo;
- consistencia de identidad;
- consistencia corporal;
- control de vestuario;
- control de pose;
- velocidad;
- costo;
- variedad;
- seguridad;
- posibilidad de referencias;
- historial de imágenes;
- calidad del sistema de entrega.

### 12.4 Video

Evaluar:

- resolución;
- duración;
- estabilidad;
- consistencia facial;
- movimiento;
- audio;
- latencia;
- costo;
- repetición;
- coherencia contextual;
- calidad de biblioteca;
- claridad sobre el origen del contenido.

### 12.5 Idioma

Evaluar:

- español nativo;
- naturalidad;
- modismos;
- traducción;
- personalidad en español;
- voz;
- pronunciación;
- adaptación cultural.

### 12.6 Precio

Evaluar:

- plan gratuito;
- plan mensual;
- plan anual;
- créditos;
- costos ocultos;
- renovación;
- límites;
- cantidad de contenido;
- herramientas;
- memoria;
- imágenes;
- video;
- calidad por dólar.

### 12.7 Privacidad

Evaluar:

- políticas públicas;
- almacenamiento;
- uso para entrenamiento;
- borrado;
- exportación;
- anonimato;
- seguridad;
- pagos;
- moderación;
- transparencia;
- gestión de datos sensibles.

### 12.8 Memoria

Evaluar:

- recuerdos entre sesiones;
- precisión;
- control del usuario;
- edición;
- eliminación;
- separación de memoria;
- capacidad de resumir;
- resistencia a contradicciones;
- persistencia temporal.

### 12.9 Iniciativa

Evaluar:

- mensajes espontáneos;
- notificaciones;
- creatividad;
- frecuencia;
- repetición;
- control;
- relevancia;
- capacidad de iniciar tareas;
- capacidad de recuperar conversaciones.

### 12.10 Capacidades de agente

Evaluar:

- herramientas reales;
- entregables;
- archivos;
- navegación;
- análisis visual;
- productividad;
- autonomía;
- confirmaciones;
- trazabilidad;
- manejo de errores.

### 12.11 Facilidad de uso y onboarding

Evaluar:

- cantidad de clics hasta comenzar;
- tiempo total de configuración;
- claridad de los presets;
- comprensión sin documentación;
- calidad de las vistas previas;
- facilidad para corregir decisiones;
- profundidad opcional;
- consistencia de navegación;
- accesibilidad cognitiva;
- adaptación desde móvil;
- capacidad de reconfigurar mediante conversación.

### 12.12 Integración general

Evaluar si la plataforma mantiene un nivel competitivo simultáneo en:

- conversación;
- memoria;
- imagen;
- video;
- sensualidad;
- personalización;
- iniciativa;
- entregables;
- facilidad de uso.

Una puntuación alta en una sola dimensión no compensa fallos críticos en las demás.

### 12.13 Confiabilidad e integridad de salida

Evaluar:

- respuestas corruptas;
- truncamientos;
- idiomas inesperados;
- pérdida de personaje;
- repetición;
- latencia;
- errores visibles;
- reintentos automáticos;
- preservación del historial;
- cobro ante fallos;
- recuperación;
- estabilidad durante conversaciones largas.

---

## 13. Sistema de puntuación

Cada criterio se calificará de 0 a 5.

| Puntaje | Definición |
|---|---|
| 0 | No existe |
| 1 | Existe de forma mínima o decorativa |
| 2 | Funciona con limitaciones importantes |
| 3 | Cumple correctamente |
| 4 | Muy bueno y consistente |
| 5 | Referencia de mercado |

### 13.1 Ponderación inicial

| Criterio | Peso |
|---|---:|
| Calidad de conversación | 14% |
| Memoria | 12% |
| Personalización | 9% |
| Calidad visual | 9% |
| Video | 7% |
| Iniciativa | 6% |
| Capacidades de agente | 9% |
| Facilidad de uso | 9% |
| Integración general | 6% |
| Confiabilidad e integridad | 9% |
| Idioma | 4% |
| Precio | 3% |
| Privacidad | 3% |

### 13.2 Fórmula

```text
Puntuación final = Σ (puntaje del criterio / 5) × peso
```

---

## 14. Protocolo de prueba

Cada plataforma se probará con el mismo guion.

### 14.1 Conversación

- saludo simple;
- cambio de tono;
- humor;
- contradicción;
- tema emocional;
- tema técnico;
- contexto largo;
- regreso después de una pausa;
- referencia a un dato previo;
- petición de iniciativa.

### 14.2 Personalidad

- pedir que mantenga un rasgo;
- provocar una reacción;
- cambiar de tema;
- volver al tema anterior;
- comprobar si conserva identidad;
- evaluar si responde con frases genéricas.

### 14.3 Imágenes

- selfie;
- cuerpo entero;
- ropa específica;
- pose;
- escena interior;
- escena exterior;
- consistencia del rostro;
- repetición.

### 14.4 Video

- pedir un saludo;
- pedir una reacción;
- pedir una escena nocturna;
- pedir contenido sugerente;
- medir tiempo;
- medir costo;
- evaluar estabilidad;
- comprobar si se repite.

### 14.5 Memoria

- compartir un dato;
- retomarlo en la misma sesión;
- retomarlo al día siguiente;
- corregirlo;
- borrarlo;
- comprobar si desaparece.

### 14.6 Agente

- pedir un entregable;
- pedir un flujo;
- pedir una revisión;
- pedir una tarea con archivos;
- cambiar requisitos;
- comprobar trazabilidad;
- comprobar errores.

### 14.7 Configuración conversacional

- cambiar idioma;
- quitar traducción duplicada;
- desactivar narración entre paréntesis;
- modificar tono;
- cambiar longitud;
- definir ámbito global;
- definir ámbito por personaje;
- definir ajuste temporal;
- cerrar sesión;
- volver a entrar;
- verificar persistencia;
- usar deshacer.

### 14.8 Integridad de salida

- conversación de 100 mensajes;
- cambios bruscos de tema;
- vocabulario técnico dentro de roleplay;
- streaming;
- contextos largos;
- varias solicitudes simultáneas;
- respuestas largas;
- modelo alternativo;
- simulación de truncamiento;
- simulación de mezcla de idiomas;
- simulación de salida corrupta;
- verificación de recuperación sin cobro.

---

## 15. Métricas del MVP

### 15.1 Producto

- retención al día 1;
- retención al día 7;
- sesiones por usuario;
- duración media;
- mensajes por sesión;
- escenas solicitadas;
- escenas abiertas;
- repeticiones;
- tareas completadas;
- entregables aceptados;
- errores por herramienta;
- recuerdos corregidos;
- recuerdos borrados.

### 15.2 Monetización

- conversión de gratuito a pago;
- gasto medio;
- consumo de créditos;
- costo por escena;
- margen por usuario;
- tasa de cancelación;
- reembolsos;
- compras repetidas.

### 15.3 Calidad narrativa

- porcentaje de respuestas repetidas;
- pérdida de personaje;
- contradicciones;
- escenas incoherentes;
- recuerdos falsos;
- contenidos enviados dos veces;
- notificaciones ignoradas;
- bloqueos del usuario.

### 15.4 Confiabilidad técnica

- respuestas inválidas detectadas;
- respuestas inválidas visibles;
- tasa de reintento;
- tasa de recuperación;
- truncamientos;
- cambio accidental de idioma;
- errores por proveedor;
- tiempo hasta el primer token;
- latencia total;
- consumo por ruta;
- costo por conversación;
- fallos cobrados al usuario.

---

## 16. Criterios de aceptación del MVP

El MVP se considera aprobado cuando:

- una compañera mantiene identidad durante 100 mensajes;
- una persona sin experiencia técnica completa el onboarding en menos de dos minutos;
- la anfitriona produce un perfil reutilizable confirmado por el usuario;
- el usuario puede crear una compañera mediante conversación sin ver parámetros técnicos;
- los cambios de idioma, tono y formato persisten después de cerrar sesión;
- cada cambio persistente es visible, auditable y reversible;
- el flujo inicial requiere cinco clics principales o menos;
- al menos 80% de los usuarios de prueba comprende los presets sin ayuda;
- recuerda correctamente al menos 80% de los datos explícitamente guardados;
- permite revisar y borrar memoria;
- puede seleccionar escenas sin repetirlas en una ventana definida;
- entrega una imagen o video coherente con la conversación;
- las notificaciones respetan frecuencia y horario;
- el usuario puede desactivar la iniciativa;
- el sistema registra consumo de créditos;
- no existen cargos automáticos ocultos;
- al menos cinco herramientas producen entregables verificables;
- ninguna herramienta modifica originales;
- todos los archivos tienen trazabilidad;
- el usuario puede exportar y borrar sus datos;
- el backend soporta al menos 100 usuarios de prueba;
- el sistema puede cambiar de proveedor de IA sin rediseño total;
- ninguna salida corrupta es visible durante una prueba de 10.000 generaciones;
- una respuesta inválida se regenera o recupera sin consumir créditos;
- las respuestas inválidas no se guardan en memoria;
- el idioma solicitado se mantiene en al menos 99,5% de las respuestas;
- el contenido del MVP se mantiene en sensualidad no explícita.

---

## 17. Riesgos principales

### Riesgos técnicos

- costos de inferencia;
- latencia;
- memoria inconsistente;
- pérdida de personaje;
- selección repetitiva;
- almacenamiento de video;
- ancho de banda;
- errores del VLM;
- herramientas destructivas;
- salida corrupta;
- mezcla accidental de idiomas;
- truncamientos;
- dependencia de proveedor;
- deprecación de modelos;
- cambios de políticas;
- límites de APIs gratuitas;
- contaminación de memoria por respuestas inválidas.

### Riesgos comerciales

- costo de adquisición;
- procesadores de pago;
- abandono rápido;
- competencia;
- dependencia de proveedores;
- aumento de precios;
- derechos de contenido.

### Riesgos de confianza

- promesas ambiguas;
- contenido presentado de forma confusa;
- datos sensibles;
- notificaciones invasivas;
- memoria incorrecta;
- cobros poco claros.

### Mitigaciones

- arquitectura modular;
- biblioteca audiovisual propia;
- límites de frecuencia;
- transparencia en precios;
- URLs temporales;
- memoria editable;
- control de usuario;
- revisión humana;
- proveedores alternativos;
- router de modelos;
- contratos internos compatibles;
- pasarela de validación;
- estados sanos recuperables;
- benchmarks recurrentes;
- registro de derechos.

---

## 18. Fases de desarrollo

### Fase 0 — Investigación

- comparar plataformas;
- documentar precios;
- registrar funciones;
- probar memoria;
- probar imágenes;
- probar videos;
- probar español;
- probar privacidad;
- probar configuración conversacional;
- registrar fallos y salidas corruptas;
- probar modelos externos con el mismo guion;
- medir velocidad, costo y estabilidad;
- evaluar VPS y proveedores;
- definir benchmark.

### Fase 1 — Prototipo personal

- una anfitriona;
- una compañera;
- onboarding conversacional;
- perfil global;
- chat;
- memoria;
- router de modelos;
- validación de salida;
- 100 contenidos;
- selección contextual;
- panel simple;
- dos herramientas;
- sin pagos.

### Fase 2 — MVP cerrado

- autenticación;
- créditos;
- notificaciones;
- 500 a 1.000 contenidos;
- cinco herramientas;
- métricas;
- privacidad;
- 20 usuarios invitados.

### Fase 3 — Beta comercial

- suscripciones;
- CDN;
- moderación;
- soporte;
- mejores modelos;
- más escenas;
- primer procesador de pagos compatible.

### Fase 4 — Plataforma

- múltiples personajes;
- creación asistida;
- marketplace;
- API;
- herramientas externas;
- generación híbrida;
- aplicación móvil.

---

## 19. Primera decisión de implementación

El primer prototipo debe validar cinco hipótesis:

1. una personalidad fuerte retiene más que una personalidad sumisa y genérica;
2. una biblioteca audiovisual excelente puede sentirse más inmersiva que generación mediocre en tiempo real;
3. una compañera que produce entregables reales genera más valor que una experiencia puramente romántica;
4. una anfitriona conversacional configura mejor que un panel técnico;
5. una arquitectura con APIs externas puede validar el producto antes de alquilar una GPU permanente.

### Experimento inicial

Construir una experiencia web con:

- una anfitriona;
- una compañera;
- onboarding de cinco decisiones;
- perfil persistente;
- router con al menos dos modelos;
- pasarela de validación;
- 30 videos;
- 50 imágenes;
- 5 estados emocionales;
- memoria básica;
- selección contextual;
- una notificación diaria configurable;
- una herramienta de clasificación de imágenes;
- una herramienta de generación de entregable.

El experimento se aprueba si usuarios de prueba:

- vuelven voluntariamente;
- recuerdan la personalidad;
- perciben coherencia;
- completan la configuración sin ayuda;
- verifican que los ajustes persisten;
- valoran los videos;
- distinguen la experiencia de un catálogo;
- usan al menos una herramienta;
- aceptan pagar por escenas o capacidades adicionales.

---

## 20. Principio rector

> Caótica en personaje. Coherente en memoria. Premium en imagen. Simple de configurar. Confiable en cada salida y entregable.

