# Observability Setup Guide

## Overview

The Aura monitoring stack includes:

- **Loki**: Log aggregation
- **Prometheus**: Metrics collection
- **Grafana**: Dashboards and visualization
- **AlertManager**: Alerting

## Quick Start

### Deploy Monitoring Stack

```bash
./k8s/scripts/setup-monitoring.sh
```

This deploys all monitoring components to the `monitoring` namespace.

### Access Grafana

```bash
# Port-forward Grafana
kubectl port-forward -n monitoring svc/grafana 3000:3000

# Open in browser
open http://localhost:3000
```

**Default credentials:**

- Username: `admin`
- Password: `admin` (change in `k8s/monitoring/grafana/grafana-secret.yaml`)

## Components

### Loki (Logging)

**Purpose**: Centralized log aggregation

**Access:**

```bash
kubectl port-forward -n monitoring svc/loki 3100:3100
```

**Query logs:**

- Via Grafana (recommended)
- Via Loki API: `http://localhost:3100/ready`

**Configuration:**

- Config: `k8s/monitoring/loki/loki-config.yaml`
- Retention: 7 days (configurable)

### Promtail (Log Collection)

**Purpose**: Collects logs from all pods and sends to Loki

**Deployment**: DaemonSet (runs on every node)

**Configuration:**

- Config: `k8s/monitoring/promtail/promtail-config.yaml`
- Scrapes logs from `aura-dev`, `aura-staging`, `aura-production` namespaces

### Prometheus (Metrics)

**Purpose**: Metrics collection and storage

**Access:**

```bash
kubectl port-forward -n monitoring svc/prometheus 9090:9090
```

**Query metrics:**

- Via Grafana (recommended)
- Via Prometheus UI: `http://localhost:9090`

**Scraping:**

- Automatically scrapes pods with `prometheus.io/scrape=true` annotation
- Scrapes backend and web-dashboard services
- Scrapes Kubernetes metrics

**Configuration:**

- Config: `k8s/monitoring/prometheus/prometheus-config.yaml`
- Retention: 15 days (configurable)

### Grafana (Dashboards)

**Purpose**: Visualization and dashboards

**Pre-configured datasources:**

- Prometheus (default)
- Loki

**Access:**

```bash
kubectl port-forward -n monitoring svc/grafana 3000:3000
```

**Creating Dashboards:**

1. **Application Metrics Dashboard**
   - Request rate
   - Latency (p50, p95, p99)
   - Error rate
   - Active connections

2. **Kubernetes Metrics Dashboard**
   - Pod CPU/Memory usage
   - Pod count
   - Node resources
   - HPA status

3. **Logs Dashboard**
   - Recent logs
   - Error logs
   - Log volume by service

### AlertManager (Alerting)

**Purpose**: Alert routing and notification

**Access:**

```bash
kubectl port-forward -n monitoring svc/alertmanager 9093:9093
```

**Alert Rules:**

- Defined in `k8s/monitoring/prometheus/prometheus-rules.yaml`
- Includes: Pod failures, high CPU, high memory, pod not ready

**Configure Notifications:**
Edit `k8s/monitoring/alertmanager/alertmanager-config.yaml`:

- Slack webhooks
- Email (SMTP)
- PagerDuty
- Custom webhooks

## Adding Metrics to Services

### Backend (FastAPI)

Add Prometheus metrics endpoint:

```python
from prometheus_client import make_asgi_app, Counter, Histogram

# Metrics
request_count = Counter('http_requests_total', 'Total HTTP requests', ['method', 'endpoint'])
request_latency = Histogram('http_request_duration_seconds', 'HTTP request latency')

# Add metrics app
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
```

Add annotation to deployment:

```yaml
annotations:
  prometheus.io/scrape: "true"
  prometheus.io/port: "8000"
  prometheus.io/path: "/metrics"
```

### Web Dashboard (Next.js)

Use Prometheus client library or expose metrics endpoint.

## Viewing Logs

### Via Grafana

1. Open Grafana
2. Go to "Explore"
3. Select "Loki" datasource
4. Query: `{namespace="aura-dev", app="backend"}`

### Via kubectl

```bash
# View logs
kubectl logs -n aura-dev deployment/backend

# Follow logs
kubectl logs -n aura-dev deployment/backend -f

# View logs from all pods
kubectl logs -n aura-dev --all-containers=true -f
```

### Via Loki API

```bash
# Query logs
curl -G -s "http://localhost:3100/loki/api/v1/query_range" \
  --data-urlencode 'query={namespace="aura-dev"}' \
  --data-urlencode 'limit=100' | jq
```

## Viewing Metrics

### Via Grafana

1. Open Grafana
2. Go to "Explore"
3. Select "Prometheus" datasource
4. Query: `rate(http_requests_total[5m])`

### Via Prometheus UI

```bash
kubectl port-forward -n monitoring svc/prometheus 9090:9090
# Open http://localhost:9090
```

## Alerting

### Configure Alerts

Edit `k8s/monitoring/prometheus/prometheus-rules.yaml` to add custom alerts.

### Test Alerts

```bash
# Trigger test alert
kubectl port-forward -n monitoring svc/prometheus 9090:9090
# Go to http://localhost:9090/alerts
```

### Configure Notifications

1. Edit `k8s/monitoring/alertmanager/alertmanager-config.yaml`
2. Add Slack webhook or SMTP config
3. Apply changes: `kubectl apply -f k8s/monitoring/alertmanager/alertmanager-config.yaml`
4. Reload AlertManager: `kubectl exec -n monitoring deployment/alertmanager -- kill -HUP 1`

## Troubleshooting

### Loki not collecting logs

```bash
# Check Promtail pods
kubectl get pods -n monitoring -l app=promtail

# Check Promtail logs
kubectl logs -n monitoring -l app=promtail

# Verify Promtail can access logs
kubectl exec -n monitoring -l app=promtail -- ls /var/log/pods
```

### Prometheus not scraping

```bash
# Check Prometheus targets
kubectl port-forward -n monitoring svc/prometheus 9090:9090
# Go to http://localhost:9090/targets

# Check service annotations
kubectl get deployment backend -n aura-dev -o yaml | grep prometheus
```

### Grafana not showing data

1. Check datasources are configured
2. Verify Prometheus/Loki are accessible
3. Check Grafana logs: `kubectl logs -n monitoring deployment/grafana`

## Production Considerations

1. **Storage**: Use PersistentVolumes for Prometheus and Loki data
2. **High Availability**: Deploy multiple replicas
3. **Retention**: Adjust retention policies based on storage
4. **Resource Limits**: Set appropriate limits for production
5. **Security**: Change default passwords, enable authentication
6. **Backup**: Backup Prometheus and Grafana data regularly

## Next Steps

- Create custom Grafana dashboards
- Configure alert notifications (Slack, email)
- Set up log retention policies
- Configure Prometheus retention
- Add custom metrics to applications
