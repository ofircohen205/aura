"""
Workflow Service

Business logic for workflow orchestration and state management.
Extracts workflow execution logic from API endpoints.
"""

import uuid
from typing import Any

from core_py.workflows.audit import build_audit_graph
from core_py.workflows.checkpointer import get_checkpointer
from core_py.workflows.struggle import build_struggle_graph
from loguru import logger

from services.workflows.exceptions import (
    WorkflowExecutionError,
    WorkflowNotFoundError,
    WorkflowServiceUnavailableError,
)


class WorkflowService:
    """Service for managing workflow execution and state."""

    async def trigger_struggle_workflow(
        self,
        edit_frequency: float,
        error_logs: list[str],
        history: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Trigger the struggle detection workflow.

        Args:
            edit_frequency: Edit frequency per time unit
            error_logs: List of error messages
            history: Previous attempt history

        Returns:
            Dictionary with thread_id, status, and final state

        Raises:
            WorkflowExecutionError: If workflow execution fails
            WorkflowServiceUnavailableError: If service is unavailable
        """
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}

        logger.info(
            "Struggle workflow triggered",
            extra={
                "thread_id": thread_id,
                "edit_frequency": edit_frequency,
                "error_count": len(error_logs),
            },
        )

        try:
            async with get_checkpointer() as checkpointer:
                graph = build_struggle_graph(checkpointer=checkpointer)

                # Initial state
                initial_state = {
                    "edit_frequency": edit_frequency,
                    "error_logs": error_logs,
                    "history": history or [],
                    "is_struggling": False,
                    "lesson_recommendation": None,
                }

                # Run the graph
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
                    raise WorkflowExecutionError("struggle", str(e)) from e

                logger.info(
                    "Struggle workflow completed",
                    extra={
                        "thread_id": thread_id,
                        "is_struggling": final_state.get("is_struggling", False),
                        "has_recommendation": final_state.get("lesson_recommendation") is not None,
                    },
                )

                return {
                    "thread_id": thread_id,
                    "status": "completed",
                    "state": final_state,
                }

        except WorkflowExecutionError:
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
            raise WorkflowServiceUnavailableError(str(e)) from e

    async def trigger_audit_workflow(
        self,
        diff_content: str,
        violations: list[str] | None = None,
    ) -> dict[str, Any]:
        """
        Trigger the code audit workflow.

        Args:
            diff_content: Git diff content to audit
            violations: Pre-existing violations

        Returns:
            Dictionary with thread_id, status, and final state

        Raises:
            WorkflowExecutionError: If workflow execution fails
            WorkflowServiceUnavailableError: If service is unavailable
        """
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}

        logger.info(
            "Audit workflow triggered",
            extra={
                "thread_id": thread_id,
                "diff_length": len(diff_content),
                "pre_existing_violations": len(violations or []),
            },
        )

        try:
            async with get_checkpointer() as checkpointer:
                graph = build_audit_graph(checkpointer=checkpointer)

                initial_state = {
                    "diff_content": diff_content,
                    "violations": violations or [],
                    "status": "pending",
                }

                # Run the graph
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
                    raise WorkflowExecutionError("audit", str(e)) from e

                logger.info(
                    "Audit workflow completed",
                    extra={
                        "thread_id": thread_id,
                        "status": final_state.get("status", "unknown"),
                        "violation_count": len(final_state.get("violations", [])),
                    },
                )

                return {
                    "thread_id": thread_id,
                    "status": "completed",
                    "state": final_state,
                }

        except WorkflowExecutionError:
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
            raise WorkflowServiceUnavailableError(str(e)) from e

    async def get_workflow_state(self, thread_id: str) -> dict[str, Any]:
        """
        Retrieve workflow state by thread ID.

        Args:
            thread_id: Unique thread identifier

        Returns:
            Dictionary with thread_id, status, and state

        Raises:
            WorkflowNotFoundError: If workflow is not found
            WorkflowServiceUnavailableError: If service is unavailable
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
                    raise WorkflowExecutionError("get_state", str(e)) from e

                if not checkpoint:
                    logger.warning("Workflow not found", extra={"thread_id": thread_id})
                    raise WorkflowNotFoundError(thread_id)

                # Extract state from checkpoint
                channel_values = checkpoint.get("channel_values", {})

                # Derive status from state if possible
                workflow_status = "unknown"
                if "status" in channel_values:
                    workflow_status = channel_values["status"]
                elif "lesson_recommendation" in channel_values:
                    workflow_status = (
                        "completed"
                        if channel_values.get("lesson_recommendation")
                        else "in_progress"
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

                return {
                    "thread_id": thread_id,
                    "status": workflow_status,
                    "state": channel_values,
                }

        except (WorkflowNotFoundError, WorkflowExecutionError):
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
            raise WorkflowServiceUnavailableError(str(e)) from e


# Global service instance (singleton pattern)
# NOTE: This singleton pattern is acceptable for stateless services like WorkflowService.
# For production with dependency injection frameworks, consider using DI instead.
# The service is stateless and thread-safe, so singleton is safe for concurrent requests.
workflow_service = WorkflowService()
