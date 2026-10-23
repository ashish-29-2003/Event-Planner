"""
Export & Sharing Route Handlers for Utsav (उत्सव).
Generates RFC-5545 iCalendar (.ics) files and printable summaries.
"""
from fastapi import APIRouter, HTTPException, Response
from src.services.storage_service import storage_service
from src.services.calendar_service import generate_ics_calendar, create_google_calendar_url

router = APIRouter(prefix="/api/export", tags=["Exports & Calendar"])

@router.get("/{event_id}/calendar")
async def export_calendar_ics(event_id: str):
    """
    Downloads RFC-5545 .ics file for calendar synchronization.
    """
    event = storage_service.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Celebration not found")
        
    tasks = storage_service.get_tasks(event_id)
    ics_content = generate_ics_calendar(event.get("title", "Celebration"), tasks)
    
    return Response(
        content=ics_content,
        media_type="text/calendar",
        headers={
            "Content-Disposition": f"attachment; filename=utsav-{event_id}.ics"
        }
    )

@router.get("/{event_id}/next-milestone-link")
async def get_next_milestone_gcal_link(event_id: str):
    """
    Returns a direct Google Calendar deep link for the earliest upcoming milestone.
    """
    event = storage_service.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Celebration not found")
        
    tasks = storage_service.get_tasks(event_id)
    upcoming_tasks = [t for t in tasks if t.status != "done" and t.due_date]
    
    if not upcoming_tasks:
        target_task = tasks[0] if tasks else None
    else:
        target_task = upcoming_tasks[0]
        
    if not target_task:
        raise HTTPException(status_code=404, detail="No tasks found for event")
        
    url = create_google_calendar_url(
        title=target_task.title,
        description=target_task.description,
        date_str=target_task.due_date,
        location=event.get("city", "India")
    )
    
    return {
        "task_title": target_task.title,
        "due_date": target_task.due_date,
        "google_calendar_url": url
    }

@router.get("/{event_id}/summary")
async def get_export_summary(event_id: str):
    """
    Returns consolidated celebration data for printable view or PDF export.
    """
    event = storage_service.get_event(event_id)
    if not event:
        raise HTTPException(status_code=404, detail="Celebration not found")
        
    return {
        "event": event,
        "budgets": storage_service.get_budget_items(event_id),
        "tasks": storage_service.get_tasks(event_id),
        "vendors": storage_service.get_vendors(event_id),
        "ideas": storage_service.get_ideas(event_id)
    }
