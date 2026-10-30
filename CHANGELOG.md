# Changelog — Samaroh (समारोह)

All notable changes to this project are documented in this file.
The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.0.0] — 2026-10-30

### Added
- **Core Pillars & Cultural Intelligence (Stages R0–R3)**
  - Automated structured plan synthesis powered by Google Gemini 1.5 Flash (`google-genai`).
  - Mathematical AI budget re-balancer protecting core wedding/festive essentials while adjusting luxury items.
  - Real-time Lakh & Crore budget tracking with two-segment progress bar (paid vs. committed allocated).
  - Phased countdown timeline with relative deadline badges (*"in 16 days"*, *"Due today"*), toggleable milestones, and owner roles.
  - Direct Google Calendar deep linking and standard RFC-5545 `.ics` export.
  - Categorized vendor quotes directory for Indian celebrations (Pandits, Mandap, Halwais, Mehendi, Dhol) with Google Maps Places API proxy.
  - 6-dimensional regional ideas hub (Theme & Mood, Decor Accents, Curated Menu, Sacred Rituals, Interactive Games, Return Gifts).
  - Complete Guests & RSVP management module with party sizing, dietary preferences, and filter pills.
  - Saffron Devanagari ॥ SVG vector favicon and complete OpenGraph/Twitter social metadata.
  - High-contrast Subhashita wisdom aphorism bar, single-language cultural greeting by time of day, and animated SVG sun/moon theme switch.
  - Dynamic event accent personalization (wedding vermilion/gold, birthday marigold, community indigo).
  - Structured cultural footer with classical Vedic guidance notice, privacy stewardship pledge, and credits.

- **Security & Multi-Tenant Defense (Stage R2)**
  - Multi-tenant tenant authorization matrix enforcing cross-user IDOR isolation on celebrations, tasks, budgets, vendors, ideas, and guests.
  - Per-user celebration quota guard (max 20 celebrations per account).
  - Persistent sliding-window rate limiter with `X-RateLimit-*` and `Retry-After` headers.
  - Strict Pydantic v2 `ConfigDict(extra="forbid")` and global 1MB payload ceiling middleware returning 413 Payload Too Large.
  - 45-sample adversarial prompt injection corpus (`tests/security/injection_corpus.json`) and defense-in-depth sanitizer.
  - Frontend DOMPurify integration defanging all XSS sinks in streaming chat and markdown renderers.
  - Strict Content-Security-Policy (CSP) and unified HTTP security headers across FastAPI and Netlify edge (`netlify.toml`).
  - Production multi-stage `Dockerfile` enforcing least-privilege non-root execution (`USER samaroh`).
  - High-entropy HMAC-SHA256 time-bound tokens (`generate_share_token`, `verify_share_token`) for private celebration sharing.
  - Strict Firebase ID token verification with audience, issuer, subject, and clock skew validation.
  - Firebase App Check attestation token enforcement on AI generation endpoints.

- **Resilience, Efficiency & Accessibility (Stages R4–R6)**
  - In-memory normalized celebration brief AI response cache in `GeminiService` reducing duplicate generation latency to <10ms.
  - GZip compression middleware (`minimum_size=500`) and immutable 1-year cache headers on static assets.
  - Client bundle optimized to 26.55 KB gzipped total transfer (LCP < 450ms, CLS 0.00, TTFT < 150ms).
  - Automated `@axe-core/playwright` accessibility audit passing 16 view/theme permutations with 0 critical and 0 serious WCAG AA violations.
  - Accessible ARIA tabs pattern, custom celebration switcher listbox with full keyboard navigation (ArrowUp, ArrowDown, Enter, Escape).
  - 15-case comprehensive edge-case suite (₹10 Crore boundaries, negative budgets, 50,000 guests, Devanagari script preservation).
  - Playwright end-to-end journey tests for Jaipur Wedding, Bengaluru Birthday, and Delhi Community celebrations.
  - Load test benchmarking 200 concurrent requests (77.2 req/s, 100% success rate, p95 658ms).

- **Code Quality & CI/CD Pipeline (Stage R7)**
  - 100% strict typing compliance across all 32 Python source files with `mypy --strict src/`.
  - Expanded Ruff rules matrix (E, F, I, B, UP, S, SIM, C4) with zero errors.
  - Client-side JavaScript strict mode evaluation test in Playwright.
  - Automated OpenAPI schema synchronization test verifying all 18 frontend API methods against backend contracts.
  - Multi-job GitHub Actions CI workflow (`.github/workflows/ci.yml`) running commit lint, mypy strict, and Playwright tests.

### Verified Evidence & Metrics
- **Automated Tests:** 245 passing tests across 33 test files.
- **Statement Coverage:** 88% overall (1476 statements, 175 missed; 100% on schemas, models, and budget math).
- **A11y Violations:** 0 critical, 0 serious (WCAG 2.2 AA).
- **Bundle Size:** 26.55 KB gzipped total application payload.
- **Live Smoke Test:** 6/6 checks passing with zero failures.
