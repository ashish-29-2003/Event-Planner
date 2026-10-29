# Samaroh (समारोह) — GenAI Celebration & Event Planner

> **॥ शुभ आरम्भ: every celebration begins well ॥**  
> An intelligent, culturally grounded celebration planning assistant for weddings, birthdays, and community festivals, powered by Google Gemini and built in Python.

[![Python Version](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.110%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Google Gemini](https://img.shields.io/badge/Google%20GenAI-Gemini%201.5%20Flash-orange.svg)](https://ai.google.dev/)
[![Netlify Status](https://img.shields.io/badge/Netlify-Deploy%20Ready-00C7B7.svg)](https://www.netlify.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Built for **PromptWars Virtual** (Google for Developers x H2S, "Build with AI", India).

---

## 🌟 Overview & Key Features

Samaroh eliminates the chaos of disjointed spreadsheets, notes, and WhatsApp chats by transforming an event brief into an actionable celebration master plan in seconds:

1. **💰 Dynamic Budget Planner with AI Re-Balancing:**
   - Real-time Lakh & Crore budget tracking across Venue, Catering, Decor, Photography, Entertainment, and Logistics.
   - Live payment tracking (Advance Paid vs. Balance Due) and visual over-budget warnings.
   - **One-Click AI Re-Balancing:** An intelligent financial agent that recalculates allocations when a category overspends, protecting core necessities like catering while trimming flexible luxury lines.

2. **⏳ Phased Countdown Timeline & Google Calendar Sync:**
   - Auto-generated 5-phase schedule: Foundation, Core Bookings, Details & Invites, Final Week, and Day-Of Run of Show.
   - Task assignment by owner role (Host, Uncle, Caterer, Decorator).
   - Instant export to RFC-5545 `.ics` file and direct deep-links to **Google Calendar**.

3. **📋 Categorized Vendor Checklist & Discovery:**
   - Covers Indian celebratory requirements: Pandits, Royal Halwais, Mandap Decorators, Mehendi Artists, Dholwalas, Stage Sound, and Candid Photographers.
   - Quote tracking, contact management, and local market quote bands.

4. **🌺 Culturally Personalized Ideas Hub:**
   - Tailored to regional culture (Marwari, Punjabi, South Indian Tamil, Bengali, Contemporary Urban).
   - Six interactive hubs: Theme & Mood, Decor Accents, Curated Regional Menu, Sacred Rituals, Interactive Games, and Return Gifts.

5. **✨ Cultural Craft & Auspicious Heritage:**
   - Classical Sanskrit invocations (*शुभ आरम्भ*, *मङ्गलम्*, *स्वागतम्*, *धन्यवादः*).
   - Daily authentic Subhashita with scholarly attribution and English translation.
   - Personalized time-of-day greetings (*शुभ संध्या, Ashish*) and personal family blessing notes on exports.
   - Sacred Diya flame pulse loader during AI generation.

6. **🛡️ 100% Demo Resilience:**
   - Instant Demo Mode loaded with 3 complete celebrations:
     - 💒 **Jaipur Royal Destination Wedding** (350 guests, ₹45L)
     - 🎂 **Bengaluru Cosmic Space Explorer Birthday** (45 guests, ₹85K)
     - 🏮 **Delhi NCR Society Diwali Mela & Dandiya** (800 residents, ₹6.5L)
   - Zero-crash fallback engine guaranteeing 100% uptime even if upstream Gemini API quotas are exhausted.

---

## 🏗️ Technical Architecture & Google Services

Samaroh is built as an asynchronous **Python-Native Full-Stack Application** designed for seamless local development and cloud serverless hosting:

- **Backend:** Python 3.10+ with **FastAPI**, **Pydantic v2**, and **Uvicorn**.
- **GenAI Engine:** Official **Google GenAI Python SDK** (`google-genai`) using `gemini-1.5-flash` with structured Pydantic schema decoding and streaming SSE chat.
- **Frontend:** Premium, responsive UI served directly by FastAPI and Netlify CDN, featuring Tailwind CSS, Google Fonts (*Noto Serif Devanagari* and *Plus Jakarta Sans*), and Lucide icons.
- **Cloud Deployment:** **Netlify** (via `netlify.toml` and Mangum serverless adapter for Python).
- **Google Services Integrated:**
  1. Google Gemini API (Planning, re-balancing, streaming assistant)
  2. Google Calendar Integration (.ics export & calendar deep links)
  3. Google Maps Platform (Vendor geocoding & discovery fallback)
  4. Google Fonts (Noto Serif Devanagari & Plus Jakarta Sans)

---

## 🚀 Quick Start (One Command)

### Prerequisites
- Python 3.10 or higher installed.
- Git.

### 1. Clone the Repository & Set Up Virtual Environment
```bash
git clone https://github.com/ashish-29-2003/Event-Planner.git
cd Event-Planner

# Create and activate virtual environment
python -m venv .venv
# On Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
# On Linux / macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Set Up Environment Variables
Copy `.env.example` to `.env`:
```bash
# On Linux / macOS:
cp .env.example .env
# On Windows (PowerShell):
Copy-Item .env.example .env
```
Add your Google Gemini API key:
```env
GEMINI_API_KEY="your-gemini-api-key-here"
```
*(Note: If no API key is supplied, Samaroh gracefully falls back to its curated celebration blueprints!)*

### 3. Launch the Application
Run the single root launcher:
```bash
python run.py
```
This automatically verifies dependencies, starts the FastAPI server at `http://127.0.0.1:8000`, and opens your web browser.

---

## 🧪 Running Automated Tests & Code Quality

```bash
# Run tests with real coverage analysis
python -m pytest -q --cov=src --cov-report=term-missing

# Run Ruff linter
python -m ruff check .
```

---

## 🌐 Deploying to Netlify

Samaroh is configured out of the box for Netlify deployment:

1. Push your code to your GitHub repository (`https://github.com/ashish-29-2003/Event-Planner.git`).
2. In Netlify, click **"Add new site"** → **"Import an existing project"** and select your GitHub repository.
3. Netlify will automatically detect `netlify.toml`:
   - **Publish directory:** `public`
   - **Functions directory:** `netlify/functions`
4. In the Netlify dashboard under **Site configuration > Environment variables**, add:
   - `GEMINI_API_KEY`: Your Google Gemini API Key.
5. Click **Deploy Site**. Every subsequent git push to `main` will automatically build and deploy!

---

## 📚 Complete Project Documentation

Every aspect of the architecture, product requirements, security, and design is documented in `/docs`:

| Document | Description |
|---|---|
| [**PRD.md**](docs/PRD.md) | 13-section Product Requirements Document |
| [**ARCHITECTURE.md**](docs/ARCHITECTURE.md) | System architecture & Mermaid topology diagrams |
| [**AGENTS.md**](docs/AGENTS.md) | Multi-agent prompts, schemas, and hallucination controls |
| [**DECISIONS.md**](docs/DECISIONS.md) | Architecture Decision Records (ADRs) |
| [**TASKS.md**](docs/TASKS.md) | Granular master task board |
| [**TRD.md**](docs/TRD.md) | Technical requirements, performance budgets & dependencies |
| [**APP_FLOW.md**](docs/APP_FLOW.md) | End-to-end Mermaid user journey flowcharts |
| [**UI_UX_FLOW.md**](docs/UI_UX_FLOW.md) | Design system, tokens, wireframes & Sanskrit typography |
| [**BACKEND_SCHEMA.md**](docs/BACKEND_SCHEMA.md) | Pydantic data models, ERD diagram & seed datasets |
| [**SECURITY_AND_TESTING.md**](docs/SECURITY_AND_TESTING.md) | STRIDE threat model, loop defense & testing strategy |
| [**IMPLEMENTATION_PLAN.md**](docs/IMPLEMENTATION_PLAN.md) | Step-by-step build sequence & 3-minute judge demo script |
| [**STAGE_STATUS.md**](docs/STAGE_STATUS.md) | Stage-gated execution tracker |

---

## 📜 License
Distributed under the MIT License. Built with devotion for Indian celebrations.
