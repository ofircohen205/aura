#!/bin/bash
# Setup kind cluster for Aura development
# Usage: ./setup-kind.sh [CLUSTER_NAME]
# Example: ./setup-kind.sh aura-dev

set -e

CLUSTER_NAME="${1:-aura-dev}"

echo "Setting up kind cluster: $CLUSTER_NAME"
echo ""

# Check if kind is installed
if ! command -v kind &> /dev/null; then
    echo "Error: kind is not installed"
    echo ""
    echo "Install with:"
    echo "  macOS: brew install kind"
    echo "  Linux: See https://kind.sigs.k8s.io/docs/user/quick-start/#installation"
    echo "  Or: go install sigs.k8s.io/kind@latest"
    exit 1
fi

# Check if cluster already exists
if kind get clusters | grep -q "^${CLUSTER_NAME}$"; then
    echo "Cluster '$CLUSTER_NAME' already exists"
    read -p "Delete and recreate? (y/N): " -r
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Deleting existing cluster..."
        kind delete cluster --name "$CLUSTER_NAME"
        # Wait for cluster to fully delete and ports to be released
        echo "Waiting for cluster deletion to complete..."
        sleep 3
        # Verify cluster is deleted
        if kind get clusters | grep -q "^${CLUSTER_NAME}$"; then
            echo "Warning: Cluster still exists, waiting longer..."
            sleep 5
        fi
    else
        echo "Using existing cluster"
        kubectl cluster-info --context "kind-${CLUSTER_NAME}"
        exit 0
    fi
fi

# Create kind cluster with retry logic for port conflicts
echo "Creating kind cluster: $CLUSTER_NAME"
MAX_RETRIES=3
RETRY_COUNT=0
while [ $RETRY_COUNT -lt $MAX_RETRIES ]; do
    if kind create cluster --name "$CLUSTER_NAME"; then
        break
    else
        RETRY_COUNT=$((RETRY_COUNT + 1))
        if [ $RETRY_COUNT -lt $MAX_RETRIES ]; then
            echo "Failed to create cluster (attempt $RETRY_COUNT/$MAX_RETRIES)"
            echo "This might be due to port conflicts. Waiting before retry..."
            sleep 5
            # Try to clean up any partial cluster
            kind delete cluster --name "$CLUSTER_NAME" 2>/dev/null || true
        else
            echo "Error: Failed to create cluster after $MAX_RETRIES attempts"
            echo "This might be due to port conflicts. Try:"
            echo "  1. Check if ports are in use: lsof -i :6443"
            echo "  2. Delete any existing kind clusters: kind get clusters | xargs -I {} kind delete cluster --name {}"
            echo "  3. Restart Docker if needed"
            exit 1
        fi
    fi
done

# Wait for cluster to be ready
echo "Waiting for cluster to be ready..."
kubectl wait --for=condition=Ready nodes --all --timeout=300s --context "kind-${CLUSTER_NAME}"

# Set kubectl context
kubectl config use-context "kind-${CLUSTER_NAME}"

# Verify cluster
echo ""
echo "✓ Cluster created successfully!"
echo ""
echo "Cluster info:"
kubectl cluster-info
echo ""
echo "Nodes:"
kubectl get nodes
echo ""
echo "To use this cluster:"
echo "  kubectl config use-context kind-${CLUSTER_NAME}"
echo ""
echo "To delete this cluster:"
echo "  kind delete cluster --name ${CLUSTER_NAME}"
