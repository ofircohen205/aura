# Kubernetes Infrastructure

This directory contains Kubernetes manifests for deploying Aura to Kubernetes clusters.

**Status**: ✅ **COMPLETE** - All phases implemented and ready for use!

This is the complete reference guide for the Kubernetes infrastructure migration (AURA-16).

## Structure

```
k8s/
├── base/                    # Base manifests (common to all environments)
│   ├── backend/            # Backend service manifests
│   ├── web-dashboard/      # Web dashboard manifests
│   ├── postgres/           # PostgreSQL database manifests
│   ├── migrations/         # Database migration job
│   ├── network-policies/    # Network security policies
│   ├── rbac/               # Service accounts and roles
│   └── kustomization.yaml  # Base Kustomize configuration
├── overlays/               # Environment-specific configurations
│   ├── dev/                # Development environment
│   ├── staging/            # Staging environment
│   └── production/         # Production environment
├── monitoring/             # Observability stack
│   ├── loki/               # Log aggregation
│   ├── promtail/           # Log collection
│   ├── prometheus/         # Metrics collection
│   ├── grafana/            # Dashboards
│   └── alertmanager/       # Alerting
└── scripts/                # Deployment and utility scripts
```

## Prerequisites

- **kind**: Kubernetes in Docker (for local development)
- **kubectl**: Kubernetes CLI tool (>= 1.24)
- **Docker**: >= 20.10 (required for kind and building images)
- **kustomize**: Included with kubectl >= 1.14

### Installing kind

**macOS**:

```bash
brew install kind
```

**Linux**:

```bash
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind
```

For production, use a managed Kubernetes service (GKE/EKS/AKS).

## Quick Start

### Development Environment

**Option 1: Automated Setup (Recommended)**

```bash
# Complete setup in one command
./k8s/scripts/dev-setup.sh

# Or using Justfile
just k8s-dev-setup
```

**Option 2: Manual Setup**

1. **Set up kind cluster**:

   ```bash
   # Create kind cluster
   ./k8s/scripts/setup-kind.sh

   # Or using Justfile
   just k8s-cluster-create
   ```

2. **Build and load images**:

   ```bash
   # Build images
   just k8s-build-dev

   # Load into kind
   just k8s-build-kind
   ```

3. **Create migration ConfigMap**:

   ```bash
   ./k8s/scripts/create-migration-configmap.sh
   ```

4. **Deploy to development**:

   ```bash
   ./k8s/scripts/deploy.sh dev
   # Or: just k8s-deploy dev
   ```

5. **Port-forward services**:

   ```bash
   ./k8s/scripts/port-forward.sh dev
   ```

6. **View logs**:

   ```bash
   ./k8s/scripts/logs.sh backend dev
   ```

7. **Teardown**:
   ```bash
   ./k8s/scripts/dev-clean.sh
   # Or: just k8s-dev-clean
   ```

## Key Features

### High Availability

- Multiple replicas (3+ in production)
- PodDisruptionBudgets for zero-downtime deployments
- Anti-affinity rules for pod distribution across nodes
- Health checks (liveness, readiness, startup probes)
- Automatic pod replacement on failure

### Auto-Scaling

- Horizontal Pod Autoscaler (HPA) configured
- CPU and memory-based scaling
- Min: 3 replicas, Max: 10 replicas (production)
- Automatic scale-up/down based on load
- Metrics-driven scaling decisions

### Security

- Network policies for service isolation
- RBAC with dedicated service accounts
- Pod security standards (restricted for production)
- Secrets management documentation
- TLS/SSL support via cert-manager
- Image scanning ready

### Observability

- ✅ Loki for centralized log aggregation (7-day retention)
- ✅ Promtail for log collection (DaemonSet)
- ✅ Prometheus for metrics collection (15-day retention)
- ✅ Grafana for dashboards and visualization
- ✅ AlertManager for alerting with pre-configured rules
- Structured logging (JSON in production, text in dev)
- Health check endpoints on all services

## Services

### Backend (FastAPI)

