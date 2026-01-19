"""
Prometheus Metrics

Provides Prometheus metrics for authentication events, rate limiting, and system health.
"""

from prometheus_client import Counter, Gauge, Histogram

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
