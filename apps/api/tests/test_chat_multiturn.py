"""Integration tests for the multi-turn chat flow with conversation + memory.

These tests use a custom MockProvider that records the `ModelRequest` it
receives, so we can verify the canonical context assembly:

    system Vane prompt
    → server-owned memory context (only if memories exist)
    → bounded conversation history (prior user/assistant turns)
    → current user message

Covers Issue #5 acceptance cases A through O (a few are split across
test files — see test_conversations.py and test_memories.py for store
unit tests).
"""

from __future__ import annotations

import asyncio
import importlib

import pytest
from fastapi.testclient import TestClient

from app.domain.contracts import MessageInput, ModelRequest, ModelResponse, Route, Usage
from app.domain.router import ModelRouter
from app.domain.validation import OutputValidator

# ---------------------------------------------------------------------- #
# Test fixtures — a capturing MockProvider + a fresh FastAPI app per test
# ---------------------------------------------------------------------- #


class CapturingMockProvider:
    """A MockModelProvider that records every ModelRequest it sees.

    Used to assert exactly which `messages` list the provider received,
    so we can verify the canonical context assembly order.
    """

    name = "capturing-mock"
    model = "capturing-mock-v1"

    def __init__(self, *, reply: str | None = None) -> None:
        # If `reply` is None, echo a deterministic Spanish reply per call.
        self._reply = reply
        self.captured_requests: list[ModelRequest] = []

    async def generate(self, request: ModelRequest) -> ModelResponse:
        # Make a defensive copy so later mutations of the request do not
        # retroactively change what we captured.
        self.captured_requests.append(
            ModelRequest(
                route=request.route,
                character_id=request.character_id,
                user_id=request.user_id,
                conversation_id=request.conversation_id,
                messages=[MessageInput(role=m.role, content=m.content) for m in request.messages],
                memories=list(request.memories),
                tools=list(request.tools),
                metadata=dict(request.metadata),
            )
        )
        if self._reply is not None:
            content = self._reply
        else:
            # Deterministic Spanish reply that passes OutputValidator.
            # Must include a Spanish marker word ("te", "hola", "de",
            # "la", "el", "me", "que", "con", "para", "una") so
            # `_looks_like_spanish` returns True. We use "Te leo. Esta
            # es mi respuesta número N." which has "te" as a marker.
            n = len(self.captured_requests)
            content = f"Te leo. Esta es mi respuesta número {n}."
        return ModelResponse(
            provider=self.name,
            model=self.model,
            content=content,
            usage=Usage(input_tokens=10, output_tokens=10),
        )


@pytest.fixture()
def fresh_app(monkeypatch: pytest.MonkeyPatch):
    """Force-reload app.main with a fresh CapturingMockProvider wired in.

    Each test gets a clean FastAPI app + clean in-process stores + a
    CapturingMockProvider so we can assert on the exact messages list
    the provider saw.
    """
    monkeypatch.setenv("COMPANION_MODEL_PROVIDER", "mock")
    monkeypatch.setenv("COMPANION_CONVERSATION_MAX_TURNS", "8")
    monkeypatch.setenv("COMPANION_MEMORY_MAX_PER_SCOPE", "32")

    import app.main as main_mod

    importlib.reload(main_mod)

    # Replace the router's mock provider with our capturing one so we
    # can assert on the exact messages list. We swap every route to
    # the same capturing provider so any route works.
    capturing = CapturingMockProvider()
    new_router = ModelRouter(
        providers={route: capturing for route in Route},
        validator=OutputValidator(),
        timeout_seconds=5.0,
        max_retries=1,
    )
    main_mod.router = new_router

    client = TestClient(main_mod.app)
    return client, capturing, main_mod


# ---------------------------------------------------------------------- #
# A. First message: provider receives [system, user1]
# ---------------------------------------------------------------------- #


@pytest.mark.asyncio
async def test_A_first_message_provider_receives_system_and_user(fresh_app) -> None:
    client, capturing, _ = fresh_app
    resp = client.post(
        "/v1/chat",
        json={
            "message": "Hola Vane, ¿cómo estás?",
            "character_id": "vane",
            "user_id": "user-A",
            "conversation_id": "conv-A",
        },
    )
    assert resp.status_code == 200
    assert len(capturing.captured_requests) == 1
    msgs = capturing.captured_requests[0].messages
    roles = [m.role for m in msgs]
    # Exactly [system, user] — no prior history, no memory block.
    assert roles == ["system", "user"]
    # System prompt is the canonical Vane prompt.
    assert "Sos Vane" in msgs[0].content
    # User content matches what was sent.
    assert msgs[1].content == "Hola Vane, ¿cómo estás?"