- **Service**: `backend`
- **Port**: 8000
- **Health Check**: `/health`
- **Namespace**: `aura-dev`, `aura-staging`, `aura-production`
- **Replicas**: 1 (dev), 3+ (production)
- **Auto-scaling**: Enabled in production

### Web Dashboard (Next.js)

- **Service**: `web-dashboard`
- **Port**: 3000
- **Namespace**: `aura-dev`, `aura-staging`, `aura-production`
- **Replicas**: 1 (dev), 3+ (production)
- **Auto-scaling**: Enabled in production

### PostgreSQL

- **Service**: `postgres`
- **Port**: 5432
- **Type**: StatefulSet with persistent storage
- **Namespace**: `aura-dev`, `aura-staging`, `aura-production`
- **Backups**: CronJob configured for production

### Migrations

- **Job**: `flyway-migrations`
- **Runs**: On deployment (init container pattern)
- **Namespace**: `aura-dev`, `aura-staging`, `aura-production`
- **ConfigMap**: `migration-scripts` (created by script)

## Image Building

### Building Images

```bash
# Build all images (dev and production)
just k8s-build

# Build development images only
just k8s-build-dev

# Build production images only
just k8s-build-prod

# Build with custom tag
./k8s/scripts/build-images.sh --dev --tag my-feature
```

### Loading Images into kind

```bash
# Build and load into kind
just k8s-build-kind

# Or manually
./k8s/scripts/load-images-kind.sh aura-dev dev
```

### Pushing Images to Registry

```bash
# Authenticate with GHCR
export GITHUB_TOKEN=your_token
./k8s/scripts/setup-registry-auth.sh

# Push images
just k8s-push --tag latest
```

## Configuration

### Environment Variables

Configuration is managed through:

- **ConfigMaps**: Non-sensitive configuration
- **Secrets**: Sensitive data (passwords, tokens, etc.)

### Development Overrides

Development environment includes:

- Volume mounts for hot-reload (backend and frontend)
- Lower resource limits
- Debug logging enabled
- Local development settings

### Production Overrides

Production environment includes:

- Multiple replicas for HA
- Resource limits and requests
- Production logging (JSON format)
- Security configurations
- Ingress with TLS

## Secrets Management

**⚠️ Important**: Secrets in this repository are for development only. For production:

1. Use a secrets management solution:
   - **Sealed Secrets** (encrypted secrets in Git)
   - **External Secrets Operator** (sync from external stores)
   - **Cloud-native solutions** (AWS Secrets Manager, GCP Secret Manager, etc.)

2. Never commit production secrets to Git

3. Use Kubernetes Secrets or external secret stores

## Migration Files

Migration files are located in `deployment/migration/`. The migration job uses a ConfigMap to access these files.

**Create migration ConfigMap**:

```bash
./k8s/scripts/create-migration-configmap.sh
```

This script:

- Reads migration files from `deployment/migration/`
- Creates a ConfigMap named `migration-scripts`
- Makes files available to the migration job

**Update migrations**:
After adding new migration files, recreate the ConfigMap:

```bash
./k8s/scripts/create-migration-configmap.sh
kubectl delete job flyway-migrations -n aura-dev
kubectl apply -k k8s/overlays/dev
```

## Logging with Loki

Logging is configured to use **Loki** for log aggregation. Services output logs in JSON format (production) or text format (development) that are collected by Loki.

### Viewing Logs

```bash
# Using kubectl (direct pod logs)
./k8s/scripts/logs.sh backend dev

# Using Grafana (if Loki is deployed)
# Access Grafana dashboard and query Loki datasource
```

### Log Configuration

- **Development**: Text format, DEBUG level
- **Production**: JSON format, INFO level
- **Loki Labels**: Automatically added by log collection (app, component, namespace)

## Observability & Monitoring

Complete observability stack deployed in `k8s/monitoring/`:

### Components

- **Loki**: Centralized log aggregation (7-day retention)
- **Promtail**: Log collection DaemonSet (runs on all nodes)
- **Prometheus**: Metrics collection and storage (15-day retention)
- **Grafana**: Dashboards and visualization (pre-configured datasources)
- **AlertManager**: Alert routing and notifications (pre-configured rules)

### Quick Start

