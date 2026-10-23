# Product Requirements Document (PRD) - Utsav (उत्सव)

**Product Name:** Utsav (उत्सव)  
**Tagline:** *शुभ आरम्भ: every celebration begins well.*  
**Target Event:** PromptWars Virtual (Google for Developers x H2S, "Build with AI")  
**Product Version:** 1.0.0-PROD  
**Author:** Staff Product Manager & Technical Lead  
**Date:** 2026-10-23  

---

## 1. Product Vision

### 1.1 Overview & Problem Statement
Planning an Indian celebration—whether an intricate 3-day wedding in Jaipur, an imaginative 5th birthday party in Bengaluru, or an 800-resident Diwali Mela in Delhi NCR—is an overwhelming logistical, financial, and emotional challenge. Families and community organizers currently juggle dozens of disjointed tools: Excel sheets for budgets, WhatsApp groups for vendor quotes, notes apps for rituals, and disparate calendar apps for countdowns.

Crucially, off-the-shelf Western event planning software completely ignores the cultural nuances of Indian festivities:
- Complex regional rituals (Mehendi, Haldi, Sangeet, Muhurat timings, Satyanarayan Puja, Griha Pravesh).
- Traditional vendor categories (Pandits, Dholwalas, Mehendi artists, Shamiana/tent houses, Halwais/caterers).
- Indian financial realities (Lakh/Crore budgeting, cash vs. UPI advances, complex vendor milestones).
- Community dynamics (RWA permissions, society committee approvals, Prasad distribution, cultural competitions).

**Utsav** bridges this gap as a world-class GenAI Celebration & Event Planner. By combining Google Gemini's advanced reasoning (via the official Google GenAI Python SDK) with an authentic, respectful cultural design system, Utsav transforms an unstructured prompt or conversational brief into an actionable, end-to-end celebration blueprint in under 10 seconds.

### 1.2 Target Audience
1. **Indian Families:** Organizing milestone life events (Weddings, Engagements, Anniversaries, Upanyanam/Thread ceremonies, Griha Pravesh).
2. **Parents:** Organizing thematic birthdays, naming ceremonies (Namkaran), and milestone celebrations.
3. **Resident Welfare Associations (RWAs) & Community Leaders:** Organizing housing society festivals (Diwali, Holi, Ganesh Utsav, Navratri, Durga Puja, Eid, Christmas).
4. **Independent Boutique Event Planners:** Seeking a fast, intelligent client pitching and co-planning workspace.

### 1.3 Strategic Goals & Hackathon Success Metrics
| Metric Category | Target Value | Verification Method |
|---|---|---|
| **Demo Completion Time** | < 3 minutes for judges to witness all 4 core pillars | Judge script walkthrough |
| **GenAI Plan Generation Time** | < 5.0 seconds for full structured plan; < 1.0s TTFT (Time to First Token) on streaming | Route handler telemetry |
| **Plan Structured Schema Accuracy** | 100% adherence to Pydantic v2 validation (0 runtime JSON parsing crashes) | Server validation unit tests |
| **Lighthouse Score** | ≥ 90 on Performance, Accessibility, Best Practices, and SEO | Chrome DevTools Lighthouse audit |
| **Accessibility Standard** | Zero critical/serious WCAG 2.2 AA violations | `@axe-core` test run |
| **Offline/Quota Resilience** | 100% uptime with instant fallback to curated demo celebration blueprints | Integration test with simulated 429 quota exhaustion |

---

## 2. User Personas

### Persona 1: Sunita Agarwal (52) – The Bride's Mother & Wedding Lead
- **Location:** Jaipur / Delhi NCR
- **Event:** Daughter's 3-Day Wedding (Vivaha) — 350 Guests, Budget: ₹35,00,000
- **Motivations:** Wants an auspicious, culturally immaculate wedding honoring Marwari traditions while avoiding budget runaway.
- **Pain Points:** Overwhelmed by vendor follow-ups, unclear vendor quotes, anxious about missing ritual items (*samagri*), family WhatsApp chaos.
- **Goal in Utsav:** Generate a 6-month countdown checklist, allocate budget across Mehendi, Sangeet, and Reception, and track vendor advances.

