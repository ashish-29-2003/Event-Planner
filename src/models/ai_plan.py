"""
Unified EventMasterPlan schema used for Google Gemini structured outputs.
"""

from pydantic import BaseModel, Field

from .budget import BudgetItem
from .ideas import IdeaItem
from .timeline import TaskItem
from .vendor import VendorItem


class EventMasterPlan(BaseModel):
    celebration_title: str = Field(..., description="Personalized celebration title")
    event_type: str = Field(..., description="wedding, birthday, community, etc.")
    cultural_summary: str = Field(..., description="Cultural essence and traditions honored")
    target_budget: float = Field(..., ge=0, description="Target master budget in INR")
    guest_count: int = Field(..., gt=0, description="Confirmed guest count")
    budget_breakdown: list[BudgetItem] = Field(..., description="Category-wise budget allocations")
    timeline_tasks: list[TaskItem] = Field(..., description="Phased timeline milestones")
    vendor_checklist: list[VendorItem] = Field(..., description="Key vendor requirements")
    personalized_ideas: list[IdeaItem] = Field(..., description="Curated ideas across 6 dimensions")
    auspicious_guidance: str | None = Field(None, description="Auspicious muhurat or seasonal tips")
    disclaimer: str = Field(
        "Notice: Timings, muhurat guidance, and vendor quotes are AI-assisted estimates for budgeting purposes only.",
        description="Mandatory planning disclaimer",
    )
