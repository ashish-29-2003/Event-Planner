# Master Task Board - Utsav (उत्सव)

**Project:** Utsav - GenAI Celebration & Event Planner  
**Stack:** Python 3.10+ (FastAPI + Pydantic v2 + Google GenAI SDK) + Modern Cultural UI + Netlify  
**Author:** Staff Product Manager & Technical Lead  

---

## Stage 0: Architecture & Planning Deliverables

- [x] **TSK-001:** Author Architecture Decision Records (ADRs) in `docs/DECISIONS.md`.  
  *Role:* Senior Architect | *Est:* 2h | *Deps:* None  
  *Acceptance:* Documents naming, Python stack, Netlify hosting, Gemini model, and fallback strategy.
- [x] **TSK-002:** Author 13-section Product Requirements Document in `docs/PRD.md`.  
  *Role:* Staff PM | *Est:* 3h | *Deps:* TSK-001  
  *Acceptance:* Maps 4 core pillars across weddings, birthdays, and community celebrations.
- [x] **TSK-003:** Author System Architecture Specification in `docs/ARCHITECTURE.md`.  
  *Role:* Senior Architect | *Est:* 3h | *Deps:* TSK-001  
  *Acceptance:* Mermaid topology diagrams, Netlify serverless deployment, folder structure.
- [x] **TSK-004:** Author Multi-Agent AI Governance & Prompts in `docs/AGENTS.md`.  
  *Role:* AI Architect | *Est:* 2h | *Deps:* TSK-001  
  *Acceptance:* Defines 6 domain agents, system instructions, and hallucination controls.
- [x] **TSK-005:** Author Technical Requirements Document in `docs/TRD.md`.  
  *Role:* DevOps Lead | *Est:* 2h | *Deps:* TSK-003  
  *Acceptance:* Defines performance budgets, browser matrix, Python dependencies, and CI/CD.
- [x] **TSK-006:** Author End-to-End Application Flows in `docs/APP_FLOW.md`.  
  *Role:* UX Architect | *Est:* 2h | *Deps:* TSK-002  
  *Acceptance:* 7 detailed Mermaid flowcharts for all core user journeys.
- [x] **TSK-007:** Author UI/UX Design System in `docs/UI_UX_FLOW.md`.  
  *Role:* UI/UX Lead | *Est:* 2h | *Deps:* TSK-006  
  *Acceptance:* Design tokens, Sanskrit typography, diya animations, and wireframes.
- [x] **TSK-008:** Author Backend Data Models & ERD in `docs/BACKEND_SCHEMA.md`.  
  *Role:* Backend Lead | *Est:* 2h | *Deps:* TSK-003  
  *Acceptance:* ERD diagram, Pydantic schemas, and curated seed datasets.
- [x] **TSK-009:** Author Security Threat Model & Testing Strategy in `docs/SECURITY_AND_TESTING.md`.  
  *Role:* Security & QA | *Est:* 2h | *Deps:* TSK-003  
  *Acceptance:* STRIDE analysis, loop defense specs, and test pyramid plan.
- [x] **TSK-010:** Author Granular Master Task Board in `docs/TASKS.md`.  
  *Role:* Staff PM | *Est:* 2h | *Deps:* TSK-002  
  *Acceptance:* Every task assigned to a stage with estimates and acceptance criteria.
- [x] **TSK-011:** Author Step-by-Step Implementation & Demo Plan in `docs/IMPLEMENTATION_PLAN.md`.  
  *Role:* Technical Lead | *Est:* 2h | *Deps:* TSK-010  
  *Acceptance:* Scaffolding commands, risk register, and 3-minute hackathon judge demo script.
- [x] **TSK-012:** Author Root `README.md` and verify `docs/STAGE_STATUS.md`.  
  *Role:* Lead Maintainer | *Est:* 1h | *Deps:* TSK-011  
  *Acceptance:* Complete overview, setup instructions, scripts, and Stage 0 exit gate passed.

---

## Stage 1: Scaffold & Code-Quality Baseline

- [ ] **TSK-101:** Initialize Git repository and configure `.gitignore` for Python & Netlify.  
  *Role:* DevOps Lead | *Est:* 1h | *Deps:* TSK-012  
  *Acceptance:* Git initialized, virtual environments and secrets ignored.
- [ ] **TSK-102:** Set up Python virtual environment and `requirements.txt`.  
  *Role:* Backend Lead | *Est:* 1h | *Deps:* TSK-101  
  *Acceptance:* FastAPI, Uvicorn, Pydantic v2, Google GenAI SDK installed.