### Persona 2: Vikram & Neha Nair (34 & 32) – The Techie Parents
- **Location:** Bengaluru, Karnataka
- **Event:** Son Aarav's 5th Birthday — 40 Kids & Parents, Budget: ₹60,000
- **Motivations:** Desires an unforgettable, creative theme ("Little Astronauts in Space") with engaging games, kid-safe food, and zero plastic return gifts.
- **Pain Points:** Time-constrained due to demanding tech jobs; lacks ideas for structured 3-hour toddler schedules.
- **Goal in Utsav:** Rapidly get an hour-by-hour timeline, themed menu, game playlist, and return-gift recommendations in 2 minutes.

### Persona 3: Rajesh Sharma (46) – The Society RWA Secretary
- **Location:** Dwarka, New Delhi
- **Event:** Annual Society Diwali Mela & Cultural Evening — 600 Residents, Budget: ₹4,00,000
- **Motivations:** Delivering a safe, vibrant community event that unites residents across all age groups within committee-approved budgets.
- **Pain Points:** Tracking police/fire clearance deadlines, stage audio setup, stall vendor allocations, and avoiding overspending on lighting.
- **Goal in Utsav:** Society-specific vendor checklist (generator backup, tent, security), committee-shareable PDF summary, and volunteer assignment.

### Persona 4: Tanya Mehta (27) – Modern Boutique Event Planner
- **Location:** Mumbai / Remote
- **Event:** Multiple parallel clients (Engagements, Roce ceremonies, Cocktail evenings)
- **Motivations:** Rapidly drafts mood boards, initial budgets, and vendor checklists to pitch prospective clients within 15 minutes of an intake call.
- **Pain Points:** Repetitive manual drafting of initial proposals; needs polished, shareable PDF and .ics exports.
- **Goal in Utsav:** Fast conversational AI drafting, live budget re-balancing slider, and client-ready export sheets.

---

## 3. Functional Requirements

### 3.1 Mapping the Four Core Pillars Across the Three Event Types

To guarantee **100% Problem Statement Alignment**, Utsav treats the Four Pillars as first-class, dedicated modules across Weddings, Birthdays, and Community Celebrations:

| Core Pillar | Weddings (e.g. Jaipur Destination / Traditional Vivaha) | Birthdays (e.g. Themed Kid / Milestone Adult) | Community Events (e.g. Society Diwali / Dandiya Mela) |
|---|---|---|---|
| **1. Budget Planner** | Multi-day split (Mehendi, Sangeet, Pheras, Reception), vendor advance payments, cash/envelope reserve, AI re-balancing when venue exceeds target. | Per-child catering estimates, entertainment/clown/magician allocation, customized cake, return gifts budget. | RWA funds vs. ticket/stall revenue, sound/light permits, security personnel, stage fabrication, prasad/sweets. |
| **2. Timeline / Checklist** | 6-month countdown down to day-of hour-by-hour muhurat schedule (Baraat arrival, Jai Mala, Pheras, Bidaai). | 4-week countdown down to party-day run of show (Welcome drinks, magic show, cake cutting, party games, gifts). | 8-week countdown covering police permissions, sound licenses, stall vendor bookings, stage setup, clean-up crew. |
| **3. Vendor Checklist** | Pandit/Officiant, Mandap Decorator, Halwai, Mehendi Artists, Bridal Makeup, Dhol, Candid Photographer, Choreographer. | Cake designer, party entertainer, balloon/eco-decor, photographer, catering, mascot/animator. | Audio-visual & sound engineering, tent/shamiana, event security, waste management, municipal permits, food trucks. |
| **4. Personalized Ideas** | Regional rituals, auspicious colour palettes, choreography song tracks, personalized wedding hashtag, return favours (*mithai hampers*). | Thematic decor ideas, interactive games (Pin the Tail, Scavenger Hunt), kid-friendly mocktails, sustainable eco-hampers. | Society rangoli competitions, senior citizen seating zones, diya-lighting ceremony, patriotic/cultural playlists. |

---

### 3.2 Feature-by-Feature Detailed Specifications

