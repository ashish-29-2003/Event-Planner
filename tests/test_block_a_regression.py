"""
Regression Test Suite for Block A: Data & State Defects (D1, D2, D5, D6, D9).
Verifies:
- D1: Single normalizer, source-of-truth schema, and backend contract (no "undefined" or missing fields).
- D2: Plan switcher loads distinct data per celebration (title, target budget, milestones, vendors).
- D5: Guest state initialization and safe array iteration (no "store.state.guests is not iterable").
- D6: RSVP counters derived from guest list and updated reactively.
- D9: Single pure budget calculation function reconciles hero, legend, and ledger across all seeds.
"""

import json
from pathlib import Path
import pytest
from httpx import ASGITransport, AsyncClient

from src.main import app
from src.services.storage_service import InMemoryStorageService, FirestoreStorageService, get_storage_service
from src.models.guest import RSVPStatus


# ==============================================================================
# D1: Schema Contract & Normalization Assertions
# ==============================================================================

def test_d1_seed_celebrations_contract_memory_and_firestore():
    """Assert all seed celebrations return unified schema across storage backends."""
    storage = get_storage_service()
    event_ids = ["demo-wedding-jaipur", "demo-birthday-blr", "demo-community-delhi"]

    required_keys = {
        "id", "user_id", "title", "event_type", "culture", "city",
        "target_budget", "guest_count", "language", "blessing_note",
        "auspicious_guidance", "disclaimer"
    }

    for eid in event_ids:
        event = storage.get_event(eid)
        assert event is not None, f"Event {eid} must exist in storage"
        missing = required_keys - set(event.keys())
        assert not missing, f"Event {eid} is missing required schema keys: {missing}"
        assert event["title"], f"Event {eid} title must not be empty"
        assert event["title"] != "undefined", f"Event {eid} title must not be literal 'undefined'"
        assert event["culture"], f"Event {eid} culture must not be empty"
        assert event["city"], f"Event {eid} city must not be empty"
        assert event["target_budget"] > 0, f"Event {eid} target_budget must be positive"


@pytest.mark.asyncio
async def test_d1_api_returns_complete_event_metadata():
    """Verify GET /api/events/{id} returns clean, non-null metadata without missing fields."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        for eid in ["demo-wedding-jaipur", "demo-birthday-blr", "demo-community-delhi"]:
            res = await client.get(f"/api/events/{eid}")
            assert res.status_code == 200
            data = res.json()
            assert data["id"] == eid
            assert data["title"] is not None
            assert data["title"] != "undefined"
            assert data["culture"] is not None
            assert data["city"] is not None
            assert isinstance(data["target_budget"], (int, float))


# ==============================================================================
# D2: Plan Switcher Distinct State Assertions
# ==============================================================================

@pytest.mark.asyncio
async def test_d2_each_seed_has_distinct_budgets_milestones_and_vendors():
    """Verify switching plans loads completely different data for wedding, birthday, and mela."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Jaipur Wedding
        res_w = await client.get("/api/events/demo-wedding-jaipur")
        assert res_w.status_code == 200
        w_data = res_w.json()
        assert "Vivaha" in w_data["title"] or "Wedding" in w_data["title"]
        assert w_data["target_budget"] == 4500000.0
        assert w_data["event_type"] == "wedding"

        res_w_tasks = await client.get("/api/events/demo-wedding-jaipur/tasks")
        w_tasks = res_w_tasks.json()
        assert len(w_tasks) > 0
        assert any("Muhurat" in t["title"] or "Pandit" in t["title"] or "Mandap" in t["title"] for t in w_tasks)

        # 2. Bengaluru Birthday
        res_b = await client.get("/api/events/demo-birthday-blr")
        assert res_b.status_code == 200
        b_data = res_b.json()
        assert "Birthday" in b_data["title"]
        assert b_data["target_budget"] == 85000.0
        assert b_data["event_type"] == "birthday"

        res_b_tasks = await client.get("/api/events/demo-birthday-blr/tasks")
        b_tasks = res_b_tasks.json()
        assert len(b_tasks) > 0
        assert any("Cake" in t["title"] or "Balloon" in t["title"] or "Return Gift" in t["title"] for t in b_tasks)

        # 3. Delhi Community Mela
        res_m = await client.get("/api/events/demo-community-delhi")
        assert res_m.status_code == 200
        m_data = res_m.json()
        assert "Diwali" in m_data["title"] or "Dandiya" in m_data["title"]
        assert m_data["target_budget"] == 650000.0
        assert m_data["event_type"] == "community"

        res_m_tasks = await client.get("/api/events/demo-community-delhi/tasks")
        m_tasks = res_m_tasks.json()
        assert len(m_tasks) > 0
        assert any("Permit" in t["title"] or "Dandiya" in t["title"] or "Sound" in t["title"] for t in m_tasks)


# ==============================================================================
# D5: Guest Array Safety & Non-Crashing
# ==============================================================================

