"""
Base Agent Utilities

Shared utilities for creating and configuring agents.
"""

from typing import Any

from langchain.agents import create_agent
from langchain_core.language_models import BaseChatModel
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

from agentic_py.ai.llm import get_llm_client


async def create_agent_with_tools(
    tools: list[Any],
    system_prompt: str | None = None,
    llm: BaseChatModel | None = None,
    checkpointer: AsyncPostgresSaver | None = None,
) -> Any:
    """
    Create a ReACT agent with tools.

    Args:
        tools: List of LangChain tools (functions decorated with @tool)
        system_prompt: Optional system prompt for the agent
        llm: Optional LLM instance (will be created if not provided)

    Returns:
        LangGraph agent that can be used as a node in workflows
    """
    if llm is None:
        llm = await get_llm_client()
        if llm is None:
            raise RuntimeError("LLM is not enabled. Set LLM_ENABLED=true to use agents.")

    return create_agent(
        model=llm,
        tools=tools,
        system_prompt=system_prompt,
        checkpointer=checkpointer,
    )
