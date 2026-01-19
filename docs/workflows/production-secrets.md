# Production Secrets Management

## Overview

This document describes how to manage secrets in production Kubernetes environments for Aura. It covers secret creation, rotation procedures, and best practices for JWT keys, database credentials, and Redis credentials.

## Options

### 1. Sealed Secrets (Recommended for GitOps)

**What**: Encrypt secrets so they can be safely stored in Git.

**Installation:**

```bash
kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.24.0/controller.yaml
```

**Usage:**

```bash
# Install kubeseal CLI
brew install kubeseal  # macOS
# or download from: https://github.com/bitnami-labs/sealed-secrets/releases

# Create a sealed secret
kubectl create secret generic backend-secrets \
  --from-literal=postgres-db-uri='postgresql://...' \
  --dry-run=client -o yaml | kubeseal -o yaml > sealed-secret.yaml

# Apply the sealed secret
kubectl apply -f sealed-secret.yaml
```

**Pros:**

- Secrets can be stored in Git (encrypted)
- Works well with GitOps workflows
- No external dependencies

**Cons:**

- Requires kubeseal CLI
- Secrets are encrypted but still visible in Git

### 2. External Secrets Operator

**What**: Sync secrets from external secret stores (AWS Secrets Manager, HashiCorp Vault, etc.)

**Installation:**

```bash
helm repo add external-secrets https://charts.external-secrets.io
helm install external-secrets external-secrets/external-secrets -n external-secrets --create-namespace
```

**Usage:**

```yaml
apiVersion: external-secrets.io/v1beta1
kind: ExternalSecret
metadata:
  name: backend-secrets
spec:
  secretStoreRef:
    name: aws-secrets-manager
    kind: SecretStore
  target:
    name: backend-secrets
  data:
    - secretKey: postgres-db-uri
      remoteRef:
        key: aura/production/postgres
        property: db-uri
```

**Pros:**

- Centralized secret management
- Integrates with cloud providers
- Automatic rotation support

**Cons:**

- Requires external secret store
- More complex setup

### 3. Cloud-Native Solutions

**AWS:**

- AWS Secrets Manager
- AWS Parameter Store
- Use External Secrets Operator

**GCP:**

- Secret Manager
- Use External Secrets Operator

**Azure:**

- Key Vault
- Use External Secrets Operator

## Required Secrets

Aura requires the following secrets for production deployment:

### 1. Backend Secrets (`backend-secrets`)

Contains:

- `JWT_SECRET_KEY` - Secret key for JWT token signing (minimum 32 characters)
- `POSTGRES_DB_URI` - PostgreSQL database connection string
- `REDIS_URL` - Redis connection string (optional, if different from default)

### 2. PostgreSQL Secrets (`postgres-secrets`)

Contains:

- `postgres-user` - PostgreSQL username
- `postgres-password` - PostgreSQL password
- `postgres-db` - PostgreSQL database name

### 3. Redis Secrets (`redis-secrets`) - Optional

Contains:

- `redis-password` - Redis password (if authentication is enabled)
- `redis-url` - Full Redis connection string with credentials

## Current Implementation

Currently, Aura uses Kubernetes Secrets directly. For production:

1. **Never commit secrets to Git**
2. **Use kubectl to create secrets:**

   ```bash
   # Backend secrets
   kubectl create secret generic backend-secrets \
     --from-literal=JWT_SECRET_KEY='your-secure-jwt-secret-key-minimum-32-characters-long' \
     --from-literal=POSTGRES_DB_URI='postgresql+psycopg://user:password@postgres:5432/aura_db' \
     --from-literal=REDIS_URL='redis://redis:6379/0' \
     -n aura-production

   # PostgreSQL secrets
   kubectl create secret generic postgres-secrets \
     --from-literal=postgres-user='aura' \
     --from-literal=postgres-password='your-secure-password' \
     --from-literal=postgres-db='aura_db' \
     -n aura-production

   # Redis secrets (if authentication is enabled)
   kubectl create secret generic redis-secrets \
     --from-literal=redis-password='your-redis-password' \
     --from-literal=redis-url='redis://:password@redis:6379/0' \
     -n aura-production
   ```

3. **Or use sealed secrets for GitOps workflows**

## Migration Path

1. **Development**: Continue using kubectl secrets (local only)
2. **Staging**: Use sealed secrets for GitOps
3. **Production**: Use External Secrets Operator with cloud secret store

