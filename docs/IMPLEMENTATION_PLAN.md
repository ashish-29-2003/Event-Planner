# Implementation & Hackathon Execution Plan - Utsav (उत्सव)

**Document Version:** 1.0.0-PROD  
**Author:** Technical Lead & Staff Product Manager  
**Date:** 2026-10-23  

---

## 1. Step-by-Step Build Sequence & Scaffolding Commands

### 1.1 Python Environment & Tooling Setup
```bash
# 1. Verify Python 3.10+ installation
python --version

# 2. Initialize and activate virtual environment
python -m venv .venv
# On Windows PowerShell:
.\.venv\Scripts\Activate.ps1

# 3. Install core dependencies
pip install fastapi uvicorn[standard] pydantic google-genai google-generativeai mangum httpx pytest pytest-asyncio python-multipart python-dotenv icalendar
```

### 1.2 Local Single-Command Runner
The project includes a root runner `run.py` to allow launching the full application with a single command:
```bash
python run.py
```
This initializes FastAPI, loads seed datasets, verifies environment variables, starts Uvicorn at `http://127.0.0.1:8000`, and opens the browser.

### 1.3 Netlify & GitHub Integration
```bash
# Initialize git repository
git init
git add .
git commit -m "feat(scaffold): initialize Utsav GenAI celebration planner"

# Connect to GitHub remote and push
git branch -M main
git remote add origin https://github.com/<username>/utsav-celebration-planner.git
git push -u origin main
```
Netlify automatically detects `netlify.toml`, deploys the `public/` folder to the global edge network, and wraps the FastAPI application inside `netlify/functions/api.py`.

---

## 2. Milestone Deliverables & Definition of Done (DoD)

### Milestone 1: Baseline Architecture (Stage 1)
- **Deliverables:** Working FastAPI server, Pydantic schemas, Netlify serverless wrapper, basic test suite passing.
- **DoD:** `python run.py` serves `/api/health` returning `200 OK`; `pytest` passes.

### Milestone 2: Google Services & Security Foundation (Stage 2)
- **Deliverables:** Official Google GenAI Python SDK integration, rate limiting, prompt injection defense, persistent storage layer.
- **DoD:** Route `/api/ai/plan` accepts a celebration brief, enforces schema, and falls back to deterministic blueprint if quota is 0.

### Milestone 3: The Four Pillars (Stage 3)
- **Deliverables:** Onboarding wizard, interactive budget planner with AI re-balancing, timeline with .ics export, vendor checklist, and personalized cultural ideas hub.
- **DoD:** All 4 pillars tested end-to-end for Weddings, Birthdays, and Community events.

### Milestone 4: Cultural Design & Polish (Stage 4)
- **Deliverables:** Warm ivory and deep indigo themes, Noto Serif Devanagari typography, diya loading pulse, budget tickers, confetti bursts.
- **DoD:** Matches design system tokens; zero layout shift; responsive from 360px to 4K.

### Milestone 5: Testing, Hardening & Deployment (Stages 5–8)
- **Deliverables:** 100% test pass rate, WCAG 2.2 AA accessibility verified, Git repository pushed to GitHub, live Netlify deployment URL verified.
- **DoD:** Live URL operational; zero console errors.

---

## 3. Risk Register & Mitigations

| Risk ID | Risk Description | Severity | Likelihood | Mitigation Strategy |
|---|---|---|---|---|
| **RSK-01** | Gemini API quota exhausted during hackathon judging. | Critical | Medium | Automatic failover to rich, curated local celebration blueprints with an unobtrusive banner notifying the user. Zero user-facing crashes. |
| **RSK-02** | Netlify serverless function 10-second timeout. | High | Low | Gemini 1.5 Flash generates structured plans in ~3.2s; streaming endpoints use SSE; timeout cap set to 8s before serving fallback. |
| **RSK-03** | Prompt injection or jailbreak attempts via user brief. | Medium | Low | Strict input sanitization in `sanitizer.py`, XML boundary tags, and strict Pydantic v2 schema enforcement. |
| **RSK-04** | Devanagari text rendering or clipping on older browsers. | Medium | Low | Preloaded Google Fonts with explicit CSS `line-height: 1.6` for all Devanagari typographic elements. |

---

## 4. 3-Minute Hackathon Judge Demo Script

**Objective:** Walk the judges through the 4 pillars in under 180 seconds, highlighting Google GenAI reasoning, cultural authenticity, and financial precision.

### Scene 1: Arrival & Auspicious Beginning (0:00 - 0:35)
1. **Host Action:** Open `utsav-ai.netlify.app` (or `http://localhost:8000`).
2. **Audio/Narration:**
   > *"Welcome to Utsav (उत्सव) — where every celebration begins with शुभ आरम्भ. Planning an Indian celebration across weddings, birthdays, and community festivals is notoriously chaotic. Today, we demonstrate how Google Gemini and our Python architecture turn a brief into an actionable celebration master plan in seconds."*
3. **Visual Highlights:** Point out the time-of-day greeting (*शुभ संध्या, Ashish*), the daily Sanskrit Subhashita, and the warm ivory cultural palette.

### Scene 2: Four Pillars in Action (Jaipur Royal Wedding) (0:35 - 1:45)
1. **Host Action:** Click *"Explore Jaipur Royal Wedding"* (or input brief in Onboarding Wizard).
2. **Narration:**
   > *"In one click, Utsav generates the Four Core Pillars:*
   > *Pillar 1: An authentic ₹45 Lakh Marwari wedding budget with live category breakdowns.*
   > *Pillar 2: A 6-month countdown timeline with Day-Of Muhurat milestones, exportable directly to Google Calendar.*
   > *Pillar 3: A categorized vendor checklist with real-market quotes and scope of work.*
   > *Pillar 4: Personalized cultural ideas spanning authentic Rajasthani menus, traditional Sangeet choreography, and eco-friendly return hampers."*

### Scene 3: Live AI Re-Balancing & Cultural Intelligence (1:45 - 2:30)
1. **Host Action:** Navigate to Budget Matrix. Increase Palace Venue cost by ₹3,00,000. Point out the over-budget warning. Click *"AI Re-Balance Budget"*.
2. **Narration:**
   > *"Watch our Python Gemini financial agent re-balance the budget in real time. It intelligently shaves allocations from flexible luxury decor while safeguarding food and catering minimums, accompanied by an explicit financial rationale."*

### Scene 4: Export, Sharing & Resilience (2:30 - 3:00)
1. **Host Action:** Navigate to Export Sheet. Add a personal blessing note: *"With love and blessings from Nanaji & Nanima."* Click Print/PDF preview.
2. **Narration:**
   > *"Finally, the user generates a royal, printable celebration master sheet complete with their personal family blessing. And if API quotas are ever exhausted, Utsav's deterministic fallback engine ensures 100% uptime for every family. शुभ आरम्भ: every celebration begins well."*

---

## 5. Final Submission Checklist

- [ ] All 12 `.md` documentation files present in `/docs` and `README.md` at root.
- [ ] Application starts with single command: `python run.py`.
- [ ] Working demo mode with 3 pre-seeded celebrations (Wedding, Birthday, Community).
- [ ] Netlify configuration verified (`netlify.toml`, `netlify/functions/api.py`).
- [ ] Git repository initialized, commits made, pushed to GitHub.
- [ ] All tests pass (`pytest -v`).
- [ ] Axe accessibility audit clean (zero critical/serious violations).
- [ ] Judge demo rehearsed and ready.
