"""
In-memory session store for HITL workflow state.

Each session stores:
  - state:            full AgentState dict (the LangGraph state passed between nodes)
  - current_step:     key of the next step to execute (or None if done)
  - completed_steps:  ordered list of completed step keys
  - step_outputs:     dict mapping step key → raw output dict from that agent

Production swap:
  Replace _sessions with a Redis client.
  Use json.dumps/loads for serialisation and set a TTL (e.g. 86400s = 24 h).
"""

import uuid
from typing import Optional


# TODO: Replace with Redis for production
_sessions: dict[str, dict] = {}


def create_session(initial_state: dict) -> str:
    """Create a new session, returning its UUID."""
    session_id = str(uuid.uuid4())
    _sessions[session_id] = {
        "state": initial_state.copy(),
        "current_step": "problem_analyst",
        "completed_steps": [],
        "step_outputs": {},
    }
    return session_id


def get_session(session_id: str) -> Optional[dict]:
    """Return the session dict, or None if not found."""
    return _sessions.get(session_id)


def save_session(session_id: str, session: dict) -> None:
    """Persist the mutated session dict back to the store."""
    _sessions[session_id] = session


def list_sessions() -> list[str]:
    """Return all active session IDs (useful for debugging)."""
    return list(_sessions.keys())