## Best Practices

1. **Rotate secrets regularly**
2. **Use different secrets per environment**
3. **Limit access to secrets (RBAC)**
4. **Audit secret access**
5. **Never log secrets**
6. **Use secret scanning in CI/CD**

## Example: Setting Up Sealed Secrets

```bash
# 1. Install sealed-secrets controller
kubectl apply -f https://github.com/bitnami-labs/sealed-secrets/releases/download/v0.24.0/controller.yaml

# 2. Get the public key (for encryption)
kubeseal --fetch-cert > sealed-secrets-public-key.pem

# 3. Create a sealed secret
kubectl create secret generic backend-secrets \
  --from-literal=postgres-db-uri='postgresql://...' \
  --dry-run=client -o yaml | \
  kubeseal --cert=sealed-secrets-public-key.pem -o yaml > k8s/overlays/production/sealed-secret-backend.yaml

# 4. Commit the sealed secret to Git
git add k8s/overlays/production/sealed-secret-backend.yaml
git commit -m "Add sealed secret for backend"
```

## Secret Rotation Procedures

### JWT Secret Key Rotation

**Important**: Rotating JWT secret keys will invalidate all existing tokens. Plan for a maintenance window or implement gradual rotation.

#### Step 1: Generate New Secret Key

```bash
# Generate a secure random key (64 characters recommended)
openssl rand -hex 32
```

#### Step 2: Update Secret

```bash
# Update the secret with new JWT key
kubectl create secret generic backend-secrets \
  --from-literal=JWT_SECRET_KEY='new-secret-key-here' \
  --from-literal=POSTGRES_DB_URI='postgresql+psycopg://user:pass@postgres:5432/aura_db' \
  --dry-run=client -o yaml | kubectl apply -f - -n aura-production
```

#### Step 3: Restart Backend Pods

```bash
# Restart backend deployment to pick up new secret
kubectl rollout restart deployment/backend -n aura-production

# Wait for rollout
kubectl rollout status deployment/backend -n aura-production
```

#### Step 4: Verify

```bash
# Test authentication with new tokens
curl -X POST https://api.yourdomain.com/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"password"}'
```

**Note**: All users will need to log in again after JWT key rotation.

### Database Credentials Rotation

#### Step 1: Update Database Password

```bash
# Connect to database and update password
kubectl exec -it -n aura-production postgres-0 -- \
  psql -U aura -d aura_db -c "ALTER USER aura WITH PASSWORD 'new-password';"
```

#### Step 2: Update Secret

```bash
# Update PostgreSQL secret
kubectl create secret generic postgres-secrets \
  --from-literal=postgres-user='aura' \
  --from-literal=postgres-password='new-password' \
  --from-literal=postgres-db='aura_db' \
  --dry-run=client -o yaml | kubectl apply -f - -n aura-production

# Update backend secret with new connection string
kubectl create secret generic backend-secrets \
  --from-literal=JWT_SECRET_KEY='existing-jwt-key' \
  --from-literal=POSTGRES_DB_URI='postgresql+psycopg://aura:new-password@postgres:5432/aura_db' \
  --dry-run=client -o yaml | kubectl apply -f - -n aura-production
```

#### Step 3: Restart Services

```bash
# Restart backend to pick up new database credentials
kubectl rollout restart deployment/backend -n aura-production

# Restart PostgreSQL StatefulSet (if needed)
kubectl rollout restart statefulset/postgres -n aura-production

# Wait for rollouts
kubectl rollout status deployment/backend -n aura-production
kubectl rollout status statefulset/postgres -n aura-production
```

#### Step 4: Verify

```bash
# Check database connectivity
kubectl exec -it -n aura-production deployment/backend -- \
  python -c "from db.database import async_engine; from sqlalchemy import text; import asyncio; asyncio.run(async_engine.connect().__aenter__().execute(text('SELECT 1')))"
```

### Redis Credentials Rotation

#### Step 1: Update Redis Password

```bash
# If using Redis with authentication, update password in Redis
kubectl exec -it -n aura-production redis-0 -- \
  redis-cli CONFIG SET requirepass "new-redis-password"
```

#### Step 2: Update Secret

