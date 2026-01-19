# Monitoring and Metrics Implementation

This document describes the Prometheus metrics and Grafana dashboards implemented for Aura authentication and system monitoring.

## Overview

Aura exposes Prometheus metrics at `/metrics` endpoint for collection by Prometheus. Metrics track authentication events, rate limiting, Redis connection pool usage, and system health.

## Metrics Endpoint

The metrics endpoint is automatically mounted at `/metrics` when `prometheus-client` is installed:

```bash
# Access metrics
curl http://localhost:8000/metrics
```

## Available Metrics

### Authentication Metrics

- **`auth_requests_total`**: Total authentication requests by endpoint and status
  - Labels: `endpoint` (register, login, refresh, logout), `status` (success, failure)
  - Example: `auth_requests_total{endpoint="login", status="success"}`

- **`auth_token_refreshes_total`**: Total token refresh requests
  - Labels: `status` (success, failure)
  - Example: `auth_token_refreshes_total{status="success"}`

- **`user_registrations_total`**: Total user registrations
  - Labels: `status` (success, failure)
  - Example: `user_registrations_total{status="success"}`

- **`auth_failures_total`**: Total authentication failures by reason
  - Labels: `reason` (invalid_credentials, inactive_user, invalid_token, expired_token)
  - Example: `auth_failures_total{reason="invalid_credentials"}`

- **`tokens_issued_total`**: Total tokens issued
  - Labels: `token_type` (access, refresh)
  - Example: `tokens_issued_total{token_type="access"}`

- **`tokens_revoked_total`**: Total tokens revoked
  - Labels: `token_type` (access, refresh)
  - Example: `tokens_revoked_total{token_type="refresh"}`

### Rate Limiting Metrics

- **`rate_limit_hits_total`**: Total rate limit hits
  - Labels: `endpoint`, `client_id`
  - Example: `rate_limit_hits_total{endpoint="/api/v1/workflows", client_id="127.0.0.1"}`

- **`rate_limit_requests_total`**: Total requests processed by rate limiter
  - Labels: `endpoint`
  - Example: `rate_limit_requests_total{endpoint="/api/v1/workflows"}`

### Redis Connection Pool Metrics

- **`redis_connections_active`**: Number of active Redis connections
  - Labels: `database` (auth_db, rate_limit_db)
  - Example: `redis_connections_active{database="auth_db"}`

- **`redis_connections_idle`**: Number of idle Redis connections
  - Labels: `database` (auth_db, rate_limit_db)
  - Example: `redis_connections_idle{database="auth_db"}`

- **`redis_connection_errors_total`**: Total Redis connection errors
  - Labels: `database`, `error_type`
  - Example: `redis_connection_errors_total{database="auth_db", error_type="connection_failed"}`

### Request Metrics

- **`http_requests_total`**: Total HTTP requests
  - Labels: `method`, `endpoint`, `status_code`
  - Example: `http_requests_total{method="POST", endpoint="/api/v1/auth/login", status_code="200"}`

- **`http_request_duration_seconds`**: HTTP request duration
  - Labels: `method`, `endpoint`
  - Example: `http_request_duration_seconds{method="POST", endpoint="/api/v1/auth/login"}`

### Database Metrics

- **`database_connections_active`**: Number of active database connections
- **`database_connections_idle`**: Number of idle database connections
- **`database_query_duration_seconds`**: Database query duration
  - Labels: `operation` (select, insert, update, delete)

### LangGraph Workflow Metrics

- **`workflow_executions_total`**: Total workflow executions
  - Labels: `workflow_type` (struggle, audit), `status` (success, failure)
  - Example: `workflow_executions_total{workflow_type="struggle", status="success"}`

- **`workflow_duration_seconds`**: Workflow execution duration
  - Labels: `workflow_type` (struggle, audit)
  - Example: `workflow_duration_seconds{workflow_type="audit"}`

- **`workflow_failures_total`**: Total workflow failures
  - Labels: `workflow_type` (struggle, audit), `error_type` (execution_error, service_unavailable)
  - Example: `workflow_failures_total{workflow_type="audit", error_type="execution_error"}`

#### Struggle Detection Workflow Metrics

- **`struggle_detections_total`**: Total struggle detections
  - Labels: `result` (struggling, not_struggling)
  - Example: `struggle_detections_total{result="struggling"}`

- **`lesson_recommendations_generated_total`**: Total lesson recommendations generated
  - Example: `lesson_recommendations_generated_total`

- **`struggle_workflow_edit_frequency`**: Edit frequency values in struggle detection workflows
  - Example: `struggle_workflow_edit_frequency`

- **`struggle_workflow_error_count`**: Error count in struggle detection workflows
  - Example: `struggle_workflow_error_count`

#### Code Audit Workflow Metrics

- **`audit_executions_total`**: Total audit workflow executions
  - Labels: `status` (pass, fail, remediation_required)
  - Example: `audit_executions_total{status="pass"}`

- **`audit_violations_detected`**: Number of violations detected in audit workflows
  - Example: `audit_violations_detected`

- **`audit_violations_by_type_total`**: Total violations detected by type
  - Labels: `violation_type` (print_statement, debugger_call, long_function, hardcoded_secret, etc.)
  - Example: `audit_violations_by_type_total{violation_type="print_statement"}`

