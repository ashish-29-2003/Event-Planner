import pytest
from fastapi.testclient import TestClient

from src.data.birthday_blr import BLR_BIRTHDAY_SEED
from src.data.community_delhi import DELHI_COMMUNITY_SEED
from src.data.wedding_jaipur import JAIPUR_WEDDING_SEED
from src.main import app

client = TestClient(app)


def test_seed_celebrations_vendor_honesty():
    """Seed data must never include synthetic or invented vendor phone numbers."""
    all_seeds = [JAIPUR_WEDDING_SEED, BLR_BIRTHDAY_SEED, DELHI_COMMUNITY_SEED]
    for seed in all_seeds:
        for vendor in seed.vendor_checklist:
            assert vendor.phone is None, f"Found invented vendor phone {vendor.phone} in {seed.celebration_title}"


def test_delhi_community_diwali_2026_date_accuracy():
    """Delhi community Diwali celebration must culminate on authentic Kartik Amavasya date: Nov 8, 2026."""
    delhi_tasks = DELHI_COMMUNITY_SEED.timeline_tasks
    event_day_tasks = [t for t in delhi_tasks if "Day-Of" in t.phase or "Event Schedule" in t.phase]
    assert len(event_day_tasks) >= 2
    for t in event_day_tasks:
        assert t.due_date == "2026-11-08", f"Task {t.title} had incorrect date {t.due_date}"


def test_health_endpoint_reports_seeds_ok():
    """GET /api/health must verify that packaged seed celebrations load properly."""
    res = client.get("/api/health")
    assert res.status_code == 200
    data = res.json()
    assert data["seeds"] == "ok"


def test_all_seeds_have_complete_subcollections():
    """All 3 packaged celebration seeds must have non-empty budgets, tasks, vendors, and ideas."""
    all_seeds = [JAIPUR_WEDDING_SEED, BLR_BIRTHDAY_SEED, DELHI_COMMUNITY_SEED]
    for seed in all_seeds:
        assert len(seed.budget_breakdown) >= 6
        assert len(seed.timeline_tasks) >= 5
        assert len(seed.vendor_checklist) >= 3
        assert len(seed.personalized_ideas) >= 6
