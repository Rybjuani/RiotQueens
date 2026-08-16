# Contrato API

La fuente ejecutable de verdad es FastAPI/Pydantic y su OpenAPI en `/openapi.json`. No se duplican manualmente los contratos en TypeScript. Una futura misión puede generar un cliente con `openapi-typescript`.

Endpoints del corte vertical:

- `GET /health`
- `POST /v1/onboarding/profile`
- `POST /v1/characters`
- `POST /v1/chat`
- `GET /v1/media/mock`

Los schemas incluyen `UserPreferenceProfile`, `CharacterConfig`, `SessionOverride`, `ModelRequest`, `ModelResponse` y `OutputValidationResult`.
