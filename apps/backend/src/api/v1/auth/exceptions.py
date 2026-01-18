"""
Authentication API Exceptions

API-level exceptions for authentication endpoints.
These exceptions are registered with FastAPI exception handlers.
"""


def register_exception_handlers(app):
    """
    Register authentication exception handlers with FastAPI app.

    Args:
        app: FastAPI application instance

    Note:
        All auth exceptions inherit from BaseApplicationException,
        which is already handled by the global exception handler in main.py.
        No special handling is needed here.
    """
    # No special handling needed - use global handler
    pass
