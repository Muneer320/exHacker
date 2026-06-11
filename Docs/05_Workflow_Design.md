# 05_Workflow_Design.md

# Workflow Design

Project: exHacker

Version: 2.0

Status: Active

---

# Purpose

This document defines:

* Workflow execution
* Agent ordering
* State transitions
* Human checkpoints
* Failure handling
* Retry behavior
* Resume behavior

This document is the source of truth for:

* LangGraph implementation
* Workflow orchestration
* Agent execution

---

# Core Principle

The workflow is the product.

Agents are implementation details.

The value of exHacker comes from:

* Correct execution order
* Correct context flow
* Correct decision points
* Correct validation process

A great workflow with average agents is better than great agents with a poor workflow.

---

# High-Level Workflow

```text
Project Creation
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
Tech Stack Recommendation
↓
Solution Architecture
↓
Build Accelerator
↓
Presentation Generation
↓
Pitch Preparation
↓
Export
```

---

# Workflow Stages

## Stage 0

Project Initialization

---

### Inputs

User Input

Contains:

* Challenge Statements
* Team Information
* Time Constraints
* Resources

---

### Actions

Create:

* Project
* Workflow Metadata
* Initial State

---

### Output

Workflow enters:

```text
CHALLENGE_INTELLIGENCE
```

---

# Stage 1

Challenge Intelligence

---

### Agent

Challenge Intelligence Agent

---

### Inputs

```text
project
resources
```

---

### Outputs

```text
challenge_intelligence
```

---

### Next Stage

```text
PROBLEM_ANALYSIS
```

---

# Stage 2

Problem Analysis

---

### Agent

Problem Analyst

---

### Inputs

```text
challenge_intelligence
team_profile
```

---

### Outputs

```text
problem_analysis
```

---

### Next Stage

```text
OPPORTUNITY_DISCOVERY
```

---

# Stage 3

Opportunity Discovery

---

### Agent

Opportunity Planner

---

### Inputs

```text
challenge_intelligence
problem_analysis
```

---

### Outputs

```text
opportunity_analysis
```

---

### Next Stage

```text
IDEA_GENERATION
```

---

# Stage 4

Idea Generation

---

### Agent

Idea Generator

---

### Inputs

```text
challenge_intelligence
problem_analysis
opportunity_analysis
team_profile
```

---

### Outputs

```text
generated_ideas
```

---

### Validation Rule

Must generate:

Minimum:

```text
3 ideas
```

Preferred:

```text
5 ideas
```

---

### Next Stage

```text
IDEA_VALIDATION
```

---

# Stage 5

Idea Validation

---

### Agent

Idea Validator

---

### Inputs

```text
generated_ideas
```

---

### Research Required

Competitors

Open Source

APIs

Existing Products

Alternative Solutions

---

### Outputs

```text
validation_reports
```

---

### Next Stage

```text
HUMAN_SELECTION
```

---

# Stage 6

Human Selection

---

### Purpose

Human chooses final direction.

---

### User Interface

Idea Comparison Dashboard

Displays:

* Idea Scores
* Risks
* Strengths
* Weaknesses
* Competitors

---

### User Action

Select:

```text
selected_idea
```

---

### Critical Rule

Human decision is final.

No agent may override it.

---

### Next Stage

```text
TECH_STACK
```

---

# Stage 7

Tech Stack Recommendation

---

### Agent

Tech Stack Advisor

---

### Inputs

```text
selected_idea
team_profile
duration
```

---

### Outputs

```text
tech_stack
```

---

### Validation Rule

Stack must be:

* Realistic
* Buildable
* Time constrained

---

### Next Stage

```text
ARCHITECTURE
```

---

# Stage 8

Solution Architecture

---

### Agent

Solution Architect

---

### Inputs

```text
selected_idea
tech_stack
team_profile
```

---

### Outputs

```text
architecture
```

---

### Validation Rule

Architecture must support:

