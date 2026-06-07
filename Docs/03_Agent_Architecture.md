# Agent Architecture Document

Project: exHacker

Version: 1.0

Status: Draft

---

# Overview

exHacker is built as a multi-agent system.

Rather than relying on a single LLM prompt, the platform decomposes hackathon planning into a sequence of specialized agents.

Each agent:

* Has a single responsibility
* Receives structured inputs
* Produces structured outputs
* Passes context to downstream agents

The system is coordinated by a central orchestrator.

---

# High-Level Architecture

User
↓
Orchestrator
↓
User Profiler
↓
Challenge Intelligence Agent
↓
Problem Analyst
↓
Opportunity Planner
↓
Idea Generator
↓
Idea Validator
↓
User Selection
↓
Solution Architect
↓
Tech Stack Advisor
↓
Build Accelerator
↓
Presentation Agent
↓
Pitch Coach
↓
Export Package

---

# Design Principles

## Single Responsibility

Every agent should solve exactly one problem.

Bad:

Research + Idea Generation + Architecture

Good:

One agent per responsibility.

---

## Structured Communication

Agents communicate through structured JSON objects.

Never through free-form text.

---

## Human Checkpoints

Important decisions remain human controlled.

Users must explicitly choose:

* Project ideas
* Final direction
* Exported artifacts

The system assists decision making.

The system does not replace it.

---

## Deterministic Pipelines

The same input should generally produce similar outputs.

Agent outputs must be structured and repeatable.

---

# Orchestrator

The orchestrator controls workflow execution.

Responsibilities:

* Agent scheduling
* State management
* Error handling
* Retry logic
* Context sharing
* Progress tracking

The orchestrator never generates business logic.

It only coordinates agents.

---

# Shared Memory

All agents read and write to a shared project state.

Project State:

```json
{
  "hackathon": {},
  "team": {},
  "challenge_intelligence": {},
  "problem_analysis": {},
  "opportunity_analysis": {},
  "ideas": [],
  "validated_ideas": [],
  "selected_idea": {},
  "architecture": {},
  "tech_stack": {},
  "build_package": {},
  "presentation": {},
  "pitch_package": {}
}
```

This state is the single source of truth.

---

# Agent Execution Flow

Stage 1

Context Understanding

* User Profiler
* Challenge Intelligence

---

Stage 2

Problem Understanding

* Problem Analyst
* Opportunity Planner

---

Stage 3

Idea Discovery

* Idea Generator
* Idea Validator

---

Stage 4

Solution Design

* Solution Architect
* Tech Stack Advisor

---

Stage 5

Build Preparation

* Build Accelerator

---

Stage 6

Submission Preparation

* Presentation Agent
* Pitch Coach

---

# Agent Specifications

## Agent 0

User Profiler

Purpose:

Understand team constraints.

Inputs:

```json
{
  "team_size": 4,
  "duration": 24,
  "skills": []
}
```

Outputs:

```json
{
  "complexity_budget": "medium",
  "recommended_scope": "mvp",
  "risk_tolerance": "medium"
}
```

---

## Agent 1

Challenge Intelligence Agent

Purpose:

Understand the challenge environment.

Researches:

* Themes
* Tracks
* Resources
* Datasets
* APIs
* Evaluation criteria

Outputs:

```json
{
  "themes": [],
  "opportunities": [],
  "constraints": [],
  "resource_opportunities": []
}
```

---

## Agent 2

Problem Analyst

Purpose:

Understand the actual problem.

Outputs:

```json
{
  "pain_points": [],
  "stakeholders": [],
  "assumptions": [],
  "success_metrics": []
}
```

---

## Agent 3

Opportunity Planner

Purpose:

Find valuable opportunities.

Outputs:

```json
{
  "market_gaps": [],
  "innovation_opportunities": [],
  "high_impact_areas": []
}
```

---

## Agent 4

Idea Generator

Purpose:

Generate candidate projects.

Output Count:

10 ideas

Outputs:

```json
{
  "ideas": []
}
```

---

## Agent 5

Idea Validator

Purpose:

Validate and score ideas.

Researches:

* Competitors
* Existing products
* Open-source solutions
* APIs

Scoring Formula:

Innovation:
30%

Feasibility:
30%

Hackathon Fit:
20%

Technical Wow Factor:
20%

Outputs:

```json
{
  "idea": "",
  "score": 87,
  "strengths": [],
  "weaknesses": []
}
```

---

# Human Decision Point

User selects one validated idea.

No automatic selection.

This is a mandatory checkpoint.

---

## Agent 6

Solution Architect

Purpose:

Create complete project blueprint.

Outputs:

* Product Vision
* Features
* Priorities
* User Stories
* Architecture
* APIs
* Database Schema
* Security Notes
* Deployment Plan
* README

This is the largest agent in the system.

---

## Agent 7

Tech Stack Advisor

Purpose:

Recommend technologies.

Considers:

* Team skills
* Duration
* Complexity
* Integrations

Outputs:

```json
{
  "frontend": "",
  "backend": "",
  "database": "",
  "hosting": "",
  "ai_stack": ""
}
```

---

## Agent 8

Build Accelerator

Purpose:

Generate implementation prompts.

Outputs:

* Frontend Prompts
* Backend Prompts
* Database Prompts
* AI Prompts
* Testing Prompts
* Deployment Prompts

Supported Platforms:

* Cursor
* Claude
* Lovable
* Bolt
* Windsurf

---

## Agent 9

Presentation Agent

Purpose:

Generate submission materials.

Outputs:

* PPT Outline
* Slide Content
* Demo Story
* Architecture Diagrams
* Impact Metrics

---

## Agent 10

Pitch Coach

Purpose:

Prepare team presentation.

Outputs:

* 30 Second Pitch
* 2 Minute Pitch
* 5 Minute Pitch
* Q&A Preparation
* Objection Handling
* Demo Script

---

# Error Handling

If an agent fails:

1. Retry once
2. Retry with reduced context
3. Surface error to orchestrator
4. Continue if failure is non-critical

Critical agents:

* Challenge Intelligence
* Problem Analyst
* Solution Architect

Failure in these agents blocks workflow.

---

# Future Agent Expansion

Potential future agents:

* Code Generation Agent
* GitHub Agent
* Project Tracker Agent
* Demo Video Agent
* UI Generator Agent
* Judge Simulator Agent
* Deployment Agent

These are not part of MVP.

---

# Summary

The exHacker architecture is built around specialized agents connected through a shared project state and coordinated by a central orchestrator.

The goal is not to answer prompts.

The goal is to progressively transform challenge statements into execution-ready hackathon blueprints.