```bash
# Deploy monitoring stack
just k8s-monitoring-setup
# Or: ./k8s/scripts/setup-monitoring.sh

# Access Grafana
kubectl port-forward -n monitoring svc/grafana 3000:3000
# Open http://localhost:3000
# Default credentials: admin/admin (change in production!)
```

### Accessing Services

```bash
# Grafana (Dashboards)
kubectl port-forward -n monitoring svc/grafana 3000:3000

# Prometheus (Metrics)
kubectl port-forward -n monitoring svc/prometheus 9090:9090

# Loki (Logs - via Grafana or API)
kubectl port-forward -n monitoring svc/loki 3100:3100

# AlertManager (Alerts)
kubectl port-forward -n monitoring svc/alertmanager 9093:9093
```

### Viewing Logs

**Via Grafana (Recommended):**

1. Open Grafana: http://localhost:3000
2. Go to "Explore"
3. Select "Loki" datasource
4. Query: `{namespace="aura-dev", app="backend"}`

**Via kubectl:**

```bash
./k8s/scripts/logs.sh backend dev
kubectl logs -n aura-dev -l app=backend -f
```

**Via Loki API:**

```bash
curl -G -s "http://localhost:3100/loki/api/v1/query_range" \
  --data-urlencode 'query={namespace="aura-dev"}' \
  --data-urlencode 'limit=100'
```

### Viewing Metrics

**Via Grafana (Recommended):**

1. Open Grafana: http://localhost:3000
2. Go to "Explore"
3. Select "Prometheus" datasource
4. Query: `rate(http_requests_total[5m])`

**Via Prometheus UI:**

```bash
kubectl port-forward -n monitoring svc/prometheus 9090:9090
# Open http://localhost:9090
```

### Alerting

Alert rules are pre-configured in `k8s/monitoring/prometheus/prometheus-rules.yaml`:

- Pod failures (CrashLoopBackOff)
- High CPU usage (>90%)
- High memory usage (>90%)
- Pod not ready

Configure notifications in `k8s/monitoring/alertmanager/alertmanager-config.yaml`:

- Slack webhooks
- Email (SMTP)
- Custom webhooks

For detailed setup, see [Observability Setup Guide](../docs/workflows/observability-setup.md).

## Network Policies

Network policies are configured to restrict:

- Ingress traffic to services (only allowed sources)
- Egress traffic from pods (only allowed destinations)
- Inter-service communication (web → backend → postgres)

Policies are defined in `k8s/base/network-policies/` and apply to all environments. For local development, you may want to disable them if they're too restrictive.

## Resource Management

### Development

- Minimal resources (100-500m CPU, 256-512Mi memory)
- Single replica
- No auto-scaling

### Production

- Resource requests and limits configured
- Multiple replicas (3+ for HA)
- Horizontal Pod Autoscaling (HPA) - auto-scales 3-10 replicas
- Resource quotas per namespace
- PodDisruptionBudgets for zero-downtime deployments
- Anti-affinity rules to spread pods across nodes
- Network policies for service isolation
- RBAC with dedicated service accounts
- Pod security standards (restricted mode)
- Ingress with TLS (cert-manager)
- Database backup CronJob

## Troubleshooting

### Pods not starting

**Check pod status and logs:**

```bash
# View pod status (recommended - shows detailed info)
just k8s-status                      # View all aura namespaces
just k8s-status aura-dev             # View pods in aura-dev
just k8s-status aura-dev backend     # View backend pods only

# Or use kubectl directly
kubectl describe pod <pod-name> -n aura-dev
kubectl logs <pod-name> -n aura-dev
```

**Common issues:**

1. **Backend CrashLoopBackOff**:
   - Verify `uv` is accessible at `/bin/uv`
   - Check PYTHONPATH is set: `/app/libs/core-py/src:/app/apps/backend/src`
   - Check environment variables are set correctly

2. **Postgres CrashLoopBackOff**:
   - Check volume permissions (should use UID/GID 999)
   - Verify PVC is created: `kubectl get pvc -n aura-dev`
   - Check postgres logs for permission errors

