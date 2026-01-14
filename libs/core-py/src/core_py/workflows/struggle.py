"""
Struggle Detection Workflow

This module implements a LangGraph workflow for detecting when a user is struggling
based on edit frequency and error patterns. When struggling is detected, it generates
a lesson recommendation.
"""

import logging
from typing import TypedDict

from langgraph.graph import END, StateGraph

from core_py.ml.config import (
    RAG_TOP_K,
    STRUGGLE_THRESHOLD_EDIT_FREQUENCY,
    STRUGGLE_THRESHOLD_ERROR_COUNT,
)
from core_py.prompts.loader import load_prompt
from core_py.rag.service import get_rag_service

logger = logging.getLogger(__name__)


class StruggleState(TypedDict, total=False):
    """State for the Struggle Detection Workflow."""

    edit_frequency: float
    error_logs: list[str]
    history: list[str]
    is_struggling: bool
    lesson_recommendation: str | None


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


def detect_struggle(state: StruggleState) -> StruggleState:
    """
    Analyzes input metrics to detect if the user is struggling.

    Args:
        state: Current workflow state containing edit frequency and error logs

    Returns:
        Updated state with is_struggling flag set
    """
    edit_freq = state["edit_frequency"]
    error_count = len(state["error_logs"])

    is_struggling = (
        edit_freq > STRUGGLE_THRESHOLD_EDIT_FREQUENCY
        or error_count > STRUGGLE_THRESHOLD_ERROR_COUNT
    )

    logger.info(
        "Struggle detection evaluated",
        extra={
            "edit_frequency": edit_freq,
            "error_count": error_count,
            "is_struggling": is_struggling,
            "threshold_frequency": STRUGGLE_THRESHOLD_EDIT_FREQUENCY,
            "threshold_errors": STRUGGLE_THRESHOLD_ERROR_COUNT,
        },
    )

    return {"is_struggling": is_struggling}


async def _generate_lesson_with_llm(formatted_prompt: str) -> str:
    """
    Generate lesson recommendation using LLM with retry logic and error handling.

    Args:
        formatted_prompt: Formatted prompt with all context

    Returns:
        Generated lesson recommendation string
    """
    from core_py.ml.config import LLM_ENABLED
    from core_py.ml.llm import invoke_llm_with_retry

    if not LLM_ENABLED:
        logger.debug("LLM is disabled, returning placeholder lesson")
        return (
            "Review the documentation on state management. "
            "[Enable LLM_ENABLED=true to generate AI-powered lessons]"
        )

    try:
        lesson = await invoke_llm_with_retry(formatted_prompt)

        logger.info(
            "Lesson generated with LLM",
            extra={
                "lesson_length": len(lesson),
            },
        )

        return lesson

    except RuntimeError as e:
        # LLM disabled or quota/auth errors
        logger.warning(f"LLM unavailable: {e}")
        return f"Review the documentation on state management. [LLM unavailable: {str(e)[:100]}]"
    except Exception as e:
        logger.error(
            "Failed to generate lesson with LLM",
            extra={
                "error": str(e),
                "error_type": type(e).__name__,
            },
            exc_info=True,
        )
        # Fallback to placeholder
        return (
            "Review the documentation on state management. "
            "[LLM generation failed, see logs for details]"
        )


async def generate_lesson(state: StruggleState) -> StruggleState:
    """
    Generates a lesson recommendation if struggling.

    Uses prompt templates to generate personalized lesson recommendations.
    The prompt template is loaded from markdown files and can be enhanced
    with RAG context when the RAG pipeline is integrated.

    Args:
        state: Current workflow state with is_struggling flag

    Returns:
        Updated state with lesson_recommendation if struggling
    """
    if state["is_struggling"]:
        try:
            # Load the lesson generation prompt template
            prompt_template = load_prompt("lesson_generation/lesson_generation_base")

            # Prepare variables for the prompt
            error_logs_str = "\n".join(f"- {error}" for error in state.get("error_logs", []))
            history_str = "\n".join(f"- {item}" for item in state.get("history", [])) or "None"

            # Query RAG service for relevant context based on error patterns
            rag_service = get_rag_service()
            error_logs_list = state.get("error_logs", [])
            rag_context = await rag_service.query_knowledge(
                query=f"Help with errors: {', '.join(error_logs_list[:3])}",  # Use first 3 errors
                error_patterns=error_logs_list,
                top_k=RAG_TOP_K,
            )

            # Format the prompt with current state
            formatted_prompt = prompt_template.format(
                edit_frequency=state.get("edit_frequency", 0.0),
                error_logs=error_logs_str,
                history=history_str,
                rag_context=rag_context,
            )

            # Log formatted prompt length for debugging
            logger.debug(f"Formatted prompt length: {len(formatted_prompt)}")

            # Call LLM to generate lesson recommendation
            lesson = await _generate_lesson_with_llm(formatted_prompt)

            logger.info(
                "Lesson recommendation generated",
                extra={
                    "is_struggling": True,
                    "has_recommendation": True,
                    "prompt_loaded": True,
                },
            )

            return {"lesson_recommendation": lesson}

        except Exception as e:
            logger.error(
                "Failed to generate lesson recommendation",
                extra={
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
                exc_info=True,
            )
            # Fallback to simple recommendation
            return {"lesson_recommendation": "Review the documentation on state management."}

    logger.debug("No lesson needed - user is not struggling")
    return {"lesson_recommendation": None}


def build_struggle_graph(checkpointer=None):
    workflow = StateGraph(StruggleState)

    workflow.add_node("detect_struggle", detect_struggle)
    workflow.add_node("generate_lesson", generate_lesson)

    workflow.set_entry_point("detect_struggle")

    def decide_next_step(state: StruggleState):
        if state["is_struggling"]:
            return "generate_lesson"
        return END

    workflow.add_conditional_edges(
        "detect_struggle", decide_next_step, {"generate_lesson": "generate_lesson", END: END}
    )

    workflow.add_edge("generate_lesson", END)

    return workflow.compile(checkpointer=checkpointer)
