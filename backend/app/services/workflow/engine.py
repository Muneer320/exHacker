import uuid
import datetime
from typing import TypedDict, List, Optional, Any, Dict
from langgraph.graph import StateGraph, END

# Import schemas to validate state structure
from app.schemas.state import ExHackerStateSchema, WorkflowStatus, WorkflowStage


class ExHackerState(TypedDict):
    metadata: Dict[str, Any]
    project: Dict[str, Any]
    team_profile: Optional[Dict[str, Any]]
    challenge_intelligence: Optional[Dict[str, Any]]
    problem_analysis: Optional[Dict[str, Any]]
    opportunity_analysis: Optional[Dict[str, Any]]
    generated_ideas: Optional[List[Dict[str, Any]]]
    validation_reports: Optional[List[Dict[str, Any]]]
    selected_idea: Optional[Dict[str, Any]]
    tech_stack: Optional[Dict[str, Any]]
    architecture: Optional[Dict[str, Any]]
    build_package: Optional[Dict[str, Any]]
    prompt_package: Optional[Dict[str, Any]]
    presentation: Optional[Dict[str, Any]]
    pitch: Optional[Dict[str, Any]]
    exports: Optional[Dict[str, Any]]
    execution: Dict[str, Any]
    errors: List[Dict[str, Any]]


# Helper function to get current UTC ISO string
def utc_now_str() -> str:
    return datetime.datetime.utcnow().isoformat() + "Z"


# Nodes implementation
async def challenge_intelligence_node(state: ExHackerState) -> ExHackerState:
    state["metadata"]["current_stage"] = WorkflowStage.CHALLENGE_INTELLIGENCE.value
    state["metadata"]["updated_at"] = utc_now_str()
    
    if state.get("challenge_intelligence"):
        return state

    # Simulate execution duration & metrics
    start_time = datetime.datetime.utcnow()
    
    challenge_stmt = state["project"]["challenge_statements"][0] if state["project"]["challenge_statements"] else "Create an innovative hackathon project"
    
    # Generate high-quality mock data
    state["challenge_intelligence"] = {
        "themes": [
            "AI-Driven Automation",
            "Human-in-the-Loop Collaboration",
            f"Solving: {challenge_stmt}"
        ],
        "constraints": [
            "48-hour development window",
            "High scalability requirement",
            "Offline first operations fallback"
        ],
        "opportunities": [
            "Integration with edge LLM API providers",
            "Real-time reactive visual status tracking",
            "Extensible modular workspace layout"
        ],
        "evaluation_factors": [
            "Technical complexity & feasibility",
            "Wow-factor of visual demo",
            "Direct impact on the hackathon theme"
        ],
        "technical_opportunities": [
            "Use LangGraph for complex agent routing",
            "Utilize SQLite for simplified local DB persistence",
            "Leverage Next.js static side optimization"
        ]
    }
    
    # Record execution metrics
    duration = (datetime.datetime.utcnow() - start_time).total_seconds()
    state["execution"]["total_duration_seconds"] += duration
    state["execution"]["total_tokens"] += 450
    state["execution"]["total_cost"] += 0.0009
    
    state["execution"]["stage_metrics"].append({
        "stage": WorkflowStage.CHALLENGE_INTELLIGENCE.value,
        "duration_seconds": duration,
        "tokens": 450,
        "cost": 0.0009
    })
    
    return state


