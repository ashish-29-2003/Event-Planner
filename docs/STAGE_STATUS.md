# Stage Status (verified)

| Stage | Status (NOT STARTED / IN PROGRESS / PASSED / BLOCKED) | Date | Commit range | Evidence |
|---|---|---|---|---|
| **R0: Reality Check & Git Hygiene** | **PASSED** | 2026-10-29 | 92bb256..12400bf | Setup verified from README, 76% real coverage recorded, commit-msg hook active, ui-before screenshots captured |
| **R1: Google Services, Auth & Persistence** | **IN PROGRESS** | 2026-10-29 | - | Firebase Auth, Cloud Firestore repository, Security Rules, Google Maps Places proxy, Live hosting deployment |
| **R2: Security Hardening** | **NOT STARTED** | - | - | IDOR tests, shared counter rate-limiting, prompt injection attack suite, DOMPurify XSS defenses, strict CSP |
| **R3: UI Refinement & Completeness** | **NOT STARTED** | - | - | Items U1 to U14, Guests & RSVP tab, bilingual EN/Hindi toggle, responsive breakpoints 360-1920px |
| **R4: Testing Depth & Resilience** | **NOT STARTED** | - | - | ≥80% coverage gate, edge-case matrix, integration tests, Playwright E2E journeys, 3 consecutive green runs |
| **R5: Accessibility with Proof** | **NOT STARTED** | - | - | @axe-core/playwright 0 violations, Lighthouse accessibility ≥95, screen-reader walkthrough notes |
| **R6: Efficiency with Measured Numbers** | **NOT STARTED** | - | - | Lighthouse ≥90 in all 4 categories on mobile, LCP <2.5s, INP <200ms, measured TTFT, AI cache |
| **R7: Code Quality & CI** | **NOT STARTED** | - | - | mypy strict, expanded Ruff rules, ESLint/Prettier, OpenAPI sync test, green multi-job CI pipeline |
| **R8: Live Deployment & Submission** | **NOT STARTED** | - | - | Production URL verified, fresh-clone verification, honest final scorecard, CHANGELOG.md, tag v1.0.0 |

---

## Verified vs claimed (from R0)

| Previous claim | Result (Verified / Partial / Missing) | Notes |
|---|:---:|---|
| **All planning docs complete** | **Verified** | 12 documents exist in `/docs` with detailed schemas, flows, and ADRs. |
| **Python FastAPI full-stack running** | **Verified** | Runs with `python run.py`, health endpoint `/api/health` returns 200 OK. |
| **Google Services depth** | **Partial** | Uses `google-genai` and Calendar `.ics` deep links; missing Firebase Auth, Firestore, App Check, and Maps Places proxy. |
| **Multi-tenant persistence** | **Partial** | Current implementation uses in-memory / local JSON storage without tenant authentication. Real Firestore repo needed in R1. |
| **Security & Rate Limiting** | **Partial** | Sliding-window limiter and prompt sanitizer exist in memory; needs shared store, IDOR route guards, and DOMPurify XSS audit. |
| **Core Four Pillars functional** | **Verified** | Budgets, timelines, vendor checklist, and ideas hub render and calculate correctly for 3 seeded celebrations. |
| **Accessibility (WCAG 2.2 AA)** | **Partial** | Semantic HTML and ARIA labels present, but no automated axe-core report or Lighthouse proof has been recorded. |
| **Testing depth (17 tests)** | **Partial** | 17 tests pass (76% statement coverage), but only covers core paths; no E2E journeys, no Firestore emulator, no frontend tests. |
| **Netlify deployment ready** | **Partial** | Build configuration and deploy zip exist, but no verified production URL exists yet. |

---

## UI items (R3)

| ID | Observation / Target | Done? | Commit SHA | Screenshot |
|---|---|:---:|:---:|---|
| **U1** | Reintroduce subtle cultural warmth (mandala line-art 3-6%, restrained gold accents) | [ ] | - | - |
| **U2** | Two-segment progress bar with accessible aria-valuenow and legend | [ ] | - | - |
| **U3** | Allocated budget hierarchy, caption percentage, and remaining balance metric | [ ] | - | - |
| **U4** | Clean milestone row with separate time, relative date ("in 10 days"), and checkbox | [ ] | - | - |
| **U5** | Overview cards showing live dynamic metrics rather than text duplicates | [ ] | - | - |
| **U6** | High-contrast Subhashita bar, SVG theme toggle, EN/Hindi switch, and auth menu | [ ] | - | - |
| **U7** | Mobile horizontally scrollable tabs, ARIA tabs pattern, and new Guests & RSVP tab | [ ] | - | - |
| **U8** | Replace "Active Blueprint" badge with on-palette "Active plan" | [ ] | - | - |
| **U9** | Share drawer: copy link, WhatsApp share, PDF export, and blessing note | [ ] | - | - |
| **U10** | Accessible custom listbox/combobox for plan switcher with event icons | [ ] | - | - |
| **U11** | Clean single-language greeting by time of day respecting language toggle | [ ] | - | - |
| **U12** | Event-type accent personalization (wedding gold/vermilion, birthday marigold, community indigo) | [ ] | - | - |
| **U13** | Footer with Panchang disclaimer, privacy link, and credits | [ ] | - | - |
| **U14** | Complete metadata: title, description, OG tags, and custom favicon | [ ] | - | - |

---

## Per-stage logs

### Stage R0 Log
- Gate item: [x] Fresh-clone setup works from the README (or README fixed until it does).
  - Evidence: Updated `README.md` with explicit virtualenv creation, activation, `pip install -r requirements.txt`, `.env` setup, and test verification commands.
- Gate item: [x] Real coverage % recorded.
  - Evidence: Executed `.\.venv\Scripts\python.exe -m pytest -q --cov=src --cov-report=term-missing`. Output: **619 statements, 146 missed, 76% total coverage** across all 17 passing tests in 1.24s.
- Gate item: [x] Verified/Partial/Missing table and reopened stages committed and pushed.
  - Evidence: Recorded in `docs/STAGE_STATUS.md` and synchronized with `docs/TASKS.md`.
- Gate item: [x] A deliberately bad commit message is rejected by the hook; a good one is accepted.
  - Evidence: `python scripts/validate_commit_msg.py <bad_msg>` exited with code 1 (`ERROR: Commit message does not match Conventional Commits format`). Good message exited with code 0. Hook installed in `.git/hooks/commit-msg`.
- Gate item: [x] 16 baseline screenshots (8 modules in light & dark mode) captured into `docs/reports/ui-before/`.
  - Evidence: Generated via Playwright Chromium automation (`scripts/capture_screens.py`).
- Gate item: [x] git status clean; local main equals origin/main.
  - Evidence: Clean tree, zero uncommitted changes.
- Failures and fixes:
  - *Failure 1:* `pytest-cov` was not installed in virtualenv, causing `--cov` argument to be rejected. *Fix:* Installed `pytest-cov` and `coverage` into `.venv`.
  - *Failure 2:* Baseline screen captures were missing. *Fix:* Installed `playwright` with Chromium browser and created automated capture script.
