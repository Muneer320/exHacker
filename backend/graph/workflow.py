from typing import Any, TypedDict

from langgraph.graph import END, StateGraph

from agents.idea_generator import idea_generator_node
from agents.idea_selector import idea_selector_node
from agents.idea_validator import idea_validator_node
from agents.opportunity_planner import opportunity_planner_node
from agents.pitch_agent import pitch_agent_node
from agents.presentation_agent import presentation_agent_node
from agents.problem_analyst import problem_analyst_node
from agents.report_generator import report_generator_node
from agents.solution_architect import solution_architect_node


class WorkflowState(TypedDict):
    challenge_statement: str
    hackathon_name: str
    sponsors: list[str]
    tracks: list[str]
    problem_analysis: dict[str, Any]
    opportunity_analysis: dict[str, Any]
    ideas: list[dict[str, Any]]
    ranked_ideas: list[dict[str, Any]]
    selected_idea: dict[str, Any]
    solution_blueprint: dict[str, Any]
    slides: list[dict[str, Any]]
    pitch_30s: str
    pitch_2min: str
    pitch_5min: str
    final_report: str
    prd_document: str
    vision_document: str


builder = StateGraph(WorkflowState)

builder.add_node("problem_analyst", problem_analyst_node)
builder.add_node("idea_generator", idea_generator_node)
builder.add_node("idea_validator", idea_validator_node)
builder.add_node("idea_selector", idea_selector_node)
builder.add_node("solution_architect", solution_architect_node)
builder.add_node("presentation_agent", presentation_agent_node)
builder.add_node("pitch_agent", pitch_agent_node)
builder.add_node("report_generator", report_generator_node)
builder.add_node("opportunity_planner", opportunity_planner_node)

builder.set_entry_point("problem_analyst")

builder.add_edge("problem_analyst", "opportunity_planner")
builder.add_edge("opportunity_planner", "idea_generator")
builder.add_edge("idea_generator", "idea_validator")
builder.add_edge("idea_validator", "idea_selector")
builder.add_edge("idea_selector", "solution_architect")
builder.add_edge("solution_architect", "presentation_agent")
builder.add_edge("presentation_agent", "pitch_agent")
builder.add_edge("pitch_agent", "report_generator")
builder.add_edge("report_generator", END)

graph = builder.compile()
