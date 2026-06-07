# Student / Hackathon Deployment Guide

## Target: $0/Month

This guide provides a complete walkthrough for deploying exHacker at **zero cost** — perfect for hackathon submissions, student projects, and portfolio demonstrations.

---

## Architecture

```
                         ┌─────────────────────┐
                         │   Vercel (Free)      │
                         │   Frontend (Next.js) │
                         └──────────┬──────────┘
                                    │ HTTPS
                         ┌──────────▼──────────┐
                         │  Railway / Render    │
                         │  Backend (FastAPI)   │  $0/month
                         └──────────┬──────────┘
                                    │
              ┌─────────────────────┼─────────────────────┐
              │                     │                     │
   ┌──────────▼──────────┐  ┌──────▼──────┐  ┌──────────▼──────────┐
   │  Supabase / Neon    │  │ Qdrant Free │  │  Grok / Gemini     │
   │  PostgreSQL (500MB) │  │ Vector DB   │  │  LLM (free tier)   │
   └─────────────────────┘  └─────────────┘  └─────────────────────┘
```

---

## Limitations & Constraints

| Resource | Limit | Impact |
|----------|-------|--------|
| Backend RAM | 512 MB (Render) / 500 MB (Railway) | Slower response under concurrent load |
| Backend CPU | Shared / 0.1 vCPU | Agent execution takes longer |
| Backend auto-sleep | 5-15 min inactivity | First request after idle is slow (cold start) |
| Database storage | 500 MB | ~10,000 projects with full state |
| Database connections | 10 regular | Limits concurrent requests |
| Vector DB | 1 GB (Qdrant) | ~500K embeddings |
| LLM rate limits | 15 RPM (Gemini) / 60 RPM (Grok) | Sequential agent execution |
| Frontend bandwidth | 100 GB (Vercel) | ~200K page loads/month |
| Build minutes | 6000 (Vercel) | ~60 builds/month |

### Expected Performance

- **API response time (warm)**: 200-500ms
- **API response time (cold start)**: 3-10s
- **Full agent workflow execution**: 30-120s (depending on LLM provider latency)
- **Concurrent users**: 1-5 without degradation
- **Database throughput**: ~50 queries/second
- **Uptime**: 99.5% (excluding auto-sleep periods)

---

## Step-by-Step Deployment Walkthrough

### Prerequisites

