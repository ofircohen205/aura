# Containerization Verification

This document verifies that Docker configuration includes all required dependencies and is properly configured for Kubernetes deployment.

## Dependency Verification

### Backend Dependencies

All authentication and core dependencies are verified in `apps/backend/pyproject.toml`:

- ✅ **bcrypt>=4.0.0** - Password hashing for authentication
- ✅ **python-jose[cryptography]>=3.3.0** - JWT token encoding/decoding
- ✅ **redis>=5.0.0** - Redis client for authentication tokens and rate limiting

### Installation Method

Dependencies are installed via `uv sync --frozen` in the Dockerfile, which:

- Reads from `pyproject.toml for dependency specifications
- Installs all dependencies including authentication-related packages
- Uses frozen lock file (`uv.lock`) for reproducible builds

## Environment Variables

### Required Environment Variables

All environment variables are documented in:

- `apps/backend/src/core/config.py` - Configuration schema with descriptions
- `docs/USER_GUIDE.md` - User-facing documentation
- `docs/GETTING_STARTED.md` - Setup instructions

### Key Environment Variables for Authentication

- `REDIS_URL` - Redis connection string (default: `redis://localhost:6379/0`)
- `REDIS_AUTH_DB` - Redis database number for auth tokens (default: `2`)
- `REDIS_RATE_LIMIT_DB` - Redis database number for rate limiting (default: `1`)
- `REDIS_ENABLED` - Enable/disable Redis (default: `true`)
- `JWT_SECRET_KEY` - Secret key for JWT token signing (required in production)
- `JWT_ALGORITHM` - JWT algorithm (default: `HS256`)
- `JWT_ACCESS_TOKEN_EXPIRE_MINUTES` - Access token expiration (default: `30`)
- `JWT_REFRESH_TOKEN_EXPIRE_DAYS` - Refresh token expiration (default: `7`)

### Kubernetes Configuration

Environment variables are configured via:

- **ConfigMaps**: Non-sensitive configuration (`k8s/base/backend/configmap.yaml`)
- **Secrets**: Sensitive data like JWT keys and database credentials (`k8s/base/backend/secret.yaml`)

## Health Checks

### Health Check Endpoints

Health checks are configured in both Docker and Kubernetes:

1. **Backend Health Check** (`/health`)
   - Verifies database connectivity
   - Returns `200 OK` if healthy, `503 Service Unavailable` if unhealthy
   - Configured in `k8s/base/backend/deployment.yaml`:
     - Liveness probe: `/health` endpoint
     - Readiness probe: `/health` endpoint
     - Startup probe: `/health` endpoint

2. **Cache Health Check** (`/health/cache`)
   - Verifies LLM cache connectivity
   - Returns cache statistics

3. **Redis Health Check** (`/health/redis`) - **NEW**
   - Verifies Redis connectivity for both auth and rate limiting databases
   - Returns connection status for each database
   - Returns `503 Service Unavailable` if all Redis databases are unavailable

### Kubernetes Health Check Configuration

Health checks are configured in `k8s/base/backend/deployment.yaml`:

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 30
  periodSeconds: 10
  timeoutSeconds: 5
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 3

startupProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 0
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 30
```

## Dockerfile Verification

### Backend Dockerfile (`apps/backend/Dockerfile`)

✅ **Base Image**: `python:3.13-slim` - Lightweight Python image
✅ **uv Installation**: Uses official uv image for fast dependency management
✅ **Dependency Installation**: `uv sync --frozen` installs all dependencies from `pyproject.toml`
✅ **Environment Variables**: `PYTHONPATH` configured for monorepo structure
✅ **Production Stage**: Uses `--no-dev` flag to exclude development dependencies

### Web Dashboard Dockerfiles

✅ **Development** (`apps/web-dashboard/Dockerfile.dev`): Node.js Alpine image with dev dependencies
✅ **Production** (`apps/web-dashboard/Dockerfile.prod`): Multi-stage build with optimized standalone output

## Verification Checklist

- [x] bcrypt dependencies in `pyproject.toml`
- [x] python-jose dependencies in `pyproject.toml` (duplicate removed)
- [x] Redis client dependencies in `pyproject.toml`
- [x] Environment variables documented in `config.py`
- [x] Health checks configured in Kubernetes manifests
- [x] Health check endpoints implemented (`/health`, `/health/cache`, `/health/redis`)
- [x] Dockerfile uses proper dependency installation method
- [x] Production Dockerfile excludes dev dependencies

## Testing

To verify containerization:

```bash
# Build backend image
docker build -f apps/backend/Dockerfile -t aura-backend:test .

# Run container and test health checks
docker run -d --name aura-test -p 8000:8000 aura-backend:test
curl http://localhost:8000/health
curl http://localhost:8000/health/redis

# Cleanup
docker stop aura-test && docker rm aura-test
```

## Related Documentation

- [Kubernetes Deployment Guide](../workflows/production-deployment.md)
- [Secrets Management](../workflows/production-secrets.md)
- [Environment Configuration](../workflows/environment-config.md) (AURA-23)