#### Feature 1: Onboarding & Celebration Personalization
- **User Story:** *As a user, I want to input my celebration parameters (type, culture/tradition, city, date, budget, guest count) so that the AI tailors all suggestions to my exact context.*
- **User Flow:**
  1. User selects Event Type (Wedding, Birthday, Community Event, Festival / Puja, Anniversary / Other).
  2. User enters Celebration Title (e.g., "Riya & Kabir's Vivaha").
  3. User specifies Cultural Background (e.g., North Indian Hindu, Marwari, South Indian Tamil, Punjabi, Bengali, Contemporary Inter-faith, Secular).
  4. User enters Host City (e.g., Jaipur, Delhi NCR, Mumbai, Bengaluru, Lucknow) and expected Date (or uses Muhurat Helper).
  5. User inputs Target Budget (with Lakh/Crore selector) and expected Guest Count.
  6. User chooses Language Style (English, Hindi, Sanskritized English).
- **Validation Rules:**
  - Event title: 2–80 characters.
  - Budget: Must be positive number (Min ₹5,000, Max ₹10,00,00,000).
  - Guest count: Integer between 2 and 50,000.
  - Date: Must be present or future date (or flagged as "Date TBD / Flexible").
- **Edge Cases:** Budget entered as 0 or negative; city not found; past dates; extreme guest counts (e.g., 20,000). Handled with inline error banners and assistive defaults.
- **Empty & Loading States:** Diya pulse animation while preparing workspace; instant transition to AI Planner.

#### Feature 2: Conversational GenAI Planner (Python FastAPI + Gemini)
- **User Story:** *As a user, I want to talk to an intelligent planning assistant or click 'Generate Full Plan' to receive an integrated, customized event plan in seconds.*
- **User Flow:**
  1. User can either click "Auto-Generate Plan" or converse with the AI Planner in a streaming chat interface.
  2. User can prompt: *"We want an eco-friendly Rajasthani royal sangeet on a ₹15 Lakh budget with authentic local food and folk dancers."*
  3. AI streams response in markdown with interactive cards directly updating the event state via Server-Sent Events (SSE).
- **Validation:** Streaming parser validates incoming chunks; structured JSON endpoint validates response against `EventPlanSchema` (Pydantic v2).
- **Error Handling:** If Gemini API returns 429 (Rate Limit) or network disconnects, the system automatically triggers a repair prompt or smoothly falls back to rich pre-seeded event templates with a toast alert.

#### Feature 3: Dynamic Budget Planner with AI Re-Balancing
- **User Story:** *As a host, I want a breakdown of expenses across categories, real-time calculation of paid vs. pending balances, and an AI button to automatically re-balance my budget if one category overspends.*
- **User Flow:**
  1. Displays overall budget progress bar (Allocated vs. Target Budget).
  2. Category cards (Venue, Catering, Decor, Photography, Entertainment, Attire & Beauty, Logistics, Miscellaneous).
  3. Each item has: Name, Estimated Cost, Actual Cost, Advance Paid, Payment Status (`Pending`, `Partial`, `Paid`), and Vendor Link.
  4. **AI Re-Balance Action:** When the user increases the Venue budget by ₹2,00,000, clicking *"AI Re-Balance"* prompts the Python backend to run Gemini's financial re-balancing agent to intelligently shave modest percentages from flexible categories (e.g., Decor, Invites) without touching critical items (e.g., Catering minimums).
- **Edge Cases:** Total expenses exceeding 150% of budget triggers high-contrast amber/red warning toast and visual badges.

#### Feature 4: Interactive Countdown Timeline & Google Calendar Export
- **User Story:** *As a planner, I want an auto-generated timeline of tasks grouped by countdown phase (6 months out, 1 month out, 1 week out, Day-of schedule) and the ability to export to Google Calendar.*
- **User Flow:**
  1. Tasks categorized into chronological milestones:
     - Phase 1: Foundation (Venue, Budget, Dates).
     - Phase 2: Core Bookings (Caterer, Decorator, Photo).
     - Phase 3: Details & Invites (Wardrobe, Guest invitations, RSVPs).
     - Phase 4: Final Week (Samagri check, Final rehearsals, Vendor balances).
     - Phase 5: Day of Celebration (Hour-by-hour sequence of events).
  2. Each task includes: Title, Phase, Due Date, Owner (e.g., "Bride's Uncle", "Host", "Vendor"), Priority (`High`, `Medium`, `Low`), and Status (`To Do`, `In Progress`, `Done`).
  3. Clicking *"Export to Google Calendar"* generates a standards-compliant `.ics` file (built via Python `icalendar` or client generator) and opens direct `calendar.google.com` links.

