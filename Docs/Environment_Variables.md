# Environment Variables Reference

All environment variables are read from a `.env` file in the project root. The backend uses `pydantic-settings` to load them via `app/core/config.py`.

---

## Core Application

| Variable | Description | Default | Required | Example |
|----------|-------------|---------|----------|---------|
| `ENVIRONMENT` | Runtime environment | `development` | No | `production`, `staging`, `development` |
| `LOG_LEVEL` | Logging verbosity | `INFO` | No | `DEBUG`, `INFO`, `WARNING`, `ERROR` |
| `DEBUG` | Enable debug mode | `True` | No | `True`, `False` |
| `APP_NAME` | Application name | `exHacker` | No | `exHacker` |
| `APP_VERSION` | Application version | `0.1.0` | No | `1.0.0` |
| `API_PREFIX` | API route prefix | `/api/v1` | No | `/api/v1` |

---

## Database

| Variable | Description | Default | Required | Example |
|----------|-------------|---------|----------|---------|
| `DATABASE_URL` | Async PostgreSQL connection string | `postgresql+asyncpg://exhacker:exhacker@localhost:5432/exhacker` | Yes | `postgresql+asyncpg://user:pass@host:5432/db` |
| `DATABASE_SYNC_URL` | Sync PostgreSQL connection string (for Alembic) | `postgresql+psycopg2://exhacker:exhacker@localhost:5432/exhacker` | Yes | `postgresql+psycopg2://user:pass@host:5432/db` |
| `DATABASE_ECHO` | Log all SQL queries | `false` | No | `true`, `false` |
| `DATABASE_POOL_SIZE` | Connection pool size | `10` | No | `10` |
| `DATABASE_MAX_OVERFLOW` | Max overflow connections | `20` | No | `20` |

### Supabase (Neon-compatible) Connection Strings

```
DATABASE_URL=postgresql+asyncpg://postgres:<password>@aws-0-<region>.pooler.supabase.com:5432/postgres?pgbouncer=true
DATABASE_SYNC_URL=postgresql+psycopg2://postgres:<password>@aws-0-<region>.pooler.supabase.com:5432/postgres?pgbouncer=true
```

### Neon Connection Strings

```
DATABASE_URL=postgresql+asyncpg://<user>:<password>@<endpoint>.neon.tech:5432/neondb?sslmode=require
DATABASE_SYNC_URL=postgresql+psycopg2://<user>:<password>@<endpoint>.neon.tech:5432/neondb?sslmode=require
```

---

## LLM Providers

The `LLM_PROVIDER` variable controls which provider is used. The system supports automatic fallback when one provider fails.

| Variable | Description | Default | Required | Example |
|----------|-------------|---------|----------|---------|
| `LLM_PROVIDER` | LLM provider selection strategy | `auto` | No | `openai`, `grok`, `gemini`, `ollama`, `auto` |
| `OPENAI_API_KEY` | OpenAI API key | empty | Conditional | `sk-...` |
| `OPENAI_MODEL` | OpenAI model name | `gpt-4o` | No | `gpt-4o`, `gpt-4o-mini` |
| `OPENAI_TEMPERATURE` | Response randomness (0.0-2.0) | `0.7` | No | `0.5` |
| `OPENAI_MAX_TOKENS` | Max tokens per response | `4096` | No | `8192` |
| `XAI_API_KEY` | xAI (Grok) API key | empty | Conditional | `xai-...` |
| `XAI_MODEL` | Grok model name | `grok-2-latest` | No | `grok-2-latest` |
| `GEMINI_API_KEY` | Google Gemini API key | empty | Conditional | `AIza...` |
| `GEMINI_MODEL` | Gemini model name | `gemini-2.0-flash` | No | `gemini-2.0-flash`, `gemini-2.0-pro` |
| `OLLAMA_BASE_URL` | Ollama server URL | `http://localhost:11434` | No | `http://192.168.1.100:11434` |
| `OLLAMA_MODEL` | Ollama model name | `llama3.2` | No | `llama3.2`, `mistral`, `codellama` |

### LLM_PROVIDER Selection

| Value | Behavior |
|-------|----------|
| `auto` | (Default) Automatically selects providers in priority order based on available API keys: Grok → Gemini → OpenAI |
| `openai` | Forces OpenAI only |
| `grok` | Forces xAI/Grok only |
| `gemini` | Forces Google Gemini only |
| `ollama` | Forces local Ollama (no API key needed, must have Ollama running) |

### Provider Priority in Auto Mode

When `LLM_PROVIDER=auto`, the backend checks for API keys and uses them in this priority:

1. **Grok** (`XAI_API_KEY`) – Free, highest priority
2. **Gemini** (`GEMINI_API_KEY`) – Free tier available, second priority
3. **OpenAI** (`OPENAI_API_KEY`) – Paid, last resort

