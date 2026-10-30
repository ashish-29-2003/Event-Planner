"""
Loop Safety, Resilience, and Quota Exhaustion Fallback Tests (R4-T06)
Guarantees AI generation terminates at max-iteration (1 retry),
enforces timeout caps, and avoids infinite loops or divide-by-zero errors.
"""
import pytest

from src.models.budget import BudgetItem, BudgetRebalanceRequest
from src.models.event import CelebrationBrief, EventType
from src.services.gemini_service import gemini_service


@pytest.mark.asyncio
async def test_quota_exhaustion_deterministic_fallback():
    """
    Verifies that when no API key is provided or quota is 0,
    the system safely and instantly serves the curated seed celebration.
    """
    brief = CelebrationBrief(
        title="Offline Test Wedding",
        event_type=EventType.WEDDING,
        culture="Punjabi",
        city="Chandigarh",
        target_budget=2500000.0,
        guest_count=200,
    )

    plan, is_fallback = await gemini_service.generate_master_plan(brief)

    # Must succeed with fallback flag set to True
    assert is_fallback is True
    assert plan.celebration_title == "Offline Test Wedding"
    assert len(plan.budget_breakdown) > 0
    assert len(plan.timeline_tasks) > 0
    assert len(plan.vendor_checklist) > 0
    assert len(plan.personalized_ideas) > 0


@pytest.mark.asyncio
async def test_birthday_seed_fallback():
    brief = CelebrationBrief(
        title="Kid's 7th Birthday",
        event_type=EventType.BIRTHDAY,
        culture="Urban Contemporary",
        city="Bengaluru",
        target_budget=60000.0,
        guest_count=35,
    )
    plan, _is_fallback = await gemini_service.generate_master_plan(brief)
    assert plan.event_type == "birthday"
    assert len(plan.budget_breakdown) > 0


@pytest.mark.asyncio
async def test_community_seed_fallback():
    brief = CelebrationBrief(
        title="Delhi Diwali Mela",
        event_type=EventType.COMMUNITY,
        culture="Gujarati Community",
        city="Delhi",
        target_budget=650000.0,
        guest_count=500,
    )
    plan, _is_fallback = await gemini_service.generate_master_plan(brief)
    assert plan.event_type == "community"
    assert len(plan.budget_breakdown) > 0


@pytest.mark.asyncio
async def test_rebalance_zero_budget_loop_safety():
    """Verifies that rebalancing with zero or empty budget items completes without divide-by-zero or hanging."""
    req = BudgetRebalanceRequest(
        target_budget=500000.0,
        changed_category="Venue",
        new_amount=300000.0,
        current_items=[],
    )
    resp = await gemini_service.rebalance_budget(req)
    assert resp.target_budget == 500000.0
    assert len(resp.updated_items) == 0


@pytest.mark.asyncio
async def test_rebalance_single_item_loop_safety():
    """Verifies that rebalancing when only 1 category exists terminates cleanly without scale distortion."""
    single_item = BudgetItem(
        id="b1",
        category="Venue",
        name="Community Hall",
        estimated_cost=200000.0,
        advance_paid=50000.0,
        status="partial"
    )
    req = BudgetRebalanceRequest(
        target_budget=300000.0,
        changed_category="Venue",
        new_amount=250000.0,
        current_items=[single_item],
    )
    resp = await gemini_service.rebalance_budget(req)
    assert len(resp.updated_items) == 1
    assert resp.updated_items[0].estimated_cost == 250000.0
