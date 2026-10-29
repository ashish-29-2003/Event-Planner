# Master Task Board - Samaroh (समारोह)

**Project:** Samaroh - GenAI Celebration & Event Planner  
**Stack:** Python 3.13 (FastAPI + Pydantic v2 + Google GenAI SDK) + Vanilla JS Minimal UI + Netlify / Cloud Run  
**Author:** Staff Product Manager & Technical Lead  

---

## Stage R0: Reality Check, Re-baseline & Git Hygiene

- [x] **R0-T01:** Verify fresh setup from README and update instructions with explicit virtualenv and install steps.  
  *Role:* DevOps Lead | *Status:* Done | *Evidence:* README.md updated and verified.
- [x] **R0-T02:** Measure and record real test coverage with pytest-cov.  
  *Role:* QA Lead | *Status:* Done | *Evidence:* 76% coverage (17/17 passing in 1.24s).
- [x] **R0-T03:** Perform honest gap audit and author Verified vs Claimed table in `docs/STAGE_STATUS.md`.  
  *Role:* Staff PM | *Status:* Done | *Evidence:* docs/STAGE_STATUS.md rewritten with reopened stages.
- [x] **R0-T04:** Install conventional commit-msg hook and `.gitmessage` template.  
  *Role:* DevOps Lead | *Status:* Done | *Evidence:* `.gitmessage`, `scripts/validate_commit_msg.py`, `.git/hooks/commit-msg`.
- [x] **R0-T05:** Capture 16 automated baseline screenshots (light/dark across all 8 modules) into `docs/reports/ui-before/`.  
  *Role:* QA / Frontend | *Status:* Done | *Evidence:* Playwright script `scripts/capture_screens.py` executed.

---

## Stage R1: Google Services Depth, Authentication & Real Persistence

- [x] **R1-T01:** Implement Firebase Authentication with Google Sign-in on frontend and ID token verification (`firebase-admin`) in FastAPI backend.  
  *Role:* Security / Backend | *Status:* Done | *Evidence:* Implemented `src/utils/auth.py`, protected endpoints returning 401 without token, verified with 11 tests in `tests/test_auth.py`.
- [x] **R1-T02:** Implement Cloud Firestore repository behind existing `StorageService` interface for events, budgets, tasks, vendors, and guests.  
  *Role:* Backend Lead | *Status:* Done | *Evidence:* Implemented `FirestoreStorageService` and `InMemoryStorageService` with disk persistence (`data/local_store.json`), added Guest domain model and REST endpoints, verified with 4 tests in `tests/test_storage.py`.
- [x] **R1-T03:** Author and test Firestore Security Rules (owner-only access to `/users/{uid}/events/**`).  
  *Role:* Security Lead | *Status:* Done | *Evidence:* Authored `firestore.rules`, `firebase.json`, `firestore.indexes.json`, verified owner isolation and public read-only rules with 6 tests in `tests/test_firestore_rules.py`.
- [x] **R1-T04:** Implement Firebase App Check verification on AI generation and state-mutating endpoints.  
  *Role:* Security Lead | *Status:* Done | *Evidence:* Implemented `src/utils/app_check.py` and wired into `/api/ai/plan` and `/api/ai/rebalance-budget`, verified with 4 tests in `tests/test_app_check.py`.
- [x] **R1-T05:** Implement Google Maps Platform Places server-side proxy for venue and vendor discovery with graceful degradation.  
  *Role:* Backend Lead | *Status:* Done | *Evidence:* Implemented `src/services/places_service.py` and `src/api/places_routes.py` with `/api/places/search`, verified Google Maps parsing and curated catalog fallback with 3 tests in `tests/test_places.py`.
- [ ] **R1-T06:** Write Hosting Architecture ADR (Cloud Run vs Netlify serverless) in `docs/DECISIONS.md`.  
  *Role:* Architect | *Est:* 1h | *Deps:* R1-T02  
  *Acceptance:* Documents how Firebase Auth and Firestore integrate cleanly with hosting target.
- [ ] **R1-T07:** Deploy live working application URL and verify with smoke test.  
  *Role:* DevOps Lead | *Est:* 2h | *Deps:* R1-T06  
  *Acceptance:* Live URL responsive, documented in README and STAGE_STATUS.md.

