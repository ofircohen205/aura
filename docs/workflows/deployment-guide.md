# Deployment Guide

This guide provides comprehensive deployment procedures, checklists, and validation steps for deploying Aura to Kubernetes environments.

## Table of Contents

1. [Pre-Deployment Checklist](#pre-deployment-checklist)
2. [Migration Execution Order](#migration-execution-order)
3. [Deployment Steps](#deployment-steps)
4. [Health Check Verification](#health-check-verification)
5. [Post-Deployment Validation](#post-deployment-validation)
6. [Rollback Procedures](#rollback-procedures)

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

## Migration Execution Order

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

## Deployment Steps

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

## Related Documentation

- [Production Deployment Guide](./production-deployment.md)
- [CI/CD Deployment Guide](./cicd-deployment.md)
- [Secrets Management](./production-secrets.md)
- [Environment Configuration](./environment-config.md)
