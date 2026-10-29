"""
Event entity data models using Pydantic v2 with strict input boundaries.
"""

from datetime import datetime, timezone
from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class EventType(str, Enum):
    WEDDING = "wedding"
    BIRTHDAY = "birthday"
    COMMUNITY = "community"
    FESTIVAL = "festival"
    OTHER = "other"


class CelebrationBrief(BaseModel):
    model_config = ConfigDict(extra="forbid")

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
        "2026-12-15", min_length=8, max_length=12, description="Target celebration date (YYYY-MM-DD)"
    )
    target_budget: float = Field(..., gt=0, le=100_000_000, description="Target budget in INR")
    guest_count: int = Field(..., gt=0, le=50_000, description="Estimated guest count")
    language: str = Field("en", min_length=2, max_length=5, description="Preferred language ('en' or 'hi')")
    notes: str | None = Field(
        None, max_length=1000, description="Special dietary or ceremonial notes"
    )


class EventCreate(CelebrationBrief):
    model_config = ConfigDict(extra="forbid")

    user_id: str | None = Field("demo-user", max_length=128, description="Authenticated user ID or guest session")
    blessing_note: str | None = Field(None, max_length=300, description="Family blessing note")


class EventResponse(EventCreate):
    model_config = ConfigDict(extra="ignore")

    id: str = Field(..., description="Unique celebration ID")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