---

## Stage R2: Security Hardening

- [ ] **R2-T01:** Implement strict authorization checks (tenant isolation) on every event, budget, task, vendor, and guest endpoint.  
  *Role:* Security Lead | *Est:* 2h | *Deps:* R1-T01  
  *Acceptance:* IDOR test suite proves cross-user access attempts fail with 403 Forbidden.
- [ ] **R2-T02:** Transition sliding-window rate limiting to shared persistent counter (per-IP and per-user).  
  *Role:* Security Lead | *Est:* 2h | *Deps:* R1-T02  
  *Acceptance:* Rate limiter operates consistently across multiple server instances with 429 and Retry-After headers.
- [ ] **R2-T03:** Comprehensive input validation audit: strict string lengths, body size limits, and Pydantic extra-field rejection.  
  *Role:* Backend Lead | *Est:* 2h | *Deps:* R2-T01  
  *Acceptance:* Malformed requests or unexpected JSON fields rejected with 422 Unprocessable Entity.
- [ ] **R2-T04:** Build adversarial prompt injection test corpus and verify sanitizer.  
  *Role:* AI Security | *Est:* 2h | *Deps:* R2-T03  
  *Acceptance:* Instruction override, role hijack, Devanagari evasion, and system prompt leakage attacks neutralised.
- [ ] **R2-T05:** Frontend XSS audit: replace unsafe DOM insertions with textContent or sanitized DOMPurify pipelines.  
  *Role:* Frontend Lead | *Est:* 2h | *Deps:* R2-T04  
  *Acceptance:* Script injection and onerror payloads neutralised in chat and dynamic lists.
- [ ] **R2-T06:** Enforce strict HTTP security headers (CSP without unsafe-inline where feasible, HSTS, X-Content-Type-Options, restricted CORS).  
  *Role:* Security Lead | *Est:* 1h | *Deps:* R2-T05  
  *Acceptance:* Verified via live curl -I output.
- [ ] **R2-T07:** Run automated dependency vulnerability audit (`pip-audit`) and secret scan.  
  *Role:* DevOps Lead | *Est:* 1h | *Deps:* R2-T06  
  *Acceptance:* Zero high/critical vulnerabilities; no API keys in repository.

---

## Stage R3: UI Refinement & Feature Completeness

- [ ] **R3-T01 (U1):** Reintroduce subtle cultural warmth: low-opacity mandala/rangoli line-art (3-6%) and restrained gold accents.  
- [ ] **R3-T02 (U2):** Build two-segment progress bar (Paid vs Allocated vs Target) with accessible `aria-valuenow` and legend.  
- [ ] **R3-T03 (U3):** Enhance Allocated budget hierarchy with percentage caption and Remaining Balance metric.  
- [ ] **R3-T04 (U4):** Refactor milestone rows: separate time field, relative dates ("in 10 days"), and interactive checkboxes.  
- [ ] **R3-T05 (U5):** Upgrade overview cards to display live dynamic metrics (top category budget donut, vendor count, pending tasks).  
- [ ] **R3-T06 (U6):** Upgrade header: high-contrast Subhashita bar, SVG theme toggle, bilingual EN/Hindi toggle, and user account menu.  
- [ ] **R3-T07 (U7):** Implement mobile horizontally scrollable tabs with edge fades, ARIA tabs pattern, and new Guests & RSVP module.  
- [ ] **R3-T08 (U8):** Standardize badges: rename "Active Blueprint" to "Active plan" using semantic palette tokens.  
- [ ] **R3-T09 (U9):** Build comprehensive Share Drawer: copy link, WhatsApp share (India-first), PDF export, and personalized blessing note.  
- [ ] **R3-T10 (U10):** Upgrade celebration switcher to accessible custom listbox with event icons, date, and budget details.  
- [ ] **R3-T11 (U11):** Refactor cultural greeting to single-language display based on language toggle.  
- [ ] **R3-T12 (U12):** Apply per-event accent personalization (wedding vermilion/gold, birthday marigold, community indigo).  
- [ ] **R3-T13 (U13):** Add structured footer with Panchang astrological disclaimer, privacy policy link, and credits.  
- [ ] **R3-T14 (U14):** Complete metadata: title, description, OpenGraph tags, and custom SVG favicon.  
- [ ] **R3-T15:** Capture 16 after-screenshots across all screens into `docs/reports/ui-after/`.

