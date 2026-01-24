"""
Prometheus Metrics

Provides Prometheus metrics for authentication events, rate limiting, and system health.
Includes a helper class for centralized metrics tracking.
"""

from contextlib import contextmanager
from typing import Any

try:
    from prometheus_client import Counter, Gauge, Histogram

    METRICS_ENABLED = True
except ImportError:
    METRICS_ENABLED = False
    # Create dummy types for type checking when metrics are disabled
    Counter = Any  # type: ignore[assignment,misc]
    Gauge = Any  # type: ignore[assignment,misc]
    Histogram = Any  # type: ignore[assignment,misc]


def is_metrics_enabled() -> bool:
    """
    Check if metrics are enabled.

    Returns:
        True if prometheus_client is available, False otherwise
    """
    return METRICS_ENABLED


class MetricsHelper:
    """
    Helper class for tracking Prometheus metrics.

    All methods check METRICS_ENABLED internally, so callers don't need to.
    """

    def inc_counter(self, metric: Counter, **labels: str) -> None:
        """
        Increment a counter metric.

        Args:
            metric: Counter metric to increment
            **labels: Label values for the metric
        """
        if not METRICS_ENABLED:
            return

        if labels:
            metric.labels(**labels).inc()
        else:
            metric.inc()

    def observe_histogram(self, metric: Histogram, value: float, **labels: str) -> None:
        """
        Observe a value in a histogram metric.

        Args:
            metric: Histogram metric to observe
            value: Value to record
            **labels: Label values for the metric
        """
        if not METRICS_ENABLED:
            return

        if labels:
            metric.labels(**labels).observe(value)
        else:
            metric.observe(value)

    def set_gauge(self, metric: Gauge, value: float, **labels: str) -> None:
        """
        Set a gauge metric value.

        Args:
            metric: Gauge metric to set
            value: Value to set
            **labels: Label values for the metric
        """
        if not METRICS_ENABLED:
            return

        if labels:
            metric.labels(**labels).set(value)
        else:
            metric.set(value)

    @contextmanager
    def track_operation(
        self,
        success_metric: Counter | None = None,
        failure_metric: Counter | None = None,
        duration_metric: Histogram | None = None,
        success_labels: dict[str, str] | None = None,
        failure_labels: dict[str, str] | None = None,
        duration_labels: dict[str, str] | None = None,
    ):
        """
        Context manager for tracking operation success/failure and duration.

        Automatically tracks success on normal exit, failure on exception,
        and duration if duration_metric is provided.

        Args:
            success_metric: Counter to increment on success
            failure_metric: Counter to increment on failure
            duration_metric: Histogram to record duration in seconds
            success_labels: Labels for success metric
            failure_labels: Labels for failure metric
            duration_labels: Labels for duration metric

        Example:
            ```python
            with metrics_helper.track_operation(
                success_metric=auth_requests_total,
                failure_metric=auth_requests_total,
                success_labels={"endpoint": "login", "status": "success"},
                failure_labels={"endpoint": "login", "status": "failure"},
            ):
                # operation code
            ```
        """
        import time

        start_time = time.time()
        success_labels = success_labels or {}
        failure_labels = failure_labels or {}
        duration_labels = duration_labels or {}

        try:
            yield
            # Success path
            if success_metric:
                self.inc_counter(success_metric, **success_labels)
        except Exception:
            # Failure path
            if failure_metric:
                self.inc_counter(failure_metric, **failure_labels)
            raise
        finally:
            # Duration tracking
            if duration_metric:
                duration = time.time() - start_time
                self.observe_histogram(duration_metric, duration, **duration_labels)


# Singleton instance
metrics_helper = MetricsHelper()

__all__ = [
    "is_metrics_enabled",
    "metrics_helper",
    # Authentication Metrics
    "auth_requests_total",
    "auth_token_refreshes_total",
    "user_registrations_total",
    "auth_failures_total",
    # Rate Limiting Metrics
    "rate_limit_hits_total",
    "rate_limit_requests_total",
    # Redis Connection Pool Metrics
    "redis_connections_active",
    "redis_connections_idle",
    "redis_connection_errors_total",
    # Token Metrics
    "tokens_issued_total",
    "tokens_revoked_total",
    # Request Metrics
    "http_requests_total",
    "http_request_duration_seconds",
    # Database Metrics
    "database_connections_active",
    "database_connections_idle",
    "database_query_duration_seconds",
    # LangGraph Workflow Metrics
    "workflow_executions_total",
    "workflow_duration_seconds",
    "workflow_failures_total",
    # Struggle Detection Workflow Metrics
    "struggle_detections_total",
    "lesson_recommendations_generated_total",
    "struggle_workflow_edit_frequency",
    "struggle_workflow_error_count",
    # Code Audit Workflow Metrics
    "audit_executions_total",
    "audit_violations_detected",
    "audit_violations_by_type",
    "audit_files_processed",
]

