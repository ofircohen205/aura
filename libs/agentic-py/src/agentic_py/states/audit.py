"""
Code Audit State

State definition for the Code Audit Workflow.
"""

from typing import Any, TypedDict


class AuditState(TypedDict, total=False):
    """State for the Code Audit Workflow.

    This state tracks code changes, violations, and audit results.
    Used by the audit agent to analyze code and check for violations.
    """

    diff_content: str
    violations: list[str]
    status: str  # "pass", "fail", "remediation_required"
    parsed_files: list[dict[str, Any]]  # Parsed file information
    parsed_hunks: list[dict[str, Any]]  # Parsed diff hunks with metadata
    file_extensions: set[str]  # File extensions in diff
    added_lines: int  # Count of added lines
    removed_lines: int  # Count of removed lines
    violation_details: list[dict[str, Any]]  # Enhanced violation information
    # Tool call results (for agentic workflows)
    retrieved_context: str | None
    tool_calls: list[dict] | None


def validate_audit_state(state: AuditState) -> AuditState:
    """
    Validate and normalize audit state structure.

    Ensures required fields are present and have correct types.
    Provides default values for optional fields.

    Args:
        state: Audit state dictionary to validate

    Returns:
        Validated and normalized state dictionary

    Raises:
        ValueError: If state structure is invalid
    """
    validated = state.copy()

    # Ensure required fields have defaults
    if "diff_content" not in validated:
        validated["diff_content"] = ""
    if "violations" not in validated:
        validated["violations"] = []
    if "status" not in validated:
        validated["status"] = "pending"

    # Validate types
    if not isinstance(validated["diff_content"], str):
        raise ValueError("diff_content must be a string")
    if not isinstance(validated["violations"], list):
        raise ValueError("violations must be a list")
    if validated["status"] not in ("pass", "fail", "pending", "remediation_required"):
        raise ValueError(f"Invalid status: {validated['status']}")

    # Ensure optional fields have defaults if missing
    if "parsed_files" not in validated:
        validated["parsed_files"] = []
    if "parsed_hunks" not in validated:
        validated["parsed_hunks"] = []
    if "file_extensions" not in validated:
        validated["file_extensions"] = set()
    if "added_lines" not in validated:
        validated["added_lines"] = 0
    if "removed_lines" not in validated:
        validated["removed_lines"] = 0
    if "violation_details" not in validated:
        validated["violation_details"] = []
    if "retrieved_context" not in validated:
        validated["retrieved_context"] = None
    if "tool_calls" not in validated:
        validated["tool_calls"] = None

    return validated
