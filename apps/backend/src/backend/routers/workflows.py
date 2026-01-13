"""
Workflow API Endpoints

Provides REST API for triggering and querying LangGraph workflows.
Includes error handling, logging, and input validation.
"""
import logging
import uuid
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from typing import List, Optional, Dict, Any

from core_py.workflows.struggle import build_struggle_graph
from core_py.workflows.audit import build_audit_graph
from core_py.workflows.checkpointer import get_checkpointer

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/workflows", tags=["workflows"])

# Configuration
MAX_DIFF_CONTENT_LENGTH = 10_000_000  # 10MB limit to prevent DoS

# Data Models
class StruggleInput(BaseModel):
    """Input model for struggle detection workflow."""
    edit_frequency: float = Field(..., ge=0, description="Edit frequency per time unit")
    error_logs: List[str] = Field(default_factory=list, description="List of error messages")
    history: List[str] = Field(default_factory=list, description="Previous attempt history")

class AuditInput(BaseModel):
    """Input model for code audit workflow."""
    diff_content: str = Field(..., min_length=0, max_length=MAX_DIFF_CONTENT_LENGTH, description="Git diff content to audit")
    violations: List[str] = Field(default_factory=list, description="Pre-existing violations")
    
    @field_validator("diff_content")
    @classmethod
    def validate_diff_content(cls, v: str) -> str:
        """Validate diff content size."""
        if len(v) > MAX_DIFF_CONTENT_LENGTH:
            raise ValueError(f"Diff content exceeds maximum length of {MAX_DIFF_CONTENT_LENGTH} characters")
        return v

class WorkflowResponse(BaseModel):
    """Response model for workflow operations."""
    thread_id: str = Field(..., description="Unique thread identifier for this workflow execution")
    status: str = Field(..., description="Workflow execution status (completed, failed, etc.)")
    state: Optional[Dict[str, Any]] = Field(None, description="Final workflow state")

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
    }
)
async def trigger_struggle_workflow(inp: StruggleInput):
    """
    Trigger the struggle detection workflow.
    
    This endpoint analyzes edit frequency and error patterns to determine
    if a user is struggling and generates appropriate lesson recommendations.
    """
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    logger.info(
        "Struggle workflow triggered",
        extra={
            "thread_id": thread_id,
            "edit_frequency": inp.edit_frequency,
            "error_count": len(inp.error_logs),
        }
    )
    
    try:
        async with get_checkpointer() as checkpointer:
            graph = build_struggle_graph(checkpointer=checkpointer)
            
            # Initial state
            initial_state = {
                "edit_frequency": inp.edit_frequency,
                "error_logs": inp.error_logs,
                "history": inp.history,
                "is_struggling": False,
                "lesson_recommendation": None
            }
            
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
                    exc_info=True
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Workflow execution failed. Please try again later."
                )
            
            logger.info(
                "Struggle workflow completed",
                extra={
                    "thread_id": thread_id,
                    "is_struggling": final_state.get("is_struggling", False),
                    "has_recommendation": final_state.get("lesson_recommendation") is not None,
                }
            )
            
            return {
                "thread_id": thread_id,
                "status": "completed",
                "state": final_state
            }
            
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
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service temporarily unavailable. Please try again later."
        )

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
    }
)
async def trigger_audit_workflow(inp: AuditInput):
    """
    Trigger the code audit workflow.
    
    This endpoint analyzes code diffs for violations against coding standards
    and returns a pass/fail status with detailed violation information.
    """
    thread_id = str(uuid.uuid4())
    config = {"configurable": {"thread_id": thread_id}}
    
    logger.info(
        "Audit workflow triggered",
        extra={
            "thread_id": thread_id,
            "diff_length": len(inp.diff_content),
            "pre_existing_violations": len(inp.violations),
        }
    )
    
    try:
        async with get_checkpointer() as checkpointer:
            graph = build_audit_graph(checkpointer=checkpointer)
            
            initial_state = {
                "diff_content": inp.diff_content,
                "violations": inp.violations,
                "status": "pending"
            }
            
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
                    exc_info=True
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Workflow execution failed. Please try again later."
                )
            
            logger.info(
                "Audit workflow completed",
                extra={
                    "thread_id": thread_id,
                    "status": final_state.get("status", "unknown"),
                    "violation_count": len(final_state.get("violations", [])),
                }
            )
            
            return {
                "thread_id": thread_id,
                "status": "completed",
                "state": final_state
            }
            
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
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service temporarily unavailable. Please try again later."
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
    }
)
async def get_workflow_state(thread_id: str):
    """
    Retrieve workflow state by thread ID.
    
    This endpoint allows querying the persisted state of a workflow execution.
    Useful for checking status of long-running workflows or retrieving results.
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
                    exc_info=True
                )
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to retrieve workflow state."
                )
            
            if not checkpoint:
                logger.warning("Workflow not found", extra={"thread_id": thread_id})
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Workflow with thread_id '{thread_id}' not found"
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
                workflow_status = "completed" if channel_values.get("lesson_recommendation") else "in_progress"
            elif channel_values:
                workflow_status = "completed"
            
            logger.debug(
                "Workflow state retrieved",
                extra={
                    "thread_id": thread_id,
                    "status": workflow_status,
                }
            )
            
            return {
                "thread_id": thread_id,
                "status": workflow_status,
                "state": channel_values
            }
            
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
            exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Service temporarily unavailable. Please try again later."
        )
