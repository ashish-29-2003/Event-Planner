"""
Route Authentication Guards & IDOR Test Suite for Samaroh (समारोह).
Validates that:
1. 100% of application routes are covered by auth guards or belong to the explicit public allowlist.
2. Mutating routes strictly require a verified Bearer token (401 without token, 401 with invalid token).
3. Demo celebrations ('demo-*') are readable by anyone, but 100% read-only against mutations (403 Forbidden).
4. Private celebrations enforce tenant isolation and IDOR protection (403 for non-owners).
5. Celebration cloning operates safely across demo templates and user-owned events.
"""

import inspect
from unittest.mock import patch

from fastapi.routing import APIRoute
from fastapi.testclient import TestClient

from src.main import app
from src.services.storage_service import storage_service
from src.utils.auth import (
    get_current_user_optional,
    get_current_user_or_demo,
    require_authenticated_user,
)

client = TestClient(app)

PUBLIC_ALLOWLIST = {
    "/api/health",
    "/health",
    "/",
    "/api/docs",
    "/api/redoc",
    "/api/openapi.json",
    "/docs/oauth2-redirect",
}

AUTH_DEPENDENCIES = {
    require_authenticated_user,
    get_current_user_or_demo,
    get_current_user_optional,
}


def _collect_all_api_routes(target) -> list[APIRoute]:
    """Recursively collects all APIRoutes across FastAPI app, mounts, and IncludedRouters."""
    collected = []
    routes = getattr(target, "routes", [])
    for r in routes:
        if isinstance(r, APIRoute):
            collected.append(r)
        elif hasattr(r, "original_router") and r.original_router:
            collected.extend(_collect_all_api_routes(r.original_router))
        elif hasattr(r, "app") and hasattr(r.app, "routes"):
            collected.extend(_collect_all_api_routes(r.app))
    return collected


def _get_route_auth_dependencies(route: APIRoute) -> list:
    """Extracts all auth dependencies attached to an APIRoute directly or via parameters."""
    deps = []
    # Check route.dependencies
    for d in getattr(route, "dependencies", []):
        if d.dependency in AUTH_DEPENDENCIES:
            deps.append(d.dependency)
    # Check endpoint parameters
    sig = inspect.signature(route.endpoint)
    for param in sig.parameters.values():
        default = param.default
        if hasattr(default, "dependency") and default.dependency in AUTH_DEPENDENCIES:
            deps.append(default.dependency)
    return deps


def test_every_route_has_auth_guard_or_is_allowlisted():
    """
    Automated architectural compliance assertion:
    Iterates every registered route in the FastAPI application and verifies
    that non-allowlisted routes have an explicit authentication dependency.
    """
    all_api_routes = _collect_all_api_routes(app)
    unguarded_routes = []
    total_guarded_routes = 0

    for route in all_api_routes:
        path = route.path
        if path in PUBLIC_ALLOWLIST or path.startswith("/static"):
            continue

        auth_deps = _get_route_auth_dependencies(route)
        if not auth_deps:
            unguarded_routes.append(f"{list(route.methods)} {path}")
        else:
            total_guarded_routes += 1

    assert (
        not unguarded_routes
    ), f"Found unguarded routes without authentication dependencies: {unguarded_routes}"
    assert (
        total_guarded_routes >= 15
    ), f"Expected at least 15 protected routes, found {total_guarded_routes}"


def test_mutating_routes_require_authentication():
    """Asserts that mutating endpoints return 401 when called without a Bearer token."""
    # 1. AI Plan generation
    resp = client.post("/api/ai/plan", json={"event_type": "wedding"})
    assert resp.status_code == 401

    # 2. AI Budget Rebalance
    resp = client.post(
        "/api/ai/rebalance-budget",
        json={
            "total_budget": 1000000,
            "changed_category": "venue",
            "new_category_cost": 400000,
            "current_allocations": [],
        },
    )
    assert resp.status_code == 401

    # 3. Budget update
    resp = client.put("/api/events/demo-wedding-jaipur/budget", json=[])
    assert resp.status_code == 401

    # 4. Task status toggle
    resp = client.post(
        "/api/events/demo-wedding-jaipur/tasks/t1/toggle",
        json={"status": "done"},
    )
    assert resp.status_code == 401

    # 5. Add guest
    resp = client.post(
        "/api/events/demo-wedding-jaipur/guests",
        json={
            "id": "g-new-test",
            "name": "Aarav Sharma",
            "affiliation": "family",
            "rsvp_status": "pending",
        },
    )
    assert resp.status_code == 401

    # 6. Delete celebration
    resp = client.delete("/api/events/demo-wedding-jaipur")
    assert resp.status_code == 401

    # 7. Clone celebration
    resp = client.post("/api/events/demo-wedding-jaipur/clone")
    assert resp.status_code == 401


def test_invalid_token_rejected_with_401():
    """Asserts that requests with forged or invalid Bearer tokens receive 401 Unauthorized."""
    headers = {"Authorization": "Bearer invalid-garbage-token-12345"}
    with patch(
        "firebase_admin.auth.verify_id_token",
        side_effect=ValueError("Token verification failed: invalid signature"),
    ):
        resp = client.post(
            "/api/ai/plan",
            json={"event_type": "wedding"},
            headers=headers,
        )
        assert resp.status_code == 401
        assert "Invalid or expired authentication token" in resp.text


