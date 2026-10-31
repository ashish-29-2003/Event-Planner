# Samaroh (समारोह) — Defect Tracking Log (R9)

This document tracks all bugs, regressions, security findings, and architectural limitations discovered during Stage R9 truth auditing, testing checklist execution, and release locking.

---

## Defect Severity Classifications
- **Critical (P0):** Application crash, authentication bypass, data loss, cross-tenant IDOR leak, remote code execution.
- **High (P1):** Core pillar calculation error, security header omission, broken navigation flow, WCAG 2.2 AA critical violation.
- **Medium (P2):** Transient network timeout, performance budget overrun, non-critical accessibility warning, missing documentation.
- **Low (P3):** Cosmetic layout shift, minor copy inconsistency, non-functional styling refinement.

---

## Active & Resolved Defect Register

### DEF-01: Live Netlify Functions Returning 404 for Python Backend
- **Severity:** Critical (P0)
- **Component:** `deploy` / `netlify.toml`
- **Discovered In:** R9-B Live Deployment Probing
- **Symptoms:** Probing `https://utsav-ai.netlify.app/api/health` returned HTTP 404 (`{"detail":"Not Found"}`). Probing `/` returned Next.js HTML from an older deployment rather than the Python FastAPI app.
- **Root Cause:**
  1. The deployed Netlify site at `https://utsav-ai.netlify.app` was linked to a separate legacy Next.js repository ("Utsav") without the Python Mangum backend build webhook.
  2. Netlify Functions do not support Python runtimes natively in modern production (only JS, TS, and Go). Mangum in `netlify/functions/api.py` cannot execute as a native serverless runtime on Netlify.
  3. The `netlify.toml` redirect originally had `to = "/.netlify/functions/api/api/:splat"` which doubled the `/api` prefix.
- **Remediation Plan:**
  - Architecture overhaul (ADR-014): Decouple frontend and backend. Netlify hosts static assets from `public/` and proxies `/api/*` via HTTP 200 rewrite to a dedicated Python API host (Cloud Run / Render / HF Spaces).
  - Add build-skip rule in `netlify.toml` to protect Netlify credits.
  - Implement trusted proxy client IP resolution for rate limiting.
- **Status:** **OPEN**
- **Evidence:** `docs/reports/smoke_test_local_report.txt`, `docs/reports/curl_headers_report.txt`.

---

### DEF-02: Pip-Audit Advisory PYSEC-2026-3721 on Installed Pip
- **Severity:** Medium (P2)
- **Component:** `security` / `deps`
- **Discovered In:** R9-B Security Audit
- **Symptoms:** Initial `pip-audit --local` run flagged 2 known vulnerabilities in `pip` 26.1.2.
- **Root Cause:** Virtualenv was initialized with older pip packaging baseline.
- **Remediation:** Upgraded pip in virtual environment to version 26.2.2. Re-ran `pip_audit --local`.
- **Status:** **RESOLVED**
- **Evidence:** `docs/reports/pip_audit_report.txt` (0 known vulnerabilities found across all 54 dependencies).

---

### DEF-03: Silent Offline Fallback Notice Omitted in User Interface
- **Severity:** Medium (P2)
- **Component:** `ui` / `ai`
- **Discovered In:** R9-A Truth Audit
- **Symptoms:** When `GEMINI_API_KEY` was missing or quota exhausted, the backend returned a curated regional blueprint, but the frontend did not explicitly display a visible transparency disclaimer to the user.
- **Root Cause:** `is_fallback` flag returned by `POST /api/ai/plan` was not consumed by the UI DOM renderer.
- **Remediation:**
  - Configured `GEMINI_MODEL` default to `gemini-2.0-flash` with fallback warning logging.
  - Added diagnostic `"ai": "live" | "fallback"` to `GET /api/health`.
  - Added `#ai-fallback-banner` in `public/index.html` and `public/css/styles.css`.
  - Updated `public/js/app.js` to display `"Notice: Showing a sample plan; live AI is unavailable"` on initialization and plan generation when operating in offline/fallback mode.
- **Status:** **RESOLVED**
- **Evidence:** `tests/test_health.py`, `tests/test_ui_refinements.py`.

---

