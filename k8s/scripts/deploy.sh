#!/bin/bash
# Deploy Aura to Kubernetes using Kustomize
# Usage: ./deploy.sh <environment> [namespace]
# Example: ./deploy.sh dev aura-dev

set -e

ENVIRONMENT="${1:-dev}"
NAMESPACE="${2:-aura-${ENVIRONMENT}}"
OVERLAY_DIR="k8s/overlays/${ENVIRONMENT}"

if [ ! -d "$OVERLAY_DIR" ]; then
    echo "Error: Overlay directory not found: $OVERLAY_DIR"
    echo "Available environments: dev, staging, production"
    exit 1
fi

echo "Deploying Aura to ${ENVIRONMENT} environment (namespace: ${NAMESPACE})..."

# Check if cluster is accessible
if ! kubectl cluster-info &> /dev/null; then
    echo "Error: Cannot connect to Kubernetes cluster"
    echo "Make sure kubectl is configured and cluster is running"
    exit 1
fi

# Create namespace if it doesn't exist
if ! kubectl get namespace "${NAMESPACE}" &> /dev/null; then
    echo "Creating namespace: ${NAMESPACE}"
    kubectl create namespace "${NAMESPACE}"
fi

# Apply manifests using kubectl and kustomize
echo "Applying Kubernetes manifests..."
kubectl apply -k "${OVERLAY_DIR}"

# Wait for deployments to be ready
echo "Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/backend -n "${NAMESPACE}" || echo "Warning: Backend deployment not ready"
kubectl wait --for=condition=available --timeout=300s deployment/web-dashboard -n "${NAMESPACE}" || echo "Warning: Web dashboard deployment not ready"
kubectl wait --for=condition=ready --timeout=300s pod -l app=postgres -n "${NAMESPACE}" || echo "Warning: PostgreSQL not ready"

# Wait for migration job to complete (if exists)
echo "Checking migration job..."
if kubectl get job flyway-migrations -n "${NAMESPACE}" &> /dev/null; then
    echo "Waiting for migrations to complete..."
    kubectl wait --for=condition=complete --timeout=300s job/flyway-migrations -n "${NAMESPACE}" || echo "Warning: Migration job not complete"
fi

echo "Deployment complete!"
echo ""
echo "To view pods:"
echo "  kubectl get pods -n ${NAMESPACE}"
echo ""
echo "To view services:"
echo "  kubectl get svc -n ${NAMESPACE}"
echo ""
echo "To port-forward services:"
echo "  kubectl port-forward -n ${NAMESPACE} svc/backend 8000:8000"
echo "  kubectl port-forward -n ${NAMESPACE} svc/web-dashboard 3000:3000"
