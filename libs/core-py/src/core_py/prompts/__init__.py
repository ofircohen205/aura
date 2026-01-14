"""
Prompt Templates Module

This module provides prompt templates for LangGraph workflows.
Prompts are stored as markdown files and loaded using LangChain PromptTemplate.
"""

from core_py.prompts.loader import load_prompt

__all__ = ["load_prompt"]
