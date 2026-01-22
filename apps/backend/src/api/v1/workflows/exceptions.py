"""
Workflows API Exception Handlers

Exception handlers for workflows service exceptions.
"""

from fastapi import FastAPI, Request
from loguru import logger

from api.exceptions import create_error_response
from services.workflows.exceptions import (
    WorkflowExecutionError,
    WorkflowNotFoundError,
    WorkflowServiceUnavailableError,
)


def register_exception_handlers(app: FastAPI) -> None:
    """Register exception handlers for the workflows service."""

    @app.exception_handler(WorkflowNotFoundError)
    async def workflow_not_found_handler(request: Request, exc: WorkflowNotFoundError):
        """Handle WorkflowNotFoundError exceptions."""
        logger.warning(f"Workflow not found: {exc}")
        return create_error_response(request, exc)

    @app.exception_handler(WorkflowExecutionError)
    async def workflow_execution_error_handler(request: Request, exc: WorkflowExecutionError):
        """Handle WorkflowExecutionError exceptions."""
        logger.error(f"Workflow execution error: {exc}")
        return create_error_response(request, exc)

    @app.exception_handler(WorkflowServiceUnavailableError)
    async def workflow_service_unavailable_handler(
        request: Request, exc: WorkflowServiceUnavailableError
    ):
        """Handle WorkflowServiceUnavailableError exceptions."""
        logger.error(f"Workflow service unavailable: {exc}")
        return create_error_response(request, exc)
