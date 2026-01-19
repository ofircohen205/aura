#!/bin/bash
# Create ConfigMap from migration files
# Usage: ./create-migration-configmap.sh [namespace]
# Example: ./create-migration-configmap.sh aura-dev

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"
NAMESPACE="${1:-aura-dev}"
MIGRATION_DIR="$PROJECT_ROOT/deployment/migration"

echo "Creating migration ConfigMap for namespace: $NAMESPACE"
echo "Migration directory: $MIGRATION_DIR"
echo ""

# Check if migration directory exists
if [ ! -d "$MIGRATION_DIR" ]; then
    echo "Error: Migration directory not found: $MIGRATION_DIR"
    exit 1
fi

# Check if namespace exists
if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
    echo "Warning: Namespace $NAMESPACE does not exist. Creating it..."
    kubectl create namespace "$NAMESPACE"
fi

# Create ConfigMap from migration files
echo "Creating ConfigMap from migration files..."
kubectl create configmap migration-scripts \
    --from-file="$MIGRATION_DIR" \
    --namespace="$NAMESPACE" \
    --dry-run=client -o yaml | \
    kubectl apply -f -

echo "✓ Migration ConfigMap created/updated in namespace: $NAMESPACE"
echo ""
echo "To verify:"
echo "  kubectl get configmap migration-scripts -n $NAMESPACE"
echo "  kubectl describe configmap migration-scripts -n $NAMESPACE"
