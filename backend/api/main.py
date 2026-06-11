from __future__ import annotations

import asyncio
import traceback
from concurrent.futures import ThreadPoolExecutor
from typing import Any

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv(usecwd=False, raise_error_if_not_found=False))

from fastapi import FastAPI, HTTPException  # noqa: E402
from fastapi.middleware.cors import CORSMiddleware  # noqa: E402
from pydantic import BaseModel  # noqa: E402

from graph.workflow import graph  # noqa: E402
from schemas.project_request import ProjectRequest  # noqa: E402
from workflow.executor import execute_step  # noqa: E402
from workflow.session_store import create_session, get_session, save_session  # noqa: E402
from workflow.steps import STEPS, get_next_step, get_step  # noqa: E402

app = FastAPI(title="exHacker API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:3001",
        "http://127.0.0.1:3001",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

_executor = ThreadPoolExecutor(max_workers=4)


@app.get("/")
def home():
    return {"message": "exHacker API Running", "version": "2.0.0"}


@app.post("/generate")
async def generate(data: ProjectRequest):
    initial_state = {
        "challenge_statement": data.challenge_statement,
        "hackathon_name": data.hackathon_name,
        "sponsors": data.sponsors,
        "tracks": data.tracks,
        "problem_analysis": {},
        "opportunity_analysis": {},
        "ideas": [],
        "ranked_ideas": [],
        "selected_idea": {},
        "solution_blueprint": {},
        "slides": [],
        "pitch_30s": "",
        "pitch_2min": "",
        "pitch_5min": "",
        "final_report": "",
        "prd_document": "",
        "vision_document": "",
    }
    try:
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(_executor, graph.invoke, initial_state)
        return result
    except Exception as exc:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(exc)) from exc


class WorkflowStartRequest(BaseModel):
    challenge_statement: str
    hackathon_name: str = ""
    sponsors: list[str] = []
    tracks: list[str] = []


class WorkflowContinueRequest(BaseModel):
    session_id: str


class WorkflowSelectIdeaRequest(BaseModel):
    session_id: str
    idea_index: int
    idea: dict[str, Any] | None = None


class WorkflowUpdateOutputRequest(BaseModel):
    session_id: str
    step: str
    updates: dict[str, Any]


@app.post("/workflow/start")
async def workflow_start(data: WorkflowStartRequest):
    initial_state: dict[str, Any] = {
        "challenge_statement": data.challenge_statement,
        "hackathon_name": data.hackathon_name,
        "sponsors": data.sponsors,
        "tracks": data.tracks,
        "problem_analysis": {},
        "opportunity_analysis": {},
        "ideas": [],
        "generated_ideas": [],
        "ranked_ideas": [],
        "selected_idea": {},
        "solution_blueprint": {},
        "architecture": {},
        "slides": [],
        "pitch_30s": "",
        "pitch_2min": "",
        "pitch_5min": "",
        "presentation": {},
        "pitch": {},
        "exports": {},
        "final_report": "",
        "prd_document": "",
        "vision_document": "",
        "tech_stack": {},
        "challenge_intelligence": {},
        "validation_reports": [],
        "build_package": {},
        "prompt_package": {},
    }
    session_id = create_session(initial_state)

    try:
        result = await execute_step(session_id, "challenge_intelligence")
        return result
    except Exception as exc:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/workflow/continue")
