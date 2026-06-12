# Docs/frontend/02_Frontend_Architecture.md

# exHacker Frontend Architecture

Version: 1.0

Status: Active

Audience:

* Frontend Engineers
* AI Engineers

---

# Purpose

This document defines how the frontend is structured.

It does NOT define:

* Colors
* Typography
* Animations

Those belong elsewhere.

This document defines:

* Routing
* State
* Data flow
* Component hierarchy
* Folder structure

---

# Frontend Principles

The frontend must be:

* Fast
* Predictable
* Modular
* Demo-friendly

Avoid:

* Massive page files
* Prop drilling
* Business logic inside UI components

---

# Technology Stack

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

Icons:

```text
Lucide React
```

Animations:

```text
Framer Motion
```

State:

```text
Zustand
```

Data Fetching:

```text
TanStack Query
```

---

# Folder Structure

```text
frontend/src

app/

components/
    layout/
    workflow/
    agents/
    ideas/
    dashboard/
    presentation/
    pitch/
    shared/

features/
    projects/
    workflow/
    ideas/
    reports/

stores/

hooks/

services/

types/

lib/

utils/
```

---

# Routing Structure

```text
/

/new-project

/workflow/[projectId]

/ideas/[projectId]

/dashboard/[projectId]

/demo
```

Only these routes are required for MVP.

---

# Data Flow

User

↓

Page

↓

Feature Layer

↓

API Service

↓

Backend

↓

Response

↓

Store

↓

UI Update

---

# State Management

Global state only for:

* Current project
* Workflow progress
* Active idea
* Theme

Everything else should come from API.

---

# Zustand Stores

## projectStore

Contains:

```typescript
projectId
projectStatus
selectedIdea
```

---

## workflowStore

Contains:

```typescript
currentStep
activeAgent
completedAgents
workflowStatus
```

---

## uiStore

Contains:

```typescript
sidebarOpen
theme
animationsEnabled
```

---

# Feature Layer

Features own business logic.

Example:

```text
features/workflow
```

Contains:

```text
api calls
state mapping
transformations
workflow logic
```

Components should remain dumb.

---

# Services Layer

Services communicate with backend.

Example:

```typescript
projectService.create()

workflowService.start()

workflowService.status()

reportService.get()
```

No fetch calls directly inside components.

---

# Component Hierarchy

Page

↓

Feature

↓

Container Component

↓

Presentation Component

↓

UI Component

---

Example

```text
Workflow Page

↓

Workflow Feature

↓

Workflow Layout

↓

Agent Timeline

↓

Card
```

---

# Error Handling

Every page must support:

Loading

Success

Error

Empty

states.

No page should ever display a blank screen.

---

# Real-Time Updates

Workflow page should poll backend.

Target:

```text
1 second
```

interval.

Future:

WebSockets.

Not required for MVP.

---

# API Layer

Single API client.

```typescript
lib/api.ts
```

Handles:

* base URL
* auth (future)
* errors
* retries

---

# Performance Rules

Never:

* Fetch inside loops
* Create large global stores
* Render huge markdown blocks directly

Always:

* Lazy load large sections
* Use memoization when necessary
* Keep state minimal

---

# Architecture Goal

A new engineer should be able to find:

* pages
* business logic
* components
* API calls

within 30 seconds.

If navigation becomes difficult, refactor.