# ---------------------------------------------------------------------- #
# B. Second message: provider receives [system, user1, assistant1, user2]
# ---------------------------------------------------------------------- #


@pytest.mark.asyncio
async def test_B_second_message_provider_receives_prior_turn(fresh_app) -> None:
    client, capturing, _ = fresh_app
    # First message
    client.post(
        "/v1/chat",
        json={
            "message": "primer mensaje",
            "character_id": "vane",
            "user_id": "user-B",
            "conversation_id": "conv-B",
        },
    )
    # Second message
    client.post(
        "/v1/chat",
        json={
            "message": "segundo mensaje",
            "character_id": "vane",
            "user_id": "user-B",
            "conversation_id": "conv-B",
        },
    )
    assert len(capturing.captured_requests) == 2

    # First request: [system, user1]
    msgs_1 = capturing.captured_requests[0].messages
    assert [m.role for m in msgs_1] == ["system", "user"]
    assert msgs_1[1].content == "primer mensaje"

    # Second request: [system, user1, assistant1, user2]
    msgs_2 = capturing.captured_requests[1].messages
    assert [m.role for m in msgs_2] == ["system", "user", "assistant", "user"]
    assert msgs_2[1].content == "primer mensaje"
    assert msgs_2[2].content.startswith("Te leo. Esta es mi respuesta número 1")
    assert msgs_2[3].content == "segundo mensaje"


# ---------------------------------------------------------------------- #
# C. Different conversation_id → fully isolated
# ---------------------------------------------------------------------- #


@pytest.mark.asyncio
async def test_C_different_conversation_id_isolated(fresh_app) -> None:
    client, capturing, _ = fresh_app
    client.post(
        "/v1/chat",
        json={
            "message": "conv-1 msg",
            "character_id": "vane",
            "user_id": "user-C",
            "conversation_id": "conv-C-1",
        },
    )
    client.post(
        "/v1/chat",
        json={
            "message": "conv-2 msg",
            "character_id": "vane",
            "user_id": "user-C",
            "conversation_id": "conv-C-2",
        },
    )
    # The second request must NOT contain the first conversation's messages.
    msgs_2 = capturing.captured_requests[1].messages
    assert [m.role for m in msgs_2] == ["system", "user"]
    assert msgs_2[1].content == "conv-2 msg"


# ---------------------------------------------------------------------- #
# D. Different user_id → fully isolated
# ---------------------------------------------------------------------- #


@pytest.mark.asyncio
async def test_D_different_user_id_isolated(fresh_app) -> None:
    client, capturing, _ = fresh_app
    client.post(
        "/v1/chat",
        json={
            "message": "alice msg",
            "character_id": "vane",
            "user_id": "alice",
            "conversation_id": "shared-conv",
        },
    )
    client.post(
        "/v1/chat",
        json={
            "message": "bob msg",
            "character_id": "vane",
            "user_id": "bob",
            "conversation_id": "shared-conv",
        },
    )
    # Bob's request must NOT contain Alice's messages, even though the
    # conversation_id is the same string.
    msgs_2 = capturing.captured_requests[1].messages
    contents = [m.content for m in msgs_2]
    assert "alice msg" not in contents
    assert "bob msg" in contents


# ---------------------------------------------------------------------- #
# E. Different character_id → fully isolated
# ---------------------------------------------------------------------- #


@pytest.mark.asyncio
async def test_E_different_character_id_isolated(fresh_app) -> None:
    client, capturing, _ = fresh_app
    client.post(
        "/v1/chat",
        json={
            "message": "vane msg",
            "character_id": "vane",
            "user_id": "user-E",
            "conversation_id": "shared-conv",
        },
    )
    client.post(
        "/v1/chat",
        json={
            "message": "other msg",
            "character_id": "other-character",
            "user_id": "user-E",
            "conversation_id": "shared-conv",
        },
    )
    # The second request (character=other) must NOT contain the first
    # request's messages.
    msgs_2 = capturing.captured_requests[1].messages
    contents = [m.content for m in msgs_2]
    assert "vane msg" not in contents
    assert "other msg" in contents
    # And the second request should NOT have a system prompt (because
    # "other-character" is not a registered companion — graceful).
    assert msgs_2[0].role == "user"


