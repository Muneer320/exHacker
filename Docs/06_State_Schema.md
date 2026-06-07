# State Schema

Project: exHacker

Version: 1.0

---

# Purpose

Defines the shared state object used by the orchestrator and all agents.

This state is the single source of truth.

Every agent:

* Reads from state
* Writes to state

No direct agent-to-agent communication is allowed.

---

# Root State

```typescript
interface ExHackerState {

  project: HackathonProject

  teamProfile?: TeamProfile

  challengeIntelligence?: ChallengeIntelligence

  problemAnalysis?: ProblemAnalysis

  opportunityAnalysis?: OpportunityAnalysis

  generatedIdeas?: Idea[]

  validationReports?: ValidationReport[]

  selectedIdea?: Idea

  architecture?: ArchitecturePackage

  techStack?: TechStack

  prompts?: PromptPackage

  presentation?: PresentationPackage

  pitch?: PitchPackage

  currentStage: WorkflowStage

  completedAgents: string[]

  errors: AgentError[]
}
```

---

# WorkflowStage

```typescript
type WorkflowStage =
  | "input"
  | "challenge_intelligence"
  | "problem_analysis"
  | "opportunity_analysis"
  | "idea_generation"
  | "idea_validation"
  | "idea_selection"
  | "architecture"
  | "tech_stack"
  | "build_acceleration"
  | "presentation"
  | "pitch"
  | "completed"
```

---

# AgentError

```typescript
interface AgentError {
  agentName: string

  timestamp: string

  message: string

  severity:
    | "warning"
    | "critical"
}
```

---

# State Mutation Rules

Only one agent can modify state at a time.

Agents may:

✓ Create fields

✓ Update fields they own

✓ Append metadata

Agents may not:

✗ Delete unrelated data

✗ Modify another agent's outputs

✗ Override user selections

---

# Human Checkpoints

Workflow pauses at:

1. Idea Selection

User chooses final idea.

2. Export

User chooses outputs.

No agent can bypass these checkpoints.

---

# State Lifecycle

Input
↓
Challenge Intelligence
↓
Problem Analysis
↓
Opportunity Analysis
↓
Idea Generation
↓
Idea Validation
↓
Human Selection
↓
Architecture
↓
Tech Stack
↓
Build Acceleration
↓
Presentation
↓
Pitch
↓
Export

The state progressively grows as agents contribute outputs.

---

# Principle

The state is the product.

Agents are temporary.

State is permanent.

Every important piece of information must exist in state.
