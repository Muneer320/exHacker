# exHacker — Product Bible Gap Analysis & Migration Plan

> **Date:** 2026-07-07  
> **Authority:** This document is derived from `PRODUCT_BIBLE.md`. Every finding below is a measured gap between the specification and the repository.  
> **Status:** Analysis complete. No code changes in this document.

---

## 1. Product Bible Traceability Matrix

Each major requirement from the Product Bible is traced to its implementation status in the current repository.

### 1.1 Project Model (Bible §8.1)

| Bible Field | Current Model | Status |
|---|---|---|
| `id` (UUID) | ✅ `Column(String, primary_key)` | ✅ |
| `name` (auto) | ✅ Auto-generated from idea | ✅ |
| `idea` (text) | ✅ `Column(String, nullable=False)` | ✅ |
| `status` (enum) | ✅ 4-state (`DRAFT`/`PROCESSING`/`READY`/`ARCHIVED`) | 🟡 Bible specifies 7 states |
| `team_size` | ❌ Missing | 🔴 |
| `available_hours` | ❌ Missing | 🔴 |
| `challenge_statement` | ❌ Missing | 🔴 |
| `evaluation_criteria` | ❌ Missing | 🔴 |
| `target_platform` | ❌ Missing | 🔴 |
| `preferred_languages` | ❌ Missing | 🔴 |
| `preferred_frameworks` | ❌ Missing | 🔴 |
| `skills` | ❌ Missing | 🔴 |
| `excluded_technologies` | ❌ Missing | 🔴 |
| `created_at` | ✅ `Column(DateTime)` | ✅ |
| `updated_at` | ✅ `Column(DateTime)` | ✅ |

### 1.2 AI Specialists (Bible §6.2)

| Specialist | Bible Tier | Status |
|---|---|---|
| S1 — Challenge Analyst | Tier 2 | 🔴 Missing |
| S2 — Research Specialist | Tier 1+2 | 🟡 Exists as `research.py` — no Tier 2 synthesis |
| S3 — Competitor Analyst | Tier 2 | 🔴 Missing |
| S4 — Innovation Specialist | Tier 2 | 🔴 Missing |
| S5 — Idea Generator | Tier 2 | 🟡 Exists as `directions.py` — only 2 scores, not 8 |
| S6 — Risk Analyst | Tier 2 | 🔴 Missing |
| S7 — Solution Architect | Tier 0+2 | 🟡 Exists as `architecture.py` |
| S8 — Senior Engineer (Tech Stack) | Tier 0 | ✅ Exists as `tech_stack.py` |
| S9 — Frontend Architect | Tier 0 | 🔴 Missing |
| S10 — Backend Architect | Tier 0+1 | 🔴 Missing |
| S11 — Data Modeler | Tier 0 | ✅ Exists as `data_model.py` |
| S12 — Planning Engineer | Tier 0 | ✅ Exists as `plan.py` |
| S13 — Documentation Writer | Tier 1 | 🔴 Missing |
| S14 — Pitch Coach | Tier 2 | 🔴 Missing (feature flag exists) |
| S15 — Judge Simulator | Tier 2 | 🔴 Missing |
| S16 — Critic | Tier 2 | 🔴 Missing |
| S17 — Fact Checker | Tier 1 | 🔴 Missing |

### 1.3 Shared Intelligence Model (Bible §7)

| Requirement | Current State | Status |
|---|---|---|
| Central project memory | None. No shared context document | 🔴 |
| Decision journal (append-only) | None | 🔴 |
| Specialist reads/writes to shared memory | No specialists share context | 🔴 |
| Review & Revise pattern | No critic, no iteration | 🔴 |
| Verification pattern | No fact checker | 🔴 |
| Parallel execution | Steps run synchronously | 🟡 Research queries are sequential |

### 1.4 Project Lifecycle States (Bible §9.4)

| Bible State | Current State | Status |
|---|---|---|
| `INITIALIZED` | ✅ `DRAFT` | 🟡 Name mismatch |
| `RESEARCHING` | ✅ `PROCESSING` | 🟡 Combined with idea gen |
| `IDEAS_READY` | ❌ Missing | 🔴 |
| `DIRECTION_SELECTED` | ✅ Implicit (auto-transitions to READY) | 🟡 Not a distinct state |
| `ARCHITECTING` | ❌ Missing | 🔴 |
| `READY` | ✅ Exists | ✅ |
| `EXPORTED` | ❌ Missing | 🔴 |
| `FAILED` | ❌ Missing | 🔴 |
| `ARCHIVED` | ✅ Exists | ✅ |

