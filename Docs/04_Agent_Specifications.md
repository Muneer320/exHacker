# 04_Agent_Specifications.md

# Agent Specifications

Project: exHacker

Version: 2.0

Status: Active

---

# Purpose

This document defines every agent in the system.

For each agent:

* Responsibilities
* Inputs
* Outputs
* State Access
* Success Criteria
* Failure Conditions

This document acts as the contract between:

* Workflow Engine
* Agents
* State Management

---

# General Agent Rules

All agents must follow these rules.

---

## Input Rule

Agents receive:

* Shared State
* Configuration
* Context

Agents must never directly call another agent.

---

## Output Rule

Agents must return structured outputs.

No free-form responses.

All outputs must match schemas.

---

## State Rule

Agents:

May:

* Read state
* Update their assigned domain

May Not:

* Modify unrelated domains
* Delete user decisions
* Override selected ideas

---

## Retry Rule

Maximum retries:

3

After 3 failures:

Workflow marked failed.

---

# Agent 1

Challenge Intelligence Agent

---

## Purpose

Understand the challenge.

Identify:

* Themes
* Constraints
* Opportunities
* Evaluation criteria

---

## Inputs

```text
project.challenge_statements

project.resources
```

---

## Outputs

```text
challenge_intelligence
```

Contains:

* themes
* constraints
* opportunities
* evaluation_factors
* technical_opportunities

---

## State Access

Read:

```text
project
resources
```

Write:

```text
challenge_intelligence
```

---

## Success Criteria

Challenge can be clearly understood by later agents.

---

# Agent 2

Problem Analyst

---

## Purpose

Convert challenge into a structured problem.

---

## Inputs

```text
challenge_intelligence

team_profile
```

---

## Outputs

```text
problem_analysis
```

Contains:

* stakeholders
* pain_points
* assumptions
* success_metrics
* refined_problem_statement

---

## State Access

Read:

```text
challenge_intelligence
team_profile
```

Write:

```text
problem_analysis
```

---

## Success Criteria

Problem becomes specific and measurable.

---

# Agent 3

Opportunity Planner

---

## Purpose

Identify valuable opportunities.

---

## Inputs

```text
challenge_intelligence

problem_analysis
```

---

## Outputs

```text
opportunity_analysis
```

Contains:

* market_gaps
* innovation_opportunities
* technical_opportunities
* impact_opportunities

---

## State Access

Read:

```text
challenge_intelligence

problem_analysis
```

Write:

```text
opportunity_analysis
```

---

## Success Criteria

Produces multiple promising directions.

---

# Agent 4

Idea Generator

---

## Purpose

Generate project concepts.

---

## Inputs

```text
challenge_intelligence

problem_analysis

opportunity_analysis

team_profile
```

---

## Outputs

```text
generated_ideas
```

Minimum:

3 ideas

Preferred:

5 ideas

---

## Per Idea

Contains:

* title
* description
* target_users
* key_features
* innovation_score

---

## State Access

Read:

```text
challenge_intelligence

problem_analysis

opportunity_analysis

team_profile
```

Write:

```text
generated_ideas
```

---

## Success Criteria

Produces multiple viable projects.

---

# Agent 5

Idea Validator

---

## Purpose

Validate generated ideas.

---

## Inputs

```text
generated_ideas
```

Research:

* competitors
* startups
* APIs
* open source projects
* similar products

---

## Outputs

```text
validation_reports
```

Per Idea:

* strengths
* weaknesses
* risks
* feasibility_score
* innovation_score
* final_score

---

## State Access

Read:

```text
generated_ideas
```

Write:

```text
validation_reports
```

---

## Success Criteria

Provides evidence-backed evaluation.

---

# Human Checkpoint

Idea Selection

---

## Purpose

Human chooses final direction.

---

## Inputs

```text
generated_ideas

validation_reports
```

---

## Output

```text
selected_idea
```

---

## Critical Rule

User decision is final.

No agent may override it.

---

# Agent 6

Tech Stack Advisor

---

## Purpose

Recommend technologies.

---

## Inputs

```text
selected_idea

team_profile

project.duration
```

---

## Outputs

```text
tech_stack
```

Contains:

* frontend
* backend
* database
* ai_stack
* deployment
* reasoning

---

## Success Criteria

Stack is realistic for available time.

---

# Agent 7

Solution Architect

---

## Purpose

Design implementation architecture.

---

## Inputs

```text
selected_idea

tech_stack

team_profile
```

---

## Outputs

```text
architecture
```

Contains:

* system_design
* components
* modules
* data_flow
* api_design
* database_design
* integrations
* mvp_scope
* future_scope

---

## Success Criteria

Team can begin implementation.

---

# Agent 8

Build Accelerator

---

## Purpose

Convert architecture into execution tasks.

---

## Inputs

```text
architecture

tech_stack

selected_idea
```

---

## Outputs

```text
build_package
```

Contains:

* frontend_tasks
* backend_tasks
* database_tasks
* testing_tasks
* deployment_tasks

---

## Additional Output

```text
prompt_package
```

Contains:

* frontend_prompts
* backend_prompts
* database_prompts
* testing_prompts
* deployment_prompts

---

## Success Criteria

Developers can immediately begin work.

---

# Agent 9

Presentation Agent

---

## Purpose

Create presentation materials.

---

## Inputs

```text
selected_idea

architecture

validation_reports
```

---

## Outputs

```text
presentation
```

Contains:

* slide_order
* slide_content
* architecture_slides
* demo_story
* business_story

---

## Success Criteria

Ready-to-build presentation.

---

# Agent 10

Pitch Coach

---

## Purpose

Prepare final presentation delivery.

---

## Inputs

```text
selected_idea

presentation

validation_reports
```

---

## Outputs

```text
pitch
```

Contains:

* 30_second_pitch
* 2_minute_pitch
* 5_minute_pitch
* judge_questions
* suggested_answers
* demo_script

---

## Success Criteria

Team is prepared for judging.

---

# Agent Execution Order

```text
Challenge Intelligence
↓
Problem Analyst
↓
Opportunity Planner
↓
Idea Generator
↓
Idea Validator
↓
Human Selection
↓
Tech Stack Advisor
↓
Solution Architect
↓
Build Accelerator
↓
Presentation Agent
↓
Pitch Coach
```

---

# Future Agents

Potential future agents:

* UI/UX Designer
* Market Research Agent
* Startup Advisor
* Grant Writer
* Business Model Generator
* Financial Planner

These should integrate through the workflow engine and shared state.

---

# Agent Design Principles

1. Single Responsibility

Each agent should do one thing well.

---

2. Structured Outputs

No free-form outputs.

---

3. Replaceable

Agents should be replaceable without changing the workflow.

---

4. Stateless Execution

Agents should not store internal memory.

Shared state is the source of truth.

---

5. Independent Testing

Every agent must be testable in isolation.

---

6. Research-Backed Decisions

Agents should rely on evidence whenever possible.

Avoid hallucinated recommendations.
