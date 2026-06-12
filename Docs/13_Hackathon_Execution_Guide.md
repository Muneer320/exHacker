# 13_Hackathon_Execution_Guide.md

# Hackathon Execution Guide

Project: exHacker

Version: 3.0

Status: Active

---

## Purpose

This document defines how exHacker must be developed during the hackathon.

It is not a product document.

It is not an architecture document.

It is an execution document.

Its purpose is to ensure:

* Clean development process
* Traceable Git history
* Predictable implementation
* AI engineer consistency
* Fast iteration without chaos

---

# Source of Truth

The Docs directory is the source of truth.

Implementation must follow the documentation.

When conflicts occur:

Priority Order:

1. Vision
2. PRD
3. User Flow
4. System Architecture
5. Agent Specifications
6. Workflow Design
7. State Model
8. API Contracts
9. Implementation Roadmap
10. Research Architecture
11. Artifact Generation
12. Master Engineering Guide
13. This Document

No implementation should contradict higher-priority documents.

---

# Branch Strategy

Primary Branch:

v2

The project must treat v2 as the main branch.

Ignore previous implementations.

Ignore old architecture.

Ignore old branches.

Build strictly from the documentation.

---

# Development Philosophy

Build vertically.

Never build large amounts of infrastructure before proving value.

Always create a working slice first.

Preferred sequence:

Input
→ Workflow
→ Agent
→ Output
→ UI

Then expand.

---

# Commit Policy

Git history will be reviewed during judging.

The repository must show genuine development progress.

Do not make giant commits.

Do not make meaningless commits.

Do not commit generated files.

Do not commit temporary fixes.

---

## Commit Rule

Create a commit whenever a meaningful unit of work is completed.

Examples:

* Project initialization
* Database models completed
* State model implemented
* Workflow engine running
* First agent implemented
* Research layer added
* API contracts implemented
* Frontend workflow page completed
* Export system completed

---

## Target Commit Frequency

Every:

30–90 minutes

or

after any meaningful milestone.

---

## Good Commit Examples

feat: initialize backend architecture

feat: implement workflow state model

feat: add project creation endpoints

feat: implement challenge intelligence agent

feat: add groq provider with fallback support

feat: implement idea generation workflow node

feat: add workflow persistence layer

feat: implement idea selection checkpoint

feat: create architecture generation agent

feat: build workflow progress dashboard

feat: add export package generation

fix: correct workflow state serialization

fix: handle provider timeout fallback

refactor: extract llm service abstraction

docs: update architecture diagrams

---

## Bad Commit Examples

update

changes

fix stuff

working version

wip

final

test

asdf

---

# Development Order

Phase 1

Foundation

* Repository setup
* Backend initialization
* Frontend initialization
* Environment configuration
* Database configuration
* CI setup

Commit

---

Phase 2

Core State

* State schemas
* Workflow metadata
* Persistence models

Commit

---

Phase 3

Workflow Engine

* LangGraph setup
* Stage routing
* Retry logic
* Human checkpoints

Commit

---

Phase 4

Agent Framework

* Agent base classes
* Prompt framework
* Validation framework

Commit

---

Phase 5

Core Agents

Implement all agents one by one.

Each completed agent should result in a commit.

Commit

---

Phase 6

Research Layer

* Competitor search
* API discovery
* Open source discovery

Commit

---

Phase 7

Artifact Generation

* README generator
* PRD generator
* Architecture generator
* Pitch generator

Commit

---

Phase 8

Frontend

* Landing page
* Project creation
* Workflow visualization
* Idea selection
* Results dashboard

Commit

---

Phase 9

Polish

* Error handling
* Loading states
* Animations
* Demo mode

Commit

---

# Engineering Rules

## Rule 1

Follow documentation.

Never invent architecture.

---

## Rule 2

Keep files small and focused.

---

## Rule 3

Prefer composition over large files.

---

## Rule 4

Use typed schemas everywhere.

---

## Rule 5

Every API must follow API Contracts.

---

## Rule 6

Every agent must follow Agent Specifications.

---

## Rule 7

Every workflow transition must follow Workflow Design.

---

## Rule 8

Groq is the default provider.

Fallback order:

Groq
→ Gemini
→ Ollama
→ OpenAI

---

## Rule 9

Build for demoability.

When choosing between:

Elegant Architecture

and

Working Demo

Choose:

Working Demo

---

# Definition of Success

A successful build allows a user to:

1. Create a project
2. Start workflow
3. Generate ideas
4. Select an idea
5. Generate architecture
6. Generate build plan
7. Generate presentation
8. Generate pitch
9. Export artifacts

End-to-end without manual intervention.

---

# Final Rule

The objective is not to create the perfect system.

The objective is to create the strongest hackathon demo possible within the available time while maintaining a professional Git history.
