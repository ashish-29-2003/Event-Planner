"""
Google Calendar & RFC-5545 iCalendar (.ics) Service.
Enables instant synchronization of celebration milestones and ritual schedules.
"""

import urllib.parse
from datetime import datetime, timedelta, timezone

from src.models.timeline import TaskItem


def create_google_calendar_url(
    title: str, description: str, date_str: str | None = None, location: str = ""
) -> str:
    """
    Creates a deep-link URL to add an event directly into Google Calendar.
    """
    base_url = "https://calendar.google.com/calendar/render?action=TEMPLATE"
    params = {
        "text": f"Samaroh: {title}",
        "details": f"{description}\n\nOrganized via Samaroh (समारोह) - GenAI Celebration Planner",
        "location": location,
    }

    if date_str:
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%d")
            # Format as YYYYMMDDTHHMMSSZ (defaulting to 10:00 AM IST / 04:30 AM UTC)
            start_str = dt.strftime("%Y%m%dT043000Z")
            end_str = (dt + timedelta(hours=2)).strftime("%Y%m%dT063000Z")
            params["dates"] = f"{start_str}/{end_str}"
        except ValueError:
            pass

    return f"{base_url}&{urllib.parse.urlencode(params)}"


def generate_ics_calendar(event_title: str, tasks: list[TaskItem]) -> str:
    """
    Assembles a standards-compliant RFC-5545 iCalendar (.ics) string.
    Can be downloaded and imported into Google Calendar, Apple Calendar, or Outlook.
    """
    now_stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "PRODID:-//Samaroh//GenAI Celebration Planner//EN",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        f"X-WR-CALNAME:Samaroh - {event_title}",
    ]

    for task in tasks:
        due_date = task.due_date
        if not due_date:
            due_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")

        try:
            dt = datetime.strptime(due_date, "%Y-%m-%d")
            date_fmt = dt.strftime("%Y%m%d")
        except ValueError:
            date_fmt = datetime.now(timezone.utc).strftime("%Y%m%d")

        summary = task.title.replace("\n", " ").replace(";", "\\;")
        desc = f"{task.phase} | Owner: {task.owner_role} | {task.description}".replace(
            "\n", " "
        ).replace(";", "\\;")

        lines.extend(
            [
                "BEGIN:VEVENT",
                f"UID:samaroh-task-{task.id}@samaroh.app",
                f"DTSTAMP:{now_stamp}",
                f"DTSTART;VALUE=DATE:{date_fmt}",
                f"DTEND;VALUE=DATE:{date_fmt}",
                f"SUMMARY:Samaroh: {summary}",
                f"DESCRIPTION:{desc}",
                f"STATUS:{'COMPLETED' if task.status == 'done' else 'CONFIRMED'}",
                "END:VEVENT",
            ]
        )

    lines.append("END:VCALENDAR")
    return "\r\n".join(lines) + "\r\n"
