"""
Event & Entity CRUD Route Handlers for Utsav (उत्सव).
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from src.models.budget import BudgetItem
from src.services.storage_service import storage_service

router = APIRouter(prefix="/api/events", tags=["Celebrations"])

class TaskToggleRequest(BaseModel):
    status: str

@router.get("")
async def list_celebrations(user_id: str = "demo-user"):
    """Lists all celebrations for the active user."""
    return storage_service.list_events(user_id)

@router.get("/{event_id}")
async def get_celebration(event_id: str):
    """Retrieves full metadata for a specific celebration."""
    event = storage_service.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Celebration not found")
    return event

@router.get("/{event_id}/budget")
async def get_event_budget(event_id: str):
    """Retrieves all budget line items for an event."""
    return storage_service.get_budget_items(event_id)

@router.put("/{event_id}/budget")
async def update_event_budget(event_id: str, items: list[BudgetItem]):
    """Updates budget items after manual edits or AI re-balancing."""
    storage_service.update_budget_items(event_id, items)
    return {"success": True, "count": len(items)}

@router.get("/{event_id}/tasks")
async def get_event_tasks(event_id: str):
    """Retrieves all timeline milestone tasks for an event."""
    return storage_service.get_tasks(event_id)

@router.post("/{event_id}/tasks/{task_id}/toggle")
async def toggle_task_status(event_id: str, task_id: str, req: TaskToggleRequest):
    """Toggles task status between todo, in_progress, and done."""
    success = storage_service.update_task_status(event_id, task_id, req.status)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"success": True, "task_id": task_id, "status": req.status}

@router.get("/{event_id}/vendors")
async def get_event_vendors(event_id: str):
    """Retrieves categorized vendors and quotes for an event."""
    return storage_service.get_vendors(event_id)

@router.get("/{event_id}/ideas")
async def get_event_ideas(event_id: str):
    """Retrieves curated cultural suggestions across 6 dimensions."""
    return storage_service.get_ideas(event_id)
