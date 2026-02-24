"""
Struggle Detection State

State definition for the Struggle Detection Workflow.
"""

from typing import Literal, TypedDict

# Signal types supported by the enhanced detection system
SignalType = Literal["undo_redo", "time_pattern", "terminal", "debug", "semantic", "edit_pattern"]


class SignalInfo(TypedDict, total=False):
    """Information about a detected signal."""

    type: SignalType
    score: float
    metadata: dict


class StruggleState(TypedDict, total=False):
    """State for the Struggle Detection Workflow.

    This state tracks user struggle indicators and lesson recommendations.
    Used by the struggle detection agent to decide when to retrieve
    knowledge and generate lessons.
    """

    # Core struggle indicators (legacy)
    edit_frequency: float
    error_logs: list[str]
    history: list[str]
    is_struggling: bool
    lesson_recommendation: str | None

    # Tool call results (for agentic workflows)
    retrieved_context: str | None
    tool_calls: list[dict] | None

    # Enhanced signal context (from multi-signal detection system)
    combined_score: float | None
    primary_signal: SignalType | None
    signals: list[SignalInfo] | None

    # Signal-specific context
    undo_redo_pattern: str | None
    hesitation_ms: int | None
    terminal_errors: list[str] | None
    debug_breakpoint_changes: int | None

    # Client context
    source: str | None
    file_path: str | None
    language_id: str | None
    code_snippet: str | None


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

    # Enhanced signal fields defaults
    if "combined_score" not in validated:
        validated["combined_score"] = None
    if "primary_signal" not in validated:
        validated["primary_signal"] = None
    if "signals" not in validated:
        validated["signals"] = None
    if "undo_redo_pattern" not in validated:
        validated["undo_redo_pattern"] = None
    if "hesitation_ms" not in validated:
        validated["hesitation_ms"] = None
    if "terminal_errors" not in validated:
        validated["terminal_errors"] = None
    if "debug_breakpoint_changes" not in validated:
        validated["debug_breakpoint_changes"] = None

    # Client context defaults
    if "source" not in validated:
        validated["source"] = None
    if "file_path" not in validated:
        validated["file_path"] = None
    if "language_id" not in validated:
        validated["language_id"] = None
    if "code_snippet" not in validated:
        validated["code_snippet"] = None

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

    # Validate enhanced signal fields
    if validated["combined_score"] is not None:
        if not isinstance(validated["combined_score"], int | float):
            raise ValueError("combined_score must be a number or None")
        if validated["combined_score"] < 0 or validated["combined_score"] > 1:
            raise ValueError("combined_score must be between 0 and 1")

    if validated["signals"] is not None and not isinstance(validated["signals"], list):
        raise ValueError("signals must be a list or None")

    if validated["hesitation_ms"] is not None:
        if not isinstance(validated["hesitation_ms"], int):
            raise ValueError("hesitation_ms must be an integer or None")
        if validated["hesitation_ms"] < 0:
            raise ValueError("hesitation_ms must be non-negative")

    if validated["debug_breakpoint_changes"] is not None:
        if not isinstance(validated["debug_breakpoint_changes"], int):
            raise ValueError("debug_breakpoint_changes must be an integer or None")
        if validated["debug_breakpoint_changes"] < 0:
            raise ValueError("debug_breakpoint_changes must be non-negative")

    return validated