If no API keys are configured, the system falls back to a bare OpenAI client (which will fail if no key is set). For truly offline development, set `LLM_PROVIDER=ollama` and run Ollama locally.

---

## CORS

| Variable | Description | Default | Required | Example |
|----------|-------------|---------|----------|---------|
| `CORS_ORIGINS` | Allowed CORS origins (JSON array) | `["http://localhost:3000"]` | Yes | `["https://exhacker.vercel.app"]` |
| `CORS_ALLOW_CREDENTIALS` | Allow credentials in CORS | `True` | No | `True` |
| `CORS_ALLOW_METHODS` | Allowed HTTP methods | `["*"]` | No | `["GET", "POST"]` |
| `CORS_ALLOW_HEADERS` | Allowed HTTP headers | `["*"]` | No | `["Content-Type", "Authorization"]` |

**Examples:**

```ini
# Development (single origin)
CORS_ORIGINS=["http://localhost:3000"]

# Production (multiple origins)
CORS_ORIGINS=["https://exhacker.vercel.app", "https://exhacker.railway.app", "https://app.exhacker.dev"]

# Wildcard (not recommended for production)
CORS_ORIGINS=["*"]
```

---

## Agent Configuration

| Variable | Description | Default | Required | Example |
|----------|-------------|---------|----------|---------|
| `AGENT_TIMEOUT_SECONDS` | Max execution time per agent | `120` | No | `300` |
| `AGENT_MAX_RETRIES` | Max retries on agent failure | `2` | No | `3` |
| `WORKFLOW_PROGRESS_POLL_INTERVAL` | Poll interval for workflow progress (seconds) | `0.5` | No | `1.0` |

---

## Monitoring

| Variable | Description | Default | Required | Example |
|----------|-------------|---------|----------|---------|
| `SENTRY_DSN` | Sentry error tracking DSN | empty | No | `https://key@o123.ingest.us.sentry.io/123` |
| `OTLP_ENDPOINT` | OpenTelemetry endpoint | empty | No | `http://otel-collector:4318` |

---

## Storage

| Variable | Description | Default | Required | Example |
|----------|-------------|---------|----------|---------|
| `UPLOAD_DIR` | Upload directory path | `uploads` | No | `/data/uploads` |
| `EXPORT_DIR` | Export directory path | `exports` | No | `/data/exports` |

---

## Docker / Compose-Only Variables

These are used by `docker-compose.yml` for the PostgreSQL container and do not directly affect the backend application.

| Variable | Description | Default | Required | Example |
|----------|-------------|---------|----------|---------|
| `POSTGRES_USER` | PostgreSQL username | `exhacker` | No | `exhacker` |
| `POSTGRES_PASSWORD` | PostgreSQL password | `exhacker` | No | `secure-password-123` |
| `POSTGRES_DB` | PostgreSQL database name | `exhacker` | No | `exhacker` |
| `POSTGRES_PORT` | PostgreSQL host port | `5432` | No | `5432` |
| `BACKEND_PORT` | Backend host port | `8000` | No | `8000` |
| `FRONTEND_PORT` | Frontend host port | `3000` | No | `3000` |

---

## Frontend Variables

| Variable | Description | Default | Required | Example |
|----------|-------------|---------|----------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL (public, bundled into client) | `http://localhost:8000/api/v1` | Yes | `https://exhacker-api.railway.app/api/v1` |

This is the **only** frontend environment variable. It must be set at build time on Vercel/Netlify/Cloudflare Pages.

---

## Complete .env.example

```ini
# exHacker Configuration
ENVIRONMENT=development
LOG_LEVEL=INFO
DEBUG=true

# Application
APP_NAME=exHacker
APP_VERSION=0.1.0
API_PREFIX=/api/v1

# Database
DATABASE_URL=postgresql+asyncpg://exhacker:exhacker@localhost:5432/exhacker
DATABASE_SYNC_URL=postgresql+psycopg2://exhacker:exhacker@localhost:5432/exhacker
DATABASE_ECHO=false
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# LLM Provider Selection
LLM_PROVIDER=auto

# OpenAI
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4o
OPENAI_TEMPERATURE=0.7
OPENAI_MAX_TOKENS=4096

# xAI (Grok) - Free tier available
XAI_API_KEY=
XAI_MODEL=grok-2-latest

# Google Gemini - Free tier available
GEMINI_API_KEY=
GEMINI_MODEL=gemini-2.0-flash

# Ollama (local, zero-cost)
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.2

# CORS
CORS_ORIGINS=["http://localhost:3000"]
CORS_ALLOW_CREDENTIALS=True
CORS_ALLOW_METHODS=["*"]
CORS_ALLOW_HEADERS=["*"]

# Agent Configuration
AGENT_TIMEOUT_SECONDS=120
AGENT_MAX_RETRIES=2

# Monitoring
SENTRY_DSN=
OTLP_ENDPOINT=

# Storage
UPLOAD_DIR=uploads
EXPORT_DIR=exports
```
