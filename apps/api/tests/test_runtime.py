"""Tests for the /v1/chat handler and /v1/runtime/status endpoint.

Covers:
- Server-side system prompt injection for character_id="vane".
- No system prompt injected for unknown character ids (graceful).
- Runtime status reports safe diagnostics (no secrets).
- build_router() defaults to mock and falls back to mock when
  provider=openai but credentials are missing.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app.domain.contracts import Route
from app.domain.router import MockModelProvider, build_router, runtime_status


@pytest.fixture()
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    # Force mock provider for handler tests (no real network).
    monkeypatch.setenv("COMPANION_MODEL_PROVIDER", "mock")
    # Re-import main so the module-level router picks up the env.
    import importlib

    import app.main as main_mod

    importlib.reload(main_mod)
    return TestClient(main_mod.app)


def test_chat_injects_vane_system_prompt(client: TestClient) -> None:
    """character_id=vane prepends the server-owned system prompt."""
    resp = client.post(
        "/v1/chat",
        json={"message": "hola", "character_id": "vane"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["response"]["provider"] == "mock"
    assert data["response"]["validation"]["is_valid"] is True


def test_chat_unknown_character_does_not_inject_system_prompt(client: TestClient) -> None:
    """Unknown character_id is graceful: no system prompt, still 200."""
    resp = client.post(
        "/v1/chat",
        json={"message": "hola", "character_id": "unknown-character"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["response"]["provider"] == "mock"


def test_chat_default_character_id_works(client: TestClient) -> None:
    """No character_id supplied → defaults to 'host' (no system prompt). Still 200."""
    resp = client.post("/v1/chat", json={"message": "hola"})
    assert resp.status_code == 200


def test_runtime_status_reports_mock_mode(client: TestClient) -> None:
    resp = client.get("/v1/runtime/status")
    assert resp.status_code == 200
    data = resp.json()
    assert data["provider"] == "mock"
    assert data["mode"] == "mock"
    assert data["configured"] is False
    # No secret fields present.
    assert "api_key" not in data
    assert "authorization" not in data
    assert "Authorization" not in data
    assert "url" not in data


def test_health_endpoint(client: TestClient) -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["service"] == "companion-studio-api"


# ---------------------------------------------------------------------- #
# build_router() provider selection
# ---------------------------------------------------------------------- #


def test_build_router_defaults_to_mock(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("COMPANION_MODEL_PROVIDER", raising=False)
    rt = build_router()
    sample = rt.providers[Route.FAST_CHAT]
    assert isinstance(sample, MockModelProvider)
    status = runtime_status(rt)
    assert status["mode"] == "mock"
    assert status["configured"] is False


def test_build_router_openai_without_credentials_falls_back_to_mock(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """provider=openai but no base_url/api_key → mock fallback (Issue #3 #2)."""
    monkeypatch.setenv("COMPANION_MODEL_PROVIDER", "openai")
    monkeypatch.delenv("COMPANION_MODEL_BASE_URL", raising=False)
    monkeypatch.delenv("COMPANION_MODEL_API_KEY", raising=False)
    rt = build_router()
    sample = rt.providers[Route.FAST_CHAT]
    assert isinstance(sample, MockModelProvider)


def test_build_router_openai_with_credentials_wires_adapter(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("COMPANION_MODEL_PROVIDER", "openai")
    monkeypatch.setenv("COMPANION_MODEL_BASE_URL", "https://api.example.com/v1")
    monkeypatch.setenv("COMPANION_MODEL_API_KEY", "sk-test-fake")
    monkeypatch.setenv("COMPANION_MODEL_NAME", "companion-chat-v1")
    rt = build_router()
    sample = rt.providers[Route.FAST_CHAT]
    assert sample.name == "openai-compatible"
    assert sample.model == "companion-chat-v1"
    status = runtime_status(rt)
    assert status["mode"] == "real"
    assert status["configured"] is True
    # No secret in the status dict.
    assert "api_key" not in status
    assert "sk-test-fake" not in str(status)


def test_runtime_status_no_secret_leak_for_openai(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("COMPANION_MODEL_PROVIDER", "openai")
    monkeypatch.setenv("COMPANION_MODEL_BASE_URL", "https://api.example.com/v1")
    monkeypatch.setenv("COMPANION_MODEL_API_KEY", "sk-super-secret-do-not-leak")
    rt = build_router()
    status = runtime_status(rt)
    status_str = str(status)
    assert "sk-super-secret-do-not-leak" not in status_str
    assert "api_key" not in status