#### Feature 5: Comprehensive Vendor Management & Discovery
- **User Story:** *As a planner, I want a categorized vendor checklist where I can track requirements, quotes, contact info, shortlists, and discover local vendors on Google Maps.*
- **User Flow:**
  1. Category filters: Venue, Catering, Decor, Photography, Mehendi/Makeup, Music/DJ, Pandit/Celebrant, Transport/Logistics.
  2. Vendor card includes: Name, Category, Contact Person, Phone, Email, Location, Rating, Quote Amount, Status (`To Research`, `Contacted`, `Shortlisted`, `Booked`, `Declined`), and Notes.
  3. **Google Maps / Places Integration:** When enabled, queries nearby venues and vendors based on event city. When disabled, seamlessly uses verified sample vendor cards with transparent pricing estimates labeled as *"Industry Estimate"*.

#### Feature 6: Culturally Personalized Ideas Generator
- **User Story:** *As a user, I want curated, creative ideas for themes, decor, menus, rituals, games, and return gifts tailored to my specific culture, city, and budget.*
- **User Flow:**
  1. Six tabbed idea hubs: **Theme & Mood**, **Decor Accents**, **Curated Menu**, **Rituals & Customs**, **Games & Engagement**, **Return Gifts / Favors**.
  2. Each idea card displays: Title, Cultural Context, Practical Execution Tip, Estimated Cost Bracket, and an *"Add to Tasks"* or *"Add to Budget"* direct action button.
- **Cultural Accuracy:** Grounded in genuine Indian traditions (e.g., Punjabi Boliyan, Maharashtrian Haldi Kunku, South Indian Thamboolam bags, Gujarati Garba choreography).

#### Feature 7: Auspicious Muhurat & Date Helper
- **User Story:** *As an Indian family planner, I want an AI helper that suggests auspicious seasonal windows and planetary considerations for my event type.*
- **Mandatory Disclaimer:** *"Notice: Muhurat windows are AI-assisted cultural estimates intended for initial planning purposes only. Please consult your family priest, astrologer, or authoritative regional Panchang (Drik/Thirukanitha) for sacramental ceremony confirmation."*

#### Feature 8: Lightweight Guest List & RSVP Tracker
- **User Story:** *As a host, I want to track invited guests, dietary requirements, RSVP statuses, and side (Bride/Groom or Adults/Kids) without external software.*
- **User Flow:**
  1. Quick add guest: Full Name, Group/Family, Count of Adults, Count of Kids, Dietary Preference (`Pure Veg`, `Jain`, `Non-Veg`, `Vegan`), RSVP Status (`Invited`, `Attending`, `Declined`, `Tentative`).
  2. Real-time counter of total confirmed heads for caterer coordination.

#### Feature 9: Multi-Event Management & Save/Resume
- **User Story:** *As an event host or planner, I want to create, switch between, and persist multiple celebrations in my account.*
- **User Flow:**
  1. Header celebration switcher dropdown allows switching between "Riya's Wedding", "Aarav's 5th Birthday", and "Diwali Mela".
  2. Persisted instantly in backend database and indexed by authenticated user ID.

#### Feature 10: PDF & Shareable Celebration Brief Export
- **User Story:** *As a planner, I want to export a beautifully formatted celebration plan summary (PDF or printable view) including an optional personal blessing note.*
- **User Flow:**
  1. User can enter an optional "Personal Blessing or Dedication" (e.g., *"With blessings from Dadi and Dada for a lifetime of love"*).
  2. Generates an elegant print-ready sheet with royal borders, auspicious emblems, budget summaries, timeline, and emergency contact list.

---

## 4. Information Architecture (IA)

