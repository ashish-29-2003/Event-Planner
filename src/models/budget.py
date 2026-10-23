"""
Budget and expense data models with AI re-balancing schemas.
"""

from enum import Enum

from pydantic import BaseModel, Field


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PARTIAL = "partial"
    PAID = "paid"


class BudgetItem(BaseModel):
    id: str = Field(..., description="Unique line item ID")
    event_id: str | None = Field(None, description="Associated celebration ID")
    category: str = Field(
        ..., description="e.g. Venue, Catering, Decor, Photography, Entertainment"
    )
    name: str = Field(..., description="Expense item title")
    estimated_cost: float = Field(..., ge=0, description="Estimated cost in INR")
    actual_cost: float = Field(0.0, ge=0, description="Actual confirmed cost in INR")
    advance_paid: float = Field(0.0, ge=0, description="Advance payment paid so far")
    status: PaymentStatus = Field(PaymentStatus.PENDING, description="Current payment status")
    notes: str | None = Field(None, description="Vendor payment terms or notes")


class CategoryAllocation(BaseModel):
    name: str
    allocated_amount: float = Field(..., ge=0)
    percentage_of_total: float = Field(..., ge=0, le=100)


class BudgetRebalanceRequest(BaseModel):
    target_budget: float = Field(..., gt=0)
    changed_category: str = Field(...)
    new_amount: float = Field(..., ge=0)
    current_items: list[BudgetItem]


class BudgetRebalanceResponse(BaseModel):
    categories: list[CategoryAllocation]
    updated_items: list[BudgetItem]
    total_allocated: float
    target_budget: float
    variance: float
    rebalance_rationale: str
