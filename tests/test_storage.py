"""
Unit & Integration Tests for Storage Service and Firestore Repository.
Verifies data persistence, seed loading, restart survival, and Guest management.
"""

from unittest.mock import patch

import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app
from src.models.event import CelebrationBrief, EventType
from src.models.guest import GuestAffiliation, GuestItem, RSVPStatus
from src.services.gemini_service import gemini_service
from src.services.storage_service import (
    FirestoreStorageService,
    InMemoryStorageService,
)


def test_in_memory_storage_seeds_initialized():
    """Seed celebrations must be available on initialization."""
    store = InMemoryStorageService(persistence_path=None)
    events = store.list_events("demo-user")
    assert len(events) >= 3
    demo_ids = [e["id"] for e in events]
    assert "demo-wedding-jaipur" in demo_ids
    assert "demo-birthday-blr" in demo_ids
    assert "demo-community-delhi" in demo_ids

    # Check subcollections
    budgets = store.get_budget_items("demo-wedding-jaipur")
    assert len(budgets) > 0
    tasks = store.get_tasks("demo-wedding-jaipur")
    assert len(tasks) > 0
    vendors = store.get_vendors("demo-wedding-jaipur")
    assert len(vendors) > 0
    guests = store.get_guests("demo-wedding-jaipur")
    assert len(guests) >= 2


@pytest.mark.asyncio
async def test_storage_data_persists_across_restart(tmp_path):
    """Verifies that saved events survive storage instance re-initialization."""
    persist_file = tmp_path / "test_store.json"
    store1 = InMemoryStorageService(persistence_path=persist_file)

    brief = CelebrationBrief(
        title="Persisted Sangeet Night",
        event_type=EventType.WEDDING,
        culture="Punjabi",
        city="Delhi",
        target_budget=1200000.0,
        guest_count=180,
    )
    plan, _ = await gemini_service.generate_master_plan(brief)
    event_id = store1.create_event_from_plan(brief, plan, user_id="user-persist")

    # Add a guest
    guest = GuestItem(
        id="g-101",
        name="Harpreet Singh",
        affiliation=GuestAffiliation.FAMILY,
        rsvp_status=RSVPStatus.ATTENDING,
        plus_ones=2,
    )
    store1.add_guest(event_id, guest)

    # Simulate restart by instantiating a new service reading from same file
    store2 = InMemoryStorageService(persistence_path=persist_file)
    restored_event = store2.get_event(event_id)
    assert restored_event is not None
    assert restored_event["title"] == "Persisted Sangeet Night"
    assert restored_event["user_id"] == "user-persist"

    restored_guests = store2.get_guests(event_id)
    assert any(g.name == "Harpreet Singh" for g in restored_guests)


def test_firestore_adapter_fallback():
    """Verifies FirestoreStorageService operates with fallback when Firestore is offline."""
    fallback = InMemoryStorageService(persistence_path=None)
    with patch("firebase_admin.firestore.client", side_effect=Exception("No GCP connection")):
        fs_store = FirestoreStorageService(fallback_adapter=fallback)

        # Should safely return fallback events without crashing
        events = fs_store.list_events("demo-user")
        assert len(events) >= 3
        event = fs_store.get_event("demo-wedding-jaipur")
        assert event is not None
        assert event["city"] == "Jaipur"


@pytest.mark.asyncio
async def test_guest_api_endpoints():
    """Tests guest listing, guest addition, and RSVP updating via API."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Get guests for demo event
        res = await client.get("/api/events/demo-wedding-jaipur/guests")
        assert res.status_code == 200
        guests = res.json()
        assert len(guests) >= 2

        # 2. Add guest without auth must return 401
        res_unauth = await client.post(
            "/api/events/demo-wedding-jaipur/guests",
            json={
                "id": "g-new-1",
                "name": "Unauthorized Attendee",
                "affiliation": "friend",
                "rsvp_status": "pending",
            },
        )
        assert res_unauth.status_code == 401

        # 3. Add guest with token to demo event returns 403 Forbidden
        res_demo = await client.post(
            "/api/events/demo-wedding-jaipur/guests",
            headers={"Authorization": "Bearer test-token-demo"},
            json={
                "id": "g-new-1",
                "name": "Aarushi Mehta",
                "phone": "+91 99887 76655",
                "affiliation": "friend",
                "rsvp_status": "attending",
                "plus_ones": 1,
                "dietary_preference": "Vegetarian",
            },
        )
        assert res_demo.status_code == 403

        # 4. Clone celebration to private workspace
        res_clone = await client.post(
            "/api/events/demo-wedding-jaipur/clone",
            headers={"Authorization": "Bearer test-token-demo"},
            json={"title": "Private Celebration For Guests"},
        )
        assert res_clone.status_code == 200
        user_event_id = res_clone.json()["event_id"]

        # 5. Add guest to private event
        res_auth = await client.post(
            f"/api/events/{user_event_id}/guests",
            headers={"Authorization": "Bearer test-token-demo"},
            json={
                "id": "g-new-1",
                "name": "Aarushi Mehta",
                "phone": "+91 99887 76655",
                "affiliation": "friend",
                "rsvp_status": "attending",
                "plus_ones": 1,
                "dietary_preference": "Vegetarian",
            },
        )
        assert res_auth.status_code == 200
        assert res_auth.json()["success"] is True

        # 6. Update RSVP status on private event
        res_rsvp = await client.post(
            f"/api/events/{user_event_id}/guests/g-new-1/rsvp",
            headers={"Authorization": "Bearer test-token-demo"},
            json={"status": "attending"},
        )
        assert res_rsvp.status_code == 200
        assert res_rsvp.json()["status"] == "attending"
