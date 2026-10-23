"""
Personalized cultural ideas data models.
"""

from enum import Enum

from pydantic import BaseModel, Field


class IdeaCategory(str, Enum):
    THEME_MOOD = "theme_mood"
    DECOR = "decor"
    MENU = "menu"
    RITUALS = "rituals"
    GAMES = "games"
    GIFTS = "gifts"


class IdeaItem(BaseModel):
    id: str = Field(..., description="Unique idea ID")
    event_id: str | None = Field(None, description="Associated celebration ID")
    tab_category: str = Field(
        ..., description="One of: theme_mood, decor, menu, rituals, games, gifts"
    )
    title: str = Field(..., description="Idea concept headline")
    description: str = Field(..., description="Detailed description and execution suggestions")
    cultural_context: str = Field(..., description="Regional or celebratory cultural significance")
    cost_bracket: str = Field("₹₹", description="Cost tier: ₹ (Low), ₹₹ (Moderate), ₹₹₹ (Luxury)")
