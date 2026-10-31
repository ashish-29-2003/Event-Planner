# Architecture Decision Records (ADRs) - Samaroh (समारोह)

This document records the foundational product and architectural decisions for **Samaroh** (formerly Utsav), a GenAI-powered Celebration & Event Planner built for the Google for Developers x H2S "Build with AI" PromptWars Hackathon.

---

## ADR 001: Product Identity, Naming, and Cultural Positioning

- **Status:** Accepted (Updated per user instruction)
- **Date:** 2026-10-23
- **Decider:** Staff Product Manager & UX Lead

### Context
The challenge requires a GenAI-powered planning assistant for Indian celebrations (weddings, birthdays, community/society events, housewarmings, and festivals). The brand must feel dignified, modern, warm, and deeply authentic—avoiding kitsch, caricature, or clichéd tropes.

### Decision
Adopt the prestigious name **Samaroh** (समारोह — Sanskrit/Hindi for grand ceremony, celebration, festive occasion) with the primary tagline:
> *"शुभ आरम्भ: every celebration begins well."*

The brand tone couples high-craft digital product aesthetics (inspired by Apple, Linear, and Stripe) with classical Indian celebratory motifs (diya warmth, torana marigolds, mandala geometry, and authentic Devanagari typography with *Noto Serif Devanagari*). Sanskrit phrases (*शुभ आरम्भ*, *स्वागतम्*, *मङ्गलम्*, *धन्यवाद*) are used meaningfully with nearby English translations.

### Alternatives Considered
1. *Utsav*: Initial working title; good but common.
2. *ShubhPlan / ShubhArambh*: Too functional; sounds like an enterprise checklist tool rather than an inspiring event companion.
3. *FestivAI*: Too generic, dilutes Indian cultural grounding, fails to evoke warmth.

### Consequences
- **Positive:** Distinctive, highly resonant with Indian families and diaspora across weddings, birthdays, and society functions; evokes grandeur and auspicious grace.
- **Negative:** Requires updating branding assets and domain target (`samaroh-ai.netlify.app`).

---

## ADR 002: Technology Stack: Python-Native Full-Stack (FastAPI + Pydantic v2 + Google GenAI SDK)

- **Status:** Accepted (User Mandated Python)
- **Date:** 2026-10-23
- **Decider:** Senior Software Architect & Lead Backend Engineer

### Context
The user explicitly requested the project to be built in **Python**, pushed to **GitHub**, and hosted on **Netlify**. The application requires high-performance asynchronous API endpoints, robust data modeling, streaming AI generation, resilient offline fallback, and clean one-command local execution.

### Decision
Adopt a modern, asynchronous **Python-Native Architecture**:
1. **Core Language & Runtime:** Python 3.10+ (specifically Python 3.13) with strict type annotations (`typing`, `Pydantic v2`).
2. **Web Framework & API:** **FastAPI** with **Uvicorn** (Asynchronous ASGI server). FastAPI provides native asynchronous request processing, automatic OpenAPI/Swagger documentation, native Pydantic v2 integration, and high throughput.
3. **GenAI SDK:** Official **Google GenAI Python SDK** (`google-genai` / `google-generativeai`) using `gemini-1.5-flash` with structured Pydantic output schemas, streaming response endpoints (`StreamingResponse` with Server-Sent Events / SSE), temperature control, and automated retry/repair loops.
4. **Data Persistence:** Cloud Firestore (via `google-cloud-firestore` / Firebase Admin Python SDK) for cloud persistence, paired with a resilient local JSON/SQLite document store for zero-friction local development and instant offline demo judging.
5. **Presentation Layer:** Premium, responsive UI served directly by FastAPI as a modern single-page / multi-view web application with Tailwind CSS, Google Fonts (*Noto Serif Devanagari* and *Plus Jakarta Sans*), Lucide icons, Framer-motion-quality CSS/JS animations, interactive budget tickers, diya loaders, and WCAG 2.2 AA accessibility.
6. **Testing Suite:** `pytest`, `pytest-asyncio`, `httpx` (FastAPI TestClient), `playwright` for Python (E2E & a11y testing), and k6 for load testing.
7. **Single-Command Launch:** `python run.py` (which launches Uvicorn with hot reload and opens the browser).

