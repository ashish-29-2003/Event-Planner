import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_404_error_envelope_structure():
    """Non-existent resource returns standardized error envelope without silent empty response."""
    res = client.get("/api/events/non-existent-celebration-id-12345")
    assert res.status_code == 404
    data = res.json()
    assert "error" in data
    assert data["error"]["code"] == "NOT_FOUND"
    assert "Celebration not found" in data["error"]["message"]
    assert "request_id" in data["error"]
    assert "X-Request-ID" in res.headers


def test_validation_error_envelope_structure():
    """Validation errors on POST endpoints return structured VALIDATION_ERROR envelope."""
    # Send empty body to /api/ai/plan which requires title, event_type, etc.
    res = client.post(
        "/api/ai/plan",
        headers={"Authorization": "Bearer test-token-valid-user"},
        json={"title": "Incomplete"},
    )
    assert res.status_code == 422
    data = res.json()
    assert "error" in data
    assert data["error"]["code"] == "VALIDATION_ERROR"
    assert "request_id" in data["error"]


def test_demo_resource_not_found():
    """Missing subcollection returns 404 error envelope."""
    res = client.get("/api/events/demo-unknown-plan/budget")
    assert res.status_code == 404
    data = res.json()
    assert data["error"]["code"] == "NOT_FOUND"
