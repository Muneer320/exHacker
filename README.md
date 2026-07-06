<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="https://img.shields.io/badge/exHacker-AI%20Product%20Studio-7C3AED?style=for-the-badge&logo=data:image/svg%2bxml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIyNCIgaGVpZ2h0PSIyNCIgdmlld0JveD0iMCAwIDI0IDI0IiBmaWxsPSJub25lIiBzdHJva2U9IndoaXRlIiBzdHJva2Utd2lkdGg9IjIiIHN0cm9rZS1saW5lY2FwPSJyb3VuZCIgc3Ryb2tlLWxpbmVqb2luPSJyb3VuZCI%2bPHBhdGggZD0iTTE1IDN2NEExIDEgMCAwIDAgMTYgOGg0Ii8%2bPHBhdGggZD0iTTE3IDIxaC0yYTIgMiAwIDAgMS0yLTJ2LTJhMiAyIDAgMCAxIDItMmgzYTIgMiAwIDAgMSAyIDJ2MSIvPjxwYXRoIGQ9Ik0xMSAyMUgyYTIgMiAwIDAgMS0yLTJ2LTFhMiAyIDAgMCAxIDItMmgzYTIgMiAwIDAgMSAyIDJ2MiIvPjxwYXRoIGQ9Ik0xMSA1SDJhMiAyIDAgMCAxLTItMlYyYTIgMiAwIDAgMSAyLTJoMTVhMiAyIDAgMCAxIDIgMnYxIi8%2bPC9zdmc%2b&logoColor=white" />
    <img alt="exHacker" src="https://img.shields.io/badge/exHacker-AI%20Product%20Studio-7C3AED?style=for-the-badge" />
  </picture>
</p>

<p align="center">
  <b>From idea to production-ready project blueprint in under 30 seconds.</b><br />
  AI-powered research, architecture, planning, and export — <br />before you write a single line of code.
</p>

<p align="center">
  <a href="https://github.com/Muneer320/exHacker/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License" /></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.11%2B-3776AB.svg" alt="Python" /></a>
  <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/FastAPI-0.111%2B-009688.svg" alt="FastAPI" /></a>
  <a href="https://nextjs.org/"><img src="https://img.shields.io/badge/Next.js-16-000000.svg" alt="Next.js" /></a>
  <a href="https://react.dev/"><img src="https://img.shields.io/badge/React-19-61DAFB.svg" alt="React" /></a>
  <a href="https://www.sqlite.org/"><img src="https://img.shields.io/badge/SQLite-State%20Store-003B57.svg" alt="SQLite" /></a>
  <a href="https://litellm.ai/"><img src="https://img.shields.io/badge/LiteLLM-Router-FF6F00.svg" alt="LiteLLM" /></a>
  <br />
  <a href="https://github.com/Muneer320/exHacker/actions"><img src="https://img.shields.io/github/actions/workflow/status/Muneer320/exHacker/ci.yml?branch=main&label=CI" alt="CI" /></a>
  <a href="https://github.com/Muneer320/exHacker"><img src="https://img.shields.io/github/stars/Muneer320/exHacker?style=social" alt="Stars" /></a>
  <a href="https://github.com/Muneer320/exHacker/commits/main"><img src="https://img.shields.io/github/last-commit/Muneer320/exHacker/main" alt="Last Commit" /></a>
  <a href="https://github.com/Muneer320/exHacker/issues"><img src="https://img.shields.io/github/issues/Muneer320/exHacker" alt="Issues" /></a>
</p>

---

## ✨ What is exHacker?

exHacker is an **AI product studio** that transforms raw ideas into validated, architecturally-sound, presentation-ready project blueprints — before you write a single line of code.

Unlike existing tools that help you *code faster* (Cursor, Claude Code) or *generate apps from prompts* (Bolt, Lovable), exHacker handles the **planning phase** — the 4-8 hours of analysis paralysis, shallow competitor research, architecture guesswork, and panic-rushed presentations that happen *before* and *after* coding.

### The Pipeline

