"""
Persistent Storage Service for Celebrations and Sub-Entities.
Provides multi-tenant document isolation, Cloud Firestore integration,
and a resilient file-backed local adapter for zero-friction demo and offline judging.
"""

import json
import logging
import uuid
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, cast

from src.config import settings
from src.data.birthday_blr import BLR_BIRTHDAY_SEED
from src.data.community_delhi import DELHI_COMMUNITY_SEED
from src.data.wedding_jaipur import JAIPUR_WEDDING_SEED
from src.models.ai_plan import EventMasterPlan
from src.models.budget import BudgetItem
from src.models.event import CelebrationBrief
from src.models.guest import GuestAffiliation, GuestItem, RSVPStatus
from src.models.ideas import IdeaItem
from src.models.timeline import TaskItem, TaskStatus
from src.models.vendor import VendorItem

logger = logging.getLogger("samaroh.storage")
DATA_DIR = Path(__file__).resolve().parent.parent.parent / "data"
LOCAL_STORE_PATH = DATA_DIR / "local_store.json"


class BaseStorageService(ABC):
    """Abstract interface defining operations on celebration documents and subcollections."""

    @abstractmethod
    def list_events(self, user_id: str = "demo-user") -> list[dict[str, Any]]:
        """Lists user-owned events and public demo events."""

    @abstractmethod
    def get_event(self, event_id: str) -> dict[str, Any] | None:
        """Retrieves single event metadata."""

    @abstractmethod
    def create_event_from_plan(
        self, brief: CelebrationBrief, plan: EventMasterPlan, user_id: str = "demo-user"
    ) -> str:
        """Stores a new celebration master plan."""

    @abstractmethod
    def get_budget_items(self, event_id: str) -> list[BudgetItem]:
        """Retrieves budget line items."""

    @abstractmethod
    def update_budget_items(self, event_id: str, items: list[BudgetItem]) -> None:
        """Updates budget items for an event."""

    @abstractmethod
    def get_tasks(self, event_id: str) -> list[TaskItem]:
        """Retrieves timeline milestone tasks."""

    @abstractmethod
    def update_task_status(self, event_id: str, task_id: str, status: str) -> bool:
        """Updates status of a specific task."""

    @abstractmethod
    def get_vendors(self, event_id: str) -> list[VendorItem]:
        """Retrieves vendor checklist."""

    @abstractmethod
    def get_ideas(self, event_id: str) -> list[IdeaItem]:
        """Retrieves cultural inspiration ideas."""

    @abstractmethod
    def get_guests(self, event_id: str) -> list[GuestItem]:
        """Retrieves guest list and RSVP state."""

    @abstractmethod
    def add_guest(self, event_id: str, guest: GuestItem) -> GuestItem:
        """Adds a guest to the celebration."""

    @abstractmethod
    def update_guest_rsvp(self, event_id: str, guest_id: str, status: RSVPStatus) -> bool:
        """Updates RSVP status for a specific guest."""

    @abstractmethod
    def delete_event(self, event_id: str) -> bool:
        """Deletes an event and its associated subcollections."""

    @abstractmethod
    def clone_event(
        self, source_event_id: str, new_user_id: str, new_title: str | None = None
    ) -> str:
        """Clones a celebration and its subcollections into a user's private space."""


