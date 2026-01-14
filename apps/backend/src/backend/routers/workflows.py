"""
Workflow API Endpoints

Provides REST API for triggering and querying LangGraph workflows.
Includes error handling, logging, and input validation.
"""

import logging
import uuid
from typing import Any

from core_py.workflows.audit import build_audit_graph
from core_py.workflows.checkpointer import get_checkpointer
from core_py.workflows.struggle import build_struggle_graph
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, field_validator

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/workflows", tags=["workflows"])

# Configuration
MAX_DIFF_CONTENT_LENGTH = 10_000_000  # 10MB limit to prevent DoS


# Data Models
class StruggleInput(BaseModel):
    """
    Input model for struggle detection workflow.

    This model represents the input data needed to detect if a developer is struggling
    based on their editing patterns and error logs.

    Examples:
        ```json
        {
            "edit_frequency": 15.5,
            "error_logs": ["TypeError: 'NoneType' object is not callable"],
            "history": ["Previous attempt: tried using dict.get()"]
        }
        ```

    Attributes:
        edit_frequency: Number of edits per time unit (e.g., per minute).
            Higher values indicate more frequent changes, potentially suggesting struggle.
            Must be >= 0.
        error_logs: List of error messages encountered during development.
            Empty list if no errors. Multiple errors may indicate struggle.
        history: List of previous attempt descriptions or context.
            Helps avoid repeating the same advice. Can be empty.
    """

    edit_frequency: float = Field(
        ...,
        ge=0,
        description="Edit frequency per time unit (e.g., edits per minute). Higher values may indicate struggle.",
        example=12.5,
    )
    error_logs: list[str] = Field(
        default_factory=list,
        description="List of error messages encountered. Empty list if no errors.",
        example=[
            "TypeError: 'NoneType' object is not callable",
            "AttributeError: 'str' object has no attribute 'append'",
        ],
    )

    @field_validator("error_logs")
    @classmethod
    def validate_error_logs(cls, v: list[str]) -> list[str]:
        """
        Validate and sanitize error logs.

        Limits individual error log length and total count to prevent abuse.
        """
        if len(v) > 100:  # Limit total number of errors
            import logging

            logger = logging.getLogger(__name__)
            logger.warning(
                "Too many error logs provided, truncating",
                extra={"original_count": len(v)},
            )
            v = v[:100]

        # Limit individual error log length
        max_error_length = 1000
        sanitized = []
        for error in v:
            if len(error) > max_error_length:
                sanitized.append(error[:max_error_length] + "... [truncated]")
            else:
                sanitized.append(error)

        return sanitized

    history: list[str] = Field(
        default_factory=list,
        description="Previous attempt history or context. Helps personalize lesson recommendations.",
        example=[
            "Tried using dict.get() with default value",
            "Attempted to use list comprehension",
        ],
    )


class AuditInput(BaseModel):
    """
    Input model for code audit workflow.

    This model represents the input data needed to audit code changes for violations
    against coding standards and best practices.

    Examples:
        ```json
        {
            "diff_content": "--- a/src/file.py\\n+++ b/src/file.py\\n@@ -1,3 +1,3 @@\\n def foo():\\n-    pass\\n+    print('hello')\\n",
            "violations": []
        }
        ```

    Attributes:
        diff_content: Git unified diff format content to audit.
            Must be valid git diff format. Maximum length is 10MB to prevent DoS.
        violations: Pre-existing violations that should be included in the audit.
            Useful for aggregating violations from multiple sources. Can be empty.
    """

    diff_content: str = Field(
        ...,
        min_length=0,
        max_length=MAX_DIFF_CONTENT_LENGTH,
        description="Git unified diff content to audit. Must be in standard git diff format (unified diff).",
        example="--- a/src/file.py\n+++ b/src/file.py\n@@ -1,3 +1,3 @@\n def foo():\n-    pass\n+    print('hello')\n",
    )

    @field_validator("diff_content")
    @classmethod
    def validate_diff_format(cls, v: str) -> str:
        """
        Validate that diff content appears to be in valid git diff format.

        Basic validation to catch obviously malformed diffs early.
        """
        if not v.strip():
            return v  # Empty diff is valid

        # Check for basic git diff markers
        has_file_headers = "---" in v or "+++" in v
        has_hunk_headers = "@@" in v

        # If content is substantial but lacks diff markers, warn
        if len(v) > 100 and not (has_file_headers or has_hunk_headers):
            import logging

            logger = logging.getLogger(__name__)
            logger.warning(
                "Diff content may not be in valid git diff format",
                extra={"content_preview": v[:200]},
            )

        return v

    violations: list[str] = Field(
        default_factory=list,
        description="Pre-existing violations to include in the audit result. Can be empty.",
        example=[],
    )

    @field_validator("diff_content")
    @classmethod
    def validate_diff_content(cls, v: str) -> str:
        """Validate diff content size."""
        if len(v) > MAX_DIFF_CONTENT_LENGTH:
            raise ValueError(
                f"Diff content exceeds maximum length of {MAX_DIFF_CONTENT_LENGTH} characters"
            )
        return v


