"""
Guest & RSVP Domain Models for Samaroh (समारोह).
Supports Indian celebration guest list management, dietary needs, side affiliation, and RSVP tracking.
"""

from enum import Enum

from pydantic import BaseModel, Field


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
    id: str = Field(..., description="Unique guest identifier")
    name: str = Field(..., description="Full name of the guest or family head")
    phone: str | None = Field(None, description="Contact phone number or WhatsApp")
    email: str | None = Field(None, description="Contact email address")
    affiliation: GuestAffiliation = Field(
        GuestAffiliation.FAMILY, description="Relationship or side affiliation"
    )
    rsvp_status: RSVPStatus = Field(
        RSVPStatus.PENDING, description="Current RSVP confirmation status"
    )
    plus_ones: int = Field(0, ge=0, description="Additional attendees accompanied")
    dietary_preference: str = Field("Vegetarian", description="Dietary or prasad requirements")
    invitation_sent: bool = Field(False, description="Whether digital Patrika / invite was sent")
    notes: str | None = Field(None, description="Accommodation or travel notes")
