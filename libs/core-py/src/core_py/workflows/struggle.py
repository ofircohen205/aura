"""
Struggle Detection Workflow

This module implements a LangGraph workflow for detecting when a user is struggling
based on edit frequency and error patterns. When struggling is detected, it generates
a lesson recommendation.
"""
import os
import logging
from typing import TypedDict, List, Optional
from langgraph.graph import StateGraph, END

logger = logging.getLogger(__name__)

# Configurable thresholds via environment variables
STRUGGLE_THRESHOLD_EDIT_FREQUENCY = float(
    os.getenv("STRUGGLE_THRESHOLD_EDIT_FREQUENCY", "10.0")
)
STRUGGLE_THRESHOLD_ERROR_COUNT = int(
    os.getenv("STRUGGLE_THRESHOLD_ERROR_COUNT", "2")
)

class StruggleState(TypedDict):
    """State for the Struggle Detection Workflow."""
    edit_frequency: float
    error_logs: List[str]
    history: List[str]
    is_struggling: bool
    lesson_recommendation: Optional[str]

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
        }
    )
    
    return {"is_struggling": is_struggling}

def generate_lesson(state: StruggleState) -> StruggleState:
    """
    Generates a lesson recommendation if struggling.
    
    Args:
        state: Current workflow state with is_struggling flag
        
    Returns:
        Updated state with lesson_recommendation if struggling
    """
    if state["is_struggling"]:
        # TODO: In real app, query Vector DB for relevant content based on error patterns
        lesson = "Review the documentation on state management."
        
        logger.info(
            "Lesson recommendation generated",
            extra={
                "is_struggling": True,
                "has_recommendation": True,
            }
        )
        
        return {"lesson_recommendation": lesson}
    
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
        "detect_struggle",
        decide_next_step,
        {
            "generate_lesson": "generate_lesson",
            END: END
        }
    )
    
    workflow.add_edge("generate_lesson", END)

    return workflow.compile(checkpointer=checkpointer)
