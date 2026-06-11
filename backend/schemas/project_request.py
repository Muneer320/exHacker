# schemas/project_request.py

from pydantic import BaseModel

class ProjectRequest(BaseModel):

    challenge_statement: str

    hackathon_name: str

    sponsors: list[str]

    tracks: list[str]