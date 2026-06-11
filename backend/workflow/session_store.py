from __future__ import annotations

import uuid
from typing import Any

_sessions: dict[str, dict[str, Any]] = {}


def create_session(initial_state: dict[str, Any]) -> str:
    session_id = str(uuid.uuid4())
    _sessions[session_id] = {
        "state": initial_state.copy(),
        "current_step": "challenge_intelligence",
        "completed_steps": [],
        "step_outputs": {},
    }
    return session_id


def get_session(session_id: str) -> dict[str, Any] | None:
    return _sessions.get(session_id)


def save_session(session_id: str, session: dict[str, Any]) -> None:
    _sessions[session_id] = session


def list_sessions() -> list[str]:
    return list(_sessions.keys())
