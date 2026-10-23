"""
Seeded Demo Blueprint: Bengaluru Urban Themed Birthday
Aarav's 5th Cosmic Space Explorer Adventure
"""
from src.models.ai_plan import EventMasterPlan
from src.models.budget import BudgetItem, PaymentStatus
from src.models.timeline import TaskItem, TaskPriority, TaskStatus
from src.models.vendor import VendorItem, VendorStatus
from src.models.ideas import IdeaItem

BLR_BIRTHDAY_SEED = EventMasterPlan(
    celebration_title="Aarav's 5th Cosmic Space Explorer Birthday",
    event_type="birthday",
    cultural_summary="An imaginative, zero-single-use-plastic, tech-meets-tradition 5th birthday celebration for 45 kids and parents at a community clubhouse in Whitefield, Bengaluru.",
    target_budget=85000.0,
    guest_count=45,
    budget_breakdown=[
        BudgetItem(
            id="b-bday-01",
            category="Venue & Hall",
            name="Community Club Party Hall & Garden Lawn",
            estimated_cost=18000.0,
            actual_cost=15000.0,
            advance_paid=5000.0,
            status=PaymentStatus.PARTIAL,
            notes="Includes air conditioning, chairs, projector screen, and sound system."
        ),
        BudgetItem(
            id="b-bday-02",
            category="Themed Cake & Bakery",
            name="3 kg Solar System Gravity-Defying Fondant & Cupcakes",
            estimated_cost=8500.0,
            actual_cost=8000.0,
            advance_paid=3000.0,
            status=PaymentStatus.PARTIAL,
            notes="Eggless Belgian dark chocolate with edible astronaut figurines."
        ),
        BudgetItem(
            id="b-bday-03",
            category="Catering & Kid Snacks",
            name="Healthy Finger Food Buffet (Mini Idlis, Sliders, Fresh Juices)",
            estimated_cost=24000.0,
            actual_cost=22000.0,
            advance_paid=8000.0,
            status=PaymentStatus.PARTIAL,
            notes="No artificial colors; Jain and gluten-free snack options included."
        ),
        BudgetItem(
            id="b-bday-04",
            category="Entertainment & Games",
            name="Science Experiment Show & Planetarium Dome Experience",
            estimated_cost=14000.0,
            actual_cost=14000.0,
            advance_paid=5000.0,
            status=PaymentStatus.PARTIAL,
            notes="45-minute interactive liquid nitrogen rocket launch & dry ice smoke show."
        ),
        BudgetItem(
            id="b-bday-05",
            category="Eco-Decor & Balloon Art",
            name="Biodegradable Paper Honeycomb Planets & Star Projectors",
            estimated_cost=10500.0,
            actual_cost=10000.0,
            advance_paid=4000.0,
            status=PaymentStatus.PARTIAL,
            notes="100% plastic-balloon-free decor; ambient cosmic blue LED uplighting."
        ),
        BudgetItem(
            id="b-bday-06",
            category="Return Gifts (Zero Plastic)",
            name="DIY Telescope Craft Kits & Seed Pencils",
            estimated_cost=10000.0,
            actual_cost=9500.0,
            advance_paid=9500.0,
            status=PaymentStatus.PAID,
            notes="Jute gift bags with personalized wooden name tags."
        ),
    ],
    timeline_tasks=[
        TaskItem(
            id="t-bday-01",
            phase="Phase 1: Foundation (3 Weeks Out)",
            title="Book Community Club Hall & Security Clearance",
            description="Reserve Whitefield clubhouse terrace and pay refundable deposit.",
            due_date="2026-11-20",
            owner_role="Host Dad",
            priority=TaskPriority.HIGH,
            status=TaskStatus.DONE
        ),
        TaskItem(
            id="t-bday-02",
            phase="Phase 2: Bookings (2 Weeks Out)",
            title="Order Custom Solar System Cake & Dessert Cups",
            description="Send flavor specs to artisan baker in Indiranagar.",
            due_date="2026-11-28",
            owner_role="Host Mom",
            priority=TaskPriority.HIGH,
            status=TaskStatus.DONE
        ),
        TaskItem(
            id="t-bday-03",
            phase="Phase 3: Invites (10 Days Out)",
            title="Send WhatsApp Animated Video Invite with RSVP Form",
            description="Track dietary preferences and child age brackets.",
            due_date="2026-12-02",
            owner_role="Host",
            priority=TaskPriority.HIGH,
            status=TaskStatus.DONE
        ),
        TaskItem(
            id="t-bday-04",
            phase="Phase 4: Day-Of Setup (2 Hours Prior)",
            title="Set Up Rocket Launch Pad & Cosmic Light Projector",
            description="Test audio mics for science show and chill juice dispensers.",
            due_date="2026-12-12",
            owner_role="Host",
            priority=TaskPriority.HIGH,
            status=TaskStatus.TODO
        ),
        TaskItem(
            id="t-bday-05",
            phase="Phase 5: Run of Show (04:30 PM - 07:30 PM)",
            title="05:30 PM - Cake Cutting & 'Happy Birthday' Astronaut Anthem",
            description="Gather kids around the solar system table for sparkler candle celebration.",
            due_date="2026-12-12",
            owner_role="Host",
            priority=TaskPriority.HIGH,
            status=TaskStatus.TODO
        ),
    ],
    vendor_checklist=[
        VendorItem(
            id="v-bday-01",
            category="venue",
            business_name="Palm Meadows Club Clubhouse",
            contact_person="Muralidhar (Estate Manager)",
            phone="+91 80 2845 0000",
            quote_amount=15000.0,
            status=VendorStatus.BOOKED,
            notes="Includes terrace party zone and projector screen.",
            address="Whitefield, Bengaluru",
            rating=4.7,
            is_estimate=False
        ),
        VendorItem(
            id="v-bday-02",
            category="catering",
            business_name="Green Kitchen Gourmet Bites",
            contact_person="Smita Rao",
            phone="+91 98450 77889",
            quote_amount=22000.0,
            status=VendorStatus.BOOKED,
            notes="Fresh fruit mocktails, baked nachos, cheese poppers, and mini dosa counter.",
            address="Koramangala, Bengaluru",
            rating=4.9,
            is_estimate=False
        ),
        VendorItem(
            id="v-bday-03",
            category="entertainment",
            business_name="Curious Sparks Science Theater",
            contact_person="Rohan Deshmukh",
            phone="+91 99001 23456",
            quote_amount=14000.0,
            status=VendorStatus.BOOKED,
            notes="Liquid nitrogen show, foam eruptions, and take-home slime experiment.",
            address="HSR Layout, Bengaluru",
            rating=4.8,
            is_estimate=False
        ),
    ],
    personalized_ideas=[
        IdeaItem(
            id="i-bday-01",
            tab_category="theme_mood",
            title="Mission to Mars: Junior Cosmonaut Academy",
            description="Kids receive customized astronaut badges and mission logbooks at the check-in gate.",
            cultural_context="Celebrates India's proud space exploration heritage (ISRO Chandrayaan & Gaganyaan).",
            cost_bracket="₹"
        ),
        IdeaItem(
            id="i-bday-02",
            tab_category="decor",
            title="Honeycomb Planet Orbs & Cosmic Constellation Wall",
            description="Eco-friendly paper honeycomb lanterns illuminated from within, forming an interactive solar system.",
            cultural_context="100% plastic-free, recyclable festive decor.",
            cost_bracket="₹₹"
        ),
        IdeaItem(
            id="i-bday-03",
            tab_category="menu",
            title="Galaxy Smoothies & Rocket Skewers",
            description="Blueberry-banana layered smoothies served in glass bottles with bamboo straws, alongside colorful fruit rocket skewers.",
            cultural_context="Nutritious, delicious, and themed to delight kids and health-conscious parents.",
            cost_bracket="₹"
        ),
        IdeaItem(
            id="i-bday-04",
            tab_category="games",
            title="Meteorite Hunt & Moon Landing Obstacle Course",
            description="Soft foam asteroid challenges and crater balance beams designed to keep toddlers active and engaged.",
            cultural_context="High-energy group teamwork promoting cooperative play.",
            cost_bracket="₹"
        ),
        IdeaItem(
            id="i-bday-05",
            tab_category="rituals",
            title="Aayushya Homam Blessings & Milestone Photo Tree",
            description="Brief family blessing prayer followed by a memory string showing Aarav's growth across his first 5 years.",
            cultural_context="Traditional Indian prayer for longevity, vigor, and good health (*Aayushya*).",
            cost_bracket="₹"
        ),
        IdeaItem(
            id="i-bday-06",
            tab_category="gifts",
            title="Cardboard Planetarium Kits & Plantable Seed Pencils",
            description="Kids take home an assemble-it-yourself DIY night sky projector and basil seed pencils.",
            cultural_context="Educational, zero-waste, and memorable sustainable favor.",
            cost_bracket="₹₹"
        ),
    ],
    auspicious_guidance="Celebration begins auspiciously on Shukla Paksha Panchami, ideally timed during daytime hours (04:30 PM - 07:30 PM) for toddler energy and parental convenience.",
    disclaimer="Notice: All game supplies and vendor rates are illustrative estimates for planning."
)