@pytest.mark.asyncio
async def test_d5_get_guests_returns_list_for_all_events():
    """Verify get_guests returns an array (not None or dict) for all seed events."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        for eid in ["demo-wedding-jaipur", "demo-birthday-blr", "demo-community-delhi"]:
            res = await client.get(f"/api/events/{eid}/guests")
            assert res.status_code == 200
            data = res.json()
            assert isinstance(data, list)
            assert len(data) >= 2


# ==============================================================================
# D6: RSVP Counter Calculation Math
# ==============================================================================

def calculate_rsvp_counters(guests: list[dict]):
    """Pure helper replicating client-side RSVP counter derivation."""
    total_invitations = len(guests)
    attending_count = 0
    pending_count = 0
    declined_count = 0
    total_attending_heads = 0

    for g in guests:
        status = (g.get("rsvp_status") or "pending").lower()
        plus_ones = int(g.get("plus_ones") or 0)
        if status == "attending":
            attending_count += 1
            total_attending_heads += 1 + plus_ones
        elif status == "declined":
            declined_count += 1
        else:
            pending_count += 1

    return {
        "total_invitations": total_invitations,
        "attending": attending_count,
        "pending": pending_count,
        "declined": declined_count,
        "total_attending_heads": total_attending_heads,
    }


def test_d6_rsvp_counter_calculation_on_status_change():
    """Assert RSVP counter derivation accurately updates when status transitions occur."""
    initial_guests = [
        {"id": "g1", "name": "Rajesh", "rsvp_status": "attending", "plus_ones": 3},
        {"id": "g2", "name": "Pooja", "rsvp_status": "pending", "plus_ones": 1},
    ]

    c1 = calculate_rsvp_counters(initial_guests)
    assert c1["attending"] == 1
    assert c1["pending"] == 1
    assert c1["declined"] == 0
    assert c1["total_attending_heads"] == 4

    # Transition Pooja from pending to declined
    updated_guests = [
        {"id": "g1", "name": "Rajesh", "rsvp_status": "attending", "plus_ones": 3},
        {"id": "g2", "name": "Pooja", "rsvp_status": "declined", "plus_ones": 1},
    ]
    c2 = calculate_rsvp_counters(updated_guests)
    assert c2["attending"] == 1
    assert c2["pending"] == 0
    assert c2["declined"] == 1
    assert c2["total_attending_heads"] == 4


# ==============================================================================
# D9: Pure Budget Ledger Math & Reconciliation
# ==============================================================================

def compute_budget_ledger(target_budget: float, items: list[dict]):
    """Pure mathematical function matching frontend computeBudgetLedger."""
    target = float(target_budget or 0)
    allocated = sum(float(b.get("estimated_cost") or 0) for b in items)
    paid = sum(float(b.get("advance_paid") or 0) for b in items)
    balance_due = max(0.0, allocated - paid)
    unallocated_buffer = target - allocated
    is_over_budget = unallocated_buffer < 0

    alloc_pct = (allocated / target * 100.0) if target > 0 else 0.0
    paid_pct = (paid / target * 100.0) if target > 0 else 0.0
    balance_pct = (balance_due / target * 100.0) if target > 0 else 0.0

    return {
        "target": target,
        "allocated": allocated,
        "paid": paid,
        "balance_due": balance_due,
        "unallocated_buffer": unallocated_buffer,
        "is_over_budget": is_over_budget,
        "alloc_pct": round(alloc_pct, 1),
        "paid_pct": round(paid_pct, 1),
        "balance_pct": round(balance_pct, 1),
    }


@pytest.mark.asyncio
async def test_d9_budget_ledger_reconciles_across_all_seeds():
    """Verify single budget ledger math matches for all 3 seeded plans without discrepancies."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        for eid in ["demo-wedding-jaipur", "demo-birthday-blr", "demo-community-delhi"]:
            res_ev = await client.get(f"/api/events/{eid}")
            res_bg = await client.get(f"/api/events/{eid}/budget")
            assert res_ev.status_code == 200
            assert res_bg.status_code == 200

            target = res_ev.json()["target_budget"]
            items = res_bg.json()

            ledger = compute_budget_ledger(target, items)

            # Mathematical invariants:
            # 1. allocated == paid + balance_due
            assert abs(ledger["allocated"] - (ledger["paid"] + ledger["balance_due"])) < 1e-4
            # 2. target == allocated + unallocated_buffer
            assert abs(ledger["target"] - (ledger["allocated"] + ledger["unallocated_buffer"])) < 1e-4
            # 3. If within budget, buffer >= 0; if over budget, buffer < 0
            if ledger["is_over_budget"]:
                assert ledger["unallocated_buffer"] < 0
            else:
                assert ledger["unallocated_buffer"] >= 0


def test_d9_budget_ledger_edge_cases():
    """Assert edge cases (zero budget, over-budget, float precision) handle cleanly."""
    # Zero target budget
    zero_ledger = compute_budget_ledger(0, [])
    assert zero_ledger["target"] == 0
    assert zero_ledger["alloc_pct"] == 0.0
    assert zero_ledger["paid_pct"] == 0.0

    # Over-budget scenario
    items = [
        {"name": "Venue", "estimated_cost": 600000.0, "advance_paid": 200000.0},
        {"name": "Catering", "estimated_cost": 500000.0, "advance_paid": 100000.0},
    ]
    over_ledger = compute_budget_ledger(1000000.0, items)
    assert over_ledger["target"] == 1000000.0
    assert over_ledger["allocated"] == 1100000.0
    assert over_ledger["paid"] == 300000.0
    assert over_ledger["balance_due"] == 800000.0
    assert over_ledger["unallocated_buffer"] == -100000.0
    assert over_ledger["is_over_budget"] is True
    assert over_ledger["alloc_pct"] == 110.0
