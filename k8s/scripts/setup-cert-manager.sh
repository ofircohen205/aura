#!/bin/bash
# Install cert-manager for TLS certificate management
# Usage: ./setup-cert-manager.sh

set -e

echo "Installing cert-manager..."

# Install cert-manager CRDs
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.13.3/cert-manager.yaml

echo "Waiting for cert-manager to be ready..."
kubectl wait --namespace cert-manager \
    --for=condition=ready pod \
    --selector=app.kubernetes.io/instance=cert-manager \
    --timeout=300s

echo "✓ cert-manager installed"
echo ""
echo "Next steps:"
echo "  1. Update cert-manager-issuer.yaml with your email"
echo "  2. Apply the ClusterIssuer: kubectl apply -f k8s/overlays/production/cert-manager-issuer.yaml"
