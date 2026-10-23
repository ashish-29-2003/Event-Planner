# Technical Architecture Specification - Utsav (उत्सव)

**Product Name:** Utsav (उत्सव)  
**System Architecture Version:** 1.0.0-PROD  
**Author:** Senior Software Architect  
**Date:** 2026-10-23  

---

## 1. High-Level System Architecture

Utsav is architected as an asynchronous **Python-Native Full-Stack Application** powered by **FastAPI**, **Pydantic v2**, and the official **Google GenAI Python SDK**. It is engineered for dual execution: locally via a high-performance **Uvicorn** server, and in cloud production via **Netlify Serverless Functions** (powered by Mangum / AWS Lambda) coupled with a global edge CDN for static assets.

### 1.1 Architecture Topology Diagram

```mermaid
flowchart TD
    subgraph Client ["Client Presentation Layer (Web / Mobile PWA)"]
        UI["Modern Responsive UI (HTML5 / Tailwind CSS / Vanilla JS)"]
        Store["Client State Store (Active Edits, Theme, Ephemeral Modals)"]
        SSEClient["EventSource / SSE Streaming Client"]
        A11y["WCAG 2.2 AA ARIA & Focus Trap Controllers"]
        Motion["CSS Spring & Cubic-Bezier Animation Engine"]
    end

    subgraph Netlify_Edge ["Netlify Global Edge Platform"]
        EdgeCDN["Netlify CDN (Static Assets, Fonts, Mandala SVGs)"]
        Redirects["netlify.toml Rewrites (/api/* -> Functions)"]
        SecurityHeaders["CSP, X-Frame-Options, HSTS Headers"]
    end

    subgraph Backend_Serverless ["Python Backend Layer (FastAPI + Mangum)"]
        FastAPIApp["FastAPI ASGI Core Application"]
        RateLimiter["Sliding-Window Rate Limiter & Security Guard"]
        PlanRoute["POST /api/ai/plan (Master Celebration Plan)"]
        ChatRoute["POST /api/ai/chat (Streaming Conversational Planner)"]
        RebalanceRoute["POST /api/ai/rebalance-budget (Financial Allocator)"]
        MuhuratRoute["POST /api/ai/muhurat (Auspicious Window Estimator)"]
        ExportRoute["GET /api/export/calendar (iCalendar .ics Generator)"]
    end

    subgraph AI_Orchestration ["Python GenAI Orchestration Layer"]
        PromptEngine["Versioned System Prompts & Guardrails"]
        GeminiSDK["Google GenAI Python SDK (gemini-1.5-flash)"]
        PydanticValidator["Pydantic v2 Schema Enforcement"]
        RepairLoop["Self-Healing Repair Prompt Loop (Max 2 Attempts)"]
        FallbackCache["Deterministic Seeded Fallback Blueprints"]
    end

    subgraph Persistence_Layer ["Data & Storage Layer"]
        LocalDB["Local Document / SQLite Store (Zero-friction local dev)"]
        CloudFirestore["Cloud Firestore / Firebase Admin SDK (Cloud multi-tenancy)"]
        SeedData["Curated Datasets (Weddings, Birthdays, Community Melas)"]
    end

    UI --> EdgeCDN
    UI -->|API Requests & SSE| Netlify_Edge
    Netlify_Edge --> Redirects
    Redirects --> FastAPIApp
    FastAPIApp --> RateLimiter
    RateLimiter --> PlanRoute & ChatRoute & RebalanceRoute & MuhuratRoute & ExportRoute
    PlanRoute & ChatRoute & RebalanceRoute --> AI_Orchestration
    AI_Orchestration --> PromptEngine
    PromptEngine --> GeminiSDK
    GeminiSDK --> PydanticValidator
    PydanticValidator -- Valid --> FastAPIApp
    PydanticValidator -- Invalid --> RepairLoop
    RepairLoop -- Failed --> FallbackCache
    FastAPIApp --> Persistence_Layer
```

---

## 2. Layer-by-Layer Architectural Breakdown