3. **Web Dashboard CrashLoopBackOff**:
   - Verify source code is copied in Dockerfile.dev
   - Check if package.json exists in the image
   - Verify working directory is `/app/apps/web-dashboard`

### Services not accessible

```bash
kubectl get svc -n aura-dev
kubectl get endpoints -n aura-dev
```

### Database connection issues

```bash
kubectl logs -l app=postgres -n aura-dev
kubectl exec -it postgres-0 -n aura-dev -- psql -U aura -d aura_db
```

### Migration failures

```bash
kubectl logs -l app=migrations -n aura-dev
kubectl describe job flyway-migrations -n aura-dev
```

**Note**: Migration ConfigMap is created by `create-migration-configmap.sh` script. If migrations fail, verify the ConfigMap exists:

```bash
kubectl get configmap migration-scripts -n aura-dev
```

### kind Cluster Port Conflicts

If you see "address already in use" errors when creating a kind cluster:

1. **Wait for old cluster to fully delete**:

   ```bash
   kind delete cluster --name aura-dev
   sleep 5
   ```

2. **Check for processes using ports**:

   ```bash
   lsof -i :6443  # Kubernetes API port
   ```

3. **Delete all kind clusters**:

   ```bash
   kind get clusters | xargs -I {} kind delete cluster --name {}
   ```

4. **Restart Docker** if needed

The setup script now includes retry logic and better port conflict handling.

## Production Deployment

For detailed production deployment instructions, see [Production Deployment Guide](../docs/workflows/production-deployment.md).

### Quick Production Setup

1. **Install Prerequisites**:

   ```bash
   ./k8s/scripts/setup-ingress.sh
   ./k8s/scripts/setup-cert-manager.sh
   ```

2. **Create Secrets**:

   ```bash
   kubectl create secret generic backend-secrets \
     --from-literal=postgres-db-uri='postgresql://...' \
     -n aura-production
   ```

3. **Update Configuration**:
   - Edit `k8s/overlays/production/ingress.yaml` with your domains
   - Update image tags in `k8s/overlays/production/kustomization.yaml`

4. **Deploy**:
   ```bash
   kubectl apply -k k8s/overlays/production
   ```

### Production Features

- ✅ High Availability (multiple replicas, PDB, anti-affinity)
- ✅ Auto-scaling (HPA based on CPU/memory)
- ✅ Ingress with TLS (Nginx + cert-manager)
- ✅ Network Policies (service isolation)
- ✅ RBAC (service accounts, roles)
- ✅ Pod Security Standards (restricted mode)
- ✅ Resource Management (quotas, limit ranges)
- ✅ Database Backups (CronJob)

## Development Workflow

### Quick Start

**Option 1: Automated Setup (Recommended)**

```bash
# Complete setup in one command
just k8s-dev-setup
```

**Option 2: Manual Setup**

```bash
# 1. Create kind cluster
just k8s-cluster-create

# 2. Build and load images
just k8s-build-kind

# 3. Create migration ConfigMap
./k8s/scripts/create-migration-configmap.sh

# 4. Deploy services
just k8s-deploy dev

# 5. Port-forward services
./k8s/scripts/port-forward.sh dev
```

### Building Images

```bash
# Build all images (dev and production)
just k8s-build

# Build development images only
just k8s-build-dev

# Build production images only
just k8s-build-prod

# Build with specific tag
./k8s/scripts/build-images.sh --dev --tag my-feature
```

### Loading Images into kind

```bash
# Load images into kind cluster
just k8s-build-kind

# Or manually
./k8s/scripts/load-images-kind.sh aura-dev dev
```

### Deploying Services

```bash
# Deploy to development environment
just k8s-deploy dev

# Or manually
./k8s/scripts/deploy.sh dev
```

### Accessing Services

**Port-forwarding** (recommended for development):

```bash
# Port-forward all services
./k8s/scripts/port-forward.sh dev

# Or manually
kubectl port-forward -n aura-dev svc/backend 8000:8000 &
kubectl port-forward -n aura-dev svc/web-dashboard 3000:3000 &
```

**Services available at**:

- Backend API: http://localhost:8000
- Web Dashboard: http://localhost:3000
- API Docs: http://localhost:8000/docs

