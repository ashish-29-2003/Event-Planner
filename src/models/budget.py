"""
Budget and expense data models with AI re-balancing schemas and strict input boundaries.
"""

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PARTIAL = "partial"
    PAID = "paid"


class BudgetItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., min_length=1, max_length=64, description="Unique line item ID")
    event_id: str | None = Field(None, max_length=64, description="Associated celebration ID")
    category: str = Field(
        ..., min_length=2, max_length=64, description="e.g. Venue, Catering, Decor, Photography, Entertainment"
    )
    name: str = Field(..., min_length=2, max_length=128, description="Expense item title")
    estimated_cost: float = Field(..., ge=0, le=100_000_000, description="Estimated cost in INR")
    actual_cost: float = Field(0.0, ge=0, le=100_000_000, description="Actual confirmed cost in INR")
    advance_paid: float = Field(0.0, ge=0, le=100_000_000, description="Advance payment paid so far")
    status: PaymentStatus = Field(PaymentStatus.PENDING, description="Current payment status")
    notes: str | None = Field(None, max_length=500, description="Vendor payment terms or notes")


class CategoryAllocation(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str = Field(..., min_length=2, max_length=64)
    allocated_amount: float = Field(..., ge=0, le=100_000_000)
    percentage_of_total: float = Field(..., ge=0, le=100)


class BudgetRebalanceRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    target_budget: float = Field(..., gt=0, le=100_000_000)
    changed_category: str = Field(..., min_length=2, max_length=64)
    new_amount: float = Field(..., ge=0, le=100_000_000)
    current_items: list[BudgetItem] = Field(..., max_length=200)


class BudgetRebalanceResponse(BaseModel):
    model_config = ConfigDict(extra="ignore")

    categories: list[CategoryAllocation]
    updated_items: list[BudgetItem]
    total_allocated: float
    target_budget: float
    variance: float
    rebalance_rationale: str
