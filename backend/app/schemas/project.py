"""Pydantic schemas for Project API."""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    """Request schema for creating a project."""
    idea: str = Field(..., min_length=10, description="The raw idea or problem statement")
    name: Optional[str] = Field(None, max_length=200, description="Project name")
    description: Optional[str] = Field(None, max_length=2000, description="Optional description")


class ProjectUpdate(BaseModel):
    """Request schema for updating a project."""
    name: Optional[str] = Field(None, max_length=200)
    description: Optional[str] = Field(None, max_length=2000)
    idea: Optional[str] = Field(None, min_length=10)


class ProjectResponse(BaseModel):
    """Response schema for a project."""
    id: str
    name: str
    description: Optional[str] = None
    idea: str
    status: str
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
