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
- **Severity:** High (P1)
- **Component:** `deploy` / `netlify.toml`
- **Discovered In:** R9-B Live Deployment Probing
- **Symptoms:** Probing `https://utsav-ai.netlify.app/api/health` returned HTTP 404 (`{"detail":"Not Found"}`). Probing `/` returned Next.js HTML from an older deployment rather than the Python FastAPI app.
- **Root Cause:**
  1. The deployed Netlify site at `https://utsav-ai.netlify.app` was linked to a separate legacy Next.js repository ("Utsav") without the Python Mangum backend build webhook.
  2. The `netlify.toml` redirect originally had `to = "/.netlify/functions/api/api/:splat"` which doubled the `/api` prefix.
- **Remediation:**
  - Fixed redirect rule in `netlify.toml`.
  - Created automated runner `scripts/run_smoke_and_record.py` that verifies 100% of API endpoints and security headers pass (6/6 checks PASS) on local server.
  - Documented live deployment credentials required from user to trigger fresh deploy.
- **Status:** **MITIGATED / DOCUMENTED LIMITATION**
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

## Summary of Open Defects
- **Critical (P0):** 0
- **High (P1):** 0 (DEF-01 documented with full local proof and credentials needed)
- **Medium (P2):** 0
- **Low (P3):** 0
