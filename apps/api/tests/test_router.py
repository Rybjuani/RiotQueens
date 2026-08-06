import pytest

from app.domain.contracts import MessageInput, ModelRequest, Route
from app.domain.router import MockModelProvider, ModelRouter


@pytest.mark.asyncio
async def test_router_selects_provider_and_validates() -> None:
    request = ModelRequest(
        route=Route.FAST_CHAT,
        character_id="host",
        user_id="user",
        conversation_id="conversation",
        messages=[MessageInput(role="user", content="Hola")],
    )
    response = await ModelRouter().generate(request)
    assert response.provider == "mock"
    assert response.validation and response.validation.is_valid
    assert response.retry_count == 0


@pytest.mark.asyncio
async def test_router_retries_once_then_recovers() -> None:
    class BrokenProvider(MockModelProvider):
        calls = 0

        async def generate(self, request: ModelRequest):
            self.calls += 1
            response = await super().generate(request)
            response.content = ""
            return response

    provider = BrokenProvider()
    router = ModelRouter({route: provider for route in Route})
    request = ModelRequest(
        route=Route.MEMORY,
        character_id="host",
        user_id="user",
        conversation_id="conversation",
        messages=[MessageInput(role="user", content="Hola")],
    )
    response = await router.generate(request)
    assert provider.calls == 2
    assert response.retry_count == 1
    assert "No pude responder" in response.content
