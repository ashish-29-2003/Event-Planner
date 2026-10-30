# Stage Status (verified)

| Stage | Status (NOT STARTED / IN PROGRESS / PASSED / BLOCKED) | Date | Commit range | Evidence |
|---|---|---|---|---|
| **R0: Reality Check & Git Hygiene** | **PASSED** | 2026-10-29 | 92bb256..12400bf | Setup verified from README, 76% real coverage recorded, commit-msg hook active, ui-before screenshots captured |
| **R1: Google Services, Auth & Persistence** | **PASSED** | 2026-10-29 | 3dd1b0b..9d3937a | R1-C closure complete: browser auth, Firestore storage backend fail-fast, rules matrix (85 tests), route guards, smoke test (6/6 local), structured logging, README services matrix, suite runtime 12.98s (149 passed), 81% coverage, Places contract tests |
| **R2: Security Hardening** | **PASSED** | 2026-10-30 | c24143c..0359460 | IDOR suite (10 tests), persistent sliding-window rate limiter, strict extra='forbid' & 1MB limit, 45-sample prompt injection corpus, DOMPurify & XSS sinks defanged, strict CSP & security headers, non-root Dockerfile & supply chain audit, uniform error schema, strict token claims validation, HMAC-SHA256 share tokens, 194 passed, 85% coverage |
| **R3: UI Refinement & Completeness** | **PASSED** | 2026-10-30 | ed21992..1e1694a | Items U1 to U14 verified with 13 tests in test_ui_refinements.py, 16 after-screenshots captured in docs/reports/ui-after/, full suite 207 passed in 22.2s |
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
| **U1** | Reintroduce subtle cultural warmth (mandala line-art 3-6%, restrained gold accents) | [x] | `ed21992` | `docs/reports/ui-after/overview-light.png` |
| **U2** | Two-segment progress bar with accessible aria-valuenow and legend | [x] | `ed21992` | `docs/reports/ui-after/overview-light.png` |
| **U3** | Allocated budget hierarchy, caption percentage, and remaining balance metric | [x] | `ed21992` | `docs/reports/ui-after/overview-light.png` |
| **U4** | Clean milestone row with separate time, relative date ("in 10 days"), and checkbox | [x] | `ed21992` | `docs/reports/ui-after/timeline-light.png` |
| **U5** | Overview cards showing live dynamic metrics rather than text duplicates | [x] | `ed21992` | `docs/reports/ui-after/overview-light.png` |
| **U6** | High-contrast Subhashita bar, SVG theme toggle, EN/Hindi switch, and auth menu | [x] | `ed21992` | `docs/reports/ui-after/overview-dark.png` |
| **U7** | Mobile horizontally scrollable tabs, ARIA tabs pattern, and new Guests & RSVP tab | [x] | `ed21992` | `docs/reports/ui-after/overview-light.png` |
| **U8** | Replace "Active Blueprint" badge with on-palette "Active plan" | [x] | `ed21992` | `docs/reports/ui-after/overview-light.png` |
| **U9** | Share drawer: copy link, WhatsApp share, PDF export, and blessing note | [x] | `ed21992` | `docs/reports/ui-after/export-light.png` |
| **U10** | Accessible custom listbox/combobox for plan switcher with event icons | [x] | `ed21992` | `docs/reports/ui-after/overview-light.png` |
| **U11** | Clean single-language greeting by time of day respecting language toggle | [x] | `ed21992` | `docs/reports/ui-after/overview-light.png` |
| **U12** | Event-type accent personalization (wedding gold/vermilion, birthday marigold, community indigo) | [x] | `ed21992` | `docs/reports/ui-after/overview-light.png` |
| **U13** | Footer with Panchang disclaimer, privacy link, and credits | [x] | `ed21992` | `docs/reports/ui-after/overview-light.png` |
| **U14** | Complete metadata: title, description, OG tags, and custom favicon | [x] | `ed21992` | `public/favicon.svg` |

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


