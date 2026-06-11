# 03_System_Architecture.md

# System Architecture

Project: exHacker

Version: 2.0

Status: Active

---

# Purpose

This document defines:

* System components
* Component responsibilities
* Data flow
* Agent architecture
* Workflow architecture
* LLM architecture
* Research architecture
* Export architecture

This document should allow a new engineer to understand the entire platform before reading any code.

---

# High-Level Architecture

```text
┌──────────────────────────┐
│        Frontend          │
│        Next.js           │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│         FastAPI          │
│      API Layer           │
└────────────┬─────────────┘
             │
             ▼
┌──────────────────────────┐
│   Workflow Orchestrator  │
│       LangGraph          │
└────────────┬─────────────┘
             │
 ┌───────────┼───────────┐
 ▼           ▼           ▼

Agents    Research     Artifacts

             │
             ▼

      Shared State

             │
             ▼

        PostgreSQL

             │
             ▼

       Export Layer
```

---

# Core Components

The platform consists of six major systems.

1. Frontend
2. API Layer
3. Workflow Engine
4. Agent Layer
5. Research Layer
6. Artifact Layer

---

# Frontend Layer

Technology:

* Next.js
* React
* TypeScript
* Tailwind
* shadcn/ui

---

## Responsibilities

The frontend is responsible for:

* User input
* Workflow visualization
* Progress tracking
* Results display
* Exports

The frontend should not contain business logic.

The frontend should not execute agents.

The frontend should only communicate with API endpoints.

---

## Pages

Current Architecture:

```text
/
├── Landing
├── Projects
├── Project Details
├── Workflow View
├── Results
└── Export
```

---

# Backend Layer

Technology:

* FastAPI

Purpose:

Provide all application APIs.

---

## Responsibilities

* Request validation
* Authentication (future)
* Workflow execution
* State retrieval
* Export generation
* Agent invocation

---

## Backend Rule

No frontend-specific logic should exist in backend services.

No workflow logic should exist inside routes.

Routes should be thin.

---

# Workflow Engine

Technology:

* LangGraph

This is the heart of exHacker.

---

## Responsibilities

* Execute agents
* Manage workflow state
* Handle retries
* Handle failures
* Resume workflows
* Support future branching

---

## Workflow Design

```text
Input
↓
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

---

## Workflow Principles

Agents never call other agents.

Agents never know who runs next.

Only the workflow engine decides execution order.

---

# Shared State Layer

All workflow information is stored in a single shared state object.

---

## Why Shared State

Without shared state:

```text
Agent A
  ↕
Agent B
  ↕
Agent C
```

creates tight coupling.

Instead:

```text
Agent A
   ↓
 Shared State
   ↑
Agent B
   ↓
 Shared State
   ↑
Agent C
```

Agents become independent.

---

## State Ownership

Every domain owns its own section.

Examples:

```text
challenge_intelligence

problem_analysis

generated_ideas

validation_reports

selected_idea

tech_stack

architecture

presentation

pitch
```

---

## Rule

Agents may only modify their assigned domain.

Agents must not modify unrelated state.

---

# Agent Layer

Agents are specialized workers.

Each agent has:

* Clear responsibility
* Defined inputs
* Defined outputs

---

## Current Agents

```text
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

## Agent Structure

Every agent must contain:

```text
Agent

Prompt

Input Schema

Output Schema

Validation

Tests
```

---

## Agent Contract

Inputs:

Shared State

Outputs:

Structured Data

Agents must never return free-form text.

All outputs must match schemas.

---

# Research Layer

Purpose:

Provide evidence-backed information.

The platform should not rely solely on model knowledge.

---

## Responsibilities

Research:

* Competitors
* Startups
* APIs
* Open Source Projects
* Similar Solutions

---

## Consumers

Used by:

* Challenge Intelligence
* Opportunity Planner
* Idea Validator

---

## Principle

Ideas should be validated using research rather than assumptions.

---

# LLM Layer

Purpose:

Provide provider-independent AI execution.

---

## Supported Providers

Priority Order:

1. Groq
2. Gemini
3. Ollama
4. OpenAI

---

## Why Abstraction

Agents should never know:

* Which provider is used
* Which model is used

Agents only call:

```python
LLMService
```

---

## Provider Architecture

```text
LLMService
│
├── Groq
├── Gemini
├── Ollama
└── OpenAI
```

---

## Fallback Logic

Example:

```text
Groq Fails
↓
Gemini
↓
Ollama
↓
OpenAI
```

Workflow should continue whenever possible.

---

# Artifact Layer

Purpose:

Generate reusable outputs.

---

## Outputs

README

PRD

Architecture

API Documentation

Presentation Package

Pitch Package

Implementation Guide

Export Package

---

## Formats

Markdown

PDF

ZIP

JSON

---

# Database Layer

Technology:

* PostgreSQL

Purpose:

Persistent storage.

---

## Stores

Projects

Workflow State

Agent Runs

Artifacts

Exports

Execution History

---

## Requirements

State persistence after every stage.

Workflow recovery after failures.

Workflow resume support.

---

# Observability

The platform must record:

* Agent executions
* Retry counts
* Errors
* LLM costs
* Token usage
* Workflow duration

---

## Purpose

Allow:

* Debugging
* Cost tracking
* Performance analysis

---

# Deployment Architecture

Development:

```text
Frontend
Backend
PostgreSQL
```

via:

Docker Compose

---

Production:

```text
Frontend
(Vercel)

↓

Backend
(Railway)

↓

Database
(Supabase)
```

---

# Architectural Principles

1. Agents are isolated.

2. Shared state is the source of truth.

3. Workflow engine controls execution.

4. Providers are replaceable.

5. Research is evidence-based.

6. Artifacts are reusable.

7. Frontend is presentation-only.

8. Backend owns business logic.

9. Every output must be structured.

10. Architecture must support future agents without major redesign.

---

# Future Expansion

Potential additions:

* Multi-user projects
* Team collaboration
* Startup planning mode
* Accelerator mode
* Grant application mode
* Custom workflow creation

The current architecture should support these without major refactoring.
