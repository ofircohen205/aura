"""
Workflow Service Exceptions

Service-specific exceptions for workflow operations.
"""

from core.exceptions import InternalServerError, NotFoundError, ServiceUnavailableError


class WorkflowNotFoundError(NotFoundError):
    """Exception raised when a workflow is not found."""

    def __init__(self, thread_id: str):
        super().__init__(
            message=f"Workflow with thread_id '{thread_id}' not found",
            details={"thread_id": thread_id},
        )


class WorkflowExecutionError(InternalServerError):
    """Exception raised when workflow execution fails."""

    def __init__(self, workflow_type: str, error: str):
        super().__init__(
            message="Workflow execution failed. Please try again later.",
            details={"workflow_type": workflow_type, "error": error},
        )


class WorkflowServiceUnavailableError(ServiceUnavailableError):
    """Exception raised when workflow service is unavailable."""

    def __init__(self, error: str):
        super().__init__(
            message="Service temporarily unavailable. Please try again later.",
            details={"error": error},
        )
