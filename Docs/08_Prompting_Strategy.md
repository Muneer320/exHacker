# 08_Prompting_Strategy.md

# Prompting Strategy

Project: exHacker

Version: 2.0

Status: Active

---

# Purpose

This document defines how agents interact with LLMs.

The quality of exHacker depends heavily on prompt quality.

This document ensures:

* Consistency
* Reliability
* Structured outputs
* Reduced hallucinations
* Lower token usage

Across all agents.

---

# Core Principle

Agents do not generate text.

Agents generate structured information.

The objective is not:

"Write something impressive."

The objective is:

"Produce reliable data that downstream agents can use."

---

# Golden Rule

Every prompt must optimize for:

1. Accuracy

2. Structure

3. Actionability

4. Brevity

5. Reusability

---

# Prompt Architecture

Every agent prompt follows the same structure.

```text
SYSTEM

ROLE

OBJECTIVE

CONTEXT

INPUT DATA

TASKS

OUTPUT FORMAT

VALIDATION RULES
```

---

# Standard Agent Template

```text
You are a specialized AI agent.

ROLE:
{agent_role}

OBJECTIVE:
{agent_objective}

CONTEXT:
{relevant_state}

TASKS:
{tasks}

RULES:
{rules}

OUTPUT:
Return valid JSON only.

Do not return markdown.

Do not explain reasoning.

Do not add extra text.
```

---

# Structured Output First

All agents must output JSON.

Never paragraphs.

Never essays.

Never markdown.

---

## Bad

```text
I think this idea is good because...
```

---

## Good

```json
{
  "strengths": [
    "...",
    "..."
  ],
  "risks": [
    "...",
    "..."
  ]
}
```

---

# JSON Enforcement

Every prompt ends with:

```text
Return valid JSON only.

No markdown.

No code fences.

No explanations.

No commentary.
```

---

# Schema Driven Generation

Each agent receives:

```text
INPUT STATE

OUTPUT SCHEMA
```

The model must populate the schema.

Not invent a new structure.

---

# Context Management

LLM context is expensive.

Agents should only receive:

* Relevant state
* Required outputs
* Necessary history

Never pass full workflow state.

---

## Example

Bad:

```text
Entire project state
```

---

Good:

```text
Problem Analysis

Opportunity Analysis

Team Profile
```

---

# Research First Principle

Agents should use research whenever possible.

Priority:

1. Research Results

2. State Data

3. Model Knowledge

Never the reverse.

---

# Hallucination Prevention

Agents must never:

* Invent APIs
* Invent competitors
* Invent datasets
* Invent integrations

If uncertain:

Return:

```json
{
  "confidence": "low"
}
```

Instead of guessing.

---

# Confidence Scoring

Every major output should include:

```json
{
  "confidence": 0.85
}
```

Range:

```text
0.0 → 1.0
```

---

# Agent Specific Strategies

---

## Challenge Intelligence

Focus:

Understanding.

Not solutioning.

Questions:

* What is the challenge?
* What constraints exist?
* What opportunities exist?

---

## Problem Analyst

Focus:

Problem clarity.

Not ideas.

Questions:

* Who suffers?
* Why?
* What outcome matters?

---

## Opportunity Planner

Focus:

Opportunity discovery.

Not implementation.

Questions:

* What gaps exist?
* What opportunities exist?

---

## Idea Generator

Focus:

Divergence.

Generate multiple directions.

Never optimize too early.

---

### Idea Generation Rule

Generate:

At least 5 ideas.

Then rank.

Do not stop at first good idea.

---

## Idea Validator

Focus:

Criticism.

Not encouragement.

The validator should attempt to break ideas.

Questions:

* Why will this fail?
* Why does this already exist?
* Why will users ignore it?

---

### Validator Bias

Prefer skepticism.

Not optimism.

---

## Tech Stack Advisor

Focus:

Practicality.

Questions:

* Can this team build it?
* Can it be deployed?
* Can it be demoed?

---

### Rule

Recommend boring technologies when possible.

Hackathons reward execution.

Not technological novelty.

---

## Solution Architect

Focus:

MVP architecture.

Not enterprise architecture.

---

### Rule

Optimize for:

48-hour implementation.

Not 5-year scalability.

---

## Build Accelerator

Focus:

Execution.

Outputs must be task-oriented.

Bad:

```text
Build frontend
```

Good:

```text
Create authentication pages.

Implement project creation form.

Implement workflow progress page.
```

---

## Presentation Agent

Focus:

Winning presentations.

Not documentation.

Questions:

* Why does this matter?
* Why is it innovative?
* Why should judges care?

---

## Pitch Coach

Focus:

Communication.

Not architecture.

Questions:

* What is memorable?
* What is persuasive?
* What questions will judges ask?

---

# Model Selection Strategy

Priority:

```text
1. Groq
2. Gemini
3. Ollama
4. OpenAI
```

---

# Model Usage Strategy

Simple Tasks:

```text
Groq
```

---

Medium Tasks:

```text
Gemini Flash
```

---

Complex Tasks:

```text
Gemini Pro
```

---

Fallback:

```text
OpenAI
```

---

Offline:

```text
Ollama
```

---

# Retry Strategy

If JSON parsing fails:

Retry.

Prompt:

```text
Your previous output was invalid.

Return valid JSON only.
```

---

If schema validation fails:

Retry.

Prompt:

```text
Output does not match schema.

Regenerate using exact schema.
```

---

Maximum Retries

```text
3
```

---

# Prompt Versioning

Every prompt should contain:

```python
PROMPT_VERSION = "v1"
```

This allows:

* A/B testing
* Improvements
* Regression tracking

---

# Evaluation Metrics

Track:

* JSON success rate
* Retry count
* Token usage
* Completion time
* User satisfaction

---

# Guiding Principle

Agents should think less like chatbots and more like specialized software components.

A successful prompt produces reliable structured data that improves downstream decision making.
