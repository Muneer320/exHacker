# ⚙️ exHacker Backend Engine

[![FastAPI](https://img.shields.io/badge/FastAPI-0.111%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.0-red.svg)](https://www.sqlalchemy.org/)
[![Aiosqlite](https://img.shields.io/badge/Aiosqlite-Async%20SQLite-blue.svg)](#)
[![Ruff](https://img.shields.io/endpoint?url=https://raw.githubusercontent.com/astral-sh/ruff/main/assets/badge/v2.json)](https://github.com/astral-sh/ruff)

This is the FastAPI backend for **exHacker**. It orchestrates the multi-agent system using **LangGraph**, persists workflow states to SQLite, rotates LLM keys, and manages mock execution fallbacks.

---

## 📂 Backend Project Structure

```text
backend/
├── app/
│   ├── agents/          # Agent framework and individual agents
│   │   ├── base.py      # Abstract agent foundation with metrics logger
│   │   └── *.py         # 10 specialized agents (challenge, problem, etc.)
│   ├── api/             # FastAPI HTTP routes & entrypoints
│   │   ├── main.py      # FastAPI application setup
│   │   └── v1/          # v1 Routers (projects, workflows)
│   ├── core/            # Configuration management
│   │   └── config.py    # Env variables validation via pydantic-settings
│   ├── db/              # Database session manager
│   │   └── session.py   # Lifespan managed async session factory
│   ├── models/          # Declarative SQLAlchemy models
│   │   ├── project.py   # Project metadata table
│   │   ├── workflow.py  # Workflow state JSON storage table
│   │   └── agent_run.py # Individual LLM query performance logging table
│   ├── schemas/         # Pydantic data schemas
│   │   ├── state.py     # Main graph state & sub-stage schemas
│   │   └── api.py       # API input/output validation payloads
│   └── services/        # Third-party integrations
│       ├── llm/         # LLM providers (Groq, Gemini, OpenAI, Ollama)
│       └── workflow/    # LangGraph workflow compiler & nodes definition
├── tests/               # Pytest testing suites (conftest, agents, workflow)
├── pyproject.toml       # Python package configuration
└── uv.lock              # Lockfile
```

---

## 🔧 Installation & Running

### 1. Requirements
*   Python 3.10+
*   [uv](https://github.com/astral-sh/uv) (recommended) or virtualenv with pip.

### 2. Set Up Environment Variables
Create a `.env` file from the example:
```bash
cp .env.example .env
```
Configure your keys:
```ini
# Key rotation (comma-separated list)
GROQ_API_KEY=groq_key_1,groq_key_2

# Fallbacks
GEMINI_API_KEY=gemini_key
OPENAI_API_KEY=openai_key

# Research
MOCK_RESEARCH=True
SEARCH_API_KEY=tavily_key
```

### 3. Start Development Server
```bash
# Using uv (fastest)
uv run uvicorn app.api.main:app --reload

# Server runs on: http://localhost:8000
# OpenAPI Interactive docs: http://localhost:8000/docs
```

---

## 📝 API Endpoints

| Method | Endpoint | Description | Payload |
| :--- | :--- | :--- | :--- |
| **GET** | `/health` | Server status check | None |
| **POST** | `/api/v1/projects` | Initialize a project and workflow state | `ProjectCreate` |
| **GET** | `/api/v1/projects` | List all projects | None |
| **GET** | `/api/v1/projects/{id}` | Retrieve specific project details | None |
| **POST** | `/api/v1/workflows/{id}/start` | Start or resume execution from the last node | None |
| **GET** | `/api/v1/workflows/{id}` | Check workflow status & metrics | None |
| **GET** | `/api/v1/workflows/{id}/state` | Fetch full serialized JSON graph state | None |
| **POST** | `/api/v1/projects/{id}/ideas/select` | Lock in the selected idea ID and resume graph | `IdeaSelect` |
| **GET** | `/api/v1/projects/{id}/exports` | Fetch structured outputs (README, architecture, slide content) | None |

---

## 🧪 Testing

We use `pytest` and `pytest-asyncio` to validate our models, agents, and the graph. The DB schema is dynamically created and dropped in-memory for testing isolation.

Run all tests:
```bash
uv run pytest
```

---

## 🛡️ Key Rotation & Resiliency
Our LLM orchestration engine (`app/services/llm/`) leverages:
1.  **Multiple API Key Rotation**: Splits Groq keys by comma and rotates when hitting rate limits (HTTP 429).
2.  **Tiered Provider Fallback**: Groq (Llama-3) ➔ Gemini (1.5 Flash) ➔ OpenAI (GPT-4o-mini) ➔ Local Ollama.
3.  **Mock Fallback**: If no keys are provided, the system dynamically populates mock schemas tailored to the project input, ensuring the app remains demo-ready.
