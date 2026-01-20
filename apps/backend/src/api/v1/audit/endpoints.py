"""Audit API Endpoints."""

from fastapi import APIRouter, Depends, FastAPI, Query, status

from api.v1.audit.exceptions import register_exception_handlers
from api.v1.audit.schemas import (
    AuditResponse,
    AuditTriggerRequest,
)
from api.v1.common.schemas import PaginatedResponse, PaginationParams
from services.audit.service import audit_service

router = APIRouter(tags=["audit"])


@router.get(
    "/",
    response_model=PaginatedResponse[AuditResponse],
    summary="List audits",
    description="Get a paginated list of audits. Currently returns empty list as audit listing is not yet fully implemented.",
    responses={
        200: {"description": "Audits retrieved successfully"},
        503: {"description": "Database connection unavailable"},
    },
)
async def list_audits(
    pagination: PaginationParams = Depends(),  # type: ignore[misc]
) -> PaginatedResponse[AuditResponse]:
    """
    List all audits with pagination.

    NOTE: This is a placeholder implementation. Full audit listing requires
    database schema changes to track audit history. Currently returns empty list.
    """
    # TODO: Implement full audit listing from database
    # For now, return empty paginated response
    return PaginatedResponse.create(
        items=[],
        total=0,
        page=pagination.page,
        page_size=pagination.page_size,
    )


@router.post(
    "/trigger",
    summary="Trigger audit",
    description="Trigger a code audit for a repository",
    response_model=AuditResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Audit started successfully"},
        400: {"description": "Invalid repository path"},
        500: {"description": "Audit execution failed"},
    },
)
async def trigger_audit(
    request: AuditTriggerRequest,
) -> AuditResponse:
    """
    Trigger a code audit for a repository.

    This endpoint initiates a code audit process that checks for
    violations against coding standards and best practices.
    """
    import uuid
    from datetime import datetime

    result = await audit_service.trigger_audit(repo_path=request.repo_path)
    # Add ID and timestamp for consistency with list endpoint
    audit_id = str(uuid.uuid4())
    return AuditResponse(
        id=audit_id,
        status=result["status"],
        repo=result["repo"],
        message=result["message"],
        created_at=datetime.utcnow().isoformat() + "Z",
        violations=None,
    )


@router.get(
    "/trigger",
    summary="Trigger audit (GET)",
    description="Trigger a code audit for a repository (GET method for backward compatibility)",
    response_model=AuditResponse,
    status_code=status.HTTP_200_OK,
    responses={
        200: {"description": "Audit started successfully"},
        400: {"description": "Invalid repository path"},
        500: {"description": "Audit execution failed"},
    },
)
async def trigger_audit_get(
    repo_path: str = Query(..., description="Path to the repository to audit", min_length=1),
) -> AuditResponse:
    """
    Trigger a code audit for a repository (GET method).

    This endpoint initiates a code audit process that checks for
    violations against coding standards and best practices.
    """
    import uuid
    from datetime import datetime

    result = await audit_service.trigger_audit(repo_path=repo_path)
    # Add ID and timestamp for consistency with list endpoint
    audit_id = str(uuid.uuid4())
    return AuditResponse(
        id=audit_id,
        status=result["status"],
        repo=result["repo"],
        message=result["message"],
        created_at=datetime.utcnow().isoformat() + "Z",
        violations=None,
    )


@router.get(
    "/{audit_id}",
    response_model=AuditResponse,
    summary="Get audit by ID",
    description="Retrieves a specific audit by its ID.",
    responses={
        200: {"description": "Audit retrieved successfully"},
        404: {"description": "Audit not found"},
        503: {"description": "Database connection unavailable"},
    },
)
async def get_audit(audit_id: str) -> AuditResponse:
    """
    Retrieve audit by ID.

    NOTE: This is a placeholder implementation. Full audit retrieval requires
    database schema changes to track audit history.
    """
    # TODO: Implement full audit retrieval from database
    from core.exceptions import NotFoundError

    raise NotFoundError(f"Audit {audit_id} not found. Audit storage not yet implemented.")


def create_audit_app() -> FastAPI:
    """Create and configure the audit service FastAPI sub-application."""
    app = FastAPI(title="Audit API")
    register_exception_handlers(app)
    app.include_router(router)
    return app
