from pydantic import BaseModel


class Idea(BaseModel):
    title: str
    description: str
    problem_solved: str
    target_users: list[str]
    core_features: list[str]
    innovation_factor: str
    why_it_wins: str
    feasibility_score: int
    innovation_score: int
    hackathon_fit_score: int


class IdeaList(BaseModel):
    ideas: list[Idea]