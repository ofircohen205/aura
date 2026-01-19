#!/bin/bash
# Complete development environment setup
# Usage: ./dev-setup.sh [CLUSTER_NAME]
# Example: ./dev-setup.sh aura-dev

set -e

CLUSTER_NAME="${1:-aura-dev}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=========================================="
echo "Aura Kubernetes Development Setup"
echo "=========================================="
echo "Cluster: $CLUSTER_NAME"
echo ""

# Step 1: Create kind cluster
echo "Step 1: Creating kind cluster..."
"$SCRIPT_DIR/setup-kind.sh" "$CLUSTER_NAME"

# Step 2: Build images
echo ""
echo "Step 2: Building Docker images..."
"$SCRIPT_DIR/build-images.sh" --dev --tag dev

# Step 3: Load images into kind
echo ""
echo "Step 3: Loading images into kind cluster..."
"$SCRIPT_DIR/load-images-kind.sh" "$CLUSTER_NAME" dev

# Step 4: Create migration ConfigMap
echo ""
echo "Step 4: Creating migration ConfigMap..."
"$SCRIPT_DIR/create-migration-configmap.sh" aura-dev

# Step 5: Deploy services
echo ""
echo "Step 5: Deploying services to Kubernetes..."
"$SCRIPT_DIR/deploy.sh" dev

# Step 6: Wait for services
echo ""
echo "Step 6: Waiting for services to be ready..."
sleep 5
kubectl get pods -n aura-dev

echo ""
echo "=========================================="
echo "✓ Development environment setup complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo "  1. Port-forward services:"
echo "     ./port-forward.sh dev"
echo ""
echo "  2. View logs:"
echo "     ./logs.sh backend dev"
echo ""
echo "  3. Access services:"
echo "     Backend: http://localhost:8000"
echo "     Web Dashboard: http://localhost:3000"
echo ""
