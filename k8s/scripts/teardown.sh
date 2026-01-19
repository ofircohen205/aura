#!/bin/bash
# Teardown Aura from Kubernetes
# Usage: ./teardown.sh <environment> [namespace]
# Example: ./teardown.sh dev aura-dev

set -e

ENVIRONMENT="${1:-dev}"
NAMESPACE="${2:-aura-${ENVIRONMENT}}"
OVERLAY_DIR="k8s/overlays/${ENVIRONMENT}"

if [ ! -d "$OVERLAY_DIR" ]; then
    echo "Error: Overlay directory not found: $OVERLAY_DIR"
    echo "Available environments: dev, staging, production"
    exit 1
fi

echo "Tearing down Aura from ${ENVIRONMENT} environment (namespace: ${NAMESPACE})..."
echo "This will delete all resources in the namespace."

read -p "Are you sure? (yes/no): " -r
if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
    echo "Aborted."
    exit 1
fi

# Delete using kustomize
kubectl delete -k "${OVERLAY_DIR}" || true

# Optionally delete the namespace (uncomment if desired)
# kubectl delete namespace "${NAMESPACE}" || true

echo "Teardown complete!"
