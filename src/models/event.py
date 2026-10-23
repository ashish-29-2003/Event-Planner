"""
Event entity data models using Pydantic v2.
"""

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, Field


class EventType(str, Enum):
    WEDDING = "wedding"
    BIRTHDAY = "birthday"
    COMMUNITY = "community"
    FESTIVAL = "festival"
    OTHER = "other"


class CelebrationBrief(BaseModel):
    title: str = Field(..., min_length=2, max_length=100, description="Title of the celebration")
    event_type: EventType = Field(EventType.WEDDING, description="Category of celebration")
    culture: str = Field(
        "Contemporary Indian",
        min_length=2,
        max_length=60,
        description="Cultural or regional tradition",
    )
    city: str = Field("Jaipur", min_length=2, max_length=60, description="Host city in India")
    target_date: str | None = Field(
        "2026-12-15", description="Target celebration date (YYYY-MM-DD)"
    )
    target_budget: float = Field(..., gt=0, le=100_000_000, description="Target budget in INR")
    guest_count: int = Field(..., gt=0, le=50_000, description="Estimated guest count")
    language: str = Field("en", description="Preferred language ('en' or 'hi')")
    notes: str | None = Field(
        None, max_length=1000, description="Special dietary or ceremonial notes"
    )


class EventCreate(CelebrationBrief):
    user_id: str | None = Field("demo-user", description="Authenticated user ID or guest session")
    blessing_note: str | None = Field(None, max_length=300, description="Family blessing note")


class EventResponse(EventCreate):
    id: str = Field(..., description="Unique celebration ID")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
