# Docs/frontend/07_Frontend_Implementation_Guide.md

# exHacker Frontend Implementation Guide

Version: 1.0

Status: Active

Priority: CRITICAL

Audience:

* AI Engineers
* Frontend Engineers

---

# Purpose

This document defines:

* What to build
* In what order to build it
* What can be skipped
* What is mandatory

This is the execution guide.

If implementation decisions conflict with other frontend docs:

```text
Follow this document.
```

---

# Development Philosophy

Goal:

```text
Maximum visual impact.
Minimum implementation complexity.
```

Remember:

This is a hackathon.

Not a SaaS startup.

Not a production platform.

Not a 3-year roadmap.

---

# MVP Goal

The MVP should successfully demonstrate:

```text
Challenge Input

↓

AI Workflow

↓

Idea Generation

↓

Idea Selection

↓

Project Package
```

Nothing else matters initially.

---

# Tech Stack

Framework:

```text
Next.js 15
```

Language:

```text
TypeScript
```

Styling:

```text
TailwindCSS
```

Components:

```text
shadcn/ui
```

Animations:

```text
Framer Motion
```

State:

```text
Zustand
```

API:

```text
TanStack Query
```

Icons:

```text
Lucide React
```

---

# Directory Structure

```text
frontend/src

app/

components/
    shared/
    layout/
    landing/
    workflow/
    agents/
    ideas/
    dashboard/
    presentation/
    pitch/
    demo/

features/

stores/

hooks/

services/

types/

lib/
```

---

# Implementation Order

Do NOT build randomly.

Follow this order.

---

# Phase 1

Foundation

Priority:

```text
CRITICAL
```

---

Tasks:

### Setup Design System

Create:

```text
tailwind theme
colors
spacing
typography
```

---

### Setup Layout

Create:

```text
Navbar
PageContainer
PageHeader
```

---

### Setup Shared Components

Create:

```text
Button
Card
StatusBadge
LoadingState
EmptyState
```

---

Commit:

```text
feat(frontend): establish design system and shared components
```

---

# Phase 2

Landing Page

Priority:

```text
HIGH
```

---

Build:

```text
HeroSection
WorkflowPreview
FeatureGrid
CTASection
```

---

Route:

```text
/
```

---

Must look polished.

---

Commit:

```text
feat(frontend): implement landing page experience
```

---

# Phase 3

Project Creation

Priority:

```text
HIGH
```

---

Route:

```text
/new-project
```

---

Build:

```text
ChallengeForm
TeamSection
ConstraintSection
ReviewStep
```

---

Store:

```text
projectStore
```

---

Commit:

```text
feat(frontend): add project onboarding workflow
```

---

# Phase 4

Workflow Command Center

Priority:

```text
CRITICAL
```

---

Route:

```text
/workflow/[projectId]
```

---

Build:

```text
WorkflowTimeline

AgentCard

AgentActivityFeed

WorkflowFooter

StatePreview
```

---

This is the showcase page.

Spend the most effort here.

---

Commit:

```text
feat(frontend): implement workflow command center
```

---

# Phase 5

Idea Selection

Priority:

```text
HIGH
```

---

Route:

```text
/ideas/[projectId]
```

---

Build:

```text
IdeaCard

IdeaComparison

IdeaSelector
```

---

Commit:

```text
feat(frontend): add idea evaluation and selection experience
```

---

# Phase 6

Results Dashboard

Priority:

```text
CRITICAL
```

---

Route:

```text
/dashboard/[projectId]
```

---

Build:

```text
OverviewTab

ArchitectureTab

ResearchTab

PitchTab

PresentationTab

ExportTab
```

---

Commit:

```text
feat(frontend): implement final project dashboard
```

---

# Phase 7

Demo Mode

Priority:

```text
VERY HIGH
```

---

Route:

```text
/demo
```

---

Build:

```text
DemoPlayer

DemoTimeline

DemoOverlay
```

---

Use static mock data first.

---

Commit:

```text
feat(frontend): add automated demo mode
```

---

# Phase 8

Animation Pass

Priority:

```text
VERY HIGH
```

---

Implement:

```text
Timeline animations

Agent activity animations

Idea generation animations

Dashboard transitions

Page transitions
```

---

No new features.

Only polish.

---

Commit:

```text
feat(frontend): add workflow and dashboard animations
```

---

# Phase 9

Backend Integration

Priority:

```text
HIGH
```

---

Connect:

```text
Create Project

Workflow Status

Idea Selection

Results Dashboard
```

---

Use:

```text
services/
```

layer only.

---

Never call backend directly from components.

---

Commit:

```text
feat(frontend): integrate backend workflow APIs
```

---

# Phase 10

Hackathon Polish

Priority:

```text
MAXIMUM
```

---

Add:

```text
Loading states

Skeletons

Empty states

Error states

Micro-interactions
```

---

Review every page.

---

Commit:

```text
feat(frontend): complete hackathon presentation polish
```

---

# Mock Data Strategy

Until backend is stable:

Create:

```text
src/mock/
```

---

Include:

```text
sampleChallenge

sampleResearch

sampleIdeas

sampleArchitecture

samplePitch
```

---

Frontend development should never block.

---

# Performance Rules

Never:

```text
Fetch in components

Use giant Zustand stores

Store API responses everywhere

Render huge markdown blocks directly
```

---

Always:

```text
Memoize expensive renders

Use loading skeletons

Use lazy loading
```

---

# Accessibility

Minimum requirements:

```text
Keyboard navigation

Focus states

Semantic HTML

Color contrast
```

---

No need for enterprise-level compliance.

---

# Mobile Support

Required:

```text
Responsive layouts

Readable content

Working navigation
```

---

Not Required:

```text
Perfect workflow visualizations
```

Desktop-first.

---

# Success Metrics

Frontend MVP is complete when:

* Landing page looks premium
* Workflow page feels alive
* Idea selection feels interactive
* Dashboard feels comprehensive
* Demo mode can impress judges without backend

---

# Final Hackathon Rule

If time runs out:

Prioritize:

```text
Workflow Page

↓

Dashboard

↓

Demo Mode

↓

Landing Page

↓

Everything Else
```

Those four screens win hackathons.

Everything else is optimization.