```
┌─────────┐    ┌──────────┐    ┌────────────┐    ┌──────────┐    ┌────────┐
│  Idea   │ →  │ Research │ →  │ Directions  │ →  │Blueprint │ →  │ Export │
│ Input   │    │ Pipeline │    │ & Selection │    │Engine    │    │ Files  │
└─────────┘    └──────────┘    └────────────┘    └──────────┘    └────────┘
     │              │                │                 │               │
  30 seconds      3-5 queries    3 AI-generated      Tech stack,    README.md
  to create       competitors,   product directions  architecture,   blueprint.json
  a project       APIs, OSS      with scores         data model,
                                                      API contracts,
                                                      implementation
                                                      plan
```

---

## 🚀 Quick Start

```bash
# 1. Clone the repository
git clone https://github.com/Muneer320/exHacker.git
cd exHacker

# 2. Start the backend (requires Python 3.11+)
cd backend
uv venv && uv pip install -e ".[dev]"
uv run uvicorn app.main:app --reload
# → http://localhost:8000 | Swagger at /docs

# 3. Start the frontend (requires Node.js 20+)
cd ../frontend
npm install
npm run dev
# → http://localhost:3000

# 4. Open the app in your browser
# Type your idea and see a complete project blueprint in seconds
```

> **No API keys needed for development.** Set `MOCK_AI=true` and `MOCK_RESEARCH=true` in `.env` — the system generates realistic fake data without any external API calls.

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Next.js 16 Frontend                     │
│  ┌─────────┐ ┌──────────┐ ┌──────────┐ ┌──────┐ ┌──────┐   │
│  │ Landing │ │ Projects │ │Research  │ │Blue- │ │Export│   │
│  │ Page    │ │ List     │ │& Direc-  │ │print  │ │      │   │
│  │         │ │ / Detail │ │tions Tab │ │Tab    │ │Modal │   │
│  └─────────┘ └──────────┘ └──────────┘ └──────┘ └──────┘   │
└──────────────────────┬──────────────────────────────────────┘
                       │ HTTP/REST