### Alternatives Considered
1. *Django*: Too heavyweight, synchronous ORM overhead, rigid template paradigm.
2. *Flask*: Lacks native async streaming, requires external plugins for Pydantic schema validation.
3. *Streamlit*: Incapable of matching the required Apple/Linear/Stripe visual craft, custom Devanagari typography, bespoke spring animations, or WCAG 2.2 AA accessibility standards.

### Consequences
- **Positive:** Direct alignment with user's Python requirement; native Google GenAI Python SDK integration; robust Pydantic data validation; zero node/npm dependency hell for backend logic; lightning-fast single-command startup (`python run.py`).
- **Negative:** Frontend assets are bundled/served statically by FastAPI rather than a separate Node SSR server.

---

## ADR 003: Deployment Architecture: Netlify & GitHub CI/CD

- **Status:** Accepted (User Mandated Netlify & GitHub)
- **Date:** 2026-10-23
- **Decider:** Senior DevOps & Cloud Architect

### Context
The user specified deploying and hosting the project on **Netlify**, with a GitHub repository syncing all changes.

### Decision
1. **Repository:** Git repository initialized locally, committed incrementally per stage, with remote tracking on GitHub.
2. **Netlify Deployment Strategy:**
   - **Static Frontend Assets:** Netlify serves the pre-rendered, optimized client UI (`dist/` or static public web app) with edge caching and SSL.
   - **Serverless API Backend:** Netlify Functions using Python runtime (`netlify/functions/`) wrapped with `mangum` to execute FastAPI route handlers serverlessly on AWS Lambda under the hood.
   - **Configuration:** Managed via `netlify.toml` with build commands, function definitions, and redirect rules:
     ```toml
     [build]
       publish = "public"
       functions = "netlify/functions"

     [functions]
       python_version = "3.11"

     [[redirects]]
       from = "/api/*"
       to = "/.netlify/functions/api/:splat"
       status = 200
     ```
3. **Local Development Parity:** Running `python run.py` serves the exact same FastAPI app locally on `http://127.0.0.1:8000` without requiring Netlify CLI.

### Consequences
- **Positive:** Zero server maintenance, free global CDN distribution, instant preview deploys on every git push to GitHub.
- **Negative:** Serverless functions have execution timeout limits (10s on Netlify free tier), necessitating streaming responses and client-side fallback handling.

---

## ADR 004: GenAI Orchestration, Model Selection, and Resilience

- **Status:** Accepted
- **Date:** 2026-10-23
- **Decider:** Senior AI Architect

### Context
The prompt mandates deep Google services integration. The GenAI planner must generate comprehensive, culturally accurate, multi-category event plans (budgets, timelines, vendor briefs, personalized ideas) while guaranteeing deterministic JSON schemas, streaming conversation, and resilience against quota exhaustion.

### Decision
1. **Model:** Google Gemini API (`gemini-1.5-flash` for high-speed streaming generation and budget re-balancing; `gemini-1.5-pro` for deep cultural synthesis when available).
2. **Execution Boundary:** All Gemini API calls execute strictly within FastAPI route handlers (`/api/ai/*`). The Gemini API key is never exposed to the client bundle.
3. **Structured Outputs:** Enforce Gemini native JSON Schema mode (`response_mime_type="application/json"`) validated against server-side **Pydantic v2** models.
4. **Self-Healing Fallback:**
   - Attempt 1: Standard structured prompt.
   - Attempt 2 (on validation failure): Repair prompt containing Pydantic validation issues with temperature reduced to 0.1.
   - Attempt 3 (on timeout / 429 quota exhaustion): Return richly crafted deterministic fallback templates (curated for weddings, birthdays, and community festivals) with an unobtrusive banner notifying the user that offline/cached intelligence is serving their request.
