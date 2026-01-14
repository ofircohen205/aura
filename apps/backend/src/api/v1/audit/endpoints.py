"""Audit API Endpoints."""

from fastapi import APIRouter, FastAPI, Query

from api.v1.audit.exceptions import register_exception_handlers
from api.v1.audit.schemas import AuditResponse
from services.audit.service import audit_service

router = APIRouter(tags=["audit"])


@router.get(
    "/",
    summary="Trigger audit",
    description="Trigger a code audit for a repository",
    response_model=AuditResponse,
    status_code=200,
    responses={
        200: {"description": "Audit started successfully"},
        400: {"description": "Invalid repository path"},
        500: {"description": "Audit execution failed"},
    },
)
async def trigger_audit(
    repo_path: str = Query(..., description="Path to the repository to audit", min_length=1),
) -> AuditResponse:
    """
    Trigger a code audit for a repository.

    This endpoint initiates a code audit process that checks for
    violations against coding standards and best practices.
    """
    result = await audit_service.trigger_audit(repo_path=repo_path)
    return AuditResponse(**result)


def create_audit_app() -> FastAPI:
    """Create and configure the audit service FastAPI sub-application."""
    app = FastAPI(title="Audit API")
    register_exception_handlers(app)
    app.include_router(router)
    return app
