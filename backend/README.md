# exHacker Backend

Python/FastAPI backend for the exHacker hackathon co-pilot.

---

## Architecture

```
backend/
├── api/main.py            # FastAPI app (12+ endpoints)
├── agents/                # 10 AI agent nodes
├── app/
│   ├── core/config.py     # Pydantic Settings
│   ├── services/llm/      # LLM provider chain with fallback
│   ├── research/          # Web research layer
│   ├── artifacts/         # Document generators
│   ├── db/                # SQLAlchemy base
│   └── models/            # ORM models
├── graph/workflow.py      # LangGraph StateGraph (legacy)
├── workflow/              # HITL execution engine
├── schemas/state.py       # ExHackerState (16 domains)
└── tests/                 # 17 tests (pytest)
```

---

## API Overview

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/health` | GET | Health check |
| `/generate` | POST | Legacy full-pipeline generation |
| `/workflow/start` | POST | Start a HITL workflow session |
| `/workflow/continue` | POST | Continue to next workflow step |
| `/workflow/select-idea` | POST | Select idea (HITL step 5) |
| `/workflow/update-output` | POST | Update step output |
| `/workflow/state/{session_id}` | GET | Get current workflow state |
| `/workflow/current-step/{session_id}` | GET | Get current step info |
| `/workflow/output/{session_id}` | GET | Get step output |
| `/workflows/{id}/status` | GET | Workflow status |
| `/workflows/{id}/resume` | POST | Resume paused workflow |
| `/workflows/{id}/restart` | POST | Restart workflow |

---

## Agent System

10 agents connected in a pipeline. Each agent:

1. Reads relevant data from the shared state
2. Calls the LLM provider chain via `generate_with_fallback()`
3. Writes structured output back to state

**Agent List**: `challenge_intelligence`, `problem_analyst`, `opportunity_planner`, `idea_generator`, `idea_selector` (HITL), `idea_validator`, `solution_architect`, `pitch_agent`, `presentation_agent`, `report_generator`

---

## LLM Provider System

Provider chain (automatic fallback):

```
Groq (llama-3.3-70b-versatile)
  └─ on failure → Gemini (gemini-2.0-flash)
                    └─ on failure → Ollama (llama3.2, local)
                                      └─ on failure → OpenAI (gpt-4o)
```

Configure via `LLM_PROVIDER` in `.env`:
- `auto` — enables fallback chain (default)
- `groq` / `gemini` / `ollama` / `openai` — pins a single provider

---

## Workflow Engine

Two workflow systems coexist:

1. **`graph/workflow.py`** — LangGraph StateGraph (legacy `/generate` endpoint)
2. **`workflow/executor.py`** — HITL execution engine (new `/workflow/*` endpoints)

Both share the same agents. The HITL engine is the current target; LangGraph is kept for backward compatibility.

---

## Local Development

```bash
cd backend
uv venv && uv sync --extra dev
cp ../.env.example .env
# Edit .env: set GROQ_API_KEY
uv run uvicorn api.main:app --reload
```

---

## Testing

```bash
uv run pytest . -v       # Run all tests
uv run ruff check .      # Lint
uv run mypy .            # Type check
```

---

## Database

PostgreSQL via SQLAlchemy async. Default connection string is `postgresql+asyncpg://exhacker:exhacker@localhost:5432/exhacker`.

```bash
uv run alembic upgrade head  # Run migrations
uv run alembic revision --autogenerate -m "description"  # Create migration
```

Database is optional for local development — the in-memory session store works without it.

---

## Dependency Management

`pyproject.toml` is the source of truth. `requirements.txt` is maintained for pip users. If using `uv`, the lock file is auto-generated on first sync.
