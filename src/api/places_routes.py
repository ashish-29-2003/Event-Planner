"""
Google Maps Platform Places Proxy Routes for Samaroh (समारोह).
Enables secure client-side discovery of celebration venues and vendors
without exposing Google Cloud API keys in frontend assets.
"""

from typing import Any

from fastapi import APIRouter, Depends, Query

from src.services.places_service import places_service
from src.utils.auth import AuthenticatedUser, get_current_user_or_demo

router = APIRouter(prefix="/api/places", tags=["Google Places Discovery"])


@router.get("/search")
async def search_places(
    query: str = Query(..., description="Celebration venue or vendor query (e.g. Palace Banquet, Marwari Halwai)"),
    city: str = Query("Jaipur", description="Target city for the celebration"),
    category: str = Query("venue", description="Category: venue, catering, decor, photography, priest"),
    user: AuthenticatedUser = Depends(get_current_user_or_demo),
) -> dict[str, Any]:
    """
    Searches for verified celebration venues and vendors.
    Proxies to Google Maps Places API when configured, degrading gracefully
    to Samaroh's curated cultural registry when API key is omitted.
    """
    candidates, source = await places_service.search_places(
        query=query,
        city=city,
        category=category,
    )

    return {
        "success": True,
        "query": query,
        "city": city,
        "category": category,
        "source": source,
        "count": len(candidates),
        "results": [c.model_dump() for c in candidates],
    }