┌──────────────────────▼──────────────────────────────────────┐
│                    FastAPI Backend                           │
│                                                              │
│  ┌──────────┐  ┌──────────┐  ┌────────────────────────┐    │
│  │ Project  │  │ Research │  │   Blueprint Engine      │    │
│  │ Service  │  │ Service  │  │  ┌──────────────────┐  │    │
│  │ (CRUD +  │  │ (Tavily  │  │  │ Tech Stack       │  │    │
│  │  State   │  │  Search) │  │  │ (Decision Tree)  │  │    │
│  │  Machine)│  │          │  │  ├──────────────────┤  │    │
│  └──────────┘  └──────────┘  │  │ Architecture     │  │    │
│                               │  │ (Templates + AI) │  │    │
│  ┌──────────┐  ┌──────────┐  │  ├──────────────────┤  │    │
│  │ Direction│  │  Export  │  │  │ Data Model       │  │    │
│  │ Generator│  │  Service │  │  │ (Entity Templates)│  │    │
│  │ (AI T2)  │  │(Markdown)│  │  ├──────────────────┤  │    │
│  └──────────┘  └──────────┘  │  │ API Contracts    │  │    │
│                               │  │ (CRUD Templates) │  │    │
│  ┌────────────────────────┐  │  ├──────────────────┤  │    │
│  │    AI Gateway           │  │  │ Implementation  │  │    │
│  │  (LiteLLM + Routing)    │  │  │ Plan (Tasks)    │  │    │
│  └────────────────────────┘  │  └──────────────────┘  │    │
│                               │                        │    │
│  ┌────────────────────────┐  └────────────────────────┘    │
│  │      SQLite Database    │                                │
│  │  (SQLAlchemy 2.0 Async) │                                │
│  └────────────────────────┘                                 │
└─────────────────────────────────────────────────────────────┘
```

### What Uses AI vs What's Deterministic

| Component | Method | SDPD Tier | Why |
|---|---|---|---|
| Research query generation | AI (Tier 1) | `deepseek-v4-flash` | Simple pattern matching |
| Direction generation | AI (Tier 2) | `glm-5.2` | Needs product reasoning |
| Architecture enrichment | AI (Tier 2, optional) | `glm-5.2` | Custom component suggestions |
| Tech stack recommendation | **Decision tree** | Tier 0 — no AI | Rules-based, deterministic |
| Architecture templates | **Pre-designed** | Tier 0 — no AI | 80% fit for standard patterns |
| Data model generation | **Keyword → Entity** | Tier 0 — no AI | Template matching |
| API contract generation | **CRUD patterns** | Tier 0 — no AI | Deterministic templates |
| Implementation plan | **Component → Tasks** | Tier 0 — no AI | Deterministic mapping |
| Markdown/JSON export | **Templates** | Tier 0 — no AI | String formatting |

---

## 🧠 System Philosophy

exHacker is built on the **System Design Philosophy Document (SDPD)** — 35 immutable engineering commandments. The most important:

1. **Never use AI where deterministic software suffices.** Template, compute, or decision tree first.
2. **Cheapest capable model first.** Don't use `glm-5.2` where `deepseek-v4-flash` works.
3. **Every AI output must be editable and cacheable.**
4. **Projects remain portable.** No lock-in. Full export at any time.
5. **Research is cached, architecture is versioned, exports are reproducible.**
6. **Templates over prompts for the 80% case.**
7. **Every project has a maximum AI budget.** Cost per project is a monitored metric.

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | Next.js 16, React 19, TypeScript | UI framework |
| **Styling** | Tailwind CSS + CSS Variables | Dark theme design system |
| **State** | TanStack Query + Zustand | Server + client state |
| **Backend** | FastAPI (Python 3.11+) | REST API server |
| **Database** | SQLite → PostgreSQL | Persistent storage |
| **ORM** | SQLAlchemy 2.0 (async) | Data access layer |
| **AI Gateway** | LiteLLM | Multi-provider model routing |
| **AI Models** | GLM 5.2 (reasoning), DeepSeek V4 Flash (cheap) | via opencode-go provider |
| **Search** | Tavily API (via httpx) | Web research |
| **Auth** | NextAuth.js (v2) | OAuth authentication |
| **Container** | Docker + Docker Compose | Development & deployment |

---

## 📂 Repository Structure

```
exHacker/
├── backend/
│   ├── app/
│   │   ├── ai/              # AI Gateway, Prompt Manager
│   │   ├── api/v1/          # FastAPI route handlers
│   │   ├── core/            # Config, exceptions, logging
│   │   ├── db/              # SQLAlchemy session + migrations
│   │   ├── models/          # SQLAlchemy ORM models
│   │   ├── services/        # Business logic
│   │   │   ├── blueprint/   # Tech stack, architecture, data model, plan, export
│   │   │   ├── project.py   # CRUD + state machine
│   │   │   └── research.py  # Tavily search + caching
│   │   └── main.py          # FastAPI entry point
│   ├── prompts/             # YAML prompt templates
│   ├── templates/           # Architecture templates
│   └── tests/               # pytest suite
├── frontend/
│   ├── src/
│   │   ├── app/             # Next.js pages
│   │   ├── components/      # UI components
│   │   └── services/        # API client
│   └── package.json
├── docs/                    # Architecture documentation
├── docker-compose.yml
└── Makefile
```

---

## 📋 Roadmap

| Phase | Status | Features |
|---|---|---|
| **M0 — Bootstrap** | ✅ Complete | Repo structure, Docker, CI, tooling |
| **M1 — Project Foundation** | ✅ Complete | CRUD, state machine, landing page |
| **M2 — Research Pipeline** | ✅ Complete | AI Gateway, Tavily search, caching |
| **M3 — Direction Generation** | ✅ Complete | AI directions, selection, state transitions |
| **M4 — Blueprint Engine** | ✅ Complete | Tech stack, architecture, data model, plan |
| **M5 — Export** | ✅ Complete | Markdown/JSON download |
| **Auth & Persistence** | 🔜 Planned | Google/GitHub OAuth, user accounts |
| **Team Collaboration** | 🔜 Planned | Shared projects, team workspaces |
| **Pitch Generation** | 🔜 Planned | AI narrative agent for presentations |

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<p align="center">
  <sub>Built with ❤️ by <a href="https://github.com/Muneer320">Muneer Alam</a></sub>
  <br />
  <sub>Powered by <a href="https://opencode.ai">OpenCode</a> · <a href="https://litellm.ai">LiteLLM</a> · <a href="https://nextjs.org">Next.js</a></sub>
</p>
