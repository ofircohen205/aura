# Local Kubernetes Development with Auto-Update

This guide explains how to set up automatic code updates for local Kubernetes development.

## Quick Start

### Option 1: Skaffold (Recommended)

Skaffold automatically watches for code changes, rebuilds images, and redeploys to Kubernetes.

**Prerequisites:**

```bash
# Install Skaffold
brew install skaffold  # macOS
# or
curl -Lo skaffold https://storage.googleapis.com/skaffold/releases/latest/skaffold-linux-amd64
sudo install skaffold /usr/local/bin/
```

**Usage:**

```bash
# Start auto-updating development environment
just k8s-skaffold-dev

# Or directly with skaffold
skaffold dev --profile dev
```

**What it does:**

- Watches for code changes in `apps/backend/`, `apps/web-dashboard/`, and `libs/core-py/`
- Automatically rebuilds Docker images when code changes
- Syncs files to running pods for faster iteration (without full rebuild)
- Deploys to Kubernetes using kustomize
- Port-forwards services automatically (backend:8000, web:3000)

**Features:**

- **File Sync**: Python/TypeScript files are synced directly to pods (faster than rebuild)
- **Hot Reload**: Backend uses `uvicorn --reload`, web uses Next.js dev mode
- **Automatic Port Forwarding**: Services accessible at localhost:8000 and localhost:3000

### Option 2: File Watcher Script

A simpler alternative that rebuilds and redeploys on file changes.

**Prerequisites:**

```bash
# Install fswatch
brew install fswatch  # macOS
# or
sudo apt-get install fswatch  # Linux
```

**Usage:**

```bash
# Watch all services
just k8s-watch dev all

# Watch only backend
just k8s-watch dev backend

# Watch only web dashboard
just k8s-watch dev web

# Or directly
./k8s/scripts/watch-and-redeploy.sh dev backend
```

**What it does:**

- Watches for file changes
- Rebuilds Docker images
- Loads images into kind cluster (if using kind)
- Restarts Kubernetes deployments
- Waits for rollout to complete

## Setup

### 1. Ensure Kubernetes Cluster is Running

```bash
# Create kind cluster (if not exists)
just k8s-cluster-create aura-dev

# Or use existing cluster
kubectl cluster-info
```

### 2. Initial Deployment

```bash
# One-time setup
just k8s-dev-setup

# Or manually
just k8s-build-kind aura-dev dev
just k8s-deploy dev
```

### 3. Start Auto-Update

Choose one of the options above (Skaffold or file watcher).

## How It Works

### Skaffold Flow

1. **File Change Detected** → Skaffold watches your code
2. **File Sync** → Changed files synced to running pods (fast)
3. **Hot Reload** → uvicorn/Next.js detects changes and reloads
4. **If Needed** → Full image rebuild and redeploy

### File Watcher Flow

1. **File Change Detected** → fswatch detects changes
2. **Image Rebuild** → Docker builds new image
3. **Load to Cluster** → Image loaded into kind (if applicable)
4. **Rollout Restart** → Kubernetes restarts deployment
5. **Wait for Ready** → Waits for new pods to be ready

## Configuration

### Skaffold Configuration

Edit `skaffold.yaml` to customize:

- Watch paths
- Build commands
- Sync patterns
- Port forwarding

### File Watcher Configuration

Edit `k8s/scripts/watch-and-redeploy.sh` to customize:

- Watch paths
- Build commands
- Deployment namespaces

## Troubleshooting

### Skaffold Issues

**Images not updating:**

```bash
# Force rebuild
skaffold build --profile dev
skaffold deploy --profile dev
```

**Port forwarding not working:**

```bash
# Check if ports are already in use
lsof -i :8000
lsof -i :3000

# Manually port-forward
kubectl port-forward -n aura-dev svc/backend 8000:8000
```

### File Watcher Issues

**fswatch not detecting changes:**

```bash
# Check if fswatch is working
fswatch -o apps/backend | head -1
```

**Images not loading into kind:**

```bash
# Check kind cluster name
kubectl config current-context

# Manually load image
kind load docker-image aura-backend:dev --name aura-dev
```

### General Issues

**Pods not restarting:**

```bash
# Check deployment status
kubectl get deployments -n aura-dev
kubectl describe deployment backend -n aura-dev

# Manual restart
kubectl rollout restart deployment/backend -n aura-dev
```

**Code changes not reflected:**

- Backend: Check if `--reload` flag is set in deployment
- Web: Check if Next.js dev mode is enabled
- Verify file sync is working (check pod logs)

## Best Practices

1. **Use Skaffold for active development** - Better performance with file sync
2. **Use file watcher for simple workflows** - No additional tools needed
3. **Monitor pod logs** - `kubectl logs -f deployment/backend -n aura-dev`
4. **Check resource usage** - `kubectl top pods -n aura-dev`
5. **Clean up regularly** - `just k8s-dev-clean` when done

## Comparison

| Feature          | Skaffold         | File Watcher          |
| ---------------- | ---------------- | --------------------- |
| Setup Complexity | Medium           | Low                   |
| Performance      | Fast (file sync) | Slower (full rebuild) |
| Dependencies     | Skaffold CLI     | fswatch               |
| Port Forwarding  | Automatic        | Manual                |
| File Sync        | Yes              | No                    |
| Hot Reload       | Yes              | Yes (via --reload)    |

## Next Steps

- See [DEVELOPMENT.md](../../docs/DEVELOPMENT.md) for general development guide
- See [DEPLOYMENT.md](../../docs/DEPLOYMENT.md) for deployment documentation
- See [k8s/README.md](./README.md) for Kubernetes-specific docs
