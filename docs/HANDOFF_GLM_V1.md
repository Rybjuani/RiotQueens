# HANDOFF — GLM V1 Integration

**Branch:** `integration/glm-v1`
**Base:** `chore/bootstrap-architecture` (`9b635b3`)
**Date:** 2026-08-07
**Issue:** [#1 — GLM v1 integration: port cyber-noir prototype into canonical monorepo](https://github.com/Rybjuani/Companion-Studio/issues/1)

## Resumen

Se portó el sistema visual cyber-noir del prototipo `companion-studio-app` (commit `783d40f`) al monorepo canónico `apps/web`, respetando SPECT v0.3, la arquitectura FastAPI existente, y las reglas de transparencia de producto del Issue #1.

## Qué se migró desde companion-studio-app

- **Sistema visual cyber-noir**: paleta deep noir black (`#0a0a0f`) + electric violet (`#785CFF`) + hot magenta (`#FF4D9D`) + amber accent. Glassmorphism, neon glow, starfield, gradient-text shimmer. Portado a **plain CSS** (sin Tailwind) para mantener dependencias mínimas.
- **Jerarquía de componentes**: Navbar (glass sticky), Hero (starfield + retrato flotante + CTA), Onboarding (5 decisiones per SPECT §2.2), ChatPanel (burbujas con accent rim, typing indicator, quick prompts), Capabilities (honest labels), Footer (glass + adult note).
- **Reproductor showcase / NaturalistaSeries**: NO migrados (requiren assets privados del owner; el branch canónico usa solo placeholders sintéticos).
- **Framer Motion**: NO migrado (reemplazado por animaciones CSS puras para evitar dependencia).
- **Tailwind / shadcn/ui**: NO migrados (el apps/web canónico usa plain CSS; mantener dependencias mínimas).

## Qué se migró y por qué NO

| Elemento del prototipo | ¿Migrado? | Razón |
|---|---|---|
| 6 compañeras hardcoded | ❌ No | SPECT §4: el MVP tiene **una sola** compañera (Vane). |
| `rating` / `chats` ficticios | ❌ No | Issue #1: eliminar toda prueba social fabricada. |
| Testimonios ficticios | ❌ No | Issue #1: sin reseñas/usuarios inventados. |
| Stats falsas (12.4k+, 2.1M, 4.9★, 99.9%) | ❌ No | Issue #1: sin métricas fabricadas. |
| Features como "implementadas" (memoria, voz, E2E, 24/7) | ❌ No | Issue #1: honest labels — `prototype` / `planned`. |
| `src/app/api/chat/route.ts` (Next.js + z-ai-web-dev-sdk) | ❌ No | Issue #1: el chat debe ir por FastAPI `/v1/chat`. z-ai-web-dev-sdk es Node-only, no puede ir en el backend Python. |
| `prisma/schema.prisma` (SQLite, User/Post tutorial) | ❌ No | Arquitectura canónica usa PostgreSQL + domain model existente. |
| System prompts con "NUNCA menciones que sos una IA" | ❌ No | Issue #1: transparencia de identidad obligatoria. |
| Imágenes/video privados del owner | ❌ No | Issue #1: usar placeholders sintéticos; assets privados gitignored. |
| `companion-studio-v1.zip` en public/ | ❌ No | Issue #1: no versionar el ZIP de entrega en el frontend. |

## Archivos modificados / creados

### Modificados
- `apps/web/app/layout.tsx` — metadata cyber-noir, `lang="es"` (preservado).
- `apps/web/app/page.tsx` — orquestación: Hero → Onboarding → ChatPanel → Capabilities → Footer.
- `apps/web/app/styles.css` — sistema visual cyber-noir completo (plain CSS).
- `apps/web/tsconfig.json` — añadido `baseUrl` + `paths` para alias `@/*`.
- `.gitignore` — añadido `*.egg-info/` (artifact de build Python).

### Creados
- `apps/web/.eslintrc.json` — config ESLint (`next/core-web-vitals`) para lint no-interactivo.
- `apps/web/lib/companion.ts` — definición de **Vane** (una compañera canónica, system prompt transparente).
- `apps/web/lib/api.ts` — client tipado para `POST /v1/chat` (FastAPI), envía `character_id="vane"`.
- `apps/web/components/Navbar.tsx` — nav glass sticky con scroll detection.
- `apps/web/components/Hero.tsx` — hero cyber-noir (starfield, retrato placeholder, CTA).
- `apps/web/components/Onboarding.tsx` — 5 decisiones per SPECT §2.2.
- `apps/web/components/ChatPanel.tsx` — chat UI → FastAPI `/v1/chat`, typing indicator, quick prompts, dev validation visibility.
- `apps/web/components/Capabilities.tsx` — capacidades con honest labels (`implemented` / `prototype` / `planned`).
- `apps/web/components/Footer.tsx` — footer glass + adult note.
- `apps/web/public/companions/vane-placeholder.svg` — retrato placeholder sintético (silueta abstracta cyber-noir, NO una persona real).
- `pnpm-lock.yaml` — lockfile para builds reproducibles.

## Backend

**No se modificó el backend.** El frontend se conecta al FastAPI existente:
- `POST /v1/chat` con `{ message, character_id: "vane", conversation_id: "web-session" }`.
- Lee `data.response.content` para la respuesta.
- Muestra `data.response.validation` en modo desarrollo.
- El `MockModelProvider` devuelve respuestas canned (honestamente etiquetado como "provider: mock" en la UI).

### z-ai-web-dev-sdk
NO se integró en el backend porque es un SDK Node-only y el backend canónico es Python 3.12 / FastAPI. Si en el futuro se desea un provider LLM real, debe implementarse como un adapter Python que cumpla el `ModelProvider` Protocol (ADR 0002), manteniendo el SDK fuera del domain layer.

## Real vs Mock

| Componente | Estado | Notas |
|---|---|---|
| Frontend (apps/web) | Real | Next.js 14 App Router, cyber-noir UI, construye y pasa lint. |
| Chat API | Mock | `MockModelProvider` devuelve strings canned. Etiquetado "provider: mock" en UI. |
| Onboarding | Real | 5 decisiones → perfil, client-side. No persiste en backend (TODO futuro). |
| Memoria | No implementada | Etiquetada "planned" en Capabilities. |
| Voz / Audiovisual | No implementada | Etiquetada "planned". |
| Validación de salida | Real | `OutputValidator` activo en backend; visible en dev mode. |
| Media / Video | Placeholder | "▣ Video enviado · placeholder · no generado en vivo". |
| Retrato de Vane | Placeholder sintético | SVG abstracto, no una persona real. |

## Endpoints actuales

| Método | Path | Estado |
|---|---|---|
| GET | `/health` | ✅ existente, sin cambios |
| POST | `/v1/onboarding/profile` | ✅ existente, sin cambios (frontend aún no lo llama) |
| POST | `/v1/characters` | ✅ existente, sin cambios |
| POST | `/v1/chat` | ✅ existente, sin cambios — frontend lo usa con `character_id="vane"` |
| GET | `/v1/media/mock` | ✅ existente, sin cambios |

## Comandos ejecutados (verificación real)

```bash
# Frontend
pnpm install                                    # ✅ 322 packages
pnpm --dir apps/web lint                        # ✅ No ESLint warnings or errors
pnpm --dir apps/web build                       # ✅ Route / 5.19 kB, First Load 92.3 kB

# Backend
cd apps/api && python3 -m venv .venv
.venv/bin/pip install -e ".[dev]"              # ✅ FastAPI 0.141.1, Pydantic 2.13.4
.venv/bin/ruff check .                          # ✅ All checks passed
.venv/bin/pytest tests/ -v                      # ✅ 5 passed

# API smoke test
curl -X POST localhost:8000/v1/chat \
  -H "Content-Type: application/json" \
  -d '{"message":"hola","character_id":"vane"}'
# → content: "Te leo. Soy la anfitriona de prueba y recibí: \"hola\" ¿Seguimos desde ahí?"
# → validation.is_valid: true
```

## Browser smoke test

Ejecutado con agent-browser contra `http://localhost:3000` (Next.js) + `http://localhost:8000` (FastAPI):

1. **Home** ✅ — Hero renderiza ("Una presencia con carácter"), badge "Prototipo cyber-noir · Una compañera", capacidades visibles, sin errores de consola.
2. **Onboarding** ✅ — Click "Conocer a Vane" → aparecen las 5 decisiones. Flow completo de 5 clicks funciona.
3. **Chat** ✅ — Aparece vista de chat con greeting de Vane, header "Prototipo · provider: mock", placeholder media "no generado en vivo".
4. **Mobile** ✅ — Viewport 390×844 (iPhone 14): hero, heading, button renderizan correctamente.
5. **API connection** ✅ — `POST /v1/chat` devuelve respuesta válida con `validation.is_valid: true`.
6. **Errores** ✅ — Sin errores de consola ni de página en todo el flujo.

## Regla de assets locales / privados

- **Assets comprometidos en el repo**: solo `apps/web/public/companions/vane-placeholder.svg` (SVG sintético, no una persona real). SVG no está en `.gitignore` (solo `*.png/*.jpg/*.jpeg/*.webp` lo están).
- **Assets privados del owner**: NO se versionaron. El `.gitignore` ignora `media/`, `uploads/`, `originals/`, `derived/`, `*.mp4`, `*.mov`, `*.png`, `*.jpg`, `*.jpeg`, `*.webp`, `fotos_studio/`, `docs_owner/`.
- **Para preview local**: el owner puede colocar un retrato real `vane.png` en `apps/web/public/companions/` (será gitignored por la regla `*.png`). El código referencia `/companions/vane-placeholder.svg` — para usar el retrato real, actualizar `vane.portrait` en `lib/companion.ts`.
- **Build sin assets privados**: `pnpm install && pnpm --dir apps/web lint && pnpm --dir apps/web build` y `pytest` todos pasan sin assets privados presentes.

## Limitaciones conocidas

1. **Chat es mock** — el `MockModelProvider` devuelve strings canned sin importar el `character_id`. Para chat real, agregar un provider Python (adapter) al `ModelRouter`.
2. **Sin memoria persistente** — el onboarding guarda el perfil solo en state del cliente. La persistencia requiere el backend de memoria planificado.
3. **Sin voz/audiovisual** — etiquetado "planned".
4. **El mock se identifica como "anfitriona"** incluso cuando `character_id="vane"` — el `MockModelProvider` ignora el character_id. Corregible con un cambio mínimo al mock o con un provider real.
5. **El frontend no llama a `/v1/onboarding/profile`** — el perfil se guarda solo en cliente. Conectarlo al backend es trabajo futuro.

## Reglas de transparencia cumplidas (Issue #1)

- ✅ Una sola compañera (Vane), no 6.
- ✅ Sin `rating` / `chats` ficticios.
- ✅ Sin testimonios falsos.
- ✅ Sin métricas fabricadas (user count, message count, uptime, satisfaction).
- ✅ Features honestamente etiquetadas: `implemented` / `prototype` / `planned`.
- ✅ Media placeholder etiquetado "no generado en vivo".
- ✅ System prompt de Vane NO instruye a ocultar su naturaleza de IA.
- ✅ Sin `.env`, tokens, ni assets privados en el repo.
- ✅ Sin `companion-studio-v1.zip` en el frontend.
- ✅ Sin Prisma SQLite migrado.
- ✅ Sin Next.js API route como backend — chat via FastAPI `/v1/chat`.
- ✅ Note adult-only "+18" presente.