- A GitHub account
- A Vercel account (https://vercel.com)
- A Railway account (https://railway.com) OR Render account (https://render.com)
- A Supabase account (https://supabase.com) OR Neon account (https://neon.tech)
- A Qdrant Cloud account (https://cloud.qdrant.io) (optional)
- A Grok API key from https://x.ai (free) OR Gemini API key from https://ai.google.dev (free)

Estimated time: **30-45 minutes**

---

### Step 1: Fork and Clone the Repository

```bash
# Fork on GitHub, then:
git clone https://github.com/<your-username>/exHacker.git
cd exHacker
```

---

### Step 2: Database Setup (Supabase Free)

1. Go to https://supabase.com and sign up
2. Create a **New Project**
   - Organization: Your personal account
   - Name: `exhacker`
   - Database Password: Generate a strong password (save it)
   - Region: Choose the closest to you
   - Pricing Plan: **Free**
3. Wait for the database to provision (~2 minutes)
4. Go to **Project Settings** > **Database** > **Connection string**
5. Copy the **URI** connection string (the one with `postgresql://`)
6. Transform it for async use:

   **Original (URI mode):**
   ```
   postgresql://postgres:<password>@db.<ref>.supabase.co:6543/postgres
   ```

   **Async URL (DATABASE_URL):**
   ```
   postgresql+asyncpg://postgres:<password>@aws-0-<region>.pooler.supabase.com:5432/postgres?pgbouncer=true&prepared_statement_name=false
   ```

   **Sync URL (DATABASE_SYNC_URL):**
   ```
   postgresql+psycopg2://postgres:<password>@aws-0-<region>.pooler.supabase.com:5432/postgres?pgbouncer=true
   ```

7. Go to **SQL Editor** and run any pending migrations later (or let Alembic do it)

---

### Step 3: LLM API Keys Setup

**Option A: Grok (xAI) — Free, Recommended**

1. Go to https://console.x.ai
2. Sign up with your email or GitHub
3. Generate an API key
4. Save it as `XAI_API_KEY`

**Option B: Gemini (Google) — Free Tier**

1. Go to https://ai.google.dev
2. Click **Get API key**
3. Create a new API key in Google AI Studio
4. Save it as `GEMINI_API_KEY`

**Option C: OpenAI (Paid, Higher Quality)**

1. Go to https://platform.openai.com/api-keys
2. Create a new secret key
3. Add $5 in billing (minimum)
4. Save it as `OPENAI_API_KEY`

---

### Step 4: Backend Deployment (Railway)

1. Go to https://railway.com and sign up (GitHub login recommended)
2. Click **New Project** > **Deploy from GitHub repo**
3. Select your forked `exHacker` repository
4. Railway will auto-detect the project — don't deploy yet
5. Click **Add a service** > **Web Service**
   - Root directory: `backend`
   - Build command: `pip install -e ".[dev]"`
   - Start command: `uvicorn app.main:app --host 0.0.0.0 --port 8000`
6. Configure **Environment Variables** (click the service, then Variables tab):

   ```ini
   ENVIRONMENT=production
   DATABASE_URL=postgresql+asyncpg://postgres:<password>@aws-0-<region>.pooler.supabase.com:5432/postgres?pgbouncer=true&prepared_statement_name=false
   DATABASE_SYNC_URL=postgresql+psycopg2://postgres:<password>@aws-0-<region>.pooler.supabase.com:5432/postgres?pgbouncer=true
   CORS_ORIGINS=["https://exhacker.vercel.app"]
   LLM_PROVIDER=auto
   XAI_API_KEY=xai-<your-key>
   GEMINI_API_KEY=AIza<your-key>
   ```

7. Go to **Deployments** tab and click **Deploy**
8. Wait for the build (~3-5 minutes)
9. Once deployed, copy your Railway URL (e.g., `https://exhacker-backend.up.railway.app`)

---

### Step 4 Alt: Backend Deployment (Render)

1. Go to https://render.com and sign up
2. Click **New +** > **Web Service**
3. Connect your GitHub repository
4. Configure:
   - **Name**: `exhacker-backend`
   - **Root Directory**: `backend`
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -e ".[dev]"`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port 10000`
   - **Plan**: **Free**
5. Click **Advanced** and add environment variables (same as Railway above)
6. Click **Create Web Service**
7. Wait for the build (~3-5 minutes)
8. Copy your Render URL (e.g., `https://exhacker-backend.onrender.com`)

---

### Step 5: Run Database Migrations

**Option A: Via Railway Shell**

```bash
# In Railway dashboard, click on your backend service
# Go to "Shell" tab
pip install -e ".[dev]"
alembic upgrade head
```

**Option B: From Local Machine (if you have PostgreSQL running locally)**

```bash
cd backend

# Temporarily use your Supabase URL
$env:DATABASE_URL = "postgresql+asyncpg://postgres:<password>@aws-0-<region>.pooler.supabase.com:5432/postgres?pgbouncer=true"
$env:DATABASE_SYNC_URL = "postgresql+psycopg2://postgres:<password>@aws-0-<region>.pooler.supabase.com:5432/postgres?pgbouncer=true"
alembic upgrade head
```

**Option C: Add Migration Command to Startup (Temporary)**

Add a startup script that runs migrations on boot:

```python
# In app/main.py lifespan section:
from app.db.migrations import create_tables
await create_tables()
```

This is already handled by the Alembic setup — run migrations once manually.

---

### Step 6: Frontend Deployment (Vercel)

1. Go to https://vercel.com and sign up (GitHub login recommended)
2. Click **Add New** > **Project**
3. Import your forked `exHacker` repository
4. Configure:
   - **Root Directory**: `frontend`
   - **Framework Preset**: Next.js (auto-detected)
   - **Build Command**: `npm run build` (default)
   - **Output Directory**: `.next` (default)
5. Add environment variable:
   - `NEXT_PUBLIC_API_URL` = `https://exhacker-backend.up.railway.app/api/v1` (your Railway URL + /api/v1)
6. Click **Deploy**
7. Wait for the build (~2 minutes)
8. Once deployed, Vercel provides a URL: `https://exhacker.vercel.app`

---

### Step 7: Update CORS

Go back to Railway/Render and update the `CORS_ORIGINS` environment variable:

```ini
CORS_ORIGINS=["https://exhacker.vercel.app"]
```

Then redeploy the backend.

---

### Step 8: Verify Deployment

1. Open your frontend URL (`https://exhacker.vercel.app`)
2. Verify it loads without errors
3. Open browser DevTools > Network tab
4. Submit a challenge and verify API calls succeed
5. Check the `/debug/costs` endpoint:
   ```
   GET https://exhacker-backend.up.railway.app/api/v1/debug/costs
   ```
6. Verify the health endpoint:
   ```
   GET https://exhacker-backend.up.railway.app/api/v1/health
   ```

---

## Switching Providers (Resilience)

If one provider goes down, switch to another with minimal changes.

### Database: Supabase → Neon

1. Create a Neon account and project
2. Copy the Neon connection string:
   ```
   DATABASE_URL=postgresql+asyncpg://<user>:<password>@<endpoint>.neon.tech:5432/neondb?sslmode=require
   DATABASE_SYNC_URL=postgresql+psycopg2://<user>:<password>@<endpoint>.neon.tech:5432/neondb?sslmode=require
   ```
3. Update Railway/Render environment variables
4. Run migrations:
   ```bash
   cd backend
   uv run alembic upgrade head
   ```

### Backend: Railway → Render

1. Create a Render Web Service as described in Step 4 Alt
2. Same environment variables
3. Update `NEXT_PUBLIC_API_URL` on Vercel to the new Render URL
4. Update `CORS_ORIGINS` if needed

### LLM: Grok → Gemini → OpenAI

The `LLM_PROVIDER=auto` mode handles this automatically — just ensure multiple API keys are configured.

If switching to a single provider:
```ini
LLM_PROVIDER=gemini
# or
LLM_PROVIDER=openai
```

### Vector DB: Qdrant → Chroma (Embedded)

Chroma can run in-process without any external service:

```python
# No environment variables needed
import chromadb
client = chromadb.Client()
```

This requires code changes in the service layer — see `backend/app/services/` for integration.

---

## Troubleshooting Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Backend returns 502 | Database connection failed | Verify DATABASE_URL in Railway/Render |
| Frontend shows blank page | CORS misconfiguration | Update CORS_ORIGINS to match frontend URL |
| LLM calls fail | Missing API key | Check that XAI_API_KEY or GEMINI_API_KEY is set |
| Cold start takes too long | Auto-sleep activated | First request after inactivity is slow — normal |
| Database connection refused | Supabase IP restrictions | Enable "Allow all IPs" in Supabase settings |
| Build fails on Vercel | Missing environment variable | Ensure NEXT_PUBLIC_API_URL is set at build time |
| Alembic migration fails | Wrong URL format | Use DATABASE_SYNC_URL (sync, not async) for migrations |
| Quota exceeded | Free tier limit reached | Check usage in the respective dashboard |

---

## Monitoring Your Free Tier Usage

| Service | Dashboard URL | What to Check |
|---------|---------------|---------------|
| Vercel | https://vercel.com/dashboard | Bandwidth, build minutes |
| Railway | https://railway.com/dashboard | Credit usage, uptime |
| Render | https://render.com/dashboard | Monthly hours, bandwidth |
| Supabase | https://supabase.com/dashboard | Database size, connections |
| Qdrant | https://cloud.qdrant.io | Storage usage |
| xAI | https://console.x.ai | Rate limits, total usage |
| Google AI | https://ai.google.dev | Free tier quota remaining |

---

## Quick-Reference: All Environment Variables

```ini
# Backend (Railway/Render)
ENVIRONMENT=production
DATABASE_URL=postgresql+asyncpg://...
DATABASE_SYNC_URL=postgresql+psycopg2://...
CORS_ORIGINS=["https://exhacker.vercel.app"]
LLM_PROVIDER=auto
XAI_API_KEY=xai-...
GEMINI_API_KEY=AIza...

# Frontend (Vercel)
NEXT_PUBLIC_API_URL=https://exhacker-backend.up.railway.app/api/v1
```
