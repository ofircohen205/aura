# Environment-Specific Configuration

This document describes the configuration differences between local development, staging, and production environments.

## Overview

Aura uses environment-based configuration to adapt behavior for different deployment contexts. Configuration is managed through:

- Environment variables (set in Kubernetes ConfigMaps/Secrets)
- Environment-specific `.env` files
- Kubernetes overlays (for environment-specific manifests)

## Environments

### Local Development

**Purpose**: Local development and testing  
**Namespace**: `aura-dev`  
**Cluster**: kind (local) or Docker Desktop Kubernetes

### Staging

**Purpose**: Pre-production testing and validation  
**Namespace**: `aura-staging`  
**Cluster**: Shared staging cluster or dedicated staging environment

### Production

**Purpose**: Live production environment  
**Namespace**: `aura-production`  
**Cluster**: Production Kubernetes cluster

## Configuration Differences

### Rate Limiting

| Setting                    | Local              | Staging      | Production   |
| -------------------------- | ------------------ | ------------ | ------------ |
| `RATE_LIMIT_ENABLED`       | `false` or `true`  | `true`       | `true`       |
| `RATE_LIMIT_REQUESTS`      | `1000` (generous)  | `500`        | `100`        |
| `RATE_LIMIT_WINDOW`        | `60` seconds       | `60` seconds | `60` seconds |
| `RATE_LIMIT_REDIS_ENABLED` | `false` (optional) | `true`       | `true`       |

**Rationale**:

- Local: Relaxed limits for development convenience
- Staging: Moderate limits to test rate limiting behavior
- Production: Strict limits to prevent abuse

### Token Expiration

| Setting                           | Local             | Staging | Production |
| --------------------------------- | ----------------- | ------- | ---------- |
| `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` | `1440` (24 hours) | `60`    | `30`       |
| `JWT_REFRESH_TOKEN_EXPIRE_DAYS`   | `30`              | `7`     | `7`        |

**Rationale**:

- Local: Longer tokens for development convenience
- Staging: Production-like settings for testing
- Production: Short-lived tokens for security

### CSRF Protection

| Setting                   | Local        | Staging  | Production |
| ------------------------- | ------------ | -------- | ---------- |
| `CSRF_PROTECTION_ENABLED` | `false`      | `true`   | `true`     |
| `CSRF_SECRET_KEY`         | Not required | Required | Required   |

**Rationale**:

- Local: Disabled for easier development and testing
- Staging/Production: Enabled for security

### HSTS Header Settings

| Setting                   | Local   | Staging             | Production          |
| ------------------------- | ------- | ------------------- | ------------------- |
| `HSTS_ENABLED`            | `false` | `true`              | `true`              |
| `HSTS_MAX_AGE`            | N/A     | `31536000` (1 year) | `31536000` (1 year) |
| `HSTS_INCLUDE_SUBDOMAINS` | N/A     | `true`              | `true`              |
| `HSTS_PRELOAD`            | N/A     | `false`             | `true`              |

**Rationale**:

- Local: Disabled (no HTTPS in local development)
- Staging: Enabled for testing HSTS behavior
- Production: Fully enabled with preload for maximum security

### CORS Configuration

| Setting                  | Local                                  | Staging                                       | Production                                    |
| ------------------------ | -------------------------------------- | --------------------------------------------- | --------------------------------------------- |
| `CORS_ALLOW_ORIGINS`     | `["*"]` or `["http://localhost:3000"]` | Specific domains                              | Specific domains only                         |
| `CORS_ALLOW_CREDENTIALS` | `true`                                 | `true`                                        | `true`                                        |
| `CORS_ALLOW_METHODS`     | `["*"]`                                | `["GET", "POST", "PUT", "DELETE", "OPTIONS"]` | `["GET", "POST", "PUT", "DELETE", "OPTIONS"]` |
| `CORS_ALLOW_HEADERS`     | `["*"]`                                | Specific headers                              | Specific headers only                         |

**Rationale**:

- Local: Permissive for development
- Staging: More restrictive to test CORS behavior
- Production: Strict whitelist for security

