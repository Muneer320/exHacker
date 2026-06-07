# exHacker

**Your Autonomous Hackathon Co-Founder**

Reduce hackathon planning time from hours to minutes by transforming challenge statements into execution-ready project blueprints.

## Architecture

exHacker is a multi-agent AI system built with:

- **Frontend**: Next.js 15+, React 19, TypeScript, TailwindCSS, shadcn/ui, TanStack Query
- **Backend**: Python 3.12+, FastAPI, LangGraph, LangChain, SQLAlchemy, PostgreSQL
- **Infrastructure**: Docker, Docker Compose

## Getting Started

### Prerequisites

- Node.js 22+
- Python 3.12+
- uv (Python package manager)
- Docker & Docker Compose

### Quick Start

```bash
# Start PostgreSQL
docker compose up -d postgres

# Install and run backend
cd backend
uv sync
uv run uvicorn app.main:app --reload

# Install and run frontend (new terminal)
cd frontend
npm install
npm run dev
```

### Environment Setup

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

## Project Structure

```
/
├── frontend/          # Next.js application
├── backend/           # FastAPI application
├── infrastructure/    # Docker, nginx configs
├── scripts/           # Utility scripts
├── .github/           # CI/CD workflows
└── docs/              # Project documentation
```

## Development

### Backend

```bash
cd backend
uv sync           # Install dependencies
uv run ruff check .     # Lint
uv run mypy app         # Type check
uv run pytest           # Run tests
```

### Frontend

```bash
cd frontend
npm install        # Install dependencies
npm run dev        # Development server
npm run lint       # Lint
npm run typecheck  # Type check
npm run build      # Production build
```
