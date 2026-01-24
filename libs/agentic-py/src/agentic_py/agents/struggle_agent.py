"""
Struggle Detection Agent

Agentic workflow for detecting user struggles and generating lesson recommendations.
The agent decides when to use RAG tools based on the current state.
"""

from typing import Any

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from loguru import logger

from agentic_py.agents.base import create_agent_with_tools
from agentic_py.prompts.loader import load_agent_system_prompt
from agentic_py.tools.rag_tools import retrieve_contextual_lesson, retrieve_knowledge


async def create_struggle_agent(
    llm: Any | None = None,
    checkpointer: AsyncPostgresSaver | None = None,
) -> Any:
    """
    Create agentic struggle detection agent with RAG tools.

    The agent has access to retrieval tools and decides when to use them
    based on the current state. The LLM reads tool descriptions from
    docstrings to understand when each tool is appropriate.

    Args:
        llm: Optional LLM instance (will be created if not provided)
        checkpointer: Optional Postgres checkpointer for state persistence

    Returns:
        LangGraph agent that can be used as a node in workflows

    Example:
        >>> agent = await create_struggle_agent(checkpointer=checkpointer)
        >>> # Use in workflow:
        >>> workflow.add_node("agent", agent)
    """
    tools = [
        retrieve_knowledge,
        retrieve_contextual_lesson,
    ]

    system_prompt = load_agent_system_prompt("agents/struggle_agent_system")

    try:
        agent = await create_agent_with_tools(
            tools=tools,
            system_prompt=system_prompt,
            llm=llm,
            checkpointer=checkpointer,
        )
        logger.debug("Struggle detection agent created successfully")
        return agent
    except Exception as e:
        logger.error(f"Failed to create struggle agent: {e}", exc_info=True)
        raise