async def problem_analysis_node(state: ExHackerState) -> ExHackerState:
    state["metadata"]["current_stage"] = WorkflowStage.PROBLEM_ANALYSIS.value
    state["metadata"]["updated_at"] = utc_now_str()
    
    if state.get("problem_analysis"):
        return state

    start_time = datetime.datetime.utcnow()
    proj_name = state["project"]["name"]
    
    state["problem_analysis"] = {
        "stakeholders": [
            "Hackathon judges & evaluators",
            "Product developers and AI engineers",
            "End users of AI automation platforms"
        ],
        "pain_points": [
            "High cognitive load setting up agent frameworks",
            "Brittle execution when LLM providers experience rate limits",
            "Lack of clean visual audit trail for background workflows"
        ],
        "assumptions": [
            "Users have valid API credentials for Groq or Gemini",
            "The workspace has standard internet connectivity",
            "The local runtime supports Python 3.10+ and Node 18+"
        ],
        "success_metrics": [
            "Reduced project generation time from hours to under 5 minutes",
            "Seamless auto-recovery from provider timeouts",
            "Clean visual output that requires zero user explanation"
        ],
        "refined_problem_statement": f"Developers struggle to orchestrate complex multi-agent workflows reliably under hackathon time constraints. {proj_name} addresses this by providing a resilient, visible, state-driven execution engine."
    }
    
    duration = (datetime.datetime.utcnow() - start_time).total_seconds()
    state["execution"]["total_duration_seconds"] += duration
    state["execution"]["total_tokens"] += 520
    state["execution"]["total_cost"] += 0.001
    
    state["execution"]["stage_metrics"].append({
        "stage": WorkflowStage.PROBLEM_ANALYSIS.value,
        "duration_seconds": duration,
        "tokens": 520,
        "cost": 0.001
    })
    
    return state


async def opportunity_discovery_node(state: ExHackerState) -> ExHackerState:
    state["metadata"]["current_stage"] = WorkflowStage.OPPORTUNITY_DISCOVERY.value
    state["metadata"]["updated_at"] = utc_now_str()
    
    if state.get("opportunity_analysis"):
        return state

    start_time = datetime.datetime.utcnow()
    
    state["opportunity_analysis"] = {
        "market_gaps": [
            "Existing frameworks are either too simple (one-shot prompts) or overly complex (LangChain raw code)",
            "Few frameworks store step-by-step state in real-time database schema snapshots"
        ],
        "innovation_opportunities": [
            "Dynamic LLM key rotation and multi-provider fallback",
            "Interactive Human-in-the-Loop selection dashboard"
        ],
        "technical_opportunities": [
            "Async FastAPI endpoints coupled with SQLAlchemy models",
            "Next.js App router combined with Tailwind micro-animations"
        ],
        "impact_opportunities": [
            "Accelerate hackathon building efficiency by 10x",
            "Provide clean boilerplate code that builds immediately"
        ]
    }
    
    duration = (datetime.datetime.utcnow() - start_time).total_seconds()
    state["execution"]["total_duration_seconds"] += duration
    state["execution"]["total_tokens"] += 480
    state["execution"]["total_cost"] += 0.00096
    
    state["execution"]["stage_metrics"].append({
        "stage": WorkflowStage.OPPORTUNITY_DISCOVERY.value,
        "duration_seconds": duration,
        "tokens": 480,
        "cost": 0.00096
    })
    
    return state