### Staging Environment

- Overlay configured with staging-specific settings
- Ready to deploy to staging cluster
- Network policies enabled
- Pod security standards (baseline)
- Medium-scale configuration

### Production Environment

- Production-ready manifests with HA
- Auto-scaling configured (HPA: 3-10 replicas)
- Ingress with TLS support (cert-manager)
- Security policies enforced (restricted pod security)
- Resource quotas and limits
- Database backup CronJob
- PodDisruptionBudgets for zero-downtime
- Anti-affinity rules for pod distribution

### Viewing Logs

```bash
# View logs for a service
./k8s/scripts/logs.sh backend dev
./k8s/scripts/logs.sh web-dashboard dev
./k8s/scripts/logs.sh postgres dev

# Or using kubectl
kubectl logs -n aura-dev -l app=backend -f
kubectl logs -n aura-dev -l app=web-dashboard -f
```

### Debugging

**Exec into a pod**:

```bash
# Get pod name
kubectl get pods -n aura-dev

# Exec into backend pod
kubectl exec -it -n aura-dev deployment/backend -- /bin/bash

# Exec into web dashboard pod
kubectl exec -it -n aura-dev deployment/web-dashboard -- /bin/sh
```

**Check pod status**:

```bash
# Recommended: Use the pod-status script
just k8s-status aura-dev

# Or use kubectl directly
# Get all pods
kubectl get pods -n aura-dev

# Describe a pod (for debugging)
kubectl describe pod <pod-name> -n aura-dev

# Check events
kubectl get events -n aura-dev --sort-by='.lastTimestamp'
```

### Database Migrations

Migrations run automatically on deployment via a Job:

```bash
# Check migration status
kubectl get jobs -n aura-dev
kubectl logs -n aura-dev job/flyway-migrations

# Re-run migrations (delete and redeploy)
kubectl delete job flyway-migrations -n aura-dev
kubectl apply -k k8s/overlays/dev
```

**Update migration files**:

```bash
# After adding new migration files
./k8s/scripts/create-migration-configmap.sh
kubectl delete job flyway-migrations -n aura-dev
kubectl apply -k k8s/overlays/dev
```

### Common Commands

```bash
# Complete setup
just k8s-dev-setup

# Build and deploy
just k8s-dev

# View logs
./k8s/scripts/logs.sh backend dev

# Port-forward
./k8s/scripts/port-forward.sh dev

# Check pod status
just k8s-status aura-dev

# Clean up
just k8s-dev-clean
```

## Critical Bug Fixes

All critical issues have been resolved:

- ✅ **Backend CrashLoopBackOff**: Fixed uv path (`/bin/uv`) and PYTHONPATH environment variable
- ✅ **Web Dashboard CrashLoopBackOff**: Fixed Dockerfile.dev to copy source code from monorepo root
- ✅ **Postgres CrashLoopBackOff**: Added security context (UID/GID 999) for proper volume permissions
- ✅ **Migration Job Stuck**: Removed conflicting ConfigMap from base kustomization
- ✅ **kind Setup Port Conflicts**: Added retry logic and better wait times for cluster deletion
- ✅ **Kustomize Strategic Merge**: Fixed patches to preserve all environment variables

## CI/CD Integration

Automated deployment workflows using GitHub Actions:

### Workflows

- **`docker-build.yml`**: Build and push Docker images to GHCR
- **`k8s-deploy-dev.yml`**: Automated dev deployments (on push to develop)
- **`k8s-deploy-staging.yml`**: Automated staging deployments (on push to main)
- **`k8s-deploy-prod.yml`**: Production deployments (on release, requires approval)

### Image Tagging

- **Development**: `dev` or git SHA
- **Staging**: `staging` or git SHA
- **Production**: Release version (e.g., `v1.0.0`) or `latest`

### Rollback

```bash
# Rollback a deployment
just k8s-rollback production backend

# Or manually
./k8s/scripts/rollback.sh production backend
kubectl rollout undo deployment/backend -n aura-production
```

For detailed CI/CD setup, see [CI/CD Deployment Guide](../docs/workflows/cicd-deployment.md).

