"""
Comprehensive IDOR & Tenant Authorization Test Suite for Samaroh (समारोह).
Verifies:
1. Complete isolation across every entity route (User Beta cannot read, edit, delete, or export User Alpha's celebration).
2. Nested resource mismatch protection (updating guest/task through the wrong parent celebration ID fails).
3. Per-user quota limits prevent unbounded persistence exhaustion attacks.
4. Non-existent resources return 404 cleanly.
"""

from fastapi.testclient import TestClient

from src.main import app
from src.models.guest import GuestAffiliation, GuestItem, RSVPStatus
from src.models.timeline import TaskItem
from src.services.storage_service import storage_service

client = TestClient(app)


def test_complete_idor_endpoint_matrix():
    """
    Exhaustively verifies IDOR protection across all celebration sub-resources.
    User Alpha creates a private celebration with full data.
    User Beta attempts every single operation and receives 403 Forbidden.
    """
    event_id = "event-sec-idor-alpha-1"
    storage_service._events[event_id] = {
        "id": event_id,
        "title": "Alpha Confidential Wedding",
        "user_id": "user-alpha",
        "event_type": "wedding",
        "city": "Udaipur",
    }
    storage_service._budgets[event_id] = []
    storage_service._tasks[event_id] = [
        TaskItem(
            id="task-sec-1",
            title="Book Mandap",
            description="Book heritage mandap decorator",
            phase="Phase 1",
            due_date="2026-11-01",
        )
    ]
    storage_service._vendors[event_id] = []
    storage_service._ideas[event_id] = []
    storage_service._guests[event_id] = [
        GuestItem(
            id="guest-sec-1",
            name="Alpha VIP Guest",
            affiliation=GuestAffiliation.FAMILY,
            rsvp_status=RSVPStatus.PENDING,
        )
    ]

    beta_headers = {"Authorization": "Bearer test-token-user-beta"}

    endpoints_to_test = [
        ("GET", f"/api/events/{event_id}", None),
        ("DELETE", f"/api/events/{event_id}", None),
        ("POST", f"/api/events/{event_id}/clone", {}),
        ("GET", f"/api/events/{event_id}/budget", None),
        ("PUT", f"/api/events/{event_id}/budget", []),
        ("GET", f"/api/events/{event_id}/tasks", None),
        ("POST", f"/api/events/{event_id}/tasks/task-sec-1/toggle", {"status": "done"}),
        ("GET", f"/api/events/{event_id}/vendors", None),
        ("GET", f"/api/events/{event_id}/ideas", None),
        ("GET", f"/api/events/{event_id}/guests", None),
        (
            "POST",
            f"/api/events/{event_id}/guests",
            {
                "id": "g-new-beta",
                "name": "Intruder Beta",
                "affiliation": "friend",
                "rsvp_status": "pending",
            },
        ),
        ("POST", f"/api/events/{event_id}/guests/guest-sec-1/rsvp", {"status": "attending"}),
        ("GET", f"/api/export/{event_id}/calendar", None),
        ("GET", f"/api/export/{event_id}/next-milestone-link", None),
        ("GET", f"/api/export/{event_id}/summary", None),
    ]

    for method, path, payload in endpoints_to_test:
        if method == "GET":
            resp = client.get(path, headers=beta_headers)
        elif method == "DELETE":
            resp = client.delete(path, headers=beta_headers)
        elif method == "POST":
            resp = client.post(path, json=payload, headers=beta_headers)
        elif method == "PUT":
            resp = client.put(path, json=payload, headers=beta_headers)

        assert (
            resp.status_code == 403
        ), f"IDOR Vulnerability Detected! {method} {path} returned {resp.status_code} instead of 403"

    # Cleanup
    storage_service.delete_event(event_id)


def test_nested_resource_mismatch_protection():
    """
    Tests that operating on a child entity (guest/task) through the wrong parent event ID returns 404.
    """
    alpha_headers = {"Authorization": "Bearer test-token-user-nested"}

    event_1 = "event-nested-1"
    event_2 = "event-nested-2"

    storage_service._events[event_1] = {"id": event_1, "title": "E1", "user_id": "user-nested"}
    storage_service._events[event_2] = {"id": event_2, "title": "E2", "user_id": "user-nested"}

    # Event 1 has task-1, Event 2 has task-2
    storage_service._tasks[event_1] = [
        TaskItem(id="task-e1", title="T1", description="D1", phase="P1")
    ]
    storage_service._tasks[event_2] = [
        TaskItem(id="task-e2", title="T2", description="D2", phase="P1")
    ]

    # Event 1 has guest-1, Event 2 has guest-2
    storage_service._guests[event_1] = [
        GuestItem(id="g-e1", name="G1", affiliation=GuestAffiliation.FAMILY)
    ]
    storage_service._guests[event_2] = [
        GuestItem(id="g-e2", name="G2", affiliation=GuestAffiliation.FAMILY)
    ]

    # Attempt to toggle task-e2 via event_1 -> 404 Task not found
    resp = client.post(
        f"/api/events/{event_1}/tasks/task-e2/toggle",
        json={"status": "done"},
        headers=alpha_headers,
    )
    assert resp.status_code == 404
    assert "Task not found" in resp.json()["detail"]

    # Attempt to update RSVP for g-e2 via event_1 -> 404 Guest not found
    resp = client.post(
        f"/api/events/{event_1}/guests/g-e2/rsvp",
        json={"status": "attending"},
        headers=alpha_headers,
    )
    assert resp.status_code == 404
    assert "Guest not found" in resp.json()["detail"]

    # Cleanup
    storage_service.delete_event(event_1)
    storage_service.delete_event(event_2)


def test_per_user_celebration_quota_enforcement():
    """
    Tests that a user cannot exceed the maximum allowed celebrations quota (20).
    """
    user_headers = {"Authorization": "Bearer test-token-quota-user"}
    user_id = "quota-user"

    # Pre-populate user with 20 celebrations
    created_ids = []
    for i in range(20):
        ev_id = f"event-quota-{i}"
        storage_service._events[ev_id] = {
            "id": ev_id,
            "title": f"Celebration {i}",
            "user_id": user_id,
        }
        created_ids.append(ev_id)

    # Attempting to clone should be rejected with 400 Bad Request
    resp = client.post(
        "/api/events/demo-wedding-jaipur/clone",
        json={"title": "Over Quota Clone"},
        headers=user_headers,
    )
    assert resp.status_code == 400
    assert "Celebration quota reached" in resp.json()["detail"]

    # Attempting to generate a plan should also be rejected with 400
    resp_plan = client.post(
        "/api/ai/plan",
        json={
            "title": "Over Quota Plan",
            "event_type": "birthday",
            "target_budget": 50000.0,
            "guest_count": 25,
            "city": "Jaipur",
        },
        headers={**user_headers, "X-Firebase-AppCheck": "test-dev-bypass"},
    )
    assert resp_plan.status_code == 400
    assert "Celebration quota reached" in resp_plan.json()["detail"]

    # Cleanup
    for ev_id in created_ids:
        storage_service.delete_event(ev_id)
