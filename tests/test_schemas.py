"""
Unit tests for Pydantic v2 data models & schemas.
"""

import pytest
from pydantic import ValidationError

from src.data.wedding_jaipur import JAIPUR_WEDDING_SEED
from src.models.budget import BudgetItem, PaymentStatus
from src.models.event import CelebrationBrief, EventType


def test_celebration_brief_valid():
    brief = CelebrationBrief(
        title="Riya's Vivaha",
        event_type=EventType.WEDDING,
        culture="Marwari",
        city="Jaipur",
        target_budget=4500000.0,
        guest_count=350,
    )
    assert brief.title == "Riya's Vivaha"
    assert brief.target_budget == 4500000.0


def test_celebration_brief_validation_error_negative_budget():
    with pytest.raises(ValidationError):
        CelebrationBrief(title="Invalid", target_budget=-500.0, guest_count=100)


def test_budget_item_schema():
    item = BudgetItem(
        id="b-1",
        category="Catering",
        name="Royal Rajasthani Feast",
        estimated_cost=500000.0,
        actual_cost=480000.0,
        advance_paid=200000.0,
        status=PaymentStatus.PARTIAL,
    )
    assert item.estimated_cost == 500000.0
    assert item.status == PaymentStatus.PARTIAL


def test_master_plan_schema_from_seed():
    assert JAIPUR_WEDDING_SEED.celebration_title == "Riya & Kabir's Royal Vivaha & Sangeet"
    assert len(JAIPUR_WEDDING_SEED.budget_breakdown) > 0
    assert len(JAIPUR_WEDDING_SEED.timeline_tasks) > 0
    assert len(JAIPUR_WEDDING_SEED.vendor_checklist) > 0
    assert len(JAIPUR_WEDDING_SEED.personalized_ideas) > 0