- [ ] **TSK-103:** Create FastAPI application factory (`src/main.py`) and single-command runner (`run.py`).  
  *Role:* Backend Lead | *Est:* 2h | *Deps:* TSK-102  
  *Acceptance:* `python run.py` launches Uvicorn server and serves health endpoint.
- [ ] **TSK-104:** Create Netlify serverless entrypoint (`netlify/functions/api.py`) and `netlify.toml`.  
  *Role:* DevOps Lead | *Est:* 2h | *Deps:* TSK-103  
  *Acceptance:* Mangum wrapper configured with build and redirect rules.
- [ ] **TSK-105:** Configure pytest suite (`tests/conftest.py`) and write initial passing test.  
  *Role:* QA Engineer | *Est:* 1h | *Deps:* TSK-103  
  *Acceptance:* `pytest` runs and passes with zero errors.

---

## Stage 2: Google Services & Security Foundation

- [ ] **TSK-201:** Implement Google GenAI Python service with structured outputs & repair logic (`src/services/gemini_service.py`).  
  *Role:* AI Engineer | *Est:* 3h | *Deps:* TSK-103  
  *Acceptance:* Uses official SDK, validates against Pydantic model, handles retries.
- [ ] **TSK-202:** Implement sliding-window rate limiter & security headers middleware.  
  *Role:* Security Engineer | *Est:* 2h | *Deps:* TSK-103  
  *Acceptance:* Throttles excessive calls, sets CSP and nosniff headers.
- [ ] **TSK-203:** Implement prompt injection sanitization utility (`src/utils/sanitizer.py`).  
  *Role:* Security Engineer | *Est:* 1h | *Deps:* TSK-201  
  *Acceptance:* Strips system override tokens, tested with adversarial inputs.
- [ ] **TSK-204:** Implement persistent storage service with local JSON/SQLite and Firestore adapter.  
  *Role:* Backend Lead | *Est:* 2h | *Deps:* TSK-103  
  *Acceptance:* CRUD operations for celebrations and sub-entities with user isolation.

---

## Stage 3: Core Features (The Four Pillars)

- [ ] **TSK-301:** Implement Onboarding Wizard & Master Plan Generator endpoint (`POST /api/ai/plan`).  
  *Role:* Full-Stack | *Est:* 3h | *Deps:* TSK-201  
  *Acceptance:* Generates complete celebration master plan with fallback on 429 quota exhaustion.
- [ ] **TSK-302:** Implement Dynamic Budget Planner & Live AI Re-balancing (`POST /api/ai/rebalance-budget`).  
  *Role:* Full-Stack | *Est:* 3h | *Deps:* TSK-301  
  *Acceptance:* Category split, paid vs. pending tracking, over-budget warnings, AI re-balance.
- [ ] **TSK-303:** Implement Phased Countdown Timeline & Google Calendar Export (`GET /api/export/calendar`).  
  *Role:* Full-Stack | *Est:* 3h | *Deps:* TSK-301  
  *Acceptance:* 5 chronological phases, task status toggle, download `.ics` and deep-link to Google Calendar.
- [ ] **TSK-304:** Implement Categorized Vendor Checklist & Quote Management.  
  *Role:* Full-Stack | *Est:* 2h | *Deps:* TSK-301  
  *Acceptance:* Tracks status, quote amount, notes, and local estimates.
- [ ] **TSK-305:** Implement Personalized Ideas Hub across 6 cultural dimensions.  
  *Role:* Full-Stack | *Est:* 2h | *Deps:* TSK-301  
  *Acceptance:* Curated themes, decor, regional menu, sacred rituals, games, return gifts.
- [ ] **TSK-306:** Implement Auspicious Muhurat Helper & Date Guidance.  
  *Role:* Full-Stack | *Est:* 1h | *Deps:* TSK-301  
  *Acceptance:* Displays seasonal windows with mandatory astrology disclaimer.
- [ ] **TSK-307:** Build Curated Seed Datasets for Weddings, Birthdays, and Community Melas.  
  *Role:* Full-Stack | *Est:* 2h | *Deps:* TSK-301  
  *Acceptance:* Demo mode instantly loads all 3 celebrations with rich details.

---

## Stage 4: Premium UI, Cultural Design & Personalization

- [ ] **TSK-401:** Assemble modern responsive web UI shell (`public/index.html`, `public/css/styles.css`).  
  *Role:* UI Designer | *Est:* 3h | *Deps:* TSK-307  
  *Acceptance:* Warm ivory and twilight indigo palettes, Noto Serif Devanagari typography.
