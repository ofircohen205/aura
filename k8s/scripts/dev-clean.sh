#!/bin/bash
# Clean up development environment
# Usage: ./dev-clean.sh [CLUSTER_NAME] [--delete-cluster]
# Example: ./dev-clean.sh aura-dev --delete-cluster

set -e

CLUSTER_NAME="${1:-aura-dev}"
DELETE_CLUSTER=false

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --delete-cluster)
            DELETE_CLUSTER=true
            shift
            ;;
        *)
            if [ -z "$CLUSTER_NAME_SET" ]; then
                CLUSTER_NAME="$1"
                CLUSTER_NAME_SET=true
            fi
            shift
            ;;
    esac
done

echo "Cleaning up development environment..."
echo "Cluster: $CLUSTER_NAME"
echo ""

# Teardown Kubernetes resources
if kubectl get namespace aura-dev &> /dev/null; then
    echo "Removing Kubernetes resources..."
    kubectl delete -k k8s/overlays/dev || true
    echo "✓ Kubernetes resources removed"
else
    echo "Namespace aura-dev not found, skipping..."
fi

# Optionally delete cluster
if [ "$DELETE_CLUSTER" = true ]; then
    if kind get clusters | grep -q "^${CLUSTER_NAME}$"; then
        echo "Deleting kind cluster: $CLUSTER_NAME"
        kind delete cluster --name "$CLUSTER_NAME"
        echo "✓ Cluster deleted"
    else
        echo "Cluster $CLUSTER_NAME not found"
    fi
else
    echo "Cluster preserved (use --delete-cluster to remove)"
fi

# Optionally remove images
read -p "Remove Docker images? (y/N): " -r
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Removing Docker images..."
    docker rmi aura-backend:dev aura-web-dashboard:dev 2>/dev/null || echo "Images not found or in use"
    echo "✓ Images removed"
fi

echo ""
echo "✓ Cleanup complete!"
