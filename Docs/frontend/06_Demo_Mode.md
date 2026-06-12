# Docs/frontend/06_Demo_Mode.md

# exHacker Demo Mode

Version: 1.0

Status: Active

Priority: HIGH

Audience:

* Frontend Engineers
* AI Engineers
* Hackathon Team

---

# Purpose

Demo Mode exists for one reason:

```text
Win Hackathons.
```

Not onboarding.

Not daily usage.

Not production users.

This mode is specifically designed for:

* Judges
* Evaluators
* Demo audiences
* Pitch presentations

---

# Why Demo Mode Exists

In a hackathon:

You usually get:

```text
3-5 minutes
```

to impress judges.

Most teams spend:

```text
2 minutes
```

explaining setup.

```text
1 minute
```

explaining architecture.

```text
30 seconds
```

showing results.

That is backwards.

---

Demo Mode should allow a judge to understand:

```text
Problem

↓

Process

↓

Intelligence

↓

Output

↓

Impact
```

without explanation.

---

# Core Principle

The product should tell its own story.

The presenter should only narrate.

---

# Route

```text
/demo
```

---

# Entry Options

### Option 1

Landing Page

```text
Watch Demo
```

---

### Option 2

Dashboard

```text
Launch Demo Mode
```

---

### Option 3

Results Page

```text
Present Project
```

---

# Demo Flow

Entire duration:

```text
60–90 seconds
```

Maximum.

---

# Demo Structure

```text
Challenge

↓

Problem Analysis

↓

Research

↓

Ideas

↓

Validation

↓

Architecture

↓

Build Plan

↓

Pitch

↓

Final Dashboard
```

---

# Scene 1

Challenge Intake

Duration:

```text
5 seconds
```

---

Display:

```text
Challenge Received
```

---

Animated challenge card.

Example:

```text
Build an AI solution for improving financial literacy among students.
```

---

Narration:

```text
exHacker begins by understanding the challenge.
```

---

# Scene 2

Problem Analysis

Duration:

```text
8 seconds
```

---

Problem Analyst activates.

---

Display:

```text
Stakeholders

Pain Points

Constraints

Success Metrics
```

---

Appear sequentially.

---

Example:

```text
Students

Lack of financial planning

Low engagement

Limited awareness
```

---

# Scene 3

Research Phase

Duration:

```text
10 seconds
```

---

Research Engine activates.

---

Display:

```text
Competitors Found

APIs Found

Open Source Projects Found
```

---

Cards appear live.

---

Example:

```text
YNAB

Mint

Khan Academy Finance

Plaid API

Razorpay APIs
```

---

This scene creates trust.

Judges immediately understand:

```text
This isn't a prompt wrapper.
```

---

# Scene 4

Idea Generation

Duration:

```text
12 seconds
```

---

Idea cards appear.

One by one.

---

Example:

```text
AI Finance Coach

Student Budget Assistant

Financial Habit Builder

Gamified Savings Platform

Career Planning Companion
```

---

Each card receives:

```text
Innovation

Feasibility

Differentiation
```

scores.

---

# Scene 5

Idea Selection

Duration:

```text
5 seconds
```

---

Best idea highlighted.

---

Other cards dim.

---

Display:

```text
Selected Solution
```

---

Show reason.

Example:

```text
Highest impact

Highest feasibility

Strongest differentiation
```

---

# Scene 6

Architecture Generation

Duration:

```text
10 seconds
```

---

Architecture builds itself.

---

Order:

```text
Frontend

↓

Backend

↓

Database

↓

AI Layer

↓

Integrations
```

---

Connections animate.

---

No technical explanation required.

Visual understanding only.

---

# Scene 7

Build Plan

Duration:

```text
8 seconds
```

---

Roadmap appears.

---

Example:

```text
Day 1

Research

Day 2

Backend

Day 3

Frontend

Day 4

Testing
```

---

Shows project realism.

---

# Scene 8

Pitch Generation

Duration:

```text
10 seconds
```

---

Display:

```text
30 Second Pitch

2 Minute Pitch

Judge Questions
```

---

Cards slide in.

---

Example Q&A:

```text
How is this different?

Why now?

How will users adopt it?
```

---

# Scene 9

Final Dashboard

Duration:

```text
10 seconds
```

---

Everything completed.

---

Display:

```text
Project Score

Architecture

Research

Pitch

Presentation

Export Package
```

---

This is the final frame.

---

# Presenter Controls

Always visible.

---

Buttons:

```text
Play

Pause

Restart

Skip

Previous
```

---

Keyboard Shortcuts

```text
Space → Pause

Right Arrow → Next

Left Arrow → Previous

R → Restart
```

---

# Demo Datasets

Demo Mode must never depend on backend availability.

---

Requirement:

Include:

```text
3-5 fully generated demo projects
```

inside frontend.

---

Examples:

```text
Finance AI

Healthcare AI

Education AI

Climate AI

Productivity AI
```

---

Benefits:

* No API failures during judging
* No network dependency
* Consistent presentation

---

# Demo Project Structure

Each demo project contains:

```text
Challenge

Research

Ideas

Architecture

Roadmap

Pitch

Slides
```

---

Stored as:

```text
frontend/src/demo-data/
```

---

# Demo Narration Layer

Optional.

---

Text overlay.

Example:

```text
Analyzing challenge...

Finding opportunities...

Researching competitors...

Generating ideas...

Selecting best solution...
```

---

This helps judges follow along.

---

# Judge Mode

Future enhancement.

---

Special route:

```text
/demo/judge
```

---

Displays:

```text
Problem

Innovation

Execution

Differentiation

Impact
```

alongside workflow.

---

Allows judges to score while watching.

---

# Performance Requirements

Demo Mode must:

```text
Run at 60 FPS
```

---

No loading screens.

---

No API requests.

---

No external dependencies.

---

Everything preloaded.

---

# Success Criteria

A judge should be able to understand:

```text
What exHacker does

How it works

Why it matters
```

within:

```text
90 seconds
```

without asking questions.

---

# Golden Rule

If the presenter disappeared,

Demo Mode should still successfully explain the product.
