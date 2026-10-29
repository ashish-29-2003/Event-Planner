"""
Guest & RSVP Domain Models for Samaroh (समारोह) with strict input validation boundaries.
Supports Indian celebration guest list management, dietary needs, side affiliation, and RSVP tracking.
"""

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class RSVPStatus(str, Enum):
    ATTENDING = "attending"
    DECLINED = "declined"
    PENDING = "pending"
    TENTATIVE = "tentative"


class GuestAffiliation(str, Enum):
    BRIDE_SIDE = "bride_side"
    GROOM_SIDE = "groom_side"
    FAMILY = "family"
    FRIEND = "friend"
    COMMUNITY = "community"
    COLLEAGUE = "colleague"


class GuestItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., min_length=1, max_length=64, description="Unique guest identifier")
    name: str = Field(..., min_length=2, max_length=100, description="Full name of the guest or family head")
    phone: str | None = Field(None, max_length=20, description="Contact phone number or WhatsApp")
    email: str | None = Field(None, max_length=120, description="Contact email address")
    affiliation: GuestAffiliation = Field(
        GuestAffiliation.FAMILY, description="Relationship or side affiliation"
    )
    rsvp_status: RSVPStatus = Field(
        RSVPStatus.PENDING, description="Current RSVP confirmation status"
    )
    plus_ones: int = Field(0, ge=0, le=20, description="Additional attendees accompanied")
    dietary_preference: str = Field("Vegetarian", max_length=64, description="Dietary or prasad requirements")
    invitation_sent: bool = Field(False, description="Whether digital Patrika / invite was sent")
    notes: str | None = Field(None, max_length=500, description="Accommodation or travel notes")