### Logging

| Setting      | Local    | Staging                      | Production                   |
| ------------ | -------- | ---------------------------- | ---------------------------- |
| `LOG_LEVEL`  | `DEBUG`  | `INFO`                       | `INFO` or `WARNING`          |
| `LOG_FORMAT` | `text`   | `json`                       | `json`                       |
| `LOG_FILE`   | `stdout` | `stdout` (collected by Loki) | `stdout` (collected by Loki) |

**Rationale**:

- Local: Verbose text logs for debugging
- Staging/Production: Structured JSON logs for log aggregation

### Database Configuration

| Setting                  | Local | Staging | Production |
| ------------------------ | ----- | ------- | ---------- |
| `POSTGRES_POOL_MAX_SIZE` | `10`  | `20`    | `50`       |
| `POSTGRES_POOL_MIN_SIZE` | `2`   | `5`     | `10`       |
| Connection Timeout       | `5s`  | `10s`   | `30s`      |

**Rationale**:

- Local: Smaller pool for resource efficiency
- Staging: Moderate pool for testing
- Production: Larger pool for high availability

### Redis Configuration

| Setting               | Local              | Staging | Production |
| --------------------- | ------------------ | ------- | ---------- |
| `REDIS_ENABLED`       | `false` (optional) | `true`  | `true`     |
| `REDIS_AUTH_DB`       | `2`                | `2`     | `2`        |
| `REDIS_RATE_LIMIT_DB` | `1`                | `1`     | `1`        |
| Connection Pool Size  | `5`                | `10`    | `20`       |

**Rationale**:

- Local: Optional for development without Redis
- Staging/Production: Required for distributed features

### API Configuration

| Setting       | Local                | Staging                  | Production             |
| ------------- | -------------------- | ------------------------ | ---------------------- |
| `API_TITLE`   | `Aura Backend (Dev)` | `Aura Backend (Staging)` | `Aura Backend`         |
| `API_VERSION` | `0.1.0-dev`          | `0.1.0-staging`          | `0.1.0` or version tag |
| `ENVIRONMENT` | `local`              | `staging`                | `production`           |

### Security Headers

| Setting                   | Local                             | Staging                           | Production      |
| ------------------------- | --------------------------------- | --------------------------------- | --------------- |
| `X_FRAME_OPTIONS`         | `SAMEORIGIN`                      | `DENY`                            | `DENY`          |
| `X_CONTENT_TYPE_OPTIONS`  | `nosniff`                         | `nosniff`                         | `nosniff`       |
| `X_XSS_PROTECTION`        | `1; mode=block`                   | `1; mode=block`                   | `1; mode=block` |
| `REFERRER_POLICY`         | `strict-origin-when-cross-origin` | `strict-origin-when-cross-origin` | `no-referrer`   |
| `CONTENT_SECURITY_POLICY` | Relaxed                           | Moderate                          | Strict          |

## Kubernetes-Specific Configuration

### Resource Limits

| Resource                     | Local   | Staging | Production |
| ---------------------------- | ------- | ------- | ---------- |
| Backend CPU Request          | `100m`  | `200m`  | `500m`     |
| Backend CPU Limit            | `500m`  | `1000m` | `2000m`    |
| Backend Memory Request       | `256Mi` | `512Mi` | `1Gi`      |
| Backend Memory Limit         | `512Mi` | `1Gi`   | `2Gi`      |
| Web Dashboard CPU Request    | `100m`  | `200m`  | `500m`     |
| Web Dashboard CPU Limit      | `500m`  | `1000m` | `2000m`    |
| Web Dashboard Memory Request | `256Mi` | `512Mi` | `1Gi`      |
| Web Dashboard Memory Limit   | `512Mi` | `1Gi`   | `2Gi`      |

### Replicas

| Service       | Local | Staging | Production        |
| ------------- | ----- | ------- | ----------------- |
| Backend       | `1`   | `2`     | `3+` (HPA: 3-10)  |
| Web Dashboard | `1`   | `2`     | `3+` (HPA: 3-10)  |
| PostgreSQL    | `1`   | `1`     | `1` (StatefulSet) |