```
[ App Root: / ]
   ├── / (Landing Page: Hero, Feature Highlights, Cultural Showcase, Demo Mode Trigger)
   ├── /auth (Authentication: Google Sign-in, Guest Session)
   ├── /dashboard (My Celebrations Hub, New Celebration Wizard)
   └── /events/{eventId} (Main Celebration Workspace)
         ├── /overview (Executive Dashboard, Countdown Ring, Quick Stats)
         ├── /ai-planner (Interactive Conversational AI Assistant)
         ├── /budget (Category Budgets, Live Ticker, AI Re-Balance)
         ├── /timeline (Milestone Checklist, Day-of Schedule, .ics Calendar Export)
         ├── /vendors (Vendor Checklist, Shortlists, Quotes, Map Discovery)
         ├── /ideas (Personalized Cultural Themes, Menu, Games, Gifts)
         ├── /guests (Guest List, Dietary Tracker, RSVP Ticker)
         ├── /muhurat (Auspicious Date & Seasonal Window Guidance)
         └── /export (Printable Summary Sheet, PDF Export, Family Blessing Note)
```

---

## 5. UI/UX Specification

### 5.1 Design Philosophy & Aesthetics
- **Core Aesthetic:** Modern luxury digital craftsmanship (Linear/Apple/Stripe precision) enriched with authentic Indian heritage accents.
- **Visual Warmth:** Avoid stark cold grays. Neutral surfaces are warm cream/ivory in light mode (`#FAF7F2`) and deep twilight indigo in dark mode (`#0B0F19`).
- **Accents:**
  - Royal Marigold (`#F59E0B` / Amber-500)
  - Kesari Saffron (`#EA580C` / Orange-600)
  - Sindoor Vermilion (`#E11D48` / Rose-600)
  - Temple Gold (`#D97706` / Amber-600)
  - Royal Indigo / Peacock (`#1E1B4B` / `#0284C7`)
- **Typography:**
  - Headings: `Noto Serif Devanagari` & `Playfair Display`
  - Body & UI Controls: `Plus Jakarta Sans` or `Inter`
  - Sanskrit Callouts: Rendered in Devanagari with proper line-height (`leading-relaxed`) and accompanying phonetic or English translation.
- **Auspicious Subhashita:** A rotating classical Sanskrit verse at the top of the dashboard:
  > *"सर्वे भवन्तु सुखिनः सर्वे सन्तु निरामयाः। सर्वे भद्राणि पश्यन्तु मा कश्चिद्दुःखभाग्भवेत्॥"*  
  > *"May all be prosperous and happy, may all be free from illness, may all see what is spiritually uplifting."* — Brihadaranyaka Upanishad

### 5.2 Micro-Interactions & Animation Specs
- **Spring Curves:** CSS cubic-bezier with `cubic-bezier(0.16, 1, 0.3, 1)` for cards and modals.
- **Budget Re-balancing:** Smooth animated number interpolation (ticker animation) over 600ms.
- **AI Synthesis State:** Diya flame with golden atmospheric radial glow pulsing gently at 1.8s cycles.
- **Task Completion:** Ink-spread checkmark with subtle celebratory gold confetti burst for milestone completion.
- **Reduced Motion:** When `(prefers-reduced-motion: reduce)` is enabled, all animations are replaced with instantaneous opacity fades (150ms).

---

## 6. Technical Architecture Summary

- **Backend Framework:** Python 3.10+ with FastAPI, Uvicorn, and Pydantic v2.
- **Deployment Platform:** Netlify with automated GitHub CI/CD, serving static assets and Python serverless functions via `netlify.toml` and Mangum.
- **GenAI Orchestration:** Official Google GenAI Python SDK (`google-genai` / `google-generativeai`) with structured JSON schema decoding via Pydantic v2.
- **Frontend Architecture:** Clean modern HTML5/CSS/JavaScript with Tailwind CSS, Lucide icons, SSE streaming client, and Google Fonts.
- **Observability:** Structured logging on FastAPI middleware with correlation IDs and performance timing.

---

## 7. API Design

