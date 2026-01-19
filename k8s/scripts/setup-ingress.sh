#!/bin/bash
# Install Nginx Ingress Controller
# Usage: ./setup-ingress.sh

set -e

echo "Installing Nginx Ingress Controller..."

# Install using Helm (recommended)
if command -v helm &> /dev/null; then
    echo "Using Helm to install Nginx Ingress Controller..."
    helm upgrade --install ingress-nginx ingress-nginx \
        --repo https://kubernetes.github.io/ingress-nginx \
        --namespace ingress-nginx \
        --create-namespace \
        --set controller.service.type=LoadBalancer
else
    echo "Helm not found. Installing via kubectl..."
    kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.8.2/deploy/static/provider/cloud/deploy.yaml

    echo "Waiting for ingress controller to be ready..."
    kubectl wait --namespace ingress-nginx \
        --for=condition=ready pod \
        --selector=app.kubernetes.io/component=controller \
        --timeout=300s
fi

echo "✓ Nginx Ingress Controller installed"
echo ""
echo "To get the external IP (if using LoadBalancer):"
echo "  kubectl get svc -n ingress-nginx ingress-nginx-controller"