5. **Streaming Chat:** Implement Server-Sent Events (SSE) via FastAPI's `StreamingResponse` using Gemini's streaming API for the interactive conversational planner.

---

## ADR 005: State Management & Client Data Layer

- **Status:** Accepted
- **Date:** 2026-10-23
- **Decider:** Senior Frontend Engineer

### Context
The application maintains two categories of state:
1. Server state: Events, budgets, vendor quotes, guest lists, timeline tasks (persisted in DB).
2. Ephemeral UI state: Active onboarding step, drawer/modal state, interactive filters, budget slider re-balancing, audio/theme preferences.

### Decision
1. **Frontend Architecture:** Clean, modular JavaScript/TypeScript client layer with native reactive store pattern and EventSource integration for SSE.
2. **Data Sync:** REST API communication with FastAPI endpoints (`/api/events/*`, `/api/ai/*`), maintaining local caching in `localStorage` and `IndexedDB` for offline reliability.
3. **Form State & Validation:** Client-side HTML5 + JavaScript schema validation backed by server-side Pydantic validation.

---

## ADR 006: Backend Persistence, Authentication, and Multi-Tenancy

- **Status:** Accepted
- **Date:** 2026-10-23
- **Decider:** Senior Software Architect & Security Engineer

### Context
Need a cloud-native database and auth system deeply aligned with Google Cloud that provides real-time sync, zero operational overhead, and robust authorization.

### Decision
Use **Firebase Authentication** and **Cloud Firestore** (or SQLite fallback):
1. **Authentication:**
   - Google Sign-In with Firebase Auth.
   - **Anonymous / Guest Demo Mode:** Generates ephemeral session IDs allowing judges and first-time users to test the full planning loop without OAuth friction.
2. **Firestore / SQLite Architecture:**
   - Tables / Collections:
     - `users`: Profile, preferences, language.
     - `events`: Event metadata, culture, date, budget, guest count.
     - `budget_items`: Category-wise line items, advance, payment status.
     - `task_items`: Phased timeline milestones and due dates.
     - `vendor_items`: Vendor requirements, quotes, contact status.
     - `guest_items`: Names, groups, dietary preferences, RSVP status.
     - `idea_items`: Curated cultural suggestions across 6 tabs.
3. **Security:** Enforce strict per-user multi-tenant isolation where `userId` matches the authenticated session token.

---

## ADR 007: Abuse Prevention, Rate Limiting, and API Security

- **Status:** Accepted
- **Date:** 2026-10-23
- **Decider:** Senior Cybersecurity Engineer

### Context
The application exposes Gemini API endpoints that can be abused or depleted by malicious traffic, spam, or denial-of-wallet attacks.

### Decision
1. **In-Memory & Sliding-Window Rate Limiting:** FastAPI middleware enforces rate limits (e.g. 15 AI planning calls per IP/User per 10-minute window).
2. **Input Sanitization & Injection Defense:**
   - Stripping markdown/control characters from prompt interpolations.
   - Rigid system prompt separation with XML tags (`<user_brief>...</user_brief>`).
   - Hard limit on brief length (1,000 characters).
3. **Security Headers:** Strict Content Security Policy (CSP), `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: strict-origin-when-cross-origin`.

---

## ADR 008: Google Services Ecosystem Depth

- **Status:** Accepted
- **Date:** 2026-10-23
- **Decider:** Staff Product Manager & Architect

### Context
PromptWars evaluation criteria explicitly dock points for *"early-stage use of Google services"*. The application must meaningfully integrate multiple Google Cloud/Developer services beyond a superficial API call.

