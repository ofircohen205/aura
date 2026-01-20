"""
Workflows API Schemas

Request and response models for workflows endpoints.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field

# Configuration
MAX_DIFF_CONTENT_LENGTH = 10_000_000  # 10MB limit to prevent DoS


class StruggleInput(BaseModel):
    """Input model for struggle detection workflow."""

    edit_frequency: float = Field(..., ge=0, description="Edit frequency per time unit")
    error_logs: list[str] = Field(default_factory=list, description="List of error messages")
    history: list[str] = Field(default_factory=list, description="Previous attempt history")


class AuditInput(BaseModel):
    """Input model for code audit workflow."""

    diff_content: str = Field(
        ...,
        min_length=0,
        max_length=MAX_DIFF_CONTENT_LENGTH,
        description="Git diff content to audit",
    )
    violations: list[str] = Field(default_factory=list, description="Pre-existing violations")


class WorkflowResponse(BaseModel):
    """Response model for workflow operations."""

    thread_id: str = Field(..., description="Unique thread identifier for this workflow execution")
    status: str = Field(..., description="Workflow execution status (completed, failed, etc.)")
    state: dict[str, Any] | None = Field(None, description="Final workflow state")
    created_at: datetime = Field(..., description="Workflow creation timestamp")
    type: str = Field(..., description="Workflow type (e.g., 'Struggle Detection', 'Code Audit')")
