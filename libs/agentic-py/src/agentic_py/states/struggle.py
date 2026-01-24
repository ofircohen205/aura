"""
Struggle Detection State

State definition for the Struggle Detection Workflow.
"""

from typing import TypedDict


class StruggleState(TypedDict, total=False):
    """State for the Struggle Detection Workflow.

    This state tracks user struggle indicators and lesson recommendations.
    Used by the struggle detection agent to decide when to retrieve
    knowledge and generate lessons.
    """

    edit_frequency: float
    error_logs: list[str]
    history: list[str]
    is_struggling: bool
    lesson_recommendation: str | None
    # Tool call results (for agentic workflows)
    retrieved_context: str | None
    tool_calls: list[dict] | None


def validate_struggle_state(state: StruggleState) -> StruggleState:
    """
    Validate and normalize struggle state structure.

    Ensures required fields are present and have correct types.
    Provides default values for optional fields.

    Args:
        state: Struggle state dictionary to validate

    Returns:
        Validated and normalized state dictionary

    Raises:
        ValueError: If state structure is invalid
    """
    validated = state.copy()

    # Ensure required fields have defaults
    if "edit_frequency" not in validated:
        validated["edit_frequency"] = 0.0
    if "error_logs" not in validated:
        validated["error_logs"] = []
    if "history" not in validated:
        validated["history"] = []
    if "is_struggling" not in validated:
        validated["is_struggling"] = False
    if "lesson_recommendation" not in validated:
        validated["lesson_recommendation"] = None
    if "retrieved_context" not in validated:
        validated["retrieved_context"] = None
    if "tool_calls" not in validated:
        validated["tool_calls"] = None

    # Validate types
    if not isinstance(validated["edit_frequency"], int | float):
        raise ValueError("edit_frequency must be a number")
    if validated["edit_frequency"] < 0:
        raise ValueError("edit_frequency must be non-negative")
    if not isinstance(validated["error_logs"], list):
        raise ValueError("error_logs must be a list")
    if not isinstance(validated["history"], list):
        raise ValueError("history must be a list")
    if not isinstance(validated["is_struggling"], bool):
        raise ValueError("is_struggling must be a boolean")
    if validated["lesson_recommendation"] is not None and not isinstance(
        validated["lesson_recommendation"], str
    ):
        raise ValueError("lesson_recommendation must be a string or None")

    return validated
