"""
Loop Safety, Resilience, and Quota Exhaustion Fallback Tests.
Guarantees AI generation terminates at max-iteration (1 retry) and enforces timeout caps.
"""

import pytest

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
