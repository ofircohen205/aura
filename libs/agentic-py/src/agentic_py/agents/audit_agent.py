"""
Code Audit Agent

Agentic workflow for auditing code changes and checking for violations.
The agent can use RAG tools to retrieve relevant coding standards and best practices.
"""

from typing import Any

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from loguru import logger

from agentic_py.agents.base import create_agent_with_tools
from agentic_py.prompts.loader import load_agent_system_prompt
from agentic_py.tools.rag_tools import retrieve_knowledge


async def create_audit_agent(
    llm: Any | None = None,
    checkpointer: AsyncPostgresSaver | None = None,
) -> Any:
    """
    Create agentic code audit agent with RAG tools.

    The agent has access to retrieval tools to look up coding standards,
    best practices, and architectural patterns when analyzing code.

    Args:
        llm: Optional LLM instance (will be created if not provided)
        checkpointer: Optional Postgres checkpointer for state persistence

    Returns:
        LangGraph agent that can be used as a node in workflows

    Example:
        >>> agent = await create_audit_agent(checkpointer=checkpointer)
        >>> # Use in workflow:
        >>> workflow.add_node("agent", agent)
    """
    tools = [retrieve_knowledge]

    system_prompt = load_agent_system_prompt("agents/audit_agent_system")

    try:
        agent = await create_agent_with_tools(
            tools=tools,
            system_prompt=system_prompt,
            llm=llm,
            checkpointer=checkpointer,
        )
        logger.debug("Code audit agent created successfully")
        return agent
    except Exception as e:
        logger.error(f"Failed to create audit agent: {e}", exc_info=True)
        raise