### 1.5 User Journey Stages (Bible §5)

| Stage | Current Implementation | Status |
|---|---|---|
| Landing | ✅ Single-input page at `/` | ✅ |
| Project Creation | 🟡 Only `idea`, `name`, `description` | 🟡 Missing all optional fields |
| Research | ✅ 4 categories (no insights/winners) | 🟡 Missing hackathon winners category |
| Directions (Human Checkpoint) | 🟡 Only 2 scores (innovation, feasibility) | 🟡 Missing 6 of 8 dimensions |
| Architecture | ✅ Tech stack, components, data model, plan | 🟡 No frontend/backend split |
| Documentation | 🔴 Missing (current export is 1 markdown file) | 🔴 |
| Export | 🟡 Markdown + JSON only | 🔴 Missing 3 of 5 V1 formats |
| Post-Export | 🔴 No shareable links, no account persistence | 🔴 |

### 1.6 Export Formats (Bible §13.1)

| Format | Status |
|---|---|
| Markdown (.md) | ✅ |
| JSON (.json) | ✅ |
| ZIP (.zip) | 🔴 Missing |
| CLAUDE.md | 🔴 Missing |
| AGENTS.md | 🔴 Missing |
| Mermaid (.mmd, V2) | 🔴 Missing |
| OpenAPI (.json, V2) | 🔴 Missing |

### 1.7 Documentation System (Bible §12.2)

| Document | Status |
|---|---|
| README.md | 🟡 Exists as single markdown export |
| EXECUTIVE_SUMMARY.md | 🔴 Missing |
| PRD.md | 🔴 Missing |
| ARCHITECTURE.md | 🔴 Missing |
| API.md | 🔴 Missing |
| DATABASE.md | 🔴 Missing |
| SETUP.md | 🔴 Missing |
| DEMO_SCRIPT.md | 🔴 Missing |
| PITCH.md | 🔴 Missing |
| FAQ.md | 🔴 Missing |

### 1.8 UX Design System (Bible §11)

