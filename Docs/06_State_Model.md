# 06_State_Model.md

# State Model

Project: exHacker

Version: 2.0

Status: Active

---

# Purpose

This document defines the shared state model used by the workflow engine.

The state is the single source of truth for the entire platform.

Every component interacts through state.

This includes:

* Workflow Engine
* Agents
* API Layer
* Persistence Layer
* Frontend
* Artifact Generation

---

# Core Principle

The state is the product.

Agents are temporary.

Workflows are temporary.

State is permanent.

If information matters, it should exist in state.

---

# State Ownership Model

Agents do not communicate directly.

Bad:

```text
Agent A
 ↓
Agent B
 ↓
Agent C
```

Good:

```text
Agent A
 ↓
State
 ↑
Agent B
 ↓
State
 ↑
Agent C
```

This ensures:

* Loose coupling
* Easier testing
* Easier debugging
* Better persistence
* Better recovery

---

# Root State

```typescript
interface ExHackerState {
    metadata: WorkflowMetadata

    project: Project

    team_profile?: TeamProfile

    challenge_intelligence?: ChallengeIntelligence

    problem_analysis?: ProblemAnalysis

    opportunity_analysis?: OpportunityAnalysis

    generated_ideas?: Idea[]

    validation_reports?: ValidationReport[]

    selected_idea?: Idea

    tech_stack?: TechStack

    architecture?: ArchitecturePackage

    build_package?: BuildPackage

    prompt_package?: PromptPackage

    presentation?: PresentationPackage

    pitch?: PitchPackage

    exports?: ExportPackage

    execution?: ExecutionMetadata

    errors?: WorkflowError[]
}
```

---

# Metadata Domain

Purpose:

Workflow tracking.

```typescript
interface WorkflowMetadata {
    workflow_id: string

    project_id: string

    status: WorkflowStatus

    current_stage: WorkflowStage

    created_at: string

    updated_at: string
}
```

---

# Workflow Status

```typescript
type WorkflowStatus =
    | "created"
    | "running"
    | "waiting_for_user"
    | "completed"
    | "failed"
```

---

# Workflow Stage

```typescript
type WorkflowStage =
    | "challenge_intelligence"
    | "problem_analysis"
    | "opportunity_discovery"
    | "idea_generation"
    | "idea_validation"
    | "human_selection"
    | "tech_stack"
    | "architecture"
    | "build_accelerator"
    | "presentation"
    | "pitch"
    | "export"
```

---

# Project Domain

Stores user input.

```typescript
interface Project {
    id: string

    name: string

    challenge_statements: string[]

    duration_hours: number

    resources?: Resource[]

    created_at: string
}
```

---

# Team Profile Domain

```typescript
interface TeamProfile {
    team_size: number

    experience_level: string

    known_technologies: string[]

    preferred_technologies: string[]
}
```

---

# Challenge Intelligence Domain

Owner:

Challenge Intelligence Agent

```typescript
interface ChallengeIntelligence {
    themes: string[]

    constraints: string[]

    opportunities: string[]

    evaluation_factors: string[]

    technical_opportunities: string[]
}
```

---

# Problem Analysis Domain

Owner:

Problem Analyst

```typescript
interface ProblemAnalysis {
    stakeholders: string[]

    pain_points: string[]

    assumptions: string[]

    success_metrics: string[]

    refined_problem_statement: string
}
```

---

# Opportunity Analysis Domain

Owner:

Opportunity Planner

```typescript
interface OpportunityAnalysis {
    market_gaps: string[]

    innovation_opportunities: string[]

    technical_opportunities: string[]

    impact_opportunities: string[]
}
```

---

# Generated Ideas Domain

Owner:

Idea Generator

```typescript
interface Idea {
    id: string

    title: string

    description: string

    target_users: string[]

    key_features: string[]

    innovation_score: number
}
```

---

# Validation Domain

Owner:

Idea Validator

