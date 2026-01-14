"""
Events API Exception Handlers

Exception handlers for events service exceptions.
"""

from fastapi import FastAPI, Request
from loguru import logger

from core.exceptions import create_error_response
from services.events.exceptions import EventProcessingError, InvalidEventError


def register_exception_handlers(app: FastAPI) -> None:
    """Register exception handlers for the events service."""

    @app.exception_handler(InvalidEventError)
    async def invalid_event_handler(request: Request, exc: InvalidEventError):
        """Handle InvalidEventError exceptions."""
        logger.warning(f"Invalid event: {exc}")
        return create_error_response(request, exc)

    @app.exception_handler(EventProcessingError)
    async def event_processing_error_handler(request: Request, exc: EventProcessingError):
        """Handle EventProcessingError exceptions."""
        logger.error(f"Event processing error: {exc}")
        return create_error_response(request, exc)
