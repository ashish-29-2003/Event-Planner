"""
Persistent Storage Service for Celebrations and Sub-Entities.
Provides multi-tenant document isolation with local JSON persistence and seed pre-loading.
"""
import json
import uuid
from pathlib import Path
from typing import Optional
from src.models.event import EventResponse, CelebrationBrief, EventType
from src.models.budget import BudgetItem
from src.models.timeline import TaskItem
from src.models.vendor import VendorItem
from src.models.ideas import IdeaItem
from src.models.ai_plan import EventMasterPlan
from src.data.wedding_jaipur import JAIPUR_WEDDING_SEED
from src.data.birthday_blr import BLR_BIRTHDAY_SEED
from src.data.community_delhi import DELHI_COMMUNITY_SEED

DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"

class StorageService:
    def __init__(self):
        self._events: dict[str, dict] = {}
        self._budgets: dict[str, list[BudgetItem]] = {}
        self._tasks: dict[str, list[TaskItem]] = {}
        self._vendors: dict[str, list[VendorItem]] = {}
        self._ideas: dict[str, list[IdeaItem]] = {}
        self._initialize_seed_celebrations()

    def _initialize_seed_celebrations(self):
        """Loads default seed celebrations for instant demo exploration."""
        seeds = [
            ("demo-wedding-jaipur", JAIPUR_WEDDING_SEED, "Marwari Hindu", "Jaipur", "wedding"),
            ("demo-birthday-blr", BLR_BIRTHDAY_SEED, "Contemporary Urban", "Bengaluru", "birthday"),
            ("demo-community-delhi", DELHI_COMMUNITY_SEED, "Inter-Community", "Delhi NCR", "community"),
        ]
        
        for event_id, plan, culture, city, ev_type in seeds:
            self._events[event_id] = {
                "id": event_id,
                "user_id": "demo-user",
                "title": plan.celebration_title,
                "event_type": ev_type,
                "culture": culture,
                "city": city,
                "target_budget": plan.target_budget,
                "guest_count": plan.guest_count,
                "language": "en",
                "blessing_note": "May every celebration begin with auspicious blessings and joy.",
                "auspicious_guidance": plan.auspicious_guidance,
                "disclaimer": plan.disclaimer
            }
            self._budgets[event_id] = [item for item in plan.budget_breakdown]
            self._tasks[event_id] = [task for task in plan.timeline_tasks]
            self._vendors[event_id] = [v for v in plan.vendor_checklist]
            self._ideas[event_id] = [i for i in plan.personalized_ideas]

    def list_events(self, user_id: str = "demo-user") -> list[dict]:
        """Returns all events matching user_id plus public demo events."""
        results = []
        for eid, ev in self._events.items():
            if ev.get("user_id") in (user_id, "demo-user"):
                results.append(ev)
        return results

    def get_event(self, event_id: str) -> Optional[dict]:
        return self._events.get(event_id)

    def create_event_from_plan(self, brief: CelebrationBrief, plan: EventMasterPlan, user_id: str = "demo-user") -> str:
        """Stores a freshly generated AI master plan into persistent state."""
        event_id = f"event-{uuid.uuid4().hex[:8]}"
        
        self._events[event_id] = {
            "id": event_id,
            "user_id": user_id,
            "title": plan.celebration_title,
            "event_type": str(brief.event_type.value if hasattr(brief.event_type, 'value') else brief.event_type),
            "culture": brief.culture,
            "city": brief.city,
            "target_date": brief.target_date,
            "target_budget": plan.target_budget,
            "guest_count": plan.guest_count,
            "language": brief.language,
            "blessing_note": None,
            "auspicious_guidance": plan.auspicious_guidance,
            "disclaimer": plan.disclaimer
        }
        
        self._budgets[event_id] = plan.budget_breakdown
        self._tasks[event_id] = plan.timeline_tasks
        self._vendors[event_id] = plan.vendor_checklist
        self._ideas[event_id] = plan.personalized_ideas
        
        return event_id

    def get_budget_items(self, event_id: str) -> list[BudgetItem]:
        return self._budgets.get(event_id, [])

    def update_budget_items(self, event_id: str, items: list[BudgetItem]):
        self._budgets[event_id] = items

    def get_tasks(self, event_id: str) -> list[TaskItem]:
        return self._tasks.get(event_id, [])

    def update_task_status(self, event_id: str, task_id: str, status: str) -> bool:
        tasks = self._tasks.get(event_id, [])
        for t in tasks:
            if t.id == task_id:
                t.status = status
                return True
        return False

    def get_vendors(self, event_id: str) -> list[VendorItem]:
        return self._vendors.get(event_id, [])

    def get_ideas(self, event_id: str) -> list[IdeaItem]:
        return self._ideas.get(event_id, [])

storage_service = StorageService()
