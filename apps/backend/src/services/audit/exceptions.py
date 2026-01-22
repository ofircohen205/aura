"""
Audit Service Exceptions

Service-specific exceptions for audit operations.
"""

from api.exceptions import InternalServerError, ValidationError


class AuditExecutionError(InternalServerError):
    """Exception raised when audit execution fails."""

    def __init__(self, error: str):
        super().__init__(
            message="Audit execution failed",
            details={"error": error},
        )


class InvalidRepositoryPathError(ValidationError):
    """Exception raised when repository path is invalid."""

    def __init__(self, repo_path: str):
        super().__init__(
            message=f"Invalid repository path: {repo_path}",
            details={"repo_path": repo_path},
        )
