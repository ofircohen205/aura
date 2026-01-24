"""
Agentic Struggle Detection Workflow

This module provides an agentic version of the struggle detection workflow
where an agent decides when to use RAG tools based on state.
"""

from langchain_core.messages import HumanMessage
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from langgraph.graph import END, StateGraph
from loguru import logger

from agentic_py.agents.struggle_agent import create_struggle_agent
from agentic_py.config.workflows import (
    STRUGGLE_THRESHOLD_EDIT_FREQUENCY,
    STRUGGLE_THRESHOLD_ERROR_COUNT,
)
from agentic_py.prompts.loader import load_agent_user_message_template
from agentic_py.states.struggle import StruggleState


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


async def generate_lesson_agentic(
    state: StruggleState, checkpointer: AsyncPostgresSaver | None = None
) -> StruggleState:
    """
    Generate lesson recommendation using an agentic approach.

    The agent decides when to use RAG tools based on the current state.
    This is more flexible than the procedural approach as the agent can
    adapt its tool usage based on context.

    Args:
        state: Current workflow state with is_struggling flag
        checkpointer: Optional Postgres checkpointer for agent state persistence

    Returns:
        Updated state with lesson_recommendation if struggling
    """
    if not state["is_struggling"]:
        logger.debug("No lesson needed - user is not struggling")
        return {"lesson_recommendation": None}

    try:
        # Create agent with tools and checkpointer
        agent = await create_struggle_agent(checkpointer=checkpointer)

        # Load user message template from markdown file
        user_template = load_agent_user_message_template("agents/struggle_agent_user")

        # Prepare variables for the template
        error_logs_str = "\n".join(f"- {error}" for error in state.get("error_logs", []))
        history_str = "\n".join(f"- {item}" for item in state.get("history", [])) or "None"

        # Format user message using template
        user_message_content = user_template.format(
            edit_frequency=state.get("edit_frequency", 0.0),
            error_logs=error_logs_str,
            history=history_str,
        )

        # Invoke agent with the message
        # The agent will decide whether to use RAG tools
        result = await agent.ainvoke({"messages": [HumanMessage(content=user_message_content)]})

        # Extract lesson from agent response
        # The agent returns messages, get the last assistant message
        messages = result.get("messages", [])
        if messages:
            last_message = messages[-1]
            lesson = last_message.content if hasattr(last_message, "content") else str(last_message)
        else:
            lesson = "Review the documentation on state management."

        logger.info(
            "Lesson recommendation generated (agentic)",
            extra={
                "is_struggling": True,
                "has_recommendation": True,
                "agent_used_tools": len([m for m in messages if hasattr(m, "tool_calls")]) > 0,
            },
        )

        return {"lesson_recommendation": lesson}

    except Exception as e:
        logger.error(
            "Failed to generate lesson recommendation (agentic)",
            extra={
                "error": str(e),
                "error_type": type(e).__name__,
            },
            exc_info=True,
        )
        # Fallback to simple recommendation
        return {"lesson_recommendation": "Review the documentation on state management."}


def build_struggle_graph_agentic(checkpointer=None):
    """
    Build struggle detection workflow using agentic pattern.

    The agent decides when to use RAG tools based on state, making the
    workflow more adaptive and intelligent.

    Args:
        checkpointer: Optional checkpointer for state persistence (used for both
                     workflow state and agent state)

    Returns:
        Compiled LangGraph workflow
    """
    workflow = StateGraph(StruggleState)

    # Create a closure to pass checkpointer to the node
    def make_generate_lesson_node(checkpointer_arg):
        async def node(state: StruggleState) -> StruggleState:
            return await generate_lesson_agentic(state, checkpointer=checkpointer_arg)

        return node

    workflow.add_node("detect_struggle", detect_struggle)
    workflow.add_node("generate_lesson", make_generate_lesson_node(checkpointer))

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