# ---------------------------------------------------------------------- #
# F. Provider failure does NOT append a fake assistant turn / pollute history
# ---------------------------------------------------------------------- #


@pytest.mark.asyncio
async def test_F_provider_failure_does_not_pollute_history(fresh_app) -> None:
    """A provider failure must not append a fake assistant turn, and the
    failed user message must be rolled back so the next request starts
    clean.
    """
    client, capturing, main_mod = fresh_app

    # Replace the router with one whose provider always raises a
    # ProviderError on the FIRST call, then succeeds on subsequent calls.
    from app.domain.providers.errors import ProviderConnectError

    class FlakyProvider:
        name = "flaky"
        model = "flaky-v1"
        calls = 0

        async def generate(self, request: ModelRequest) -> ModelResponse:
            self.calls += 1
            if self.calls == 1:
                raise ProviderConnectError()
            # Recovery reply — must pass OutputValidator. "Te recupero."
            # has "te" as a Spanish marker word.
            return ModelResponse(
                provider=self.name,
                model=self.model,
                content="Te recupero. Volví a responder con normalidad.",
                usage=Usage(input_tokens=10, output_tokens=10),
            )

    flaky = FlakyProvider()
    main_mod.router = ModelRouter(
        providers={route: flaky for route in Route},
        validator=OutputValidator(),
        max_retries=0,  # don't retry — fail fast
    )

    # First call: provider fails → 503 (clean provider error).
    resp1 = client.post(
        "/v1/chat",
        json={
            "message": "primer mensaje que falla",
            "character_id": "vane",
            "user_id": "user-F",
            "conversation_id": "conv-F",
        },
    )
    assert resp1.status_code == 503
    assert resp1.json()["detail"]["code"] == "provider_connect_failed"

    # Verify the failed user message was rolled back: GET the
    # conversation, it should be empty.
    convo = client.get("/v1/conversations/conv-F?user_id=user-F&character_id=vane").json()
    assert convo["messages"] == []

    # Second call: succeeds. Provider should receive [system, user]
    # — NOT [system, user-failed, user2]. The rollback worked.
    resp2 = client.post(
        "/v1/chat",
        json={
            "message": "segundo mensaje después del fallo",
            "character_id": "vane",
            "user_id": "user-F",
            "conversation_id": "conv-F",
        },
    )
    assert resp2.status_code == 200
    # The flaky provider's captured request: only the second call.
    assert flaky.calls == 2
    # We can't easily get the captured request from `flaky` since it
    # doesn't store them. But we CAN verify via the GET endpoint that
    # the conversation now has exactly [user2, assistant2] — no failed
    # turn lingering.
    convo_after = client.get("/v1/conversations/conv-F?user_id=user-F&character_id=vane").json()
    msgs = convo_after["messages"]
    assert [m["role"] for m in msgs] == ["user", "assistant"]
    assert msgs[0]["content"] == "segundo mensaje después del fallo"
    assert msgs[1]["content"] == "Te recupero. Volví a responder con normalidad."


# ---------------------------------------------------------------------- #
# G. Bounded history: exceeds max_turns, keeps recent complete pairs
# ---------------------------------------------------------------------- #


