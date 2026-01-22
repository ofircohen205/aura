"""
Events Service Exceptions

Service-specific exceptions for event processing.
"""

from api.exceptions import InternalServerError, ValidationError


class EventProcessingError(InternalServerError):
    """Exception raised when event processing fails."""

    def __init__(self, error: str):
        super().__init__(
            message="Event processing failed",
            details={"error": error},
        )


class InvalidEventError(ValidationError):
    """Exception raised when event data is invalid."""

    def __init__(self, message: str, details: dict | None = None):
        super().__init__(
            message=message,
            details=details or {},
        )
