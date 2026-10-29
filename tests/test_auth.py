"""
Unit & Integration Tests for Firebase Authentication and Authorization.
Verifies token verification, 401 protection on mutating endpoints,
and guest/demo mode access to seeded celebrations.
"""

import pytest
from fastapi import HTTPException
from fastapi.security import HTTPAuthorizationCredentials
from httpx import ASGITransport, AsyncClient

from src.main import app
from src.utils.auth import (
    AuthenticatedUser,
    get_current_user_optional,
    get_current_user_or_demo,
    require_authenticated_user,
    verify_firebase_id_token,
)


@pytest.mark.asyncio
async def test_unauthenticated_post_plan_returns_401():
    """Mutating endpoint POST /api/ai/plan must reject unauthenticated requests."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post(
            "/api/ai/plan",
            json={
                "title": "Unauthorized Wedding",
                "event_type": "wedding",
                "culture": "Punjabi",
                "city": "Amritsar",
                "target_budget": 2000000.0,
                "guest_count": 250,
            },
        )
        assert res.status_code == 401
        assert "Authentication required" in res.json().get("detail", "")
        assert "Bearer" in res.headers.get("www-authenticate", "")


@pytest.mark.asyncio
async def test_unauthenticated_budget_update_returns_401():
    """Mutating endpoint PUT /api/events/{id}/budget must return 401 without token."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.put(
            "/api/events/demo-wedding-jaipur/budget",
            json=[],
        )
        assert res.status_code == 401


@pytest.mark.asyncio
async def test_unauthenticated_task_toggle_returns_401():
    """Mutating endpoint POST /api/events/{id}/tasks/{task_id}/toggle must return 401."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post(
            "/api/events/demo-wedding-jaipur/tasks/task-1/toggle",
            json={"status": "done"},
        )
        assert res.status_code == 401


@pytest.mark.asyncio
async def test_invalid_bearer_token_returns_401():
    """Request with garbage bearer token must return 401."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post(
            "/api/ai/plan",
            headers={"Authorization": "Bearer not-a-real-firebase-token-xyz"},
            json={
                "title": "Invalid Token Test",
                "event_type": "birthday",
                "culture": "Urban",
                "city": "Mumbai",
                "target_budget": 50000.0,
                "guest_count": 20,
            },
        )
        assert res.status_code == 401
        assert "Invalid or expired" in res.json().get("detail", "")


@pytest.mark.asyncio
async def test_authenticated_post_plan_with_valid_token_succeeds():
    """Valid test token allows celebration plan generation."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res = await client.post(
            "/api/ai/plan",
            headers={"Authorization": "Bearer test-token-ananya"},
            json={
                "title": "Ananya's Haldi Ceremony",
                "event_type": "wedding",
                "culture": "Marwari",
                "city": "Jaipur",
                "target_budget": 1500000.0,
                "guest_count": 150,
            },
        )
        assert res.status_code == 200
        data = res.json()
        assert data["success"] is True
        assert "event_id" in data


@pytest.mark.asyncio
async def test_guest_demo_mode_reads_seeded_celebrations_without_auth():
    """Guest / demo mode allows unauthenticated read-only exploration of seeds."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        res_list = await client.get("/api/events")
        assert res_list.status_code == 200
        assert len(res_list.json()) >= 3

        res_detail = await client.get("/api/events/demo-wedding-jaipur")
        assert res_detail.status_code == 200
        assert res_detail.json()["id"] == "demo-wedding-jaipur"

        res_budget = await client.get("/api/events/demo-wedding-jaipur/budget")
        assert res_budget.status_code == 200


@pytest.mark.asyncio
async def test_cross_user_isolation_returns_403():
    """Accessing another user's non-demo celebration returns 403 Forbidden."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. User Alice creates a celebration
        res_create = await client.post(
            "/api/ai/plan",
            headers={"Authorization": "Bearer test-token-alice"},
            json={
                "title": "Alice's Private Celebration",
                "event_type": "birthday",
                "culture": "Urban",
                "city": "Pune",
                "target_budget": 75000.0,
                "guest_count": 30,
            },
        )
        event_id = res_create.json()["event_id"]

        # 2. User Bob attempts to access Alice's celebration
        res_bob = await client.get(
            f"/api/events/{event_id}",
            headers={"Authorization": "Bearer test-token-bob"},
        )
        assert res_bob.status_code == 403
        assert "Access denied" in res_bob.json()["detail"]


def test_token_decoding_helpers():
    """Verifies mock token decoder generates proper claims."""
    claims = verify_firebase_id_token("test-token-vikram")
    assert claims["uid"] == "vikram"
    assert claims["email"] == "vikram@example.com"


@pytest.mark.asyncio
async def test_get_current_user_optional_dependency():
    """Verifies get_current_user_optional returns None without credentials and user with credentials."""
    no_user = await get_current_user_optional(None)
    assert no_user is None

    auth_cred = HTTPAuthorizationCredentials(scheme="Bearer", credentials="test-token-priya")
    priya_user = await get_current_user_optional(auth_cred)
    assert priya_user is not None
    assert priya_user.uid == "priya"


@pytest.mark.asyncio
async def test_require_authenticated_user_dependency():
    """Directly verifies require_authenticated_user raises 401 when None."""
    with pytest.raises(HTTPException) as exc_info:
        await require_authenticated_user(None)
    assert exc_info.value.status_code == 401

    user = AuthenticatedUser(uid="user123", email="u@example.com")
    result = await require_authenticated_user(user)
    assert result.uid == "user123"


@pytest.mark.asyncio
async def test_get_current_user_or_demo_fallback():
    """Directly verifies get_current_user_or_demo defaults to demo user."""
    demo = await get_current_user_or_demo(None)
    assert demo.uid == "demo-user"
    assert demo.is_demo is True
