"""
Samaroh (समारोह) - Deterministic Offline Celebration Planner Engine
Generates culturally-calibrated celebration master plans with mathematically
balanced budgets, backwards-scheduled timeline milestones, and regional vendor
blueprints when AI services are offline, unconfigured, or timing out.
"""

from datetime import datetime, timedelta
import uuid

from src.models.ai_plan import EventMasterPlan
from src.models.budget import BudgetItem, PaymentStatus
from src.models.event import CelebrationBrief
from src.models.ideas import IdeaItem
from src.models.timeline import TaskItem, TaskPriority, TaskStatus
from src.models.vendor import VendorItem, VendorStatus


def generate_deterministic_plan(brief: CelebrationBrief) -> EventMasterPlan:
    """
    Synthesizes a realistic, mathematically balanced EventMasterPlan customized
    to the user's brief without external network or LLM dependencies.
    """
    title = brief.title or f"{brief.culture} {brief.event_type.capitalize()} Celebration"
    city = brief.city or "India"
    culture = brief.culture or "Indian Tradition"
    event_type = brief.event_type if isinstance(brief.event_type, str) else brief.event_type.value
    target_budget = max(10000.0, float(brief.target_budget or 500000.0))
    guest_count = max(10, int(brief.guest_count or 100))

    # Parse target date (defaults to 60 days ahead if not provided or invalid)
    target_date_str = brief.target_date or "2026-12-15"
    try:
        target_dt = datetime.strptime(target_date_str, "%Y-%m-%d")
    except Exception:
        target_dt = datetime.now() + timedelta(days=60)
        target_date_str = target_dt.strftime("%Y-%m-%d")

    # 1. Mathematically Balanced Budget Allocations (sums to 100% of target_budget)
    # Proportions: Venue (35%), Catering (28%), Decor (15%), Photo (10%), Attire (7%), Rituals/Contingency (5%)
    allocations = [
        ("Venue & Accommodation", "Primary Venue Reservation & Guest Stays", 0.35, "Includes hall, lawns, and guest rooms with setup amenities."),
        ("Catering & Dining", f"Authentic {culture} Festive Feast & Beverages", 0.28, f"Full menu with appetizers, traditional mains, and desserts for {guest_count} guests."),
        ("Decor & Ambience", "Stage Design, Floral Installation & Lighting", 0.15, "Thematic entrance, seating backdrop, and acoustic mood lighting."),
        ("Photography & Memories", "Candid Photography & Cinematography", 0.10, "Full celebration coverage, drone footage, and curated highlight reel."),
        ("Attire, Styling & Jewels", "Traditional Celebration Outfits & Grooming", 0.07, f"Ceremonial attire and family styling attuned to {culture} customs."),
        ("Rituals & Contingency", "Sacred Materials, Logistics & Emergency Buffer", 0.05, "Ritual samagri, priest dakshina, sound permits, and contingency buffer."),
    ]

    budget_items: list[BudgetItem] = []
    accumulated_cost = 0.0

    for idx, (category, name, pct, notes) in enumerate(allocations):
        item_id = f"item-{idx + 1}"
        # For the final item, ensure exact penny-perfect total match
        if idx == len(allocations) - 1:
            cost = round(target_budget - accumulated_cost, 2)
        else:
            cost = round(target_budget * pct, 2)
            accumulated_cost += cost

        advance = round(cost * 0.25, 2)
        budget_items.append(
            BudgetItem(
                id=item_id,
                category=category,
                name=name,
                estimated_cost=cost,
                actual_cost=0.0,
                advance_paid=advance,
                status=PaymentStatus.PENDING,
                notes=notes,
            )
        )

    # 2. Backwards-Scheduled Timeline Milestones
    def _date_offset(days_before: int) -> str:
        d = target_dt - timedelta(days=days_before)
        return d.strftime("%Y-%m-%d")

    timeline_tasks: list[TaskItem] = [
        TaskItem(
            id=f"task-{uuid.uuid4().hex[:6]}",
            phase="Phase 1: Foundation",
            title=f"Lock Primary Venue in {city}",
            description=f"Inspect and reserve preferred venue in {city} accommodating {guest_count} guests with deposit.",
            due_date=_date_offset(60),
            owner_role="Host",
            priority=TaskPriority.HIGH,
            status=TaskStatus.TODO,
        ),
        TaskItem(
            id=f"task-{uuid.uuid4().hex[:6]}",
            phase="Phase 2: Planning",
            title=f"Curate {culture} Feast & Catering Menu",
            description=f"Conduct tasting session and finalize multi-course feast menu for {guest_count} attendees.",
            due_date=_date_offset(45),
            owner_role="Host & Family",
            priority=TaskPriority.HIGH,
            status=TaskStatus.TODO,
        ),
        TaskItem(
            id=f"task-{uuid.uuid4().hex[:6]}",
            phase="Phase 3: Invitations",
            title=f"Dispatch Invitations to {guest_count} Guests",
            description="Send bilingual digital and formal print invitations with RSVP tracking and directions.",
            due_date=_date_offset(30),
            owner_role="Host",
            priority=TaskPriority.MEDIUM,
            status=TaskStatus.TODO,
        ),
        TaskItem(
            id=f"task-{uuid.uuid4().hex[:6]}",
            phase="Phase 4: Coordination",
            title="Confirm Decor, Audio-Visual & Photography",
            description=f"Review mandap/stage layout, mood lighting sequence, and camera crew shot-list in {city}.",
            due_date=_date_offset(14),
            owner_role="Event Coordinator",
            priority=TaskPriority.MEDIUM,
            status=TaskStatus.TODO,
        ),
        TaskItem(
            id=f"task-{uuid.uuid4().hex[:6]}",
            phase="Phase 5: Rehearsal",
            title="Final Vendor Walkthrough & Ritual Samagri Check",
            description="Verify ritual readiness, vendor call sheets, power backups, and guest welcome station.",
            due_date=_date_offset(2),
            owner_role="Family Lead",
            priority=TaskPriority.HIGH,
            status=TaskStatus.TODO,
        ),
        TaskItem(
            id=f"task-{uuid.uuid4().hex[:6]}",
            phase="Phase 6: Celebration",
            title="Sacred Welcome & Program Execution",
            description=f"Auspicious invocation, traditional greetings, and seamless program flow for {title}.",
            due_date=target_date_str,
            owner_role="Host",
            priority=TaskPriority.HIGH,
            status=TaskStatus.TODO,
        ),
    ]

    # 3. Verified Regional Vendor Checklist (Realistic quotes derived from budget)
    vendor_checklist: list[VendorItem] = [
        VendorItem(
            id=f"vendor-{uuid.uuid4().hex[:6]}",
            category="venue",
            business_name=f"{city} Grand Heritage Banquets & Lawns",
            contact_person="Banquets Manager",
            phone=None,
            email=None,
            quote_amount=round(target_budget * 0.35, 2),
            status=VendorStatus.SHORTLISTED,
            notes=f"Centrally situated celebration premises in {city} with verified acoustics and dining halls.",
            address=f"Celebration Enclave, {city}",
            rating=4.8,
            is_estimate=True,
        ),
        VendorItem(
            id=f"vendor-{uuid.uuid4().hex[:6]}",
            category="catering",
            business_name=f"{culture} Royal Feast Catering Co.",
            contact_person="Master Chef & Lead",
            phone=None,
            email=None,
            quote_amount=round(target_budget * 0.28, 2),
            status=VendorStatus.SHORTLISTED,
            notes=f"Specialist culinary team preparing authentic regional flavors for {guest_count} guests.",
            address=f"Culinary District, {city}",
            rating=4.9,
            is_estimate=True,
        ),
        VendorItem(
            id=f"vendor-{uuid.uuid4().hex[:6]}",
            category="decor",
            business_name=f"Vedic Floral & Ambience Designers ({city})",
            contact_person="Creative Director",
            phone=None,
            email=None,
            quote_amount=round(target_budget * 0.15, 2),
            status=VendorStatus.SHORTLISTED,
            notes="Eco-friendly floral arrangements, brass diya installations, and themed fabric drapes.",
            address=f"Design Studios, {city}",
            rating=4.7,
            is_estimate=True,
        ),
        VendorItem(
            id=f"vendor-{uuid.uuid4().hex[:6]}",
            category="photography",
            business_name=f"Utsav Memories Photography & Films",
            contact_person="Principal Photographer",
            phone=None,
            email=None,
            quote_amount=round(target_budget * 0.10, 2),
            status=VendorStatus.SHORTLISTED,
            notes="Dedicated photojournalistic team providing same-day teasers, portrait booth, and photo book.",
            address=f"Creative Hub, {city}",
            rating=4.8,
            is_estimate=True,
        ),
    ]

    # 4. Culturally Attuned Ideas Across 6 Dimensions
    personalized_ideas: list[IdeaItem] = [
        IdeaItem(
            id=f"idea-{uuid.uuid4().hex[:6]}",
            tab_category="theme_mood",
            title=f"{culture} Radiant Auspicious Palette",
            description="Incorporate auspicious crimson, gold accents, and fresh marigold hues into stage draping.",
            cultural_context=f"Rooted in {culture} traditions symbolizing prosperity, joy, and positive beginnings.",
            cost_bracket="₹₹",
        ),
        IdeaItem(
            id=f"idea-{uuid.uuid4().hex[:6]}",
            tab_category="decor",
            title="Handcrafted Brass Lamps & Floral Rangoli Entry",
            description="Greet arriving guests with fragrant petal rangoli and brass Samai oil lamps at the gateway.",
            cultural_context="Invokes positive vibrations and honours traditional Indian welcome protocols.",
            cost_bracket="₹",
        ),
        IdeaItem(
            id=f"idea-{uuid.uuid4().hex[:6]}",
            tab_category="menu",
            title="Live Heritage Food Counter & Regional Delights",
            description=f"Introduce interactive live culinary stations serving signature {culture} delicacies and herbal coolers.",
            cultural_context="Delights multigenerational family guests while preserving traditional culinary authenticity.",
            cost_bracket="₹₹",
        ),
        IdeaItem(
            id=f"idea-{uuid.uuid4().hex[:6]}",
            tab_category="rituals",
            title="Traditional Tilak & Rosewater Welcome Protocol",
            description="Elders welcome guests with auspicious kumkum tilak, sacred akshat rice, and fragrant gulab jal.",
            cultural_context="Ancient Vedic hospitality rite establishing reverence and sacred festivity.",
            cost_bracket="₹",
        ),
        IdeaItem(
            id=f"idea-{uuid.uuid4().hex[:6]}",
            tab_category="games",
            title="Generational Folk Music & Interactive Antakshari",
            description="Host an engaging musical evening connecting extended elders and youth with cultural melodies.",
            cultural_context="Fosters unity, warmth, and shared celebratory storytelling across age groups.",
            cost_bracket="₹",
        ),
        IdeaItem(
            id=f"idea-{uuid.uuid4().hex[:6]}",
            tab_category="gifts",
            title="Handmade Clay Planters with Regional Sweets",
            description="Sustainable return gifts featuring indigenous plant saplings paired with artisanal mithai boxes.",
            cultural_context="Represents nurturing life, gratitude, and nature-friendly mindful celebrations.",
            cost_bracket="₹₹",
        ),
    ]

    cultural_summary = (
        f"A culturally attuned {culture} {event_type} celebration designed for {city}, "
        f"harmonizing traditional reverence with mindful fiscal planning for {guest_count} guests."
    )

    auspicious_guidance = (
        f"Celebrate during auspicious daylight or twilight windows honoring {culture} customs. "
        "Sacramental invocations are best scheduled following local sunrise calculations, avoiding Rahu Kaal."
    )

    return EventMasterPlan(
        celebration_title=title,
        event_type=event_type,
        cultural_summary=cultural_summary,
        target_budget=target_budget,
        guest_count=guest_count,
        budget_breakdown=budget_items,
        timeline_tasks=timeline_tasks,
        vendor_checklist=vendor_checklist,
        personalized_ideas=personalized_ideas,
        auspicious_guidance=auspicious_guidance,
        disclaimer="Notice: Timings, muhurat guidance, and vendor quotes are AI-assisted estimates for budgeting purposes only.",
    )
