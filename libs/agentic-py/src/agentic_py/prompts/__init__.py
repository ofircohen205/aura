"""
Prompt Templates Module

This module provides prompt templates for LangGraph workflows.
Prompts are stored as markdown files and loaded using LangChain PromptTemplate.
"""

from agentic_py.prompts.loader import (
    load_agent_system_prompt,
    load_agent_user_message_template,
    load_prompt,
)

__all__ = [
    "load_prompt",
    "load_agent_system_prompt",
    "load_agent_user_message_template",
]
