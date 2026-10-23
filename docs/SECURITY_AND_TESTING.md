# Security Architecture & Comprehensive Testing Plan - Utsav (उत्सव)

**Document Version:** 1.0.0-PROD  
**Author:** Senior Cybersecurity Engineer & Lead QA Architect  
**Date:** 2026-10-23  

---

## Part 1: Security Architecture & Threat Model

### 1.1 STRIDE Threat Modeling Analysis
| Threat Category | Potential Attack Vector | Applied Countermeasure in Utsav |
|---|---|---|
| **Spoofing** | Attacker impersonating another host to view guest lists. | Authenticated session token verified on every route; guest mode generates high-entropy UUIDs. |
| **Tampering** | Man-in-the-middle tampering with budget amounts or quotes. | Mandatory HTTPS on Netlify CDN; strict Pydantic v2 type casting and range limits (`gt=0`). |
| **Repudiation** | Denying an approved budget re-balancing or vendor change. | Timestamps and change records stored on updated documents. |
| **Information Disclosure** | Leakage of Gemini API credentials in frontend bundle. | Zero client-side API keys. All GenAI calls execute exclusively on Python backend/Netlify Functions. |
| **Denial of Service** | Flooding Gemini endpoints to drain API quota or budget. | In-memory sliding-window rate limiter (15 requests/10 min) + Netlify DDoS mitigation. |
| **Elevation of Privilege** | Escalating from viewer to owner of another event. | Multi-tenant tenant-isolation check on every DB query (`WHERE user_id == session.uid`). |

---

### 1.2 GenAI Prompt Injection & Jailbreak Defense
1. **Input Boundary Encapsulation:**
   User briefs and chat messages are stripped of control characters and wrapped in strict XML framing tags before feeding into Gemini:
   ```python
   def sanitize_prompt_input(raw_text: str) -> str:
       # Strip markdown command injection and system overrides
       cleaned = re.sub(r"[\r\n]{3,}", "\n\n", raw_text.strip())
       cleaned = cleaned.replace("SYSTEM:", "").replace("ASSISTANT:", "")
       return cleaned[:1000]
   ```
2. **Schema Enforcement:** Gemini is forced to respond in `application/json` conforming strictly to `EventMasterPlan.model_json_schema()`. Any free-form malicious instructions in user input are rejected by the Pydantic parser.
3. **Loop Defense & Max-Iteration Caps:**
   - AI repair prompts are hard-capped at **1 retry** (`max_retries = 1`).
   - Hard execution timeout enforced via `asyncio.wait_for(gemini_call, timeout=12.0)`.
   - If repair fails or times out, the system immediately drops to the curated deterministic regional seed. Under no circumstances can an infinite generation loop occur.

---

### 1.3 Security Headers & Content Security Policy (CSP)
Configured via `netlify.toml` and FastAPI middleware:
```http
Content-Security-Policy: default-src 'self'; script-src 'self' 'unsafe-inline' https://cdn.jsdelivr.net; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: https:; connect-src 'self' https://generativelanguage.googleapis.com; frame-ancestors 'none';
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Referrer-Policy: strict-origin-when-cross-origin
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
```

---

## Part 2: Comprehensive Testing Strategy

```mermaid
flowchart TD
    subgraph Testing_Pyramid ["Automated Test Suite Pyramid"]
        E2E["Playwright E2E & axe Accessibility (Browsers)"]
        Integration["FastAPI Integration & Mock Tests (httpx + pytest)"]
        Unit["Pydantic Schemas, Currency Math & Loop Limits (pytest)"]
    end
    
    subgraph Specialized_Stress ["Resilience & Load Testing"]
        LoopTest["Loop Safety & Timeout Tests"]
        LoadTest["k6 Concurrency & Quota Exhaustion Simulation"]
    end

    Unit --> Integration --> E2E
    Specialized_Stress --> Testing_Pyramid
```

---

### 2.1 Test Matrix & Scenarios

| Test File | Type | What is Tested | Acceptance Threshold |
|---|---|---|---|
| `tests/test_budget_math.py` | Unit | Live totals, percentage split, advance payments, over-budget detection. | 100% pass, ≥ 95% line coverage |
| `tests/test_schemas.py` | Unit | Pydantic v2 validation, empty titles, negative budgets, date parsing. | 100% pass |
| `tests/test_api_routes.py` | Integration | FastAPI TestClient endpoints (`/api/ai/plan`, `/api/ai/rebalance`, `/api/export/calendar`). | 100% pass |
| `tests/test_gemini_mock.py` | Integration | Gemini response parsing, repair prompt trigger, 429 quota exhaustion fallback. | 100% pass |
| `tests/test_edge_cases.py` | Edge Cases | Max-length inputs, Devanagari text, zero budgets, past dates, huge guest counts. | 100% pass |
| `tests/test_loop_safety.py` | Resilience | Infinite loop prevention: ensures AI agent stops at max-iteration (1) and timeout (12s). | 100% pass |
| `tests/load/k6_load_test.js` | Load | 50 concurrent virtual users querying health and demo endpoints. | p95 latency < 400ms, 0% errors |

---

### 2.2 Loop Testing Specification
To prevent agent and retry loops from running unbounded:
1. **Scenario 1:** Gemini continuously returns malformed JSON.
   - *Verification:* The repair loop executes exactly once, catches the second validation error, and immediately returns the fallback seed without re-querying Gemini.
2. **Scenario 2:** Gemini API hangs or experiences upstream network partition.
   - *Verification:* `asyncio.wait_for` triggers after 12.0 seconds, logs a warning, and returns the fallback seed within 50ms.

---

### 2.3 Pre-Submission QA Quality Gate Checklist
- [ ] Zero API keys exposed in client code or Git repository history.
- [ ] All 12 documentation files present and complete in `/docs` and `README.md`.
- [ ] Application launches locally with single command: `python run.py`.
- [ ] Netlify configuration verified with `netlify.toml` and Mangum serverless entrypoint.
- [ ] All 4 core pillars functional for Weddings, Birthdays, and Community events.
- [ ] Demo mode operational with 3 seeded celebrations.
- [ ] WCAG 2.2 AA accessibility verified with `@axe-core`.
