"""
Audit API Schemas

Request and response models for audit endpoints.
"""

from pydantic import BaseModel, Field


class AuditTriggerRequest(BaseModel):
    """Request model for triggering an audit."""

    repo_path: str = Field(..., description="Path to the repository to audit", min_length=1)


class AuditResponse(BaseModel):
    """Response model for audit operations."""

    status: str = Field(..., description="Audit status")
    repo: str = Field(..., description="Repository path")
    message: str = Field(..., description="Status message")
