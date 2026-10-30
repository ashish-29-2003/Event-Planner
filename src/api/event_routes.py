"""
Event & Entity CRUD Route Handlers for Samaroh (समारोह).
Enforces owner verification, tenant isolation, read-only demo protections, and Firebase identity.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict, Field

from src.models.budget import BudgetItem
from src.models.guest import GuestItem, RSVPStatus
from src.models.ideas import IdeaItem
from src.models.timeline import TaskItem
from src.models.vendor import VendorItem
from src.services.storage_service import storage_service
from src.utils.auth import (
    AuthenticatedUser,
    get_current_user_or_demo,
    require_authenticated_user,
)

router = APIRouter(prefix="/api/events", tags=["Celebrations"])


class TaskToggleRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: str = Field(..., min_length=2, max_length=20)


class GuestRSVPRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    status: RSVPStatus


class CloneEventRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    title: str | None = Field(None, min_length=2, max_length=100)


@router.get("")
async def list_celebrations(
    user: AuthenticatedUser = Depends(get_current_user_or_demo),
) -> list[dict[str, Any]]:
    """Lists all celebrations for the active user plus public demo celebrations."""
    return storage_service.list_events(user.uid)


@router.get("/{event_id}")
async def get_celebration(
    event_id: str,
    user: AuthenticatedUser = Depends(get_current_user_or_demo),
) -> dict[str, Any]:
    """Retrieves full metadata for a specific celebration."""
    event = storage_service.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Celebration not found")
    if not event_id.startswith("demo-") and event.get("user_id") != user.uid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: celebration belongs to another user",
        )
    return event


@router.delete("/{event_id}")
async def delete_celebration(
    event_id: str,
    user: AuthenticatedUser = Depends(require_authenticated_user),
) -> dict[str, Any]:
    """Deletes a celebration. Requires owner authentication. Demo celebrations cannot be deleted."""
    if event_id.startswith("demo-"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Demo celebrations are read-only templates and cannot be deleted.",
        )
    event = storage_service.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Celebration not found")
    if event.get("user_id") != user.uid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: cannot delete another user's celebration",
        )
    success = storage_service.delete_event(event_id)
    return {"success": success, "deleted": event_id}


@router.post("/{event_id}/clone")
async def clone_celebration(
    event_id: str,
    req: CloneEventRequest | None = None,
    user: AuthenticatedUser = Depends(require_authenticated_user),
) -> dict[str, Any]:
    """Clones an existing celebration (including demo templates) into the user's private space."""
    event = storage_service.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Celebration not found")
    if not event_id.startswith("demo-") and event.get("user_id") != user.uid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: cannot clone private celebration of another user",
        )

    # Per-user quota check
    existing_events = [
        e for e in storage_service.list_events(user.uid) if not e.get("id", "").startswith("demo-")
    ]
    if len(existing_events) >= 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Celebration quota reached: maximum 20 celebrations per user account.",
        )

    new_id = storage_service.clone_event(
        source_event_id=event_id,
        new_user_id=user.uid,
        new_title=req.title if req else None,
    )
    return {"success": True, "event_id": new_id}


@router.get("/{event_id}/budget")
async def get_event_budget(
    event_id: str,
    user: AuthenticatedUser = Depends(get_current_user_or_demo),
) -> list[BudgetItem]:
    """Retrieves all budget line items for an event."""
    event = storage_service.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Celebration not found")
    if not event_id.startswith("demo-") and event.get("user_id") != user.uid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: celebration belongs to another user",
        )
    return storage_service.get_budget_items(event_id)


@router.put("/{event_id}/budget")
async def update_event_budget(
    event_id: str,
    items: list[BudgetItem],
    user: AuthenticatedUser = Depends(require_authenticated_user),
) -> dict[str, Any]:
    """Updates budget items. Demo celebrations are read-only and return 403."""
    if event_id.startswith("demo-"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Demo celebrations are read-only templates. Clone or create your own celebration to edit.",
        )
    event = storage_service.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Celebration not found")
    if event.get("user_id") != user.uid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: cannot modify another user's budget",
        )
    storage_service.update_budget_items(event_id, items)
    return {"success": True, "count": len(items)}