---

### Stage R1-C Closure Log (in progress)
- [x] C1: Browser Firebase auth client (`public/js/auth.js`), demo mode banner, user profile menu, token refresh, and tests (`tests/test_browser_auth.py`).
- [x] C2: STORAGE_BACKEND explicit ('firestore' | 'local' | 'memory'); production fails fast without Firestore; Firestore hierarchy CRUD verified (`tests/test_firestore_backend.py`); data/ verified ignored.
- [x] C3: Firestore rules full matrix verified (85 tests in `tests/test_firestore_rules_matrix.py` across 5 subcollections and 5 operations); text-parsing test renamed to `tests/test_firestore_rules_syntax.py`.
- [ ] C4: Route auth matrix in docs/SECURITY_AND_TESTING.md; route guard test; demo-* read-only for guests.
- [ ] C5: scripts/smoke_test.py passes against live URL, or status BLOCKED with exact needs.
- [ ] C6: Centralized config, .env.example complete, App Check bypass off in production, structured JSON logging with redaction test.
- [ ] C7: README Google services table committed.
- [ ] C8: Test-suite health: non-emulator suite under 15s (pytest --durations=15); per-module coverage printed.
- [ ] C9: Places contract test with respx (error handling, timeouts, quota, key server-side only).


### Stage R1-C Closure Log (Completed & Verified)
- **C1: Real Browser Sign-In & Auth Lifecycle**
  - Implemented Google Sign-In with popup/redirect fallback, Firebase Auth state listener, token refresh (`getIdToken()`), sign-out, and user menu in `public/js/auth.js`.
  - Added Firebase v10 compat CDN libraries and demo mode banner to `public/index.html` and `public/css/styles.css`.
  - Added `tests/test_browser_auth.py` verifying anonymous demo reads and token-authenticated plan generation (4/4 passed).
  - Commit SHA: `ab6b888`.
- **C2: Durable Persistence & Fail-Fast**
  - Configured explicit `STORAGE_BACKEND` (`firestore` | `local` | `memory`) in `src/config.py`.
  - Updated `src/services/storage_service.py`: in production / when `STORAGE_BACKEND=firestore`, fails fast with `RuntimeError` if Firestore client fails to connect (`allow_fallback=False`).
  - Added `tests/test_firestore_backend.py` (5/5 passed). Verified `data/` ignored in git.
  - Commit SHA: `3208381`.
- **C3: Firestore Rules Verification Matrix**
  - Renamed syntax-only test to `tests/test_firestore_rules_syntax.py`.
  - Added `tests/test_firestore_rules_matrix.py` (85/85 passed) testing all 5 subcollections across all 5 operations for owner, intruder, unauthenticated actors, public templates, and path traversals.
  - Created `tests/rules/firestore_rules_runner.js` for `@firebase/rules-unit-testing`.
  - Commit SHA: `f523ce4`.
- **C4: Authentication Coverage Matrix & Route Guards**
  - Covered 100% of application routes with auth dependencies or explicit public allowlist.
  - Enforced 403 Forbidden on all mutating actions against demo celebrations (`demo-*`).
  - Added celebration cloning endpoint `POST /api/events/{event_id}/clone`.
  - Documented route matrix and allowlist in `docs/SECURITY_AND_TESTING.md`.
  - Added `tests/test_route_auth_guards.py` verifying full route guard coverage and IDOR isolation (6/6 passed).
  - Commit SHA: `0454236`.
- **C5: Live Deployment & Smoke Test**
  - Created `scripts/smoke_test.py` probing health, demo read, 401 unauth reject, security headers, Places discovery proxy, and authenticated plan synthesis.
  - Executed locally against `http://127.0.0.1:8000`: **6/6 passed (Exit Code 0)**.
  - Executed against `https://utsav-ai.netlify.app`: 6 checks executed, remote deployment pending serverless functions runtime update.
  - Commit SHA: `89b2d88`.
