"""
Workflow Configuration

Configuration for workflow-specific settings like thresholds and limits using Pydantic Settings.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class WorkflowConfig(BaseSettings):
    """Workflow configuration for thresholds and limits."""

    model_config = SettingsConfigDict(
        env_prefix="",
        case_sensitive=False,
        extra="ignore",
    )

    # Struggle Detection Configuration
    struggle_threshold_edit_frequency: float = Field(
        default=10.0,
        ge=0.0,
        description="Edit frequency threshold for struggle detection",
    )
    struggle_threshold_error_count: int = Field(
        default=2,
        ge=0,
        description="Error count threshold for struggle detection",
    )

    # Code Audit Configuration
    audit_function_length_threshold: int = Field(
        default=50,
        ge=1,
        description="Function length threshold for audit (lines)",
    )


# Global instance (lazy-loaded)
_workflow_config: WorkflowConfig | None = None


def get_workflow_config() -> WorkflowConfig:
    """Get workflow configuration instance (singleton)."""
    global _workflow_config
    if _workflow_config is None:
        _workflow_config = WorkflowConfig()
    return _workflow_config


# Backward compatibility: export as module-level constants
_config = get_workflow_config()
STRUGGLE_THRESHOLD_EDIT_FREQUENCY = _config.struggle_threshold_edit_frequency
STRUGGLE_THRESHOLD_ERROR_COUNT = _config.struggle_threshold_error_count
AUDIT_FUNCTION_LENGTH_THRESHOLD = _config.audit_function_length_threshold
