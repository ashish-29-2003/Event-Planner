"""
HMAC Signed Share & Export Link Safety Tests for Samaroh (समारोह).
Verifies:
1. Generation and constant-time HMAC-SHA256 signature verification.
2. Tamper-resistance and expiration boundary enforcement.
3. Access control: Owners can create share tokens; token holders can access public summary/calendar without credentials; invalid tokens are rejected with 403.
"""

import time

from fastapi.testclient import TestClient

from src.main import create_app
from src.services.storage_service import storage_service
from src.utils.tokens import generate_share_token, verify_share_token

client = TestClient(create_app())


def test_share_token_generation_and_verification():
    """Verify that a freshly generated share token verifies correctly."""
    token = generate_share_token("evt-test-123", ttl_seconds=3600)
    assert verify_share_token("evt-test-123", token)


def test_tampered_token_rejected():
    """Verify that altering the signature or event ID invalidates the token."""
    token = generate_share_token("evt-test-123", ttl_seconds=3600)

    # Different event ID
    assert not verify_share_token("evt-other-456", token)

    # Tampered signature
    tampered = token[:-4] + "ffff"
    assert not verify_share_token("evt-test-123", tampered)

    # Malformed token
    assert not verify_share_token("evt-test-123", "invalid-token-string")


def test_expired_token_rejected():
    """Verify that tokens beyond expiration time are rejected."""
    # Token with 10s TTL
    token = generate_share_token("evt-test-exp", ttl_seconds=10)
    now = time.time()
    # Verified at now + 20s
    assert not verify_share_token("evt-test-exp", token, current_time=now + 20)


def test_share_token_api_workflow_end_to_end():
    """
    E2E test:
    - User creates private celebration
    - Non-owner without token gets 403
    - Owner creates share-token via POST /api/export/{id}/share-token
    - Unauthenticated guest accesses summary and calendar with token -> 200 OK
    - Guest with invalid token gets 403
    """
    owner_id = "user-deepa"
    event_id = storage_service.clone_event(
        source_event_id="demo-wedding-jaipur",
        new_user_id=owner_id,
        new_title="Deepa & Rohan Sangeet",
    )

    # 1. Unauthenticated or stranger request without token -> 403
    resp_blocked = client.get(
        f"/api/export/{event_id}/summary",
        headers={"Authorization": "Bearer test-token-stranger"},
    )
    assert resp_blocked.status_code == 403

    # 2. Owner generates share token
    resp_token = client.post(
        f"/api/export/{event_id}/share-token",
        headers={"Authorization": f"Bearer test-token-{owner_id}"},
    )
    assert resp_token.status_code == 200
    token_data = resp_token.json()
    token = token_data["token"]
    assert token

    # 3. Anonymous caller accesses summary using valid token -> 200 OK
    resp_shared = client.get(f"/api/export/{event_id}/summary?token={token}")
    assert resp_shared.status_code == 200
    assert resp_shared.json()["event"]["title"] == "Deepa & Rohan Sangeet"

    # 4. Anonymous caller accesses calendar .ics using valid token -> 200 OK
    resp_cal = client.get(f"/api/export/{event_id}/calendar?token={token}")
    assert resp_cal.status_code == 200
    assert "text/calendar" in resp_cal.headers.get("content-type", "")

    # 5. Anonymous caller with bad token -> 403
    resp_invalid = client.get(f"/api/export/{event_id}/summary?token=9999999999.invalidbadhex")
    assert resp_invalid.status_code == 403
    assert "Invalid or expired share token" in resp_invalid.json()["detail"]