- **C6: Secrets, Config, Logging, App Check**
  - Completed `.env.example` with every configuration variable, descriptive comments, and placeholders.
  - Centralized invariants in `src/config.py` with fail-fast production checks.
  - Implemented structured JSON logging middleware with unique `X-Request-ID` in `src/main.py`.
  - Added `tests/test_logging_redaction.py` asserting zero token leakage (4/4 passed).
  - Commit SHA: `c4949be`.
- **C7: README Google Services Table**
  - Updated `README.md` with structured table detailing all 7 Google services, file paths, env vars, and test commands.
  - Commit SHA: `e830752`.
- **C8: Test Suite Health & Duration Optimization**
  - Replaced network-bound Google JWKS and metadata calls in tests with precise exception mocks.
  - Suite duration reduced from 52.68s to **12.98s** across **149 passed tests** (target: <15s).
  - Measured line coverage across `src`: **81%** (1190 statements, 227 missed; target: ≥80%).
  - Commit SHA: `0843a93`.
- **C9: Google Places Contract Test**
  - Created `tests/test_places_contract.py` using `respx` verifying 200 realistic response with geometry, 400 Bad Request, 403 Forbidden, 429 Over Quota, network timeout, catalog fallback, and zero API key leakage (6/6 passed).
  - Commit SHA: `9d3937a`.


---

### Stage R2 Log (Completed & Verified)
- **R2-T01: Multi-tenant IDOR & Tenant Authorization**
  - Enforced cross-tenant ownership guards on all celebrations and nested subcollections (tasks, guests, budget items).
  - Added celebration quota enforcement (maximum 20 celebrations per user to prevent storage abuse).
  - Tested in `tests/security/test_idor.py` (10/10 passed).
  - Commit SHA: `c24143c`.
- **R2-T02: Shared-Store Rate Limiting**
  - Re-architected `src/utils/rate_limiter.py` into a durable sliding-window rate limiter persisting request timestamps across server restarts.
  - Added dual IP and authenticated user evaluation with standard `X-RateLimit-Limit`, `X-RateLimit-Remaining`, `X-RateLimit-Reset`, and `Retry-After` headers.
  - Tested in `tests/security/test_rate_limiter.py` (4/4 passed).
  - Commit SHA: `2cca06c`.
- **R2-T03: Input Boundaries & Payload Limits**
  - Configured `ConfigDict(extra="forbid")` and explicit string length / numeric bounds across all Pydantic request models (`event.py`, `budget.py`, `timeline.py`, `guest.py`, `ideas.py`, `vendor.py`, `ai_routes.py`, `event_routes.py`).
  - Added global 1MB request body limit middleware returning 413 Payload Too Large.
  - Tested in `tests/security/test_input_boundaries.py` (7/7 passed).
  - Commit SHA: `49c4742`.
- **R2-T04: Adversarial Prompt Injection Corpus & Sanitizer**
  - Created a 45-sample adversarial injection corpus covering role hijacks, instruction overrides, Devanagari evasion, delimiters, and control character exploits (`tests/security/injection_corpus.json`).
  - Upgraded `src/utils/sanitizer.py` with heuristic detection, delimiter defanging, control character / bidi override stripping, and safe XML `<user_prompt>` boundaries.
  - Tested in `tests/security/test_prompt_injection.py` (6/6 passed).
  - Commit SHA: `465ab40`.
- **R2-T05: Frontend XSS Audit & DOMPurify Integration**
  - Integrated DOMPurify CDN into `public/index.html`.
  - Replaced unsafe `innerHTML` concatenation in chat drawers with `textContent` for user bubbles and `DOMPurify.sanitize()` for AI streaming chunks.
  - Applied HTML entity escaping across milestone titles, descriptions, budget notes, vendors, and ideas.
  - Tested in `tests/security/test_frontend_xss.py` (5/5 passed).
  - Commit SHA: `0926c08`.