## Implementation Status

**All Phases Complete!** ✅

### ✅ Phase 1: Foundation & Base Manifests - COMPLETE

- Base Kubernetes manifests for all services
- Kustomize structure with base + overlays
- Environment separation (dev, staging, production)
- Health checks and resource management

### ✅ Phase 2: Docker-K8s Integration & Development Environment - COMPLETE

- Docker image build system
- kind cluster setup for local development
- Development workflow automation
- Migration job with ConfigMap support

### ✅ Phase 3: Production Configuration - COMPLETE

- High Availability (PodDisruptionBudgets, anti-affinity)
- Auto-scaling (HPA for backend and web dashboard)
- Ingress & TLS (Nginx Ingress, cert-manager)
- Network Policies (service isolation)
- RBAC (service accounts, roles, permissions)
- Pod Security Standards (restricted for production)
- Resource Management (quotas, limit ranges)
- Database backup strategy

### ✅ Phase 4: Observability - COMPLETE

- Loki for centralized log aggregation
- Promtail for log collection (DaemonSet)
- Prometheus for metrics collection
- Grafana for dashboards and visualization
- AlertManager for alerting
- Pre-configured alert rules
- Grafana datasources configured

### ✅ Phase 5: CI/CD Integration - COMPLETE

- GitHub Actions workflow for Docker image building
- Automated deployment workflows (dev, staging, production)
- Environment promotion (dev → staging → prod)
- Rollback scripts and procedures
- Image tagging strategy (SHA, version tags)
- Manual approval gates for production

### ✅ Critical Bug Fixes - COMPLETE

- Backend: Fixed uv path and PYTHONPATH environment variable
- Web Dashboard: Fixed Dockerfile to copy source code
- Postgres: Added security context for volume permissions
- Migrations: Resolved ConfigMap conflicts
- kind Setup: Improved port conflict handling
- Kustomize: Fixed strategic merge patches for env vars

**Ready for:**

- ✅ Local development with kind
- ✅ Staging deployments
- ✅ Production deployments with HA, scaling, and security
- ✅ Complete observability (logs, metrics, dashboards, alerts)
- ✅ Automated CI/CD workflows
- ✅ Comprehensive documentation

## References

- [Kubernetes Documentation](https://kubernetes.io/docs/)
- [Kustomize Documentation](https://kustomize.io/)
- [kind Documentation](https://kind.sigs.k8s.io/)
- [Loki Documentation](https://grafana.com/docs/loki/latest/)

## Next Steps (Optional - Future Enhancements)

### Tracing (Optional)

- Deploy Tempo or Jaeger for distributed tracing
- Instrument applications for tracing
- Create tracing dashboards

### GitOps (Optional)

- Argo CD or Flux setup
- GitOps workflow configuration
- Automated sync from Git

### Advanced Features

- Canary deployments
- Blue-green deployments
- Custom Grafana dashboards
- Cost optimization strategies

## Related Documentation

- [Observability Setup Guide](../docs/workflows/observability-setup.md) - Monitoring stack setup
- [CI/CD Deployment Guide](../docs/workflows/cicd-deployment.md) - Automated deployment workflows
- [Production Deployment Guide](../docs/workflows/production-deployment.md) - Production deployment instructions
- [Production Secrets Guide](../docs/workflows/production-secrets.md) - Secrets management

---

## Migration Complete! 🎉

The Kubernetes migration is **complete and production-ready**. All phases (1-5) are implemented:

- ✅ Phase 1: Foundation & Base Manifests
- ✅ Phase 2: Docker-K8s Integration & Development Environment
- ✅ Phase 3: Production Configuration (HA, Scaling, Security)
- ✅ Phase 4: Observability (Loki, Prometheus, Grafana, AlertManager)
- ✅ Phase 5: CI/CD Integration (GitHub Actions workflows)

The infrastructure supports:

- ✅ Local development with kind
- ✅ Staging deployments
- ✅ Production deployments with HA, scaling, and security
- ✅ Complete observability (logs, metrics, dashboards, alerts)
- ✅ Automated CI/CD workflows
- ✅ Comprehensive documentation

**Ready to deploy!**
