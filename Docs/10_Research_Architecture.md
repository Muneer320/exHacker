# Research Architecture

Project: exHacker

Version: 2.0

Status: Active

---

# Purpose

Research is the biggest differentiator between:

* Generic AI planning
* Evidence-backed project planning

Most hackathon assistants generate ideas.

Very few validate them.

exHacker should behave more like a researcher than a chatbot.

---

# Research Philosophy

Bad:

```text
Generate idea
→ Looks cool
→ Recommend it
```

Good:

```text
Generate idea
↓
Research market
↓
Research competitors
↓
Research APIs
↓
Research open source
↓
Score idea
↓
Recommend
```

---

# Research System Overview

```text
Idea
 ↓

Research Coordinator
 │
 ├── Competitor Search
 ├── API Discovery
 ├── Open Source Discovery
 ├── Startup Discovery
 └── Market Signals

 ↓

Research Report

 ↓

Idea Validator
```

---

# Research Sources

---

## Competitor Research

Purpose:

Determine whether idea already exists.

Search For:

* Startups
* SaaS Products
* Mobile Apps
* Existing Platforms

Output:

```json
{
  "name": "",
  "description": "",
  "website": "",
  "similarity_score": 0.82
}
```

---

## API Discovery

Purpose:

Reduce build complexity.

Search For:

* Public APIs
* SDKs
* AI APIs
* Government APIs
* Sponsor APIs

Output:

```json
{
  "name": "",
  "provider": "",
  "description": "",
  "pricing": "",
  "integration_effort": "low"
}
```

---

## Open Source Discovery

Purpose:

Avoid rebuilding existing solutions.

Search For:

* GitHub Repositories
* Frameworks
* Templates
* Boilerplates

Output:

```json
{
  "name": "",
  "stars": 0,
  "license": "",
  "relevance_score": 0.92
}
```

---

## Startup Discovery

Purpose:

Understand market maturity.

Questions:

* Is this already funded?
* Is this crowded?
* Is there whitespace?

Output:

```json
{
  "startup_name": "",
  "funding_stage": "",
  "market": "",
  "relevance": 0.88
}
```

---

# Research Coordinator

Purpose:

Single entry point.

Agents never call individual research modules.

Instead:

```python
research_service.run()
```

returns everything.

---

# Research Pipeline

Step 1

Receive Idea

↓

Step 2

Extract Keywords

↓

Step 3

Generate Search Queries

↓

Step 4

Parallel Research

↓

Step 5

Aggregate Results

↓

Step 6

Score Findings

↓

Step 7

Generate Research Report

---

# Novelty Scoring

Range:

```text
0 → 100
```

---

## Formula

```text
Novelty =
40% Competitor Density
+
30% Startup Density
+
20% Open Source Density
+
10% Market Saturation
```

---

## Interpretation

90+

Very Novel

---

70+

Good Opportunity

---

50+

Moderately Crowded

---

30+

Highly Crowded

---

10+

Red Ocean

---

# Feasibility Scoring

Questions:

* Can it be built?
* Can it be demoed?
* Can it be completed in time?

---

## Formula

```text
Feasibility =
35% API Availability
+
35% Existing Libraries
+
20% Team Skills
+
10% Complexity
```

---

# Differentiation Scoring

Questions:

* Why would judges care?
* What makes it unique?

---

## Formula

```text
Differentiation =
Innovation
+
Execution Advantage
+
Unique Features
```

---

# Final Idea Score

```text
Final Score =
35% Feasibility
+
35% Differentiation
+
20% Novelty
+
10% Market Opportunity
```

---

# Research Report Schema

```typescript
interface ResearchReport {
    competitors: Competitor[]
    startups: Startup[]
    apis: Api[]
    open_source: OpenSource[]

    novelty_score: number
    feasibility_score: number
    differentiation_score: number

    final_score: number

    recommendations: string[]
}
```

---

# Agent Usage

Challenge Intelligence

Uses:

* Market Signals

---

Opportunity Planner

Uses:

* Competitor Research

---

Idea Validator

Uses:

* Full Research Report

---

# Caching Strategy

Research is expensive.

Cache:

* Query Results
* GitHub Results
* API Results

TTL:

```text
24 hours
```

---

# Future Research Sources

Potential Additions:

* Product Hunt
* Hacker News
* Reddit
* Crunchbase
* YC Directory
* Indie Hackers

---

# Success Criteria

Research should improve idea quality.

The user should consistently receive:

* More realistic ideas
* Better differentiation
* Faster implementation paths

Instead of generic LLM suggestions.
