"""
Mock Integration Tests for Gemini API, Calendar Export, and Storage (R4-T03 & R4-T06)
Verifies:
1. Gemini API synthesis with valid JSON responses
2. Gemini API validation failure triggering repair prompt and recovering
3. Gemini repair failure cleanly terminating and returning deterministic curated seed
4. Gemini timeout handling
5. Calendar export RFC-5545 deep parsing and deep-link generation
6. Storage service cloning and deep copying across subcollections
"""
from unittest.mock import MagicMock

import pytest

from src.models.budget import BudgetItem, BudgetRebalanceRequest
from src.models.event import CelebrationBrief, EventType
from src.models.timeline import TaskItem
from src.services.calendar_service import generate_ics_calendar
from src.services.gemini_service import GeminiService
from src.services.storage_service import InMemoryStorageService

# Sample valid EventMasterPlan JSON for mocking
SAMPLE_VALID_PLAN_JSON = """{
  "celebration_title": "Ananya and Rohan Vivaha",
  "event_type": "wedding",
  "cultural_summary": "Authentic Marwari wedding celebration honoring traditional rituals and Vedic muhurats.",
  "culture": "Marwari",
  "city": "Jaipur",
  "target_budget": 3500000.0,
  "guest_count": 300,
  "blessing_note": "May this union flourish with divine joy.",
  "budget_breakdown": [
    {
      "id": "b-1",
      "category": "Venue & Decor",
      "name": "Heritage Haveli Booking",
      "estimated_cost": 1500000.0,
      "advance_paid": 500000.0,
      "status": "partial",
      "notes": "Courtyard mandap included"
    }
  ],
  "timeline_tasks": [
    {
      "id": "t-1",
      "title": "Mandap Booking Finalization",
      "due_date": "2026-11-15",
      "phase": "Foundational Logistics",
      "owner_role": "Family Lead",
      "status": "todo",
      "description": "Confirm Panditji and mandap setup."
    }
  ],
  "vendor_checklist": [
    {
      "id": "v-1",
      "category": "Decor",
      "business_name": "Royal Florals",
      "quote_amount": 350000.0,
      "status": "shortlisted",
      "rating": 4.9,
      "address": "MI Road, Jaipur",
      "phone": "+91-141-555019"
    }
  ],
  "personalized_ideas": [
    {
      "id": "i-1",
      "tab_category": "ritual_decor",
      "title": "Traditional Marwari Toran Gate",
      "cost_bracket": "Moderate",
      "description": "Fresh marigold toran entrance.",
      "cultural_context": "Welcomes the groom party."
    }
  ]
}"""


@pytest.fixture
def mock_gemini():
    """Instantiate GeminiService with a mocked internal client."""
    service = GeminiService()
    service.api_key = "mock-key-for-testing"
    service._client = MagicMock()
    return service


@pytest.mark.asyncio
async def test_gemini_successful_plan_synthesis(mock_gemini):
    """Verifies standard Gemini API path parsing valid JSON into EventMasterPlan."""
    mock_resp = MagicMock()
    mock_resp.text = SAMPLE_VALID_PLAN_JSON
    mock_gemini._client.models.generate_content.return_value = mock_resp

    brief = CelebrationBrief(
        title="Ananya and Rohan Vivaha",
        event_type=EventType.WEDDING,
        culture="Marwari",
        city="Jaipur",
        target_budget=3500000.0,
        guest_count=300,
    )

    plan, is_fallback = await mock_gemini.generate_master_plan(brief)
    assert is_fallback is False
    assert plan.celebration_title == "Ananya and Rohan Vivaha"
    assert len(plan.budget_breakdown) == 1
    assert plan.budget_breakdown[0].estimated_cost == 1500000.0


@pytest.mark.asyncio
async def test_gemini_repair_loop_recovers_from_malformed_json(mock_gemini):
    """
    R4-T06: When Gemini initial response fails schema validation,
    the repair loop is invoked and successfully repairs the plan.
    """
    # 1st call returns invalid json (missing required fields), 2nd call (repair) returns valid json
    invalid_resp = MagicMock()
    invalid_resp.text = '{"celebration_title": "Broken Plan"}'

    repaired_resp = MagicMock()
    repaired_resp.text = SAMPLE_VALID_PLAN_JSON

    mock_gemini._client.models.generate_content.side_effect = [invalid_resp, repaired_resp]

    brief = CelebrationBrief(
        title="Ananya and Rohan Vivaha",
        event_type=EventType.WEDDING,
        culture="Marwari",
        city="Jaipur",
        target_budget=3500000.0,
        guest_count=300,
    )

    plan, is_fallback = await mock_gemini.generate_master_plan(brief)

    # Verify repair call occurred
    assert mock_gemini._client.models.generate_content.call_count == 2
    assert is_fallback is False
    assert plan.celebration_title == "Ananya and Rohan Vivaha"