### Decision
Integrate the following 7 Google services natively:
1. **Google Gemini API**: Structured JSON generation, streaming planning assistant, budget re-balancing agent.
2. **Firebase Authentication**: Google OAuth, anonymous auth, session validation.
3. **Cloud Firestore**: Real-time multi-tenant document database with validated security rules.
4. **Firebase App Check (reCAPTCHA Enterprise)**: Bot and abuse deterrence on API routes.
5. **Google Calendar Export**: Auto-generated `.ics` file generation and direct `calendar.google.com/calendar/render` deep links for all event timeline milestones and rituals.
6. **Google Maps Platform (Places API & Maps JavaScript / Static Maps)**: Vendor address geocoding and discovery for event cities (Delhi NCR, Mumbai, Jaipur, Bengaluru, Chennai, etc.) with mock fallback when API keys are omitted.
7. **Google Fonts**: `Noto Serif Devanagari` and `Plus Jakarta Sans`.

---

## ADR 009: Design System, Cultural Visual Language, and Motion

- **Status:** Accepted
- **Date:** 2026-10-23
- **Decider:** Senior UX/UI Designer

### Context
Indian celebrations demand vibrant warmth, but modern apps require clean whitespace, legible typography, and restraint.

### Decision
1. **Theme Tokens:**
   - Base Light: Warm Ivory (`#FAF7F2`), Card Ivory (`#FFFFFF`), Border (`#F0EAE1`).
   - Base Dark: Deep Indigo (`#0B0F19`), Card Indigo (`#131B2E`), Border (`#1E293B`).
   - Accents: Saffron/Kesari (`#FF7A00`), Sindoor Vermilion (`#E11D48`), Royal Gold (`#D97706`), Marigold Amber (`#F59E0B`), Deep Peacock Blue (`#0284C7`).
2. **Cultural Visual Accents:**
   - SVG Mandala vectors as low-opacity decorative hero backdrops.
   - Diya flame pulse loader for AI synthesis states.
   - Traditional auspicious greetings with inline contextual translations.
   - Rotating daily/session Subhashita (verified classical Sanskrit aphorism with attribution and meaning).
3. **Motion Strategy:**
   - Smooth CSS cubic-bezier transitions (`cubic-bezier(0.16, 1, 0.3, 1)`).
   - Animated number tickers for budget re-balancing calculations.
   - Automatic reduction of all motion when `prefers-reduced-motion` is detected.

---

## ADR 010: Offline Demo Mode & Seed Data Strategy

- **Status:** Accepted
- **Date:** 2026-10-23
- **Decider:** Senior QA Engineer

### Context
Judges must be able to explore the full capabilities of Samaroh even in scenarios where API keys are unavailable, network is throttled, or Gemini quotas are saturated.

### Decision
Build a first-class **Demo Mode** toggled via the UI banner and URL parameter (`?demo=true`). Demo mode includes 3 pre-built, production-grade celebrations:
1. **Wedding (Jaipur Destination):** *"Riya & Kabir's Royal Sangeet & Vivaha"* — 350 guests, ₹45,00,000 budget, 8-stage timeline, 12 vendor categories, Rajasthani/Marwari traditions.
2. **Birthday (Bengaluru Urban):** *"Aarav's 5th Cosmic Explorer Adventure"* — 45 guests, ₹85,000 budget, space-theme menu, return gifts, timeline.
3. **Community Event (Delhi NCR Society):** *"Gulmohar Enclave Diwali Mela & Dandiya Night"* — 800 residents, ₹6,50,000 budget, RWA permits, food stalls, sound stage, safety protocols.

---

## ADR 011: Cloud Architecture, Authentication & Persistence (Firebase Auth & Firestore)

- **Status:** Accepted
- **Date:** 2026-10-29
- **Decider:** Senior Cloud Architect & Security Lead

### Context
Moving beyond early-stage evaluation requires robust Google Cloud services integration. An in-memory store fails across serverless instance restarts, and without identity verification, "multi-tenant" claims are subject to IDOR vulnerabilities.