def test_demo_celebrations_are_strictly_read_only():
    """
    Asserts that mutating actions against demo celebrations are strictly rejected with 403 Forbidden,
    even when called by an authenticated user.
    """
    auth_headers = {"Authorization": "Bearer test-token-any-user"}

    # 1. Attempt to delete demo celebration
    resp = client.delete("/api/events/demo-wedding-jaipur", headers=auth_headers)
    assert resp.status_code == 403
    assert "Demo celebrations are read-only templates" in resp.json()["detail"]

    # 2. Attempt to modify demo budget
    resp = client.put(
        "/api/events/demo-wedding-jaipur/budget",
        json=[],
        headers=auth_headers,
    )
    assert resp.status_code == 403
    assert "Demo celebrations are read-only templates" in resp.json()["detail"]

    # 3. Attempt to toggle demo task
    resp = client.post(
        "/api/events/demo-wedding-jaipur/tasks/task-1/toggle",
        json={"status": "done"},
        headers=auth_headers,
    )
    assert resp.status_code == 403
    assert "Demo celebrations are read-only templates" in resp.json()["detail"]

    # 4. Attempt to add guest to demo celebration
    resp = client.post(
        "/api/events/demo-wedding-jaipur/guests",
        json={
            "id": "guest-test-1",
            "name": "Intruder Guest",
            "affiliation": "bride_side",
            "rsvp_status": "pending",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 403
    assert "Demo celebrations are read-only templates" in resp.json()["detail"]

    # 5. Attempt to update RSVP in demo celebration
    resp = client.post(
        "/api/events/demo-wedding-jaipur/guests/guest-1/rsvp",
        json={"status": "attending"},
        headers=auth_headers,
    )
    assert resp.status_code == 403
    assert "Demo celebrations are read-only templates" in resp.json()["detail"]


def test_private_celebration_idor_enforcement():
    """
    Tests IDOR tenant isolation:
    - User A creates/owns a celebration.
    - User B cannot read, modify, export, or delete User A's celebration.
    """
    # Create private event for user-alpha
    event_id = "event-priv-alpha-99"
    storage_service._events[event_id] = {
        "id": event_id,
        "title": "Alpha Private Sangeet",
        "user_id": "user-alpha",
        "event_type": "sangeet",
        "city": "Jaipur",
    }
    storage_service._budgets[event_id] = []
    storage_service._tasks[event_id] = []
    storage_service._vendors[event_id] = []
    storage_service._ideas[event_id] = []
    storage_service._guests[event_id] = []

    user_beta_headers = {"Authorization": "Bearer test-token-user-beta"}
    user_alpha_headers = {"Authorization": "Bearer test-token-user-alpha"}

    # 1. User B tries to read User A's celebration -> 403
    resp = client.get(f"/api/events/{event_id}", headers=user_beta_headers)
    assert resp.status_code == 403

    # 2. User B tries to read User A's budget -> 403
    resp = client.get(f"/api/events/{event_id}/budget", headers=user_beta_headers)
    assert resp.status_code == 403

    # 3. User B tries to update User A's budget -> 403
    resp = client.put(f"/api/events/{event_id}/budget", json=[], headers=user_beta_headers)
    assert resp.status_code == 403

    # 4. User B tries to read User A's tasks -> 403
    resp = client.get(f"/api/events/{event_id}/tasks", headers=user_beta_headers)
    assert resp.status_code == 403

    # 5. User B tries to read User A's export summary -> 403
    resp = client.get(f"/api/export/{event_id}/summary", headers=user_beta_headers)
    assert resp.status_code == 403

    # 6. User B tries to export User A's calendar -> 403
    resp = client.get(f"/api/export/{event_id}/calendar", headers=user_beta_headers)
    assert resp.status_code == 403

    # 7. User B tries to clone User A's private celebration -> 403
    resp = client.post(f"/api/events/{event_id}/clone", headers=user_beta_headers)
    assert resp.status_code == 403

    # 8. User B tries to delete User A's celebration -> 403
    resp = client.delete(f"/api/events/{event_id}", headers=user_beta_headers)
    assert resp.status_code == 403

    # 9. User A (owner) reads their own celebration -> 200
    resp = client.get(f"/api/events/{event_id}", headers=user_alpha_headers)
    assert resp.status_code == 200
    assert resp.json()["title"] == "Alpha Private Sangeet"

    # 10. User A successfully deletes their celebration -> 200
    resp = client.delete(f"/api/events/{event_id}", headers=user_alpha_headers)
    assert resp.status_code == 200
    assert resp.json()["deleted"] == event_id


def test_clone_demo_celebration_to_user():
    """
    Tests cloning a public demo celebration into an authenticated user's private space.
    """
    user_headers = {"Authorization": "Bearer test-token-cloner-user"}
    resp = client.post(
        "/api/events/demo-wedding-jaipur/clone",
        json={"title": "My Custom Royal Wedding"},
        headers=user_headers,
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["success"] is True
    new_event_id = data["event_id"]
    assert new_event_id.startswith("event-")

    # Cloner can now read the newly cloned celebration
    read_resp = client.get(f"/api/events/{new_event_id}", headers=user_headers)
    assert read_resp.status_code == 200
    assert read_resp.json()["title"] == "My Custom Royal Wedding"
    assert read_resp.json()["user_id"] == "cloner-user"

    # Clean up
    del_resp = client.delete(f"/api/events/{new_event_id}", headers=user_headers)
    assert del_resp.status_code == 200
