#!/bin/bash
# Watch for code changes and automatically rebuild/redeploy to Kubernetes
# Usage: ./watch-and-redeploy.sh [environment] [service]
# Example: ./watch-and-redeploy.sh dev backend

set -e

ENVIRONMENT="${1:-dev}"
SERVICE="${2:-all}"  # 'backend', 'web', or 'all'
NAMESPACE="aura-${ENVIRONMENT}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Check if required tools are installed
command -v fswatch >/dev/null 2>&1 || {
    echo "Error: fswatch is required but not installed."
    echo "Install with: brew install fswatch (macOS) or apt-get install fswatch (Linux)"
    exit 1
}

command -v kubectl >/dev/null 2>&1 || {
    echo "Error: kubectl is required but not installed."
    exit 1
}

echo "=========================================="
echo "Kubernetes Auto-Update Watcher"
echo "=========================================="
echo "Environment: $ENVIRONMENT"
echo "Namespace: $NAMESPACE"
echo "Service: $SERVICE"
echo "Watching for code changes..."
echo ""
echo "Press Ctrl+C to stop"
echo "=========================================="
echo ""

# Function to rebuild and redeploy
rebuild_and_redeploy() {
    local changed_file="$1"
    local service_to_rebuild=""

    # Determine which service changed
    if echo "$changed_file" | grep -q "apps/backend"; then
        service_to_rebuild="backend"
    elif echo "$changed_file" | grep -q "apps/web-dashboard"; then
        service_to_rebuild="web-dashboard"
    elif echo "$changed_file" | grep -q "libs/core-py"; then
        service_to_rebuild="backend"  # Core lib affects backend
    fi

    # Skip if service filter doesn't match
    if [ "$SERVICE" != "all" ] && [ "$service_to_rebuild" != "$SERVICE" ]; then
        return 0
    fi

    echo ""
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] Detected change: $changed_file"
    echo "Rebuilding and redeploying: $service_to_rebuild"

    # Build image
    cd "$PROJECT_ROOT"
    if [ "$service_to_rebuild" == "backend" ]; then
        echo "Building backend image..."
        docker build -f apps/backend/Dockerfile --target development -t aura-backend:dev .

        # Load into kind if using kind
        if kubectl config current-context 2>/dev/null | grep -q "kind"; then
            kind load docker-image aura-backend:dev --name "$(kubectl config current-context | cut -d'-' -f2-)" 2>/dev/null || true
        fi

        # Restart deployment
        echo "Restarting backend deployment..."
        kubectl rollout restart deployment/backend -n "$NAMESPACE" || true
        kubectl rollout status deployment/backend -n "$NAMESPACE" --timeout=5m || true

    elif [ "$service_to_rebuild" == "web-dashboard" ]; then
        echo "Building web dashboard image..."
        docker build -f apps/web-dashboard/Dockerfile.dev -t aura-web-dashboard:dev .

        # Load into kind if using kind
        if kubectl config current-context 2>/dev/null | grep -q "kind"; then
            kind load docker-image aura-web-dashboard:dev --name "$(kubectl config current-context | cut -d'-' -f2-)" 2>/dev/null || true
        fi

        # Restart deployment
        echo "Restarting web-dashboard deployment..."
        kubectl rollout restart deployment/web-dashboard -n "$NAMESPACE" || true
        kubectl rollout status deployment/web-dashboard -n "$NAMESPACE" --timeout=5m || true
    fi

    echo "✓ Update complete"
    echo ""
}

# Watch for changes
cd "$PROJECT_ROOT"

# Watch paths based on service
if [ "$SERVICE" == "backend" ]; then
    WATCH_PATHS="apps/backend libs/core-py"
elif [ "$SERVICE" == "web" ] || [ "$SERVICE" == "web-dashboard" ]; then
    WATCH_PATHS="apps/web-dashboard"
else
    WATCH_PATHS="apps/backend apps/web-dashboard libs/core-py"
fi

echo "Watching: $WATCH_PATHS"
echo ""

# Use fswatch to watch for changes
fswatch -o $WATCH_PATHS | while read f; do
    # Get the actual changed file
    changed_file=$(fswatch -1 $WATCH_PATHS 2>/dev/null | head -1 || echo "")
    if [ -n "$changed_file" ]; then
        rebuild_and_redeploy "$changed_file"
    else
        # Fallback: rebuild all if we can't determine the file
        echo ""
        echo "[$(date '+%Y-%m-%d %H:%M:%S')] Change detected, rebuilding all services..."
        rebuild_and_redeploy "unknown"
    fi
done
