"""
Unit tests for Budget math, calculation, and AI re-balancing logic.
"""

import pytest

from src.models.budget import BudgetItem, BudgetRebalanceRequest
from src.services.gemini_service import gemini_service
from src.utils.currency import format_inr, format_lakhs_crores


def test_currency_formatting_indian_lakhs():
    assert format_inr(1250000) == "₹12,50,000"
    assert format_inr(45000000) == "₹4,50,00,000"
    assert format_lakhs_crores(4500000) == "₹45.0 Lakh"
    assert format_lakhs_crores(12500000) == "₹1.25 Cr"


@pytest.mark.asyncio
async def test_budget_rebalancing_math():
    items = [
        BudgetItem(id="1", category="Venue", name="Palace", estimated_cost=1000000.0),
        BudgetItem(id="2", category="Catering", name="Feast", estimated_cost=1000000.0),
        BudgetItem(id="3", category="Decor", name="Florals", estimated_cost=1000000.0),
    ]
    target_budget = 3000000.0

    # Increase Venue from 1,000,000 to 1,500,000
    req = BudgetRebalanceRequest(
        target_budget=target_budget,
        changed_category="Venue",
        new_amount=1500000.0,
        current_items=items,
    )

    response = await gemini_service.rebalance_budget(req)

    # Total allocated should remain within or equal to target_budget
    assert response.total_allocated <= target_budget
    assert abs(response.variance) < 1000.0  # slight rounding margin
    assert "Venue" in response.rebalance_rationale