class WorkflowResponse(BaseModel):
    """
    Response model for workflow operations.

    This model represents the response from workflow execution endpoints.
    It includes the workflow state and execution status.

    Examples:
        ```json
        {
            "thread_id": "550e8400-e29b-41d4-a716-446655440000",
            "status": "completed",
            "state": {
                "is_struggling": true,
                "lesson_recommendation": "Review the documentation on state management."
            }
        }
        ```

    Attributes:
        thread_id: Unique identifier for this workflow execution.
            Can be used to retrieve workflow state later via GET endpoint.
        status: Execution status of the workflow.
            Common values: "completed", "failed", "in_progress".
        state: Final workflow state containing all results and intermediate data.
            Structure varies by workflow type (struggle vs audit).
            None if workflow failed before producing state.
    """

    thread_id: str = Field(
        ...,
        description="Unique thread identifier for this workflow execution. Use this ID to retrieve workflow state later.",
        example="550e8400-e29b-41d4-a716-446655440000",
    )
    status: str = Field(
        ...,
        description="Workflow execution status. Values: 'completed', 'failed', 'in_progress'.",
        example="completed",
    )
    state: dict[str, Any] | None = Field(
        None,
        description="Final workflow state containing results and intermediate data. Structure varies by workflow type.",
        example={
            "is_struggling": True,
            "lesson_recommendation": "Review documentation on state management.",
        },
    )