- **`audit_files_processed`**: Number of files processed in audit workflows
  - Example: `audit_files_processed`

## Prometheus Configuration

The backend deployment includes Prometheus annotations for automatic scraping:

```yaml
annotations:
  prometheus.io/scrape: "true"
  prometheus.io/port: "8000"
  prometheus.io/path: "/metrics"
```

Prometheus will automatically discover and scrape pods with these annotations.

## Grafana Dashboards

Pre-configured Grafana dashboards are available:

1. **Authentication Metrics**: `k8s/monitoring/grafana/dashboards/authentication-metrics.json`
   - Authentication requests, token operations, rate limiting, Redis connections

2. **Workflow Metrics**: `k8s/monitoring/grafana/dashboards/workflow-metrics.json`
   - LangGraph workflow executions, struggle detection, code audit results

### Authentication Dashboard Panels

1. **Authentication Requests Rate**: Shows rate of authentication requests by endpoint and status
2. **Authentication Success/Failure Rate**: Compares success vs failure rates
3. **User Registrations**: Total user registrations in the last hour
4. **Token Refreshes**: Rate of token refresh requests
5. **Authentication Failures by Reason**: Pie chart of failure reasons
6. **Rate Limit Hits**: Rate of rate limit hits by endpoint
7. **Tokens Issued**: Rate of tokens issued by type
8. **Redis Connection Pool Usage**: Active and idle connections per database

### Workflow Dashboard Panels

1. **Workflow Executions Rate**: Shows rate of workflow executions by type and status
2. **Workflow Duration**: P50, P95, P99 duration percentiles by workflow type
3. **Struggle Detections**: Total struggling users detected in the last hour
4. **Lesson Recommendations Generated**: Total lesson recommendations in the last hour
5. **Struggle Detection Results**: Pie chart of struggling vs not struggling
6. **Audit Execution Status**: Rate of audit executions by status (pass/fail/remediation_required)
7. **Audit Violations Detected**: P50, P95, P99 violation counts per audit
8. **Violations by Type**: Rate of violations detected by violation type
9. **Files Processed per Audit**: P50, P95, P99 files processed per audit
10. **Workflow Failures**: Rate of workflow failures by type and error type
11. **Struggle Workflow Input Metrics**: Edit frequency and error count distributions

### Importing Dashboards

1. Access Grafana:

   ```bash
   kubectl port-forward -n monitoring svc/grafana 3000:3000
   ```

2. Import Authentication Metrics Dashboard:
   - Go to Dashboards → Import
   - Upload `k8s/monitoring/grafana/dashboards/authentication-metrics.json`
   - Select Prometheus datasource
   - Click Import

3. Import Workflow Metrics Dashboard:
   - Go to Dashboards → Import
   - Upload `k8s/monitoring/grafana/dashboards/workflow-metrics.json`
   - Select Prometheus datasource
   - Click Import

## Query Examples

### Authentication Success Rate

```promql
sum(rate(auth_requests_total{status="success"}[5m])) / sum(rate(auth_requests_total[5m])) * 100
```

### Rate Limit Hit Rate

```promql
sum(rate(rate_limit_hits_total[5m])) by (endpoint)
```

### Token Issuance Rate

```promql
sum(rate(tokens_issued_total[5m])) by (token_type)
```

### Redis Connection Pool Utilization

```promql
redis_connections_active / (redis_connections_active + redis_connections_idle) * 100
```

### Workflow Execution Rate

```promql
sum(rate(workflow_executions_total[5m])) by (workflow_type)
```

### Workflow Success Rate

```promql
sum(rate(workflow_executions_total{status="success"}[5m])) / sum(rate(workflow_executions_total[5m])) * 100
```

### Struggle Detection Rate

```promql
sum(rate(struggle_detections_total{result="struggling"}[5m]))
```

### Audit Pass Rate

```promql
sum(rate(audit_executions_total{status="pass"}[5m])) / sum(rate(audit_executions_total[5m])) * 100
```

### Average Violations per Audit

```promql
avg(audit_violations_detected)
```

## Alerting Rules

Example alert rules for authentication metrics:

```yaml
- alert: HighAuthenticationFailureRate
  expr: rate(auth_requests_total{status="failure"}[5m]) > 0.1
  for: 5m
  annotations:
    summary: "High authentication failure rate detected"

- alert: RateLimitHitsHigh
  expr: rate(rate_limit_hits_total[5m]) > 10
  for: 5m
  annotations:
    summary: "High rate of rate limit hits detected"
```

## Implementation Details

### Metrics Collection

Metrics are collected automatically when:

- Authentication endpoints are called (register, login, refresh, logout)
- Rate limiting occurs
- Tokens are issued or revoked
- Rate limiting middleware processes requests

### Graceful Degradation

If `prometheus-client` is not installed, metrics collection is disabled gracefully:

- No errors are raised
- Application continues to function normally
- Metrics endpoints return 404

### Performance Impact

Metrics collection has minimal performance impact:

- Counters use atomic operations
- Histograms use efficient bucketing
- Metrics are collected asynchronously where possible

## Related Documentation

- [Observability Setup Guide](./observability-setup.md)
- [Production Deployment](./production-deployment.md)
- [Environment Configuration](./environment-config.md)