```bash
# Update Redis secret
kubectl create secret generic redis-secrets \
  --from-literal=redis-password='new-redis-password' \
  --from-literal=redis-url='redis://:new-redis-password@redis:6379/0' \
  --dry-run=client -o yaml | kubectl apply -f - -n aura-production

# Update backend secret with new Redis URL
kubectl create secret generic backend-secrets \
  --from-literal=JWT_SECRET_KEY='existing-jwt-key' \
  --from-literal=POSTGRES_DB_URI='existing-db-uri' \
  --from-literal=REDIS_URL='redis://:new-redis-password@redis:6379/0' \
  --dry-run=client -o yaml | kubectl apply -f - -n aura-production
```

#### Step 3: Restart Backend

```bash
# Restart backend to pick up new Redis credentials
kubectl rollout restart deployment/backend -n aura-production
kubectl rollout status deployment/backend -n aura-production
```

#### Step 4: Verify

```bash
# Check Redis connectivity
curl http://localhost:8000/health/redis
# Or via port-forward
kubectl port-forward -n aura-production svc/backend 8000:8000
curl http://localhost:8000/health/redis
```

## Secret Rotation Schedule

Recommended rotation schedule:

- **JWT Secret Key**: Every 90 days (or after security incidents)
- **Database Password**: Every 180 days
- **Redis Password**: Every 180 days (if authentication is enabled)

## Secret Management Best Practices

1. **Generate Strong Secrets**:

   ```bash
   # JWT Secret (64 characters)
   openssl rand -hex 32

   # Database Password (32 characters)
   openssl rand -base64 24

   # Redis Password (32 characters)
   openssl rand -base64 24
   ```

2. **Use Different Secrets Per Environment**:
   - Never reuse production secrets in staging or development
   - Use environment-specific secret namespaces

3. **Limit Secret Access (RBAC)**:

   ```yaml
   # Example RBAC to limit secret access
   apiVersion: rbac.authorization.k8s.io/v1
   kind: Role
   metadata:
     name: secret-reader
     namespace: aura-production
   rules:
     - apiGroups: [""]
       resources: ["secrets"]
       resourceNames: ["backend-secrets"]
       verbs: ["get", "list"]
   ```

4. **Audit Secret Access**:

   ```bash
   # Enable audit logging for secret access
   # Check Kubernetes audit logs for secret access events
   kubectl get events -n aura-production --field-selector involvedObject.kind=Secret
   ```

5. **Never Log Secrets**:
   - Ensure application code never logs secret values
   - Use environment variables, not hardcoded values
   - Mask secrets in CI/CD logs

6. **Use Secret Scanning in CI/CD**:
   - Enable GitHub secret scanning
   - Use tools like `git-secrets` or `truffleHog` to scan commits

## Security Considerations

- Secrets are base64 encoded (not encrypted) in Kubernetes by default
- Enable encryption at rest for etcd (Kubernetes control plane)
- Use RBAC to limit who can read secrets
- Use network policies to limit pod-to-pod communication
- Regularly rotate secrets (see rotation schedule above)
- Monitor secret access through audit logs
- Use sealed secrets or external secret managers for GitOps workflows
- Never commit secrets to Git (even if base64 encoded)

## Example: Complete Secret Setup

```bash
# 1. Generate secrets
JWT_SECRET=$(openssl rand -hex 32)
DB_PASSWORD=$(openssl rand -base64 24)
REDIS_PASSWORD=$(openssl rand -base64 24)

# 2. Create backend secret
kubectl create secret generic backend-secrets \
  --from-literal=JWT_SECRET_KEY="$JWT_SECRET" \
  --from-literal=POSTGRES_DB_URI="postgresql+psycopg://aura:${DB_PASSWORD}@postgres:5432/aura_db" \
  --from-literal=REDIS_URL="redis://:${REDIS_PASSWORD}@redis:6379/0" \
  -n aura-production

# 3. Create PostgreSQL secret
kubectl create secret generic postgres-secrets \
  --from-literal=postgres-user='aura' \
  --from-literal=postgres-password="$DB_PASSWORD" \
  --from-literal=postgres-db='aura_db' \
  -n aura-production

# 4. Create Redis secret (if authentication enabled)
kubectl create secret generic redis-secrets \
  --from-literal=redis-password="$REDIS_PASSWORD" \
  --from-literal=redis-url="redis://:${REDIS_PASSWORD}@redis:6379/0" \
  -n aura-production

# 5. Verify secrets
kubectl get secrets -n aura-production
```

## Related Documentation

- [Deployment Guide](./deployment-guide.md)
- [Environment Configuration](./environment-config.md)
- [Production Deployment](./production-deployment.md)