# Authentication Metrics
auth_requests_total = Counter(
    "auth_requests_total",
    "Total authentication requests",
    ["endpoint", "status"],  # endpoint: register, login, refresh, logout; status: success, failure
)

auth_token_refreshes_total = Counter(
    "auth_token_refreshes_total",
    "Total token refresh requests",
    ["status"],  # status: success, failure
)

user_registrations_total = Counter(
    "user_registrations_total",
    "Total user registrations",
    ["status"],  # status: success, failure
)

auth_failures_total = Counter(
    "auth_failures_total",
    "Total authentication failures",
    ["reason"],  # reason: invalid_credentials, inactive_user, invalid_token, expired_token
)

# Rate Limiting Metrics
rate_limit_hits_total = Counter(
    "rate_limit_hits_total",
    "Total rate limit hits",
    ["endpoint", "client_id"],  # endpoint: API endpoint, client_id: client identifier
)

rate_limit_requests_total = Counter(
    "rate_limit_requests_total",
    "Total requests processed by rate limiter",
    ["endpoint"],
)

# Redis Connection Pool Metrics
redis_connections_active = Gauge(
    "redis_connections_active",
    "Number of active Redis connections",
    ["database"],  # database: auth_db, rate_limit_db
)

redis_connections_idle = Gauge(
    "redis_connections_idle",
    "Number of idle Redis connections",
    ["database"],
)

redis_connection_errors_total = Counter(
    "redis_connection_errors_total",
    "Total Redis connection errors",
    ["database", "error_type"],  # error_type: connection_failed, timeout, etc.
)

# Token Metrics
tokens_issued_total = Counter(
    "tokens_issued_total",
    "Total tokens issued",
    ["token_type"],  # token_type: access, refresh
)

tokens_revoked_total = Counter(
    "tokens_revoked_total",
    "Total tokens revoked",
    ["token_type"],
)

# Request Metrics (for general API monitoring)
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "endpoint", "status_code"],
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request duration in seconds",
    ["method", "endpoint"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

# Database Metrics
database_connections_active = Gauge(
    "database_connections_active",
    "Number of active database connections",
)

database_connections_idle = Gauge(
    "database_connections_idle",
    "Number of idle database connections",
)

database_query_duration_seconds = Histogram(
    "database_query_duration_seconds",
    "Database query duration in seconds",
    ["operation"],  # operation: select, insert, update, delete
    buckets=(0.001, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0),
)

# LangGraph Workflow Metrics
workflow_executions_total = Counter(
    "workflow_executions_total",
    "Total workflow executions",
    ["workflow_type", "status"],  # workflow_type: struggle, audit; status: success, failure
)

workflow_duration_seconds = Histogram(
    "workflow_duration_seconds",
    "Workflow execution duration in seconds",
    ["workflow_type"],  # workflow_type: struggle, audit
    buckets=(0.1, 0.5, 1.0, 2.5, 5.0, 10.0, 30.0, 60.0, 120.0, 300.0),
)

workflow_failures_total = Counter(
    "workflow_failures_total",
    "Total workflow failures",
    [
        "workflow_type",
        "error_type",
    ],  # workflow_type: struggle, audit; error_type: execution_error, service_unavailable
)

# Struggle Detection Workflow Metrics
struggle_detections_total = Counter(
    "struggle_detections_total",
    "Total struggle detections",
    ["result"],  # result: struggling, not_struggling
)

lesson_recommendations_generated_total = Counter(
    "lesson_recommendations_generated_total",
    "Total lesson recommendations generated",
)

struggle_workflow_edit_frequency = Histogram(
    "struggle_workflow_edit_frequency",
    "Edit frequency values in struggle detection workflows",
    buckets=(0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0),
)

struggle_workflow_error_count = Histogram(
    "struggle_workflow_error_count",
    "Error count in struggle detection workflows",
    buckets=(0, 1, 2, 5, 10, 20, 50, 100),
)

# Code Audit Workflow Metrics
audit_executions_total = Counter(
    "audit_executions_total",
    "Total audit workflow executions",
    ["status"],  # status: pass, fail, remediation_required
)

audit_violations_detected = Histogram(
    "audit_violations_detected",
    "Number of violations detected in audit workflows",
    buckets=(0, 1, 2, 5, 10, 20, 50, 100),
)

audit_violations_by_type = Counter(
    "audit_violations_by_type_total",
    "Total violations detected by type",
    [
        "violation_type"
    ],  # violation_type: print_statement, debugger_call, long_function, hardcoded_secret, etc.
)

audit_files_processed = Histogram(
    "audit_files_processed",
    "Number of files processed in audit workflows",
    buckets=(1, 5, 10, 20, 50, 100, 200, 500),
)