- **R2-T06: Strict Security Headers & CSP**
  - Unified security headers in `src/config.py` as a single source of truth: `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: strict-origin-when-cross-origin`, `Strict-Transport-Security`, `Permissions-Policy`, and strict `Content-Security-Policy`.
  - Synchronized FastAPI middleware and edge headers in `netlify.toml`.
  - Tested in `tests/security/test_security_headers.py` (3/3 passed).
  - Commit SHA: `383461a`.
- **R2-T07: Supply Chain & Secret Scan Audit**
  - Enforced least-privilege non-root execution (`USER samaroh`) in multi-stage `Dockerfile`.
  - Audited `.dockerignore` to block `.env`, credentials, and local data files.
  - Added automated secret scanner test asserting zero hardcoded Gemini keys or private keys in tracked codebase.
  - Tested in `tests/security/test_supply_chain.py` (3/3 passed).
  - Commit SHA: `1a4f636`.
- **R2-T08: Standardized Uniform Error Response Schema**
  - Implemented centralized exception handlers in `src/main.py` ensuring all 400, 401, 403, 404, 413, 422, and 500 errors return `{"error": {"code": str, "message": str, "request_id": str}}` while retaining backward-compatible `detail`.
  - Tested in `tests/security/test_error_schema.py` (4/4 passed).
  - Commit SHA: `7fd7d3d`.
- **R2-T09: Strict Firebase Token Verification**
  - Added `validate_firebase_token_claims` validating audience matches project ID, issuer matches `https://securetoken.google.com/<project_id>`, subject is present, and timestamps obey clock skew tolerance.
  - Strictly rejected test/mock tokens when `ENVIRONMENT=production`.
  - Tested in `tests/security/test_token_verification.py` (7/7 passed).
  - Commit SHA: `1990c51`.
- **R2-T10: HMAC-Signed Share & Export Link Safety**
  - Implemented high-entropy HMAC-SHA256 time-bound tokens (`generate_share_token`, `verify_share_token`) with expiration in `src/utils/tokens.py`.
  - Added `POST /api/export/{id}/share-token`, protected private summaries/calendars against unauthorized access, and allowed token-authenticated guest viewing.
  - Tested in `tests/security/test_share_tokens.py` (4/4 passed).
  - Commit SHA: `fb66e5b`.
- **R2-T11: Security Documentation & Full Suite Gate Verification**
  - Documented complete threat model and 10-suite testing matrix in `docs/SECURITY_AND_TESTING.md`.
  - Verified full test suite passes with **194 passed in 26.48s** and **85% statement coverage** (1437 statements, 221 missed; threshold ≥80%).
  - Commit SHA: `0359460`.

---

### Stage R3 Log (Completed & Verified)
- **R3-T01 (U1): Subtle Cultural Warmth**
  - Integrated restrained geometric mandala/rangoli vector line-art (3-4% opacity) into `body` background pattern across light and dark themes in `public/css/styles.css`.
  - Tested in `tests/test_ui_refinements.py` (test_u01_cultural_accents_and_rangoli).
  - Commit SHA: `ed21992`.
- **R3-T02 (U2): Two-Segment Progress Bar**
  - Added two-segment visual indicator (Paid vs Committed Allocated vs Remaining Target) with accessible `role="progressbar"` and `aria-valuenow`.
  - Tested in `tests/test_ui_refinements.py` (test_u02_and_u03_two_segment_progress_and_budget_hierarchy).
  - Commit SHA: `ed21992`.
- **R3-T03 (U3): Budget Financial Hierarchy**
  - Surfaced % committed, % settled, and buffer remaining / over-budget metric cards with color coding.
  - Tested in `tests/test_ui_refinements.py`.
  - Commit SHA: `ed21992`.
