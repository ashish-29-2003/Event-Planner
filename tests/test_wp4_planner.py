import pytest
from src.models.event import CelebrationBrief, EventType
from src.services.planner_service import generate_deterministic_plan
from src.services.gemini_service import gemini_service


def test_deterministic_budget_math_precision():
    """Deterministic plan budget must sum exactly to the brief's target budget."""
    for test_budget in [50000.0, 150000.0, 750000.0, 4500000.0]:
        brief = CelebrationBrief(
            title="Kavya's Sweet 16",
            event_type=EventType.BIRTHDAY,
            culture="Punjabi",
            city="Chandigarh",
            target_budget=test_budget,
            guest_count=75,
            target_date="2026-11-20",
        )
        plan = generate_deterministic_plan(brief)
        assert plan.target_budget == test_budget

        total_allocated = sum(b.estimated_cost for b in plan.budget_breakdown)
        assert round(total_allocated, 2) == round(test_budget, 2)
        assert len(plan.budget_breakdown) == 6


def test_deterministic_timeline_milestones_schedule():
    """Milestone dates must be ordered chronologically leading to target_date."""
    brief = CelebrationBrief(
        title="Community Diwali Dandiya",
        event_type=EventType.COMMUNITY,
        culture="Gujarati",
        city="Ahmedabad",
        target_budget=600000.0,
        guest_count=500,
        target_date="2026-11-08",
    )
    plan = generate_deterministic_plan(brief)
    assert len(plan.timeline_tasks) == 6
    assert plan.timeline_tasks[-1].due_date == "2026-11-08"

    # Tasks should be ordered backwards
    dates = [t.due_date for t in plan.timeline_tasks if t.due_date]
    assert dates == sorted(dates)


def test_deterministic_ideas_and_vendors():
    """Must generate 6 cultural ideas and 4 shortlisted vendors without synthetic phone numbers."""
    brief = CelebrationBrief(
        title="Arjun & Meera Vivaha",
        event_type=EventType.WEDDING,
        culture="Tamil Brahmin",
        city="Chennai",
        target_budget=2000000.0,
        guest_count=250,
        target_date="2026-12-05",
    )
    plan = generate_deterministic_plan(brief)
    assert len(plan.personalized_ideas) == 6
    dimensions = {i.tab_category for i in plan.personalized_ideas}
    assert len(dimensions) == 6

    assert len(plan.vendor_checklist) == 4
    for v in plan.vendor_checklist:
        assert v.quote_amount > 0
        assert v.is_estimate is True
        assert v.phone is None  # Never fake vendor phones


@pytest.mark.asyncio
async def test_gemini_service_offline_fallback_reflects_brief(monkeypatch):
    """Offline/fallback master plan generation must reflect user's input, not hardcoded Jaipur seed."""
    monkeypatch.setattr(gemini_service, "_client", None)
    brief = CelebrationBrief(
        title="Aarav's Cosmic Birthday",
        event_type=EventType.BIRTHDAY,
        culture="Contemporary",
        city="Bengaluru",
        target_budget=85000.0,
        guest_count=40,
        target_date="2026-10-28",
    )
    plan, is_fallback = await gemini_service.generate_master_plan(brief)
    assert is_fallback is True
    assert plan.celebration_title == "Aarav's Cosmic Birthday"
    assert plan.target_budget == 85000.0
    total_allocated = sum(b.estimated_cost for b in plan.budget_breakdown)
    assert round(total_allocated, 2) == 85000.0
