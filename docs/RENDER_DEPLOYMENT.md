# Render Dedicated API Host Deployment Guide for Samaroh (समारोह)

This guide documents the setup and configuration of Samaroh's containerized Python FastAPI ASGI backend on **Render** (`render.com`), fulfilling **ADR-014** and resolving defect **DEF-01**.

---

## 1. Architecture Context

- **Frontend:** Static HTML/JS/CSS hosted on Netlify Edge CDN (`public/`).
- **Backend API:** Containerized Python 3.13 FastAPI backend deployed as a Web Service on Render.
- **Proxy Rewrite:** Netlify routes `/api/*` to `https://<render-service-name>.onrender.com/api/:splat` via HTTP 200 rewrite rule in `public/_redirects`.

---

## 2. Deployment Steps on Render

### Option A: Using Render Blueprints (`render.yaml`)
1. Log in to [dashboard.render.com](https://dashboard.render.com).
2. Click **New +** -> **Blueprint**.
3. Connect repository: `ashish-29-2003/Event-Planner`, branch `main`.
4. Render detects `render.yaml` automatically and configures the `samaroh-api` Docker service.
5. Provide the secret environment variables when prompted (see Section 3 below).
6. Click **Apply**.

### Option B: Manual Web Service Setup
1. Log in to [dashboard.render.com](https://dashboard.render.com).
2. Click **New +** -> **Web Service**.
3. Connect repository: `ashish-29-2003/Event-Planner`, branch `main`.
4. Configure service settings:
   - **Name:** `samaroh-api` (or custom name)
   - **Language:** **Docker** (Render uses the root `Dockerfile`)
   - **Region:** Singapore (`singapore`) or Frankfurt / Oregon
   - **Instance Type:** Free
   - **Health Check Path:** `/api/health`
5. Configure Environment Variables as specified below.
6. Click **Deploy Web Service**.

---

## 3. Environment Variables & Secrets Reference

Configure these in Render -> **Environment**:

| Variable | Value / Description | Required? |
| :--- | :--- | :--- |
| `ENVIRONMENT` | `production` | Yes |
| `STORAGE_BACKEND` | `firestore` | Yes |
| `GEMINI_MODEL` | `gemini-2.0-flash` | Yes |
| `FIREBASE_PROJECT_ID` | `samaroh-celebrations` | Yes |
| `ENABLE_AUTH_ENFORCEMENT` | `true` | Yes |
| `ENABLE_APP_CHECK` | `true` | Yes |
| `APP_CHECK_MODE` | `monitor` (or `enforcing` once reCAPTCHA registered) | Yes |
| `APP_CHECK_DEV_BYPASS` | `false` | Yes |
| `GEMINI_API_KEY` | *(Your Google Gemini API Key from Google AI Studio)* | **Secret** |
| `FIREBASE_SERVICE_ACCOUNT_JSON` | *(Raw contents of your Firebase Service Account JSON key)* | **Secret** |
| `CORS_ORIGINS` | Netlify domain (e.g. `https://utsav-ai.netlify.app,https://samaroh-celebrations.web.app`) | Yes |
| `GOOGLE_MAPS_API_KEY` | *(Optional Google Maps Places API key)* | Optional |

---

## 4. Verification Check

Once deployment is marked **Live** on Render:
1. Probe the health endpoint:
   ```bash
   curl -s https://<your-service>.onrender.com/api/health
   ```
2. Expected response:
   ```json
   {
     "status": "healthy",
     "version": "1.0.0",
     "storage": "firestore"
   }
   ```
3. Copy the live Render service URL (e.g. `https://samaroh-api.onrender.com`) to `public/_redirects` on Netlify.
