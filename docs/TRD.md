# Technical Requirements Document (TRD) - Samaroh (समारोह)

**Product Name:** Samaroh (समारोह)  
**Document Version:** 1.0.0-PROD  
**Author:** Senior Software Architect & Lead DevOps Engineer  
**Date:** 2026-10-23  

---

## 1. Non-Functional Requirements & Performance Budgets

### 1.1 Web Vitals & Frontend Performance Targets
The user interface must remain snappy, fluid, and responsive on standard Indian mobile connections and low-spec Android devices.

| Metric | Target (Mobile 4G) | Target (Desktop Fiber) | Measurement Tool |
|---|---|---|---|
| **Largest Contentful Paint (LCP)** | < 2.5 seconds | < 1.2 seconds | Lighthouse / Web Vitals API |
| **Interaction to Next Paint (INP)** | < 200 ms | < 50 ms | Chrome UX Report (CrUX) |
| **Cumulative Layout Shift (CLS)** | < 0.1 | < 0.02 | PerformanceObserver |
| **First Contentful Paint (FCP)** | < 1.5 seconds | < 0.8 seconds | Lighthouse |
| **Time to Interactive (TTI)** | < 3.2 seconds | < 1.8 seconds | Lighthouse |
| **Initial JavaScript Bundle Size** | < 80 KB (gzipped) | < 80 KB (gzipped) | Network panel audit |

### 1.2 GenAI Latency Targets & Token Budgets
| Operation | Model | Target Latency (p50) | Target Latency (p95) | Timeout Limit |
|---|---|---|---|---|
| **Full Event Master Plan** | Gemini 1.5 Flash | 2.5s | 4.8s | 12.0s |
| **Streaming Chat (TTFT)** | Gemini 1.5 Flash | 800ms | 1.4s | 5.0s |
| **Budget Re-balancing** | Gemini 1.5 Flash | 1.2s | 2.2s | 8.0s |
| **Muhurat / Ritual Guidance** | Gemini 1.5 Flash | 1.5s | 2.8s | 8.0s |

*Fail-safe policy:* If an upstream Gemini call exceeds its timeout limit or returns an HTTP 429/503, the Python backend immediately switches to deterministic fallback templates within 150ms.

---

## 2. Browser & Device Compatibility Matrix

Samaroh is built mobile-first to accommodate Indian family planners coordinating on smartphones.

| Platform / OS | Supported Versions | Testing Baseline |
|---|---|---|
| **Mobile Android** | Android 10+ (Chrome Mobile, Samsung Internet) | Chrome 120+ on Pixel / Samsung Galaxy |
| **Mobile iOS** | iOS 16+ (Mobile Safari, Chrome for iOS) | Safari on iPhone 13/14/15 |
| **Desktop Windows** | Windows 10/11 (Chrome, Edge, Firefox) | Chrome 122+, Edge 122+ |
| **Desktop macOS** | macOS 13+ (Safari, Chrome) | Safari 17+, Chrome 122+ |
| **Responsive Breakpoints** | 360px (mobile min), 640px (`sm`), 768px (`md`), 1024px (`lg`), 1280px (`xl`), 1536px (`2xl`) | Verified in Playwright viewport matrix |

---

## 3. Availability, Error Budgets, and Uptime

- **Target Availability:** 99.9% monthly uptime for core dashboard and persistence operations.
- **Error Budget Policy:** 0.1% allowable failure rate on persistent read/write operations.
- **Graceful Degradation:**
  - If Google Gemini API is degraded or quota is exhausted, users can still view, edit, add, delete, and export all existing budgets, tasks, vendors, and ideas.
  - New AI plan generations switch smoothly to curated regional templates with zero user-facing crash screens.

---

## 4. Rate Limiting & Abuse Prevention

Implemented on FastAPI middleware via a sliding-window token bucket:

