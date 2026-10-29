"""
Personalized cultural ideas data models with strict input boundaries.
"""

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class IdeaCategory(str, Enum):
    THEME_MOOD = "theme_mood"
    DECOR = "decor"
    MENU = "menu"
    RITUALS = "rituals"
    GAMES = "games"
    GIFTS = "gifts"


class IdeaItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., min_length=1, max_length=64, description="Unique idea ID")
    event_id: str | None = Field(None, max_length=64, description="Associated celebration ID")
    tab_category: str = Field(
        ..., min_length=2, max_length=64, description="One of: theme_mood, decor, menu, rituals, games, gifts"
    )
    title: str = Field(..., min_length=2, max_length=150, description="Idea concept headline")
    description: str = Field(..., min_length=2, max_length=1000, description="Detailed description and execution suggestions")
    cultural_context: str = Field(..., min_length=2, max_length=500, description="Regional or celebratory cultural significance")
    cost_bracket: str = Field("₹₹", max_length=10, description="Cost tier: ₹ (Low), ₹₹ (Moderate), ₹₹₹ (Luxury)")
