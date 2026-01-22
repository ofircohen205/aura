"""
Tests for state validation functions.
"""

import pytest

from agentic_py.workflows import AuditState, StruggleState, validate_audit_state, validate_struggle_state


class TestAuditStateValidation:
    """Tests for audit state validation."""

    def test_validate_audit_state_complete(self):
        """Test validation with complete state."""
        state: AuditState = {
            "diff_content": "test diff",
            "violations": ["violation1"],
            "status": "fail",
            "parsed_files": [{"path": "test.py"}],
            "parsed_hunks": [],
            "file_extensions": {"py"},
            "added_lines": 10,
            "removed_lines": 5,
            "violation_details": [],
        }

        validated = validate_audit_state(state)
        assert validated == state

    def test_validate_audit_state_minimal(self):
        """Test validation with minimal required fields."""
        state: AuditState = {
            "diff_content": "test",
            "violations": [],
            "status": "pending",
        }

        validated = validate_audit_state(state)
        assert validated["diff_content"] == "test"
        assert validated["violations"] == []
        assert validated["status"] == "pending"
        assert validated["parsed_files"] == []
        assert validated["parsed_hunks"] == []
        assert validated["file_extensions"] == set()
        assert validated["added_lines"] == 0
        assert validated["removed_lines"] == 0
        assert validated["violation_details"] == []

    def test_validate_audit_state_defaults(self):
        """Test validation adds defaults for missing fields."""
        state: AuditState = {}

        validated = validate_audit_state(state)
        assert validated["diff_content"] == ""
        assert validated["violations"] == []
        assert validated["status"] == "pending"

    def test_validate_audit_state_invalid_status(self):
        """Test validation with invalid status."""
        state: AuditState = {
            "diff_content": "test",
            "violations": [],
            "status": "invalid_status",
        }

        with pytest.raises(ValueError, match="Invalid status"):
            validate_audit_state(state)

    def test_validate_audit_state_invalid_types(self):
        """Test validation with invalid types."""
        state = {
            "diff_content": 123,  # Should be string
            "violations": [],
            "status": "pending",
        }

        with pytest.raises(ValueError, match="must be a string"):
            validate_audit_state(state)

        state = {
            "diff_content": "test",
            "violations": "not a list",  # Should be list
            "status": "pending",
        }

        with pytest.raises(ValueError, match="must be a list"):
            validate_audit_state(state)


class TestStruggleStateValidation:
    """Tests for struggle state validation."""

    def test_validate_struggle_state_complete(self):
        """Test validation with complete state."""
        state: StruggleState = {
            "edit_frequency": 15.0,
            "error_logs": ["error1"],
            "history": ["history1"],
            "is_struggling": True,
            "lesson_recommendation": "Test lesson",
        }

        validated = validate_struggle_state(state)
        assert validated == state

    def test_validate_struggle_state_minimal(self):
        """Test validation with minimal required fields."""
        state: StruggleState = {
            "edit_frequency": 10.0,
            "error_logs": [],
            "history": [],
            "is_struggling": False,
            "lesson_recommendation": None,
        }

        validated = validate_struggle_state(state)
        assert validated["edit_frequency"] == 10.0
        assert validated["error_logs"] == []
        assert validated["history"] == []
        assert validated["is_struggling"] is False
        assert validated["lesson_recommendation"] is None

    def test_validate_struggle_state_defaults(self):
        """Test validation adds defaults for missing fields."""
        state: StruggleState = {}

        validated = validate_struggle_state(state)
        assert validated["edit_frequency"] == 0.0
        assert validated["error_logs"] == []
        assert validated["history"] == []
        assert validated["is_struggling"] is False
        assert validated["lesson_recommendation"] is None

    def test_validate_struggle_state_negative_frequency(self):
        """Test validation with negative edit frequency."""
        state: StruggleState = {
            "edit_frequency": -5.0,
            "error_logs": [],
            "history": [],
            "is_struggling": False,
            "lesson_recommendation": None,
        }

        with pytest.raises(ValueError, match="must be non-negative"):
            validate_struggle_state(state)

    def test_validate_struggle_state_invalid_types(self):
        """Test validation with invalid types."""
        state = {
            "edit_frequency": "not a number",
            "error_logs": [],
            "history": [],
            "is_struggling": False,
            "lesson_recommendation": None,
        }

        with pytest.raises(ValueError, match="must be a number"):
            validate_struggle_state(state)

        state = {
            "edit_frequency": 10.0,
            "error_logs": "not a list",
            "history": [],
            "is_struggling": False,
            "lesson_recommendation": None,
        }

        with pytest.raises(ValueError, match="must be a list"):
            validate_struggle_state(state)

        state = {
            "edit_frequency": 10.0,
            "error_logs": [],
            "history": [],
            "is_struggling": "not a boolean",
            "lesson_recommendation": None,
        }

        with pytest.raises(ValueError, match="must be a boolean"):
            validate_struggle_state(state)

        state = {
            "edit_frequency": 10.0,
            "error_logs": [],
            "history": [],
            "is_struggling": False,
            "lesson_recommendation": 123,  # Should be string or None
        }

        with pytest.raises(ValueError, match="must be a string or None"):
            validate_struggle_state(state)
