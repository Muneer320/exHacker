# Docs/frontend/03_Page_Specifications.md

# exHacker Page Specifications

Version: 1.0

Status: Active

Audience:

* Frontend Engineers
* Designers
* AI Engineers

---

# Purpose

This document defines every page in the MVP.

The goal is to ensure:

* Consistent UX
* Consistent visual hierarchy
* Consistent implementation

The frontend should be built exactly from these specifications.

---

# Page Flow

```text
Landing

↓

New Project

↓

Workflow Command Center

↓

Idea Selection

↓

Results Dashboard

↓

Export
```

Additional route:

```text
Demo Mode
```

---

# 1. Landing Page

Route:

```text
/
```

Purpose:

* Explain product instantly
* Convince user to start
* Show AI workflow visually

---

## Layout

```text
Navbar

↓

Hero

↓

Workflow Preview

↓

Features

↓

CTA
```

---

## Hero Section

Full screen.

Contains:

### Headline

```text
Build Better Hackathon Projects.
In Minutes.
```

---

### Subheadline

```text
Challenge → Ideas → Validation →
Architecture → Pitch → Presentation
```

---

### CTA

Primary:

```text
Start Building
```

Secondary:

```text
Watch Demo
```

---

### Background

Animated grid.

Subtle particles.

Floating workflow connections.

Never distracting.

---

## Workflow Preview

Visual workflow.

```text
Challenge

↓

Analysis

↓

Research

↓

Ideas

↓

Architecture

↓

Pitch
```

Animated.

Nodes glow on hover.

---

## Features Section

3 Cards.

### AI Team

Multiple specialized agents.

---

### Research Engine

Competitors, APIs, OSS.

---

### Build Package

Architecture, roadmap, pitch, slides.

---

# 2. New Project Page

Route:

```text
/new-project
```

Purpose:

Collect project information.

Should feel like onboarding.

Not a form.

---

## Layout

Centered container.

Large cards.

Step-based progression.

---

## Step 1

Challenge

Fields:

* Problem statement
* Theme
* Rules

---

## Step 2

Team

Fields:

* Team size
* Skills
* Experience

---

## Step 3

Constraints

Fields:

* Hackathon duration
* Available tools
* Preferred technologies

---

## Step 4

Review

Summary screen.

Button:

```text
Launch AI Team
```

---

# 3. Workflow Command Center

Route:

```text
/workflow/[projectId]
```

Purpose:

Most important page.

This is the judge-winning screen.

Must feel alive.

---

# Layout

Three-column layout.

```text
Left
Timeline

Center
Agent Activity

Right
State Preview
```

---

# Left Panel

Workflow Timeline

Shows:

```text
Challenge Intelligence

Problem Analysis

Research

Idea Generation

Idea Validation

Selection

Architecture

Build Plan

Presentation

Pitch
```

Each stage:

* Waiting
* Running
* Complete
* Failed

---

# Center Panel

Agent Activity

Large focus area.

Displays currently active agent.

---

Example

```text
Problem Analyst

Analyzing stakeholders...
Identifying constraints...
Extracting opportunities...
```

---

Agent card includes:

* Name
* Description
* Progress
* Output preview

---

# Right Panel

State Preview

Live updates.

Examples:

```text
Current Problem

Current Opportunities

Generated Ideas

Selected Idea
```

Updates in real time.

---

# Workflow Footer

Shows:

```text
Elapsed Time

Current Agent

Progress %

Estimated Completion
```

---

# 4. Idea Selection Page

Route:

```text
/ideas/[projectId]
```

Purpose:

Allow user to choose idea.

This page must feel premium.

---

# Layout

Top summary.

Below:

Grid of idea cards.

---

## Idea Card

Contains:

Title

Tagline

Innovation Score

Feasibility Score

Complexity Score

Differentiation Score

---

Expandable Section:

### Strengths

### Weaknesses

### Risks

### Competitors

### APIs

---

Primary CTA:

```text
Select Idea
```

---

# Selection Interaction

When selected:

* Card expands
* Others dim
* Confirmation modal appears

Then:

```text
Continue Workflow
```

---

# 5. Results Dashboard

Route:

```text
/dashboard/[projectId]
```

Purpose:

Show final deliverables.

This is the final demo page.

---

# Layout

```text
Header

↓

Project Overview

↓

Tabbed Workspace
```

---

# Header

Displays:

Project Name

Overall Score

Generated Date

Export Button

---

# Overview Section

Contains:

Problem

Solution

Tech Stack

Summary

---

# Tabs

## Overview

High-level summary.

---

## Architecture

Visual architecture.

Mermaid diagram.

System cards.

Data flow.

---

## Build Plan

Timeline.

Milestones.

Task groups.

---

## Tech Stack

Frontend

Backend

Database

AI

Infrastructure

Each explained.

---

## Presentation

Slide previews.

Thumbnail grid.

Open slide details.

---

## Pitch

30 seconds

2 minutes

5 minutes

Judge Q&A

---

## Research

Competitors

APIs

Open Source Projects

Market Insights

---

# Export Actions

Generate:

```text
README

PRD

Architecture

Pitch

Presentation

Full Package
```

---

# 6. Demo Mode

Route:

```text
/demo
```

Purpose:

Hackathon presentation mode.

Designed specifically for judges.

---

# Layout

Single-page experience.

Minimal controls.

Large visuals.

---

# Demo Flow

Step 1

Challenge appears.

---

Step 2

Workflow starts automatically.

---

Step 3

Agents activate one by one.

---

Step 4

Ideas appear.

---

Step 5

Best idea selected.

---

Step 6

Architecture generated.

---

Step 7

Pitch generated.

---

Step 8

Final dashboard shown.

---

# Demo Controls

Pause

Resume

Restart

Skip

---

# Timing

Entire demo:

```text
60–90 seconds
```

Maximum.

---

# Mobile Experience

Not primary.

Required:

* Responsive layouts
* Readable cards
* Basic navigation

Not required:

* Full workflow visualization

Desktop-first design.

---

# Page Priority

Priority 1

Workflow Command Center

---

Priority 2

Results Dashboard

---

Priority 3

Idea Selection

---

Priority 4

Landing Page

---

Priority 5

Demo Mode

---

# Golden Rule

If a judge only sees:

* Landing Page
* Workflow Command Center
* Results Dashboard

for 2 minutes,

they should completely understand the value of exHacker.
