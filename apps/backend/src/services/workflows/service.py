"""
Workflow Service

Business logic for workflow orchestration and state management.
Extracts workflow execution logic from API endpoints.
"""

import time
import uuid
from datetime import UTC, datetime
from typing import Any

from agentic_py.workflows.audit import build_audit_graph
from agentic_py.workflows.checkpointer import get_checkpointer
from agentic_py.workflows.struggle import build_struggle_graph
from loguru import logger

from core.metrics import (
    audit_executions_total,
    audit_files_processed,
    audit_violations_by_type,
    audit_violations_detected,
    lesson_recommendations_generated_total,
    metrics_helper,
    struggle_detections_total,
    struggle_workflow_edit_frequency,
    struggle_workflow_error_count,
    workflow_duration_seconds,
    workflow_executions_total,
    workflow_failures_total,
)
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
            Dictionary with thread_id, status, state, created_at, and type

        Raises:
            WorkflowExecutionError: If workflow execution fails
            WorkflowServiceUnavailableError: If service is unavailable
        """
        thread_id = str(uuid.uuid4())
        config = {"configurable": {"thread_id": thread_id}}
        created_at = datetime.now(UTC)

        logger.info(
            "Struggle workflow triggered",
            extra={
                "thread_id": thread_id,
                "edit_frequency": edit_frequency,
                "error_count": len(error_logs),
            },
        )

        metrics_helper.observe_histogram(struggle_workflow_edit_frequency, edit_frequency)
        metrics_helper.observe_histogram(struggle_workflow_error_count, len(error_logs))

        start_time = time.time()

        try:
            async with get_checkpointer() as checkpointer:
                graph = build_struggle_graph(checkpointer=checkpointer)

                initial_state = {
                    "edit_frequency": edit_frequency,
                    "error_logs": error_logs,
                    "history": history or [],
                    "is_struggling": False,
                    "lesson_recommendation": None,
                }

                try:
                    final_state = await graph.ainvoke(initial_state, config=config)
                except Exception as e:
                    duration = time.time() - start_time
                    metrics_helper.inc_counter(
                        workflow_executions_total, workflow_type="struggle", status="failure"
                    )
                    metrics_helper.observe_histogram(
                        workflow_duration_seconds, duration, workflow_type="struggle"
                    )
                    metrics_helper.inc_counter(
                        workflow_failures_total,
                        workflow_type="struggle",
                        error_type="execution_error",
                    )

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

                duration = time.time() - start_time
                is_struggling = final_state.get("is_struggling", False)
                has_recommendation = final_state.get("lesson_recommendation") is not None

                metrics_helper.inc_counter(
                    workflow_executions_total, workflow_type="struggle", status="success"
                )
                metrics_helper.observe_histogram(
                    workflow_duration_seconds, duration, workflow_type="struggle"
                )
                metrics_helper.inc_counter(
                    struggle_detections_total,
                    result="struggling" if is_struggling else "not_struggling",
                )
                if has_recommendation:
                    metrics_helper.inc_counter(lesson_recommendations_generated_total)

                logger.info(
                    "Struggle workflow completed",
                    extra={
                        "thread_id": thread_id,
                        "is_struggling": is_struggling,
                        "has_recommendation": has_recommendation,
                    },
                )

                return {
                    "thread_id": thread_id,
                    "status": "completed",
                    "state": final_state,
                    "created_at": created_at,
                    "type": "Struggle Detection",
                }

        except WorkflowExecutionError:
            raise
        except Exception as e:
            duration = time.time() - start_time
            metrics_helper.inc_counter(
                workflow_executions_total, workflow_type="struggle", status="failure"
            )
            metrics_helper.observe_histogram(
                workflow_duration_seconds, duration, workflow_type="struggle"
            )
            metrics_helper.inc_counter(
                workflow_failures_total,
                workflow_type="struggle",
                error_type="service_unavailable",
            )

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
        created_at = datetime.now(UTC)

        logger.info(
            "Audit workflow triggered",
            extra={
                "thread_id": thread_id,
                "diff_length": len(diff_content),
                "pre_existing_violations": len(violations or []),
            },
        )

        start_time = time.time()

        try:
            async with get_checkpointer() as checkpointer:
                graph = build_audit_graph(checkpointer=checkpointer)

                initial_state = {
                    "diff_content": diff_content,
                    "violations": violations or [],
                    "status": "pending",
                }

                try:
                    final_state = await graph.ainvoke(initial_state, config=config)
                except Exception as e:
                    duration = time.time() - start_time
                    metrics_helper.inc_counter(
                        workflow_executions_total, workflow_type="audit", status="failure"
                    )
                    metrics_helper.observe_histogram(
                        workflow_duration_seconds, duration, workflow_type="audit"
                    )
                    metrics_helper.inc_counter(
                        workflow_failures_total,
                        workflow_type="audit",
                        error_type="execution_error",
                    )

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

                duration = time.time() - start_time
                audit_status = final_state.get("status", "unknown")
                violation_list = final_state.get("violations", [])
                violation_count = len(violation_list)
                parsed_files = final_state.get("parsed_files", [])
                file_count = len(parsed_files)

                metrics_helper.inc_counter(
                    workflow_executions_total, workflow_type="audit", status="success"
                )
                metrics_helper.observe_histogram(
                    workflow_duration_seconds, duration, workflow_type="audit"
                )
                metrics_helper.inc_counter(audit_executions_total, status=audit_status)
                metrics_helper.observe_histogram(audit_violations_detected, violation_count)
                metrics_helper.observe_histogram(audit_files_processed, file_count)

                violation_details = final_state.get("violation_details", [])
                for violation in violation_details:
                    violation_type = violation.get("rule_name") or violation.get("type", "unknown")
                    if violation_type and violation_type != "unknown":
                        metrics_helper.inc_counter(
                            audit_violations_by_type, violation_type=violation_type
                        )

                logger.info(
                    "Audit workflow completed",
                    extra={
                        "thread_id": thread_id,
                        "status": audit_status,
                        "violation_count": violation_count,
                    },
                )

                return {
                    "thread_id": thread_id,
                    "status": "completed",
                    "state": final_state,
                    "created_at": created_at,
                    "type": "Code Audit",
                }

        except WorkflowExecutionError:
            raise
        except Exception as e:
            duration = time.time() - start_time
            metrics_helper.inc_counter(
                workflow_executions_total, workflow_type="audit", status="failure"
            )
            metrics_helper.observe_histogram(
                workflow_duration_seconds, duration, workflow_type="audit"
            )
            metrics_helper.inc_counter(
                workflow_failures_total,
                workflow_type="audit",
                error_type="service_unavailable",
            )

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
            Dictionary with thread_id, status, state, created_at, and type

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

                channel_values = checkpoint.get("channel_values", {})
                checkpoint_metadata = checkpoint.get("metadata", {})

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

                workflow_type = checkpoint_metadata.get("type")
                if not workflow_type:
                    if (
                        "edit_frequency" in channel_values
                        or "lesson_recommendation" in channel_values
                    ):
                        workflow_type = "Struggle Detection"
                    elif "diff_content" in channel_values or "violations" in channel_values:
                        workflow_type = "Code Audit"
                    else:
                        workflow_type = "Unknown"

                created_at = checkpoint_metadata.get("created_at")
                if created_at:
                    if isinstance(created_at, str):
                        try:
                            created_at = datetime.fromisoformat(created_at.replace("Z", "+00:00"))
                        except (ValueError, AttributeError):
                            logger.warning(
                                "Could not parse created_at from metadata, using checkpoint timestamp",
                                extra={"thread_id": thread_id, "created_at": created_at},
                            )
                            created_at = None
                    elif not isinstance(created_at, datetime):
                        created_at = None

                if not created_at:
                    checkpoint_ts = checkpoint.get("ts")
                    if checkpoint_ts:
                        if isinstance(checkpoint_ts, int | float):
                            created_at = datetime.fromtimestamp(checkpoint_ts, tz=UTC)
                        else:
                            created_at = datetime.now(UTC)
                            logger.warning(
                                "Checkpoint timestamp is not numeric, using current time",
                                extra={"thread_id": thread_id},
                            )
                    else:
                        created_at = datetime.now(UTC)
                        logger.warning(
                            "Could not determine workflow created_at, using current time",
                            extra={"thread_id": thread_id},
                        )

                logger.debug(
                    "Workflow state retrieved",
                    extra={
                        "thread_id": thread_id,
                        "status": workflow_status,
                        "type": workflow_type,
                    },
                )

                return {
                    "thread_id": thread_id,
                    "status": workflow_status,
                    "state": channel_values,
                    "created_at": created_at,
                    "type": workflow_type,
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


workflow_service = WorkflowService()