async def idea_generation_node(state: ExHackerState) -> ExHackerState:
    state["metadata"]["current_stage"] = WorkflowStage.IDEA_GENERATION.value
    state["metadata"]["updated_at"] = utc_now_str()
    
    if state.get("generated_ideas"):
        return state

    start_time = datetime.datetime.utcnow()
    proj_name = state["project"]["name"]
    
    # Generate 3 distinct high-quality ideas
    state["generated_ideas"] = [
        {
            "id": str(uuid.uuid4()),
            "title": f"{proj_name} Sentinel",
            "description": "An autonomous AI agent that monitors APIs and auto-recovers failing queries using rotating Groq and Gemini keys, ensuring 100% uptime for production demos.",
            "target_users": ["Hackathon Teams", "Indie Hackers", "App Developers"],
            "key_features": ["Dynamic Key Rotation", "Automatic Error Retries", "Status Check Dashboard"],
            "innovation_score": 8.5
        },
        {
            "id": str(uuid.uuid4()),
            "title": f"{proj_name} Blueprint",
            "description": "An interactive canvas that generates modular FastAPI database structures and frontend Next.js pages directly from a simple challenge prompt.",
            "target_users": ["Software Architects", "Prototypers", "Backend Developers"],
            "key_features": ["SQL Schema Generation", "Component Mapping", "ZIP Downloader"],
            "innovation_score": 9.2
        },
        {
            "id": str(uuid.uuid4()),
            "title": f"{proj_name} PitchMaster",
            "description": "An automated advisor that analyzes your product architecture and builds beautiful, ready-to-present markdown pitch slides customized for hackathon judges.",
            "target_users": ["Pitchers", "Product Managers", "Team Leaders"],
            "key_features": ["Markdown Slide Export", "Judge Q&A Simulator", "30-second Elevator Script"],
            "innovation_score": 8.8
        }
    ]
    
    duration = (datetime.datetime.utcnow() - start_time).total_seconds()
    state["execution"]["total_duration_seconds"] += duration
    state["execution"]["total_tokens"] += 950
    state["execution"]["total_cost"] += 0.0019
    
    state["execution"]["stage_metrics"].append({
        "stage": WorkflowStage.IDEA_GENERATION.value,
        "duration_seconds": duration,
        "tokens": 950,
        "cost": 0.0019
    })
    
    return state


async def idea_validation_node(state: ExHackerState) -> ExHackerState:
    state["metadata"]["current_stage"] = WorkflowStage.IDEA_VALIDATION.value
    state["metadata"]["updated_at"] = utc_now_str()
    
    if state.get("validation_reports"):
        return state

    start_time = datetime.datetime.utcnow()
    ideas = state.get("generated_ideas", [])
    
    reports = []
    for idea in ideas:
        idea_id = idea["id"]
        title = idea["title"]
        
        # Build structured mockup reports
        reports.append({
            "idea_id": idea_id,
            "competitors": [
                {"name": "LangSmith Monitor", "description": "Observability tool for LLM app workflows", "url": "https://langchain.com/langsmith"},
                {"name": "Helicone", "description": "Open source LLM monitoring tool", "url": "https://helicone.ai"}
            ],
            "open_source_projects": [
                {"name": "langgraph-python", "description": "LangChain's graph based orchestration library", "url": "https://github.com/langchain-ai/langgraph", "stars": 3400},
                {"name": "fastapi", "description": "High performance async web framework", "url": "https://github.com/fastapi/fastapi", "stars": 68000}
            ],
            "apis": [
                {"name": "Groq Cloud API", "description": "Ultra fast Llama-3 inference endpoint", "url": "https://groq.com"},
                {"name": "Google Gemini API", "description": "Multimodal fallback inference provider", "url": "https://ai.google.dev"}
            ],
            "strengths": [
                f"Tackles direct pain point in {title} execution",
                "Extremely visual and perfect for a live 3-minute demo",
                "Lightweight SQLite setup allows offline deployment"
            ],
            "weaknesses": [
                "Depends heavily on external LLM response reliability",
                "Requires careful schema serialization for complex state"
            ],
            "risks": [
                "LLM rate limits during live judging",
                "Database lockups if multiple threads write concurrently"
            ],
            "feasibility_score": 9.0,
            "innovation_score": idea["innovation_score"],
            "final_score": round((9.0 + idea["innovation_score"]) / 2, 2)
        })
        
    state["validation_reports"] = reports
    
    duration = (datetime.datetime.utcnow() - start_time).total_seconds()
    state["execution"]["total_duration_seconds"] += duration
    state["execution"]["total_tokens"] += 1200
    state["execution"]["total_cost"] += 0.0024
    
    state["execution"]["stage_metrics"].append({
        "stage": WorkflowStage.IDEA_VALIDATION.value,
        "duration_seconds": duration,
        "tokens": 1200,
        "cost": 0.0024
    })
    
    return state


