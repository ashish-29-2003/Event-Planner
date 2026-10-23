"""
Seeded Demo Blueprint: Jaipur Royal Destination Wedding (Marwari Vivaha)
"""
from src.models.ai_plan import EventMasterPlan
from src.models.budget import BudgetItem, PaymentStatus
from src.models.timeline import TaskItem, TaskPriority, TaskStatus
from src.models.vendor import VendorItem, VendorStatus
from src.models.ideas import IdeaItem

JAIPUR_WEDDING_SEED = EventMasterPlan(
    celebration_title="Riya & Kabir's Royal Vivaha & Sangeet",
    event_type="wedding",
    cultural_summary="A majestic 3-day Marwari royal heritage celebration in Jaipur, honoring traditional ceremonies (Mehendi, Sangeet, Mayra/Bhaat, Pheras, and Reception) with Rajasthani hospitality.",
    target_budget=4500000.0,
    guest_count=350,
    budget_breakdown=[
        BudgetItem(
            id="b-wed-01",
            category="Venue & Accommodation",
            name="Heritage Palace Courtyard & 40 Guest Suites (2 Nights)",
            estimated_cost=1800000.0,
            actual_cost=1800000.0,
            advance_paid=600000.0,
            status=PaymentStatus.PARTIAL,
            notes="Includes Royal Lawns, Sangeet Amphitheatre, and poolside Mehendi cabanas."
        ),
        BudgetItem(
            id="b-wed-02",
            category="Catering & Royal Feasts",
            name="Royal Rajasthani & Continental Gourmet (6 Feasts for 350 Guests)",
            estimated_cost=1200000.0,
            actual_cost=1150000.0,
            advance_paid=400000.0,
            status=PaymentStatus.PARTIAL,
            notes="Pure vegetarian royal thali, Dal Baati Churma live counter, Ker Sangri, Jalebi live tawa."
        ),
        BudgetItem(
            id="b-wed-03",
            category="Decor & Floral Architecture",
            name="Genda Phool, Rajnigandha, Velvet Drapes & Mandap Setup",
            estimated_cost=550000.0,
            actual_cost=520000.0,
            advance_paid=200000.0,
            status=PaymentStatus.PARTIAL,
            notes="Eco-friendly temple flowers, brass diyas, and mirrored toranas."
        ),
        BudgetItem(
            id="b-wed-04",
            category="Photography & Cinematography",
            name="Candid Wedding Cinema, Drone Coverage & Traditional Album",
            estimated_cost=320000.0,
            actual_cost=300000.0,
            advance_paid=100000.0,
            status=PaymentStatus.PARTIAL,
            notes="3-day coverage, teaser film in 48 hours, full 4K documentary."
        ),
        BudgetItem(
            id="b-wed-05",
            category="Music & Entertainment",
            name="Rajasthani Manganiyar Troupe, DJ & Sangeet Choreographer",
            estimated_cost=250000.0,
            actual_cost=240000.0,
            advance_paid=100000.0,
            status=PaymentStatus.PARTIAL,
            notes="Live Shenai for morning rituals, Bollywood DJ for Sangeet night."
        ),
        BudgetItem(
            id="b-wed-06",
            category="Mehendi & Bridal Styling",
            name="Bridal Mehendi Artist, Guest Mehendi Team & Salon Services",
            estimated_cost=120000.0,
            actual_cost=110000.0,
            advance_paid=50000.0,
            status=PaymentStatus.PARTIAL,
            notes="Organic Marwari henna cones, floral jewelry for Haldi."
        ),
        BudgetItem(
            id="b-wed-07",
            category="Puja & Officiant",
            name="Vedic Pandit Team & Sacred Hawan Samagri",
            estimated_cost=60000.0,
            actual_cost=50000.0,
            advance_paid=20000.0,
            status=PaymentStatus.PARTIAL,
            notes="Sanskrit Vedic recitations with English explanations for younger guests."
        ),
        BudgetItem(
            id="b-wed-08",
            category="Favors & Mithai Hampers",
            name="Silver Coin Keepsakes & Handcrafted Ghevar Boxes",
            estimated_cost=200000.0,
            actual_cost=180000.0,
            advance_paid=90000.0,
            status=PaymentStatus.PARTIAL,
            notes="Custom laser-etched royal boxes for all 350 attending families."
        ),
    ],
    timeline_tasks=[
        TaskItem(
            id="t-wed-01",
            phase="Phase 1: Foundation (6 Months Out)",
            title="Confirm Heritage Palace Booking & Deposit in Jaipur",
            description="Sign legal contract for banquet laws, 40 rooms, and sound permissions.",
            due_date="2026-06-15",
            owner_role="Host",
            priority=TaskPriority.HIGH,
            status=TaskStatus.DONE
        ),
        TaskItem(
            id="t-wed-02",
            phase="Phase 1: Foundation (6 Months Out)",
            title="Consult Family Pandit for Sacred Muhurat Windows",
            description="Finalize exact Lagna and Phera muhurat timings (Godhuli Vela).",
            due_date="2026-06-25",
            owner_role="Parents",
            priority=TaskPriority.HIGH,
            status=TaskStatus.DONE
        ),
        TaskItem(
            id="t-wed-03",
            phase="Phase 2: Core Bookings (3 Months Out)",
            title="Book Halwai Catering Team & Tasting Session",
            description="Finalize menu selections: Dal Baati, Gatte ki Sabzi, Malpua, and dry fruit counters.",
            due_date="2026-09-10",
            owner_role="Host",
            priority=TaskPriority.HIGH,
            status=TaskStatus.DONE
        ),
        TaskItem(
            id="t-wed-04",
            phase="Phase 2: Core Bookings (3 Months Out)",
            title="Engage Wedding Cinematography & Photography Team",
            description="Sign contract with drone permissions and shot list for Mehendi & Pheras.",
            due_date="2026-09-20",
            owner_role="Couple",
            priority=TaskPriority.MEDIUM,
            status=TaskStatus.DONE
        ),
        TaskItem(
            id="t-wed-05",
            phase="Phase 3: Details & Invites (1 Month Out)",
            title="Dispatch Digital Invites & Track Outstation RSVPs",
            description="Share flight recommendations to Jaipur (JAI) and airport shuttle details.",
            due_date="2026-11-15",
            owner_role="Host",
            priority=TaskPriority.HIGH,
            status=TaskStatus.IN_PROGRESS
        ),
        TaskItem(
            id="t-wed-06",
            phase="Phase 4: Final Week (7 Days Out)",
            title="Assemble Puja Samagri & Organic Haldi Cones",
            description="Procure gangajal, dry fruits, supari, and ceremonial shawls.",
            due_date="2026-12-08",
            owner_role="Maternal Uncle",
            priority=TaskPriority.HIGH,
            status=TaskStatus.TODO
        ),
        TaskItem(
            id="t-wed-07",
            phase="Phase 5: Day-Of Schedule (Hour-by-Hour)",
            title="09:00 AM - Shubh Ganesh Puja & Mehendi Dawn",
            description="Blessings invocation, acoustic Shehnai, floral seating for bride.",
            due_date="2026-12-15",
            owner_role="Pandit / Host",
            priority=TaskPriority.HIGH,
            status=TaskStatus.TODO
        ),
        TaskItem(
            id="t-wed-08",
            phase="Phase 5: Day-Of Schedule (Hour-by-Hour)",
            title="05:30 PM - Royal Baraat Procession & Milni",
            description="Dhol ensemble, vintage car escort, rose-petal shower at palace gates.",
            due_date="2026-12-15",
            owner_role="Groom's Side",
            priority=TaskPriority.HIGH,
            status=TaskStatus.TODO
        ),
        TaskItem(
            id="t-wed-09",
            phase="Phase 5: Day-Of Schedule (Hour-by-Hour)",
            title="07:15 PM - Godhuli Lagna Pheras & Saptapadi",
            description="Sacred 7 vows around the holy agni under floral mandap.",
            due_date="2026-12-15",
            owner_role="Officiant",
            priority=TaskPriority.HIGH,
            status=TaskStatus.TODO
        ),
    ],
    vendor_checklist=[
        VendorItem(
            id="v-wed-01",
            category="venue",
            business_name="Rajvilas Palace Heritage Courtyards",
            contact_person="Digvijay Singh (Banquets)",
            phone="+91 141 268 0000",
            email="events@rajvilasjaipur.com",
            quote_amount=1800000.0,
            status=VendorStatus.BOOKED,
            notes="Includes lawns, 40 suites, generator backup, and lighting permits.",
            address="Goner Road, Jaipur, Rajasthan",
            rating=4.9,
            is_estimate=False
        ),
        VendorItem(
            id="v-wed-02",
            category="catering",
            business_name="Mewar Royal Halwai & Gourmet Banquets",
            contact_person="Rameshwar Sharma",
            phone="+91 98290 12345",
            email="rameshwar@mewarcaterers.in",
            quote_amount=1150000.0,
            status=VendorStatus.BOOKED,
            notes="350 Pax, 6 feasts, copper chafing dishes, kulhad chai counters.",
            address="MI Road, Jaipur",
            rating=4.9,
            is_estimate=False
        ),
        VendorItem(
            id="v-wed-03",
            category="decor",
            business_name="Virasat Floral & Mandap Designers",
            contact_person="Ananya Shekhawat",
            phone="+91 98281 67890",
            email="ananya@virasatdecor.com",
            quote_amount=520000.0,
            status=VendorStatus.SHORTLISTED,
            notes="Marigold chandeliers, brass diya pathways, temple lotus mandap.",
            address="C-Scheme, Jaipur",
            rating=4.8,
            is_estimate=True
        ),
        VendorItem(
            id="v-wed-04",
            category="photography",
            business_name="Dharohar Wedding Cinematography",
            contact_person="Kunal Mathur",
            phone="+91 99280 44556",
            email="kunal@dharoharfilms.com",
            quote_amount=300000.0,
            status=VendorStatus.BOOKED,
            notes="3 candid photographers, 2 cinematographers, drone operator.",
            address="Vaishali Nagar, Jaipur",
            rating=4.9,
            is_estimate=False
        ),
    ],
    personalized_ideas=[
        IdeaItem(
            id="i-wed-01",
            tab_category="theme_mood",
            title="Gulabi Nagari Royal Heritage Elegance",
            description="Warm terracotta, pale pink, and antique brass tones reflecting the Pink City's architecture, lit by 1,000 flickering clay diyas at dusk.",
            cultural_context="Honors historic Rajputana palace aesthetics with sustainable local terracotta crafts.",
            cost_bracket="₹₹"
        ),
        IdeaItem(
            id="i-wed-02",
            tab_category="decor",
            title="Torana of Mango Leaves & Marigold Shimmer",
            description="Entrance gates adorned with auspicious mango leaves (Amra pallava) and layered saffron genda phool to invite divine blessings.",
            cultural_context="Traditional Indian welcome symbolism dispelling negative energies.",
            cost_bracket="₹"
        ),
        IdeaItem(
            id="i-wed-03",
            tab_category="menu",
            title="Live Ker Sangri & Kesari Ghevar Stations",
            description="Authentic Rajasthani desert delicacies prepared hot on live griddles, paired with saffron-infused rabri in eco-friendly clay bowls.",
            cultural_context="Signature celebratory dessert of Rajasthan symbolizing sweetness in married life.",
            cost_bracket="₹₹"
        ),
        IdeaItem(
            id="i-wed-04",
            tab_category="rituals",
            title="Mayra (Bhaat) Maternal Blessing Ceremony",
            description="Grand maternal uncle procession carrying traditional silver gifts, brass cookware, and handwoven Bandhej sarees to honor the bride's lineage.",
            cultural_context="Essential Marwari kinship ritual honoring maternal family ties.",
            cost_bracket="₹₹"
        ),
        IdeaItem(
            id="i-wed-05",
            tab_category="games",
            title="Palki Arrival & Antakshari Jugalbandi",
            description="Friendly musical face-off between Bride's and Groom's families featuring classic Bollywood and Rajasthani folk lyrics.",
            cultural_context="Breaks the ice between families before formal Pheras begin.",
            cost_bracket="₹"
        ),
        IdeaItem(
            id="i-wed-06",
            tab_category="gifts",
            title="Handcrafted Blue Pottery & Attar Vials",
            description="Authentic Jaipur GI-tagged blue pottery spice jars paired with pure Kannauj Gulab attar in embroidered silk pouches.",
            cultural_context="Supports local heritage artisans and provides guests with an everlasting fragrant keepsake.",
            cost_bracket="₹₹"
        ),
    ],
    auspicious_guidance="Godhuli Vela (dusk sunset window, 05:45 PM - 06:30 PM) is considered supreme for Lagna and Saptapadi vows in Rajasthan during Rohini Nakshatra.",
    disclaimer="Notice: Timings, muhurat guidance, and vendor quotes are AI-assisted estimates for budgeting purposes only."
)