- [ ] **TSK-402:** Integrate cultural SVG motifs (Mandala, Diya, Kalash, Torana).  
  *Role:* UI Designer | *Est:* 2h | *Deps:* TSK-401  
  *Acceptance:* Subtle mandala backdrops, pulsating diya loader during AI thought.
- [ ] **TSK-403:** Implement Personalization Engine (Time-of-day Sanskrit greeting, personal blessing note).  
  *Role:* Frontend Lead | *Est:* 2h | *Deps:* TSK-401  
  *Acceptance:* Greets user by name & time of day, includes family blessing note in exports.
- [ ] **TSK-404:** Implement fluid micro-interactions, budget number tickers, and confetti bursts.  
  *Role:* Frontend Lead | *Est:* 2h | *Deps:* TSK-401  
  *Acceptance:* Spring transitions, budget ticker animation, celebratory confetti on task check.

---

## Stage 5: Accessibility (WCAG 2.2 AA)

- [ ] **TSK-501:** Implement semantic landmarks, keyboard focus management, and skip navigation.  
  *Role:* A11y Specialist | *Est:* 2h | *Deps:* TSK-401  
  *Acceptance:* Full keyboard accessibility, visible focus indicators, skip-to-content link.
- [ ] **TSK-502:** Configure ARIA live regions for streaming AI updates and toast notifications.  
  *Role:* A11y Specialist | *Est:* 1h | *Deps:* TSK-501  
  *Acceptance:* Screen-readers announce AI status and task updates smoothly.
- [ ] **TSK-503:** Enforce color contrast (≥ 4.5:1 text, ≥ 3:1 UI) and reduced-motion overrides.  
  *Role:* A11y Specialist | *Est:* 1h | *Deps:* TSK-501  
  *Acceptance:* Verified in light and dark themes; `@media (prefers-reduced-motion)` respected.

---

## Stage 6: Testing Depth & Resilience

- [ ] **TSK-601:** Implement Unit & Pydantic Schema Validation Tests (`tests/test_schemas.py`).  
  *Role:* QA Engineer | *Est:* 2h | *Deps:* TSK-307  
  *Acceptance:* Validates required fields, budget bounds, date constraints.
- [ ] **TSK-602:** Implement Budget Math & Re-balancing Tests (`tests/test_budget_math.py`).  
  *Role:* QA Engineer | *Est:* 2h | *Deps:* TSK-302  
  *Acceptance:* Confirms total variance, percentage split, and payment statuses.
- [ ] **TSK-603:** Implement Edge-Case Test Suite (`tests/test_edge_cases.py`).  
  *Role:* QA Engineer | *Est:* 2h | *Deps:* TSK-601  
  *Acceptance:* Tests empty input, negative budget, Devanagari text, huge guest counts.
- [ ] **TSK-604:** Implement Loop Safety & Max-Iteration Cap Tests (`tests/test_loop_safety.py`).  
  *Role:* Security Engineer | *Est:* 2h | *Deps:* TSK-201  
  *Acceptance:* Proves AI repair loop terminates at 1 retry and enforces 12s timeout.

---

## Stage 7: Efficiency & Performance

- [ ] **TSK-701:** Optimize static assets, font preloading, and caching headers in `netlify.toml`.  
  *Role:* DevOps Lead | *Est:* 1h | *Deps:* TSK-401  
  *Acceptance:* Fast font loading, gzip compression, sub-second TTFT on cached responses.
- [ ] **TSK-702:** Implement in-memory AI plan response cache keyed by normalized brief.  
  *Role:* Backend Lead | *Est:* 1h | *Deps:* TSK-301  
  *Acceptance:* Instantaneous responses for repeated celebration briefs.

---

## Stage 8: Final Audit, GitHub Sync & Netlify Deployment

- [ ] **TSK-801:** Conduct full self-assessment audit against PromptWars criteria in `docs/STAGE_STATUS.md`.  
  *Role:* Staff PM | *Est:* 2h | *Deps:* All previous tasks  
  *Acceptance:* All 6 evaluation criteria scored with concrete file and test evidence.
- [ ] **TSK-802:** Commit all files to Git and push to remote GitHub repository.  
  *Role:* DevOps Lead | *Est:* 1h | *Deps:* TSK-801  
  *Acceptance:* Repository created, all stages committed, pushed to GitHub.
- [ ] **TSK-803:** Deploy and verify live application on Netlify.  
  *Role:* DevOps Lead | *Est:* 1h | *Deps:* TSK-802  
  *Acceptance:* Production URL live on Netlify, recorded in `README.md`.
