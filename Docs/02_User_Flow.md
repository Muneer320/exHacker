# 02_User_Journey.md

# User Journey & Workflow Specification

Project: exHacker

Version: 2.0

Status: Active

---

# Purpose

This document defines:

* What the user sees
* What happens internally
* Which agents execute
* What data is generated
* Human approval points
* Failure handling

This document is the bridge between:

* Product
* Frontend
* Backend
* Workflow Orchestration

---

# Core Principle

The user should never interact directly with agents.

The user interacts with:

* Forms
* Results
* Recommendations
* Approval checkpoints

Agents operate behind the scenes.

---

# High-Level Journey

Landing Page
↓
Project Creation
↓
Challenge Analysis
↓
Opportunity Discovery
↓
Idea Exploration
↓
Idea Validation
↓
Idea Selection
↓
Architecture Design
↓
Build Planning
↓
Presentation Creation
↓
Pitch Preparation
↓
Export

---

# Stage 1

Project Creation

---

## User Sees

New Project Form

Fields:

### Challenge Statements

Required

Examples:

* Build an AI healthcare assistant
* Improve financial literacy
* Create a sustainability solution

---

### Team Information

Required

Fields:

* Team Size
* Experience Level
* Technologies Known
* Technologies Preferred

---

### Time Available

Required

Examples:

* 24 hours
* 36 hours
* 48 hours

---

### Resources

Optional

Examples:

* APIs
* Datasets
* Documentation
* Sponsor Resources

---

## User Action

Click:

Start Analysis

---

## System Action

Creates:

Project

Creates:

Initial Workflow State

Triggers:

Challenge Intelligence Agent

---

## State Updates

Creates:

project

team_profile

workflow_metadata

---

# Stage 2

Challenge Intelligence

---

## User Sees

Analysis Progress Screen

Example:

✓ Project Created

✓ Challenge Intelligence Running

⏳ Problem Analysis Pending

⏳ Opportunity Discovery Pending

---

## Agent

Challenge Intelligence Agent

---

## Agent Inputs

* Challenge Statements
* Resources

---

## Agent Outputs

* Themes
* Constraints
* Opportunities
* Evaluation Factors

---

## State Updates

challenge_intelligence

---

# Stage 3

Problem Analysis

---

## Agent

Problem Analyst Agent

---

## Inputs

challenge_intelligence

team_profile

project

---

## Outputs

* Stakeholders
* Pain Points
* Assumptions
* Success Metrics
* Refined Problem Statement

---

## State Updates

problem_analysis

---

# Stage 4

Opportunity Discovery

---

## Agent

Opportunity Planner Agent

---

## Inputs

problem_analysis

challenge_intelligence

---

## Outputs

* Market Gaps
* Innovation Areas
* Technical Opportunities
* High Impact Opportunities

---

## State Updates

opportunity_analysis

---

# Stage 5

Idea Generation

---

## Agent

Idea Generator Agent

---

## Inputs

challenge_intelligence

problem_analysis

opportunity_analysis

team_profile

---

## Outputs

Minimum:

3 ideas

Preferred:

5 ideas

For each idea:

* Title
* Description
* Target Users
* Key Features
* Innovation Score

---

## State Updates

generated_ideas

---

# Stage 6

Idea Validation

---

## Agent

Idea Validator Agent

---

## Inputs

generated_ideas

team_profile

project

---

## Research Sources

* Existing Products
* Competitors
* Open Source Projects
* APIs
* Similar Solutions

---

## Outputs

Per Idea:

* Strengths
* Weaknesses
* Risks
* Feasibility Score
* Innovation Score
* Final Score

---

## State Updates

validation_reports

---

# Stage 7

Human Selection

---

## User Sees

Idea Comparison Dashboard

Displays:

* All Ideas
* Validation Results
* Scores
* Strengths
* Risks

---

## User Action

Select One Idea

---

## Critical Rule

No agent may override the user selection.

---

## State Updates

selected_idea

---

# Stage 8

Tech Stack Recommendation

---

## Agent

Tech Stack Advisor

---

## Inputs

selected_idea

team_profile

time_constraints

---

## Outputs

Frontend

Backend

Database

AI Stack

Hosting

Deployment Strategy

Justifications

---

## State Updates

tech_stack

---

# Stage 9

Solution Architecture

---

## Agent

Solution Architect

---

## Inputs

selected_idea

tech_stack

team_profile

---

## Outputs

System Design

Components

Data Flow

Database Design

API Design

Integrations

MVP Scope

Future Scope

---

## State Updates

architecture

---

# Stage 10

Build Accelerator

---

## Agent

Build Accelerator

---

## Inputs

architecture

tech_stack

selected_idea

---

## Outputs

Frontend Tasks

Backend Tasks

Database Tasks

Testing Tasks

Deployment Tasks

Implementation Prompts

---

## State Updates

build_package

prompt_package

---

# Stage 11

Presentation Generation

---

## Agent

Presentation Agent

---

## Inputs

selected_idea

architecture

validation_reports

---

## Outputs

Slide Structure

Slide Content

Demo Flow

Architecture Slides

Technical Slides

Business Slides

---

## State Updates

presentation

---

# Stage 12

Pitch Preparation

---

## Agent

Pitch Coach

---

## Inputs

selected_idea

presentation

validation_reports

---

## Outputs

30 Second Pitch

2 Minute Pitch

5 Minute Pitch

Judge Questions

Suggested Answers

Demo Narrative

---

## State Updates

pitch

---

# Stage 13

Export

---

## User Sees

Export Dashboard

Available Exports:

* Markdown
* PDF
* ZIP Package

---

## Generated Files

README.md

PRD.md

Architecture.md

API_Spec.md

Presentation.md

Pitch.md

Implementation_Guide.md

---

## State Updates

export_package

---

# Failure Handling

Every Agent:

Maximum Retries: 3

If Failure Persists:

Workflow Status:

FAILED

Error Logged

User Notified

---

# Resume Support

Workflow State must be persisted.

If server crashes:

Workflow resumes from the last completed stage.

Previously completed agents must not re-run unless explicitly requested.

---

# Human Checkpoints

Mandatory:

Idea Selection

Optional Future:

Architecture Approval

Presentation Approval

Pitch Approval

---

# Success Condition

A workflow is successful when:

* A final idea is selected
* Architecture is generated
* Tech stack is generated
* Build package exists
* Presentation exists
* Pitch exists
* Export package exists

Only then may workflow status become:

COMPLETED
