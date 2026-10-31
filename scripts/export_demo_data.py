"""
Export Seed Celebrations to Static JSON Files for Degraded Demo Mode.
Extracts curated seed data from Samaroh's Python models and writes them to
public/demo-data/ so the web application can browse the four pillars
even during extended backend cold starts or connectivity interruptions.
"""

import json
import sys
from pathlib import Path

# Ensure project root is on sys.path
ROOT_DIR = Path(__file__).resolve().parent.parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from src.services.storage_service import InMemoryStorageService

PUBLIC_DEMO_DIR = Path(__file__).resolve().parent.parent / "public" / "demo-data"


def export_demo_data() -> None:
    PUBLIC_DEMO_DIR.mkdir(parents=True, exist_ok=True)
    store = InMemoryStorageService(persistence_path=None)

    events = store.list_events("demo-user")
    events_path = PUBLIC_DEMO_DIR / "events.json"
    events_path.write_text(json.dumps(events, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Exported {len(events)} demo events to {events_path}")

    for event in events:
        eid = event["id"]
        # 1. Event details
        (PUBLIC_DEMO_DIR / f"{eid}.json").write_text(
            json.dumps(event, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        # 2. Budget
        budgets = [b.model_dump() for b in store.get_budget_items(eid)]
        (PUBLIC_DEMO_DIR / f"{eid}_budget.json").write_text(
            json.dumps(budgets, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        # 3. Tasks
        tasks = [t.model_dump() for t in store.get_tasks(eid)]
        (PUBLIC_DEMO_DIR / f"{eid}_tasks.json").write_text(
            json.dumps(tasks, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        # 4. Vendors
        vendors = [v.model_dump() for v in store.get_vendors(eid)]
        (PUBLIC_DEMO_DIR / f"{eid}_vendors.json").write_text(
            json.dumps(vendors, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        # 5. Ideas
        ideas = [i.model_dump() for i in store.get_ideas(eid)]
        (PUBLIC_DEMO_DIR / f"{eid}_ideas.json").write_text(
            json.dumps(ideas, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        # 6. Guests
        guests = [g.model_dump() for g in store.get_guests(eid)]
        (PUBLIC_DEMO_DIR / f"{eid}_guests.json").write_text(
            json.dumps(guests, indent=2, ensure_ascii=False), encoding="utf-8"
        )
        print(f"Exported all subcollections for {eid}")

    print("Demo data export completed successfully.")


if __name__ == "__main__":
    export_demo_data()
