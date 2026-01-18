"""
Exception Handling Framework

Base exception classes and HTTP exception mapping utilities.
Provides consistent error handling across the application.
"""

from typing import Any

from fastapi import Request, status
from fastapi.responses import JSONResponse


class BaseApplicationException(Exception):
    """Base exception for all application-specific exceptions."""

    def __init__(
        self,
        message: str,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        details: dict[str, Any] | None = None,
    ):
        """
        Initialize base application exception.

        Args:
            message: Human-readable error message
            status_code: HTTP status code for this exception
            details: Additional error details
        """
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)


class NotFoundError(BaseApplicationException):
    """Exception raised when a requested resource is not found."""

    def __init__(self, message: str = "Resource not found", details: dict[str, Any] | None = None):
        super().__init__(message, status.HTTP_404_NOT_FOUND, details)


class ValidationError(BaseApplicationException):
    """Exception raised when input validation fails."""

    def __init__(self, message: str = "Validation error", details: dict[str, Any] | None = None):
        super().__init__(message, status.HTTP_400_BAD_REQUEST, details)


class ConflictError(BaseApplicationException):
    """Exception raised when a resource conflict occurs."""

    def __init__(self, message: str = "Resource conflict", details: dict[str, Any] | None = None):
        super().__init__(message, status.HTTP_409_CONFLICT, details)


class UnauthorizedError(BaseApplicationException):
    """Exception raised when authentication is required or fails."""

    def __init__(self, message: str = "Unauthorized", details: dict[str, Any] | None = None):
        super().__init__(message, status.HTTP_401_UNAUTHORIZED, details)


class ForbiddenError(BaseApplicationException):
    """Exception raised when access is forbidden."""

    def __init__(self, message: str = "Forbidden", details: dict[str, Any] | None = None):
        super().__init__(message, status.HTTP_403_FORBIDDEN, details)


class ServiceUnavailableError(BaseApplicationException):
    """Exception raised when a service is temporarily unavailable."""

    def __init__(
        self,
        message: str = "Service temporarily unavailable",
        details: dict[str, Any] | None = None,
    ):
        super().__init__(message, status.HTTP_503_SERVICE_UNAVAILABLE, details)


class InternalServerError(BaseApplicationException):
    """Exception raised for internal server errors."""

    def __init__(
        self, message: str = "Internal server error", details: dict[str, Any] | None = None
    ):
        super().__init__(message, status.HTTP_500_INTERNAL_SERVER_ERROR, details)


def create_error_response(
    request: Request,
    exc: BaseApplicationException,
    correlation_id: str | None = None,
) -> JSONResponse:
    """
    Create a standardized error response from an application exception.

    Args:
        request: FastAPI request object
        exc: Application exception instance
        correlation_id: Optional correlation ID for request tracing

    Returns:
        JSONResponse with standardized error format
    """
    error_response = {
        "error": {
            "message": exc.message,
            "type": exc.__class__.__name__,
            "status_code": exc.status_code,
        },
    }

    # Add details if present
    if exc.details:
        error_response["error"]["details"] = exc.details

    # Add correlation ID if available
    if correlation_id:
        error_response["error"]["correlation_id"] = correlation_id

    # Add request path for debugging
    error_response["error"]["path"] = request.url.path

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response,
    )


async def application_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """
    Global exception handler for BaseApplicationException.

    Args:
        request: FastAPI request object
        exc: Application exception instance

    Returns:
        JSONResponse with error details
    """
    # Type narrowing: we know this is BaseApplicationException from the handler registration
    if not isinstance(exc, BaseApplicationException):
        # This shouldn't happen, but handle gracefully
        raise TypeError(f"Expected BaseApplicationException, got {type(exc)}")

    # Type narrowing ensures exc is BaseApplicationException here
    app_exc: BaseApplicationException = exc

    # Try to get correlation ID from request state (set by logging middleware)
    correlation_id = getattr(request.state, "correlation_id", None)

    return create_error_response(request, app_exc, correlation_id)


async def generic_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    """
    Global exception handler for unhandled exceptions.

    Args:
        request: FastAPI request object
        exc: Unhandled exception instance

    Returns:
        JSONResponse with error details
    """
    from core.config import get_settings

    # Log the exception (logging middleware should handle this)
    settings = get_settings()
    correlation_id = getattr(request.state, "correlation_id", None)

    # Sanitize error messages in production to prevent information disclosure
    if settings.environment.value == "production":
        error_message = "An unexpected error occurred"
        error_type = "InternalServerError"
    else:
        error_message = str(exc)
        error_type = exc.__class__.__name__

    error_response = {
        "error": {
            "message": error_message,
            "type": error_type,
            "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,
            "path": request.url.path,
        },
    }

    if correlation_id:
        error_response["error"]["correlation_id"] = correlation_id

    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=error_response,
    )
