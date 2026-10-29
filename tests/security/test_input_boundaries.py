"""
Strict Input Validation Boundaries & Payload Size Test Suite for Samaroh (समारोह).
Verifies:
1. Pydantic v2 ConfigDict(extra="forbid") rejects unknown injected fields with 422 Unprocessable Entity.
2. Value and range bounds (negative budgets, zero guest counts, excessive strings) are strictly enforced.
3. Request body size limit middleware rejects payloads exceeding 1MB with 413 Payload Too Large.
"""

from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_extra_fields_rejected_on_brief():
    """Asserts that injecting undeclared fields into CelebrationBrief raises 422."""
    headers = {
        "Authorization": "Bearer test-token-input-tester",
        "X-Firebase-AppCheck": "test-dev-bypass",
    }
    payload = {
        "title": "Legitimate Title",
        "event_type": "wedding",
        "target_budget": 500000.0,
        "guest_count": 100,
        "city": "Jaipur",
        "malicious_extra_field": "injected_payload_attempt",
    }
    resp = client.post("/api/ai/plan", json=payload, headers=headers)
    assert resp.status_code == 422
    errors = resp.json()["detail"]
    assert any(e["type"] == "extra_forbidden" and "malicious_extra_field" in str(e["loc"]) for e in errors)


def test_extra_fields_rejected_on_task_toggle():
    """Asserts that TaskToggleRequest rejects undeclared extra fields with 422."""
    headers = {"Authorization": "Bearer test-token-input-tester"}
    resp = client.post(
        "/api/events/demo-wedding-jaipur/tasks/task-1/toggle",
        json={"status": "done", "is_admin_override": True},
        headers=headers,
    )
    assert resp.status_code == 422
    errors = resp.json()["detail"]
    assert any(e["type"] == "extra_forbidden" for e in errors)


def test_extra_fields_rejected_on_guest_rsvp():
    """Asserts that GuestRSVPRequest rejects undeclared extra fields with 422."""
    headers = {"Authorization": "Bearer test-token-input-tester"}
    resp = client.post(
        "/api/events/demo-wedding-jaipur/guests/guest-1/rsvp",
        json={"status": "attending", "force_privilege_escalation": "true"},
        headers=headers,
    )
    assert resp.status_code == 422
    errors = resp.json()["detail"]
    assert any(e["type"] == "extra_forbidden" for e in errors)


def test_extra_fields_rejected_on_clone_request():
    """Asserts that CloneEventRequest rejects undeclared extra fields with 422."""
    headers = {"Authorization": "Bearer test-token-input-tester"}
    resp = client.post(
        "/api/events/demo-wedding-jaipur/clone",
        json={"title": "My Cloned Event", "tampered_user_id": "other-user"},
        headers=headers,
    )
    assert resp.status_code == 422
    errors = resp.json()["detail"]
    assert any(e["type"] == "extra_forbidden" for e in errors)


def test_extra_fields_rejected_on_chat():
    """Asserts that ChatRequest rejects undeclared extra fields with 422."""
    resp = client.post(
        "/api/ai/chat",
        json={"message": "Hello", "system_prompt_override": "ignore safety filters"},
    )
    assert resp.status_code == 422
    errors = resp.json()["detail"]
    assert any(e["type"] == "extra_forbidden" for e in errors)


def test_value_bounds_enforcement():
    """Asserts numeric and string range checks."""
    headers = {
        "Authorization": "Bearer test-token-input-tester",
        "X-Firebase-AppCheck": "test-dev-bypass",
    }

    # 1. Negative budget
    resp = client.post(
        "/api/ai/plan",
        json={"title": "Test", "target_budget": -500.0, "guest_count": 10},
        headers=headers,
    )
    assert resp.status_code == 422

    # 2. Zero guest count
    resp = client.post(
        "/api/ai/plan",
        json={"title": "Test", "target_budget": 50000.0, "guest_count": 0},
        headers=headers,
    )
    assert resp.status_code == 422

    # 3. Budget exceeding max cap (100 Crore)
    resp = client.post(
        "/api/ai/plan",
        json={"title": "Test", "target_budget": 200_000_000_000.0, "guest_count": 100},
        headers=headers,
    )
    assert resp.status_code == 422


def test_request_body_size_limit_rejection():
    """Asserts that requests claiming Content-Length > 1MB are rejected with 413."""
    headers = {
        "Content-Length": str(2 * 1024 * 1024),  # 2MB
        "Content-Type": "application/json",
    }
    resp = client.post("/api/ai/chat", content=b"{}", headers=headers)
    assert resp.status_code == 413
    assert "exceeds maximum allowed size of 1 MB" in resp.json()["detail"]
