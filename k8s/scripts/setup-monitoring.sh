#!/bin/bash
# Deploy monitoring stack (Loki, Prometheus, Grafana, AlertManager)
# Usage: ./setup-monitoring.sh

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

echo "=========================================="
echo "Deploying Monitoring Stack"
echo "=========================================="
echo ""

# Check if kubectl is available
if ! command -v kubectl &> /dev/null; then
    echo "Error: kubectl is not installed"
    exit 1
fi

# Check if kustomize is available
if ! command -v kustomize &> /dev/null && ! kubectl kustomize --help &> /dev/null; then
    echo "Error: kustomize is not installed"
    exit 1
fi

# Deploy monitoring stack
echo "Deploying monitoring stack..."
cd "$PROJECT_ROOT/k8s/monitoring"

if kubectl kustomize . | kubectl apply -f -; then
    echo "✓ Monitoring stack deployed"
else
    echo "Error: Failed to deploy monitoring stack"
    exit 1
fi

# Wait for pods to be ready
echo ""
echo "Waiting for monitoring pods to be ready..."
kubectl wait --for=condition=ready pod -l app=loki -n monitoring --timeout=5m || true
kubectl wait --for=condition=ready pod -l app=prometheus -n monitoring --timeout=5m || true
kubectl wait --for=condition=ready pod -l app=grafana -n monitoring --timeout=5m || true
kubectl wait --for=condition=ready pod -l app=alertmanager -n monitoring --timeout=5m || true

# Show status
echo ""
echo "Monitoring stack status:"
kubectl get pods -n monitoring

echo ""
echo "=========================================="
echo "✓ Monitoring stack deployment complete!"
echo "=========================================="
echo ""
echo "Services:"
echo "  - Loki: http://loki.monitoring.svc.cluster.local:3100"
echo "  - Prometheus: http://prometheus.monitoring.svc.cluster.local:9090"
echo "  - Grafana: http://grafana.monitoring.svc.cluster.local:3000"
echo "  - AlertManager: http://alertmanager.monitoring.svc.cluster.local:9093"
echo ""
echo "To access Grafana:"
echo "  kubectl port-forward -n monitoring svc/grafana 3000:3000"
echo "  Then open http://localhost:3000"
echo "  Default credentials: admin / admin (change in grafana-secret.yaml)"
echo ""
