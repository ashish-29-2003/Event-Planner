"""
Event entity data models using Pydantic v2.
"""
from enum import Enum
from typing import Optional
from datetime import date, datetime
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
    culture: str = Field("Contemporary Indian", min_length=2, max_length=60, description="Cultural or regional tradition")
    city: str = Field("Jaipur", min_length=2, max_length=60, description="Host city in India")
    target_date: Optional[str] = Field("2026-12-15", description="Target celebration date (YYYY-MM-DD)")
    target_budget: float = Field(..., gt=0, le=100_000_000, description="Target budget in INR")
    guest_count: int = Field(..., gt=0, le=50_000, description="Estimated guest count")
    language: str = Field("en", description="Preferred language ('en' or 'hi')")
    notes: Optional[str] = Field(None, max_length=1000, description="Special dietary or ceremonial notes")

class EventCreate(CelebrationBrief):
    user_id: Optional[str] = Field("demo-user", description="Authenticated user ID or guest session")
    blessing_note: Optional[str] = Field(None, max_length=300, description="Family blessing note")

class EventResponse(EventCreate):
    id: str = Field(..., description="Unique celebration ID")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
