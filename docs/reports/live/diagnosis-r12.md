# Stage R12 Live Diagnosis Report (WP0)

**Date:** 2026-10-31  
**Environment:** Production (`https://samaroh.onrender.com`)  
**Backend:** FastAPI, Python 3.13, Cloud Firestore, Gemini 2.0 Flash  
**Commit Tested:** `f8bab06`  

---

## 1. Executive Summary

A comprehensive diagnostic probe was executed against `https://samaroh.onrender.com` evaluating the three packaged celebrations (`demo-wedding-jaipur`, `demo-birthday-blr`, `demo-community-delhi`) across two distinct client states:
- **Mode (a):** Public client without `Authorization` header.
- **Mode (b):** Client bearing a stale mock token (`test-token-google-user-...`) stored in browser `localStorage`.

### Root Cause 1: Stale Client Session Tokens
Prior releases seeded mock tokens into browser `localStorage` (`samaroh-auth-token`, `samaroh-auth-user`). When users revisit the production deployment, every HTTP request includes `Authorization: Bearer test-token-...`. In production mode (`ENVIRONMENT=production`), the backend auth middleware strictly rejects mock tokens with `401 Unauthorized: Test/mock tokens are rejected in production environment.`

### Root Cause 2: Demo Read Rejection with Invalid/Mock Tokens
In `src/utils/auth.py` and `src/api/event_routes.py`, `get_current_user_or_demo` attempted token verification before checking whether the targeted resource is a public demo celebration. Consequently, a client carrying any invalid or stale token received a 401 even when browsing read-only demo celebrations.

### Root Cause 3: API Layer Silent Failure Masking
In `public/js/api.js`, endpoints returning error payloads (e.g., `401 {"detail": "..."}`) were caught or checked with `Array.isArray(data) ? data : []`. The error object was silently coerced into an empty array `[]`, causing the UI to clear all tabs (budget, timeline, vendors) without displaying an error message or retry option.

### Root Cause 4: Plan Creation Auth Dependency & Fallback Trap
`POST /api/ai/plan` strictly enforces authentication (`require_authenticated_user`). When unauthenticated guests submit the "+ New Plan" modal, the request returns 401. The frontend catch block caught this error, popped a generic alert, and forcibly navigated to `loadCelebration('demo-wedding-jaipur')`, leaving users unable to create personal plans or see custom generated blueprints.

---

## 2. Live Probe Matrix

| Endpoint / Operation | Mode (a) No Auth | Mode (b) Bearer `test-token` | Finding |
|---|---|---|---|
| `GET /api/events/demo-wedding-jaipur` | **200 OK** (Title: Riya & Kabir) | **401 Unauthorized** | Demo blocked if stale token present |
| `GET /api/events/demo-wedding-jaipur/budget` | **200 OK** (8 categories) | **401 Unauthorized** | Masked to `[]` in UI |
| `GET /api/events/demo-wedding-jaipur/tasks` | **200 OK** (9 tasks) | **401 Unauthorized** | Masked to `[]` in UI |
| `GET /api/events/demo-wedding-jaipur/vendors` | **200 OK** (4 vendors) | **401 Unauthorized** | Masked to `[]` in UI |
| `GET /api/events/demo-events/demo-birthday-blr` | **200 OK** (Title: Aarav 1st Birthday) | **401 Unauthorized** | Switcher fails if token present |
| `GET /api/events/demo-community-delhi` | **200 OK** (Title: Delhi Diwali) | **401 Unauthorized** | Switcher fails if token present |
| `POST /api/ai/plan` (New Plan Brief) | **401 Unauthorized** (Auth required) | **401 Unauthorized** | Blocks personal plan creation |
| `POST /api/ai/rebalance-budget` | **401 Unauthorized** | **401 Unauthorized** | Rebalance requires auth |

---

## 3. Required Remediation Plan

1. **WP1:** Purge stale client tokens at startup (`localStorage.removeItem` for `test-token-*`), add `GET /api/me`, and grant unconditional read access for `demo-*` celebration resources even if an invalid token is provided.
2. **WP2:** Remove silent array coercions in `api.js`. Introduce typed `ApiError` with UI retry states and toast notifications.
3. **WP3:** Guarantee offline/packaged seed integrity, calibrate Diwali 2026 date (Nov 8, 2026), and strip invented phone numbers.
4. **WP4 & WP5:** Implement deterministic offline plan generator and allow guests to create personal celebrations in browser draft mode with switcher persistence, resolving the user-reported limitation.
