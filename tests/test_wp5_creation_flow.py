import pytest
from fastapi.testclient import TestClient

from src.main import app

client = TestClient(app)


def test_unauthenticated_guest_can_create_and_read_celebration_plan():
    """
    Unauthenticated guests can generate a custom celebration plan without 401 Unauthorized,
    and immediately read the created celebration and all its subcollections.
    """
    brief_data = {
        "title": "Priya & Siddharth's Sangeet Night",
        "event_type": "wedding",
        "culture": "Punjabi",
        "city": "Amritsar",
        "target_budget": 1200000.0,
        "guest_count": 220,
        "target_date": "2026-11-25",
        "language": "en",
        "notes": "Traditional dhol and vibrant decor",
    }

    # 1. Create plan without Authorization header via draft mode endpoint
    res_create = client.post("/api/ai/plan/draft", json=brief_data)
    assert res_create.status_code == 200, f"Failed creation: {res_create.text}"
    create_data = res_create.json()
    assert create_data["success"] is True
    assert "event_id" in create_data
    event_id = create_data["event_id"]
    assert event_id.startswith("event-")

    # 2. Read created celebration master record as guest
    res_event = client.get(f"/api/events/{event_id}")
    assert res_event.status_code == 200
    ev = res_event.json()
    assert ev["title"] == "Priya & Siddharth's Sangeet Night"
    assert ev["city"] == "Amritsar"
    assert ev["target_budget"] == 1200000.0

    # 3. Read subcollections as guest
    res_b = client.get(f"/api/events/{event_id}/budget")
    assert res_b.status_code == 200
    budgets = res_b.json()
    assert isinstance(budgets, list)
    assert len(budgets) == 6
    assert round(sum(b["estimated_cost"] for b in budgets), 2) == 1200000.0

    res_t = client.get(f"/api/events/{event_id}/tasks")
    assert res_t.status_code == 200
    tasks = res_t.json()
    assert isinstance(tasks, list)
    assert len(tasks) == 6

    res_v = client.get(f"/api/events/{event_id}/vendors")
    assert res_v.status_code == 200
    vendors = res_v.json()
    assert isinstance(vendors, list)
    assert len(vendors) == 4

    res_i = client.get(f"/api/events/{event_id}/ideas")
    assert res_i.status_code == 200
    ideas = res_i.json()
    assert isinstance(ideas, list)
    assert len(ideas) == 6


def test_authenticated_user_plan_creation_persists_under_user_uid():
    """Authenticated users have their celebrations stored under their user ID."""
    brief_data = {
        "title": "Vikram's 50th Milestone",
        "event_type": "birthday",
        "culture": "Urban",
        "city": "Mumbai",
        "target_budget": 450000.0,
        "guest_count": 60,
        "target_date": "2026-12-10",
    }
    headers = {"Authorization": "Bearer test-token-vikram-owner"}
    res = client.post("/api/ai/plan", headers=headers, json=brief_data)
    assert res.status_code == 200
    data = res.json()
    event_id = data["event_id"]

    # Owner can read
    res_read = client.get(f"/api/events/{event_id}", headers=headers)
    assert res_read.status_code == 200
    assert res_read.json()["title"] == "Vikram's 50th Milestone"
