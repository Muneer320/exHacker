# exHacker — Running & Deployment Guide

> **Target audience:** Student / hackathon developer  
> **Goal:** $0/month deployment  
> **Last updated:** 2026-06-08

---

## Table of Contents

1. [Local Development](#1-local-development)
2. [Environment Variables](#2-environment-variables)
3. [Docker](#3-docker)
4. [Supabase Setup](#4-supabase-setup)
5. [Railway Deployment](#5-railway-deployment)
6. [Vercel Deployment](#6-vercel-deployment)
7. [Groq Setup](#7-groq-setup)
8. [Gemini Setup](#8-gemini-setup)
9. [Ollama Setup](#9-ollama-setup)
10. [Troubleshooting](#10-troubleshooting)

---

## 1. Local Development

### Prerequisites

- Python 3.12+
- Node.js 18+
- Docker Desktop
- `uv` (Python package manager)

### Install uv

```powershell
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# macOS / Linux
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### Backend Setup

```powershell
cd backend
uv sync --extra dev
```

### Start PostgreSQL

```powershell
docker compose up -d postgres
```

### Run Database Migrations

```powershell
cd backend
uv run alembic upgrade head
```

### Start Backend

```powershell
cd backend
uv run uvicorn app.main:app --reload --port 8000
```

### Frontend Setup

```powershell
cd frontend
npm install
npm run dev
```

### Verify

- Backend: http://localhost:8000/api/v1/health
- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:3000

---

## 2. Environment Variables

Copy `.env.example` to `.env` in the project root:

```powershell
cp .env.example .env
```

### Core

| Variable | Default | Description |
|----------|---------|-------------|
| `ENVIRONMENT` | `development` | `development`, `staging`, `production` |
| `LOG_LEVEL` | `INFO` | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `DEBUG` | `true` | Enable debug mode |

### Database

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://exhacker:exhacker@localhost:5432/exhacker` | Async connection string |
| `DATABASE_SYNC_URL` | `postgresql+psycopg2://exhacker:exhacker@localhost:5432/exhacker` | Sync connection string |

### LLM Providers (see sections 7-9 for setup)

| Variable | Default | Description |
|----------|---------|-------------|
| `LLM_PROVIDER` | `auto` | `groq`, `gemini`, `ollama`, `openai`, or `auto` |
| `GROQ_API_KEY` | — | Groq API key (primary) |
| `GROQ_MODEL` | `llama-3.3-70b-versatile` | Groq model name |
| `GEMINI_API_KEY` | — | Google Gemini API key |
| `GEMINI_MODEL` | `gemini-2.0-flash` | Gemini model name |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama server URL |
| `OLLAMA_MODEL` | `llama3.2` | Ollama model name |
| `OPENAI_API_KEY` | — | OpenAI API key (last resort) |

### Auto-Selection Logic

When `LLM_PROVIDER=auto`, the system tries providers in this order:

1. **Groq** — if `GROQ_API_KEY` is set
2. **Gemini** — if `GEMINI_API_KEY` is set
3. **Ollama** — always attempted (no API key needed)
4. **OpenAI** — if `OPENAI_API_KEY` is set

If a provider fails, the next one is tried automatically.

---

## 3. Docker

### Start Everything

```powershell
docker compose up
```

This starts:
- **PostgreSQL** on port 5432
- **Backend** on port 8000
- **Frontend** on port 3000

### Start with Ollama (optional)

Uncomment the `ollama` service in `docker-compose.yml`, then:

```powershell
docker compose up
```

On first run, pull a model inside the container:

```powershell
docker exec exhacker-ollama ollama pull llama3.2
```

### Stop Everything

```powershell
docker compose down
```

### Reset Database

```powershell
docker compose down -v
docker compose up -d postgres
cd backend
uv run alembic upgrade head
```

---

## 4. Supabase Setup

Supabase provides a free PostgreSQL database (500 MB).

### Create an Account

1. Go to [supabase.com](https://supabase.com)
2. Sign up with GitHub
3. Create a new project (free tier)

### Get Connection String

1. In your project dashboard, go to **Project Settings → Database**
2. Find **Connection string → URI**
3. Copy the string and replace `postgresql://` with `postgresql+asyncpg://`

### Update .env

```env
DATABASE_URL=postgresql+asyncpg://postgres:[PASSWORD]@[HOST]:6543/postgres
DATABASE_SYNC_URL=postgresql+psycopg2://postgres:[PASSWORD]@[HOST]:6543/postgres
```

### Run Migrations

```powershell
cd backend
uv run alembic upgrade head
```

### Connection Pooling (recommended for serverless)

Use the **connection pooler** (port 6543) instead of the direct connection (port 5432). Supabase shows both in the connection string section.

---

## 5. Railway Deployment

Railway offers free backend hosting with 500 hours/month and $5 credit.

### Prerequisites

- A GitHub account
- Your project pushed to GitHub

### Deploy Backend

1. Go to [railway.app](https://railway.app)
2. Click **New Project → Deploy from GitHub repo**
3. Select your repository
4. Set the **Root Directory** to `backend`
5. Add a **PostgreSQL** plugin (Railway provisions it automatically)
6. Add environment variables:
   - `ENVIRONMENT=production`
   - `GROQ_API_KEY=your_key`
   - `GEMINI_API_KEY=your_key`
   - `CORS_ORIGINS=["https://your-frontend.vercel.app"]`
7. Set **Start Command** to:
   ```bash
   alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
8. Deploy

> Railway automatically sets `DATABASE_URL` when you add the PostgreSQL plugin. It uses the correct `postgresql://` scheme, so the backend will need to handle this. The current config expects `postgresql+asyncpg://`. If Railway uses standard PostgreSQL URL, you may need to update the backend to auto-detect the scheme.

---

## 6. Vercel Deployment

Vercel offers free frontend hosting.

### Prerequisites

- A GitHub account
- Your project pushed to GitHub

### Deploy Frontend

1. Go to [vercel.com](https://vercel.com)
2. Click **Add New → Project**
3. Import your GitHub repository
4. Set **Root Directory** to `frontend`
5. Add environment variable:
   - `NEXT_PUBLIC_API_URL=https://your-backend.railway.app/api/v1`
6. Deploy

### Environment Variables for Vercel

| Variable | Value |
|----------|-------|
| `NEXT_PUBLIC_API_URL` | `https://[your-backend].railway.app/api/v1` |

---

## 7. Groq Setup

Groq is the **default provider** and offers a free tier.

### Get an API Key

1. Go to [console.groq.com](https://console.groq.com)
2. Sign up with GitHub or Google
3. Go to **API Keys** → **Create API Key**
4. Copy the key

### Update .env

```env
GROQ_API_KEY=gsk_YOUR_KEY_HERE
GROQ_MODEL=llama-3.3-70b-versatile
LLM_PROVIDER=auto
```

### Available Models

| Model | Context | Best for |
|-------|---------|----------|
| `llama-3.3-70b-versatile` | 128K | Default, general use |
| `llama-3.1-8b-instant` | 128K | Faster, simpler tasks |
| `mixtral-8x7b-32768` | 32K | Mixture of experts |

### Rate Limits (Free Tier)

- 30 requests per minute
- 14,400 requests per day
- 6 requests per second

---

## 8. Gemini Setup

Gemini is the **secondary provider** with a generous free tier.

### Get an API Key

1. Go to [makersuite.google.com/app/apikey](https://makersuite.google.com/app/apikey)
2. Click **Create API Key**
3. Copy the key

### Update .env

```env
GEMINI_API_KEY=AIzaYOUR_KEY_HERE
GEMINI_MODEL=gemini-2.0-flash
LLM_PROVIDER=auto
```

> Gemini is used automatically as a fallback if Groq is unavailable.

### Rate Limits (Free Tier)

- 1,500 requests per day
- 30 requests per minute

---

## 9. Ollama Setup

Ollama runs **entirely locally** — zero cost, no API key needed.

### Install Ollama

**Windows:**

```powershell
winget install Ollama.Ollama
```

**macOS / Linux:**

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### Pull a Model

```powershell
ollama pull llama3.2
```

### Start Ollama Server

```powershell
ollama serve
```

### Update .env

```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2
LLM_PROVIDER=auto
```

### Using Ollama with Docker

Uncomment the `ollama` service in `docker-compose.yml`, then:

```powershell
docker compose up -d ollama
docker exec exhacker-ollama ollama pull llama3.2
```

---

## 10. Troubleshooting

### "relation 'projects' does not exist"

Migrations haven't been run:

```powershell
cd backend
uv run alembic upgrade head
```

### PostgreSQL connection refused

Ensure PostgreSQL is running:

```powershell
docker compose up -d postgres
```

### "The asyncio extension requires an async driver"

Your `DATABASE_URL` is using a sync driver (`psycopg2`). Use `postgresql+asyncpg://` instead:

```env
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/db
```

### uv command not found

Install uv:

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### All LLM providers failed

1. Check your API keys are set in `.env`
2. Verify network connectivity to the provider
3. Run with `LOG_LEVEL=DEBUG` to see which provider fails
4. Try Ollama locally for zero-cost debugging
5. Check `GET /api/v1/debug/providers` to see which providers are registered

### CORS errors in frontend

Ensure `CORS_ORIGINS` includes your frontend URL:

```env
CORS_ORIGINS=["http://localhost:3000", "https://your-app.vercel.app"]
```

### Database connection timeout

If using Supabase free tier, the database spins down after 1 week of inactivity. Wake it up by visiting the Supabase dashboard and running a query.

### Port already in use

```powershell
# Find process on port 8000
netstat -ano | findstr :8000
# Kill it
taskkill /PID [PID] /F
```

### Frontend can't reach backend

1. Verify backend is running: http://localhost:8000/api/v1/health
2. Check `NEXT_PUBLIC_API_URL` in frontend `.env.local`
3. For CORS issues, check backend logs

### Error: "No module named 'app'"

Run commands from the `backend/` directory, not the project root.

```powershell
cd backend
uv run uvicorn app.main:app --reload
```