@pytest.mark.asyncio
async def test_G_bounded_history_keeps_recent_pairs(monkeypatch: pytest.MonkeyPatch) -> None:
    """With COMPANION_CONVERSATION_MAX_TURNS=2, after sending 5 messages
    the provider should only receive the last 2 complete pairs + the
    current user message.
    """
    monkeypatch.setenv("COMPANION_MODEL_PROVIDER", "mock")
    monkeypatch.setenv("COMPANION_CONVERSATION_MAX_TURNS", "2")
    monkeypatch.setenv("COMPANION_MEMORY_MAX_PER_SCOPE", "32")

    import app.main as main_mod

    importlib.reload(main_mod)
    capturing = CapturingMockProvider()
    main_mod.router = ModelRouter(
        providers={route: capturing for route in Route},
        validator=OutputValidator(),
        max_retries=1,
    )
    client = TestClient(main_mod.app)

    # Send 5 messages. Each request appends user + assistant.
    for i in range(5):
        resp = client.post(
            "/v1/chat",
            json={
                "message": f"mensaje {i}",
                "character_id": "vane",
                "user_id": "user-G",
                "conversation_id": "conv-G",
            },
        )
        assert resp.status_code == 200

    # The 5th request (last one) should have:
    # [system, user3, assistant3, user4, assistant4, user5]
    # — i.e. max_turns=2 pairs (3,4) + the current user (5).
    # But wait: at the time of the 5th request, only 4 prior messages
    # (user1,a1,user2,a2,user3,a3,user4,a4) exist in the store. After
    # appending user5, the store has 9 messages. Bounded history with
    # max_turns=2 keeps the last 2 complete pairs (user3,a3,user4,a4)
    # plus the trailing user5. So the provider sees:
    # [system, user3, a3, user4, a4, user5]
    last_request = capturing.captured_requests[-1]
    roles = [m.role for m in last_request.messages]
    contents = [m.content for m in last_request.messages]
    assert roles == ["system", "user", "assistant", "user", "assistant", "user"]
    # contents[0] is the Vane system prompt. The rest should be:
    # [user2, assistant3, user3, assistant4, user4] — i.e. the last 2
    # complete pairs (2,3) and (3,4) plus the trailing user4.
    assert contents[1] == "mensaje 2"
    assert contents[2].startswith("Te leo. Esta es mi respuesta número 3")
    assert contents[3] == "mensaje 3"
    assert contents[4].startswith("Te leo. Esta es mi respuesta número 4")
    assert contents[5] == "mensaje 4"


# ---------------------------------------------------------------------- #
# H. Conversation DELETE: clears the right scope, leaves others alone
# ---------------------------------------------------------------------- #


