<p align="center">
  <img src="https://img.shields.io/badge/exHacker-AI%20Product%20Studio-3D7CF6?style=for-the-badge" alt="exHacker" width="320" />
</p>

<p align="center">
  <b>From hackathon idea to complete strategy in under 3 minutes.</b><br />
  7 AI specialists research, analyse, architect, and document your project<br />
  <i>before you write a single line of code.</i>
</p>

<p align="center">
  <a href="https://github.com/Muneer320/exHacker/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License" /></a>
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/python-3.11%2B-3776AB.svg" alt="Python" /></a>
  <a href="https://fastapi.tiangolo.com/"><img src="https://img.shields.io/badge/FastAPI-0.111%2B-009688.svg" alt="FastAPI" /></a>
  <a href="https://nextjs.org/"><img src="https://img.shields.io/badge/Next.js-16-000000.svg" alt="Next.js" /></a>
  <a href="https://react.dev/"><img src="https://img.shields.io/badge/React-19-61DAFB.svg" alt="React" /></a>
  <br />
  <a href="https://github.com/Muneer320/exHacker/actions"><img src="https://img.shields.io/github/actions/workflow/status/Muneer320/exHacker/ci.yml?branch=main&label=CI" alt="CI" /></a>
  <a href="https://github.com/Muneer320/exHacker"><img src="https://img.shields.io/github/stars/Muneer320/exHacker?style=social" alt="Stars" /></a>
  <a href="https://github.com/Muneer320/exHacker/commits/main"><img src="https://img.shields.io/github/last-commit/Muneer320/exHacker/main" alt="Last Commit" /></a>
</p>

<p align="center">
  <a href="https://exhacker-frontend.vercel.app/">🚀 Live Demo</a>
  ·
  <a href="#-architecture">Architecture</a>
  ·
  <a href="#-specialists">Specialists</a>
  ·
  <a href="#-quick-start">Quick Start</a>
</p>

---

## ✨ What is exHacker?

exHacker is an **AI-powered hackathon strategy engine** built by participants, for participants. Paste any hackathon challenge and watch 7 AI specialists work together to produce:

- 🧠 **Challenge Intelligence** — Deep analysis of constraints, opportunities, and strategy
- 🔍 **Research** — 10-category market research with synthesis
- 🎯 **Competitor Analysis** — Gap analysis, white space, differentiation opportunities
- 💡 **Scored Ideas** — 5 differentiated concepts with 8-dimension scoring
- 🏗️ **Architecture Blueprint** — System design with Mermaid diagrams, API contracts, trade-offs
- 📝 **Documentation Package** — PRD, README, tech stack, API docs, database design, pitch guide
- ⏱ **Decision Timeline** — Every decision tracked and explainable

### 🎯 Live Demo

**Frontend:** https://exhacker-frontend.vercel.app/  
**API:** https://exhacker-backend.vercel.app/health  
**API Docs:** https://exhacker-backend.vercel.app/docs  

---

## 🏆 WOW Features

| Feature | Description |
|---|---|
| **Live Architecture Evolution** | Watch your system design being built component-by-component |
| **Project Readiness Score** | Real-time 0-100 score with 5 sub-scores in the sidebar |
| **Command Palette** | Ctrl+K to navigate across all workspace pages |
| **Idea Comparison** | Side-by-side table comparing 10 scores, features, and effort |
| **Mermaid Diagrams** | All architecture diagrams rendered as interactive SVGs |
| **GitHub-Style Docs Viewer** | Rendered markdown with syntax highlighting and inline Mermaid |

---

## 🏗 Architecture

```
Frontend (Next.js 16 + React 19)
├── /app        → 12 pages (landing, workspace × 10, projects)
├── /components → 4 domains (pipeline, shared, diagrams, markdown)
└── /services   → API client with mock fallback

Backend (FastAPI + Python 3.11)
├── /api/v1     → 10 routers, 40 endpoints
├── /services
│   ├── /specialists  → 7 AI specialist implementations
│   └── /shared       → Memory, journal, context API
└── /models     → 10 SQLAlchemy models
```

---

## 🧠 Specialists

| # | Specialist | Purpose | Model Tier |
|---|---|---|---|
| S1 | **Challenge Analyst** | Extract themes, constraints, opportunities | Tier 2 (glm-5.2) |
| S2 | **Research Specialist** | 10-category market research | Tier 1 (deepseek) + Tier 2 |
| S3 | **Competitor Analyst** | Gap analysis, white space, differentiation | Tier 2 |
| S4 | **Shared Intelligence** | Memory + decision journal + context API | Tier 0 (deterministic) |
| S5 | **Idea Generator** | 5 scored ideas with self-critique | Tier 2 × 2 |
| S7 | **Solution Architect** | Full technical blueprint with Mermaid | Tier 2 |
| S13 | **Documentation Writer** | 10 deterministic document templates | Tier 0 (templates) |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Node.js 22+
- SQLite (bundled with Python)

### Backend

```bash
cd backend
python -m venv .venv && source .venv/bin/activate
pip install -e .
# Mock mode (no AI API key needed):
MOCK_AI=true MOCK_RESEARCH=true uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Environment Variables

| Variable | Required | Default | Purpose |
|---|---|---|---|
| `MOCK_AI` | No | `false` | Bypass AI APIs with mock responses |
| `MOCK_RESEARCH` | No | `false` | Bypass search APIs with mock data |
| `NEXT_PUBLIC_API_URL` | No | `http://localhost:8000/api/v1` | Backend URL for frontend |

---

## 🧪 Testing

```bash
# Backend
cd backend && pytest -v

# Frontend (type check)
cd frontend && npx tsc --noEmit

# CI (GitHub Actions)
# Triggered automatically on push to main
```

---

## 🛠 Tech Stack

| Layer | Technology |
|---|---|
| **Frontend** | Next.js 16, React 19, TypeScript, lucide-react |
| **Backend** | FastAPI, Python 3.11, SQLAlchemy, SQLite |
| **AI** | LiteLLM gateway, DeepSeek V4, GLM 5.2 |
| **Diagrams** | mermaid.js, react-markdown, react-syntax-highlighter |
| **Infrastructure** | Vercel (frontend + serverless API), GitHub Actions |

---

## 📄 License

MIT © Muneer Alam

---

## 🙏 Acknowledgements

Built during a hackathon, for hackathon participants. Inspired by the belief that great ideas deserve a great strategy before a single line of code is written.
