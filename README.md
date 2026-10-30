# Samaroh (समारोह) — GenAI Celebration & Event Planner

> **॥ शुभ आरम्भ: every celebration begins well ॥**  
> An intelligent, culturally grounded celebration planning assistant for weddings, birthdays, and community festivals, powered by Google Gemini and built in Python.

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Google Gemini](https://img.shields.io/badge/Google%20GenAI-Gemini%201.5%20Flash-orange.svg)](https://ai.google.dev/)
[![Netlify Status](https://img.shields.io/badge/Netlify-Deploy%20Ready-00C7B7.svg)](https://www.netlify.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Built for **PromptWars Virtual** (Google for Developers x H2S, "Build with AI", India).

---

## 🌟 Overview & Key Features

Samaroh eliminates the chaos of disjointed spreadsheets, notes, and WhatsApp chats by transforming an event brief into an actionable celebration master plan in seconds:

1. **💰 Dynamic Budget Planner with AI Re-Balancing:**
   - Real-time Lakh & Crore budget tracking across Venue, Catering, Decor, Photography, Entertainment, and Logistics.
   - Live payment tracking (Advance Paid vs. Balance Due) and visual over-budget warnings.
   - **One-Click AI Re-Balancing:** An intelligent financial agent that recalculates allocations when a category overspends, protecting core necessities like catering while trimming flexible luxury lines.

2. **⏳ Phased Countdown Timeline & Google Calendar Sync:**
   - Auto-generated 5-phase schedule: Foundation, Core Bookings, Details & Invites, Final Week, and Day-Of Run of Show.
   - Task assignment by owner role (Host, Uncle, Caterer, Decorator).
   - Instant export to RFC-5545 `.ics` file and direct deep-links to **Google Calendar**.

3. **📋 Categorized Vendor Checklist & Discovery:**
   - Covers Indian celebratory requirements: Pandits, Royal Halwais, Mandap Decorators, Mehendi Artists, Dholwalas, Stage Sound, and Candid Photographers.
   - Quote tracking, contact management, and local market quote bands.

4. **🌺 Culturally Personalized Ideas Hub:**
   - Tailored to regional culture (Marwari, Punjabi, South Indian Tamil, Bengali, Contemporary Urban).
   - Six interactive hubs: Theme & Mood, Decor Accents, Curated Regional Menu, Sacred Rituals, Interactive Games, and Return Gifts.

5. **✨ Cultural Craft & Auspicious Heritage:**
   - Classical Sanskrit invocations (*शुभ आरम्भ*, *मङ्गलम्*, *स्वागतम्*, *धन्यवादः*).
   - Daily authentic Subhashita with scholarly attribution and English translation.
   - Personalized time-of-day greetings (*शुभ संध्या, Ashish*) and personal family blessing notes on exports.
   - Sacred Diya flame pulse loader during AI generation.

6. **🛡️ 100% Demo Resilience:**
   - Instant Demo Mode loaded with 3 complete celebrations:
     - 💒 **Jaipur Royal Destination Wedding** (350 guests, ₹45L)
     - 🎂 **Bengaluru Cosmic Space Explorer Birthday** (45 guests, ₹85K)
     - 🏮 **Delhi NCR Society Diwali Mela & Dandiya** (800 residents, ₹6.5L)
   - Zero-crash fallback engine guaranteeing 100% uptime even if upstream Gemini API quotas are exhausted.

---

## 🏗️ Technical Architecture & Google Services

Samaroh is built as an asynchronous **Python-Native Full-Stack Application** designed for seamless local development and cloud serverless hosting:

- **Backend:** Python 3.10+ with **FastAPI**, **Pydantic v2**, and **Uvicorn**.
- **GenAI Engine:** Official **Google GenAI Python SDK** (`google-genai`) using `gemini-1.5-flash` with structured Pydantic schema decoding and streaming SSE chat.
- **Frontend:** Premium, responsive UI served directly by FastAPI and Netlify CDN, featuring Tailwind CSS, Google Fonts (*Noto Serif Devanagari* and *Plus Jakarta Sans*), and Lucide icons.
- **Cloud Deployment:** **Netlify** (via `netlify.toml` and Mangum serverless adapter for Python).
### 🌐 Google Services Architecture & Integration Matrix

Samaroh integrates with Google platforms across three architectural tiers: **4 Core Backend Google Cloud/Firebase APIs**, **1 Server-Proxied Google API**, and **2 Client-Side Integrations**.

#### 1. Core Backend Google APIs & Cloud Services
| # | Google Service | Purpose in Samaroh | Implementation File Paths | Required Environment Variables | Test Command |
|---|---|---|---|---|---|
| 1 | **Gemini API** (`google-genai`) | Multi-agent celebration planning, structured schema generation, SSE streaming chat, and budget re-balancing | `src/services/gemini_service.py`<br>`src/api/ai_routes.py` | `GEMINI_API_KEY`<br>`GEMINI_MODEL` (defaults to `gemini-2.0-flash`) | `pytest tests/test_mock_integrations.py` |
| 2 | **Firebase Authentication** (`firebase-admin`) | User identity verification, Bearer ID token validation, Google Sign-In popup/redirect, tenant isolation | `src/utils/auth.py`<br>`public/js/auth.js`<br>`src/api/event_routes.py` | `FIREBASE_PROJECT_ID`<br>`FIREBASE_CREDENTIALS_PATH`<br>`ENABLE_AUTH_ENFORCEMENT` | `pytest tests/test_browser_auth.py`<br>`pytest tests/test_route_auth_guards.py` |
| 3 | **Cloud Firestore** (`google-cloud-firestore`) | Durable multi-tenant NoSQL persistence for celebrations, subcollections (budgets, tasks, vendors, ideas, guests), and security rules enforcement | `src/services/storage_service.py`<br>`firestore.rules` | `STORAGE_BACKEND=firestore`<br>`FIREBASE_PROJECT_ID` | `pytest tests/test_firestore_backend.py`<br>`pytest tests/test_firestore_rules_matrix.py` |
| 4 | **Firebase App Check** (`firebase-admin`) | Cryptographic abuse prevention and bot protection on AI plan generation endpoints with fail-closed production verification | `src/utils/app_check.py`<br>`src/api/ai_routes.py` | `ENABLE_APP_CHECK`<br>`APP_CHECK_DEV_BYPASS` | `pytest tests/test_app_check.py`<br>`pytest tests/test_logging_redaction.py` |

#### 2. Server-Proxied Google Services
| # | Service | Purpose | Architecture & Security | Required Environment Variables | Test Command |
|---|---|---|---|---|---|
| 5 | **Google Maps Places API** (`httpx`) | Curated venue & vendor discovery with address, rating, and opening hours | Backend server proxy (`/api/places/search`); API key never exposed to browser; falls back to curated verified Indian vendor catalog if unconfigured | `GOOGLE_MAPS_API_KEY` (optional) | `pytest tests/test_places_contract.py` |

#### 3. Client-Side Platform Integrations
| # | Integration | Purpose | Implementation Details | Test Command |
|---|---|---|---|---|
| 6 | **Google Calendar** (RFC-5545 & Deep Links) | Phased celebration timeline sync, milestone due date deep linking, and RFC-5545 `.ics` export | `src/services/calendar_service.py`<br>`src/api/export_routes.py` | `pytest tests/test_mock_integrations.py -k test_calendar` |
| 7 | **Google Fonts** (Web CDN) | Cultural typography: *Noto Serif Devanagari*, *Cinzel*, and *Plus Jakarta Sans* | `public/index.html`<br>`public/css/styles.css` | `pytest tests/test_accessibility_axe.py` |


---

## 🚀 Quick Start (One Command)

### Prerequisites
- Python 3.10 or higher installed.
- Git.

### 1. Clone the Repository & Set Up Virtual Environment
```bash
git clone https://github.com/ashish-29-2003/Event-Planner.git
cd Event-Planner

# Create and activate virtual environment
python -m venv .venv
# On Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# On Linux / macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Set Up Environment Variables
Copy `.env.example` to `.env`:
```bash
# On Linux / macOS:
cp .env.example .env
# On Windows (PowerShell):
Copy-Item .env.example .env
```
Add your Google Gemini API key:
```env
GEMINI_API_KEY="your-gemini-api-key-here"
```
*(Note: If no API key is supplied, Samaroh gracefully falls back to its curated celebration blueprints!)*

### 3. Launch the Application
Run the single root launcher:
```bash
python run.py
```
This automatically verifies dependencies, starts the FastAPI server at `http://127.0.0.1:8000`, and opens your web browser.

---

## 🎬 3-Minute Hackathon Judge Demo Script

Follow this step-by-step walkthrough to evaluate Samaroh's capabilities in under 3 minutes:

### Minute 1: Cultural Warmth & First Impressions
1. **Launch**: Open [Live Demo on Netlify](https://utsav-ai.netlify.app/) (or run `python run.py` locally).
2. **First Glimpse**: Notice the high-contrast Subhashita bar (*॥ सर्वे भवन्तु सुखिनः सर्वे सन्तु निरामयाः ॥*), single-language cultural greeting by time of day, and subtle geometric mandala rangoli watermark (3% opacity).
3. **Themes & Accents**: Toggle between Light and Dark mode using the animated SVG sun/moon toggle. Notice the accent dynamically morphs to ceremonial vermilion & gold for weddings, marigold for birthdays, and royal indigo for community festivals.
4. **Celebration Switcher**: Press `Tab` or click the accessible celebration switcher. Use the arrow keys (`↓` / `↑`) to navigate between the 3 seeded master celebrations: *Jaipur Royal Vivaha* (350 guests, ₹35L), *Bengaluru Cosmic Birthday* (45 guests, ₹85K), and *Delhi Diwali Dandiya Mela* (800 residents, ₹6.5L).

### Minute 2: Core Four Pillars & Real-Time AI Financial Re-Balance
1. **Budget Matrix & Two-Segment Progress Bar**: Navigate to the **Budget** tab. Observe the two-segment progress bar showing settled payments (green) and committed allocations (amber) against target budget.
2. **Live AI Re-Balancing**: Change a budget line or click **AI Re-Balance**. Watch the mathematical allocator adjust flexible luxury lines (decor, entertainment) while fiercely protecting core essentials (catering, sacramental muhurat rituals) with a detailed rationale.
3. **Phased Timeline & Relative Deadlines**: Open the **Timeline** tab. See auto-sequenced phases with relative countdown tags (*"in 16 days"*, *"Due today"*), toggleable milestones, and owner roles (Host, Caterer, Decorator).
4. **Curated Vendors & Places Discovery**: Switch to the **Vendors** tab. Notice categorized quotes for Indian weddings (Mandap, Halwai, Pandit, Mehendi, Dhol) with Google Maps Places proxy search.
5. **Ideas & Guests**: Explore the 6-dimensional **Ideas** hub and **Guests & RSVP** tracker with party sizing and dietary preferences.

### Minute 3: Multi-Tenant Identity, Sovereign Sharing & Export
1. **Google Identity & Tenant Isolation**: Sign in via Google popup/redirect. Notice private storage isolation (`/users/{uid}/events/{id}`) backed by Cloud Firestore and local persistence surviving server restarts.
2. **Cryptographic Share Drawer**: Click **Share Celebration**. Generate a time-bound HMAC-SHA256 signed token. Click **WhatsApp** for instant family coordination or copy the secure link.
3. **Google Calendar Sync**: Click **Add to Google Calendar** to trigger direct deep linking or export a standard RFC-5545 `.ics` file.
4. **Vedic Stewardship**: Scroll to the structured footer with Vedic guidance disclaimers and privacy pledges (zero advertising, zero PII sold).

---

## 🧪 Running Automated Tests & Code Quality

Samaroh is engineered with evidence-backed quality guarantees:

```bash
# 1. Run full test suite with coverage gate (245 tests, 88% overall statement coverage)
python -m pytest --cov=src --cov-fail-under=80 -v

# 2. Run Python strict typing audit (32/32 source files passing)
python -m mypy --strict src/

# 3. Run expanded Ruff lint rules (E, F, I, B, UP, S, SIM, C4)
python -m ruff check .

# 4. Run automated axe-core accessibility matrix (0 critical, 0 serious WCAG violations)
python -m pytest tests/test_accessibility_axe.py -v

# 5. Run Web Vitals and performance benchmarks (<30KB gzipped bundle, LCP <450ms)
python -m pytest tests/test_performance_and_vitals.py -v

# 6. Run live deployment smoke test (6/6 checks passing)
python scripts/smoke_test.py --url http://127.0.0.1:8000
```

---

## 🌐 Deploying to Netlify

Samaroh is configured out of the box for Netlify deployment:

1. Push your code to your GitHub repository (`https://github.com/ashish-29-2003/Event-Planner.git`).
2. In Netlify, click **"Add new site"** → **"Import an existing project"** and select your GitHub repository.
3. Netlify will automatically detect `netlify.toml`:
   - **Publish directory:** `public`
   - **Functions directory:** `netlify/functions`
4. In the Netlify dashboard under **Site configuration > Environment variables**, add:
   - `GEMINI_API_KEY`: Your Google Gemini API Key.
5. Click **Deploy Site**. Every subsequent git push to `main` will automatically build and deploy!

---

## 📚 Complete Project Documentation

Every aspect of the architecture, product requirements, security, and design is documented in `/docs`:

| Document | Description |
|---|---|
| [**PRD.md**](docs/PRD.md) | 13-section Product Requirements Document |
| [**ARCHITECTURE.md**](docs/ARCHITECTURE.md) | System architecture & Mermaid topology diagrams |
| [**AGENTS.md**](docs/AGENTS.md) | Multi-agent prompts, schemas, and hallucination controls |
| [**DECISIONS.md**](docs/DECISIONS.md) | Architecture Decision Records (ADRs) |
| [**TASKS.md**](docs/TASKS.md) | Granular master task board |
| [**TRD.md**](docs/TRD.md) | Technical requirements, performance budgets & dependencies |
| [**APP_FLOW.md**](docs/APP_FLOW.md) | End-to-end Mermaid user journey flowcharts |
| [**UI_UX_FLOW.md**](docs/UI_UX_FLOW.md) | Design system, tokens, wireframes & Sanskrit typography |
| [**BACKEND_SCHEMA.md**](docs/BACKEND_SCHEMA.md) | Pydantic data models, ERD diagram & seed datasets |
| [**SECURITY_AND_TESTING.md**](docs/SECURITY_AND_TESTING.md) | STRIDE threat model, loop defense & testing strategy |
| [**IMPLEMENTATION_PLAN.md**](docs/IMPLEMENTATION_PLAN.md) | Step-by-step build sequence & 3-minute judge demo script |
| [**STAGE_STATUS.md**](docs/STAGE_STATUS.md) | Stage-gated execution tracker |

---

## 📜 License
Distributed under the MIT License. Built with devotion for Indian celebrations.
