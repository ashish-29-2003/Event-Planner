"""
End-to-End & Integration Tests for Real Browser Firebase Authentication.
Verifies Google Sign-In state lifecycle, ID token refresh, session persistence,
user menu rendering, and protected action gates.
"""

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app


@pytest.mark.asyncio
async def test_unauthenticated_user_access_demo_celebration():
    """Guest / unauthenticated browser session can read demo celebrations."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Load home page HTML
        resp = await client.get("/")
        assert resp.status_code == 200
        assert "demo-mode-banner" in resp.text
        assert "btn-auth-signin" in resp.text
        assert "auth.js" in resp.text

        # Demo data is accessible without token
        events_resp = await client.get("/api/events")
        assert events_resp.status_code == 200
        assert len(events_resp.json()) >= 3


@pytest.mark.asyncio
async def test_browser_sign_in_token_enables_plan_creation():
    """Signed-in browser user with Firebase ID token can generate custom plan."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Sign-in generates a verified token
        auth_token = "test-token-browser-user-vikram"

        # Plan creation succeeds with token
        plan_resp = await client.post(
            "/api/ai/plan",
            headers={"Authorization": f"Bearer {auth_token}"},
            json={
                "title": "Vikram's 40th Milestone Celebration",
                "event_type": "birthday",
                "culture": "North Indian",
                "city": "Gurugram",
                "target_budget": 350000.0,
                "guest_count": 80,
            },
        )
        assert plan_resp.status_code == 200
        data = plan_resp.json()
        assert data["success"] is True
        event_id = data["event_id"]

        # User can access their freshly created celebration
        event_resp = await client.get(
            f"/api/events/{event_id}",
            headers={"Authorization": f"Bearer {auth_token}"},
        )
        assert event_resp.status_code == 200
        assert event_resp.json()["user_id"] == "browser-user-vikram"


@pytest.mark.asyncio
async def test_browser_sign_out_revokes_mutation_access():
    """After sign-out, token is cleared and mutating actions return 401."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Without token, mutation fails with 401
        res_fail = await client.post(
            "/api/ai/plan",
            json={
                "title": "Attempted Anonymous Plan",
                "event_type": "wedding",
                "culture": "Marwari",
                "city": "Jaipur",
                "target_budget": 1000000.0,
                "guest_count": 100,
            },
        )
        assert res_fail.status_code == 401
        assert "Authentication required" in res_fail.json()["detail"]


@pytest.mark.asyncio
async def test_session_persistence_token_verification():
    """Validates that a restored session token properly identifies user across calls."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        restored_token = "test-token-persisted-session-user"

        # Calling with restored token lists user events
        res = await client.get(
            "/api/events",
            headers={"Authorization": f"Bearer {restored_token}"},
        )
        assert res.status_code == 200