```typescript
interface ValidationReport {
    idea_id: string

    competitors: Competitor[]

    open_source_projects: OpenSourceProject[]

    apis: ApiResource[]

    strengths: string[]

    weaknesses: string[]

    risks: string[]

    feasibility_score: number

    innovation_score: number

    final_score: number
}
```

---

# Selected Idea Domain

Owner:

Human User

```typescript
selected_idea: Idea
```

Critical Rule:

User selection is immutable.

No agent may override it.

---

# Tech Stack Domain

Owner:

Tech Stack Advisor

```typescript
interface TechStack {
    frontend: string

    backend: string

    database: string

    ai_stack: string[]

    deployment: string[]

    reasoning: string[]
}
```

---

# Architecture Domain

Owner:

Solution Architect

```typescript
interface ArchitecturePackage {
    system_design: string

    components: Component[]

    modules: Module[]

    api_design: ApiDefinition[]

    database_design: DatabaseDesign

    integrations: Integration[]

    mvp_scope: string[]

    future_scope: string[]
}
```

---

# Build Package Domain

Owner:

Build Accelerator

```typescript
interface BuildPackage {
    frontend_tasks: string[]

    backend_tasks: string[]

    database_tasks: string[]

    testing_tasks: string[]

    deployment_tasks: string[]
}
```

---

# Prompt Package Domain

Owner:

Build Accelerator

```typescript
interface PromptPackage {
    frontend_prompts: string[]

    backend_prompts: string[]

    database_prompts: string[]

    testing_prompts: string[]

    deployment_prompts: string[]
}
```

---

# Presentation Domain

Owner:

Presentation Agent

```typescript
interface PresentationPackage {
    slide_order: string[]

    slide_content: Slide[]

    demo_story: string

    business_story: string
}
```

---

# Pitch Domain

Owner:

Pitch Coach

```typescript
interface PitchPackage {
    pitch_30s: string

    pitch_2m: string

    pitch_5m: string

    judge_questions: QA[]

    demo_script: string
}
```

---

# Export Domain

Owner:

Export System

```typescript
interface ExportPackage {
    readme: string

    architecture_doc: string

    presentation_doc: string

    pitch_doc: string

    implementation_guide: string
}
```

---

# Execution Metadata

Purpose:

Observability.

```typescript
interface ExecutionMetadata {
    total_duration_seconds: number

    total_tokens: number

    total_cost: number

    provider_usage: ProviderUsage[]

    stage_metrics: StageMetric[]
}
```

---

# Error Domain

Purpose:

Workflow recovery.

```typescript
interface WorkflowError {
    stage: string

    timestamp: string

    message: string

    retry_count: number
}
```

---

# State Mutation Rules

---

## Rule 1

Agents may only write to their own domains.

Example:

Challenge Intelligence Agent

May Write:

```text
challenge_intelligence
```

May Not Write:

```text
architecture

presentation

pitch
```

---

## Rule 2

Agents may read any previously completed domain.

---

## Rule 3

Agents may not delete state.

---

## Rule 4

Agents may not overwrite user decisions.

---

## Rule 5

Every state mutation must be persisted.

---

# Persistence Requirements

Persist state:

* After every completed stage
* Before every human checkpoint
* Before export

This enables:

* Resume support
* Recovery
* Auditing

---

# Database Representation

Recommended:

```text
projects

workflow_states

agent_runs

exports

execution_logs
```

The database stores snapshots of state.

The workflow engine reconstructs state from persistence.

---

# Frontend Usage

Frontend should consume state through APIs.

Frontend should never reconstruct workflow state itself.

The backend remains the authority.

---

# Future Extensions

Future domains may include:

* Team Collaboration
* Multi-Agent Conversations
* Startup Planning
* Grant Writing
* Business Modeling

These should be added as new domains rather than modifying existing domains whenever possible.

---

# Guiding Principle

Every important piece of information generated during a workflow should exist exactly once inside the shared state.

State duplication should be avoided.

State is the source of truth.
