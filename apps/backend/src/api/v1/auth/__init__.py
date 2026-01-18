"""
Authentication API

FastAPI sub-application for user authentication and authorization.
"""

from api.v1.auth.endpoints import create_auth_app

__all__ = ["create_auth_app"]