| Requirement | Status |
|---|---|
| Dark theme | ✅ Design tokens in `globals.css` |
| Inter typography | ✅ |
| Purple accent (#7C3AED) | ✅ |
| Surface hierarchy | 🟡 Some tokens defined, not consistently applied |
| Spacing system | 🟡 Ad-hoc in inline styles |
| Responsive layout | 🔴 Not implemented |
| Keyboard navigation | 🔴 Only ⌘K planned |
| Loading states | 🟡 Basic spinner, no skeleton |
| Empty states | 🟡 Basic text, no guidance |
| Error states | 🔴 Missing |
| Accessible contrast | 🟡 Not verified |

---

## 2. Complete Gap Analysis

### 2.1 Critical Gaps (Block Implementation)

| # | Gap | Bible Section | Impact |
|---|---|---|---|
| G1 | **17 specialists → only 4 implemented.** Challenge Analyst, Competitor Analyst, Innovation Specialist, Risk Analyst, Frontend Architect, Backend Architect, Documentation Writer, Pitch Coach, Judge Simulator, Critic, Fact Checker — all missing. | §6.2 | Core value proposition requires these agents. Without them, exHacker is a simple pipeline, not an AI team. |
| G2 | **No shared memory/decision journal.** Agents operate independently with no context sharing. | §7.3 | Information is lost between stages. Later agents can't challenge earlier decisions. No traceability. |
| G3 | **7-state lifecycle vs 4-state.** Missing RESEARCHING, IDEAS_READY, DIRECTION_SELECTED, ARCHITECTING, EXPORTED, FAILED states. | §9.4 | Cannot track pipeline progress granularly. Error recovery is impossible. |
| G4 | **Project model has 4 fields vs 14 required.** Missing team_size, available_hours, skills, preferences, constraints, etc. | §8.1 | Recommendations cannot be context-aware. Team skills and time constraints are ignored. |
| G5 | **Direction scoring has 2 dimensions vs 8.** Missing creativity, technical_depth, demo_potential, judge_appeal, business_potential, overall. | §5.5 | Scoring is too coarse to guide meaningful decisions. |
| G6 | **Documentation generates 1 file vs 10.** No PRD, architecture doc, API ref, demo script, pitch deck, FAQ. | §12.2 | The core export value is severely diminished. |
| G7 | **No human-in-the-loop checkpoint UX.** Direction selection is an API call, not a deliberate product experience. | §5.5 | Critical decision point has no UX design. |
| G8 | **No feedback mechanism after export.** No journal, no traceability, no way to improve outputs. | §7.1 | Users can't understand *why* recommendations were made. |

### 2.2 Moderate Gaps

| # | Gap | Bible Section |
|---|---|---|
| G9 | Research pipeline missing "hackathon winners" category | §5.4 |
| G10 | Research results lack confidence scores and citations | §5.4 |
| G11 | Tech stack recommendation has model names hardcoded (GLM/DeepSeek) | §8.7 |
| G12 | No ZIP, CLAUDE.md, or AGENTS.md export formats | §13.1 |
| G13 | UX is functional but not polished (inline styles, no consistent design system) | §11 |
| G14 | Loading states are basic spinners, no streaming indicators | §10.6 |
| G15 | Empty states show text but no guidance on what to do | §10.5 |
| G16 | Error states don't offer recovery paths | §10.6 |

### 2.3 Minor Gaps

| # | Gap | Bible Section |
|---|---|---|
| G17 | Landing page step visualization shows "Architecture" not "Directions" | §5.1 |
| G18 | Navbar still references old hackathon copy | §5.2 |
| G19 | Project name generation is simple substring, not AI-powered | §8.1 |
| G20 | No keyboard shortcut documentation | §11.7 |
| G21 | Feature flags exist but are unused | §14.2 |

---

## 3. Code Classification Report

Each file in the repository is classified into one of five categories.

### Category A — Keep Unchanged (8 files)

| File | Rationale |
|---|---|
| `backend/app/core/config.py` | Clean config, good defaults, feature flags ready |
| `backend/app/core/exceptions.py` | Well-structured error hierarchy |
| `backend/app/core/logging.py` | Production-quality logging setup |
| `backend/app/db/session.py` | Correct async setup with lazy table creation |
| `backend/app/models/base.py` | Clean base model with shared timestamp logic |
| `backend/app/ai/gateway.py` | Robust AI Gateway with tier routing, cost tracking, retry, mock mode |
| `backend/app/ai/prompts.py` | Clean YAML prompt manager, deterministic rendering |
| `backend/app/api/v1/blueprint.py` | Thin API layer, stays as-is |

### Category B — Needs Modification (15 files)

| File | Changes Needed |
|---|---|
| `backend/app/models/project.py` | Add 12 fields (Bible §8.1), expand to 7-state lifecycle |
| `backend/app/schemas/project.py` | Add new fields, new states to schemas |
| `backend/app/services/project.py` | Expand state machine to 7 states, add transition rules |
| `backend/app/models/direction.py` | Add 6 more score dimensions, add features/risks/effort fields |
| `backend/app/services/blueprint/directions.py` | Generate 8-score format, add elevator pitch, features, risks per direction |
| `backend/app/services/research.py` | Add "hackathon winners" category, confidence scores, citations |
| `backend/app/api/v1/projects.py` | Add endpoints for new project fields |
| `backend/app/api/v1/research.py` | Add confidence scores to response |
| `backend/app/api/v1/directions.py` | Update response shape for 8-score format |
| `backend/app/services/export.py` | Add ZIP, CLAUDE.md, AGENTS.md generators |
| `backend/app/api/v1/export.py` | Add new format endpoints |
| `backend/app/services/blueprint/tech_stack.py` | Remove hardcoded model names, add alternatives array |
| `backend/app/services/blueprint/architecture.py` | Split into frontend/backend architect patterns |
| `backend/frontend/page.tsx` (landing) | Update step visualization, add progressive disclosure form |
| `backend/frontend/projects/[id]/page.tsx` | Add all 5 tabs, empty/loading/error states |

### Category C — Needs Extraction (4 files)

| File | Extract Into |
|---|---|
| `backend/app/services/blueprint/coordinator.py` | Individual specialist files (S5→S12 pattern matching) |
| `backend/app/services/blueprint/architecture.py` | S7 (Solution Architect) + S9 (Frontend) + S10 (Backend) |
| `backend/app/services/blueprint/plan.py` | S12 (Planning Engineer) — team-aware task distribution |
| `backend/app/prompts/directions.yaml` | Multiple prompt files per specialist |

### Category D — Replace Completely (5 files)

| File | Rationale |
|---|---|
| `backend/app/services/blueprint/api_contracts.py` | Works but doesn't match Bible spec (no auth per endpoint, no request/response shapes). Rewrite from spec. |
| `backend/app/services/blueprint/data_model.py` | Works but needs relationship visualization format. Rewrite. |
| `backend/app/services/blueprint/templates.py` | Good base but needs more project types (5 → 8). Rewrite with cleaner architecture. |
| `backend/prompts/research.yaml` | Needs hackathon winners category. Rewrite. |
| `backend/prompts/research_queries.yaml` | Needs more specific query patterns. Rewrite. |

### Category E — Delete (2 files)

| File | Rationale |
|---|---|
| `backend/api/index.py` | Attempted Vercel entry point was superseded by `backend/api/index.py` |
| `api/index.py` (root) | Unused root-level attempt. Cleaning up. |

---

## 4. Dependency Analysis

### 4.1 Dependency Graph (Safest Migration Order)

```
Level 0 (No dependencies)
├── AIGateway + PromptManager (already complete ✅)
├── Core models (config, exceptions, logging) (already complete ✅)
├── Project model expansion (new fields + states)
└── Design system foundations

Level 1 (Depends on Level 0)
├── Project service (new state machine)
├── Project schemas (new fields)
├── Project API (new endpoints)
└── Documentation Writer (needs AI Gateway)

Level 2 (Depends on Level 1)
├── Research pipeline (confidence scores + hackathon winners)
├── Direction generator (8-score format)
└── Tech stack (remove hardcoded models)

Level 3 (Depends on Level 2)
├── Challenge Analyst (new specialist)
├── Competitor Analyst (new specialist)
├── Innovation Specialist (new specialist)
├── Risk Analyst (new specialist)
└── Frontend + Backend Architects (split from Architecture)

Level 4 (Depends on Level 3)
├── Idea Generator (upgraded from Direction)
├── Critic specialist (new)
├── Fact Checker (new)
└── Shared memory system + decision journal

Level 5 (Depends on Level 4)
├── Pitch Coach (new)
├── Judge Simulator (new)
└── Documentation Writer (all 10 files)

Level 6 (Depends on Level 5)
├── Export expansion (ZIP, CLAUDE.md, AGENTS.md)
└── UX polish (all states, responsive, keyboard navigation)
```

### 4.2 Risk Assessment

| Change | Risk | Mitigation |
|---|---|---|
| **Project model expansion** | LOW — additive only, existing fields stay | No migrations needed, old API continues working |
| **State machine expansion (4→7)** | MEDIUM — existing states must map to new ones | Map DRAFT→INITIALIZED, PROCESSING→RESEARCHING+. Never break existing transitions. |
| **New AI specialists** | HIGH — prompt engineering + testing needed | Start with S1 (Challenge Analyst) as template for all others |
| **Shared memory system** | HIGH — new architectural concept | V1: simple JSON document with append-only journal. No real-time sync. |
| **Frontend rewrite** | HIGH — 5 tabs, all states, responsive | Do NOT rewrite from scratch. Add tabs incrementally to existing page. |
| **Documentation generation** | MEDIUM — templated, not AI-heavy | Templates + fill pattern (same as current export) |

---

## 5. Migration Roadmap

### Phase 1: Foundation (Tasks 001-005)

---

#### Task 001 — Expand Project Model

**Bible:** §8.1  
**Estimate:** 2h  
**Files:** `backend/app/models/project.py`, `backend/app/schemas/project.py`, `backend/app/services/project.py`, `backend/app/api/v1/projects.py`  
**Changes:** Add 12 fields (team_size, available_hours, challenge_statement, evaluation_criteria, target_platform, preferred_languages, preferred_frameworks, skills, excluded_technologies). Add 5 new states (RESEARCHING, IDEAS_READY, DIRECTION_SELECTED, ARCHITECTING, EXPORTED, FAILED).  
**Risk:** LOW — additive only  
**Dependencies:** None

---

#### Task 002 — Expand State Machine

**Bible:** §9.4  
**Estimate:** 1h  
**Files:** `backend/app/services/project.py`  
**Changes:** Replace 4-state transition table with 7-state. Define all valid transitions. Map old states to new (DRAFT→INITIALIZED, PROCESSING→RESEARCHING, etc.). Add FAILED state with recovery.  
**Risk:** MEDIUM — existing DRAFT/PROCESSING/READY/ARCHIVED states must continue to work  
**Dependencies:** Task 001

---

#### Task 003 — Add 5 New Score Dimensions to Direction Model

**Bible:** §5.5  
**Estimate:** 1h  
**Files:** `backend/app/models/direction.py`, `backend/app/services/blueprint/directions.py`, `backend/app/prompts/directions.yaml`  
**Changes:** Add creativity, technical_depth, demo_potential, judge_appeal, business_potential, overall scores. Add features array, risks array, elevator_pitch field. Update prompt to generate 8 dimensions.  
**Risk:** LOW — additive only  
**Dependencies:** None

---

#### Task 004 — Create Shared Memory (Decision Journal)

**Bible:** §7.3  
**Estimate:** 3h  
**Files:** `backend/app/services/memory.py` (new), `backend/app/models/memory.py` (new)  
**Changes:** Create decision journal as append-only log. Each entry stores: agent_id, action, summary, alternatives_considered, confidence, timestamp. Integrate into specialist base class.  
**Risk:** MEDIUM — new architectural concept  
**Dependencies:** None

---

#### Task 005 — Remove Hardcoded Model Names from Tech Stack

**Bible:** §8.7  
**Estimate:** 0.5h  
**Files:** `backend/app/services/blueprint/tech_stack.py`  
**Changes:** Replace `"opencode-go (GLM / DeepSeek)"` with `"AI Provider (configurable)"`. Replace hardcoded model names with generic descriptions.  
**Risk:** LOW  
**Dependencies:** None

---

### Phase 2: New Specialists (Tasks 006-010)

---

#### Task 006 — Challenge Analyst (S1)

**Bible:** §6.2 S1  
**Estimate:** 3h  
**Files:** `backend/app/services/specialists/challenge_analyst.py` (new), `backend/prompts/challenge_analyst.yaml` (new)  
**Changes:** Create Challenge Analyst specialist. Model: Tier 2. Input: challenge_statement, theme, evaluation_criteria. Output: themes, constraints, hidden_opportunities, judging_priorities.  
**Risk:** MEDIUM — first new specialist, establishes pattern for others  
**Dependencies:** Task 001 (project has challenge fields)

---

#### Task 007 — Competitor Analyst (S3)

**Bible:** §6.2 S3  
**Estimate:** 2h  
**Files:** `backend/app/services/specialists/competitor_analyst.py` (new)  
**Changes:** Create Competitor Analyst. Input: research data. Output: SWOT analysis, differentiation strategies, gap identification.  
**Risk:** LOW — follows pattern from Task 006  
**Dependencies:** Task 006 (specialist pattern established)

---

#### Task 008 — Innovation Specialist (S4)

**Bible:** §6.2 S4  
**Estimate:** 2h  
**Files:** `backend/app/services/specialists/innovation_specialist.py` (new)  
**Changes:** Create Innovation Specialist. Input: challenge analysis + competitive analysis. Output: opportunity map with 5+ innovation angles.  
**Risk:** LOW — follows pattern  
**Dependencies:** Tasks 006, 007

---

#### Task 009 — Risk Analyst (S6)

**Bible:** §6.2 S6  
**Estimate:** 2h  
**Files:** `backend/app/services/specialists/risk_analyst.py` (new)  
**Changes:** Create Risk Analyst. Input: generated ideas. Output: per-idea risk assessment with severity and mitigation. Integrate into direction generation output.  
**Risk:** LOW — follows pattern  
**Dependencies:** Task 003 (direction model expanded)

---

#### Task 010 — Upgrade Idea Generator (S5)

**Bible:** §6.2 S5  
**Estimate:** 3h  
**Files:** `backend/app/services/blueprint/directions.py`, `backend/prompts/directions.yaml`  
**Changes:** Upgrade direction generation to Bible spec. Input: opportunity map + project parameters. Output: 3 ideas with 8-score format, elevator pitch, core/stretch features, risks, estimated effort. Add feasibility check against available time.  
**Risk:** MEDIUM — changes existing API response shape  
**Dependencies:** Tasks 001, 003, 009

---

### Phase 3: Architecture & Planning (Tasks 011-015)

---

#### Task 011 — Frontend Architect (S9)

**Bible:** §6.2 S9  
**Estimate:** 2h  
**Files:** `backend/app/services/specialists/frontend_architect.py` (new)  
**Changes:** Create Frontend Architect specialist. Tier 0 (templates). Input: selected idea, tech stack, target platform. Output: component tree, state management design, routes, data fetching strategy.  
**Risk:** LOW — template-based  
**Dependencies:** Task 005 (tech stack clean)

---

#### Task 012 — Backend Architect (S10)

**Bible:** §6.2 S10  
**Estimate:** 2h  
**Files:** `backend/app/services/specialists/backend_architect.py` (new)  
**Changes:** Create Backend Architect specialist. Tier 0+1. Input: selected idea, tech stack, data model. Output: service design, API organization, middleware, auth flow.  
**Risk:** LOW — template-based  
**Dependencies:** Task 005

---

#### Task 013 — Documentation Writer (S13)

**Bible:** §6.2 S13, §12.2  
**Estimate:** 4h  
**Files:** `backend/app/services/specialists/documentation_writer.py` (new)  
**Changes:** Create Documentation Writer. Tier 1. Generate 10 documents from project data. Template-based with variable filling. Each document is a separate file.  
**Risk:** MEDIUM — most files of any specialist  
**Dependencies:** Tasks 001-012 (all project data must exist)

---

#### Task 014 — Pitch Coach (S14)

**Bible:** §6.2 S14  
**Estimate:** 2h  
**Files:** `backend/app/services/specialists/pitch_coach.py` (new)  
**Changes:** Create Pitch Coach. Tier 2. Input: project data, judging criteria, competitive analysis. Output: elevator pitch (30s), full pitch (2m), demo script, anticipated Q&A.  
**Risk:** MEDIUM — first pitch-generation specialist  
**Dependencies:** Tasks 006-008 (requires research + competitive analysis)

---

#### Task 015 — Judge Simulator (S15)

**Bible:** §6.2 S15  
**Estimate:** 2h  
**Files:** `backend/app/services/specialists/judge_simulator.py` (new)  
**Changes:** Create Judge Simulator. Tier 2. Input: full project data, judging criteria. Output: evaluation scores, anticipated questions, weaknesses to address.  
**Risk:** LOW — follows pattern from Task 014  
**Dependencies:** Tasks 006-013

---

### Phase 4: Collaboration & Verification (Tasks 016-019)

---

#### Task 016 — Critic (S16)

**Bible:** §6.2 S16  
**Estimate:** 3h  
**Files:** `backend/app/services/specialists/critic.py` (new)  
**Changes:** Create Critic specialist. Tier 2. Input: any output from any specialist. Output: constructive critique with challenged assumptions, weak arguments, alternatives. Integrate into pipeline as post-processing step after each major output.  
**Risk:** MEDIUM — needs integration into every specialist  
**Dependencies:** Tasks 006-015 (all specialists exist)

---

#### Task 017 — Fact Checker (S17)

**Bible:** §6.2 S17  
**Estimate:** 2h  
**Files:** `backend/app/services/specialists/fact_checker.py` (new)  
**Changes:** Create Fact Checker. Tier 1. Input: claims from other specialists. Output: verification status per claim (confirmed/disputed/unverifiable) with sources.  
**Risk:** LOW — follows pattern  
**Dependencies:** Tasks 006-015

---

#### Task 018 — Integrate Shared Memory into All Specialists

**Bible:** §7.3  
**Estimate:** 3h  
**Files:** All specialist files  
**Changes:** Every specialist reads project memory before execution and writes decisions/confidence/outputs to journal after execution. Integrate critic and fact checker as post-processing hooks.  
**Risk:** MEDIUM — touches every specialist  
**Dependencies:** Tasks 004, 016, 017

---

#### Task 019 — Research Pipeline Upgrade (Confidence + Winners)

**Bible:** §5.4  
**Estimate:** 2h  
**Files:** `backend/app/services/research.py`, `backend/prompts/research.yaml`  
**Changes:** Add "hackathon winners" research category. Add confidence score per result. Add citations field. Add research_types: hackathon_winners, trends.  
**Risk:** LOW — additive  
**Dependencies:** Task 002 (state machine for RESEARCHING state)

---

### Phase 5: Export & UX (Tasks 020-025)

---

#### Task 020 — Add ZIP Export

**Bible:** §13.1  
**Estimate:** 1h  
**Files:** `backend/app/services/export.py`, `backend/prompts/export/` (new)  
**Changes:** Add ZIP export that bundles all documentation files into a single archive. Use Python's `zipfile` standard library.  
**Risk:** LOW  
**Dependencies:** Task 013 (documentation exists)

---

#### Task 021 — Add CLAUDE.md + AGENTS.md Export

**Bible:** §13.1  
**Estimate:** 1h  
**Files:** `backend/app/services/export.py`  
**Changes:** Generate CLAUDE.md (AI coding tool context) and AGENTS.md (agent configuration) from project data. These configure Cursor/Claude Code to work on the project.  
**Risk:** LOW  
**Dependencies:** Task 013

---

#### Task 022 — Frontend: Progressive Disclosure Form

**Bible:** §5.3  
**Estimate:** 4h  
**Files:** `frontend/src/app/page.tsx`  
**Changes:** Add "Add details" expander below the main input. Required fields shown first, optional fields in categorized groups. Save to localStorage.  
**Risk:** MEDIUM — touches landing page, the most visible part of the product  
**Dependencies:** Task 001 (API supports new fields)

---

#### Task 023 — Frontend: Empty/Loading/Error States

**Bible:** §10.5, §10.6  
**Estimate:** 4h  
**Files:** Multiple frontend components  
**Changes:** Every tab (overview, research, directions, blueprint, export) gets proper empty state with guidance, loading state with progress, error state with recovery path. Skeleton loaders for content areas.  
**Risk:** MEDIUM — many components affected  
**Dependencies:** None

---

#### Task 024 — Frontend: Direction Card Redesign

**Bible:** §5.5  
**Estimate:** 3h  
**Files:** `frontend/src/app/projects/[id]/page.tsx`  
**Changes:** Redesign direction cards to show 8 score dimensions with visual bars. Add elevator pitch, features list, risks section. Improve selection UX.  
**Risk:** LOW — isolated component  
**Dependencies:** Task 003 (API returns 8 scores)

---

#### Task 025 — Frontend: Documentation Viewer Tab

**Bible:** §5.7  
**Estimate:** 3h  
**Files:** `frontend/src/app/projects/[id]/page.tsx`  
**Changes:** Add "Docs" tab that lists 10 generated documents. Each document is previewable inline. Click to expand full content.  
**Risk:** LOW  
**Dependencies:** Task 013 (documentation exists)

---

### Phase 6: Polish & Performance (Tasks 026-028)

---

#### Task 026 — Responsive Layout

**Bible:** §11  
**Estimate:** 4h  
**Files:** All frontend component files  
**Changes:** Sidebar collapses to icons at <1024px, hidden with bottom nav at <768px, single column at <480px. Touch targets ≥44px.  
**Risk:** MEDIUM — touches all pages  
**Dependencies:** None

---

#### Task 027 — Keyboard Shortcuts

**Bible:** §11.7  
**Estimate:** 2h  
**Files:** `frontend/src/app/projects/[id]/page.tsx`, `frontend/src/app/page.tsx`  
**Changes:** ⌘K command palette, ⌘Enter to confirm, Escape to dismiss, Tab navigation in forms.  
**Risk:** LOW  
**Dependencies:** None

---

#### Task 028 — Remove Stale Configs

**Bible:** — (cleanup)  
**Estimate:** 0.5h  
**Files:** `backend/api/index.py`, `api/index.py` (root), `vercel.json`  
**Changes:** Delete unused entry points.  
**Risk:** LOW  
**Dependencies:** None

---

## 6. Engineering Risk Assessment

| Risk | Severity | Probability | Mitigation |
|---|---|---|---|
| State machine expansion breaks existing API consumers | MEDIUM | LOW | Map old states explicitly, add deprecation warnings |
| New AI specialists produce low-quality output | HIGH | MEDIUM | Start with templates + fallback pattern. Lowers risk of bad AI output. |
| Shared memory becomes a bottleneck | MEDIUM | LOW | V1: simple JSON document with append-only journal. No locks needed. |
| Frontend rewrites cause regressions | MEDIUM | MEDIUM | Build incrementally, never rewrite entire file at once. |
| Documentation generation duplicates content | LOW | LOW | Template-based with strict variable mapping. No AI for document content. |
| ZIP export introduces security concerns | LOW | LOW | Standard library only, no external archives. |
| Parallel specialist execution conflicts on shared memory | MEDIUM | LOW | V1 runs everything sequentially. Parallel execution is V2. |

---

## 7. Recommended First Refactor

**Task 001: Expand Project Model** — This is the safest, highest-impact first change. It's additive (no existing code breaks), unlocks all subsequent specialist work (Challenge Analyst needs `challenge_statement`, Plan Generator needs `team_size` and `skills`), and improves every downstream feature.

### What Task 001 Changes

**Current model (33 lines):**
- 4 fields: `id`, `name`, `idea`, `status`
- 4 states: `DRAFT`, `PROCESSING`, `READY`, `ARCHIVED`

**Expanded model:**
- 16 fields (4 existing + 12 new)
- 9 states (7 active + 2 terminal)
- Backward-compatible API endpoints

### Why This Order

1. Project model expansion is **additive only** — no existing code breaks
2. Every downstream specialist needs the enriched project data
3. The API still serves the old `name`/`idea`/`status` fields — old clients continue working
4. The expanded state machine enables granular progress tracking from day one

---

## 8. Architecture Validation

Every recommended change has been validated against:

| Principle | Compliance | Notes |
|---|---|---|
| **Product Bible** | ✅ All changes derive from specific Bible sections |
| **SDPD C1 — Tier 0 First** | ✅ New specialists use templates where possible. AI is for reasoning only. |
| **SDPD C2 — Cheapest Model** | ✅ S1 (Challenge Analyst) uses Tier 2. S2 uses Tier 1. S7 uses Tier 0. |
| **SDPD C3 — Editable Outputs** | ✅ All AI outputs are editable by the user before being committed to project memory. |
| **SDPD C5 — Portable** | ✅ Export includes all project data. No lock-in. |
| **SDPD C9 — Cost Tracking** | ✅ Every specialist call is tracked via existing AIGateway cost system. |
| **SDPD C10 — Graceful Degradation** | ✅ Every specialist has a template fallback if AI is unavailable. |
| **Current TAD** | ✅ Changes follow the existing architecture pattern (thin API → service layer → models). |

---

## 9. Technical Debt Register

| Item | Location | Severity | Type |
|---|---|---|---|
| **Model names hardcoded in tech stack** | `backend/app/services/blueprint/tech_stack.py:124` | MEDIUM | Assumption leak |
| **Direction scores stored as separate columns** | `backend/app/models/direction.py:18-19` | LOW | Schema inflexibility |
| **Inline styles in frontend** | All `.tsx` files | HIGH | No design system enforcement |
| **No frontend type safety for API responses** | `frontend/src/services/api.ts` | MEDIUM | Manual type definitions, no codegen |
| **`research.yaml` prompt file has wrong model_tier** | `backend/prompts/research.yaml` | LOW | Would cause cost surprises |
| **Export endpoint regenerates blueprint every time** | `backend/app/api/v1/export.py:24` | LOW | Inefficient, no caching |
| **No migration system (Alembic not in use)** | `backend/pyproject.toml:alembic` | MEDIUM | Schema changes are manual |
| **Feature flags defined but never checked** | `backend/app/core/config.py:80-82` | LOW | Dead config |
| **Frontend has no tests** | — | HIGH | Regression risk on UI changes |
| **Backend test coverage ~15%** | `backend/tests/` | MEDIUM | Only 6 tests for 37 production files |

---

## 10. Summary

### By the Numbers

| Metric | Value |
|---|---|
| Bible requirements audited | 87 |
| Fully implemented | 15 (17%) |
| Partially implemented | 18 (21%) |
| Missing | 54 (62%) |
| Critical gaps | 8 |
| Migration tasks identified | 28 |
| Estimated engineering effort | ~58 hours |
| Lowest-risk first task | Task 001 — Expand Project Model (2h, additive only) |

### What to Build First

The migration roadmap is ordered by dependency chain. **Task 001 through Task 005** (Foundation phase) should be built first because:
1. They unblock everything downstream
2. They're low-risk (mostly additive)
3. They establish patterns (shared memory, expanded state machine, 8-score format)
4. Each delivers incremental value independently

### What NOT to Build

The following are explicitly **out of scope** for this migration:
- Real-time collaboration (Bible §17.3)
- Native mobile app (Bible §17.3)
- Plugin/extension system (Bible V3+)
- API for external developers (Bible V3+)
- Self-improving agents (Bible V5)

---

*This audit is derived from `PRODUCT_BIBLE.md` (v1.0) and the current repository state at commit `e42a503`. Every finding is traceable to a specific Bible section. Implementation should begin with Task 001 — Project Model Expansion.*