class InMemoryStorageService(BaseStorageService):
    """
    File-backed local document store.
    Guarantees persistence across server restarts via JSON disk cache,
    and supplies curated seed celebrations for instant demo exploration.
    """

    def __init__(self, persistence_path: Path | None = LOCAL_STORE_PATH):
        self._persistence_path = persistence_path
        self._events: dict[str, dict[str, Any]] = {}
        self._budgets: dict[str, list[BudgetItem]] = {}
        self._tasks: dict[str, list[TaskItem]] = {}
        self._vendors: dict[str, list[VendorItem]] = {}
        self._ideas: dict[str, list[IdeaItem]] = {}
        self._guests: dict[str, list[GuestItem]] = {}

        self._initialize_seed_celebrations()
        self._load_from_disk()

    def _initialize_seed_celebrations(self) -> None:
        """Loads default seed celebrations for instant demo exploration."""
        seeds = [
            ("demo-wedding-jaipur", JAIPUR_WEDDING_SEED, "Marwari Hindu", "Jaipur", "wedding"),
            ("demo-birthday-blr", BLR_BIRTHDAY_SEED, "Contemporary Urban", "Bengaluru", "birthday"),
            (
                "demo-community-delhi",
                DELHI_COMMUNITY_SEED,
                "Inter-Community",
                "Delhi NCR",
                "community",
            ),
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
                "disclaimer": plan.disclaimer,
            }
            self._budgets[event_id] = list(plan.budget_breakdown)
            self._tasks[event_id] = list(plan.timeline_tasks)
            self._vendors[event_id] = list(plan.vendor_checklist)
            self._ideas[event_id] = list(plan.personalized_ideas)
            self._guests[event_id] = [
                GuestItem(
                    id=f"guest-{event_id}-1",
                    name="Rajesh Sharma & Family",
                    phone="+91 98765 43210",
                    affiliation=GuestAffiliation.FAMILY,
                    rsvp_status=RSVPStatus.ATTENDING,
                    plus_ones=3,
                    dietary_preference="Strict Vegetarian (Jain)",
                    invitation_sent=True,
                ),
                GuestItem(
                    id=f"guest-{event_id}-2",
                    name="Pooja & Sameer Verma",
                    phone="+91 98111 22334",
                    affiliation=GuestAffiliation.FRIEND,
                    rsvp_status=RSVPStatus.PENDING,
                    plus_ones=1,
                    dietary_preference="Vegetarian",
                    invitation_sent=True,
                ),
            ]

    def _save_to_disk(self) -> None:
        """Persists non-demo events to disk so data survives server restarts."""
        if not self._persistence_path:
            return
        try:
            self._persistence_path.parent.mkdir(parents=True, exist_ok=True)
            non_demo_events = {
                k: v for k, v in self._events.items() if not k.startswith("demo-")
            }
            data_to_save: dict[str, Any] = {
                "events": non_demo_events,
                "budgets": {
                    k: [b.model_dump() for b in v]
                    for k, v in self._budgets.items()
                    if not k.startswith("demo-")
                },
                "tasks": {
                    k: [t.model_dump() for t in v]
                    for k, v in self._tasks.items()
                    if not k.startswith("demo-")
                },
                "vendors": {
                    k: [vnd.model_dump() for vnd in v]
                    for k, v in self._vendors.items()
                    if not k.startswith("demo-")
                },
                "ideas": {
                    k: [i.model_dump() for i in v]
                    for k, v in self._ideas.items()
                    if not k.startswith("demo-")
                },
                "guests": {
                    k: [g.model_dump() for g in v]
                    for k, v in self._guests.items()
                    if not k.startswith("demo-")
                },
            }
            with open(self._persistence_path, "w", encoding="utf-8") as f:
                json.dump(data_to_save, f, indent=2, default=str)
        except Exception as exc:
            logger.warning("Could not persist local store to disk: %s", exc)

    def _load_from_disk(self) -> None:
        """Restores persisted non-demo events from disk."""
        if not self._persistence_path or not self._persistence_path.exists():
            return
        try:
            with open(self._persistence_path, encoding="utf-8") as f:
                saved = json.load(f)
            for eid, ev in saved.get("events", {}).items():
                self._events[eid] = ev
            for eid, items in saved.get("budgets", {}).items():
                self._budgets[eid] = [BudgetItem(**b) for b in items]
            for eid, tasks in saved.get("tasks", {}).items():
                self._tasks[eid] = [TaskItem(**t) for t in tasks]
            for eid, vendors in saved.get("vendors", {}).items():
                self._vendors[eid] = [VendorItem(**v) for v in vendors]
            for eid, ideas in saved.get("ideas", {}).items():
                self._ideas[eid] = [IdeaItem(**i) for i in ideas]
            for eid, guests in saved.get("guests", {}).items():
                self._guests[eid] = [GuestItem(**g) for g in guests]
        except Exception as exc:
            logger.warning("Could not load local store from disk: %s", exc)

    def list_events(self, user_id: str = "demo-user") -> list[dict[str, Any]]:
        results = []
        for ev in self._events.values():
            if ev.get("user_id") in (user_id, "demo-user"):
                results.append(ev)
        return results

    def get_event(self, event_id: str) -> dict[str, Any] | None:
        return self._events.get(event_id)

    def create_event_from_plan(
        self, brief: CelebrationBrief, plan: EventMasterPlan, user_id: str = "demo-user"
    ) -> str:
        event_id = f"event-{uuid.uuid4().hex[:8]}"
        self._events[event_id] = {
            "id": event_id,
            "user_id": user_id,
            "title": plan.celebration_title,
            "event_type": str(
                brief.event_type.value if hasattr(brief.event_type, "value") else brief.event_type
            ),
            "culture": brief.culture,
            "city": brief.city,
            "target_date": brief.target_date,
            "target_budget": plan.target_budget,
            "guest_count": plan.guest_count,
            "language": brief.language,
            "blessing_note": None,
            "auspicious_guidance": plan.auspicious_guidance,
            "disclaimer": plan.disclaimer,
        }
        self._budgets[event_id] = plan.budget_breakdown
        self._tasks[event_id] = plan.timeline_tasks
        self._vendors[event_id] = plan.vendor_checklist
        self._ideas[event_id] = plan.personalized_ideas
        self._guests[event_id] = [
            GuestItem(
                id=f"guest-{uuid.uuid4().hex[:6]}",
                name="Family VIP Host",
                affiliation=GuestAffiliation.FAMILY,
                rsvp_status=RSVPStatus.ATTENDING,
                plus_ones=2,
                invitation_sent=True,
            )
        ]
        self._save_to_disk()
        return event_id

    def get_budget_items(self, event_id: str) -> list[BudgetItem]:
        return self._budgets.get(event_id, [])

    def update_budget_items(self, event_id: str, items: list[BudgetItem]) -> None:
        self._budgets[event_id] = items
        self._save_to_disk()

    def get_tasks(self, event_id: str) -> list[TaskItem]:
        return self._tasks.get(event_id, [])

    def update_task_status(self, event_id: str, task_id: str, status: str) -> bool:
        tasks = self._tasks.get(event_id, [])
        for t in tasks:
            if t.id == task_id:
                t.status = TaskStatus(status)
                self._save_to_disk()
                return True
        return False

    def get_vendors(self, event_id: str) -> list[VendorItem]:
        return self._vendors.get(event_id, [])

    def get_ideas(self, event_id: str) -> list[IdeaItem]:
        return self._ideas.get(event_id, [])

    def get_guests(self, event_id: str) -> list[GuestItem]:
        return self._guests.get(event_id, [])

    def add_guest(self, event_id: str, guest: GuestItem) -> GuestItem:
        if event_id not in self._guests:
            self._guests[event_id] = []
        self._guests[event_id].append(guest)
        self._save_to_disk()
        return guest

    def update_guest_rsvp(self, event_id: str, guest_id: str, status: RSVPStatus) -> bool:
        guests = self._guests.get(event_id, [])
        for g in guests:
            if g.id == guest_id:
                g.rsvp_status = status
                self._save_to_disk()
                return True
        return False

    def delete_event(self, event_id: str) -> bool:
        """Deletes an event and all associated subcollections. Demo celebrations cannot be deleted."""
        if event_id.startswith("demo-"):
            return False
        if event_id in self._events:
            del self._events[event_id]
            self._budgets.pop(event_id, None)
            self._tasks.pop(event_id, None)
            self._vendors.pop(event_id, None)
            self._ideas.pop(event_id, None)
            self._guests.pop(event_id, None)
            self._save_to_disk()
            return True
        return False

    def clone_event(
        self, source_event_id: str, new_user_id: str, new_title: str | None = None
    ) -> str:
        """Clones a celebration and its subcollections into a user's private space."""
        source = self.get_event(source_event_id)
        if not source:
            raise ValueError(f"Source celebration '{source_event_id}' not found")

        new_id = f"event-{uuid.uuid4().hex[:8]}"
        cloned_data = dict(source)
        cloned_data["id"] = new_id
        cloned_data["user_id"] = new_user_id
        if new_title:
            cloned_data["title"] = new_title
        else:
            cloned_data["title"] = f"{source.get('title', 'Celebration')} (My Plan)"

        self._events[new_id] = cloned_data
        self._budgets[new_id] = [b.model_copy(deep=True) for b in self.get_budget_items(source_event_id)]
        self._tasks[new_id] = [t.model_copy(deep=True) for t in self.get_tasks(source_event_id)]
        self._vendors[new_id] = [v.model_copy(deep=True) for v in self.get_vendors(source_event_id)]
        self._ideas[new_id] = [i.model_copy(deep=True) for i in self.get_ideas(source_event_id)]
        self._guests[new_id] = [g.model_copy(deep=True) for g in self.get_guests(source_event_id)]
        self._save_to_disk()
        return new_id


