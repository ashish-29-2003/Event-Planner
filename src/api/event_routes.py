"""
Event & Entity CRUD Route Handlers for Samaroh (समारोह).
Enforces owner verification, tenant isolation, and Firebase identity.
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel

from src.models.budget import BudgetItem
from src.models.guest import GuestItem, RSVPStatus
from src.services.storage_service import storage_service
from src.utils.auth import (
    AuthenticatedUser,
    get_current_user_or_demo,
    require_authenticated_user,
)

router = APIRouter(prefix="/api/events", tags=["Celebrations"])


class TaskToggleRequest(BaseModel):
    status: str


class GuestRSVPRequest(BaseModel):
    status: RSVPStatus


@router.get("")
async def list_celebrations(
    user: AuthenticatedUser = Depends(get_current_user_or_demo),
):
    """Lists all celebrations for the active user plus public demo celebrations."""
    return storage_service.list_events(user.uid)


@router.get("/{event_id}")
async def get_celebration(
    event_id: str,
    user: AuthenticatedUser = Depends(get_current_user_or_demo),
):
    """Retrieves full metadata for a specific celebration."""
    event = storage_service.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Celebration not found")
    if not event_id.startswith("demo-") and event.get("user_id") != user.uid:
        raise HTTPException(
            status_code=403,
            detail="Access denied: celebration belongs to another user",
        )
    return event


@router.get("/{event_id}/budget")
async def get_event_budget(
    event_id: str,
    user: AuthenticatedUser = Depends(get_current_user_or_demo),
):
    """Retrieves all budget line items for an event."""
    event = storage_service.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Celebration not found")
    if not event_id.startswith("demo-") and event.get("user_id") != user.uid:
        raise HTTPException(
            status_code=403,
            detail="Access denied: celebration belongs to another user",
        )
    return storage_service.get_budget_items(event_id)


@router.put("/{event_id}/budget")
async def update_event_budget(
    event_id: str,
    items: list[BudgetItem],
    user: AuthenticatedUser = Depends(require_authenticated_user),
):
    """Updates budget items after manual edits or AI re-balancing. Requires authentication."""
    event = storage_service.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Celebration not found")
    if not event_id.startswith("demo-") and event.get("user_id") != user.uid:
        raise HTTPException(
            status_code=403,
            detail="Access denied: cannot modify another user's budget",
        )
    storage_service.update_budget_items(event_id, items)
    return {"success": True, "count": len(items)}


@router.get("/{event_id}/tasks")
async def get_event_tasks(
    event_id: str,
    user: AuthenticatedUser = Depends(get_current_user_or_demo),
):
    """Retrieves all timeline milestone tasks for an event."""
    event = storage_service.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Celebration not found")
    if not event_id.startswith("demo-") and event.get("user_id") != user.uid:
        raise HTTPException(
            status_code=403,
            detail="Access denied: celebration belongs to another user",
        )
    return storage_service.get_tasks(event_id)


@router.post("/{event_id}/tasks/{task_id}/toggle")
async def toggle_task_status(
    event_id: str,
    task_id: str,
    req: TaskToggleRequest,
    user: AuthenticatedUser = Depends(require_authenticated_user),
):
    """Toggles task status between todo, in_progress, and done. Requires authentication."""
    event = storage_service.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Celebration not found")
    if not event_id.startswith("demo-") and event.get("user_id") != user.uid:
        raise HTTPException(
            status_code=403,
            detail="Access denied: cannot modify another user's tasks",
        )
    success = storage_service.update_task_status(event_id, task_id, req.status)
    if not success:
        raise HTTPException(status_code=404, detail="Task not found")
    return {"success": True, "task_id": task_id, "status": req.status}


@router.get("/{event_id}/vendors")
async def get_event_vendors(
    event_id: str,
    user: AuthenticatedUser = Depends(get_current_user_or_demo),
):
    """Retrieves categorized vendors and quotes for an event."""
    event = storage_service.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Celebration not found")
    if not event_id.startswith("demo-") and event.get("user_id") != user.uid:
        raise HTTPException(
            status_code=403,
            detail="Access denied: celebration belongs to another user",
        )
    return storage_service.get_vendors(event_id)


@router.get("/{event_id}/ideas")
async def get_event_ideas(
    event_id: str,
    user: AuthenticatedUser = Depends(get_current_user_or_demo),
):
    """Retrieves curated cultural suggestions across 6 dimensions."""
    event = storage_service.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Celebration not found")
    if not event_id.startswith("demo-") and event.get("user_id") != user.uid:
        raise HTTPException(
            status_code=403,
            detail="Access denied: celebration belongs to another user",
        )
    return storage_service.get_ideas(event_id)


@router.get("/{event_id}/guests")
async def get_event_guests(
    event_id: str,
    user: AuthenticatedUser = Depends(get_current_user_or_demo),
):
    """Retrieves guest list and RSVP status for an event."""
    event = storage_service.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Celebration not found")
    if not event_id.startswith("demo-") and event.get("user_id") != user.uid:
        raise HTTPException(
            status_code=403,
            detail="Access denied: celebration belongs to another user",
        )
    return storage_service.get_guests(event_id)


@router.post("/{event_id}/guests")
async def add_event_guest(
    event_id: str,
    guest: GuestItem,
    user: AuthenticatedUser = Depends(require_authenticated_user),
):
    """Adds a new guest to the celebration guest list. Requires authentication."""
    event = storage_service.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Celebration not found")
    if not event_id.startswith("demo-") and event.get("user_id") != user.uid:
        raise HTTPException(
            status_code=403,
            detail="Access denied: cannot add guests to another user's event",
        )
    created = storage_service.add_guest(event_id, guest)
    return {"success": True, "guest": created}


@router.post("/{event_id}/guests/{guest_id}/rsvp")
async def update_guest_rsvp(
    event_id: str,
    guest_id: str,
    req: GuestRSVPRequest,
    user: AuthenticatedUser = Depends(get_current_user_or_demo),
):
    """Updates a guest's RSVP status."""
    event = storage_service.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Celebration not found")
    if not event_id.startswith("demo-") and event.get("user_id") != user.uid:
        raise HTTPException(
            status_code=403,
            detail="Access denied",
        )
    success = storage_service.update_guest_rsvp(event_id, guest_id, req.status)
    if not success:
        raise HTTPException(status_code=404, detail="Guest not found")
    return {"success": True, "guest_id": guest_id, "status": req.status}
