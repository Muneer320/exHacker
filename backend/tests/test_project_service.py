"""Tests for Project Service — state machine enforcement."""

import pytest

from app.core.exceptions import InvalidStateTransitionError
from app.models.project import ProjectStatus
from app.services.project import _validate_transition


class TestStateMachine:
    """Test the project state machine transitions."""

    def test_valid_transitions(self):
        """All approved transitions should pass."""
        # DRAFT → PROCESSING, ARCHIVED
        _validate_transition(ProjectStatus.DRAFT, ProjectStatus.PROCESSING)
        _validate_transition(ProjectStatus.DRAFT, ProjectStatus.ARCHIVED)

        # PROCESSING → READY, DRAFT
        _validate_transition(ProjectStatus.PROCESSING, ProjectStatus.READY)
        _validate_transition(ProjectStatus.PROCESSING, ProjectStatus.DRAFT)

        # READY → DRAFT, ARCHIVED
        _validate_transition(ProjectStatus.READY, ProjectStatus.DRAFT)
        _validate_transition(ProjectStatus.READY, ProjectStatus.ARCHIVED)

    def test_invalid_transitions(self):
        """Invalid transitions should raise InvalidStateTransitionError."""
        invalid_cases = [
            (ProjectStatus.DRAFT, ProjectStatus.READY),
            (ProjectStatus.DRAFT, ProjectStatus.DRAFT),
            (ProjectStatus.PROCESSING, ProjectStatus.ARCHIVED),
            (ProjectStatus.PROCESSING, ProjectStatus.PROCESSING),
            (ProjectStatus.READY, ProjectStatus.PROCESSING),
            (ProjectStatus.READY, ProjectStatus.READY),
            (ProjectStatus.ARCHIVED, ProjectStatus.DRAFT),
            (ProjectStatus.ARCHIVED, ProjectStatus.PROCESSING),
            (ProjectStatus.ARCHIVED, ProjectStatus.READY),
            (ProjectStatus.ARCHIVED, ProjectStatus.ARCHIVED),
        ]
        for current, target in invalid_cases:
            with pytest.raises(InvalidStateTransitionError) as exc_info:
                _validate_transition(current, target)
            assert exc_info.value.code == "INVALID_TRANSITION"
            assert exc_info.value.status_code == 400

    def test_error_details(self):
        """Error should include current state, requested state, and allowed transitions."""
        try:
            _validate_transition(ProjectStatus.READY, ProjectStatus.PROCESSING)
        except InvalidStateTransitionError as e:
            assert e.detail is not None
            assert e.detail["current_state"] == "ready"
            assert e.detail["requested_state"] == "processing"
            assert "draft" in e.detail["allowed_transitions"]
            assert "archived" in e.detail["allowed_transitions"]
            assert e.suggestion is not None

    def test_archived_is_terminal(self):
        """ARCHIVED should have no allowed transitions."""
        from app.services.project import _VALID_TRANSITIONS
        assert _VALID_TRANSITIONS[ProjectStatus.ARCHIVED] == set()
