"""
Workflows API Schemas

Request and response models for workflows endpoints.
"""

from datetime import datetime
from typing import Any, Literal

from pydantic import BaseModel, Field

# Configuration
MAX_DIFF_CONTENT_LENGTH = 10_000_000  # 10MB limit to prevent DoS

# Signal types supported by the enhanced detection system
SignalType = Literal["undo_redo", "time_pattern", "terminal", "debug", "semantic", "edit_pattern"]


class SignalMetadata(BaseModel):
    """Metadata for a detected signal."""

    type: SignalType = Field(..., description="Type of signal detected")
    score: float = Field(..., ge=0, le=1, description="Signal confidence score (0-1)")
    metadata: dict[str, Any] = Field(default_factory=dict, description="Signal-specific metadata")


class StruggleInput(BaseModel):
    """Input model for struggle detection workflow."""

    edit_frequency: float = Field(..., ge=0, description="Edit frequency per time unit")
    error_logs: list[str] = Field(default_factory=list, description="List of error messages")
    history: list[str] = Field(default_factory=list, description="Previous attempt history")

    # Optional client context (e.g. VSCode extension). These are not required by the workflow,
    # but help with observability and future improvements.
    source: str | None = Field(
        default=None, description="Client source identifier (e.g., 'vscode')"
    )
    file_path: str | None = Field(
        default=None, description="Absolute or workspace-relative file path"
    )
    language_id: str | None = Field(default=None, description="Editor language identifier")
    code_snippet: str | None = Field(
        default=None,
        max_length=50_000,
        description="Small code snippet around the struggle location (bounded for safety)",
    )
    client_timestamp: int | None = Field(
        default=None, description="Client-side timestamp in milliseconds since epoch"
    )
    struggle_reason: str | None = Field(
        default=None, description="Client-side trigger reason (e.g., retries, errors, frequency)"
    )
    retry_count: int | None = Field(
        default=None, ge=0, description="Detected retry count in window"
    )

    # Enhanced signal fields (from multi-signal detection system)
    combined_score: float | None = Field(
        default=None,
        ge=0,
        le=1,
        description="Weighted aggregate score from all signals (0-1)",
    )
    primary_signal: SignalType | None = Field(
        default=None,
        description="The signal type that contributed most to the detection",
    )
    signals: list[SignalMetadata] | None = Field(
        default=None,
        description="All contributing signals with their scores and metadata",
    )

    # Signal-specific context fields
    undo_redo_pattern: str | None = Field(
        default=None,
        description="Description of detected undo/redo pattern (e.g., 'undo-redo-undo cycle')",
    )
    hesitation_ms: int | None = Field(
        default=None,
        ge=0,
        description="Longest pause before rapid edits in milliseconds",
    )
    terminal_errors: list[str] | None = Field(
        default=None,
        description="Stack traces or error messages from terminal output",
    )
    debug_breakpoint_changes: int | None = Field(
        default=None,
        ge=0,
        description="Number of breakpoint add/remove/change operations",
    )


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
