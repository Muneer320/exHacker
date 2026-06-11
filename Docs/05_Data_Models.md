# Data Models

Project: exHacker

Version: 1.0

---

# Purpose

This document defines all core entities used throughout the exHacker system.

These models act as the shared language between:

* Frontend
* Backend
* Database
* Agents
* Export System

All agent outputs must conform to these models.

---

# HackathonProject

Represents a user-created project.

```typescript
interface HackathonProject {
  id: string

  name: string

  challengeStatements: string[]

  durationHours: number

  createdAt: string

  updatedAt: string

  status:
    | "draft"
    | "researching"
    | "idea_generation"
    | "architecture"
    | "completed"

  team: TeamProfile

  resources: ResourceCollection

  selectedIdea?: Idea
}
```

---

# TeamProfile

```typescript
interface TeamProfile {
  teamSize: number

  experienceLevel:
    | "beginner"
    | "intermediate"
    | "advanced"

  skills: string[]

  complexityBudget:
    | "low"
    | "medium"
    | "high"

  recommendedScope:
    | "mvp"
    | "advanced_mvp"
}
```

---

# ResourceCollection

```typescript
interface ResourceCollection {
  tracks: string[]

  datasets: string[]

  apis: string[]

  documentationLinks: string[]
}
```

---

# ChallengeIntelligence

```typescript
interface ChallengeIntelligence {
  themes: string[]

  opportunities: string[]

  constraints: string[]

  resourceOpportunities: string[]

  evaluationFocus: string[]
}
```

---

# ProblemAnalysis

```typescript
interface ProblemAnalysis {
  stakeholders: string[]

  painPoints: string[]

  assumptions: string[]

  successMetrics: string[]

  problemDefinition: string
}
```

---

# OpportunityAnalysis

```typescript
interface OpportunityAnalysis {
  marketGaps: string[]

  innovationOpportunities: string[]

  highImpactAreas: string[]

  technicalOpportunities: string[]
}
```

---

# Idea

```typescript
interface Idea {
  id: string

  title: string

  description: string

  targetUsers: string[]

  keyFeatures: string[]

  innovationScore: number

  feasibilityScore: number

  hackathonFitScore: number

  technicalWowScore: number

  finalScore: number
}
```

---

# ValidationReport

```typescript
interface ValidationReport {
  ideaId: string

  competitors: Competitor[]

  openSourceProjects: OpenSourceProject[]

  availableApis: ApiResource[]

  strengths: string[]

  weaknesses: string[]

  risks: string[]

  finalScore: number
}
```

---

# Competitor

```typescript
interface Competitor {
  name: string

  description: string

  strengths: string[]

  weaknesses: string[]
}
```

---

# ArchitecturePackage

```typescript
interface ArchitecturePackage {
  vision: string

  productScope: string

  features: Feature[]

  userStories: UserStory[]

  architecture: ArchitectureDiagram

  apiDesign: ApiDefinition[]

  databaseSchema: DatabaseSchema

  integrations: Integration[]
}
```

---

# Feature

```typescript
interface Feature {
  title: string

  description: string

  priority:
    | "critical"
    | "high"
    | "medium"
    | "low"
}
```

---

# UserStory

```typescript
interface UserStory {
  actor: string

  goal: string

  benefit: string
}
```

---

# TechStack

```typescript
interface TechStack {
  frontend: string

  backend: string

  database: string

  hosting: string

  aiModels: string[]

  vectorDb?: string

  authProvider?: string
}
```

---

# PromptPackage

```typescript
interface PromptPackage {
  frontendPrompts: string[]

  backendPrompts: string[]

  databasePrompts: string[]

  aiPrompts: string[]

  testingPrompts: string[]

  deploymentPrompts: string[]
}
```

---

# PresentationPackage

```typescript
interface PresentationPackage {
  slides: Slide[]

  diagrams: Diagram[]

  demoStory: string
}
```

---

# PitchPackage

```typescript
interface PitchPackage {
  pitch30: string

  pitch120: string

  pitch300: string

  qa: QuestionAnswer[]

  demoScript: string
}
```

---

# ExportPackage

```typescript
interface ExportPackage {
  project: HackathonProject

  intelligence: ChallengeIntelligence

  problemAnalysis: ProblemAnalysis

  opportunities: OpportunityAnalysis

  architecture: ArchitecturePackage

  prompts: PromptPackage

  presentation: PresentationPackage

  pitch: PitchPackage
}
```

---

# Principle

Every agent output must map directly into one or more of these models.

No free-form outputs should exist inside the system.
