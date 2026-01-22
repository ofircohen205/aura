"""
Audit API Exception Handlers

Exception handlers for audit service exceptions.
"""

from fastapi import FastAPI, Request
from loguru import logger

from api.exceptions import create_error_response
from services.audit.exceptions import AuditExecutionError, InvalidRepositoryPathError


def register_exception_handlers(app: FastAPI) -> None:
    """Register exception handlers for the audit service."""

    @app.exception_handler(InvalidRepositoryPathError)
    async def invalid_repo_path_handler(request: Request, exc: InvalidRepositoryPathError):
        """Handle InvalidRepositoryPathError exceptions."""
        logger.warning(f"Invalid repository path: {exc}")
        return create_error_response(request, exc)

    @app.exception_handler(AuditExecutionError)
    async def audit_execution_error_handler(request: Request, exc: AuditExecutionError):
        """Handle AuditExecutionError exceptions."""
        logger.error(f"Audit execution error: {exc}")
        return create_error_response(request, exc)