### DEF-04: Non-Distributed Serverless In-Memory Response Cache
- **Severity:** Low (P3)
- **Component:** `perf` / `api`
- **Discovered In:** R9-A Truth Audit
- **Symptoms:** AI response cache operates in-memory (`GeminiService._cache`). On serverless multi-instance platforms (Netlify Functions / Cloud Run), separate instances maintain distinct in-memory stores, leading to cache misses on cold instances.
- **Root Cause:** Architecture uses lean ASGI process memory without external Redis dependency to maintain single-command local runability.
- **Remediation:** Explicitly documented architectural trade-off in `docs/ARCHITECTURE.md` and `docs/STAGE_STATUS.md`.
- **Status:** **DOCUMENTED ARCHITECTURAL LIMITATION**
- **Evidence:** `docs/reports/performance_report.json`.

---

### DEF-05: Untracked Deploy Zip in Working Tree
- **Severity:** Low (P3)
- **Component:** `build` / `repo`
- **Discovered In:** R9-A Truth Audit
- **Symptoms:** `dist/samaroh-netlify-deploy.zip` was generated in the working tree.
- **Root Cause:** Build scripts wrote archives directly into project root.
- **Remediation:** Added `*.zip` and `dist/` explicitly to `.gitignore` and removed zip artifact from workspace.
- **Status:** **RESOLVED**
- **Evidence:** `.gitignore`.

---

### DEF-06 (D1): Hero Shows "undefined" as Plan Title and "Indian • India" as Subtitle
- **Severity:** Critical (P0)
- **Component:** `ui` / `store` / `app.js`
- **Discovered In:** User Video Recording Walkthrough (0:00 to 2:30)
- **Symptoms:** Hero title rendered literal string "undefined" and subtitle rendered "Indian • India".
- **Root Cause:** When an API response returned error detail or missing attributes, `activeEvent.title` was evaluated as undefined and assigned directly to `titleEl.innerText`.
- **Remediation:** Added `normalizeEvent(raw)` contract mapper in `public/js/store.js` and `public/js/api.js`. Guarantees title, culture, city, budget, and dates always have valid non-empty defaults and safe fallbacks. Never renders "undefined".
- **Regression Test:** `tests/test_block_a_regression.py::test_d1_seed_celebrations_contract_memory_and_firestore`, `test_d1_api_returns_complete_event_metadata`.
- **Status:** **RESOLVED (Block A)**

---

### DEF-07 (D2): Plan Switcher Does Not Switch Data Between Plans
- **Severity:** Critical (P0)
- **Component:** `ui` / `switcher` / `app.js`
- **Discovered In:** User Video Recording Walkthrough (0:00 to 0:16)
- **Symptoms:** Selecting "Bengaluru Cosmic Birthday" or "Delhi Diwali Dandiya Mela" left Jaipur wedding data on screen.
- **Root Cause:** Switcher button label changed, but per-plan state was not cleanly reset and subsequent subcollection fetches threw or remained tied to initial event ID.
- **Remediation:** Added `store.resetCelebration(eventId)` in `store.js` and updated `loadCelebration(eventId)` in `app.js` to re-fetch and render all modules (Overview, Budget, Timeline, Vendors, Ideas, Muhurat, Export, Guests) with updated event-type styling (`theme-wedding`, `theme-birthday`, `theme-community`).
- **Regression Test:** `tests/test_block_a_regression.py::test_d2_each_seed_has_distinct_budgets_milestones_and_vendors`.
- **Status:** **RESOLVED (Block A)**

---

### DEF-08 (D5): Add Guest Crashes with "store.state.guests is not iterable"
- **Severity:** High (P1)
- **Component:** `ui` / `guests` / `app.js`
- **Discovered In:** User Video Recording Walkthrough (1:14 to 1:20)
- **Symptoms:** Clicking Save Guest threw `TypeError: store.state.guests is not iterable`.
- **Root Cause:** `store.state.guests` was undefined when API returned non-array or when state was uninitialized, and array spread `[...store.state.guests, saved]` failed.
- **Remediation:** Initialized `guests: []` in store constructor and enforced `Array.isArray(guests) ? guests : []` guards in `store.setState`, `api.getGuests`, and guest form submission.
- **Regression Test:** `tests/test_block_a_regression.py::test_d5_get_guests_returns_list_for_all_events`.
- **Status:** **RESOLVED (Block A)**

---

### DEF-09 (D6): RSVP Counters Do Not Update on Status Change
- **Severity:** High (P1)
- **Component:** `ui` / `guests` / `app.js`
- **Discovered In:** User Video Recording Walkthrough (1:24 to 1:30)
- **Symptoms:** Changing a guest from Pending to Declined showed "Declined" in the select dropdown, but cards still showed Awaiting 2, Declined 0.
- **Root Cause:** `updateGuestRSVPStatus` failed on demo templates (403 read-only) before updating local store, preventing reactive counter recalculation.
- **Remediation:** Added pure helper `computeRsvpCounters(guests)` and updated `updateGuestRSVPStatus` to optimistically update the local store immediately, re-rendering all guest counter cards.
- **Regression Test:** `tests/test_block_a_regression.py::test_d6_rsvp_counter_calculation_on_status_change`.
- **Status:** **RESOLVED (Block A)**