---

## Stage R4: Testing Depth & Resilience

- [ ] **R4-T01:** Enforce overall test coverage gate ≥ 80% (and ≥ 90% on budget math, validation, and AI parsing).  
- [ ] **R4-T02:** Implement comprehensive edge-case test suite (empty inputs, negative budget, Devanagari text, huge guest counts, Gemini timeouts).  
- [ ] **R4-T03:** Build mock integration tests for Gemini API, Firestore emulator, and calendar export.  
- [ ] **R4-T04:** Write frontend unit tests for `store.js` and `api.js` (SSE stream handling).  
- [ ] **R4-T05:** Implement Playwright E2E journey tests for Wedding, Birthday, and Community event planning flows.  
- [ ] **R4-T06:** Implement loop safety and max-iteration cap tests asserting repair loops terminate cleanly.  
- [ ] **R4-T07:** Run load testing scenario (k6 or Locust) and document p95 latencies and error rates.  
- [ ] **R4-T08:** Run full test suite 3 consecutive times with 100% green pass rate.

---

## Stage R5: Accessibility with Proof

- [ ] **R5-T01:** Run automated `@axe-core/playwright` accessibility audit on all views in light and dark themes; resolve all critical/serious issues.  
- [ ] **R5-T02:** Run Google Lighthouse Accessibility audit on mobile build and achieve score ≥ 95.  
- [ ] **R5-T03:** Conduct full manual keyboard navigation walkthrough (focus traps, visible indicators, skip link).  
- [ ] **R5-T04:** Conduct screen-reader pass (NVDA/VoiceOver) with ARIA live region verification; document in report.

---

## Stage R6: Efficiency with Measured Numbers

- [ ] **R6-T01:** Run Lighthouse Mobile performance audit; achieve ≥ 90 across Performance, Accessibility, Best Practices, and SEO.  
- [ ] **R6-T02:** Measure and record Web Vitals (LCP < 2.5s, INP < 200ms, CLS < 0.1) and Time-To-First-Token (TTFT).  
- [ ] **R6-T03:** Implement asset optimization: content-hashed static assets, long cache headers, font-display swap, and gzip/brotli.  
- [ ] **R6-T04:** Implement in-memory / Firestore AI response cache keyed by normalized celebration brief.  
- [ ] **R6-T05:** Measure and record transferred bundle sizes (JS/CSS) in `docs/TRD.md`.

---

## Stage R7: Code Quality & CI

- [ ] **R7-T01:** Python strict typing audit with `mypy --strict` passing across `src/`.  
- [ ] **R7-T02:** Expand Ruff rules (E, F, I, B, UP, S, SIM, C4) with zero errors.  
- [ ] **R7-T03:** Frontend JavaScript linting and formatting with ESLint and Prettier.  
- [ ] **R7-T04:** Author OpenAPI schema sync test verifying frontend expectations against backend contracts.  
- [ ] **R7-T05:** Configure multi-job GitHub Actions CI pipeline running lint, mypy, pytest, Playwright, and commit-msg verification.  
- [ ] **R7-T06:** Update `docs/ARCHITECTURE.md` to ensure diagrams and directory trees match real code.

---

## Stage R8: Live Deployment & Final Submission

- [ ] **R8-T01:** Deploy production build to cloud hosting; confirm environment variables and secrets.  
- [ ] **R8-T02:** Execute end-to-end smoke test against live production URL.  
- [ ] **R8-T03:** Update `README.md` with production URL, demo guide, and 3-minute hackathon judge script.  
- [ ] **R8-T04:** Author final honest evaluation scorecard in `docs/STAGE_STATUS.md` across all 6 PromptWars criteria.  
- [ ] **R8-T05:** Generate `CHANGELOG.md` from commit history and tag release `v1.0.0`.  
- [ ] **R8-T06:** Final git verification: clean working tree, all commits pushed to `origin/main`.
