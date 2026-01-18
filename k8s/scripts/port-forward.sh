#!/bin/bash
# Port-forward Aura services
# Usage: ./port-forward.sh <environment> [namespace]
# Example: ./port-forward.sh dev aura-dev

set -e

ENVIRONMENT="${1:-dev}"
NAMESPACE="${2:-aura-${ENVIRONMENT}}"

echo "Port-forwarding Aura services in ${ENVIRONMENT} environment (namespace: ${NAMESPACE})..."
echo ""
echo "Services will be available at:"
echo "  Backend: http://localhost:8000"
echo "  Web Dashboard: http://localhost:3000"
echo ""
echo "Press Ctrl+C to stop port-forwarding"
echo ""

# Port-forward backend and web-dashboard in background
kubectl port-forward -n "${NAMESPACE}" svc/backend 8000:8000 &
BACKEND_PID=$!

kubectl port-forward -n "${NAMESPACE}" svc/web-dashboard 3000:3000 &
WEB_PID=$!

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Stopping port-forwarding..."
    kill $BACKEND_PID $WEB_PID 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM

# Wait for processes
wait $BACKEND_PID $WEB_PID
