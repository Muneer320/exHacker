# Docs/frontend/05_Animation_Interactions.md

# exHacker Animation & Interaction System

Version: 1.0

Status: Active

Audience:

* Frontend Engineers
* Designers
* AI Engineers

---

# Purpose

This document defines every major animation and interaction pattern.

Animations are not decorative.

Animations communicate:

* Progress
* State
* Activity
* Intelligence

The user should constantly feel that work is being performed.

---

# Philosophy

Bad animation:

```text
Pretty
Distracting
Pointless
```

Good animation:

```text
Useful
Informative
Fast
```

---

# Inspiration

Reference products:

* Linear
* Raycast
* Arc
* Perplexity
* Cursor

Avoid:

* Crypto websites
* Landing page templates
* Overly dramatic effects

---

# Global Motion Rules

Animation Duration

Fast:

```css
150ms
```

Default:

```css
250ms
```

Large transitions:

```css
400ms
```

Never exceed:

```css
700ms
```

---

# Easing

Use:

```css
ease-out
```

or

```css
cubic-bezier(0.16,1,0.3,1)
```

Avoid:

```css
bounce
elastic
cartoon effects
```

---

# Landing Page

## Hero Fade

When page loads:

Headline:

```text
Fade Up
```

Duration:

```css
400ms
```

Delay:

```css
0ms
```

---

Subheadline:

```text
Fade Up
```

Delay:

```css
100ms
```

---

CTA Buttons:

```text
Fade Up
```

Delay:

```css
200ms
```

---

# Workflow Preview

Workflow nodes connect gradually.

Sequence:

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

Each node lights up.

Creates understanding immediately.

---

# Button Interactions

Hover:

```css
scale(1.02)
```

---

Press:

```css
scale(0.98)
```

---

Duration:

```css
150ms
```

---

# Card Interactions

Hover:

```css
translateY(-2px)
```

---

Border glow appears.

---

Shadow slightly increases.

---

Never:

```css
translateY(-20px)
```

---

# Workflow Command Center

This is the most important page.

Most animations live here.

---

# Workflow Timeline

When a stage becomes active:

1. Previous stage turns green.
2. Connector animates.
3. New stage begins pulsing.

---

Visual progression should feel alive.

---

# Active Agent Card

Current agent:

* Slight glow
* Animated border
* Pulse indicator

---

Animation:

```css
opacity
scale(1 → 1.02 → 1)
```

Loop.

Very subtle.

---

# Agent Thinking State

Agent should never look idle.

Display:

```text
Analyzing...
Researching...
Generating...
Scoring...
```

Animated dots:

```text
.
..
...
```

Looping.

---

# Agent Activity Feed

New messages:

```text
Slide In
Fade In
```

Duration:

```css
200ms
```

---

Auto-scroll to latest item.

---

# Research Discovery Animation

When new resource appears:

Example:

```text
Competitor Found

Stripe Atlas
```

Card:

```text
Fade In
Expand
```

Duration:

```css
250ms
```

---

Creates feeling of live research.

---

# State Preview Updates

When data changes:

Old value:

```text
Fade Out
```

New value:

```text
Fade In
```

Avoid full re-renders.

---

# Idea Generation

Most exciting interaction.

---

When ideas appear:

Do NOT instantly render all ideas.

Instead:

Idea 1

↓

Idea 2

↓

Idea 3

↓

Idea 4

↓

Idea 5

One by one.

---

Animation:

```css
Slide Up
Fade In
```

---

Delay:

```css
100ms between cards
```

---

Effect

Feels like ideas are being created.

---

# Idea Cards

Hover:

```css
border highlight
```

---

Expand:

```css
height animation
```

---

Duration:

```css
250ms
```

---

# Idea Selection

When user selects an idea:

Selected card:

```css
scale(1.03)
```

---

Other cards:

```css
opacity: 0.5
```

---

Confirmation glow.

---

Workflow resumes.

---

# Architecture Generation

Show architecture progressively.

---

Sequence:

Frontend

↓

Backend

↓

Database

↓

AI Layer

↓

External Services

---

Nodes connect gradually.

Not instantly.

---

Effect:

Architecture feels generated.

---

# Mermaid Diagrams

Fade in.

Then:

Draw connecting lines.

---

Duration:

```css
500ms
```

---

# Dashboard Tabs

Switching tabs:

Old content:

```css
Fade Out
```

New content:

```css
Fade In
```

---

Duration:

```css
150ms
```

---

No page reload feeling.

---

# Pitch Cards

Appear sequentially.

---

30 Second Pitch

↓

2 Minute Pitch

↓

Judge Q&A

---

Feels like deliverables being completed.

---

# Export Action

When export begins:

Button changes to:

```text
Preparing Package...
```

---

Progress indicator appears.

---

Export complete:

```text
Package Ready
```

Success animation.

---

# Loading Screens

Never use spinners alone.

Bad:

```text
Loading...
```

---

Good:

```text
Researching competitors...

Found 12 APIs...

Generating architecture...
```

---

Always show activity.

---

# Skeleton Loaders

Required for:

* Dashboard
* Research
* Ideas
* Workflow

---

Avoid blank spaces.

---

# Page Transitions

Route changes:

```css
Fade
```

*

```css
Slight Upward Motion
```

---

Duration:

```css
200ms
```

---

# Demo Mode

Most cinematic experience.

---

Sequence:

Challenge appears.

↓

Agent activates.

↓

Research appears.

↓

Ideas appear.

↓

Architecture builds.

↓

Pitch appears.

↓

Final dashboard.

---

Entire flow:

```text
60-90 seconds
```

---

Every stage should feel intentional.

---

# Reduced Motion Support

Must support:

```css
prefers-reduced-motion
```

---

Disable:

* Pulses
* Loops
* Complex transitions

Keep:

* Basic fades

---

# Motion Priority

Priority 1

Workflow Timeline

---

Priority 2

Agent Activity

---

Priority 3

Idea Generation

---

Priority 4

Architecture Generation

---

Priority 5

Landing Page Effects

---

# Golden Rule

Every animation should answer:

```text
What just happened?

What is happening now?

What happens next?
```

If it cannot answer one of those questions,

remove it.
