"""
AI Route Handlers for Samaroh (समारोह).
Exposes endpoints for master plan generation, streaming chat,
budget re-balancing, and auspicious muhurat windows.
"""

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, Response, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, ConfigDict, Field

from src.models.budget import BudgetRebalanceRequest, BudgetRebalanceResponse
from src.models.event import CelebrationBrief
from src.services.gemini_service import gemini_service
from src.services.storage_service import storage_service
from src.utils.app_check import verify_app_check_token
from src.utils.auth import AuthenticatedUser, get_current_user_or_demo, require_authenticated_user
from src.utils.rate_limiter import enforce_rate_limit, global_rate_limiter

router = APIRouter(prefix="/api/ai", tags=["AI Orchestration"])
rate_limiter = global_rate_limiter


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    message: str = Field(..., min_length=1, max_length=1000)
    event_id: str = Field("demo-wedding-jaipur", min_length=2, max_length=64)


@router.post("/plan")
async def create_event_plan(
    brief: CelebrationBrief,
    request: Request,
    response: Response,
    user: AuthenticatedUser = Depends(require_authenticated_user),
    _app_check: bool = Depends(verify_app_check_token),
) -> dict[str, Any]:
    """
    Synthesizes a complete celebration master plan from a user's brief.
    Enforces shared-store rate limits with X-RateLimit-* and Retry-After headers,
    validates Firebase authentication and App Check, and persists under user scope.
    """
    # Enforce dual-key (IP + User) rate limiting with standardized headers
    enforce_rate_limit(request=request, response=response, user=user)

    # Per-user quota check (prevents unbounded persistence abuse)
    existing_events = [
        e for e in storage_service.list_events(user.uid) if not e.get("id", "").startswith("demo-")
    ]
    if len(existing_events) >= 20:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Celebration quota reached: maximum 20 celebrations per user account.",
        )

    plan, is_fallback = await gemini_service.generate_master_plan(brief)

    # Persist the generated plan under authenticated user's scope
    event_id = storage_service.create_event_from_plan(brief, plan, user_id=user.uid)

    return {"success": True, "event_id": event_id, "is_fallback": is_fallback, "plan": plan}


@router.post("/rebalance-budget", response_model=BudgetRebalanceResponse)
async def rebalance_budget(
    req: BudgetRebalanceRequest,
    user: AuthenticatedUser = Depends(require_authenticated_user),
    _app_check: bool = Depends(verify_app_check_token),
) -> BudgetRebalanceResponse:
    """
    AI financial re-balancing agent. Recalculates category allocations
    when a line item cost changes to protect the master budget.
    """
    return await gemini_service.rebalance_budget(req)


@router.post("/chat")
async def chat_streaming(
    req: ChatRequest,
    user: AuthenticatedUser = Depends(get_current_user_or_demo),
) -> StreamingResponse:
    """
    Streaming conversational event planner via Server-Sent Events (SSE).
    """
    return StreamingResponse(
        gemini_service.stream_chat(req.message), media_type="text/event-stream"
    )


@router.get("/muhurat")
async def get_muhurat_guidance(
    culture: str = "Marwari",
    event_type: str = "wedding",
    user: AuthenticatedUser = Depends(get_current_user_or_demo),
) -> dict[str, Any]:
    """
    Auspicious seasonal windows and nakshatra guidance with mandatory Vedic disclaimer.
    """
    return {
        "culture": culture,
        "event_type": event_type,
        "windows": [
            {
                "season": "Winter Wedding Windows (Margashirsha & Pausha)",
                "auspicious_dates": [
                    "2026-11-24",
                    "2026-11-29",
                    "2026-12-04",
                    "2026-12-11",
                    "2026-12-15",
                ],
                "lagnas": "Godhuli Vela, Vrishabha, Mithuna",
                "nakshatras": "Rohini, Mrigashira, Uttara Phalguni",
            },
            {
                "season": "Spring Auspicious Windows (Magha & Phalguna)",
                "auspicious_dates": ["2027-01-28", "2027-02-06", "2027-02-14", "2027-02-22"],
                "lagnas": "Kanya, Tula",
                "nakshatras": "Hasta, Swati, Anuradha",
            },
        ],
        "cultural_tips": [
            "Avoid planning sacramental rituals during Rahu Kaal (approx 90 min daily based on local sunrise).",
            "Perform Ganapati Sthapana and Mandap Muhurat 3 to 5 days prior to wedding day.",
            "Godhuli Lagna (time of sunset when cows return home) is considered exceptionally auspicious.",
        ],
        "disclaimer": "Notice: Muhurat windows are AI-assisted cultural estimates intended for initial planning purposes only. Please consult your family priest, astrologer, or authoritative regional Panchang (Drik/Thirukanitha) for sacramental ceremony confirmation.",
    }
