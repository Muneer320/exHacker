"""Pydantic schemas for Project API (Bible §8.1)."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    """Request schema for creating a project.

    Bible §8.1: Required fields are idea and optionally challenge/team context.
    """
    idea: str = Field(..., min_length=10, description="The raw idea or problem statement")

    # Optional challenge context
    challenge_statement: Optional[str] = Field(None, description="Hackathon challenge description")
    theme: Optional[str] = Field(None, description="Hackathon theme or track")
    organizer: Optional[str] = Field(None, description="Hackathon organizer")
    evaluation_criteria: Optional[str] = Field(None, description="Judging criteria")
    rules: Optional[str] = Field(None, description="Additional rules")

    # Optional team context
    available_hours: Optional[str] = Field(None, description="Available time (24h, 36h, 48h)")
    team_size: Optional[str] = Field(None, description="Team size")
    team_experience: Optional[str] = Field(None, description="Team experience level")
    preferred_languages: Optional[str] = Field(None, description="Preferred languages (comma-separated)")
    preferred_frameworks: Optional[str] = Field(None, description="Preferred frameworks (comma-separated)")
    target_platform: Optional[str] = Field(None, description="Target platform")
    skills: Optional[str] = Field(None, description="Team skills (comma-separated)")
    excluded_technologies: Optional[str] = Field(None, description="Technologies to avoid")
    constraints: Optional[str] = Field(None, description="Additional constraints")

    # Original fields
    name: Optional[str] = Field(None, max_length=200, description="Project name")
    description: Optional[str] = Field(None, max_length=2000, description="Optional description")


class ProjectUpdate(BaseModel):
    """Request schema for updating a project."""
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    idea: Optional[str] = Field(None, min_length=10)
    challenge_statement: Optional[str] = None
    theme: Optional[str] = None
    organizer: Optional[str] = None
    evaluation_criteria: Optional[str] = None
    rules: Optional[str] = None
    available_hours: Optional[str] = None
    team_size: Optional[str] = None
    team_experience: Optional[str] = None
    preferred_languages: Optional[str] = None
    preferred_frameworks: Optional[str] = None
    target_platform: Optional[str] = None
    skills: Optional[str] = None
    excluded_technologies: Optional[str] = None
    constraints: Optional[str] = None


class ProjectResponse(BaseModel):
    """Response schema for a project (Bible §8.1)."""
    id: str
    name: str
    description: Optional[str] = None
    idea: str
    status: str
    challenge_statement: Optional[str] = None
    theme: Optional[str] = None
    organizer: Optional[str] = None
    evaluation_criteria: Optional[str] = None
    rules: Optional[str] = None
    available_hours: Optional[str] = None
    team_size: Optional[str] = None
    team_experience: Optional[str] = None
    preferred_languages: Optional[str] = None
    preferred_frameworks: Optional[str] = None
    target_platform: Optional[str] = None
    skills: Optional[str] = None
    excluded_technologies: Optional[str] = None
    constraints: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    model_config = {"from_attributes": True}


class ProjectListResponse(BaseModel):
    """Response schema for listing projects."""
    projects: list[ProjectResponse]


class StateTransitionRequest(BaseModel):
    """Request schema for transitioning project state."""
    transition: str = Field(..., description="Target state to transition to")


class StateTransitionResponse(BaseModel):
    """Response schema for state transitions."""
    id: str
    status: str
    message: str