async def pause_for_selection_node(state: ExHackerState) -> ExHackerState:
    state["metadata"]["current_stage"] = WorkflowStage.HUMAN_SELECTION.value
    state["metadata"]["status"] = WorkflowStatus.WAITING_FOR_USER.value
    state["metadata"]["updated_at"] = utc_now_str()
    return state


async def tech_stack_node(state: ExHackerState) -> ExHackerState:
    state["metadata"]["current_stage"] = WorkflowStage.TECH_STACK.value
    state["metadata"]["updated_at"] = utc_now_str()
    
    if state.get("tech_stack"):
        return state

    start_time = datetime.datetime.utcnow()
    
    state["tech_stack"] = {
        "frontend": "Next.js 15 (React 19, TypeScript, Tailwind CSS, Lucide React)",
        "backend": "FastAPI (Python 3.12, Uvicorn, LangGraph, Pydantic v2)",
        "database": "SQLite (SQLAlchemy Async AioSQLite local session engine)",
        "ai_stack": [
            "Groq API Wrapper (Primary inference)",
            "Google Gemini API SDK (Secondary fallback)",
            "LangGraph (Orchestration agent system)"
        ],
        "deployment": [
            "Vercel (Frontend static deployment)",
            "Railway / Render (FastAPI app server)"
        ],
        "reasoning": [
            "Next.js is the industry standard for slick responsive web UIs.",
            "FastAPI provides fast, type-safe API schema endpoints matching standard contracts.",
            "SQLite solves local setup complications and allows seamless offline testing."
        ]
    }
    
    duration = (datetime.datetime.utcnow() - start_time).total_seconds()
    state["execution"]["total_duration_seconds"] += duration
    state["execution"]["total_tokens"] += 410
    state["execution"]["total_cost"] += 0.00082
    
    state["execution"]["stage_metrics"].append({
        "stage": WorkflowStage.TECH_STACK.value,
        "duration_seconds": duration,
        "tokens": 410,
        "cost": 0.00082
    })
    
    return state


async def architecture_node(state: ExHackerState) -> ExHackerState:
    state["metadata"]["current_stage"] = WorkflowStage.ARCHITECTURE.value
    state["metadata"]["updated_at"] = utc_now_str()
    
    if state.get("architecture"):
        return state

    start_time = datetime.datetime.utcnow()
    selected_idea = state.get("selected_idea", {})
    idea_title = selected_idea.get("title", "Selected Solution")
    
    state["architecture"] = {
        "system_design": f"The architecture of {idea_title} follows a clean decoupling of backend and frontend layers, communicating via RESTful JSON API contracts. Background task workflows run in LangGraph state machines.",
        "components": [
            {"name": "Workflow State Engine", "description": "LangGraph orchestrated agent wrapper.", "responsibilities": ["Node execution", "State checks"]},
            {"name": "API Service Controller", "description": "FastAPI routes mapping database CRUD requests.", "responsibilities": ["Input validation", "Trigger execution"]}
        ],
        "modules": [
            {"name": "llm_service", "description": "LLM routing and error-handling fallback.", "dependencies": ["groq", "google-generativeai"]},
            {"name": "db_session", "description": "SQLAlchemy session manager.", "dependencies": ["aiosqlite"]}
        ],
        "api_design": [
            {"endpoint": "/api/v1/projects", "method": "POST", "description": "Creates a new project structure.", "request_body": {"name": "str", "challenge_statements": "list"}, "response_body": {"success": "bool", "data": "dict"}},
            {"endpoint": "/api/v1/projects/{project_id}/ideas/select", "method": "POST", "description": "Locks selected idea choice.", "request_body": {"idea_id": "str"}, "response_body": {"success": "bool", "data": "dict"}}
        ],
        "database_design": {
            "tables": [
                {"table_name": "projects", "columns": [{"name": "id", "type": "String"}, {"name": "name", "type": "String"}]},
                {"table_name": "workflow_states", "columns": [{"name": "id", "type": "String"}, {"name": "state_json", "type": "JSON"}]}
            ],
            "relationships": [
                "projects.id -> workflow_states.project_id (one-to-one)"
            ]
        },
        "integrations": [
            {"service_name": "Groq Cloud API", "purpose": "Ultra fast generation response", "type": "REST SDK"}
        ],
        "mvp_scope": [
            "Interactive workflow runner",
            "Database persistence models",
            "Mock outputs generation"
        ],
        "future_scope": [
            "Real-time WebSocket event broadcaster",
            "Custom agent creation layout"
        ]
    }
    
    duration = (datetime.datetime.utcnow() - start_time).total_seconds()
    state["execution"]["total_duration_seconds"] += duration
    state["execution"]["total_tokens"] += 850
    state["execution"]["total_cost"] += 0.0017
    
    state["execution"]["stage_metrics"].append({
        "stage": WorkflowStage.ARCHITECTURE.value,
        "duration_seconds": duration,
        "tokens": 850,
        "cost": 0.0017
    })
    
    return state