### Decision
1. **Authentication:** Integrate Firebase Authentication with Google Sign-in on the frontend. The FastAPI backend verifies Firebase ID tokens via `firebase-admin` (with fallback to Google JWKS public key verification). Protected routes (`/api/events`, write actions) require a valid token, returning HTTP 401 if missing or invalid. Seeded celebrations remain accessible under a sandboxed read-only demo context.
2. **Persistence:** Cloud Firestore document repository structured under `/users/{uid}/events/{eventId}` with subcollections (`budgets`, `tasks`, `vendors`, `guests`). The repository interface abstracts storage so in-memory adapters remain available for unit tests and zero-dependency offline judging.
3. **Firestore Security Rules:** Deny all access by default; allow read and write only if `request.auth.uid == resource.data.owner_uid` (or matching path `/users/{uid}`).
4. **App Check:** Enforce Firebase App Check header verification on state-mutating and GenAI planning endpoints.
5. **Hosting:** Support Cloud Run containerization (`Dockerfile`) with non-root execution and health checks, alongside Netlify serverless deployment (`netlify.toml` + Mangum).

---

## ADR 012: Google Maps Platform Server-Side Places Discovery Proxy

- **Status:** Accepted
- **Date:** 2026-10-29
- **Decider:** Lead Backend Engineer

### Context
Finding accurate Indian celebration venues, halwais, decorators, and pandits requires geospatial intelligence without exposing sensitive Google Cloud API credentials in the browser bundle.

### Decision
Implement a dedicated server-side proxy endpoint `GET /api/places/search` in FastAPI:
1. Calls Google Maps Places API (Text Search / Places API New) securely using `GOOGLE_MAPS_API_KEY`.
2. Proxies normalized vendor data (name, address, rating, user review count, price level) to the client.
3. Degrades gracefully: if `GOOGLE_MAPS_API_KEY` is omitted, returns curated city candidates with a transparent indicator (`source: "curated_catalog"`).


---

## ADR 013: Hosting Architecture & Runtime Topology: Cloud Run vs Netlify Serverless

- **Status:** Accepted
- **Date:** 2026-10-29
- **Decider:** Principal Software Architect & DevOps Lead

### Context
Samaroh requires low-latency Server-Sent Events (SSE) streaming for Gemini GenAI planning, persistent connections, and deep Google Cloud integration (Firebase Auth, Cloud Firestore, Google Maps Places API). Serverless hosts (like Netlify Functions on AWS Lambda) impose strict 10s–26s execution timeouts, buffer HTTP streams, and terminate state across cold starts. Conversely, Netlify provides effortless edge CDN distribution for static assets and Git-driven continuous previews.

### Decision
Adopt a **Dual-Topology Hosting Architecture**:
1. **Primary Production Runtime (Google Cloud Run):**
   - Containerized deployment using an optimized multi-stage `Dockerfile` based on `python:3.13-slim`.
   - Runs non-root (`samaroh` user) on port 8080 with automated health check probes (`GET /api/health`).
   - Native HTTP/2 streaming support: Gemini SSE tokens stream immediately to the client without buffering or 10-second gateway cutoffs.
   - Zero-key IAM integration: Google Cloud Run service accounts automatically authenticate `firebase-admin` and `google-cloud-firestore` without committing or mounting credentials JSON files.
2. **Serverless Preview Runtime (Netlify + Mangum):**
   - Static frontend assets served from `/public` via Netlify Global Edge CDN with automated Brotli/Gzip compression.
   - Dynamic API requests routed through `netlify/functions/api.py` using `mangum` ASGI adapter.
   - In-memory / file-backed JSON store provides instant demo exploration even if Cloud Firestore permissions are unconfigured during external judging.
3. **Environment Parity:**
   Both environments share the identical configuration contract (`GEMINI_API_KEY`, `FIREBASE_PROJECT_ID`, `GOOGLE_MAPS_API_KEY`, `ENABLE_AUTH_ENFORCEMENT`, `ENABLE_APP_CHECK`).

### Consequences
- **Positive:** Uncompromised streaming GenAI performance on Google Cloud; seamless static CDN caching on Netlify; resilient fallback guarantees zero broken demo states for hackathon evaluators.
- **Negative:** Requires maintaining both `Dockerfile` and `netlify.toml` / serverless function configuration.