@router.post(
    "/struggle",
    response_model=WorkflowResponse,
    status_code=status.HTTP_200_OK,
    summary="Trigger struggle detection workflow",
    description="""
    Analyzes user edit patterns and error logs to detect if the user is struggling.

    This workflow uses LangGraph to process development metrics and determine if a developer
    is experiencing difficulty. When struggling is detected, it generates personalized lesson
    recommendations based on the specific errors and patterns observed.

    **Workflow Process:**
    1. Analyzes edit frequency and error count against configurable thresholds
    2. Determines if user is struggling (is_struggling flag)
    3. If struggling, generates lesson recommendation (currently placeholder, will use RAG)

    **Usage Example:**
    ```bash
    curl -X POST "http://localhost:8000/api/v1/workflows/struggle" \\
      -H "Content-Type: application/json" \\
      -d '{
        "edit_frequency": 15.0,
        "error_logs": ["TypeError: 'NoneType' object is not callable"],
        "history": []
      }'
    ```

    **Response:**
    - If struggling: Returns lesson_recommendation with guidance
    - If not struggling: Returns null lesson_recommendation
    """,
    responses={
        200: {
            "description": "Workflow completed successfully",
            "content": {
                "application/json": {
                    "example": {
                        "thread_id": "550e8400-e29b-41d4-a716-446655440000",
                        "status": "completed",
                        "state": {
                            "edit_frequency": 15.0,
                            "error_logs": ["TypeError: 'NoneType' object is not callable"],
                            "history": [],
                            "is_struggling": True,
                            "lesson_recommendation": "Review the documentation on state management.",
                        },
                    }
                }
            },
        },
        422: {"description": "Validation error - invalid input parameters"},
        500: {"description": "Workflow execution failed - internal server error"},
        503: {"description": "Service unavailable - database connection failed"},
    },
)
async def trigger_struggle_workflow(inp: StruggleInput):
    """
    Trigger the struggle detection workflow.

    This endpoint analyzes edit frequency and error patterns to determine
    if a user is struggling and generates appropriate lesson recommendations.

    **Input Parameters:**
    - `edit_frequency`: Number of edits per time unit. Values > 10.0 typically indicate struggle.
    - `error_logs`: List of error messages. More than 2 errors may indicate struggle.
    - `history`: Previous attempts or context to avoid repeating advice.

    **Output:**
    - `is_struggling`: Boolean indicating if struggle was detected
    - `lesson_recommendation`: Personalized lesson if struggling, null otherwise
    - `thread_id`: Unique identifier for retrieving workflow state later

    **Error Handling:**
    - Returns 422 if input validation fails (e.g., negative edit_frequency)
    - Returns 500 if workflow execution fails
    - Returns 503 if database is unavailable
    """
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    logger.info(
        "Struggle workflow triggered",
        extra={
            "thread_id": thread_id,
            "edit_frequency": inp.edit_frequency,
            "error_count": len(inp.error_logs),
        },
    )

    try:
        async with get_checkpointer() as checkpointer:
            graph = build_struggle_graph(checkpointer=checkpointer)

            # Validate and normalize initial state
            from core_py.workflows.struggle import validate_struggle_state

            initial_state = validate_struggle_state(
                {
                    "edit_frequency": inp.edit_frequency,
                    "error_logs": inp.error_logs,
                    "history": inp.history,
                    "is_struggling": False,
                    "lesson_recommendation": None,
                }
            )

            # Run the graph (invoke returns the final state)
            try:
                final_state = await graph.ainvoke(initial_state, config=config)
            except Exception as e:
                logger.error(
                    "Workflow graph execution failed",
                    extra={
                        "thread_id": thread_id,
                        "workflow_type": "struggle",
                        "error": str(e),
                        "error_type": type(e).__name__,
                    },
                    exc_info=True,
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Workflow execution failed. Please try again later.",
                ) from e

            logger.info(
                "Struggle workflow completed",
                extra={
                    "thread_id": thread_id,
                    "is_struggling": final_state.get("is_struggling", False),
                    "has_recommendation": final_state.get("lesson_recommendation") is not None,
                },
            )

            return {"thread_id": thread_id, "status": "completed", "state": final_state}

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(
            "Struggle workflow failed",
            extra={
                "thread_id": thread_id,
                "error": str(e),
                "error_type": type(e).__name__,
            },
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service temporarily unavailable. Please try again later.",
        ) from e


