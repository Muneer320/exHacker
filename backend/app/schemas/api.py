from typing import List, Optional, Any, Dict
from pydantic import BaseModel
from app.schemas.state import TeamProfile


class ProjectCreateRequest(BaseModel):
    name: str
    challenge_statements: List[str]
    duration_hours: int
    team_profile: TeamProfile


class IdeaSelectRequest(BaseModel):
    idea_id: str
