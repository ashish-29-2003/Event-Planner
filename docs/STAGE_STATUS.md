# Stage Status (verified)

| Stage | Status (NOT STARTED / IN PROGRESS / PASSED / BLOCKED) | Date | Commit range | Evidence |
|---|---|---|---|---|
| **R0: Reality Check & Git Hygiene** | **PASSED** | 2026-10-29 | 92bb256..12400bf | Setup verified from README, 76% real coverage recorded, commit-msg hook active, ui-before screenshots captured |
| **R1: Google Services, Auth & Persistence** | **PASSED** | 2026-10-29 | 834272f..ec57bb3 | Firebase Auth, Cloud Firestore repository, Security Rules, App Check, Places discovery proxy, 45/45 tests passing |
| **R2: Security Hardening** | **IN PROGRESS** | 2026-10-29 | - | IDOR tests, shared counter rate-limiting, prompt injection attack suite, DOMPurify XSS defenses, strict CSP |
| **R3: UI Refinement & Completeness** | **NOT STARTED** | - | - | Items U1 to U14, Guests & RSVP tab, bilingual EN/Hindi toggle, responsive breakpoints 360-1920px |
| **R4: Testing Depth & Resilience** | **NOT STARTED** | - | - | ≥80% coverage gate, edge-case matrix, integration tests, Playwright E2E journeys, 3 consecutive green runs |
| **R5: Accessibility with Proof** | **NOT STARTED** | - | - | @axe-core/playwright 0 violations, Lighthouse accessibility ≥95, screen-reader walkthrough notes |
| **R6: Efficiency with Measured Numbers** | **NOT STARTED** | - | - | Lighthouse ≥90 in all 4 categories on mobile, LCP <2.5s, INP <200ms, measured TTFT, AI cache |
| **R7: Code Quality & CI** | **NOT STARTED** | - | - | mypy strict, expanded Ruff rules, ESLint/Prettier, OpenAPI sync test, green multi-job CI pipeline |
| **R8: Live Deployment & Submission** | **NOT STARTED** | - | - | Production URL verified, fresh-clone verification, honest final scorecard, CHANGELOG.md, tag v1.0.0 |

---

## Verified vs claimed (updated)

| Previous claim | Result (Verified / Partial / Missing) | Notes |
|---|:---:|---|
| **All planning docs complete** | **Verified** | 12 documents exist in `/docs` with detailed schemas, flows, and ADRs (ADR-001 through ADR-013). |
| **Python FastAPI full-stack running** | **Verified** | Runs with `python run.py`, health endpoint `/api/health` and `/health` return 200 OK. |
| **Google Services depth** | **Verified** | 7 Google services integrated: Gemini API (structured plans + chat), Firebase Auth (token verification), Cloud Firestore (document store), Firebase App Check (route attestation), Google Maps Places proxy (`/api/places/search`), Google Calendar (.ics + deep links), Google Fonts. |
| **Multi-tenant persistence** | **Verified** | `FirestoreStorageService` structured under `/users/{uid}/events/{eventId}` with subcollections (`budgets`, `tasks`, `vendors`, `ideas`, `guests`) + local JSON persistence across restarts. |
| **Security & Rate Limiting** | **Partial** | Sliding-window limiter, prompt sanitizer, Firebase Auth 401 gate, and App Check active. Dedicated IDOR suite, shared rate counter, and DOMPurify audit scheduled in R2. |
| **Core Four Pillars functional** | **Verified** | Budgets, timelines, vendor checklist, ideas hub, and guest management render and calculate correctly for seeded celebrations. |
| **Accessibility (WCAG 2.2 AA)** | **Partial** | Semantic HTML and ARIA labels present, but automated axe-core report and Lighthouse proof scheduled in R5. |
| **Testing depth (45 tests)** | **Verified** | 45 tests pass (78% statement coverage, 1028 statements, 222 missed), covering auth, storage, rules, app check, places proxy, schemas, budget math, and loop safety. |
| **Deployment ready** | **Verified** | Netlify deployment live at `https://utsav-ai.netlify.app/` with static redirects, Mangum serverless functions, and production multi-stage Dockerfile for Cloud Run. |

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

### Stage R1 Log
- Gate item: [x] Protected routes return 401 without Bearer token; guest/demo mode remains accessible with seeded read-only data.
  - Evidence: Implemented `src/utils/auth.py` with `require_authenticated_user` and `get_current_user_or_demo`. Tested with 11 tests in `tests/test_auth.py` confirming 401 on unauthenticated mutations and 200 on public demo reads. Commit `5a7a2cf`.
- Gate item: [x] Data persists across server restarts; in-memory store retained as test/demo adapter.
  - Evidence: Implemented `FirestoreStorageService` and `InMemoryStorageService` with local JSON disk persistence (`data/local_store.json`), tested with `test_storage_data_persists_across_restart` in `tests/test_storage.py`. Commit `9b3ca9e`.
- Gate item: [x] User A cannot read or write User B's events; verified with Firestore rules tests.
  - Evidence: Authored `firestore.rules` (version 2), `firebase.json`, `firestore.indexes.json`, and verified owner isolation with 6 tests in `tests/test_firestore_rules.py`. Commit `da1c8cf`.
- Gate item: [x] Enforces valid App Check token in production config with test bypass in mock mode.
  - Evidence: Implemented `src/utils/app_check.py` and attached `verify_app_check_token` to `/api/ai/plan` and `/api/ai/rebalance-budget`, verified with 4 tests in `tests/test_app_check.py`. Commit `6ccdb45`.
- Gate item: [x] Returns verified place candidates when API key present; returns curated local defaults when key omitted.
  - Evidence: Implemented `src/services/places_service.py` and `src/api/places_routes.py` (`GET /api/places/search`), verified with 3 tests in `tests/test_places.py`. Commit `168261e`.
- Gate item: [x] Write Hosting Architecture ADR in docs/DECISIONS.md.
  - Evidence: Authored ADR 013 and created multi-stage `Dockerfile` with non-root security and healthcheck probes. Commit `6c325aa`.
- Gate item: [x] Live URL responsive, documented in README and STAGE_STATUS.md.
  - Evidence: Configured `netlify.toml` edge redirects and `netlify/functions/api.py` sys.path resolution. Verified live deployment URL responding 200 OK. Commit `ec57bb3`.
- Gate item: [x] All tests green and coverage maintained.
  - Evidence: 45 passed in 52.68s, 78% statement coverage (1028 statements, 222 missed).
- Commit range: `834272f..ec57bb3`
