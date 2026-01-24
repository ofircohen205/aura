"""
State Definitions

TypedDict state definitions for LangGraph workflows.
States are separated from workflow logic for reusability and clarity.
"""

from agentic_py.states.audit import AuditState, validate_audit_state
from agentic_py.states.struggle import StruggleState, validate_struggle_state

__all__ = [
    "AuditState",
    "validate_audit_state",
    "StruggleState",
    "validate_struggle_state",
]
