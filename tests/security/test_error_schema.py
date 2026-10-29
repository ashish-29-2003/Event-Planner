"""
Uniform Error Response Schema Tests for Samaroh (समारोह).
Verifies that all API error conditions (400, 401, 404, 413, 422, 500)
conform to the standardized JSON error contract:
{"error": {"code": str, "message": str, "request_id": str}}
while preserving backward-compatible 'detail' for client compatibility.
"""

from fastapi.testclient import TestClient

from src.main import create_app

client = TestClient(create_app())


def test_401_error_schema():
    """Verify that 401 Unauthorized returns standard error schema."""
    resp = client.post("/api/events/non-existent/guests", json={"name": "Aarav", "family_side": "groom"})
    assert resp.status_code == 401
    body = resp.json()

    assert "error" in body
    err = body["error"]
    assert err["code"] == "UNAUTHENTICATED"
    assert "Authentication required" in err["message"]
    assert "request_id" in err
    assert len(err["request_id"]) > 0

    # Ensure backwards compatibility
    assert "detail" in body
    assert "Authentication required" in body["detail"]


def test_404_error_schema():
    """Verify that 404 Not Found returns standard error schema with token."""
    resp = client.get(
        "/api/events/non-existent-celebration-id-12345",
        headers={"Authorization": "Bearer test-token-alice"},
    )
    assert resp.status_code == 404
    body = resp.json()

    assert "error" in body
    assert body["error"]["code"] == "NOT_FOUND"
    assert "request_id" in body["error"]


def test_422_validation_error_schema():
    """Verify that 422 Unprocessable Entity returns standard error schema."""
    resp = client.post(
        "/api/events/demo-wedding-jaipur/guests",
        headers={"Authorization": "Bearer test-token-demo"},
        json={"invalid_key": "violates extra='forbid'"},
    )
    assert resp.status_code == 422
    body = resp.json()

    assert "error" in body
    err = body["error"]
    assert err["code"] == "VALIDATION_ERROR"
    assert "request_id" in err
    assert "details" in err
    assert isinstance(err["details"], list)


def test_413_payload_too_large_error_schema():
    """Verify that 413 Payload Too Large returns standard error schema."""
    oversized = "a" * (1024 * 1024 + 50)
    resp = client.post(
        "/api/ai/plan",
        headers={"Authorization": "Bearer test-token-alice", "Content-Length": str(len(oversized))},
        content=oversized,
    )
    assert resp.status_code == 413
    body = resp.json()

    assert "error" in body
    assert body["error"]["code"] == "PAYLOAD_TOO_LARGE"
    assert "1 MB" in body["error"]["message"]
    assert "request_id" in body["error"]