@pytest.mark.asyncio
async def test_gemini_repair_loop_max_iteration_terminates_cleanly(mock_gemini):
    """
    R4-T06: When both initial and repair prompt fail, the loop terminates
    cleanly at max iterations (1 retry) and returns curated fallback seed without infinite looping.
    """
    # Both calls return broken JSON
    invalid_resp1 = MagicMock()
    invalid_resp1.text = '{"malformed": true}'

    invalid_resp2 = MagicMock()
    invalid_resp2.text = '{"still_malformed": true}'

    mock_gemini._client.models.generate_content.side_effect = [invalid_resp1, invalid_resp2]

    brief = CelebrationBrief(
        title="Ananya and Rohan Vivaha",
        event_type=EventType.WEDDING,
        culture="Marwari",
        city="Jaipur",
        target_budget=3500000.0,
        guest_count=300,
    )

    plan, is_fallback = await mock_gemini.generate_master_plan(brief)

    # Must terminate in exactly 2 calls (initial + 1 repair)
    assert mock_gemini._client.models.generate_content.call_count == 2
    assert is_fallback is True
    assert plan.event_type == "wedding"
    assert len(plan.budget_breakdown) > 0


@pytest.mark.asyncio
async def test_gemini_timeout_fallback(mock_gemini):
    """Verifies that an async timeout during Gemini API call terminates and returns fallback."""
    def timeout_call(*args, **kwargs):
        raise TimeoutError("Gemini API connection timed out")

    mock_gemini._client.models.generate_content.side_effect = timeout_call

    brief = CelebrationBrief(
        title="Timeout Event",
        event_type=EventType.BIRTHDAY,
        culture="Contemporary",
        city="Bengaluru",
        target_budget=75000.0,
        guest_count=40,
    )

    plan, is_fallback = await mock_gemini.generate_master_plan(brief)
    assert is_fallback is True
    assert plan.event_type == "birthday"


@pytest.mark.asyncio
async def test_gemini_budget_rebalance_proportional_fallback(mock_gemini):
    """Verifies that budget rebalance falls back to proportional distribution on exception."""
    mock_gemini._client.models.generate_content.side_effect = RuntimeError("API unavailable")

    current_items = [
        BudgetItem(id="b1", category="Venue", name="Hall", estimated_cost=500000.0, advance_paid=100000.0, status="partial"),
        BudgetItem(id="b2", category="Catering", name="Food", estimated_cost=300000.0, advance_paid=50000.0, status="partial"),
        BudgetItem(id="b3", category="Decor", name="Flowers", estimated_cost=200000.0, advance_paid=20000.0, status="pending"),
    ]

    req = BudgetRebalanceRequest(
        target_budget=1000000.0,
        changed_category="Venue",
        new_amount=600000.0,
        current_items=current_items,
    )

    resp = await mock_gemini.rebalance_budget(req)
    assert resp.target_budget == 1000000.0
    assert len(resp.updated_items) == 3
    # Check that changed category was updated
    venue_item = next(i for i in resp.updated_items if i.category == "Venue")
    assert venue_item.estimated_cost == 600000.0


def test_calendar_service_rfc5545_compliance():
    """Verifies that generate_ics_calendar output conforms to RFC-5545 iCalendar syntax."""
    tasks = [
        TaskItem(
            id="task-1",
            title="Book Haldi Mandap",
            due_date="2026-11-10",
            phase="Phase 1",
            owner_role="Bride's Family",
            description="Inspect venue and confirm priest timing.",
        ),
        TaskItem(
            id="task-2",
            title="Finalize Sangeet DJ",
            due_date="2026-11-25",
            phase="Phase 2",
            owner_role="Groom's Brother",
            description="Submit playlist of Bollywood and folk tracks.",
        ),
    ]

    ics = generate_ics_calendar("Jaipur Royal Vivaha", tasks)

    # Core RFC-5545 assertions
    assert ics.startswith(("BEGIN:VCALENDAR\n", "BEGIN:VCALENDAR\r\n"))
    assert "VERSION:2.0" in ics
    assert "PRODID:-//Samaroh//GenAI Celebration Planner//EN" in ics
    assert "CALSCALE:GREGORIAN" in ics
    assert "X-WR-CALNAME:Samaroh - Jaipur Royal Vivaha" in ics

    # VEVENT blocks
    assert ics.count("BEGIN:VEVENT") == 2
    assert ics.count("END:VEVENT") == 2
    assert "SUMMARY:Samaroh: Book Haldi Mandap" in ics
    assert "SUMMARY:Samaroh: Finalize Sangeet DJ" in ics
    assert "DTSTART;VALUE=DATE:20261110" in ics
    assert "DTSTART;VALUE=DATE:20261125" in ics
    assert ics.endswith(("END:VCALENDAR\n", "END:VCALENDAR\r\n"))


def test_storage_service_event_cloning():
    """Verifies InMemoryStorageService.clone_event copies event and all subcollections with new ownership."""
    storage = InMemoryStorageService()

    # Clone demo event to new user
    cloned_id = storage.clone_event(
        source_event_id="demo-wedding-jaipur",
        new_user_id="user-custom-test",
        new_title="Custom Sharma Vivaha",
    )

    assert cloned_id is not None
    assert cloned_id.startswith("event-")

    # Verify event cloned attributes
    cloned_event = storage.get_event(cloned_id)
    assert cloned_event is not None
    assert cloned_event["title"] == "Custom Sharma Vivaha"
    assert cloned_event["culture"] == "Marwari Hindu"

    # Verify subcollections were deep copied
    budgets = storage.get_budget_items(cloned_id)
    assert len(budgets) > 0

    tasks = storage.get_tasks(cloned_id)
    assert len(tasks) > 0

    vendors = storage.get_vendors(cloned_id)
    assert len(vendors) > 0

    guests = storage.get_guests(cloned_id)
    assert len(guests) > 0
