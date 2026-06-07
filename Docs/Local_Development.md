# Local Development Guide

## Prerequisites

| Tool | Version | Purpose |
|------|---------|---------|
| Python | 3.12+ | Backend runtime |
| Node.js | 18+ (22+ recommended) | Frontend runtime |
| Docker | Latest | PostgreSQL, containerized deployment |
| Docker Compose | Latest | Multi-service orchestration |
| uv | Latest | Python package manager |

### Installing uv

**Windows (PowerShell):**
```powershell
powershell -ExecutionStrategy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Linux / macOS:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Verify installation:
```bash
uv --version
```

---

## Windows Setup (PowerShell)

```powershell
# Clone the repository
git clone <repo-url> && cd exHacker

# Create environment file
Copy-Item .env.example .env

# Start PostgreSQL via Docker
docker compose up -d postgres

# Backend setup
cd backend
uv sync --extra dev
uv run alembic upgrade head
cd ..

# Frontend setup
cd frontend
npm install
cd ..

# Start development servers (use separate terminals)

# Terminal 1: Backend
cd backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev

# Or use the convenience script:
.\scripts\dev.ps1
```

---

## Linux Setup (bash)

```bash
# Clone the repository
git clone <repo-url> && cd exHacker

# Create environment file
cp .env.example .env

# Start PostgreSQL via Docker
docker compose up -d postgres

# Backend setup
cd backend
uv sync --extra dev
uv run alembic upgrade head
cd ..

# Frontend setup
cd frontend
npm install
cd ..

# Start development servers (use separate terminals)

# Terminal 1: Backend
cd backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev
```

---

## macOS Setup (bash)

```bash
# Clone the repository
git clone <repo-url> && cd exHacker

# Create environment file
cp .env.example .env

# Start PostgreSQL via Docker
docker compose up -d postgres

# Backend setup
cd backend
uv sync --extra dev
uv run alembic upgrade head
cd ..

# Frontend setup
cd frontend
npm install
cd ..

# Start development servers (use separate terminals)

# Terminal 1: Backend
cd backend
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev
```

---

## Docker Setup (Full Stack)

Start all services (frontend, backend, PostgreSQL) with a single command:

```bash
docker compose up
```

This starts:
- **postgres**: PostgreSQL 16 Alpine on port 5432
- **backend**: FastAPI on port 8000 with auto-reload
- **frontend**: Next.js on port 3000

Stop everything:
```bash
docker compose down
```

Remove volumes (resets database):
```bash
docker compose down -v
```

---

## Environment Variables

Copy the example file and adjust values:

```bash
# All platforms
cp .env.example .env
```

Key variables to configure:
- `OPENAI_API_KEY` – Required for OpenAI LLM provider
- `XAI_API_KEY` – Required for Grok LLM provider (free, recommended)
- `GEMINI_API_KEY` – Required for Gemini LLM provider (free tier available)
- `DATABASE_URL` – PostgreSQL connection string (Docker default works out of the box)

See [Environment_Variables.md](./Environment_Variables.md) for the full reference.

---

## Running Tests

```bash
# Backend tests
cd backend
uv run pytest

# With coverage
uv run pytest --cov=app --cov-report=term-missing

# Run specific test file
uv run pytest tests/test_health.py

# Frontend tests (if configured)
cd frontend
npm run test        # if test framework is configured
```

---

## Running Linters

```bash
# Backend linting
cd backend
uv run ruff check .
uv run mypy app

# Backend linting with auto-fix
uv run ruff check . --fix

# Frontend linting
cd frontend
npm run lint
npm run typecheck
```

---

## API Documentation

Once the backend is running, interactive API docs are available at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

---

## Debug Endpoints

The backend exposes debug endpoints (enabled in development):

```bash
# View LLM cost summary
curl http://localhost:8000/api/v1/debug/costs

# View configured LLM providers
curl http://localhost:8000/api/v1/debug/providers

# Reset cost tracker
curl -X POST http://localhost:8000/api/v1/debug/costs/reset

# View workflow state for a project
curl http://localhost:8000/api/v1/debug/workflow/<project-id>
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `uv` command not found | Install uv via the script above, then restart your terminal |
| PostgreSQL connection refused | Ensure Docker is running and `docker compose up -d postgres` completed |
| Port 8000 in use | Change backend port: `uv run uvicorn app.main:app --reload --port 8001` |
| Port 3000 in use | Next.js will auto-select next available, or set `PORT=3001` |
| Alembic migration fails | Ensure PostgreSQL is healthy: `docker compose ps` |
| `langchain` import errors | Run `uv sync --extra dev` to install all dependencies |
| Permission denied on scripts | `chmod +x scripts/*.sh` on Linux/macOS |