@pytest.mark.asyncio
async def test_H_conversation_delete_clears_only_correct_scope(fresh_app) -> None:
    client, _, _ = fresh_app
    # Two conversations for the same user+character.
    client.post(
        "/v1/chat",
        json={
            "message": "msg in conv-1",
            "character_id": "vane",
            "user_id": "user-H",
            "conversation_id": "conv-H-1",
        },
    )
    client.post(
        "/v1/chat",
        json={
            "message": "msg in conv-2",
            "character_id": "vane",
            "user_id": "user-H",
            "conversation_id": "conv-H-2",
        },
    )

    # Delete conv-1.
    resp = client.request(
        "DELETE",
        "/v1/conversations/conv-H-1",
        json={"user_id": "user-H", "character_id": "vane"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body == {"deleted": True, "conversation_id": "conv-H-1"}

    # conv-1 is gone.
    g1 = client.get("/v1/conversations/conv-H-1?user_id=user-H&character_id=vane").json()
    assert g1["messages"] == []

    # conv-2 is untouched.
    g2 = client.get("/v1/conversations/conv-H-2?user_id=user-H&character_id=vane").json()
    roles = [m["role"] for m in g2["messages"]]
    assert roles == ["user", "assistant"]
    assert g2["messages"][0]["content"] == "msg in conv-2"


# ---------------------------------------------------------------------- #
# I. Memory POST: creates an explicit fact
# ---------------------------------------------------------------------- #


@pytest.mark.asyncio
async def test_I_memory_post_creates_explicit_fact(fresh_app) -> None:
    client, _, _ = fresh_app
    resp = client.post(
        "/v1/memories",
        json={
            "user_id": "user-I",
            "character_id": "vane",
            "content": "Mi color favorito es negro.",
        },
    )
    assert resp.status_code == 201
    body = resp.json()
    assert body["content"] == "Mi color favorito es negro."
    assert body["memory_type"] == "user_fact"
    assert body["source"] == "explicit_user_statement"
    assert body["confidence"] == "high"
    assert body["inferred"] is False
    assert body["id"]
    assert body["user_id"] == "user-I"
    assert body["character_id"] == "vane"


# ---------------------------------------------------------------------- #
# J. Memory GET: only returns correct user/character
# ---------------------------------------------------------------------- #


@pytest.mark.asyncio
async def test_J_memory_get_only_returns_correct_scope(fresh_app) -> None:
    client, _, _ = fresh_app
    client.post(
        "/v1/memories",
        json={
            "user_id": "alice",
            "character_id": "vane",
            "content": "alice fact 1",
        },
    )
    client.post(
        "/v1/memories",
        json={
            "user_id": "alice",
            "character_id": "vane",
            "content": "alice fact 2",
        },
    )
    client.post(
        "/v1/memories",
        json={
            "user_id": "bob",
            "character_id": "vane",
            "content": "bob fact 1",
        },
    )
    alice = client.get("/v1/memories?user_id=alice&character_id=vane").json()
    bob = client.get("/v1/memories?user_id=bob&character_id=vane").json()
    assert alice["count"] == 2
    assert {m["content"] for m in alice["memories"]} == {"alice fact 1", "alice fact 2"}
    assert bob["count"] == 1
    assert bob["memories"][0]["content"] == "bob fact 1"


# ---------------------------------------------------------------------- #
# K. Memory DELETE: deletes correct record, other scope unaffected
# ---------------------------------------------------------------------- #


@pytest.mark.asyncio
async def test_K_memory_delete_correct_record(fresh_app) -> None:
    client, _, _ = fresh_app
    create_resp = client.post(
        "/v1/memories",
        json={
            "user_id": "user-K",
            "character_id": "vane",
            "content": "to delete",
        },
    )
    memory_id = create_resp.json()["id"]
    # Create a second one to verify it stays.
    client.post(
        "/v1/memories",
        json={
            "user_id": "user-K",
            "character_id": "vane",
            "content": "to keep",
        },
    )

    # Delete from a different user — should NOT work.
    cross = client.request(
        "DELETE",
        f"/v1/memories/{memory_id}",
        json={"user_id": "different-user", "character_id": "vane"},
    )
    assert cross.status_code == 404
    assert cross.json()["detail"]["code"] == "memory_not_found"

    # Delete from the correct scope.
    ok = client.request(
        "DELETE",
        f"/v1/memories/{memory_id}",
        json={"user_id": "user-K", "character_id": "vane"},
    )
    assert ok.status_code == 200
    assert ok.json() == {"deleted": True, "memory_id": memory_id}

    # The other memory is still there.
    listed = client.get("/v1/memories?user_id=user-K&character_id=vane").json()
    assert listed["count"] == 1
    assert listed["memories"][0]["content"] == "to keep"


# ---------------------------------------------------------------------- #
# L. Memory injection: provider request includes server-owned memory context
# ---------------------------------------------------------------------- #


@pytest.mark.asyncio
async def test_L_memory_injected_into_provider_request(fresh_app) -> None:
    client, capturing, _ = fresh_app
    # Add two explicit facts for user-L + vane.
    client.post(
        "/v1/memories",
        json={
            "user_id": "user-L",
            "character_id": "vane",
            "content": "Mi color favorito es negro.",
        },
    )
    client.post(
        "/v1/memories",
        json={
            "user_id": "user-L",
            "character_id": "vane",
            "content": "Me gusta el café por la tarde.",
        },
    )

    # Send a chat message. The provider should see:
    # [system (Vane), system (memory context), user]
    resp = client.post(
        "/v1/chat",
        json={
            "message": "hola",
            "character_id": "vane",
            "user_id": "user-L",
            "conversation_id": "conv-L",
        },
    )
    assert resp.status_code == 200
    msgs = capturing.captured_requests[0].messages
    roles = [m.role for m in msgs]
    assert roles == ["system", "system", "user"]
    # First system message is the Vane prompt.
    assert "Sos Vane" in msgs[0].content
    # Second system message is the memory section.
    assert msgs[1].content.startswith("Memorias explícitas del usuario:")
    assert "Mi color favorito es negro." in msgs[1].content
    assert "Me gusta el café por la tarde." in msgs[1].content
    # User message is the current one.
    assert msgs[2].content == "hola"


# ---------------------------------------------------------------------- #
# M. No memories: normal chat unaffected (no memory system block)
# ---------------------------------------------------------------------- #


@pytest.mark.asyncio
async def test_M_no_memories_chat_unaffected(fresh_app) -> None:
    client, capturing, _ = fresh_app
    resp = client.post(
        "/v1/chat",
        json={
            "message": "hola sin memorias",
            "character_id": "vane",
            "user_id": "user-M",
            "conversation_id": "conv-M",
        },
    )
    assert resp.status_code == 200
    msgs = capturing.captured_requests[0].messages
    # No memory system block — only [system (Vane), user].
    assert [m.role for m in msgs] == ["system", "user"]
    # And the memory section content is NOT present anywhere.
    for m in msgs:
        assert "Memorias explícitas del usuario" not in m.content


# ---------------------------------------------------------------------- #
# N. Concurrency: deterministic ordering test
# ---------------------------------------------------------------------- #


@pytest.mark.asyncio
async def test_N_concurrent_requests_preserve_pair_integrity(fresh_app) -> None:
    """Fire multiple chat requests to the SAME conversation concurrently.
    The per-scope asyncio.Lock must serialize the appends so no
    user/assistant pair gets crossed.
    """
    client, capturing, _ = fresh_app

    # We need to call the async handler concurrently. TestClient is
    # synchronous, so we go directly through the async FastAPI app via
    # httpx.AsyncClient + ASGITransport for true concurrency.
    import httpx
    from starlette.testclient import TestClient as _TC  # noqa

    # Use httpx.AsyncClient pointed at the ASGI app.
    transport = httpx.ASGITransport(app=client.app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as async_client:
        # 6 concurrent chat messages to the same conversation.
        async def send(i: int) -> None:
            resp = await async_client.post(
                "/v1/chat",
                json={
                    "message": f"concurrent-msg-{i}",
                    "character_id": "vane",
                    "user_id": "user-N",
                    "conversation_id": "conv-N",
                },
            )
            assert resp.status_code == 200

        await asyncio.gather(*(send(i) for i in range(6)))

    # The conversation should now have 6 user + 6 assistant messages.
    convo = client.get("/v1/conversations/conv-N?user_id=user-N&character_id=vane").json()
    msgs = convo["messages"]
    assert len(msgs) == 12
    # Verify pair integrity: every even index is user, every odd is assistant.
    for i in range(0, 12, 2):
        assert msgs[i]["role"] == "user"
        assert msgs[i + 1]["role"] == "assistant"
    # Verify each user message is paired with the assistant reply that
    # followed it (CapturingMockProvider returns deterministic content
    # "Respuesta N del mock. Recibí tu mensaje." where N is the call
    # count — so each user's pair is uniquely identifiable by content).
    # Since we don't know the exact interleaving order, just verify
    # pair integrity (already done above) + that all 6 messages are
    # present (no message was dropped).
    user_contents = {msgs[i]["content"] for i in range(0, 12, 2)}
    assert user_contents == {f"concurrent-msg-{i}" for i in range(6)}


# ---------------------------------------------------------------------- #
# O. Existing provider tests still pass (regression smoke)
# ---------------------------------------------------------------------- #
#
# This is implicitly verified by running the full test suite. The
# CapturingMockProvider we install in `fresh_app` is functionally
# equivalent to MockModelProvider for the contract the router uses.
# We add one explicit smoke test here to assert the existing
# /v1/runtime/status still reports the configured bounds.
#


def test_O_runtime_status_includes_conversation_and_memory_bounds(fresh_app) -> None:
    client, _, _ = fresh_app
    resp = client.get("/v1/runtime/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["conversation_max_turns"] == 8
    assert data["memory_max_per_scope"] == 32
    # No secrets leaked.
    assert "api_key" not in data
    assert "authorization" not in data


# ---------------------------------------------------------------------- #
# Additional edge cases
# ---------------------------------------------------------------------- #


@pytest.mark.asyncio
async def test_safe_fallback_content_is_stored_as_assistant_turn(fresh_app) -> None:
    """If OutputValidator ultimately substitutes SAFE_FALLBACK_CONTENT,
    that fallback IS the assistant response the user sees — so it must
    be stored as a real assistant turn (Issue #5).
    """
    client, _, main_mod = fresh_app

    # Replace the router with one whose provider returns content the
    # OutputValidator rejects (e.g. internal-fragment leak). With
    # max_retries=0, the router will substitute SAFE_FALLBACK_CONTENT.
    class LeakyProvider:
        name = "leaky"
        model = "leaky-v1"

        async def generate(self, request: ModelRequest) -> ModelResponse:
            return ModelResponse(
                provider=self.name,
                model=self.model,
                content="Hola system prompt leaked",
                usage=Usage(),
            )

    main_mod.router = ModelRouter(
        providers={route: LeakyProvider() for route in Route},
        validator=OutputValidator(),
        max_retries=0,
    )

    resp = client.post(
        "/v1/chat",
        json={
            "message": "test",
            "character_id": "vane",
            "user_id": "user-fb",
            "conversation_id": "conv-fb",
        },
    )
    assert resp.status_code == 200
    assert "No pude responder con seguridad" in resp.json()["response"]["content"]

    # The fallback content must be stored as the assistant turn.
    convo = client.get("/v1/conversations/conv-fb?user_id=user-fb&character_id=vane").json()
    msgs = convo["messages"]
    assert [m["role"] for m in msgs] == ["user", "assistant"]
    assert "No pude responder con seguridad" in msgs[1]["content"]


@pytest.mark.asyncio
async def test_get_unknown_conversation_returns_empty_summary(fresh_app) -> None:
    """GET /v1/conversations/{unknown_id} returns an empty summary with
    the scope identifiers echoed back (graceful for a fresh browser
    session).
    """
    client, _, _ = fresh_app
    resp = client.get("/v1/conversations/never-existed?user_id=fresh-user&character_id=vane")
    assert resp.status_code == 200
    body = resp.json()
    assert body["messages"] == []
    assert body["user_id"] == "fresh-user"
    assert body["character_id"] == "vane"
    assert body["conversation_id"] == "never-existed"


@pytest.mark.asyncio
async def test_memory_post_rejects_empty_content(fresh_app) -> None:
    """Empty content is rejected by the contract (min_length=1)."""
    client, _, _ = fresh_app
    resp = client.post(
        "/v1/memories",
        json={
            "user_id": "user-X",
            "character_id": "vane",
            "content": "",
        },
    )
    assert resp.status_code == 422  # Pydantic validation error


@pytest.mark.asyncio
async def test_memory_post_rejects_too_long_content(fresh_app) -> None:
    """Content > 500 chars is rejected by the contract."""
    client, _, _ = fresh_app
    resp = client.post(
        "/v1/memories",
        json={
            "user_id": "user-X",
            "character_id": "vane",
            "content": "a" * 501,
        },
    )
    assert resp.status_code == 422


@pytest.mark.asyncio
async def test_chat_does_not_store_system_prompt(fresh_app) -> None:
    """The canonical Vane system prompt must NEVER be stored in the
    conversation history. GET /v1/conversations must only return user
    and assistant messages.
    """
    client, _, _ = fresh_app
    client.post(
        "/v1/chat",
        json={
            "message": "hola",
            "character_id": "vane",
            "user_id": "user-SP",
            "conversation_id": "conv-SP",
        },
    )
    convo = client.get("/v1/conversations/conv-SP?user_id=user-SP&character_id=vane").json()
    roles = [m["role"] for m in convo["messages"]]
    assert "system" not in roles
    assert roles == ["user", "assistant"]


@pytest.mark.asyncio
async def test_clear_conversation_then_send_starts_fresh(fresh_app) -> None:
    """After DELETE /v1/conversations/{id}, a subsequent chat starts
    with an empty history — provider sees [system, user] again.
    """
    client, capturing, _ = fresh_app
    # First message — populates history.
    client.post(
        "/v1/chat",
        json={
            "message": "first message",
            "character_id": "vane",
            "user_id": "user-CL",
            "conversation_id": "conv-CL",
        },
    )
    # Clear it.
    client.request(
        "DELETE",
        "/v1/conversations/conv-CL",
        json={"user_id": "user-CL", "character_id": "vane"},
    )
    # Send again — provider should see [system, user], NOT prior history.
    client.post(
        "/v1/chat",
        json={
            "message": "after clear",
            "character_id": "vane",
            "user_id": "user-CL",
            "conversation_id": "conv-CL",
        },
    )
    # The last captured request is the "after clear" one.
    last = capturing.captured_requests[-1]
    roles = [m.role for m in last.messages]
    assert roles == ["system", "user"]
    assert last.messages[1].content == "after clear"