@router.post(
    "/audit",
    response_model=WorkflowResponse,
    status_code=status.HTTP_200_OK,
    summary="Trigger code audit workflow",
    description="""
    Performs static analysis on code changes to detect violations against coding standards.

    This workflow uses LangGraph to parse git diffs and check for violations using AST parsing
    and pattern matching. It provides detailed violation information including file paths,
    line numbers, severity levels, and remediation suggestions.

    **Workflow Process:**
    1. Parses git diff format to extract file paths, line numbers, and code blocks
    2. Analyzes code using AST parsing (for Python) and pattern matching
    3. Detects violations such as:
       - Print statements in production code
       - Debugger calls (pdb, ipdb, breakpoint)
       - Hardcoded secrets (passwords, API keys, tokens)
       - Long functions (>50 lines)
    4. Returns pass/fail status with detailed violation information

    **Usage Example:**
    ```bash
    curl -X POST "http://localhost:8000/api/v1/workflows/audit" \\
      -H "Content-Type: application/json" \\
      -d '{
        "diff_content": "--- a/src/file.py\\n+++ b/src/file.py\\n@@ -1,3 +1,3 @@\\n def foo():\\n-    pass\\n+    print('hello')\\n",
        "violations": []
      }'
    ```

    **Response:**
    - `status`: "pass" if no violations, "fail" if violations found
    - `violations`: List of violation messages
    - `violation_details`: Detailed violation information with file, line, severity, remediation
    """,
    responses={
        200: {
            "description": "Audit completed successfully",
            "content": {
                "application/json": {
                    "example": {
                        "thread_id": "550e8400-e29b-41d4-a716-446655440000",
                        "status": "completed",
                        "state": {
                            "diff_content": "--- a/src/file.py\n+++ b/src/file.py\n@@ -1,3 +1,3 @@\n def foo():\n-    pass\n+    print('hello')\n",
                            "violations": [
                                "Avoid using print statements in production code. Use logging instead."
                            ],
                            "status": "fail",
                            "violation_details": [
                                {
                                    "file_path": "src/file.py",
                                    "line_number": 3,
                                    "severity": "error",
                                    "rule_name": "no_print_statements",
                                    "message": "Avoid using print statements in production code. Use logging instead.",
                                    "remediation": "Replace print() with logger.debug() or logger.info()",
                                }
                            ],
                        },
                    }
                }
            },
        },
        400: {"description": "Invalid input - diff content too large (exceeds 10MB limit)"},
        422: {"description": "Validation error - invalid input format"},
        500: {"description": "Workflow execution failed - internal server error"},
        503: {"description": "Service unavailable - database connection failed"},
    },
)
async def trigger_audit_workflow(inp: AuditInput):
    """
    Trigger the code audit workflow.

    This endpoint analyzes code diffs for violations against coding standards
    and returns a pass/fail status with detailed violation information.

    **Input Parameters:**
    - `diff_content`: Git unified diff format content. Must be valid git diff format.
      Maximum size: 10MB to prevent DoS attacks.
    - `violations`: Pre-existing violations to include in results (optional).

    **Output:**
    - `status`: "pass" if no violations, "fail" if violations detected
    - `violations`: List of violation messages (human-readable)
    - `violation_details`: List of detailed violation objects with:
      - `file_path`: Path to file with violation
      - `line_number`: Line number of violation
      - `severity`: "error", "warning", or "info"
      - `rule_name`: Identifier for the violated rule
      - `message`: Human-readable violation message
      - `remediation`: Suggested fix for the violation
    - `parsed_files`: List of files changed in the diff
    - `parsed_hunks`: List of diff hunks with line numbers
    - `file_extensions`: Set of file extensions in the diff

    **Error Handling:**
    - Returns 400 if diff content exceeds size limit
    - Returns 422 if input validation fails
    - Returns 500 if workflow execution fails
    - Returns 503 if database is unavailable
    """
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}

    logger.info(
        "Audit workflow triggered",
        extra={
            "thread_id": thread_id,
            "diff_length": len(inp.diff_content),
            "pre_existing_violations": len(inp.violations),
        },
    )

    try:
        async with get_checkpointer() as checkpointer:
            graph = build_audit_graph(checkpointer=checkpointer)

            # Validate and normalize initial state
            from core_py.workflows.audit import validate_audit_state

            initial_state = validate_audit_state(
                {
                    "diff_content": inp.diff_content,
                    "violations": inp.violations,
                    "status": "pending",
                }
            )

            try:
                final_state = await graph.ainvoke(initial_state, config=config)
            except Exception as e:
                logger.error(
                    "Workflow graph execution failed",
                    extra={
                        "thread_id": thread_id,
                        "workflow_type": "audit",
                        "error": str(e),
                        "error_type": type(e).__name__,
                    },
                    exc_info=True,
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Workflow execution failed. Please try again later.",
                ) from e

            logger.info(
                "Audit workflow completed",
                extra={
                    "thread_id": thread_id,
                    "status": final_state.get("status", "unknown"),
                    "violation_count": len(final_state.get("violations", [])),
                },
            )

            return {"thread_id": thread_id, "status": "completed", "state": final_state}

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(
            "Audit workflow failed",
            extra={
                "thread_id": thread_id,
                "error": str(e),
                "error_type": type(e).__name__,
            },
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service temporarily unavailable. Please try again later.",
        ) from e