---

### DEF-10 (D9): Budget Numbers Contradict Each Other Across Hero, Legend, and Ledger
- **Severity:** High (P1)
- **Component:** `ui` / `budget` / `app.js`
- **Discovered In:** User Video Recording Walkthrough (0:00 to 0:30)
- **Symptoms:** Metric box showed "Advance paid ₹15,60,000" while legend showed "Paid ₹15,10,000"; "100.0% committed" vs "Committed ₹28,00,000" (62%); "Remaining ₹0" vs "Buffer available ₹1,90,000".
- **Root Cause:** Legend numbers in `index.html` were static hardcoded values never updated by JavaScript, and metric box used disparate formulas.
- **Remediation:** Created single pure mathematical function `computeBudgetLedger(targetBudget, budgets)` that dynamically reconciles Target, Allocated, Paid, Balance Due, and Unallocated Buffer across metric boxes, progress bar tracks, and accessible legends.
- **Regression Test:** `tests/test_block_a_regression.py::test_d9_budget_ledger_reconciles_across_all_seeds`, `test_d9_budget_ledger_edge_cases`.
- **Status:** **RESOLVED (Block A)**

---

---

## Stage R12 Work Packages & Resolution Register

### R12-WP0: Live Diagnosis Matrix
- **Status:** **RESOLVED**
- **Artifact:** `docs/reports/live/diagnosis-r12.md`
- **Summary:** Probed all 3 celebration endpoints under Mode (a) Public No-Auth and Mode (b) Bearer mock token. Confirmed 4 root causes: stale tokens in client storage, 401s on optional demo routes, silent array coercions in `api.js`, and auth lock on plan synthesis.

### R12-WP1: Session Purge and Universal Public Demo Reads
- **Status:** **RESOLVED**
- **Commit:** `a3ca82a`
- **Regression Test:** `tests/test_wp1_session.py` (4 passed)
- **Live Check:** `GET /api/events/demo-wedding-jaipur` returns 200 with Bearer mock token; `GET /api/me` returns 401 without Bearer token.

### R12-WP2: Elimination of Silent Failures & Typed ApiError
- **Status:** **RESOLVED**
- **Commit:** `abff379`
- **Regression Test:** `tests/test_wp2_error_handling.py` (3 passed)
- **Summary:** Introduced typed `ApiError`, explicit tab states (`loading`, `ready`, `empty`, `error` with Retry button), and accessible floating toast notifications replacing disruptive `alert()` popups.

### R12-WP3: Seed Data Consistency & Authentic Panchang Dates
- **Status:** **RESOLVED**
- **Commit:** `a695252`
- **Regression Test:** `tests/test_wp3_seed_consistency.py` (4 passed)
- **Summary:** Calibrated Delhi Diwali community celebration to authentic Kartik Amavasya date (Nov 8, 2026), stripped all invented phone numbers (`phone=None`), and added seed integrity self-check in `/api/health`.

### R12-WP4: Deterministic Offline Plan Generation Engine
- **Status:** **RESOLVED**
- **Commit:** `77772c2`
- **Regression Test:** `tests/test_wp4_planner.py` (4 passed)
- **Summary:** Built `planner_service.py` synthesizing mathematically balanced budgets (Venue 35%, Catering 28%, Decor 15%, Photo 10%, Attire 7%, Rituals 5%), chronological milestones backwards from celebration date, regional vendors, and 6-dimension cultural ideas.

### R12-WP5: Personal Plan Creation, Draft Mode & Celebration Switcher
- **Status:** **RESOLVED**
- **Commit:** `e046422`
- **Regression Test:** `tests/test_wp5_creation_flow.py` (2 passed)
- **Live Check on Render:**
  - `POST https://samaroh.onrender.com/api/ai/plan/draft` -> Created `event-a7912139` ("Ashish Personal Birthday Celebration", ₹1,20,000, 6 budget lines, 6 tasks).
  - `GET https://samaroh.onrender.com/api/events/event-a7912139` -> HTTP 200 with full data.
  - Dynamically rendered in celebration switcher with persistent `localStorage` synchronization.

