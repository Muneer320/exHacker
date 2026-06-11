# 07_API_Contracts.md

# API Contracts

Project: exHacker

Version: 2.0

Status: Active

---

# Purpose

This document defines all API contracts between:

* Frontend
* Backend
* Workflow Engine

This document is the source of truth for:

* Request schemas
* Response schemas
* Status codes
* Error handling

Frontend and backend should be buildable independently using this document alone.

---

# API Principles

---

## Rule 1

All APIs return structured JSON.

---

## Rule 2

All responses follow a consistent envelope.

```json
{
  "success": true,
  "data": {},
  "message": "Operation successful"
}
```

---

## Rule 3

Errors follow a consistent structure.

```json
{
  "success": false,
  "error": {
    "code": "PROJECT_NOT_FOUND",
    "message": "Project does not exist"
  }
}
```

---

# Base URL

Development

```text
http://localhost:8000/api/v1
```

Production

```text
https://api.exhacker.app/api/v1
```

---

# Health APIs

---

## GET /health

Purpose:

Verify backend health.

---

### Response

```json
{
  "success": true,
  "data": {
    "status": "healthy"
  }
}
```

---

# Project APIs

---

## POST /projects

Purpose:

Create a project.

Triggers workflow initialization.

---

### Request

```json
{
  "name": "AI Hackathon Project",
  "challenge_statements": [
    "Build an AI solution for education"
  ],
  "duration_hours": 48,
  "team_profile": {
    "team_size": 4,
    "experience_level": "intermediate",
    "known_technologies": [
      "Python",
      "React"
    ],
    "preferred_technologies": [
      "FastAPI",
      "Next.js"
    ]
  }
}
```

---

### Response

```json
{
  "success": true,
  "data": {
    "project_id": "uuid",
    "workflow_id": "uuid",
    "status": "created"
  }
}
```

---

# Get Project

---

## GET /projects/{project_id}

Purpose:

Retrieve project information.

---

### Response

```json
{
  "success": true,
  "data": {
    "project": {}
  }
}
```

---

# List Projects

---

## GET /projects

Purpose:

List projects.

---

### Response

```json
{
  "success": true,
  "data": {
    "projects": []
  }
}
```

---

# Workflow APIs

---

## POST /workflows/{workflow_id}/start

Purpose:

Start workflow execution.

---

### Response

```json
{
  "success": true,
  "data": {
    "workflow_id": "uuid",
    "status": "running"
  }
}
```

---

# Workflow Status

---

## GET /workflows/{workflow_id}

Purpose:

Retrieve workflow progress.

---

### Response

```json
{
  "success": true,
  "data": {
    "workflow_id": "uuid",
    "status": "running",
    "current_stage": "idea_generation",
    "progress": 45
  }
}
```

---

# Workflow State

---

## GET /workflows/{workflow_id}/state

Purpose:

Retrieve full workflow state.

Used by:

* Frontend
* Debugging
* Resume logic

---

### Response

```json
{
  "success": true,
  "data": {
    "state": {}
  }
}
```

---

# Resume Workflow

---

## POST /workflows/{workflow_id}/resume

Purpose:

Resume paused workflow.

---

### Response

```json
{
  "success": true,
  "data": {
    "status": "running"
  }
}
```

---

# Restart Workflow

---

## POST /workflows/{workflow_id}/restart

Purpose:

Restart workflow from beginning.

---

### Response

```json
{
  "success": true,
  "data": {
    "status": "running"
  }
}
```

---

# Human Selection APIs

This is the most important user interaction.

---

## GET /projects/{project_id}/ideas

Purpose:

Fetch generated ideas.

---

### Response

```json
{
  "success": true,
  "data": {
    "ideas": [],
    "validation_reports": []
  }
}
```

---

# Select Idea

---

## POST /projects/{project_id}/ideas/select

Purpose:

User chooses final idea.

---

### Request

```json
{
  "idea_id": "uuid"
}
```

---

### Response