async def build_accelerator_node(state: ExHackerState) -> ExHackerState:
    state["metadata"]["current_stage"] = WorkflowStage.BUILD_ACCELERATOR.value
    state["metadata"]["updated_at"] = utc_now_str()
    
    if state.get("build_package") and state.get("prompt_package"):
        return state

    start_time = datetime.datetime.utcnow()
    
    state["build_package"] = {
        "frontend_tasks": [
            "Initialize Next.js app structure",
            "Configure Tailwind theme configuration matching the premium dark spec",
            "Build projects view, dashboard status tracking components"
        ],
        "backend_tasks": [
            "Initialize FastAPI server entrypoint",
            "Implement SQLAlchemy models and DB session helper",
            "Assemble LangGraph orchestrator steps"
        ],
        "database_tasks": [
            "Verify SQLite db connections",
            "Create schema initialization migrations"
        ],
        "testing_tasks": [
            "Write tests verifying database CRUD",
            "Implement LangGraph test runners"
        ],
        "deployment_tasks": [
            "Create Dockerfile container layouts",
            "Setup automatic Vercel webhook builds"
        ]
    }
    
    state["prompt_package"] = {
        "frontend_prompts": [
            "Build a responsive React landing page using Tailwind CSS, including dark glass cards and deep purple glow backdrops."
        ],
        "backend_prompts": [
            "Write a FastAPI endpoint that handles LangGraph state resume execution and stores the snapshot in SQLAlchemy db."
        ],
        "database_prompts": [
            "Define a SQLAlchemy base table mapping project items including JSON schema fields."
        ],
        "testing_prompts": [
            "Create pytest mock objects simulating LLM client responses."
        ],
        "deployment_prompts": [
            "Provide a production-ready docker-compose configuration for SQLite."
        ]
    }
    
    duration = (datetime.datetime.utcnow() - start_time).total_seconds()
    state["execution"]["total_duration_seconds"] += duration
    state["execution"]["total_tokens"] += 640
    state["execution"]["total_cost"] += 0.00128
    
    state["execution"]["stage_metrics"].append({
        "stage": WorkflowStage.BUILD_ACCELERATOR.value,
        "duration_seconds": duration,
        "tokens": 640,
        "cost": 0.00128
    })
    
    return state


