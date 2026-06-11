from pydantic import BaseModel

class ProblemAnalysis(BaseModel):

    problem_statement: str

    pain_points: list[str]

    stakeholders: list[str]

    constraints: list[str]

    success_metrics: list[str]

    opportunities: list[str]

    ai_opportunities: list[str]

    unique_hackathon_angles: list[str]

    suggested_features: list[str]

    technical_challenges: list[str]

    judging_criteria_alignment: list[str]