async def workflow_continue(data: WorkflowContinueRequest):
    session = get_session(data.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    current_step = session.get("current_step")

    if current_step is None:
        return {"done": True, "message": "Workflow is already complete"}

    step_meta = get_step(current_step)
    if step_meta and step_meta.get("is_select_step"):
        raise HTTPException(
            status_code=400,
            detail="This step requires manual idea selection. Use POST /workflow/select-idea instead.",
        )

    try:
        result = await execute_step(data.session_id, current_step)
        return result
    except Exception as exc:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/workflow/select-idea")
async def workflow_select_idea(data: WorkflowSelectIdeaRequest):
    session = get_session(data.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.get("current_step") != "select_idea":
        raise HTTPException(
            status_code=400,
            detail=f"Expected step 'select_idea', current step is '{session.get('current_step')}'",
        )

    state = session["state"]
    reports = state.get("validation_reports", []) or state.get("ranked_ideas", [])

    if not reports:
        raise HTTPException(status_code=400, detail="No validated ideas in session state")

    if not (0 <= data.idea_index < len(reports)):
        raise HTTPException(
            status_code=400,
            detail=f"idea_index {data.idea_index} is out of range (0–{len(reports) - 1})",
        )

    selected_idea = data.idea or reports[data.idea_index]

    state["selected_idea"] = selected_idea

    next_step = get_next_step("select_idea")
    session["current_step"] = next_step
    session["completed_steps"].append("select_idea")
    session["step_outputs"]["select_idea"] = {"selected_idea": selected_idea}
    session["state"] = state
    save_session(data.session_id, session)

    next_meta = get_step(next_step)

    return {
        "session_id": data.session_id,
        "completed_step": "select_idea",
        "completed_step_label": "Idea Selection",
        "selected_idea": selected_idea,
        "next_step": next_step,
        "next_step_label": next_meta["label"] if next_meta else None,
        "next_is_select_step": False,
        "done": next_step is None,
    }


@app.post("/workflow/update-output")
async def workflow_update_output(data: WorkflowUpdateOutputRequest):
    session = get_session(data.session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if data.step not in session["completed_steps"]:
        raise HTTPException(
            status_code=400,
            detail=f"Step '{data.step}' has not been completed yet",
        )

    session["step_outputs"][data.step].update(data.updates)
    session["state"].update(data.updates)
    save_session(data.session_id, session)

    return {"ok": True, "step": data.step, "updated_keys": list(data.updates.keys())}


@app.get("/workflow/state/{session_id}")
async def workflow_state(session_id: str):
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "session_id": session_id,
        "state": session["state"],
        "current_step": session["current_step"],
        "completed_steps": session["completed_steps"],
        "step_outputs": session["step_outputs"],
        "steps_meta": STEPS,
        "done": session["current_step"] is None,
    }


@app.get("/workflow/current-step/{session_id}")
async def workflow_current_step(session_id: str):
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    current = session["current_step"]
    return {
        "session_id": session_id,
        "current_step": current,
        "step_meta": get_step(current),
        "completed_steps": session["completed_steps"],
        "done": current is None,
    }


@app.get("/workflow/output/{session_id}")
async def workflow_output(session_id: str):
    session = get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    completed: list[str] = session["completed_steps"]
    if not completed:
        return {"step": None, "output": None}

    last = completed[-1]
    return {
        "step": last,
        "step_meta": get_step(last),
        "output": session["step_outputs"].get(last),
    }


@app.get("/workflows/{workflow_id}")
async def get_workflow_status(workflow_id: str):
    session = get_session(workflow_id)
    if not session:
        raise HTTPException(status_code=404, detail="Workflow not found")

    done = session["current_step"] is None
    total = len(STEPS)
    completed_count = len(session["completed_steps"])
    progress = int((completed_count / total) * 100) if total > 0 else 0

    return {
        "workflow_id": workflow_id,
        "status": "completed" if done else "running",
        "current_stage": session["current_step"],
        "progress": progress,
    }


@app.post("/workflows/{workflow_id}/resume")
async def resume_workflow(workflow_id: str):
    session = get_session(workflow_id)
    if not session:
        raise HTTPException(status_code=404, detail="Workflow not found")

    if session["current_step"] is None:
        return {"status": "completed", "message": "Workflow is already completed"}

    return {"status": "running", "current_step": session["current_step"]}


@app.post("/workflows/{workflow_id}/restart")
async def restart_workflow(workflow_id: str):
    session = get_session(workflow_id)
    if not session:
        raise HTTPException(status_code=404, detail="Workflow not found")

    session["current_step"] = "challenge_intelligence"
    session["completed_steps"] = []
    session["step_outputs"] = {}
    save_session(workflow_id, session)

    return {"status": "running"}
