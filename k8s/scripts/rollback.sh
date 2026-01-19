#!/bin/bash
# Rollback Kubernetes deployment to previous version
# Usage: ./rollback.sh [environment] [deployment-name]
# Example: ./rollback.sh production backend

set -e

ENVIRONMENT="${1:-dev}"
DEPLOYMENT="${2:-backend}"
NAMESPACE="aura-${ENVIRONMENT}"

if [ -z "$ENVIRONMENT" ] || [ -z "$DEPLOYMENT" ]; then
    echo "Usage: $0 [environment] [deployment-name]"
    echo "Example: $0 production backend"
    exit 1
fi

echo "=========================================="
echo "Rolling back deployment: $DEPLOYMENT"
echo "Environment: $ENVIRONMENT"
echo "Namespace: $NAMESPACE"
echo "=========================================="
echo ""

# Check if namespace exists
if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
    echo "Error: Namespace $NAMESPACE does not exist"
    exit 1
fi

# Check if deployment exists
if ! kubectl get deployment "$DEPLOYMENT" -n "$NAMESPACE" &> /dev/null; then
    echo "Error: Deployment $DEPLOYMENT does not exist in namespace $NAMESPACE"
    exit 1
fi

# Show current revision
echo "Current revision:"
kubectl rollout history deployment/"$DEPLOYMENT" -n "$NAMESPACE" | head -5
echo ""

# Confirm rollback
read -p "Rollback to previous revision? (y/N): " -r
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Rollback cancelled"
    exit 0
fi

# Perform rollback
echo "Rolling back..."
kubectl rollout undo deployment/"$DEPLOYMENT" -n "$NAMESPACE"

# Wait for rollout to complete
echo "Waiting for rollout to complete..."
kubectl rollout status deployment/"$DEPLOYMENT" -n "$NAMESPACE" --timeout=10m

# Show new revision
echo ""
echo "New revision:"
kubectl rollout history deployment/"$DEPLOYMENT" -n "$NAMESPACE" | head -5

echo ""
echo "✓ Rollback complete!"
echo ""
echo "Current pods:"
kubectl get pods -n "$NAMESPACE" -l app="$DEPLOYMENT"
