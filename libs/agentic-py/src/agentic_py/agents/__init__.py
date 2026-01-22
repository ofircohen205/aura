"""
Agents Module

Agent definitions for LangGraph workflows using tools.
Agents decide when to use tools based on state and tool descriptions.
"""

from agentic_py.agents.audit_agent import create_audit_agent
from agentic_py.agents.struggle_agent import create_struggle_agent

__all__ = [
    "create_struggle_agent",
    "create_audit_agent",
]