@router.get("/{event_id}/tasks")
async def get_event_tasks(
    event_id: str,
    user: AuthenticatedUser = Depends(get_current_user_or_demo),
) -> list[TaskItem]:
    """Retrieves all timeline milestone tasks for an event."""
    event = storage_service.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Celebration not found")
    if not event_id.startswith("demo-") and event.get("user_id") != user.uid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: celebration belongs to another user",
        )
    return storage_service.get_tasks(event_id)


@router.post("/{event_id}/tasks/{task_id}/toggle")
async def toggle_task_status(
    event_id: str,
    task_id: str,
    req: TaskToggleRequest,
    user: AuthenticatedUser = Depends(require_authenticated_user),
) -> dict[str, Any]:
    """Toggles task status. Demo celebrations are read-only and return 403."""
    if event_id.startswith("demo-"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Demo celebrations are read-only templates. Clone or create your own celebration to edit.",
        )
    event = storage_service.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Celebration not found")
    if event.get("user_id") != user.uid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
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
) -> list[VendorItem]:
    """Retrieves categorized vendors and quotes for an event."""
    event = storage_service.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Celebration not found")
    if not event_id.startswith("demo-") and event.get("user_id") != user.uid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: celebration belongs to another user",
        )
    return storage_service.get_vendors(event_id)


@router.get("/{event_id}/ideas")
async def get_event_ideas(
    event_id: str,
    user: AuthenticatedUser = Depends(get_current_user_or_demo),
) -> list[IdeaItem]:
    """Retrieves curated cultural suggestions across 6 dimensions."""
    event = storage_service.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Celebration not found")
    if not event_id.startswith("demo-") and event.get("user_id") != user.uid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: celebration belongs to another user",
        )
    return storage_service.get_ideas(event_id)


@router.get("/{event_id}/guests")
async def get_event_guests(
    event_id: str,
    user: AuthenticatedUser = Depends(get_current_user_or_demo),
) -> list[GuestItem]:
    """Retrieves guest list and RSVP status for an event."""
    event = storage_service.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Celebration not found")
    if not event_id.startswith("demo-") and event.get("user_id") != user.uid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: celebration belongs to another user",
        )
    return storage_service.get_guests(event_id)


@router.post("/{event_id}/guests")
async def add_event_guest(
    event_id: str,
    guest: GuestItem,
    user: AuthenticatedUser = Depends(require_authenticated_user),
) -> dict[str, Any]:
    """Adds a guest to the guest list. Demo celebrations are read-only and return 403."""
    if event_id.startswith("demo-"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Demo celebrations are read-only templates. Clone or create your own celebration to edit.",
        )
    event = storage_service.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Celebration not found")
    if event.get("user_id") != user.uid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: cannot add guests to another user's event",
        )
    created = storage_service.add_guest(event_id, guest)
    return {"success": True, "guest": created}


@router.post("/{event_id}/guests/{guest_id}/rsvp")
async def update_guest_rsvp(
    event_id: str,
    guest_id: str,
    req: GuestRSVPRequest,
    user: AuthenticatedUser = Depends(require_authenticated_user),
) -> dict[str, Any]:
    """Updates a guest's RSVP status. Demo celebrations are read-only and return 403."""
    if event_id.startswith("demo-"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Demo celebrations are read-only templates. Clone or create your own celebration to edit.",
        )
    event = storage_service.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Celebration not found")
    if event.get("user_id") != user.uid:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: cannot update another user's guest RSVP",
        )
    success = storage_service.update_guest_rsvp(event_id, guest_id, req.status)
    if not success:
        raise HTTPException(status_code=404, detail="Guest not found")
    return {"success": True, "guest_id": guest_id, "status": req.status}
