# Docs/frontend/04_Component_Specifications.md

# exHacker Component Specifications

Version: 1.0

Status: Active

Audience:

* Frontend Engineers
* Designers
* AI Engineers

---

# Purpose

This document defines all reusable frontend components.

The goal is:

* Consistency
* Reusability
* Predictable implementation

No page should invent its own component if an existing component can be reused.

---

# Component Hierarchy

```text
UI Components

↓

Shared Components

↓

Feature Components

↓

Page Layouts

↓

Pages
```

---

# UI Components

Built on top of:

```text
shadcn/ui
```

Examples:

```text
Button

Card

Badge

Input

Textarea

Dialog

Tabs

Tooltip

Skeleton

Progress
```

These should remain generic.

No business logic.

---

# Shared Components

Reusable throughout the app.

Location:

```text
components/shared
```

---

# PageHeader

Purpose:

Consistent page headers.

Props:

```typescript
title
description
actions
```

Used in:

* Dashboard
* Workflow
* Research

---

# EmptyState

Purpose:

Display empty screens.

Props:

```typescript
title
description
icon
action
```

---

# LoadingState

Purpose:

Consistent loading UI.

Variants:

```text
page
card
section
```

---

# StatusBadge

Purpose:

Workflow statuses.

Variants:

```text
Running

Completed

Waiting

Failed
```

---

# Agent Components

Location:

```text
components/agents
```

---

# AgentCard

Purpose:

Display agent status.

Most frequently used component.

---

Props:

```typescript
name
description
status
progress
currentTask
```

---

States:

```text
Waiting

Running

Completed

Failed
```

---

Visual Elements

* Agent icon
* Agent color
* Status indicator
* Current action
* Progress

---

# AgentActivityFeed

Purpose:

Live activity logs.

Example:

```text
Researching competitors...

Found 12 APIs...

Ranking ideas...
```

Auto-scroll.

---

# AgentAvatar

Purpose:

Agent identity.

Not a literal avatar.

Shows:

* icon
* color
* role

---

# Workflow Components

Location:

```text
components/workflow
```

---

# WorkflowTimeline

Purpose:

Visualize workflow stages.

---

Props:

```typescript
steps
currentStep
completedSteps
```

---

Displays:

```text
Challenge Intelligence

Problem Analysis

Research

Idea Generation

Validation

Architecture

Pitch
```

---

# WorkflowStep

Child component.

Single timeline item.

Contains:

* name
* icon
* status

---

# WorkflowProgress

Purpose:

Overall workflow progress.

Displays:

```text
72%

7/10 Steps Completed
```

---

# WorkflowFooter

Displays:

* elapsed time
* active agent
* completion estimate

---

# Idea Components

Location:

```text
components/ideas
```

---

# IdeaCard

Purpose:

Show generated idea.

Core component.

---

Props:

```typescript
idea
```

---

Displays:

Title

Description

Innovation

Feasibility

Complexity

Differentiation

---

Expandable Sections:

```text
Strengths

Weaknesses

Risks

Competitors

APIs
```

---

# IdeaComparison

Purpose:

Compare ideas side-by-side.

Desktop only.

---

# IdeaSelector

Purpose:

Handles selection.

States:

```text
Selected

Not Selected

Locked
```

---

# Research Components

Location:

```text
components/research
```

---

# ResearchPanel

Purpose:

Display research results.

---

Contains:

Competitors

APIs

Open Source Projects

Insights

---

# CompetitorCard

Displays:

* name
* description
* strengths
* weaknesses

---

# ApiCard

Displays:

* API name
* purpose
* pricing
* documentation link

---

# OSSProjectCard

Displays:

* project
* stars
* relevance
* repo link

---

# Dashboard Components

Location:

```text
components/dashboard
```

---

# ProjectScoreCard

Purpose:

Display overall score.

Example:

```text
87 / 100
```

---

# OverviewPanel

Displays:

* problem
* solution
* summary

---

# ExportPanel

Contains:

```text
Export README

Export PRD

Export Architecture

Export Pitch

Export Package
```

---

# Architecture Components

Location:

```text
components/architecture
```

---

# ArchitectureViewer

Purpose:

Visualize system design.

---

Displays:

* architecture diagram
* service cards
* data flow

---

# ArchitectureNode

Represents:

Frontend

Backend

Database

AI Layer

External APIs

---

# MermaidRenderer

Purpose:

Render generated Mermaid diagrams.

Supports:

```text
flowchart

sequence

architecture
```

---

# Presentation Components

Location:

```text
components/presentation
```

---

# SlidePreview

Purpose:

Single slide preview.

---

Displays:

* slide number
* title
* thumbnail

---

# SlideGrid

Purpose:

Display all generated slides.

---

# PresentationViewer

Purpose:

Full-screen preview.

---

# Pitch Components

Location:

```text
components/pitch
```

---

# PitchCard

Purpose:

Display pitch.

Variants:

```text
30 Seconds

2 Minutes

5 Minutes
```

---

# QnACard

Purpose:

Judge preparation.

Displays:

Question

Suggested Answer

Confidence

---

# Landing Components

Location:

```text
components/landing
```

---

# HeroSection

Contains:

Headline

Subheadline

CTA

---

# WorkflowPreview

Animated workflow visualization.

---

# FeatureGrid

Displays:

AI Team

Research Engine

Build Package

---

# StatsBar

Displays:

```text
Agents

Research Sources

Artifacts Generated
```

---

# Demo Components

Location:

```text
components/demo
```

---

# DemoPlayer

Controls:

Play

Pause

Restart

Skip

---

# DemoTimeline

Shows demo progression.

---

# DemoOverlay

Displays narration.

Example:

```text
Challenge received.

Analyzing requirements...

Generating ideas...
```

---

# Component Rules

## Rule 1

Components should be reusable.

---

## Rule 2

Components should be presentation-focused.

Business logic belongs in features.

---

## Rule 3

No direct API calls in components.

---

## Rule 4

No workflow state manipulation inside UI.

Use stores/features.

---

## Rule 5

Every component must support:

```text
Loading

Empty

Error

Success
```

states where applicable.

---

# Golden Rule

A component should do one thing extremely well.

If a component requires more than 12–15 props,

it should probably be split into smaller components.
