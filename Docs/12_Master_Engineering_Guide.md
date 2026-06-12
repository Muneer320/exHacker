# 12_Master_Engineering_Guide.md

# exHacker Master Engineering Guide

Project: exHacker

Version: 2.0

Status: Active

Audience:

* AI Engineers
* Human Engineers
* Future Contributors

---

# Read This First

If you are new to the project:

Read documents in this order:

```text id="m1"
12_Master_Engineering_Guide.md

00_Vision.md

01_PRD.md

03_System_Architecture.md

04_Agent_Specifications.md

05_Workflow_Design.md

06_State_Model.md
```

Everything else is supplementary.

---

# What Is exHacker?

exHacker is an AI-powered Hackathon Co-Pilot.

It helps teams go from:

```text id="m2"
Problem Statement
↓
Project Idea
↓
Validation
↓
Architecture
↓
Build Plan
↓
Presentation
↓
Pitch
```

in a single workflow.

The goal is to remove planning overhead from hackathons.

---

# Core Product Promise

Given:

* A challenge
* Team information
* Time constraints

The platform should answer:

> What should we build, and how should we build it?

within a few minutes.

---

# What Makes exHacker Different?

Most hackathon tools:

```text id="m3"
Prompt
↓
LLM
↓
Answer
```

exHacker:

```text id="m4"
Prompt
↓
Research
↓
Analysis
↓
Validation
↓
Architecture
↓
Execution Plan
↓
Presentation
↓
Pitch
```

The workflow is the differentiator.

Not the model.

---

# System Overview

```text id="m5"
Frontend
(Next.js)

↓

Backend
(FastAPI)

↓

Workflow Engine
(LangGraph)

↓

Agents

↓

Shared State

↓

Artifacts

↓

Exports
```

---

# Current Architecture

Frontend:

```text id="m6"
Next.js
React
TypeScript
Tailwind
shadcn/ui
```

Backend:

```text id="m7"
FastAPI
Pydantic
SQLAlchemy
LangGraph
```

Database:

```text id="m8"
PostgreSQL
```

LLM Layer:

```text id="m9"
Groq
Gemini
Ollama
OpenAI
```

Priority:

```text id="m10"
Groq
↓
Gemini
↓
Ollama
↓
OpenAI
```

---

# Core Workflow

```text id="m11"
Challenge Intelligence
↓
Problem Analysis
↓
Opportunity Discovery
↓
Idea Generation
↓
Idea Validation
↓
Human Selection
↓
Tech Stack
↓
Architecture
↓
Build Accelerator
↓
Presentation
↓
Pitch
↓
Export
```

This workflow is the product.

---

# Current Agent List

```text id="m12"
Challenge Intelligence

Problem Analyst

Opportunity Planner

Idea Generator

Idea Validator

Tech Stack Advisor

Solution Architect

Build Accelerator

Presentation Agent

Pitch Coach
```

---

# Source Of Truth

The most important concept in the entire codebase:

```text id="m13"
Shared State
```

Agents do not communicate.

Agents do not call each other.

Agents only:

```text id="m14"
Read State

Write State
```

Everything flows through state.

---

# Golden Engineering Rules

---

## Rule 1

Agents are isolated.

Never make agents depend on each other.

---

## Rule 2

Workflow controls execution.

Agents never control workflow.

---

## Rule 3

State is the source of truth.

Never duplicate state.

---

## Rule 4

User decisions are final.

Especially:

```text id="m15"
selected_idea
```

must never be overridden.

---

## Rule 5

Structured outputs only.

No free-form responses.

Everything must map to schemas.

---

## Rule 6

Research before recommendation.

Evidence > intuition.

---

## Rule 7

Optimize for hackathons.

Choose:

```text id="m16"
Simple > Complex
```

---

Choose:

```text id="m17"
Fast > Perfect
```

---

Choose:

```text id="m18"
Buildable > Innovative
```

---

# Current Priorities

Priority Order:

---

## Priority 1

Workflow Stability

Must work end-to-end.

---

## Priority 2

Agent Quality

Outputs must be useful.

---

## Priority 3

Research Layer

Biggest differentiator.

---

## Priority 4

Artifact Generation

Main user deliverable.

---

## Priority 5

Frontend Experience

Presentation layer.

---

## Priority 6

Optimization

Costs

Caching

Performance

---

# What Should Be Built Next?

If starting today:

---

## Phase 1

Finish Workflow

Checklist:

```text id="m19"
All nodes execute

All state persists

Resume works

Retries work
```

---

## Phase 2

Finish Research Layer

Checklist:

```text id="m20"
Competitor Search

GitHub Search

API Search

Research Scoring
```

---

## Phase 3

Finish Artifact Generation

Checklist:

```text id="m21"
README

Architecture

Implementation Guide

Presentation

Pitch
```

---

## Phase 4

Frontend UX

Checklist:

```text id="m22"
Project Creation

Workflow Tracking

Idea Selection

Results Dashboard

Exports
```

---

# Technical Debt To Watch

---

## Agent Coupling

Never allow:

```text id="m23"
Agent A
↓
Agent B
```

direct dependencies.

---

## Giant Prompts

Keep prompts focused.

Context is expensive.

---

## State Bloat

Only store useful information.

Avoid storing raw LLM dumps.

---

## Overengineering

Remember:

This is a hackathon product.

Not an enterprise platform.

---

# Current MVP Definition

MVP is complete when a user can:

1. Create project

2. Generate ideas

3. Validate ideas

4. Select idea

5. Receive architecture

6. Receive tech stack

7. Receive build plan

8. Receive presentation

9. Receive pitch

10. Export package

without manual intervention.

---

# Non Goals

Not building:

```text id="m24"
Slack

Discord

GitHub

Jira

Linear

Notion
```

---

Not building:

```text id="m25"
Multi-user collaboration
```

in MVP.

---

Not building:

```text id="m26"
Authentication
```

in MVP.

---

# Future Roadmap

Potential Future Modes:

```text id="m27"
Hackathon Mode

Startup Mode

Accelerator Mode

Grant Mode

Product Discovery Mode
```

All should reuse:

```text id="m28"
Workflow Engine

Agent Layer

Research Layer

Artifact Layer
```

---

# Recommended Repository Structure

```text id="m29"
frontend/

backend/

docs/

scripts/

infrastructure/
```

Inside backend:

```text id="m30"
agents/

research/

artifacts/

workflows/

services/

schemas/

models/
```

This structure should remain stable.

---

# Success Metrics

The platform succeeds if:

A team can go from:

```text id="m31"
Problem Statement
```

to

```text id="m32"
Buildable Project
```

in under:

```text id="m33"
5 minutes
```

while producing outputs that are genuinely useful.

---

# If You Only Remember One Thing

exHacker is not an AI chatbot.

exHacker is a workflow system that transforms a hackathon challenge into an execution-ready project package.

Every engineering decision should move the platform closer to that goal.
