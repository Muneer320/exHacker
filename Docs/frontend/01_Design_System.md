# Docs/frontend/01_Design_System.md

# exHacker Design System

Version: 1.0

Status: Active

Audience:

* Frontend Engineers
* Designers
* AI Engineers

---

# Purpose

This document defines the complete visual language of exHacker.

Every page.

Every component.

Every interaction.

Must follow this system.

Consistency is more important than creativity.

---

# Design Philosophy

Three words:

```text id="d1"
Premium
Focused
Technical
```

The UI should feel like:

* Cursor
* Linear
* Vercel
* Arc Browser

Not:

* Bootstrap dashboard
* Admin panel
* Crypto website
* Traditional SaaS

---

# Theme

Dark First.

Dark mode is the primary experience.

Light mode is optional and lower priority.

---

# Color Palette

## Background

Primary:

```css id="d2"
#050816
```

Used for:

* App background
* Landing page background

---

Secondary:

```css id="d3"
#0B1020
```

Used for:

* Cards
* Panels
* Modals

---

Tertiary:

```css id="d4"
#111827
```

Used for:

* Nested cards
* Agent cards
* Tab containers

---

# Accent Colors

Primary:

```css id="d5"
#7C3AED
```

Purpose:

* Primary buttons
* Active states
* Progress indicators

---

Secondary:

```css id="d6"
#06B6D4
```

Purpose:

* Research
* Information
* Discovery

---

Success:

```css id="d7"
#22C55E
```

Purpose:

* Completed agents
* Successful workflow steps

---

Warning:

```css id="d8"
#F59E0B
```

Purpose:

* Waiting for user action
* Idea selection

---

Error:

```css id="d9"
#EF4444
```

Purpose:

* Failed workflows
* Errors

---

# Typography

## Font Family

Primary:

```text id="d10"
Inter
```

Fallback:

```text id="d11"
system-ui
```

---

# Font Scale

## Hero

```css id="d12"
72px
Font Weight: 800
```

Landing page only.

---

## H1

```css id="d13"
48px
Font Weight: 700
```

---

## H2

```css id="d14"
32px
Font Weight: 700
```

---

## H3

```css id="d15"
24px
Font Weight: 600
```

---

## Body

```css id="d16"
16px
Font Weight: 400
```

---

## Small Text

```css id="d17"
14px
Font Weight: 400
```

---

# Layout

## Max Width

```css id="d18"
1440px
```

---

## Content Width

```css id="d19"
1200px
```

---

## Standard Padding

Desktop:

```css id="d20"
32px
```

---

Tablet:

```css id="d21"
24px
```

---

Mobile:

```css id="d22"
16px
```

---

# Border Radius

Small:

```css id="d23"
8px
```

---

Medium:

```css id="d24"
12px
```

---

Large:

```css id="d25"
16px
```

---

Hero Cards:

```css id="d26"
24px
```

---

# Shadows

Avoid heavy shadows.

Prefer:

```css id="d27"
border
backdrop blur
subtle glow
```

Instead of giant shadow effects.

---

# Glass Effect

Allowed.

But subtle.

Example:

```css id="d28"
background: rgba(255,255,255,0.03)

backdrop-filter: blur(12px)

border:
1px solid rgba(255,255,255,0.08)
```

---

# Buttons

## Primary Button

Color:

```css id="d29"
#7C3AED
```

Hover:

```css id="d30"
brightness(1.1)
```

---

## Secondary Button

Transparent.

Border:

```css id="d31"
rgba(255,255,255,0.15)
```

---

# Cards

Every card should have:

```css id="d32"
background: #0B1020
border-radius: 16px
border: 1px solid rgba(255,255,255,0.08)
```

---

# Icons

Library:

```text id="d33"
Lucide React
```

Only.

No mixed icon libraries.

---

# Agent Identity Colors

Challenge Intelligence:

```css id="d34"
#06B6D4
```

---

Problem Analyst:

```css id="d35"
#8B5CF6
```

---

Opportunity Planner:

```css id="d36"
#F59E0B
```

---

Idea Generator:

```css id="d37"
#EC4899
```

---

Idea Validator:

```css id="d38"
#22C55E
```

---

Solution Architect:

```css id="d39"
#3B82F6
```

---

Presentation Agent:

```css id="d40"
#A855F7
```

---

Pitch Coach:

```css id="d41"
#F97316
```

---

# Status Colors

Running:

```css id="d42"
#3B82F6
```

Animated pulse.

---

Completed:

```css id="d43"
#22C55E
```

---

Waiting:

```css id="d44"
#F59E0B
```

---

Failed:

```css id="d45"
#EF4444
```

---

# Progress Indicators

Never use boring loading bars.

Prefer:

* Agent timelines
* Animated dots
* Workflow progression
* Live activity logs

---

# Empty States

Every empty state should teach.

Bad:

```text id="d46"
No data.
```

Good:

```text id="d47"
Start a project to see AI agents analyze your challenge and generate solutions.
```

---

# Component Philosophy

Every component should answer:

```text id="d48"
What is happening?

Why is it happening?

What should the user do next?
```

If it cannot answer those questions, redesign it.

---

# Golden Rule

A judge should be able to understand:

* Current stage
* Current agent
* Current progress

Within 3 seconds of looking at the screen.

Never sacrifice clarity for aesthetics.
