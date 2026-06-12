# Codebase Audit

> Generated: 2026-06-11
> Purpose: Onboarding document for engineers and AI agents

---

## Current Architecture

exHacker v2 uses a **backend-for-frontend** pattern with a Python/FastAPI API server and a Next.js/React frontend.

### Backend Structure

```
backend/
├── agents/          # 10 AI agent nodes (workflow steps)
├── api/             # FastAPI application (routes, middleware)
├── app/
│   ├── artifacts/   # Generator services (README, PRD, pitch, etc.)
│   ├── core/        # App configuration (pydantic-settings)
│   ├── db/          # SQLAlchemy base
│   ├── models/      # SQLAlchemy ORM models
│   ├── research/    # Research layer (competitor, API, OSS search)
│   └── services/
│       └── llm/     # LLM provider system (Groq→Gemini→Ollama→OpenAI)
├── graph/           # LangGraph StateGraph (legacy /generate compat)
├── locales/         # i18n (en.json)
├── schemas/         # Pydantic state models (ExHackerState, etc.)
├── tests/           # Pytest test suite
├── workflow/        # HITL execution engine (10-step pipeline)
├── pyproject.toml   # Package config, ruff, mypy, pytest
└── requirements.txt # Pip dependencies (pyproject.toml is source of truth)
```

### Frontend Structure

```
frontend/
├── src/
│   ├── app/           # Next.js App Router pages
│   │   ├── page.tsx           # Landing/hero
│   │   ├── generate/page.tsx  # Generate flow
│   │   ├── new-project/page.tsx
│   │   ├── results/page.tsx
│   │   └── workflow/page.tsx  # 10-step HITL workflow
│   ├── components/     # React components
│   │   ├── ui/         # shadcn-style primitives
│   │   └── *.tsx       # Domain components
│   ├── lib/            # API client, utilities
│   ├── types/          # TypeScript interfaces
│   ├── stores/         # State stores (scaffold)
│   └── features/       # Feature modules (scaffold)
├── package.json
└── tsconfig.json
```

---

## Workflow Overview

The system runs a **10-step Human-in-the-Loop (HITL) pipeline**:

| Step | Agent/Node | Description |
|------|-----------|-------------|
| 1 | `challenge_intelligence` | Analyzes hackathon challenge |
| 2 | `problem_analyst` | Decomposes problem statement |
| 3 | `opportunity_planner` | Identifies opportunities |
| 4 | `idea_generator` | Generates solution ideas |
| 5 | `idea_selector` | User selects best idea (HITL) |
| 6 | `idea_validator` | Validates selected idea |
| 7 | `solution_architect` | Designs architecture |
| 8 | `pitch_agent` | Generates pitch materials |
| 9 | `presentation_agent` | Creates presentation |
| 10 | `report_generator` | Final report + export |

Each agent uses `generate_with_fallback()` from `app/services/llm/service.py`.

---

## State Flow

Central state model: `ExHackerState` (`schemas/state.py`)

- **TypedDict** structure with 16 optional domains
- Each agent reads from and writes to specific state keys
- Workflow is driven by `WorkflowState` TypedDict in `workflow/steps.py`
- In-memory session store (`workflow/session_store.py`) manages active sessions
- Legacy `LangGraph` StateGraph (`graph/workflow.py`) provides backward compatibility for `/generate`

---

## Major Modules

### LLM Provider System (`app/services/llm/`)

- Abstract base → GroqProvider → GeminiProvider → OllamaProvider → OpenAIProvider
- Fallback chain: tries each provider in order on failure
- `LLMService` singleton with `generate_with_fallback()`
- `CostTracker` collects usage metrics

### Research Layer (`app/research/`)

- `ResearchCoordinator` orchestrates searches
- `CompetitorSearch` - web search for competing solutions
- `ApiDiscovery` - finds relevant APIs
- `OpenSourceDiscovery` - discovers OSS libraries

### Artifact Generators (`app/artifacts/`)

- `ReadmeGenerator`, `ArchitectureGenerator`, `PRDGenerator`
- `ImplementationGuideGenerator`, `PitchGenerator`
- `ExportService` - zip export of all generated artifacts

### Workflow Engine (`workflow/`)

- `executor.py` - HITL execution engine with session management
- `session_store.py` - In-memory store (placeholder for Redis/PostgreSQL)
- `steps.py` - 10-step pipeline definition

---

## Cleanup Decisions Made

### Removed Items

| Item | Reason |
|------|--------|
| `backend/.mypy_cache/` | Generated cache |
| `backend/.pytest_cache/` | Generated cache |
| `backend/.ruff_cache/` | Generated cache |
| `backend/.venv/` | Virtual env (locked by process, gitignored) |
| `backend/exhacker.egg-info/` | Build artifact |
| `backend/alembic/` | Only had `__pycache__` — no source `.py` files |
| `backend/app/agents/` | Dead dir — only `__pycache__`, no source |
| `backend/app/api/` | Dead dir — only `__pycache__`, no source |
| `backend/app/schemas/` | Dead dir — only `__pycache__`, no source |
| `backend/app/workflows/` | Dead dir — only `__pycache__`, no source |
| `backend/app/prompts/` | Dead dir — only `__pycache__`, no source |
| `frontend/.next/` | Next.js build output |
| `frontend/node_modules/` | Node deps (locked by process, gitignored) |
| `frontend/src/utils/` | Empty directory |

### Updated Items

| Item | Change |
|------|--------|
| `.gitignore` | Added `.ruff_cache/`, `*.egg-info/`, `exports/`, `artifacts/`, `generated/`, `tmp/`, alembic cache patterns |
| `infrastructure/README.md` | Added placeholder to document intent (dir was empty) |

### Kept Items

| Item | Rationale |
|------|-----------|
| `backend/requirements.txt` | No `uv.lock` exists — pip is current package manager. `pyproject.toml` remains source of truth for dev. |
| `backend/graph/` | Kept for backward compatibility with legacy `/generate` endpoint |
| `start.bat` | Convenience startup script |

---

## Technical Debt

### High Priority

1. **No database persistence** — sessions are in-memory only (`workflow/session_store.py`). Will be lost on restart.
2. **Missing Alembic migrations** — `backend/alembic/` had no source files (only cache). Migration system needs to be re-initialized.
3. **CI depends on `.venv`** — uses `uv run` but no `uv.lock` exists. Works because `uv` auto-generates lock on first run.

### Medium Priority

4. **`graph/workflow.py` vs `workflow/executor.py`** — Two workflow systems exist. Should converge on one after legacy `/generate` is deprecated.
5. **Frontend `next build` fails** — missing `@tailwindcss/postcss` dependency (pre-existing setup issue).
6. **In-memory session store** — no TTL/eviction policy. Could OOM under load.
7. **Locale system** — `locales/en.json` exists with only English. i18n is incomplete.

### Low Priority

8. **Frontend `src/stores/` and `src/features/`** — scaffold directories with only `index.ts` re-exports.
9. **`frontend/src/app` pages** — some pages (like `generate/` and `new-project/`) may overlap with the new `workflow/` page.
10. **No screenshots** — README placeholder sections reference screenshots that don't exist yet.

---

## Future Cleanup Candidates

- Consolidate `backend/graph/` into `backend/workflow/` when `/generate` endpoint is retired
- Replace in-memory session store with Redis-backed store
- Re-initialize Alembic and create initial migration
- Remove `requirements.txt` once `uv.lock` is committed and uv is the sole package manager
- Add pre-commit hooks for ruff + mypy
- Remove dead pages from frontend app router once HITL workflow is fully implemented
