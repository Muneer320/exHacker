from __future__ import annotations

from pydantic import BaseModel


class ProjectRequest(BaseModel):
    challenge_statement: str
    hackathon_name: str = ""
    sponsors: list[str] = []
    tracks: list[str] = []
    team_profile: dict | None = None
    duration_hours: int = 48