@router.get(
    "/{thread_id}",
    response_model=WorkflowResponse,
    summary="Get workflow state",
    description="""
    Retrieves the current state of a workflow by thread ID.

    This endpoint allows querying the persisted state of a workflow execution.
    Useful for checking status of long-running workflows, retrieving results,
    or debugging workflow execution.

    **Usage Example:**
    ```bash
    curl "http://localhost:8000/api/v1/workflows/550e8400-e29b-41d4-a716-446655440000"
    ```

    **Response:**
    Returns the workflow state as stored in the database checkpoint.
    The state structure varies by workflow type (struggle vs audit).
    """,
    responses={
        200: {
            "description": "Workflow state retrieved successfully",
            "content": {
                "application/json": {
                    "example": {
                        "thread_id": "550e8400-e29b-41d4-a716-446655440000",
                        "status": "completed",
                        "state": {
                            "is_struggling": True,
                            "lesson_recommendation": "Review the documentation on state management.",
                        },
                    }
                }
            },
        },
        404: {"description": "Workflow not found - thread_id does not exist"},
        500: {"description": "Failed to retrieve workflow state - internal server error"},
        503: {"description": "Service unavailable - database connection failed"},
    },
)
async def get_workflow_state(thread_id: str):
    """
    Retrieve workflow state by thread ID.

    This endpoint allows querying the persisted state of a workflow execution.
    Useful for checking status of long-running workflows or retrieving results.

    **Path Parameters:**
    - `thread_id`: Unique identifier returned from workflow trigger endpoints.
      Format: UUID string (e.g., "550e8400-e29b-41d4-a716-446655440000").

    **Output:**
    - `thread_id`: The requested thread ID (echoed back)
    - `status`: Workflow status ("completed", "in_progress", "unknown")
    - `state`: Complete workflow state dictionary containing all results

    **Error Handling:**
    - Returns 404 if workflow with given thread_id does not exist
    - Returns 500 if database query fails
    - Returns 503 if database is unavailable
    """
    logger.debug("Retrieving workflow state", extra={"thread_id": thread_id})

    try:
        async with get_checkpointer() as checkpointer:
            config = {"configurable": {"thread_id": thread_id}}

            try:
                checkpoint = await checkpointer.aget(config)
            except Exception as e:
                logger.error(
                    "Failed to retrieve checkpoint",
                    extra={
                        "thread_id": thread_id,
                        "error": str(e),
                        "error_type": type(e).__name__,
                    },
                    exc_info=True,
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to retrieve workflow state.",
                ) from e

            if not checkpoint:
                logger.warning("Workflow not found", extra={"thread_id": thread_id})
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Workflow with thread_id '{thread_id}' not found",
                )

            # Extract state from checkpoint
            channel_values = checkpoint.get("channel_values", {})

            # Derive status from state if possible
            # For struggle workflow: check if lesson_recommendation exists
            # For audit workflow: use the status field
            workflow_status = "unknown"
            if "status" in channel_values:
                workflow_status = channel_values["status"]
            elif "lesson_recommendation" in channel_values:
                workflow_status = (
                    "completed" if channel_values.get("lesson_recommendation") else "in_progress"
                )
            elif channel_values:
                workflow_status = "completed"

            logger.debug(
                "Workflow state retrieved",
                extra={
                    "thread_id": thread_id,
                    "status": workflow_status,
                },
            )

            return {"thread_id": thread_id, "status": workflow_status, "state": channel_values}

    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        logger.error(
            "Failed to get workflow state",
            extra={
                "thread_id": thread_id,
                "error": str(e),
                "error_type": type(e).__name__,
            },
            exc_info=True,
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service temporarily unavailable. Please try again later.",
        ) from e
