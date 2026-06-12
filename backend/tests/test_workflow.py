import pytest
import httpx
from httpx import AsyncClient
from app.api.main import app
from app.schemas.state import WorkflowStatus, WorkflowStage


@pytest.mark.asyncio
async def test_workflow_end_to_end_integration():
    """Verify the complete lifecycle of a project and its LangGraph state engine:
    1. Project & workflow creation
    2. Listing & retrieval
    3. Running to Human Checkpoint (Idea selection)
    4. Selecting an idea and resuming to completion
    5. Retrieving generated results packages
    """
    transport = httpx.ASGITransport(app=app)
    
    # Step 1: Create project
    project_payload = {
        "name": "Integration Test App",
        "challenge_statements": [
            "Build a robust automated pipeline system"
        ],
        "duration_hours": 36,
        "team_profile": {
            "team_size": 3,
            "experience_level": "advanced",
            "known_technologies": ["Python", "FastAPI"],
            "preferred_technologies": ["LangGraph", "SQLite"]
        }
    }
    
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        create_res = await ac.post("/api/v1/projects", json=project_payload)
        
    assert create_res.status_code == 201
    res_data = create_res.json()
    assert res_data["success"] is True
    project_id = res_data["data"]["project_id"]
    workflow_id = res_data["data"]["workflow_id"]
    assert project_id is not None
    assert workflow_id is not None
    assert res_data["data"]["status"] == WorkflowStatus.CREATED.value
    
    # Step 2: List projects & retrieve project details
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        list_res = await ac.get("/api/v1/projects")
        get_res = await ac.get(f"/api/v1/projects/{project_id}")
        
    assert list_res.status_code == 200
    assert len(list_res.json()["data"]["projects"]) >= 1
    
    assert get_res.status_code == 200
    assert get_res.json()["data"]["project"]["name"] == "Integration Test App"
    
    # Step 3: Start workflow (this runs nodes up to human check point)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        start_res = await ac.post(f"/api/v1/workflows/{workflow_id}/start")
        
    assert start_res.status_code == 200
    assert start_res.json()["success"] is True
    # The workflow should run through idea_validation and then suspend waiting for selection
    assert start_res.json()["data"]["status"] == WorkflowStatus.WAITING_FOR_USER.value
    
    # Step 4: Verify generated ideas and status metrics
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        ideas_res = await ac.get(f"/api/v1/projects/{project_id}/ideas")
        status_res = await ac.get(f"/api/v1/workflows/{workflow_id}")
        state_res = await ac.get(f"/api/v1/workflows/{workflow_id}/state")
        
    assert ideas_res.status_code == 200
    ideas_data = ideas_res.json()["data"]
    assert len(ideas_data["ideas"]) >= 3  # Agent generates 5 ideas by default
    assert len(ideas_data["validation_reports"]) >= 3
    idea_to_select = ideas_data["ideas"][1]  # Select the second idea
    
    assert status_res.status_code == 200
    assert status_res.json()["data"]["status"] == WorkflowStatus.WAITING_FOR_USER.value
    assert status_res.json()["data"]["current_stage"] == WorkflowStage.HUMAN_SELECTION.value
    
    assert state_res.status_code == 200
    state_json = state_res.json()["data"]["state"]
    assert state_json["challenge_intelligence"] is not None
    assert state_json["problem_analysis"] is not None
    assert state_json["selected_idea"] is None
    
    # Step 5: Select idea (this triggers resume execution to completion)
    select_payload = {
        "idea_id": idea_to_select["id"]
    }
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        select_res = await ac.post(f"/api/v1/projects/{project_id}/ideas/select", json=select_payload)
        
    assert select_res.status_code == 200
    assert select_res.json()["success"] is True
    assert select_res.json()["data"]["workflow_status"] == WorkflowStatus.COMPLETED.value
    assert select_res.json()["data"]["selected_idea"] == idea_to_select["id"]
    
    # Step 6: Verify all generated deliverables
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        tech_res = await ac.get(f"/api/v1/projects/{project_id}/tech-stack")
        arch_res = await ac.get(f"/api/v1/projects/{project_id}/architecture")
        pres_res = await ac.get(f"/api/v1/projects/{project_id}/presentation")
        pitch_res = await ac.get(f"/api/v1/projects/{project_id}/pitch")
        exp_res = await ac.get(f"/api/v1/projects/{project_id}/exports")
        
    assert tech_res.status_code == 200
    assert tech_res.json()["data"]["tech_stack"]["frontend"] is not None
    
    assert arch_res.status_code == 200
    assert arch_res.json()["data"]["architecture"]["system_design"] is not None
    
    assert pres_res.status_code == 200
    assert len(pres_res.json()["data"]["presentation"]["slide_order"]) > 0
    
    assert pitch_res.status_code == 200
    assert pitch_res.json()["data"]["pitch"]["pitch_30s"] is not None
    
    assert exp_res.status_code == 200
    assert exp_res.json()["data"]["exports"]["readme"] is not None
