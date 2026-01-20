# Deployment Guide

This guide provides comprehensive deployment procedures for Aura to Kubernetes environments, including manual deployments, CI/CD automation, and production-specific procedures.

## Table of Contents

1. [Overview](#overview)
2. [Environment Configuration](#environment-configuration)
3. [Secrets Management](#secrets-management)
4. [CI/CD Deployment](#cicd-deployment)
5. [Manual Deployment](#manual-deployment)
6. [Production Deployment](#production-deployment)
7. [Observability Setup](#observability-setup)
8. [Monitoring and Metrics](#monitoring-and-metrics)
9. [Pre-Deployment Checklist](#pre-deployment-checklist)
10. [Migration Execution](#migration-execution)
11. [Health Check Verification](#health-check-verification)
12. [Post-Deployment Validation](#post-deployment-validation)
13. [Rollback Procedures](#rollback-procedures)
14. [Troubleshooting](#troubleshooting)

## Overview

Aura uses GitHub Actions for automated Docker image building and Kubernetes deployments. This guide covers both automated CI/CD workflows and manual deployment procedures.

### Kubernetes Infrastructure

The Kubernetes infrastructure is organized as follows:

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

### Prerequisites

- **kind**: Kubernetes in Docker (for local development)
- **kubectl**: Kubernetes CLI tool (>= 1.24)
- **Docker**: >= 20.10 (required for kind and building images)
- **kustomize**: Included with kubectl >= 1.14

**Installing kind:**

macOS:

```bash
brew install kind
```

Linux:

```bash
curl -Lo ./kind https://kind.sigs.k8s.io/dl/v0.20.0/kind-linux-amd64
chmod +x ./kind
sudo mv ./kind /usr/local/bin/kind
```

For production, use a managed Kubernetes service (GKE/EKS/AKS).

## Environment Configuration

Aura uses environment-based configuration to adapt behavior for different deployment contexts. Configuration is managed through environment variables, `.env` files, and Kubernetes overlays.

### Environments

- **Local Development**: `aura-dev` namespace, relaxed settings for development
- **Staging**: `aura-staging` namespace, production-like settings for testing
- **Production**: `aura-production` namespace, strict security and performance settings

### Key Configuration Differences

**Rate Limiting:**

- Local: `1000` requests/60s (generous)
- Staging: `500` requests/60s
- Production: `100` requests/60s

**Token Expiration:**

- Local: `1440` minutes (24 hours)
- Staging: `60` minutes
- Production: `30` minutes

**CSRF Protection:**

- Local: Disabled
- Staging/Production: Enabled

**Logging:**

- Local: `DEBUG` level, `text` format
- Staging/Production: `INFO` level, `json` format

**Database Pool:**

- Local: Max `10`, Min `2`
- Staging: Max `20`, Min `5`
- Production: Max `50`, Min `10`

## Secrets Management

### Options

1. **Sealed Secrets** (Recommended for GitOps) - Encrypt secrets for Git storage
2. **External Secrets Operator** - Sync from AWS Secrets Manager, Vault, etc.
3. **Cloud-Native Solutions** - AWS Secrets Manager, GCP Secret Manager, Azure Key Vault

### Required Secrets

- **Backend Secrets**: `JWT_SECRET_KEY`, `POSTGRES_DB_URI`, `REDIS_URL`
- **PostgreSQL Secrets**: `postgres-user`, `postgres-password`, `postgres-db`
- **Redis Secrets** (optional): `redis-password`, `redis-url`

### Secret Rotation

**JWT Secret Key:**

```bash
# Generate new key
openssl rand -hex 32

# Update secret
kubectl create secret generic backend-secrets \
  --from-literal=JWT_SECRET_KEY='new-key' \
  --dry-run=client -o yaml | kubectl apply -f - -n aura-production

# Restart backend
kubectl rollout restart deployment/backend -n aura-production
```

**Database Credentials:**

1. Update password in database
2. Update PostgreSQL and backend secrets
3. Restart services

## CI/CD Deployment

### Workflows

#### 1. Docker Image Building (`docker-build.yml`)

**Triggers:**

- Push to `main` or `develop` branches
- Release creation
- Manual workflow dispatch

**What it does:**

- Builds backend Docker image (production target)
- Builds web dashboard Docker image
- Pushes images to GitHub Container Registry (GHCR)
- Tags images with git SHA or release tag

**Image Tags:**

- `latest` - Always points to latest build
- `{git-sha}` - Specific commit SHA
- `{release-tag}` - Release version (e.g., `v1.0.0`)

#### 2. Development Deployment (`k8s-deploy-dev.yml`)

**Triggers:**

- Push to `develop` or `feature/**` branches
- Manual workflow dispatch

**What it does:**

- Deploys to `aura-dev` namespace
- Uses kustomize to apply dev overlay
- Waits for rollout to complete

**Prerequisites:**

- `KUBECONFIG_DEV` secret in GitHub repository

#### 3. Staging Deployment (`k8s-deploy-staging.yml`)

**Triggers:**

- Push to `main` branch
- Manual workflow dispatch

**What it does:**

- Deploys to `aura-staging` namespace
- Updates image tags in kustomization
- Waits for rollout to complete
- Runs health checks

**Prerequisites:**

- `KUBECONFIG_STAGING` secret in GitHub repository
- Staging environment configured in GitHub

#### 4. Production Deployment (`k8s-deploy-prod.yml`)

**Triggers:**

- Release publication
- Manual workflow dispatch (requires confirmation)

**What it does:**

- Deploys to `aura-production` namespace
- Updates image tags to release version
- Requires manual confirmation (type "deploy")
- Waits for rollout to complete
- Runs production health checks

**Prerequisites:**

- `KUBECONFIG_PRODUCTION` secret in GitHub repository
- Production environment configured in GitHub
- Manual approval required

### Setup

#### 1. Configure GitHub Secrets

Add the following secrets to your GitHub repository:

**Kubernetes Deployments:**

```
KUBECONFIG_DEV=<base64-encoded-kubeconfig>
KUBECONFIG_STAGING=<base64-encoded-kubeconfig>
KUBECONFIG_PRODUCTION=<base64-encoded-kubeconfig>
```

**To get kubeconfig:**

```bash
# Get kubeconfig and encode it
cat ~/.kube/config | base64
```

**Other CI/CD Secrets:**

- `GITHUB_TOKEN` - Automatically provided by GitHub Actions
- `VERCEL_TOKEN`, `VERCEL_ORG_ID`, `VERCEL_PROJECT_ID` - For Vercel deployments (web dashboard)
- `VSCE_PAT` - For VS Code Marketplace publishing (future)
- `PYPI_API_TOKEN` - For PyPI publishing (future)

**Setting up secrets via GitHub CLI:**

```bash
# Example: Set kubeconfig (base64 encoded)
cat ~/.kube/config | base64 | gh secret set KUBECONFIG_DEV

# Example: Set Vercel token
gh secret set VERCEL_TOKEN --body "xxxxx"
```

**Security Best Practices:**

1. Rotate secrets regularly
2. Use least privilege - grant only necessary permissions
3. Audit access - regularly review who has access to secrets
4. Use OIDC where possible - prefer workload identity over static tokens

#### 2. Configure GitHub Environments

1. Go to repository Settings → Environments
2. Create environments: `staging`, `production`
3. Configure protection rules:
   - **Staging**: Optional reviewers
   - **Production**: Required reviewers, deployment branches (main only)

#### 3. Configure Image Registry

Images are pushed to GitHub Container Registry (GHCR):

- Registry: `ghcr.io`
- Format: `ghcr.io/{owner}/aura-backend:{tag}`
- Format: `ghcr.io/{owner}/aura-web-dashboard:{tag}`

**Permissions:**

- Workflows automatically have `GITHUB_TOKEN` with package write permissions
- No additional setup needed for public repositories

### Deployment Flow

**Development:**

1. Push code to `develop` branch
2. Images are built and pushed to GHCR
3. Deployment workflow triggers
4. Services deployed to `aura-dev` namespace

**Staging:**

1. Merge to `main` branch
2. Images are built with `staging` tag
3. Deployment workflow triggers
4. Services deployed to `aura-staging` namespace
5. Health checks run

**Production:**

1. Create GitHub release
2. Images are built with release tag
3. Manual approval required
4. Services deployed to `aura-production` namespace
5. Health checks run
6. Monitor deployment

### Manual Deployment via Workflows

1. Go to Actions tab in GitHub
2. Select workflow (e.g., "Deploy to Production")
3. Click "Run workflow"
4. Enter parameters:
   - Image tag (e.g., `v1.0.0`)
   - Confirmation (for production: type "deploy")
5. Click "Run workflow"

### Image Tagging Strategy

- **Development**: `dev` or git SHA (updated on every push to develop)
- **Staging**: `staging` or git SHA (updated on merge to main)
- **Production**: Release version (e.g., `v1.0.0`) + `latest` tag (updated on release creation)

## Kubernetes Development Setup

### Quick Start (Development)

**Option 1: Automated Setup (Recommended)**

```bash
# Complete setup in one command
just k8s-dev-setup
# Or: ./k8s/scripts/dev-setup.sh
```

**Option 2: Manual Setup**

1. **Set up kind cluster:**

   ```bash
   just k8s-cluster-create
   # Or: ./k8s/scripts/setup-kind.sh
   ```

2. **Build and load images:**

   ```bash
   just k8s-build-kind
   ```

3. **Create migration ConfigMap:**

   ```bash
   ./k8s/scripts/create-migration-configmap.sh
   ```

4. **Deploy to development:**

   ```bash
   just k8s-deploy dev
   # Or: ./k8s/scripts/deploy.sh dev
   ```

5. **Port-forward services:**

   ```bash
   ./k8s/scripts/port-forward.sh dev
   ```

6. **View logs:**

   ```bash
   ./k8s/scripts/logs.sh backend dev
   ```

7. **Teardown:**
   ```bash
   just k8s-dev-clean
   # Or: ./k8s/scripts/dev-clean.sh
   ```

### Services Overview

- **Backend**: Service `backend`, Port 8000, Health Check `/health`, Namespaces: `aura-dev`, `aura-staging`, `aura-production`
- **Web Dashboard**: Service `web-dashboard`, Port 3000, Namespaces: `aura-dev`, `aura-staging`, `aura-production`
- **PostgreSQL**: Service `postgres`, Port 5432, StatefulSet with persistent storage, Backups via CronJob
- **Migrations**: Job `flyway-migrations`, Runs on deployment, ConfigMap `migration-scripts`

### Key Features

**High Availability:**

- Multiple replicas (3+ in production)
- PodDisruptionBudgets for zero-downtime deployments
- Anti-affinity rules for pod distribution across nodes
- Health checks (liveness, readiness, startup probes)
- Automatic pod replacement on failure

**Auto-Scaling:**

- Horizontal Pod Autoscaler (HPA) configured
- CPU and memory-based scaling
- Min: 3 replicas, Max: 10 replicas (production)
- Automatic scale-up/down based on load

**Security:**

- Network policies for service isolation
- RBAC with dedicated service accounts
- Pod security standards (restricted for production)
- TLS/SSL support via cert-manager

**Observability:**

- Loki for centralized log aggregation (7-day retention)
- Promtail for log collection (DaemonSet)
- Prometheus for metrics collection (15-day retention)
- Grafana for dashboards and visualization
- AlertManager for alerting with pre-configured rules

## Manual Deployment

### Prerequisites

1. **Kubernetes Cluster**: Production-ready cluster (EKS, GKE, AKS, or self-hosted) or kind for local development
2. **kubectl**: Configured to access your cluster
3. **kustomize**: For building manifests
4. **Docker Images**: Pushed to container registry (GHCR)
5. **Domain Names**: Configured DNS for your domains (production)
6. **TLS Certificates**: cert-manager installed (for automatic TLS in production)

### Step 1: Update Image Tags

For production, update image tags in kustomization:

```bash
cd k8s/overlays/production
kustomize edit set image \
  aura-backend=ghcr.io/ofircohen205/aura-backend:v1.0.0 \
  aura-web-dashboard=ghcr.io/ofircohen205/aura-web-dashboard:v1.0.0
```

### Step 2: Preview Changes

```bash
# Preview what will be deployed
kubectl kustomize k8s/overlays/production | less

# Or use kustomize directly
kustomize build k8s/overlays/production > /tmp/preview.yaml
```

### Step 3: Deploy to Kubernetes

```bash
# Apply manifests
kubectl apply -k k8s/overlays/production

# Or use the deployment script
./k8s/scripts/deploy.sh production
```

### Step 4: Wait for Rollout

```bash
# Wait for backend deployment
kubectl rollout status deployment/backend -n aura-production --timeout=15m

# Wait for web dashboard deployment
kubectl rollout status deployment/web-dashboard -n aura-production --timeout=15m

# Check pod status
kubectl get pods -n aura-production
```

## Production Deployment

### Install Prerequisites

#### Install Nginx Ingress Controller

```bash
cd k8s/scripts
./setup-ingress.sh
```

#### Install cert-manager

```bash
./setup-cert-manager.sh
```

#### Configure cert-manager ClusterIssuer

1. Edit `k8s/overlays/production/cert-manager-issuer.yaml`
2. Update the email address
3. Apply:
   ```bash
   kubectl apply -f k8s/overlays/production/cert-manager-issuer.yaml
   ```

### Create Secrets

**Never commit secrets to Git!**

```bash
# Create backend secrets
kubectl create secret generic backend-secrets \
  --from-literal=postgres-db-uri='postgresql://user:password@postgres:5432/aura' \
  -n aura-production

# Create postgres secrets
kubectl create secret generic postgres-secrets \
  --from-literal=postgres-user='aura' \
  --from-literal=postgres-password='your-secure-password' \
  --from-literal=postgres-db='aura' \
  -n aura-production
```

**For GitOps workflows**, use Sealed Secrets (see [Secrets Management](#secrets-management) section above).

### Update Configuration

#### Update Domain Names

Edit `k8s/overlays/production/ingress.yaml`:

```yaml
spec:
  rules:
    - host: api.yourdomain.com # Change this
    - host: app.yourdomain.com # Change this
```

Edit `k8s/overlays/production/kustomization.yaml`:

```yaml
configMapGenerator:
  - name: web-dashboard-config
    literals:
      - NEXT_PUBLIC_API_URL=https://api.yourdomain.com # Change this
```

#### Update Image Tags

Edit `k8s/overlays/production/kustomization.yaml`:

```yaml
images:
  - name: aura-backend
    newName: ghcr.io/your-org/aura-backend
    newTag: v1.0.0 # Use specific version tags
```

### Build and Push Images

```bash
# Build production images
just k8s-build-prod

# Push to registry
just k8s-push-images
```

### Configure DNS

1. Get the external IP of your ingress controller:

   ```bash
   kubectl get svc -n ingress-nginx ingress-nginx-controller
   ```

2. Create DNS A records:
   - `api.yourdomain.com` → Ingress IP
   - `app.yourdomain.com` → Ingress IP

3. Wait for DNS propagation (can take a few minutes)

4. Verify TLS certificates:
   ```bash
   kubectl get certificate -n aura-production
   kubectl describe certificate aura-tls -n aura-production
   ```

### Scaling

#### Manual Scaling

```bash
kubectl scale deployment backend -n aura-production --replicas=5
```

#### Auto-Scaling

HPA is already configured. It will automatically scale based on CPU/memory usage.

View HPA status:

```bash
kubectl get hpa -n aura-production
kubectl describe hpa backend-hpa -n aura-production
```

### Backup and Recovery

#### Database Backups

Backup CronJob is configured in `k8s/overlays/production/postgres-backup.yaml`.

To run a manual backup:

```bash
kubectl create job --from=cronjob/postgres-backup manual-backup-$(date +%s) -n aura-production
```

#### Restore from Backup

```bash
# Copy backup to postgres pod
kubectl cp backup.sql.gz aura-production/postgres-0:/tmp/

# Restore
kubectl exec -it -n aura-production postgres-0 -- \
  gunzip -c /tmp/backup.sql.gz | psql -U aura -d aura
```

### Production Considerations

**High Availability:**

- Multiple replicas (3+) for backend and web dashboard
- PodDisruptionBudgets ensure availability during updates
- Anti-affinity rules spread pods across nodes

**Performance:**

- HPA automatically scales based on load
- Resource requests/limits prevent resource contention
- Health checks ensure only healthy pods receive traffic

**Reliability:**

- Liveness probes restart unhealthy pods
- Readiness probes prevent traffic to starting pods
- Startup probes give apps time to initialize

**Security:**

- Network Policies: Already configured to isolate services
- RBAC: Service accounts with minimal permissions
- Pod Security: Restricted security standards enforced
- Secrets: Never commit to Git, use sealed secrets or external secrets
- TLS: All traffic encrypted via cert-manager
- Resource Limits: Configured to prevent resource exhaustion

## Pre-Deployment Checklist

### Infrastructure Readiness

- [ ] Kubernetes cluster is running and accessible
- [ ] `kubectl` is configured and can access the cluster
- [ ] Target namespace exists (or will be created during deployment)
- [ ] Resource quotas are appropriate for the deployment
- [ ] Network policies are configured (if required)
- [ ] Ingress controller is installed (for production/staging)
- [ ] cert-manager is installed (for TLS certificates in production)

### Image and Registry

- [ ] Docker images are built and tested
- [ ] Images are pushed to container registry (GHCR)
- [ ] Image tags are correct and match deployment version
- [ ] Image digests are verified (for production)
- [ ] Image scanning completed (no critical vulnerabilities)

### Configuration

- [ ] Environment-specific configuration files are updated
- [ ] ConfigMaps are created or will be created during deployment
- [ ] Secrets are created (never commit secrets to Git)
- [ ] Database connection strings are correct
- [ ] Redis connection strings are correct
- [ ] JWT secret keys are set (for authentication)
- [ ] CORS origins are configured correctly
- [ ] API URLs are correct for the environment

### Database

- [ ] Database is accessible from Kubernetes cluster
- [ ] Database credentials are correct
- [ ] Migration files are up to date
- [ ] Migration ConfigMap is created (for Flyway migrations)
- [ ] Database backup is taken (for production)

### Monitoring and Observability

- [ ] Monitoring stack is deployed (Loki, Prometheus, Grafana)
- [ ] Alert rules are configured
- [ ] Log aggregation is working
- [ ] Metrics collection is enabled

### Security

- [ ] Secrets are stored securely (Kubernetes Secrets or external secret manager)
- [ ] RBAC is configured correctly
- [ ] Network policies are applied (if required)
- [ ] Pod security standards are enforced
- [ ] TLS certificates are configured (for production)

## Migration Execution

### Migration Files

Migration files are located in `deployment/migration/` and follow the naming pattern: `V{version}__{description}.sql`

- Version numbers are sequential integers
- Descriptions are snake_case
- Rollback scripts: `V{version}__{description}_ROLLBACK.sql`

### 1. Pre-Migration Validation

Before running migrations:

```bash
# Verify database connectivity
kubectl exec -it -n aura-production deployment/backend -- psql $POSTGRES_DB_URI -c "SELECT 1"

# Check current database schema version
kubectl exec -it -n aura-production deployment/backend -- psql $POSTGRES_DB_URI -c "SELECT version FROM schema_migrations ORDER BY version DESC LIMIT 1"
```

### 2. Create Migration ConfigMap

```bash
# Create ConfigMap with migration files
./k8s/scripts/create-migration-configmap.sh

# Verify ConfigMap exists
kubectl get configmap migration-scripts -n aura-production
```

**Note**: After adding new migration files, recreate the ConfigMap:

```bash
./k8s/scripts/create-migration-configmap.sh
kubectl delete job flyway-migrations -n aura-dev
kubectl apply -k k8s/overlays/dev
```

### 3. Run Migrations

Migrations run automatically via an init container or Job:

**Automatic (via init container):**

- Migrations run before the main application starts
- If migrations fail, the pod will not start
- Check migration logs: `kubectl logs -n aura-production -l app=migrations`

**Manual (via Job):**

```bash
# Apply migration job
kubectl apply -f k8s/base/migrations/job.yaml

# Wait for completion
kubectl wait --for=condition=complete --timeout=300s job/flyway-migrations -n aura-production

# Check migration logs
kubectl logs -n aura-production job/flyway-migrations
```

**Using Flyway directly:**

```bash
flyway migrate
```

**Manual execution:**

```bash
psql -U aura -d aura_db -f deployment/migration/V3__create_users_tables.sql
```

### 4. Verify Migration Success

```bash
# Check migration job status
kubectl get jobs -n aura-production

# Verify schema version
kubectl exec -it -n aura-production deployment/backend -- psql $POSTGRES_DB_URI -c "SELECT version FROM schema_migrations ORDER BY version DESC LIMIT 1"

# Check for any migration errors
kubectl logs -n aura-production job/flyway-migrations | grep -i error
```

### Migration Rollback

If migrations fail or need to be rolled back:

```bash
# Check available rollback scripts
ls deployment/migration/*ROLLBACK.sql

# Execute rollback manually (if needed)
kubectl exec -it -n aura-production deployment/backend -- psql $POSTGRES_DB_URI -f /path/to/rollback.sql

# Or use Flyway rollback (if configured)
kubectl exec -it -n aura-production deployment/backend -- flyway undo
```

**WARNING**: Rollback scripts will delete data. Always backup before rolling back.

### Migration Best Practices

1. **Always test migrations** in a development environment first
2. **Backup database** before running migrations in production
3. **Review rollback scripts** to understand data loss implications
4. **Test rollback procedures** in development before production use
5. **Document breaking changes** in migration comments
6. **Use transactions** where possible for atomic migrations

### Index Strategy

- **Single column indexes**: Created for frequently queried columns (email, username)
- **Composite indexes**: Created for common query patterns (email + is_active, is_active + created_at)
- **Unique indexes**: Enforce data integrity (email, username)

### Creating New Migrations

When creating new migrations:

1. Increment version number
2. Include rollback script
3. Document any breaking changes
4. Test in development first
5. Update migration documentation

## Health Check Verification

### Automated Health Checks

Health checks run automatically in CI/CD pipelines:

```bash
# Run health check script
./k8s/scripts/health-check.sh production aura-production 60 10
```

### Manual Health Check Verification

#### 1. Backend Health

```bash
# Port-forward to backend
kubectl port-forward -n aura-production svc/backend 8000:8000 &

# Check main health endpoint
curl http://localhost:8000/health

# Check Redis health
curl http://localhost:8000/health/redis

# Check cache health
curl http://localhost:8000/health/cache

# Stop port-forward
kill %1
```

Expected responses:

**Main Health (`/health`):**

```json
{
  "status": "ok",
  "database": "connected"
}
```

**Redis Health (`/health/redis`):**

```json
{
  "status": "ok",
  "redis": {
    "auth_db": {
      "database": 2,
      "connected": true
    },
    "rate_limit_db": {
      "database": 1,
      "connected": true
    }
  }
}
```

#### 2. Web Dashboard Health

```bash
# Port-forward to web dashboard
kubectl port-forward -n aura-production svc/web-dashboard 3000:3000 &

# Check dashboard
curl http://localhost:3000/

# Stop port-forward
kill %1
```

#### 3. Database Connectivity

```bash
# Check database connection from backend pod
kubectl exec -it -n aura-production deployment/backend -- python -c "
from db.database import async_engine
from sqlalchemy import text
import asyncio

async def test():
    async with async_engine.connect() as conn:
        result = await conn.execute(text('SELECT 1'))
        print('Database connected:', result.scalar())

asyncio.run(test())
"
```

#### 4. Redis Connectivity

```bash
# Check Redis connection from backend pod
kubectl exec -it -n aura-production deployment/backend -- python -c "
from services.redis import test_redis_connection, REDIS_AUTH_DB, REDIS_RATE_LIMIT_DB
import asyncio

async def test():
    auth_ok = await test_redis_connection(REDIS_AUTH_DB)
    rate_ok = await test_redis_connection(REDIS_RATE_LIMIT_DB)
    print(f'Redis Auth DB: {auth_ok}')
    print(f'Redis Rate Limit DB: {rate_ok}')

asyncio.run(test())
"
```

## Web Dashboard Verification

### Local Development Verification

**Prerequisites:**

- Node.js 20+ installed
- npm installed
- Backend API running on http://localhost:8000

**Steps:**

1. Install dependencies: `cd apps/web-dashboard && npm install`
2. Set environment variables: `echo "NEXT_PUBLIC_API_URL=http://localhost:8000" > .env.local`
3. Start development server: `npm run dev`
4. Verify:
   - ✅ Frontend accessible at http://localhost:3000
   - ✅ No console errors
   - ✅ Can navigate to /auth/login
   - ✅ Can navigate to /auth/register
   - ✅ Protected routes redirect to login when not authenticated
   - ✅ Hot reload works when editing files

### Docker Deployment Verification

**Development Docker:**

```bash
docker build -f apps/web-dashboard/Dockerfile.dev -t aura-web-dashboard:dev .
docker run -p 3000:3000 -e NEXT_PUBLIC_API_URL=http://localhost:8000 \
  -v $(pwd)/apps/web-dashboard:/app aura-web-dashboard:dev
```

**Production Docker:**

```bash
docker build -f apps/web-dashboard/Dockerfile.prod -t aura-web-dashboard:prod .
docker run -p 3000:3000 -e NODE_ENV=production \
  -e NEXT_PUBLIC_API_URL=http://backend:8000 aura-web-dashboard:prod
```

**Verify:**

- ✅ Container starts without errors
- ✅ Application accessible at http://localhost:3000
- ✅ Production optimizations applied (standalone output)
- ✅ No source maps in production build

### Kubernetes Deployment Verification

**Development:**

```bash
# Check pod status
kubectl get pods -l app=web-dashboard

# Check service
kubectl get svc web-dashboard

# Port forward to access locally
kubectl port-forward svc/web-dashboard 3000:3000
```

**Production:**

- ✅ All replicas are running
- ✅ Ingress is configured correctly
- ✅ TLS certificates are valid
- ✅ Application accessible via production URL
- ✅ Health checks pass
- ✅ Resource limits are appropriate

### Health Checks

**Application Health:**

```bash
curl http://localhost:3000
# ✅ Returns 200 OK
# ✅ HTML content is returned
```

**Kubernetes Health Checks:**

- Liveness probe: Initial delay 30s, Period 10s
- Readiness probe: Initial delay 10s, Period 5s

### Common Issues

**Cannot connect to backend API:**

- Verify `NEXT_PUBLIC_API_URL` is set correctly
- Check CORS configuration on backend
- Verify network connectivity between services

**Hot reload not working:**

- Check volume mounts in docker-compose
- Verify file watching is enabled
- Check for file system permission issues

**Build fails:**

- Verify all dependencies are installed
- Check Node.js version (requires 20+)
- Clear .next directory and rebuild

## Post-Deployment Validation

### 1. Service Availability

```bash
# Check all services are running
kubectl get svc -n aura-production

# Check ingress is configured
kubectl get ingress -n aura-production

# Test ingress endpoints (if configured)
curl https://api.yourdomain.com/health
curl https://app.yourdomain.com/
```

### 2. Pod Status

```bash
# Check all pods are running
kubectl get pods -n aura-production

# Check pod readiness
kubectl get pods -n aura-production -o wide

# Check for any CrashLoopBackOff or Error states
kubectl get pods -n aura-production | grep -E "Error|CrashLoopBackOff"
```

### 3. Resource Usage

```bash
# Check resource usage
kubectl top pods -n aura-production

# Check HPA status (if enabled)
kubectl get hpa -n aura-production
```

### 4. Logs Verification

```bash
# Check backend logs for errors
kubectl logs -n aura-production -l app=backend --tail=100 | grep -i error

# Check web dashboard logs
kubectl logs -n aura-production -l app=web-dashboard --tail=100

# Check migration logs
kubectl logs -n aura-production -l app=migrations --tail=100
```

### 5. Functional Testing

```bash
# Test API endpoints
curl -X POST https://api.yourdomain.com/api/v1/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123","username":"testuser"}'

# Test authentication
curl -X POST https://api.yourdomain.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'
```

### 6. Monitoring Verification

```bash
# Check Prometheus targets
kubectl port-forward -n monitoring svc/prometheus 9090:9090
# Open http://localhost:9090/targets

# Check Grafana dashboards
kubectl port-forward -n monitoring svc/grafana 3000:3000
# Open http://localhost:3000

# Check Loki logs
kubectl port-forward -n monitoring svc/loki 3100:3100
```

## Rollback Procedures

### Quick Rollback

```bash
# Use rollback script
./k8s/scripts/rollback.sh production backend

# Or use kubectl directly
kubectl rollout undo deployment/backend -n aura-production
kubectl rollout status deployment/backend -n aura-production
```

### Rollback to Specific Revision

```bash
# View rollout history
kubectl rollout history deployment/backend -n aura-production

# Rollback to specific revision
kubectl rollout undo deployment/backend -n aura-production --to-revision=2

# Verify rollback
kubectl rollout status deployment/backend -n aura-production
```

### Database Rollback

If database migrations need to be rolled back:

```bash
# 1. Stop the application (prevent new connections)
kubectl scale deployment backend --replicas=0 -n aura-production

# 2. Execute rollback migration
kubectl exec -it -n aura-production deployment/backend -- \
  psql $POSTGRES_DB_URI -f /path/to/rollback.sql

# 3. Restart application
kubectl scale deployment backend --replicas=3 -n aura-production
```

### Complete Environment Rollback

```bash
# Rollback all deployments
kubectl rollout undo deployment/backend -n aura-production
kubectl rollout undo deployment/web-dashboard -n aura-production

# Wait for rollouts
kubectl rollout status deployment/backend -n aura-production
kubectl rollout status deployment/web-dashboard -n aura-production

# Verify health after rollback
./k8s/scripts/health-check.sh production aura-production
```

## Troubleshooting

### Deployment Fails

1. **Check pod status:**

   ```bash
   kubectl get pods -n aura-production
   kubectl describe pod <pod-name> -n aura-production
   ```

2. **Check events:**

   ```bash
   kubectl get events -n aura-production --sort-by='.lastTimestamp'
   ```

3. **Check logs:**
   ```bash
   kubectl logs -n aura-production <pod-name>
   ```

### Health Checks Fail

1. **Check service endpoints:**

   ```bash
   kubectl get endpoints -n aura-production
   ```

2. **Check service connectivity:**

   ```bash
   kubectl exec -it -n aura-production deployment/backend -- curl http://localhost:8000/health
   ```

3. **Check database connectivity:**
   ```bash
   kubectl exec -it -n aura-production deployment/backend -- env | grep POSTGRES
   ```

### Migration Issues

1. **Check migration job:**

   ```bash
   kubectl get jobs -n aura-production
   kubectl logs -n aura-production job/flyway-migrations
   ```

2. **Verify ConfigMap:**
   ```bash
   kubectl get configmap migration-scripts -n aura-production -o yaml
   ```

### Images Not Found

```bash
# Verify images exist in GHCR
# Check image pull secrets
kubectl get secrets -n aura-production

# Check image pull policy
kubectl get deployment backend -n aura-production -o yaml | grep imagePullPolicy
```

### Rollout Stuck

```bash
# Check rollout status
kubectl rollout status deployment/backend -n aura-production

# Check replica sets
kubectl get rs -n aura-production

# Check pod events
kubectl describe pod <pod-name> -n aura-production
```

### Pods Not Starting

```bash
# Describe pod
kubectl describe pod <pod-name> -n aura-production

# Check events
kubectl get events -n aura-production --sort-by='.lastTimestamp'
```

### Ingress Not Working

```bash
# Check ingress
kubectl describe ingress aura-ingress -n aura-production

# Check ingress controller logs
kubectl logs -n ingress-nginx deployment/ingress-nginx-controller
```

### TLS Certificate Issues

```bash
# Check certificate status
kubectl describe certificate aura-tls -n aura-production

# Check cert-manager logs
kubectl logs -n cert-manager deployment/cert-manager
```

### Database Connection Issues

```bash
# Check postgres pod
kubectl logs -n aura-production statefulset/postgres

# Test connection
kubectl exec -it -n aura-production statefulset/postgres -- psql -U aura -d aura
```

## Best Practices

1. **Always test in staging before production**
2. **Use semantic versioning for releases**
3. **Monitor deployments in GitHub Actions**
4. **Set up notifications for deployment failures**
5. **Keep deployment history for rollback**
6. **Use feature flags for gradual rollouts**
7. **Run health checks after deployment**
8. **Monitor metrics and logs post-deployment**

## Image Building and Loading

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

## Observability Setup

### Monitoring Stack

- **Loki**: Log aggregation
- **Prometheus**: Metrics collection
- **Grafana**: Dashboards and visualization
- **AlertManager**: Alerting

### Quick Start

```bash
# Deploy monitoring stack
./k8s/scripts/setup-monitoring.sh

# Access Grafana
kubectl port-forward -n monitoring svc/grafana 3000:3000
# Open http://localhost:3000 (admin/admin)
```

### Components

**Loki**: Centralized log aggregation

- Access: `kubectl port-forward -n monitoring svc/loki 3100:3100`
- Retention: 7 days (configurable)

**Promtail**: Log collection (DaemonSet)

- Scrapes logs from all pods
- Sends to Loki

**Prometheus**: Metrics collection

- Access: `kubectl port-forward -n monitoring svc/prometheus 9090:9090`
- Auto-discovers pods with `prometheus.io/scrape=true` annotation
- Retention: 15 days

**Grafana**: Dashboards

- Pre-configured datasources: Prometheus, Loki
- Import dashboards from `k8s/monitoring/grafana/dashboards/`

## Monitoring and Metrics

### Metrics Endpoint

```bash
curl http://localhost:8000/metrics
```

### Available Metrics

**Authentication Metrics:**

- `auth_requests_total` - Total auth requests by endpoint and status
- `auth_token_refreshes_total` - Token refresh requests
- `user_registrations_total` - User registrations
- `auth_failures_total` - Auth failures by reason
- `tokens_issued_total` - Tokens issued by type
- `tokens_revoked_total` - Tokens revoked by type

**Rate Limiting Metrics:**

- `rate_limit_hits_total` - Rate limit hits
- `rate_limit_requests_total` - Total requests processed

**Redis Metrics:**

- `redis_connections_active` - Active connections
- `redis_connections_idle` - Idle connections
- `redis_connection_errors_total` - Connection errors

**Workflow Metrics:**

- `workflow_executions_total` - Workflow executions by type and status
- `workflow_duration_seconds` - Workflow execution duration
- `workflow_failures_total` - Workflow failures
- `struggle_detections_total` - Struggle detections
- `audit_executions_total` - Audit executions
- `audit_violations_detected` - Violations detected

### Grafana Dashboards

Pre-configured dashboards:

1. **Authentication Metrics** - Auth requests, tokens, rate limiting
2. **Workflow Metrics** - LangGraph workflows, struggle detection, audits

### Query Examples

**Authentication Success Rate:**

```promql
sum(rate(auth_requests_total{status="success"}[5m])) / sum(rate(auth_requests_total[5m])) * 100
```

**Workflow Execution Rate:**

```promql
sum(rate(workflow_executions_total[5m])) by (workflow_type)
```

## Related Documentation

- [Security Guide](SECURITY.md) - Security features and best practices
- [Development Guide](DEVELOPMENT.md) - Local development setup
- [Architecture Guide](ARCHITECTURE.md) - System architecture overview
