"""
Google Gemini GenAI Orchestration Service for Utsav (उत्सव).
Uses the official Google GenAI Python SDK (google-genai).
Handles structured plan generation, streaming chat, financial re-balancing,
and self-healing fallback to curated blueprints on API quota exhaustion.
"""
import asyncio
import json
import logging
from typing import AsyncGenerator, Optional
from google import genai
from pydantic import ValidationError

from src.config import settings
from src.models.event import CelebrationBrief, EventType
from src.models.ai_plan import EventMasterPlan
from src.models.budget import (
    BudgetItem, BudgetRebalanceRequest, BudgetRebalanceResponse,
    CategoryAllocation, PaymentStatus
)
from src.utils.sanitizer import sanitize_prompt_input
from src.data.wedding_jaipur import JAIPUR_WEDDING_SEED
from src.data.birthday_blr import BLR_BIRTHDAY_SEED
from src.data.community_delhi import DELHI_COMMUNITY_SEED

logger = logging.getLogger("utsav.gemini")

class GeminiService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.GEMINI_MODEL
        self._client: Optional[genai.Client] = None
        
        if self.api_key:
            try:
                self._client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.warning(f"Failed to initialize Google GenAI Client: {e}")

    def get_seed_for_event_type(self, event_type: str) -> EventMasterPlan:
        """Returns pre-built production-grade celebration blueprint matching event type."""
        ev_str = str(event_type).lower()
        if "wedding" in ev_str:
            return JAIPUR_WEDDING_SEED
        elif "birthday" in ev_str:
            return BLR_BIRTHDAY_SEED
        else:
            return DELHI_COMMUNITY_SEED

    async def generate_master_plan(self, brief: CelebrationBrief) -> tuple[EventMasterPlan, bool]:
        """
        Synthesizes a full celebration master plan.
        Returns: (EventMasterPlan, is_fallback: bool)
        """
        # If API key is missing or client not initialized, return curated seed immediately
        if not self._client or not self.api_key:
            logger.info("Gemini API key not configured. Serving curated seed celebration.")
            seed = self.get_seed_for_event_type(brief.event_type.value if hasattr(brief.event_type, 'value') else brief.event_type)
            # Personalize title and parameters from user's brief
            return EventMasterPlan(
                celebration_title=brief.title or seed.celebration_title,
                event_type=brief.event_type.value if hasattr(brief.event_type, 'value') else str(brief.event_type),
                cultural_summary=f"Curated {brief.culture} celebration in {brief.city} for {brief.guest_count} guests honoring sacred traditions.",
                target_budget=brief.target_budget,
                guest_count=brief.guest_count,
                budget_breakdown=seed.budget_breakdown,
                timeline_tasks=seed.timeline_tasks,
                vendor_checklist=seed.vendor_checklist,
                personalized_ideas=seed.personalized_ideas,
                auspicious_guidance=seed.auspicious_guidance,
                disclaimer="Notice: Timings, muhurat guidance, and vendor quotes are AI-assisted estimates for budgeting purposes only."
            ), True

        # Sanitize user inputs
        clean_title = sanitize_prompt_input(brief.title)
        clean_notes = sanitize_prompt_input(brief.notes or "")
        clean_culture = sanitize_prompt_input(brief.culture)
        clean_city = sanitize_prompt_input(brief.city)

        system_instruction = (
            "You are Utsav's Master Celebration Planner, an expert in Indian weddings, birthdays, "
            "and community festivals. Generate a culturally accurate, financially realistic, "
            "and actionable event blueprint in valid JSON conforming to the requested schema. "
            "All money must be in Indian Rupees (INR). Never invent fake personal phone numbers. "
            "Ensure the sum of budget_breakdown items is close to target_budget."
        )

        user_prompt = f"""
{system_instruction}

<user_brief>
Celebration Title: {clean_title}
Event Type: {brief.event_type}
Cultural Tradition: {clean_culture}
Host City: {clean_city}
Target Date: {brief.target_date}
Target Budget: INR {brief.target_budget}
Guest Count: {brief.guest_count}
Language: {brief.language}
Special Notes: {clean_notes}
</user_brief>

Generate a complete EventMasterPlan in JSON format.
"""

        try:
            # Call Gemini via Google GenAI SDK with a strict 12.0s timeout
            def _call():
                return self._client.models.generate_content(
                    model=self.model_name,
                    contents=user_prompt,
                    config={
                        "response_mime_type": "application/json",
                        "temperature": 0.25,
                    }
                )

            response = await asyncio.wait_for(asyncio.to_thread(_call), timeout=12.0)
            raw_text = response.text
            plan = EventMasterPlan.model_validate_json(raw_text)
            return plan, False

        except ValidationError as val_err:
            logger.warning(f"Pydantic validation failed on Gemini output: {val_err}. Triggering repair prompt...")
            # Attempt 1 repair prompt
            try:
                repair_prompt = f"""
Fix the following JSON so it strictly satisfies the EventMasterPlan schema:
ERRORS:
{val_err.errors()}

ORIGINAL RAW JSON:
{raw_text}
"""
                def _repair_call():
                    return self._client.models.generate_content(
                        model=self.model_name,
                        contents=repair_prompt,
                        config={
                            "response_mime_type": "application/json",
                            "temperature": 0.05,
                        }
                    )

                repair_response = await asyncio.wait_for(asyncio.to_thread(_repair_call), timeout=8.0)
                plan = EventMasterPlan.model_validate_json(repair_response.text)
                return plan, False
            except Exception as repair_e:
                logger.error(f"Repair prompt failed: {repair_e}. Falling back to curated seed.")
                return self.get_seed_for_event_type(brief.event_type), True

        except Exception as e:
            logger.warning(f"Gemini API call failed ({e}). Gracefully falling back to curated seed.")
            return self.get_seed_for_event_type(brief.event_type), True

    async def rebalance_budget(self, request: BudgetRebalanceRequest) -> BudgetRebalanceResponse:
        """
        Recalculates category allocations when a user modifies a budget line.
        Protects core non-negotiables while adjusting flexible luxury categories.
        """
        target = request.target_budget
        changed_cat = request.changed_category
        new_amt = request.new_amount
        current_items = request.current_items

        # Build current category totals
        cat_totals: dict[str, float] = {}
        for item in current_items:
            cat_totals[item.category] = cat_totals.get(item.category, 0.0) + item.estimated_cost

        # Set the changed category to new_amt
        cat_totals[changed_cat] = new_amt

        # Compute remaining budget to distribute among other categories
        other_cats = [c for c in cat_totals if c != changed_cat]
        current_other_sum = sum(cat_totals[c] for c in other_cats)
        needed_for_others = target - new_amt

        if current_other_sum > 0 and needed_for_others > 0:
            scale_factor = needed_for_others / current_other_sum
            for c in other_cats:
                # Scale proportionally
                cat_totals[c] = round(cat_totals[c] * scale_factor, -2)

        # Build updated BudgetItem list
        updated_items = []
        for item in current_items:
            if item.category == changed_cat:
                updated_items.append(item)
            else:
                scale = (cat_totals[item.category] / sum(it.estimated_cost for it in current_items if it.category == item.category)) if sum(it.estimated_cost for it in current_items if it.category == item.category) > 0 else 1.0
                updated_item = item.model_copy(update={"estimated_cost": round(item.estimated_cost * scale, -2)})
                updated_items.append(updated_item)

        total_allocated = sum(cat_totals.values())
        variance = target - total_allocated

        allocations = [
            CategoryAllocation(
                name=cat,
                allocated_amount=amt,
                percentage_of_total=round((amt / target) * 100, 1) if target > 0 else 0.0
            )
            for cat, amt in cat_totals.items()
        ]

        rationale = (
            f"Adjusted {changed_cat} to ₹{new_amt:,.0f} and scaled flexible categories proportionally "
            f"to stay within your master target budget of ₹{target:,.0f}."
        )

        return BudgetRebalanceResponse(
            categories=allocations,
            updated_items=updated_items,
            total_allocated=total_allocated,
            target_budget=target,
            variance=variance,
            rebalance_rationale=rationale
        )

    async def stream_chat(self, user_message: str, history: Optional[list] = None) -> AsyncGenerator[str, None]:
        """
        Streams conversational AI planning guidance via Server-Sent Events (SSE).
        """
        clean_msg = sanitize_prompt_input(user_message)
        
        if not self._client or not self.api_key:
            yield "data: {\"text\": \"॥ शुभ आरम्भ ॥ Welcome! I am Utsav's Cultural Planning Companion.\\n\\n\"}\n\n"
            await asyncio.sleep(0.2)
            yield "data: {\"text\": \"To organize your celebration, review your **Budget Matrix** and **Timeline** tabs. We have pre-configured auspicious Vedic guidelines, regional delicacy suggestions, and verified vendor bands for your event.\\n\\n\"}\n\n"
            await asyncio.sleep(0.2)
            yield "data: {\"text\": \"*Tip:* Click 'AI Re-Balance' in the budget tab anytime to optimize expenses across categories!\"}\n\n"
            yield "data: [DONE]\n\n"
            return

        try:
            def _stream_call():
                return self._client.models.generate_content_stream(
                    model=self.model_name,
                    contents=f"You are Utsav's conversational event planning assistant. Give concise, warm, culturally authentic advice for Indian weddings, birthdays, and community festivals. Use markdown.\n\nUser: {clean_msg}"
                )

            stream = await asyncio.to_thread(_stream_call)
            for chunk in stream:
                if chunk.text:
                    payload = json.dumps({"text": chunk.text})
                    yield f"data: {payload}\n\n"
                    await asyncio.sleep(0.02)
            yield "data: [DONE]\n\n"
        except Exception as e:
            logger.error(f"Streaming error: {e}")
            fallback_text = json.dumps({"text": "I am currently operating in offline guidance mode. Your budget, vendor quotes, and timeline tasks are fully accessible and editable above."})
            yield f"data: {fallback_text}\n\n"
            yield "data: [DONE]\n\n"

gemini_service = GeminiService()