### Auto-Scaling

| Setting       | Local   | Staging | Production |
| ------------- | ------- | ------- | ---------- |
| HPA Enabled   | `false` | `false` | `true`     |
| Min Replicas  | N/A     | N/A     | `3`        |
| Max Replicas  | N/A     | N/A     | `10`       |
| Target CPU    | N/A     | N/A     | `70%`      |
| Target Memory | N/A     | N/A     | `80%`      |

### Health Checks

| Setting                   | Local | Staging | Production |
| ------------------------- | ----- | ------- | ---------- |
| Liveness Initial Delay    | `30s` | `30s`   | `30s`      |
| Liveness Period           | `10s` | `10s`   | `10s`      |
| Readiness Initial Delay   | `10s` | `10s`   | `10s`      |
| Readiness Period          | `5s`  | `5s`    | `5s`       |
| Startup Failure Threshold | `30`  | `30`    | `30`       |

### Network Policies

| Setting                  | Local   | Staging | Production |
| ------------------------ | ------- | ------- | ---------- |
| Network Policies Enabled | `false` | `true`  | `true`     |
| Default Deny             | `false` | `true`  | `true`     |

### Pod Security

| Setting               | Local        | Staging    | Production              |
| --------------------- | ------------ | ---------- | ----------------------- |
| Pod Security Standard | `privileged` | `baseline` | `restricted`            |
| Run as Non-Root       | `false`      | `true`     | `true`                  |
| Read-Only Root FS     | `false`      | `false`    | `true` (where possible) |

## Configuration Files

### Environment Files

- **Local**: `.env.local` (gitignored, created locally)
- **Staging**: `.env.staging` (gitignored, managed via ConfigMap)
- **Production**: `.env.production` (gitignored, managed via ConfigMap)

### Kubernetes Overlays

- **Local**: `k8s/overlays/dev/`
- **Staging**: `k8s/overlays/staging/`
- **Production**: `k8s/overlays/production/`

## Setting Environment Variables

### Local Development

Create `.env.local` in project root:

```bash
ENVIRONMENT=local
RATE_LIMIT_ENABLED=false
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=1440
CSRF_PROTECTION_ENABLED=false
LOG_LEVEL=DEBUG
LOG_FORMAT=text
```

### Kubernetes (Staging/Production)

Set via ConfigMap or Secret:

```bash
# Create ConfigMap
kubectl create configmap backend-config \
  --from-literal=RATE_LIMIT_ENABLED=true \
  --from-literal=RATE_LIMIT_REQUESTS=100 \
  --from-literal=LOG_LEVEL=INFO \
  -n aura-production

# Or use kustomize
# Edit k8s/overlays/production/kustomization.yaml
```

## Configuration Validation

### Validate Configuration

```bash
# Check current configuration
kubectl get configmap backend-config -n aura-production -o yaml

# Test configuration in pod
kubectl exec -it -n aura-production deployment/backend -- env | grep -E "RATE_LIMIT|JWT|CSRF"
```

### Configuration Testing

Test environment-specific behavior:

```bash
# Local: Should have relaxed rate limits
curl http://localhost:8000/api/v1/auth/login

# Staging: Should enforce rate limits
curl https://api.staging.aura.example.com/api/v1/auth/login

# Production: Should have strict rate limits
curl https://api.aura.example.com/api/v1/auth/login
```

## Best Practices

1. **Never commit secrets**: Use Kubernetes Secrets or external secret managers
2. **Use ConfigMaps for non-sensitive config**: Version controlled and auditable
3. **Test in staging first**: Validate configuration changes before production
4. **Document changes**: Update this document when adding new configuration options
5. **Use environment-specific overlays**: Keep configurations separate and clear
6. **Validate before deployment**: Check configuration values before applying

## Related Documentation

- [Deployment Guide](./deployment-guide.md)
- [Secrets Management](./production-secrets.md)
- [Production Deployment](./production-deployment.md)
- [Configuration Management](../../apps/backend/src/core/config.py)