async def presentation_node(state: ExHackerState) -> ExHackerState:
    state["metadata"]["current_stage"] = WorkflowStage.PRESENTATION.value
    state["metadata"]["updated_at"] = utc_now_str()
    
    if state.get("presentation"):
        return state

    start_time = datetime.datetime.utcnow()
    selected_idea = state.get("selected_idea", {})
    idea_title = selected_idea.get("title", "Selected Idea")
    
    state["presentation"] = {
        "slide_order": ["Slide 1: Problem", "Slide 2: Solution", "Slide 3: Architecture", "Slide 4: Market Validation", "Slide 5: Team"],
        "slide_content": [
            {"title": "The Core Problem", "content": ["Orchestrating agent workflows is slow and brittle.", "Rate limits derail live hackathon demos.", "Devs lack visible audit trails."], "visual_notes": "Deep red background with high-contrast warning icon."},
            {"title": f"Introducing {idea_title}", "content": ["Resilient state machines running on LangGraph.", "Priority fallback chaining between Groq and Gemini.", "Visual logs mapped to SQLite schema snapshots."], "visual_notes": "Sleek dark purple mockup with glowing success checks."}
        ],
        "demo_story": "We start the demo by creating a project, showing live logs. We pull out the Groq API key to trigger an error and show the fallback engine seamlessly switching to Gemini live without crash.",
        "business_story": "Hackathon developers are our entry point. Once validated, this architecture scales to indie builders and enterprise workflow monitoring systems."
    }
    
    duration = (datetime.datetime.utcnow() - start_time).total_seconds()
    state["execution"]["total_duration_seconds"] += duration
    state["execution"]["total_tokens"] += 590
    state["execution"]["total_cost"] += 0.00118
    
    state["execution"]["stage_metrics"].append({
        "stage": WorkflowStage.PRESENTATION.value,
        "duration_seconds": duration,
        "tokens": 590,
        "cost": 0.00118
    })
    
    return state


async def pitch_node(state: ExHackerState) -> ExHackerState:
    state["metadata"]["current_stage"] = WorkflowStage.PITCH.value
    state["metadata"]["updated_at"] = utc_now_str()
    
    if state.get("pitch"):
        return state

    start_time = datetime.datetime.utcnow()
    selected_idea = state.get("selected_idea", {})
    idea_title = selected_idea.get("title", "Selected Solution")
    
    state["pitch"] = {
        "pitch_30s": f"Meet {idea_title}. We orchestrate agent-driven projects using LangGraph, ensuring 100% demo resilience with Groq and Gemini fallbacks. Every state transition is written to SQLite locally, giving you total observability.",
        "pitch_2m": f"Every hackathon developer knows the pain: your demo crashes during judging because of rate limits. With {idea_title}, we build on top of a highly resilient, state-persisted LangGraph machine. If Groq times out, Gemini takes over in milliseconds. Our Next.js dashboard visualizes every agent step live, letting judges inspect outputs instantly.",
        "pitch_5m": f"Good afternoon judges. We are presenting {idea_title}, the state-driven copilot for resilient builds. [Detailed explanation of state architecture, fallback chaining, database persistence, and market viability metrics]. We invite you to try the demo yourself.",
        "judge_questions": [
            {"question": "How does this scale to complex graphs?", "answer": "LangGraph is designed for cyclic workflows. By storing state in serialized database models, we can load and resume execution seamlessly, maintaining low memory usage."},
            {"question": "What happens if all fallback providers fail?", "answer": "The system writes a WORKFLOW_FAILED error log to SQLite, updating the metadata status so developers can debug logs or retry manually."}
        ],
        "demo_script": "[Start dashboard] [Click run workflow] [Inspect challenge intelligence outputs] [Simulate Groq API error] [Inspect Gemini fallback logs] [Generate artifacts package]"
    }
    
    duration = (datetime.datetime.utcnow() - start_time).total_seconds()
    state["execution"]["total_duration_seconds"] += duration
    state["execution"]["total_tokens"] += 540
    state["execution"]["total_cost"] += 0.00108
    
    state["execution"]["stage_metrics"].append({
        "stage": WorkflowStage.PITCH.value,
        "duration_seconds": duration,
        "tokens": 540,
        "cost": 0.00108
    })
    
    return state


