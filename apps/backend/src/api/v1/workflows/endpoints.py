"""Workflows API Endpoints."""

from uuid import UUID

from fastapi import APIRouter, Depends, FastAPI, Request, status
from loguru import logger

from api.exceptions import ValidationError
from api.logging import get_log_context, log_operation
from api.v1.common.schemas import PaginatedResponse, PaginationParams
from api.v1.workflows.exceptions import register_exception_handlers
from api.v1.workflows.schemas import (
    AuditInput,
    StruggleInput,
    WorkflowResponse,
)
from services.workflows.service import workflow_service

router = APIRouter(tags=["workflows"])


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
async def trigger_struggle_workflow(
    inp: StruggleInput,
    request: Request,
) -> WorkflowResponse:
    """
    Trigger the struggle detection workflow.

    This endpoint analyzes edit frequency and error patterns to determine
    if a user is struggling and generates appropriate lesson recommendations.
    """
    with log_operation(
        "trigger_struggle_workflow",
        request,
        edit_frequency=inp.edit_frequency,
        error_logs_count=len(inp.error_logs),
        history_count=len(inp.history) if inp.history else 0,
    ) as op_ctx:
        result = await workflow_service.trigger_struggle_workflow(
            edit_frequency=inp.edit_frequency,
            error_logs=inp.error_logs,
            history=inp.history,
        )

        op_ctx["thread_id"] = result.get("thread_id")
        op_ctx["status"] = result.get("status")
        is_struggling = result.get("state", {}).get("is_struggling", False)
        op_ctx["is_struggling"] = is_struggling
        op_ctx["has_recommendation"] = (
            result.get("state", {}).get("lesson_recommendation") is not None
        )

        logger.info(
            "Struggle workflow triggered successfully",
            extra=op_ctx,
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
async def trigger_audit_workflow(
    inp: AuditInput,
    request: Request,
) -> WorkflowResponse:
    """
    Trigger the code audit workflow.

    This endpoint analyzes code diffs for violations against coding standards
    and returns a pass/fail status with detailed violation information.
    """
    with log_operation(
        "trigger_audit_workflow",
        request,
        diff_length=len(inp.diff_content),
        pre_existing_violations_count=len(inp.violations) if inp.violations else 0,
    ) as op_ctx:
        result = await workflow_service.trigger_audit_workflow(
            diff_content=inp.diff_content,
            violations=inp.violations,
        )

        op_ctx["thread_id"] = result.get("thread_id")
        op_ctx["status"] = result.get("status")
        violation_count = len(result.get("state", {}).get("violations", []))
        op_ctx["violation_count"] = violation_count

        logger.info(
            "Audit workflow triggered successfully",
            extra=op_ctx,
        )

        return WorkflowResponse(**result)


@router.get(
    "/",
    response_model=PaginatedResponse[WorkflowResponse],
    summary="List workflows",
    description="Get a paginated list of workflows. Currently returns empty list as workflow listing is not yet fully implemented.",
    responses={
        200: {"description": "Workflows retrieved successfully"},
        503: {"description": "Database connection unavailable"},
    },
)
async def list_workflows(
    request: Request,
    pagination: PaginationParams = Depends(),  # type: ignore[misc]
) -> PaginatedResponse[WorkflowResponse]:
    """
    List all workflows with pagination.

    NOTE: This is a placeholder implementation. Full workflow listing requires
    database schema changes to track workflow metadata. Currently returns empty list.
    """
    log_context = get_log_context(request, page=pagination.page, page_size=pagination.page_size)
    logger.debug(
        "Listing workflows (placeholder implementation)",
        extra=log_context,
    )

    # TODO: Implement full workflow listing from checkpointer or database
    # For now, return empty paginated response
    return PaginatedResponse.create(
        items=[],
        total=0,
        page=pagination.page,
        page_size=pagination.page_size,
    )


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
async def get_workflow_state(
    thread_id: str,
    request: Request,
) -> WorkflowResponse:
    """
    Retrieve workflow state by thread ID.

    This endpoint allows querying the persisted state of a workflow execution.
    Useful for checking status of long-running workflows or retrieving results.
    """
    with log_operation(
        "get_workflow_state",
        request,
        thread_id=thread_id,
    ) as op_ctx:
        try:
            UUID(thread_id)
        except ValueError as e:
            op_ctx["error"] = f"Invalid thread_id format: {thread_id}"
            logger.warning(
                "Invalid thread_id format",
                extra=op_ctx,
            )
            raise ValidationError(f"Invalid thread_id format: {thread_id}") from e

        result = await workflow_service.get_workflow_state(thread_id=thread_id)

        op_ctx["status"] = result.get("status")
        op_ctx["workflow_type"] = result.get("type")

        logger.info(
            "Workflow state retrieved successfully",
            extra=op_ctx,
        )

        return WorkflowResponse(**result)


def create_workflows_app() -> FastAPI:
    """Create and configure the workflows service FastAPI sub-application."""
    app = FastAPI(title="Workflows API")
    register_exception_handlers(app)
    app.include_router(router)
    return app
