import pytest
from fastapi.testclient import TestClient

from src.config import settings
from src.main import app

client = TestClient(app)


def test_api_me_unauthenticated_returns_401():
    """GET /api/me without Bearer token must return HTTP 401."""
    res = client.get("/api/me")
    assert res.status_code == 401
    data = res.json()
    assert "error" in data or "detail" in data


def test_api_me_mock_token_in_production_returns_401(monkeypatch):
    """GET /api/me with test/mock token in production must be rejected with 401."""
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    monkeypatch.setattr(settings, "ENABLE_AUTH_ENFORCEMENT", True)
    headers = {"Authorization": "Bearer test-token-google-user-123"}
    res = client.get("/api/me", headers=headers)
    assert res.status_code == 401


def test_demo_celebration_with_mock_token_in_production_succeeds(monkeypatch):
    """
    Public demo celebration reads must NEVER fail with 401 even if client sends
    a stale/mock Bearer token in production.
    """
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    headers = {"Authorization": "Bearer test-token-google-user-123"}

    # Test all 3 demo celebrations
    demo_ids = ["demo-wedding-jaipur", "demo-birthday-blr", "demo-community-delhi"]
    for demo_id in demo_ids:
        res = client.get(f"/api/events/{demo_id}", headers=headers)
        assert res.status_code == 200, f"Failed on {demo_id}: {res.text}"
        data = res.json()
        assert data["id"] == demo_id
        assert "title" in data

        # Sub-resources
        b_res = client.get(f"/api/events/{demo_id}/budget", headers=headers)
        assert b_res.status_code == 200, f"Budget failed on {demo_id}: {b_res.text}"
        assert isinstance(b_res.json(), list)

        t_res = client.get(f"/api/events/{demo_id}/tasks", headers=headers)
        assert t_res.status_code == 200, f"Tasks failed on {demo_id}: {t_res.text}"
        assert isinstance(t_res.json(), list)

        v_res = client.get(f"/api/events/{demo_id}/vendors", headers=headers)
        assert v_res.status_code == 200, f"Vendors failed on {demo_id}: {v_res.text}"
        assert isinstance(v_res.json(), list)


def test_private_event_with_invalid_token_is_forbidden(monkeypatch):
    """Private event reads must not leak to mock/anonymous users."""
    monkeypatch.setattr(settings, "ENVIRONMENT", "production")
    headers = {"Authorization": "Bearer test-token-google-user-123"}
    res = client.get("/api/events/private-celebration-999", headers=headers)
    assert res.status_code in (403, 404)
