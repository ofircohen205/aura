"""Workflows API Endpoints."""

from uuid import UUID

from fastapi import APIRouter, FastAPI, status

from api.v1.workflows.exceptions import register_exception_handlers
from api.v1.workflows.schemas import AuditInput, StruggleInput, WorkflowResponse
from core.exceptions import ValidationError
from services.workflows.service import workflow_service

router = APIRouter(prefix="/workflows", tags=["workflows"])


@router.post(
    "/struggle",
    response_model=WorkflowResponse,
    status_code=status.HTTP_200_OK,
    summary="Trigger struggle detection workflow",
    description="Analyzes user edit patterns and error logs to detect if the user is struggling. "
    "Returns a lesson recommendation if struggling is detected.",
    responses={
        200: {"description": "Workflow completed successfully"},
        500: {"description": "Workflow execution failed"},
        503: {"description": "Database connection unavailable"},
    },
)
async def trigger_struggle_workflow(inp: StruggleInput) -> WorkflowResponse:
    """
    Trigger the struggle detection workflow.

    This endpoint analyzes edit frequency and error patterns to determine
    if a user is struggling and generates appropriate lesson recommendations.
    """
    result = await workflow_service.trigger_struggle_workflow(
        edit_frequency=inp.edit_frequency,
        error_logs=inp.error_logs,
        history=inp.history,
    )
    return WorkflowResponse(**result)


@router.post(
    "/audit",
    response_model=WorkflowResponse,
    status_code=status.HTTP_200_OK,
    summary="Trigger code audit workflow",
    description="Performs static analysis on code changes to detect violations "
    "against coding standards and best practices.",
    responses={
        200: {"description": "Audit completed successfully"},
        400: {"description": "Invalid input (e.g., diff content too large)"},
        500: {"description": "Workflow execution failed"},
        503: {"description": "Database connection unavailable"},
    },
)
async def trigger_audit_workflow(inp: AuditInput) -> WorkflowResponse:
    """
    Trigger the code audit workflow.

    This endpoint analyzes code diffs for violations against coding standards
    and returns a pass/fail status with detailed violation information.
    """
    result = await workflow_service.trigger_audit_workflow(
        diff_content=inp.diff_content,
        violations=inp.violations,
    )
    return WorkflowResponse(**result)


@router.get(
    "/{thread_id}",
    response_model=WorkflowResponse,
    summary="Get workflow state",
    description="Retrieves the current state of a workflow by thread ID.",
    responses={
        200: {"description": "Workflow state retrieved successfully"},
        404: {"description": "Workflow not found"},
        503: {"description": "Database connection unavailable"},
    },
)
async def get_workflow_state(thread_id: str) -> WorkflowResponse:
    """
    Retrieve workflow state by thread ID.

    This endpoint allows querying the persisted state of a workflow execution.
    Useful for checking status of long-running workflows or retrieving results.
    """
    # Validate UUID format
    try:
        UUID(thread_id)
    except ValueError as e:
        raise ValidationError(f"Invalid thread_id format: {thread_id}") from e

    result = await workflow_service.get_workflow_state(thread_id=thread_id)
    return WorkflowResponse(**result)


def create_workflows_app() -> FastAPI:
    """Create and configure the workflows service FastAPI sub-application."""
    app = FastAPI(title="Workflows API")
    register_exception_handlers(app)
    app.include_router(router)
    return app