* MVP Scope
* Required Features
* Recommended Stack

---

### Next Stage

```text
BUILD_ACCELERATOR
```

---

# Stage 9

Build Accelerator

---

### Agent

Build Accelerator

---

### Inputs

```text
architecture
tech_stack
selected_idea
```

---

### Outputs

```text
build_package

prompt_package
```

---

### Next Stage

```text
PRESENTATION
```

---

# Stage 10

Presentation Generation

---

### Agent

Presentation Agent

---

### Inputs

```text
selected_idea
architecture
validation_reports
```

---

### Outputs

```text
presentation
```

---

### Next Stage

```text
PITCH
```

---

# Stage 11

Pitch Preparation

---

### Agent

Pitch Coach

---

### Inputs

```text
selected_idea
presentation
validation_reports
```

---

### Outputs

```text
pitch
```

---

### Next Stage

```text
EXPORT
```

---

# Stage 12

Export

---

### Purpose

Generate downloadable assets.

---

### Outputs

README

PRD

Architecture

Presentation

Pitch

Implementation Guide

ZIP Package

---

### Final Status

```text
COMPLETED
```

---

# Workflow State Machine

```text
CREATED
↓
CHALLENGE_INTELLIGENCE
↓
PROBLEM_ANALYSIS
↓
OPPORTUNITY_DISCOVERY
↓
IDEA_GENERATION
↓
IDEA_VALIDATION
↓
WAITING_FOR_SELECTION
↓
TECH_STACK
↓
ARCHITECTURE
↓
BUILD_ACCELERATOR
↓
PRESENTATION
↓
PITCH
↓
EXPORT
↓
COMPLETED
```

---

# Human Checkpoints

Current Mandatory Checkpoints

---

## Idea Selection

Required.

User must select final idea.

Workflow pauses until selection.

---

# Future Checkpoints

Potential:

* Architecture Approval
* Presentation Approval
* Pitch Approval

Not implemented in v2.

---

# Retry Strategy

Every agent execution supports:

Maximum Retries:

```text
3
```

---

## Retry Flow

```text
Agent Failure
↓
Retry #1
↓
Retry #2
↓
Retry #3
↓
Fail Workflow
```

---

# Failure States

Workflow may enter:

```text
FAILED
```

When:

* Agent repeatedly fails
* State corruption detected
* Required output missing

---

# Recovery Strategy

User may:

* Resume workflow
* Re-run failed stage
* Restart workflow

---

# Persistence Requirements

State must be saved:

After every completed stage.

---

## Why

Allows:

* Crash recovery
* Resume support
* Audit trail
* Progress tracking

---

# Workflow Metadata

Track:

* Start Time
* End Time
* Current Stage
* Completed Stages
* Failed Stages
* Retry Count
* Agent Durations
* Token Usage
* Cost Metrics

---

# Performance Targets

Challenge Intelligence

< 30 sec

---

Problem Analysis

< 30 sec

---

Opportunity Discovery

< 30 sec

---

Idea Generation

< 60 sec

---

Idea Validation

< 120 sec

---

Architecture

< 60 sec

---

Presentation

< 60 sec

---

Pitch

< 30 sec

---

Full Workflow

Target:

< 5 minutes

Maximum:

< 10 minutes

---

# LangGraph Requirements

Workflow Engine Must Support:

* Directed execution
* Conditional routing
* Human pauses
* Resume support
* Persistence
* Retry handling
* Observability

LangGraph is responsible for orchestration.

Agents should remain unaware of workflow logic.

---

# Future Workflow Extensions

Potential future modes:

Hackathon Mode

Startup Mode

Grant Mode

Accelerator Mode

Product Discovery Mode

Each mode should reuse the same workflow engine while swapping workflow definitions.

---

# Guiding Principle

Agents create information.

The workflow creates value.

The workflow should always optimize for helping a team reach implementation as quickly and confidently as possible.
