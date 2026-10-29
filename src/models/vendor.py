"""
Vendor checklist, quote tracking, and procurement data models with strict input boundaries.
"""

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class VendorCategory(str, Enum):
    VENUE = "venue"
    CATERING = "catering"
    DECOR = "decor"
    PHOTOGRAPHY = "photography"
    MEHENDI_MAKEUP = "mehendi_makeup"
    MUSIC_ENTERTAINMENT = "music_entertainment"
    PANDIT_OFFICIANT = "pandit_officiant"
    TRANSPORT_LOGISTICS = "transport_logistics"
    INVITATIONS_GIFTS = "invitations_gifts"
    MISC = "misc"


class VendorStatus(str, Enum):
    TO_RESEARCH = "to_research"
    CONTACTED = "contacted"
    SHORTLISTED = "shortlisted"
    BOOKED = "booked"
    DECLINED = "declined"


class VendorItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., min_length=1, max_length=64, description="Unique vendor ID")
    event_id: str | None = Field(None, max_length=64, description="Associated celebration ID")
    category: str = Field(..., min_length=2, max_length=64, description="Category: venue, catering, decor, photography, etc.")
    business_name: str = Field(..., min_length=2, max_length=150, description="Vendor trade or business name")
    contact_person: str | None = Field(None, max_length=100, description="Point of contact name")
    phone: str | None = Field(None, max_length=20, description="Contact phone or WhatsApp")
    email: str | None = Field(None, max_length=120, description="Contact email")
    quote_amount: float = Field(0.0, ge=0, le=100_000_000, description="Quoted amount in INR")
    status: VendorStatus = Field(VendorStatus.TO_RESEARCH)
    notes: str | None = Field(None, max_length=1000, description="Deliverables, scope, or terms")
    address: str | None = Field(None, max_length=250, description="Vendor city or location")
    rating: float | None = Field(4.8, ge=1.0, le=5.0)
    is_estimate: bool = Field(True, description="Flag indicating price is an estimate")