| Endpoint | Rate Limit | Scope | Action on Exceeded |
|---|---|---|---|
| `/api/ai/plan` | 8 requests / 10 minutes | IP + User UID | HTTP 429 with `Retry-After` header + Fallback Template |
| `/api/ai/chat` | 20 requests / 10 minutes | IP + User UID | HTTP 429 with inline chat notification |
| `/api/ai/rebalance-budget` | 15 requests / 10 minutes | IP + User UID | HTTP 429 with offline mathematical re-balance fallback |
| `/api/export/*` | 30 requests / 10 minutes | IP + User UID | HTTP 429 rate limit banner |

---

## 5. Internationalization & Cultural Typography (i18n / l10n)

### 5.1 Language Architecture
- **Primary Languages Supported:**
  1. English (Indian English formatting: Lakhs/Crores, DD/MM/YYYY).
  2. Hindi (Devanagari script: पूर्ण हिंदी इंटरफ़ेस).
  3. Sanskritized Cultural Accents (Auspicious invocations, headers, and Subhashitas).
- **Typography Engine:**
  - English: `Plus Jakarta Sans` or `Inter` via Google Fonts.
  - Devanagari: `Noto Serif Devanagari` via Google Fonts with explicit CSS `line-height: 1.6` to avoid Devanagari vowel-sign clipping.
  - Every Devanagari text fragment includes an explicit `lang="hi"` attribute for assistive screen-reader phonetics.

### 5.2 Cultural Formatting Rules
- **Currency:** Indian Rupee symbol (`₹`) formatted with standard Indian grouping (e.g., `₹25,00,000` instead of Western `2,500,000`).
- **Dates:** Indian standard `DD MMMM YYYY` (e.g., `14 दिसम्बर 2026`).

---

## 6. Privacy, PII & Data Retention

1. **User Data Ownership:** Users retain complete ownership of all created celebrations and guest information.
2. **PII Minimization:** The application requires only an email address or anonymous session ID. Guest telephone numbers are strictly optional.
3. **Zero AI Training on User PII:** Gemini API calls are transmitted through Google Cloud Developer enterprise terms where user payloads are not retained for model training.
4. **Data Deletion:** Deleting a celebration triggers a cascading delete across all associated subcollections.

---

## 7. Python Dependencies & Justification

| Dependency | Purpose | Justification |
|---|---|---|
| `fastapi` | Modern ASGI Web Framework | High performance, async support, automatic OpenAPI docs, Pydantic integration. |
| `uvicorn[standard]` | ASGI Server | Lightning-fast asynchronous server for local execution. |
| `pydantic` (v2) | Data Validation & Schema | Strict data modeling, runtime type enforcement, JSON schema export for Gemini. |
| `google-genai` / `google-generativeai` | Official Google GenAI Python SDK | Official SDK for Gemini 1.5 Flash/Pro with structured output and streaming. |
| `mangum` | Serverless ASGI Adapter | Translates Netlify / AWS Lambda serverless function events to FastAPI ASGI format. |
| `httpx` | Async HTTP Client | Used for internal async API calls and integration testing with FastAPI TestClient. |
| `pytest` & `pytest-asyncio` | Testing Framework | Comprehensive unit and integration test runner. |
| `python-multipart` | Form Data Parser | Required by FastAPI for multipart form data parsing. |
| `python-dotenv` | Environment Variables | Reads local `.env` configuration securely. |
| `icalendar` | Calendar Generation | Generates RFC-5545 `.ics` files for timeline milestone export. |

---

## 8. Continuous Integration & Deployment Pipeline (CI/CD)

The GitHub Actions workflow executes on every pull request and push to `main`:
1. **Lint & Formatting:** `ruff check .` and `black --check .`
2. **Type Checking:** `mypy .` in strict mode.
3. **Unit & Integration Tests:** `pytest -v --cov=src` with coverage reporting.
4. **Netlify Automated Deploy:** GitHub repository integration automatically triggers Netlify build and deploy upon merging to `main`.