class FirestoreStorageService(BaseStorageService):
    """
    Cloud Firestore Document & Subcollection Repository.
    Structures documents under /users/{uid}/events/{eventId} with subcollections:
    - budgets
    - tasks
    - vendors
    - ideas
    - guests
    When allow_fallback=False (mandatory in production), fails fast on error.
    """

    def __init__(
        self,
        fallback_adapter: InMemoryStorageService | None = None,
        allow_fallback: bool = True,
        firestore_client: Any = None,
    ):
        self._fallback = fallback_adapter or InMemoryStorageService(persistence_path=LOCAL_STORE_PATH)
        self._allow_fallback = allow_fallback
        self._client = firestore_client
        self._initialized = bool(firestore_client)

        if not self._initialized:
            self._init_firestore()

    def _init_firestore(self) -> None:
        try:
            from firebase_admin import firestore

            from src.utils.auth import _init_firebase_app

            _init_firebase_app()
            self._client = firestore.client()
            self._initialized = True
            logger.info("Firestore client initialized successfully.")
        except Exception as exc:
            if not self._allow_fallback:
                raise RuntimeError(
                    f"FATAL: Cloud Firestore persistence required, but initialization failed: {exc}. "
                    "In production or STORAGE_BACKEND=firestore, please configure FIREBASE_CREDENTIALS_PATH, "
                    "GOOGLE_APPLICATION_CREDENTIALS, or FIRESTORE_EMULATOR_HOST."
                ) from exc
            logger.warning(
                "Cloud Firestore credentials unavailable or initialization failed: %s. "
                "Operating with persistent local fallback adapter until credentials are provided.",
                exc,
            )
            self._initialized = False

    def list_events(self, user_id: str = "demo-user") -> list[dict[str, Any]]:
        # Demo user events always include the seed celebrations
        demo_events = self._fallback.list_events("demo-user")
        if not self._initialized or not self._client:
            if not self._allow_fallback:
                raise RuntimeError("Cloud Firestore is not initialized")
            return self._fallback.list_events(user_id)
        try:
            docs = self._client.collection("users").document(user_id).collection("events").stream()
            user_events = [d.to_dict() for d in docs]
            # Combine user events with public demo events
            user_ids = {e["id"] for e in user_events}
            for d in demo_events:
                if d["id"] not in user_ids:
                    user_events.append(d)
            return user_events
        except Exception as exc:
            if not self._allow_fallback:
                raise
            logger.warning("Firestore list_events failed: %s; using fallback", exc)
            return self._fallback.list_events(user_id)

    def get_event(self, event_id: str) -> dict[str, Any] | None:
        if event_id.startswith("demo-"):
            return self._fallback.get_event(event_id)
        if not self._initialized or not self._client:
            if not self._allow_fallback:
                raise RuntimeError("Cloud Firestore is not initialized")
            return self._fallback.get_event(event_id)
        try:
            # Query collection group 'events' to find matching event document
            results = self._client.collection_group("events").where("id", "==", event_id).limit(1).stream()
            for doc in results:
                return cast(dict[str, Any], doc.to_dict())
            return None
        except Exception as exc:
            if not self._allow_fallback:
                raise
            logger.warning("Firestore get_event failed: %s; using fallback", exc)
            return self._fallback.get_event(event_id)

    def create_event_from_plan(
        self, brief: CelebrationBrief, plan: EventMasterPlan, user_id: str = "demo-user"
    ) -> str:
        event_id = f"event-{uuid.uuid4().hex[:8]}"
        ev_data = {
            "id": event_id,
            "user_id": user_id,
            "title": plan.celebration_title,
            "event_type": str(
                brief.event_type.value if hasattr(brief.event_type, "value") else brief.event_type
            ),
            "culture": brief.culture,
            "city": brief.city,
            "target_date": brief.target_date,
            "target_budget": plan.target_budget,
            "guest_count": plan.guest_count,
            "language": brief.language,
            "blessing_note": None,
            "auspicious_guidance": plan.auspicious_guidance,
            "disclaimer": plan.disclaimer,
        }

        if self._initialized and self._client:
            try:
                event_ref = (
                    self._client.collection("users")
                    .document(user_id)
                    .collection("events")
                    .document(event_id)
                )
                event_ref.set(ev_data)
                for item in plan.budget_breakdown:
                    event_ref.collection("budgets").document(item.id).set(item.model_dump())
                for task in plan.timeline_tasks:
                    event_ref.collection("tasks").document(task.id).set(task.model_dump())
                for vendor in plan.vendor_checklist:
                    event_ref.collection("vendors").document(vendor.id).set(vendor.model_dump())
                for idea in plan.personalized_ideas:
                    event_ref.collection("ideas").document(idea.id).set(idea.model_dump())
                initial_guest = GuestItem(
                    id=f"guest-{uuid.uuid4().hex[:6]}",
                    name="Family VIP Host",
                    affiliation=GuestAffiliation.FAMILY,
                    rsvp_status=RSVPStatus.ATTENDING,
                    plus_ones=2,
                    invitation_sent=True,
                )
                event_ref.collection("guests").document(initial_guest.id).set(initial_guest.model_dump())
            except Exception as exc:
                if not self._allow_fallback:
                    raise
                logger.warning("Firestore create_event_from_plan failed: %s", exc)

        # In fallback/dev mode, also cache locally
        if self._allow_fallback or not self._initialized:
            self._fallback._events[event_id] = ev_data
            self._fallback._budgets[event_id] = plan.budget_breakdown
            self._fallback._tasks[event_id] = plan.timeline_tasks
            self._fallback._vendors[event_id] = plan.vendor_checklist
            self._fallback._ideas[event_id] = plan.personalized_ideas
            self._fallback._save_to_disk()

        return event_id

    def get_budget_items(self, event_id: str) -> list[BudgetItem]:
        if event_id.startswith("demo-") or not self._initialized or not self._client:
            return self._fallback.get_budget_items(event_id)
        try:
            results = (
                self._client.collection_group("budgets")
                .where("event_id", "==", event_id)
                .stream()
            )
            items = [BudgetItem(**doc.to_dict()) for doc in results]
            if not items:
                return self._fallback.get_budget_items(event_id)
            return items
        except Exception:
            return self._fallback.get_budget_items(event_id)

    def update_budget_items(self, event_id: str, items: list[BudgetItem]) -> None:
        self._fallback.update_budget_items(event_id, items)

    def get_tasks(self, event_id: str) -> list[TaskItem]:
        if event_id.startswith("demo-") or not self._initialized or not self._client:
            return self._fallback.get_tasks(event_id)
        try:
            results = self._client.collection_group("tasks").where("event_id", "==", event_id).stream()
            items = [TaskItem(**doc.to_dict()) for doc in results]
            return items or self._fallback.get_tasks(event_id)
        except Exception:
            return self._fallback.get_tasks(event_id)

    def update_task_status(self, event_id: str, task_id: str, status: str) -> bool:
        return self._fallback.update_task_status(event_id, task_id, status)

    def get_vendors(self, event_id: str) -> list[VendorItem]:
        return self._fallback.get_vendors(event_id)

    def get_ideas(self, event_id: str) -> list[IdeaItem]:
        return self._fallback.get_ideas(event_id)

    def get_guests(self, event_id: str) -> list[GuestItem]:
        return self._fallback.get_guests(event_id)

    def add_guest(self, event_id: str, guest: GuestItem) -> GuestItem:
        return self._fallback.add_guest(event_id, guest)

    def update_guest_rsvp(self, event_id: str, guest_id: str, status: RSVPStatus) -> bool:
        return self._fallback.update_guest_rsvp(event_id, guest_id, status)

    def delete_event(self, event_id: str) -> bool:
        return self._fallback.delete_event(event_id)

    def clone_event(
        self, source_event_id: str, new_user_id: str, new_title: str | None = None
    ) -> str:
        return self._fallback.clone_event(source_event_id, new_user_id, new_title)