### 2.1 Presentation & UI Layer (Client)
- **Serving:** Static HTML5, modular JavaScript ES modules, and Tailwind CSS served directly by Netlify's global edge network (or by FastAPI's `StaticFiles` during local execution).
- **Styling & Assets:** Tailwind CSS with CSS custom properties (variables) for theme tokens (`--bg-primary`, `--accent-saffron`, `--accent-gold`, etc.), Google Fonts (*Noto Serif Devanagari* and *Plus Jakarta Sans*), and Lucide icon SVGs.
- **State Management:** Reactive vanilla JS store implementing publish-subscribe patterns for instant UI updates, tab changes, and budget tickers.
- **Streaming Client:** Uses native browser `fetch` with `ReadableStream` reader (or `EventSource`) to receive SSE tokens from the FastAPI `/api/ai/chat` endpoint and render markdown in real time.

### 2.2 API & Backend Framework (FastAPI)
- **Core Engine:** FastAPI 0.110+ on Python 3.10/3.13.
- **Serverless Adapter:** `mangum` transforms FastAPI's ASGI interface into standard AWS Lambda / Netlify Function handler format (`handler = Mangum(app)`).
- **Validation:** Pydantic v2 provides compile-time and runtime validation with automatic OpenAPI 3.1 spec generation (`/docs`).
- **Security Middleware:** Custom FastAPI middleware for Content Security Policy, CORS allowlisting, and sliding-window rate limiting.

### 2.3 GenAI Orchestration Layer
The orchestration engine handles structured outputs and conversational streaming with resilient self-healing:

```mermaid
sequenceDiagram
    autonumber
    actor Client as User Browser
    participant API as FastAPI /api/ai/plan
    participant Engine as AI Orchestrator (Python)
    participant Gemini as Google Gemini 1.5 Flash
    participant Validator as Pydantic v2 Validator
    participant Fallback as Seeded Fallback Blueprints

    Client->>API: POST /api/ai/plan (Celebration Brief)
    API->>API: Rate limit check & input sanitization
    API->>Engine: generate_master_plan(brief)
    Engine->>Gemini: generate_content(system_prompt + brief, response_schema)
    alt Gemini Returns Valid JSON
        Gemini-->>Engine: Raw JSON String
        Engine->>Validator: EventPlanSchema.model_validate_json(raw_json)
        alt Pydantic Validation Succeeded
            Validator-->>API: Validated EventPlan Model
            API-->>Client: 200 OK (EventPlan)
        else Pydantic Validation Failed
            Validator-->>Engine: ValidationError Details
            Engine->>Gemini: Repair Prompt (raw_json + errors)
            Gemini-->>Engine: Repaired JSON String
            Engine->>Validator: model_validate_json(repaired)
            alt Repaired Valid
                Validator-->>API: Validated EventPlan
                API-->>Client: 200 OK (EventPlan)
            else Still Invalid
                Engine->>Fallback: get_seeded_blueprint(brief.event_type)
                Fallback-->>API: Curated Fallback Plan
                API-->>Client: 200 OK (Fallback Plan + banner flag)
            end
        end
    else Gemini 429 Quota Exhausted or Timeout
        Gemini-->>Engine: Exception (429 / Timeout)
        Engine->>Fallback: get_seeded_blueprint(brief.event_type)
        Fallback-->>API: Curated Fallback Plan
        API-->>Client: 200 OK (Fallback Plan + banner flag)
    end
```

---

## 3. Directory & Folder Structure

The repository maintains strict Python best practices:

```
utsav-event-planner/
├── .github/
│   └── workflows/
│       └── ci.yml               # Automated Lint, Mypy, Pytest & Netlify Deploy Check
├── docs/                        # Complete Phase 1 Documentation Deliverables
│   ├── PRD.md
│   ├── ARCHITECTURE.md
│   ├── AGENTS.md
│   ├── DECISIONS.md
│   ├── TASKS.md
│   ├── TRD.md
│   ├── APP_FLOW.md
│   ├── UI_UX_FLOW.md
│   ├── SECURITY_AND_TESTING.md
│   ├── BACKEND_SCHEMA.md
│   ├── IMPLEMENTATION_PLAN.md
│   └── STAGE_STATUS.md
├── netlify/
│   └── functions/               # Netlify Serverless Function Handlers
│       ├── api.py               # Mangum entrypoint wrapping FastAPI app
│       └── requirements.txt     # Python serverless dependencies
├── public/                      # Static Web Assets (Served by Netlify & FastAPI)
│   ├── index.html               # Main Single-Page Application Shell
│   ├── css/
│   │   ├── styles.css           # Tailwind + Custom Cultural Styling
│   │   └── fonts.css            # Noto Serif Devanagari & Plus Jakarta Sans
│   ├── js/
│   │   ├── app.js               # Core UI orchestrator & router
│   │   ├── api.js               # REST client for FastAPI endpoints
│   │   ├── sse-client.js        # Streaming AI chat EventSource client
│   │   ├── store.js             # Reactive client-side state store
│   │   ├── components/          # Modular view components
│   │   │   ├── budget.js        # Budget matrix & AI re-balancing UI
│   │   │   ├── timeline.js      # Milestone checklist & .ics export
│   │   │   ├── vendors.js       # Vendor quotes & discovery cards
│   │   │   ├── ideas.js         # Cultural ideas deck
│   │   │   ├── muhurat.js       # Auspicious dates helper
│   │   │   └── export.js        # Printable PDF celebration brief
│   │   └── mock-data.js         # Client-side instant demo fallback
│   └── assets/                  # Diya, Kalash, Torana, Mandala SVGs
├── src/
│   ├── __init__.py
│   ├── main.py                  # FastAPI Application Factory & Lifespan
│   ├── config.py                # Pydantic Settings (.env configuration)
│   ├── api/                     # Route Handlers
│   │   ├── __init__.py
│   │   ├── ai_routes.py         # /api/ai/plan, /api/ai/chat, /api/ai/rebalance
│   │   ├── event_routes.py      # /api/events CRUD endpoints
│   │   └── export_routes.py     # /api/export/calendar, /api/export/summary
│   ├── models/                  # Pydantic v2 Models & Schemas
│   │   ├── __init__.py
│   │   ├── event.py             # Event, Host & Metadata schemas
│   │   ├── budget.py            # Budget items & rebalance schemas
│   │   ├── timeline.py          # Task and milestone schemas
│   │   ├── vendor.py            # Vendor quotes and categories
│   │   └── ai_plan.py           # Unified EventMasterPlan schema
│   ├── services/                # Business Logic & External Integrations
│   │   ├── __init__.py
│   │   ├── gemini_service.py    # Google GenAI SDK wrapper & repair loop
│   │   ├── storage_service.py   # SQLite / Firestore multi-tenant persistence
│   │   └── calendar_service.py  # RFC-5545 iCalendar generation
│   ├── data/                    # Curated Seed Data
│   │   ├── __init__.py
│   │   ├── wedding_jaipur.py    # 350-guest Royal Rajasthani Wedding Seed
│   │   ├── birthday_blr.py      # 45-guest Cosmic Space Explorer Birthday Seed
│   │   └── community_delhi.py   # 800-resident Society Diwali Mela Seed
│   └── utils/
│       ├── __init__.py
│       ├── rate_limiter.py      # Token-bucket sliding window rate limiter
│       ├── sanitizer.py         # Prompt injection & input sanitization
│       └── currency.py          # Indian Lakh/Crore number formatting
├── tests/                       # Automated Test Suite
│   ├── conftest.py              # Pytest fixtures and test clients
│   ├── test_budget_math.py      # Budget calculation unit tests
│   ├── test_schemas.py          # Pydantic v2 validation tests
│   ├── test_api_routes.py       # FastAPI TestClient endpoint integration tests
│   ├── test_gemini_mock.py      # AI service mock tests (success & 429 fallback)
│   ├── test_edge_cases.py       # Huge inputs, negative budget, Devanagari text
│   └── test_loop_safety.py      # Iteration cap & timeout tests
├── netlify.toml                 # Netlify Build, Functions & Redirects Config
├── requirements.txt             # Project Python Dependencies
├── pyproject.toml               # Tool configuration (ruff, pytest, mypy)
├── run.py                       # Single-command local runner (`python run.py`)
└── README.md                    # Root project documentation
```

---

## 4. Netlify Deployment Architecture

### 4.1 `netlify.toml` Configuration
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

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "strict-origin-when-cross-origin"
```

### 4.2 Serverless Wrapper (`netlify/functions/api.py`)
```python
from mangum import Mangum
from src.main import app

# Mangum adapts FastAPI's ASGI app for Netlify / AWS Lambda serverless execution
handler = Mangum(app, lifespan="off")
```

---

## 5. Observability & Telemetry

- **Structured JSON Logging:** FastAPI middleware logs request timing, endpoint paths, client IP hashes, and Gemini inference latency.
- **Health Checks:** `/api/health` reports status of the Python runtime, active memory usage, and Gemini API connectivity.
- **Client Error Boundary:** In-browser error handlers catch network interruptions and seamlessly transition to local offline cache.
