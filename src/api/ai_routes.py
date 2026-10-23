"""
AI Route Handlers for Utsav (उत्सव).
Exposes endpoints for master plan generation, streaming chat,
budget re-balancing, and auspicious muhurat windows.
"""
from fastapi import APIRouter, HTTPException, Request, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from src.models.event import CelebrationBrief
from src.models.budget import BudgetRebalanceRequest, BudgetRebalanceResponse
from src.services.gemini_service import gemini_service
from src.services.storage_service import storage_service
from src.utils.rate_limiter import SlidingWindowRateLimiter

router = APIRouter(prefix="/api/ai", tags=["AI Orchestration"])
rate_limiter = SlidingWindowRateLimiter(max_requests=25, window_seconds=600)

class ChatRequest(BaseModel):
    message: str
    event_id: str = "demo-wedding-jaipur"

@router.post("/plan")
async def create_event_plan(brief: CelebrationBrief, request: Request):
    """
    Synthesizes a complete celebration master plan from a user's brief.
    Enforces rate limits and returns both the plan and the saved event ID.
    """
    client_ip = request.client.host if request.client else "127.0.0.1"
    allowed, remaining = rate_limiter.is_allowed(client_ip)
    if not allowed:
        raise HTTPException(
            status_code=429,
            detail="Rate limit reached for AI plan generation. Please explore our instant demo celebrations."
        )

    plan, is_fallback = await gemini_service.generate_master_plan(brief)
    
    # Persist the generated plan
    event_id = storage_service.create_event_from_plan(brief, plan)
    
    return {
        "success": True,
        "event_id": event_id,
        "is_fallback": is_fallback,
        "plan": plan
    }

@router.post("/rebalance-budget", response_model=BudgetRebalanceResponse)
async def rebalance_budget(req: BudgetRebalanceRequest):
    """
    AI financial re-balancing agent. Recalculates category allocations
    when a line item cost changes to protect the master budget.
    """
    return await gemini_service.rebalance_budget(req)

@router.post("/chat")
async def chat_streaming(req: ChatRequest):
    """
    Streaming conversational event planner via Server-Sent Events (SSE).
    """
    return StreamingResponse(
        gemini_service.stream_chat(req.message),
        media_type="text/event-stream"
    )

@router.get("/muhurat")
async def get_muhurat_guidance(culture: str = "Marwari", event_type: str = "wedding"):
    """
    Auspicious seasonal windows and nakshatra guidance with mandatory Vedic disclaimer.
    """
    return {
        "culture": culture,
        "event_type": event_type,
        "windows": [
            {
                "season": "Winter Wedding Windows (Margashirsha & Pausha)",
                "auspicious_dates": ["2026-11-24", "2026-11-29", "2026-12-04", "2026-12-11", "2026-12-15"],
                "lagnas": "Godhuli Vela, Vrishabha, Mithuna",
                "nakshatras": "Rohini, Mrigashira, Uttara Phalguni"
            },
            {
                "season": "Spring Auspicious Windows (Magha & Phalguna)",
                "auspicious_dates": ["2027-01-28", "2027-02-06", "2027-02-14", "2027-02-22"],
                "lagnas": "Kanya, Tula",
                "nakshatras": "Hasta, Swati, Anuradha"
            }
        ],
        "cultural_tips": [
            "Avoid planning sacramental rituals during Rahu Kaal (approx 90 min daily based on local sunrise).",
            "Perform Ganapati Sthapana and Mandap Muhurat 3 to 5 days prior to wedding day.",
            "Godhuli Lagna (time of sunset when cows return home) is considered exceptionally auspicious."
        ],
        "disclaimer": "Notice: Muhurat windows are AI-assisted cultural estimates intended for initial planning purposes only. Please consult your family priest, astrologer, or authoritative regional Panchang (Drik/Thirukanitha) for sacramental ceremony confirmation."
    }
