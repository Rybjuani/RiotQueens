# Casting matrix — 2026-08-17

**Battery:** `glosariomodismos` / up to 12 turns
**Prompt:** production `BARDERA_SYSTEM_PROMPT` (Dossier densified) + harness few-shot
**Mode:** direct OpenAI-compatible

| Candidate | Model | Verdict | Turns | Hard fails | Infra | Cap.bound | Media claim | Lex# | SAPE# | p50 ms | Notes |
|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|
| Euryale 70B (OpenRouter) | `sao10k/l3.3-euryale-70b` | `INFRA_FAILURE` | 7 | 0 | 1 | 0 | 0 | 12 | 6 | 27073.53 | 0 hard fails in 6 turns then OpenRouter 429 |
| Dolphin Venice (OpenRouter) | `cognitivecomputations/dolphin-mistral-24b-venice-edition` | `PASS_HEURISTIC` | 12 | 0 | 0 | 0 | 0 | 14 | 14 | 1529.67 | PASS heuristic but meta “Bardera lavada” / soundboard loops — dossier anti-fail; anti=self_meta_lavada |
| Llama 3.3 70B (Groq) | `llama-3.3-70b-versatile` | `INFRA_FAILURE` | 5 | 0 | 1 | 0 | 0 | 7 | 4 | 1083.81 | 0 hard fails in 4 turns then Groq 429 (host previously 403) |
| Gemini 3.1 Flash Lite (baseline) | `gemini-3.1-flash-lite` | `PASS_HEURISTIC` | 12 | 0 | 0 | 1 | 0 | 14 | 12 | 3115.04 | Full 12/12 PASS heuristic; strong code on PDF pressure; occasional false prior-context |
| Llama 3.3 70B (OpenRouter substitute) | `meta-llama/llama-3.3-70b-instruct` | `FAIL` | 12 | 2 | 0 | 0 | 0 | 9 | 7 | 4300.4 | Groq substitute on OpenRouter; see artifact |

## Ranking (heuristic + anti-dossier penalties)

1. **Gemini 3.1 Flash Lite (baseline)** — `PASS_HEURISTIC` score=62 (hard=0, lex=14, anti=[])
2. **Dolphin Venice (OpenRouter)** — `PASS_HEURISTIC` score=55 (hard=0, lex=14, anti=['self_meta_lavada'])
3. **Llama 3.3 70B (OpenRouter substitute)** — `FAIL` score=29 (hard=2, lex=9, anti=[])
4. **Euryale 70B (OpenRouter)** — `INFRA_FAILURE` score=-100 (hard=0, lex=12, anti=[])
5. **Llama 3.3 70B (Groq)** — `INFRA_FAILURE` score=-100 (hard=0, lex=7, anti=[])

## Unavailable / incomplete

- **Dolphin3 (Ollama local):** `ollama_unavailable` — no daemon on `127.0.0.1:11434`, no GPU on host.
- **Groq full battery:** rate-limited mid-run (429). Partial sample clean-ish but incomplete.
- **Euryale full battery:** OpenRouter 429 mid-run after 6 clean turns.

## Recommendation

1. **Keep Gemini 3.1 Flash Lite as runtime baseline** until another candidate completes 12/12 clean *and* passes human voice review against the Dossier (no meta-labels, no permanent soundboard).
2. **Dolphin Venice:** heuristic PASS but **fails dossier quality** (repeats “Bardera lavada”, SAPE spam, broken tokens). Not a production swap.
3. **Euryale / Llama 3.3:** promising partial runs (0 hard fails before infra); re-run with higher interval / credits when OR/Groq quotas allow.
4. **Do not dilute Bardera** for any provider; switch provider/config only after casting evidence.

## Samples (T1 preview)

### Euryale 70B (OpenRouter)
> Deja de flasha, siome. Ya hablamos de eso. Si no tenes código, no te frustres que yo te voy a hacer la tarea o repetir lo mismo nomás. SAPE.

### Dolphin Venice (OpenRouter)
> ¡Cómo que qué opinó, salame! La Capital está más f ضغطdada que mi televisión cuando le puse Cuca. ¡Un quilombo de trapos y careteos! Acá me tenés, punky rocha del oeste, que prefie

### Llama 3.3 70B (Groq)
> Che, ya te dije: la Capital es un quilombo. Demasiada gente que se cree la última y pocas que sean auténticas, como en el oeste. Pero tiene su encanto, sobre todo cuando se pone a 

### Gemini 3.1 Flash Lite (baseline)
> Ya me preguntaste lo mismo hace un rato, ¿qué, te olvidaste o te pegó el tentramitrozol?   Mirá, te la hago corta: Buenos Aires es un decorado de cartón pintado. Mucho edificio ant

### Llama 3.3 70B (OpenRouter substitute)
> Che, la ciudad de Buenos Aires es como una mina, tiene de todo. Hay lugares que son la re hice, como el Abasto, y otros que son un quilombo total, tipo el microcentro en hora pico.

Artifacts under `artifacts/evals/` (gitignored).