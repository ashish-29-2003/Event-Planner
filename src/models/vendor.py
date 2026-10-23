"""
Vendor checklist, quote tracking, and procurement data models.
"""
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

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
    id: str = Field(..., description="Unique vendor ID")
    event_id: Optional[str] = Field(None, description="Associated celebration ID")
    category: str = Field(..., description="Category: venue, catering, decor, photography, etc.")
    business_name: str = Field(..., description="Vendor trade or business name")
    contact_person: Optional[str] = Field(None, description="Point of contact name")
    phone: Optional[str] = Field(None, description="Contact phone or WhatsApp")
    email: Optional[str] = Field(None, description="Contact email")
    quote_amount: float = Field(0.0, ge=0, description="Quoted amount in INR")
    status: VendorStatus = Field(VendorStatus.TO_RESEARCH)
    notes: Optional[str] = Field(None, description="Deliverables, scope, or terms")
    address: Optional[str] = Field(None, description="Vendor city or location")
    rating: Optional[float] = Field(4.8, ge=1.0, le=5.0)
    is_estimate: bool = Field(True, description="Flag indicating price is an estimate")