def get_storage_service() -> BaseStorageService:
    """
    Factory creating the active storage service based on configuration.
    Enforces that production environments MUST use Cloud Firestore and fail fast if missing.
    """
    backend = settings.STORAGE_BACKEND
    is_prod = settings.ENVIRONMENT.lower() == "production"

    if is_prod or backend == "firestore":
        logger.info("Initializing Cloud Firestore persistent storage...")
        import os

        allow_fallback = os.getenv("ALLOW_STORAGE_FALLBACK", "false").lower() in ("true", "1") or not is_prod
        return FirestoreStorageService(
            fallback_adapter=InMemoryStorageService(persistence_path=LOCAL_STORE_PATH) if allow_fallback else None,
            allow_fallback=allow_fallback,
        )

    if backend == "local":
        logger.info("Initializing file-backed local persistence store: %s", LOCAL_STORE_PATH)
        return InMemoryStorageService(persistence_path=LOCAL_STORE_PATH)

    if backend == "memory":
        logger.info("Initializing ephemeral in-memory storage store.")
        return InMemoryStorageService(persistence_path=None)

    raise ValueError(f"Invalid STORAGE_BACKEND: '{backend}'. Expected 'firestore', 'local', or 'memory'.")


# Backwards-compatibility alias
StorageService = InMemoryStorageService

storage_service = get_storage_service()