### 7.1 `POST /api/ai/plan`
- **Purpose:** Generates a full structured event master plan from an onboarding brief.
- **Request Body:**
  ```json
  {
    "eventType": "wedding",
    "title": "Riya & Kabir's Vivaha",
    "culture": "Marwari Hindu",
    "city": "Jaipur",
    "guestCount": 350,
    "budget": 3500000,
    "date": "2026-12-14",
    "language": "en",
    "notes": "Vegetarian royal Rajasthani menu"
  }
  ```
- **Response (200 OK):** Validated `EventPlan` JSON object matching Pydantic `EventPlanSchema`.

### 7.2 `POST /api/ai/chat`
- **Purpose:** Handles conversational multi-turn planning queries with streaming SSE responses.
- **Response:** `text/event-stream` returning markdown chunks and interactive action cards.

### 7.3 `POST /api/ai/rebalance-budget`
- **Purpose:** Recalculates category allocations when one category budget changes.
- **Response:** Updated array of budget categories with rationale explanation.

### 7.4 `POST /api/ai/muhurat`
- **Purpose:** Returns auspicious date windows, nakshatra guidelines, and seasonal tips.

---

## 8. Data Models & Schemas

### 8.1 Core Entities
- `User`: `{ uid, email, displayName, language, createdAt }`
- `Event`: `{ id, userId, title, eventType, culture, city, date, targetBudget, guestCount, language, blessingNote, createdAt, updatedAt }`
- `BudgetItem`: `{ id, eventId, category, name, estimatedCost, actualCost, advancePaid, status, notes }`
- `TaskItem`: `{ id, eventId, phase, title, description, dueDate, owner, priority, status }`
- `VendorItem`: `{ id, eventId, category, name, contactPerson, phone, email, quoteAmount, status, notes, address }`
- `IdeaItem`: `{ id, eventId, tab, title, description, culturalContext, estimatedCostRange }`
- `GuestItem`: `{ id, eventId, name, group, adults, kids, diet, rsvpStatus }`

---

## 9. Performance Strategy

- **Lighthouse Performance Budget:**
  - Largest Contentful Paint (LCP): < 2.5s
  - Interaction to Next Paint (INP): < 200ms
  - Cumulative Layout Shift (CLS): < 0.1
- **AI Streaming:** Server-Sent Events (SSE) allow perceived response latency under 900ms.
- **Debounced Inputs:** Budget sliders and guest search fields debounced at 250ms.

---

## 10. Security & Compliance

- **Zero Client-Side Secrets:** Gemini API keys stored strictly in server environment variables on Netlify and local `.env`.
- **Rate Limiting:** Sliding-window limiter on `/api/ai/*` restricting requests to 15 calls / 10 minutes per IP/User.
- **Content Security Policy (CSP):** Enforced with strict script, frame, and connect-src directives.
- **Prompt Injection Defense:** Strict input sanitization stripping prompt delimiters, XML boundary framing (`<user_input>`), and schema validation on output.

---

## 11. Accessibility (WCAG 2.2 AA)

- **Contrast:** Strict 4.5:1 ratio for standard text, 3:1 for UI borders and icons.
- **Screen Reader Support:** Semantic HTML5, ARIA labels, live regions (`aria-live="polite"`).
- **Keyboard Navigation:** Full tab-order navigation with visible focus rings. Modal focus traps.
- **Multilingual Support:** Explicit `lang="hi"` tags for Devanagari text spans.

---

## 12. Development Roadmap

- **Milestone 1 (Scaffolding & Baseline):** Python virtual environment, FastAPI server, Pydantic schemas, Tailwind CSS UI, and pytest harness.
- **Milestone 2 (Google Services & Netlify Config):** Gemini API integration with Python SDK, rate limiting, and Netlify deployment setup.
- **Milestone 3 (Core Four Pillars):** Onboarding, AI Planner, Budget Planner, Timeline + .ics, Vendor Checklist, Personalized Ideas for all 3 event types.
- **Milestone 4 (Cultural UI & Polish):** Theme tokens, Sanskrit callouts, Diya animations, countdown ring, print/PDF export.
- **Milestone 5 (Hardening, QA & Deployment):** Edge-case testing, load testing, git commits, GitHub repository sync, and Netlify live deployment.