---

## ADR 014: Decoupled Architecture: Netlify Static Edge Frontend with Dedicated Containerized Python API Host Proxy

- **Status:** Accepted (Supersedes serverless Netlify Functions component in ADR-003 and ADR-013)
- **Date:** 2026-10-31
- **Decider:** Principal Software Architect & DevOps Lead

### Context
Official Netlify documentation (`docs.netlify.com/functions/overview`) confirms that Netlify Functions natively support only **JavaScript/TypeScript** and **Go**. Python is supported exclusively during build time (e.g. for static site generators such as MkDocs, Sphinx, or Pelican), not as a serverless function execution runtime. Consequently, deploying Python FastAPI wrapped with Mangum in `netlify/functions/api.py` fails in modern Netlify production environments, resulting in HTTP 404 responses for all `/api/*` endpoints (defect DEF-01).

Furthermore, Netlify credit usage imposes a cost (~15 credits) on every production build deploy, and the account has a finite credit reserve (~236 credits remaining). Pushing backend or test changes without frontend impact wastes credits needlessly.

### Decision
Decouple the live hosting architecture into two specialized tiers:

1. **Frontend Presentation Tier (Netlify Edge CDN):**
   - **Static Serving:** Netlify hosts the pre-rendered, vanilla ES6+ web application directly from `public/` (HTML, CSS, modular JS, SVG assets, audio).
   - **Credit Hygiene Build Rule:** Configure `build.ignore` in `netlify.toml` to only deploy when changes touch `public/` or `netlify.toml`:
     ```toml
     [build]
       publish = "public"
       ignore = "git diff --quiet $CACHED_COMMIT_REF $COMMIT_REF -- public/ netlify.toml"
     ```
   - **Edge API Proxy Rewrite:** Proxy all API traffic seamlessly using an HTTP 200 rewrite rule in `public/_redirects`:
     ```
     /api/*  https://<api-host>/api/:splat  200!
     ```
   - **Edge Security Headers:** Enforce strict CSP, HSTS, `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`, and `Cross-Origin-Opener-Policy: same-origin-allow-popups` (for Firebase Google OAuth popups) at the Netlify Edge via `public/_headers`.
   - **Functions Retirement:** Remove `netlify/functions/api.py` and delete the `[functions]` configuration block from `netlify.toml`.

2. **Backend Application Tier (Dedicated Containerized Python Host):**
   - Containerized deployment using the multi-stage `Dockerfile` (`python:3.13-slim`, non-root `samaroh` user, `0.0.0.0:$PORT`).
   - Host selection:
     - **Option A (Google Cloud Run):** Production host in `asia-south1` (Mumbai), co-located with Cloud Firestore and Google Gemini API, utilizing native IAM workload identity for credential-free Firestore authentication.
     - **Option B (Render / Hugging Face Spaces):** Fallback container host without credit card requirements, using Firebase service account credentials stored in host secrets.
   - **Proxy-Aware Client IP Extraction:** Rate limiter in `src/utils/rate_limiter.py` updated to extract client IP from `X-Nf-Client-Connection-Ip` or `X-Forwarded-For` when requests arrive from Netlify's proxy, preventing all Netlify users from sharing a single rate-limit bucket.
   - **Streaming Resilience:** If Netlify proxy buffers or truncates Server-Sent Events (SSE) connections exceeding 26 seconds, frontend chat can stream directly from `window.__API_BASE__` with CORS enabled on the backend.

### Consequences
- **Positive:**
  - Fully resolves DEF-01 by providing an official, supported Python 3.13 runtime.
  - Retains Netlify's ultra-fast global CDN for static frontend assets.
  - Protects user's Netlify credit balance by skipping builds on backend-only or doc-only commits.
  - Transparent to frontend users; client JavaScript fetches `/api/*` directly on the same origin without CORS complexity in standard mode.
- **Negative:**
  - Requires maintaining the containerized backend deployment on the dedicated API host alongside the Netlify frontend configuration.