```json
{
  "success": true,
  "data": {
    "selected_idea": "uuid",
    "workflow_status": "running"
  }
}
```

---

# Critical Rule

Once selected:

```text
selected_idea
```

becomes immutable.

No agent may overwrite it.

---

# Results APIs

---

## GET /projects/{project_id}/architecture

Returns:

```json
{
  "success": true,
  "data": {
    "architecture": {}
  }
}
```

---

## GET /projects/{project_id}/tech-stack

Returns:

```json
{
  "success": true,
  "data": {
    "tech_stack": {}
  }
}
```

---

## GET /projects/{project_id}/presentation

Returns:

```json
{
  "success": true,
  "data": {
    "presentation": {}
  }
}
```

---

## GET /projects/{project_id}/pitch

Returns:

```json
{
  "success": true,
  "data": {
    "pitch": {}
  }
}
```

---

# Export APIs

---

## GET /projects/{project_id}/exports

Purpose:

List available exports.

---

### Response

```json
{
  "success": true,
  "data": {
    "exports": [
      {
        "type": "readme"
      },
      {
        "type": "architecture"
      },
      {
        "type": "presentation"
      }
    ]
  }
}
```

---

# Generate Export

---

## POST /projects/{project_id}/exports/generate

Purpose:

Generate artifacts.

---

### Request

```json
{
  "formats": [
    "markdown",
    "pdf"
  ]
}
```

---

### Response

```json
{
  "success": true,
  "data": {
    "export_job_id": "uuid"
  }
}
```

---

# Download Export

---

## GET /exports/{export_id}/download

Purpose:

Download artifact.

---

### Response

File Download

Supported:

* PDF
* ZIP
* Markdown

---

# Agent Execution APIs

Used internally.

---

## GET /projects/{project_id}/agent-runs

Returns:

```json
{
  "success": true,
  "data": {
    "runs": []
  }
}
```

---

# Cost Monitoring APIs

Useful for development.

---

## GET /debug/costs

Returns:

```json
{
  "success": true,
  "data": {
    "total_cost": 0,
    "total_tokens": 0,
    "provider_usage": []
  }
}
```

---

# Provider Monitoring

---

## GET /debug/providers

Returns:

```json
{
  "success": true,
  "data": {
    "active_provider": "groq",
    "fallback_chain": [
      "groq",
      "gemini",
      "ollama",
      "openai"
    ]
  }
}
```

---

# Error Codes

---

## Validation

```text
VALIDATION_ERROR
```

Input invalid.

---

## Not Found

```text
PROJECT_NOT_FOUND

WORKFLOW_NOT_FOUND

EXPORT_NOT_FOUND
```

---

## Workflow

```text
WORKFLOW_PAUSED

WORKFLOW_FAILED

WORKFLOW_ALREADY_RUNNING
```

---

## Agent

```text
AGENT_EXECUTION_FAILED

AGENT_TIMEOUT

AGENT_OUTPUT_INVALID
```

---

## LLM

```text
PROVIDER_UNAVAILABLE

PROVIDER_TIMEOUT

TOKEN_LIMIT_EXCEEDED
```

---

# Authentication

Current Version:

No Authentication

---

Future Version:

JWT Authentication

```text
Authorization: Bearer <token>
```

---

# API Versioning

Current:

```text
/api/v1
```

Future:

```text
/api/v2
```

Breaking changes must create a new version.

---

# Real-Time Updates

Future Enhancement

Preferred:

WebSockets

```text
/ws/workflows/{workflow_id}
```

Events:

```json
{
  "event": "stage_completed",
  "stage": "idea_generation"
}
```

---

# API Design Principles

1. Stateless APIs

2. Structured Responses

3. Versioned Routes

4. Consistent Error Handling

5. Human Approval Points Exposed via APIs

6. Workflow State Accessible at All Times

7. Frontend Never Talks Directly To Agents

8. Workflow Engine Is The Source Of Truth

9. APIs Must Support Resume And Recovery

10. Every User Action Must Be Representable Through An API Endpoint