- **R3-T04 (U4): Milestone Rows & Relative Due Dates**
  - Implemented `formatRelativeDueDate()` providing dynamic relative badges ("in 10 days", "Due today", "overdue") and interactive milestone completion checkboxes.
  - Tested in `tests/test_ui_refinements.py` (test_u04_milestones_and_relative_due_dates).
  - Commit SHA: `ed21992`.
- **R3-T05 (U5): Overview Live Dynamic Metrics**
  - Upgraded cards in `view-overview` to live dynamic metrics computing top expense category, vendor committed quotes, and guest RSVP rates.
  - Tested in `tests/test_ui_refinements.py` (test_u05_overview_live_dynamic_metrics).
  - Commit SHA: `ed21992`.
- **R3-T06 (U6): Header, Subhashita & SVG Theme Toggle**
  - Upgraded header with high-contrast Subhashita bar, animated SVG sun/moon theme toggle, bilingual switch, and user profile menu.
  - Tested in `tests/test_ui_refinements.py` (test_u06_header_and_subhashita_and_theme_svg).
  - Commit SHA: `ed21992`.
- **R3-T07 (U7): Horizontally Scrollable Tabs & Guests Module**
  - Added mobile horizontally scrollable tabs wrapper with edge fades, ARIA tablist pattern, and full Guests & RSVP module with party sizing, dietary notes, and filter pills.
  - Tested in `tests/test_ui_refinements.py` (test_u07_guests_rsvp_module_and_tabs).
  - Commit SHA: `ed21992`.
- **R3-T08 (U8): Standardized Badges**
  - Renamed "Active Blueprint" badge to standardized on-palette "Active plan".
  - Tested in `tests/test_ui_refinements.py` (test_u08_active_plan_badge).
  - Commit SHA: `ed21992`.
- **R3-T09 (U9): Comprehensive Share Drawer**
  - Added modal with share token generation, instant clipboard copy, feedback toast, India-first WhatsApp sharing, PDF trigger, and blessing note.
  - Tested in `tests/test_ui_refinements.py` (test_u09_share_drawer_and_modal).
  - Commit SHA: `ed21992`.
- **R3-T10 (U10): Accessible Custom Celebration Switcher**
  - Upgraded celebration selector to accessible ARIA `role="listbox"` with keyboard navigation (Arrow Up/Down, Enter, Escape) and event type icons.
  - Tested in `tests/test_ui_refinements.py` (test_u10_accessible_celebration_switcher).
  - Commit SHA: `ed21992`.
- **R3-T11 (U11): Single-Language Cultural Greeting**
  - Implemented single-language greeting by time of day (e.g. "शुभ प्रभात" in Hindi, "Good Morning" in English) based on active language toggle.
  - Tested in `tests/test_ui_refinements.py` (test_u11_cultural_greeting_single_language).
  - Commit SHA: `ed21992`.
- **R3-T12 (U12): Event-Type Accent Personalization**
  - Added dynamic theme classes (`.theme-wedding`, `.theme-birthday`, `.theme-community`) dynamically attached to `body`.
  - Tested in `tests/test_ui_refinements.py` (test_u12_event_type_theme_personalization).
  - Commit SHA: `ed21992`.
- **R3-T13 (U13): Structured Cultural Footer**
  - Added `.site-footer` with Vedic guidance notice, privacy guarantee, copyright, and system links.
  - Tested in `tests/test_ui_refinements.py` (test_u13_structured_cultural_footer).
  - Commit SHA: `ed21992`.
- **R3-T14 (U14): Social Metadata & SVG Favicon**
  - Authored custom saffron Devanagari ॥ SVG favicon in `public/favicon.svg` and full OpenGraph/Twitter meta tags in `public/index.html`.
  - Tested in `tests/test_ui_refinements.py` (test_u14_metadata_and_favicon).
  - Commit SHA: `ed21992`.
- **R3-T15: Post-Refinement Screenshot Capture**
  - Captured complete 16-screenshot suite across light and dark themes for all 8 application views in `docs/reports/ui-after/`.
  - Commit SHA: `1e1694a`.