async def export_node(state: ExHackerState) -> ExHackerState:
    state["metadata"]["current_stage"] = WorkflowStage.EXPORT.value
    state["metadata"]["updated_at"] = utc_now_str()
    
    if state.get("exports"):
        return state

    start_time = datetime.datetime.utcnow()
    selected_idea = state.get("selected_idea", {})
    idea_title = selected_idea.get("title", "Selected Solution")
    
    state["exports"] = {
        "readme": f"# {idea_title}\n\nResilient agent workflow orchestrated by LangGraph.\n\n## Get Started\n\n```bash\nnpm install\nnpm run dev\n```",
        "architecture_doc": f"# Architecture Package - {idea_title}\n\nDescribes the database tables, component structures, API routing designs, and integration fallbacks.",
        "presentation_doc": f"# Presentation Slides\n\n1. Problem Statement\n2. The {idea_title} Solution\n3. Engineering Persistences\n4. Demo Script",
        "pitch_doc": f"# Pitch Preparation Guide\n\nContains the 30-second elevator pitch, 2-minute slide walk, and answers to judging panels.",
        "implementation_guide": f"# MVP Implementation Steps\n\nStep-by-step instructions generated by our build accelerator agent."
    }
    
    state["metadata"]["status"] = WorkflowStatus.COMPLETED.value
    
    duration = (datetime.datetime.utcnow() - start_time).total_seconds()
    state["execution"]["total_duration_seconds"] += duration
    state["execution"]["total_tokens"] += 380
    state["execution"]["total_cost"] += 0.00076
    
    state["execution"]["stage_metrics"].append({
        "stage": WorkflowStage.EXPORT.value,
        "duration_seconds": duration,
        "tokens": 380,
        "cost": 0.00076
    })
    
    return state


# Routing conditional function
def route_after_validation(state: ExHackerState) -> str:
    """Decides if the workflow proceeds to tech_stack selection or pauses for user input."""
    if state.get("selected_idea") is not None:
        return "tech_stack"
    return "pause_for_selection"


# Build state graph compiled instance
def build_workflow_graph() -> StateGraph:
    builder = StateGraph(ExHackerState)
    
    # Register all nodes
    builder.add_node("challenge_intelligence", challenge_intelligence_node)
    builder.add_node("problem_analysis", problem_analysis_node)
    builder.add_node("opportunity_discovery", opportunity_discovery_node)
    builder.add_node("idea_generation", idea_generation_node)
    builder.add_node("idea_validation", idea_validation_node)
    builder.add_node("pause_for_selection", pause_for_selection_node)
    builder.add_node("tech_stack", tech_stack_node)
    builder.add_node("architecture", architecture_node)
    builder.add_node("build_accelerator", build_accelerator_node)
    builder.add_node("presentation", presentation_node)
    builder.add_node("pitch", pitch_node)
    builder.add_node("export", export_node)
    
    # Establish routing edges
    builder.set_entry_point("challenge_intelligence")
    builder.add_edge("challenge_intelligence", "problem_analysis")
    builder.add_edge("problem_analysis", "opportunity_discovery")
    builder.add_edge("opportunity_discovery", "idea_generation")
    builder.add_edge("idea_generation", "idea_validation")
    
    # Conditional edge routing after validation
    builder.add_conditional_edges(
        "idea_validation",
        route_after_validation,
        {
            "tech_stack": "tech_stack",
            "pause_for_selection": "pause_for_selection"
        }
    )
    
    # Rest of workflow
    builder.add_edge("pause_for_selection", END)
    builder.add_edge("tech_stack", "architecture")
    builder.add_edge("architecture", "build_accelerator")
    builder.add_edge("build_accelerator", "presentation")
    builder.add_edge("presentation", "pitch")
    builder.add_edge("pitch", "export")
    builder.add_edge("export", END)
    
    return builder.compile()


# Compile global instance
workflow_graph = build_workflow_graph()


# Execution Orchestrator Runner
async def run_workflow(initial_state: ExHackerState) -> ExHackerState:
    """Executes the workflow graph. Returns the final state after execution completes or pauses."""
    current_state = initial_state
    
    # Run the graph and stream state changes
    async for event in workflow_graph.astream(current_state):
        # Merge event state modifications back into current_state
        for node_name, state_update in event.items():
            current_state.update(state_update)
            
    return current_state
