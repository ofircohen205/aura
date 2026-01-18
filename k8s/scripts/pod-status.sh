#!/bin/bash
# View pod status for Aura Kubernetes deployments
# Usage: ./pod-status.sh [namespace] [service]
# Examples:
#   ./pod-status.sh                    # Show all aura namespaces
#   ./pod-status.sh aura-dev           # Show pods in aura-dev
#   ./pod-status.sh aura-dev backend   # Show backend pods in aura-dev

set -e

NAMESPACE="${1:-}"
SERVICE="${2:-}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo "=========================================="
echo "Aura Kubernetes Pod Status"
echo "=========================================="
echo ""

# If no namespace specified, show all aura namespaces
if [ -z "$NAMESPACE" ]; then
    echo "📦 All Aura Namespaces:"
    echo ""

    # Check for aura namespaces
    NAMESPACES=$(kubectl get namespaces -o name 2>/dev/null | grep -E "aura|monitoring" | sed 's/namespace\///' || echo "")

    if [ -z "$NAMESPACES" ]; then
        echo "  ${YELLOW}No aura or monitoring namespaces found${NC}"
        echo ""
        echo "To create a development environment:"
        echo "  just k8s-dev-setup"
        echo ""
        exit 0
    fi

    # Show pods in each namespace
    for ns in $NAMESPACES; do
        echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        echo "${BLUE}Namespace: ${ns}${NC}"
        echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
        kubectl get pods -n "$ns" 2>/dev/null || echo "  ${YELLOW}No pods found${NC}"
        echo ""
    done

    # Show system pods summary
    echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo "${BLUE}System Namespaces (Summary)${NC}"
    echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    kubectl get pods -n kube-system --no-headers 2>/dev/null | wc -l | xargs -I {} echo "  kube-system: {} pods"
    echo ""

else
    # Show specific namespace
    echo "${BLUE}Namespace: ${NAMESPACE}${NC}"
    echo ""

    # Check if namespace exists
    if ! kubectl get namespace "$NAMESPACE" &> /dev/null; then
        echo "  ${RED}Error: Namespace '$NAMESPACE' does not exist${NC}"
        echo ""
        echo "Available namespaces:"
        kubectl get namespaces -o name | sed 's/namespace\///' | grep -E "aura|monitoring" || echo "  (none found)"
        exit 1
    fi

    # If service specified, filter by label
    if [ -n "$SERVICE" ]; then
        echo "Service: ${SERVICE}"
        echo ""
        kubectl get pods -n "$NAMESPACE" -l app="$SERVICE" -o wide
    else
        kubectl get pods -n "$NAMESPACE" -o wide
    fi

    echo ""
    echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
    echo "${BLUE}Pod Details${NC}"
    echo "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

    # Get pod names
    if [ -n "$SERVICE" ]; then
        PODS=$(kubectl get pods -n "$NAMESPACE" -l app="$SERVICE" -o name 2>/dev/null | sed 's/pod\///' || echo "")
    else
        PODS=$(kubectl get pods -n "$NAMESPACE" -o name 2>/dev/null | sed 's/pod\///' || echo "")
    fi

    if [ -z "$PODS" ]; then
        echo "  ${YELLOW}No pods found${NC}"
    else
        for pod in $PODS; do
            STATUS=$(kubectl get pod "$pod" -n "$NAMESPACE" -o jsonpath='{.status.phase}' 2>/dev/null || echo "Unknown")
            READY=$(kubectl get pod "$pod" -n "$NAMESPACE" -o jsonpath='{.status.containerStatuses[0].ready}' 2>/dev/null || echo "false")
            RESTARTS=$(kubectl get pod "$pod" -n "$NAMESPACE" -o jsonpath='{.status.containerStatuses[0].restartCount}' 2>/dev/null || echo "0")

            if [ "$STATUS" = "Running" ] && [ "$READY" = "true" ]; then
                COLOR=$GREEN
                ICON="✓"
            elif [ "$STATUS" = "Running" ]; then
                COLOR=$YELLOW
                ICON="⏳"
            elif [ "$STATUS" = "Pending" ]; then
                COLOR=$YELLOW
                ICON="⏳"
            else
                COLOR=$RED
                ICON="✗"
            fi

            echo ""
            echo "  ${COLOR}${ICON} ${pod}${NC}"
            echo "    Status: ${STATUS}"
            echo "    Ready: ${READY}"
            echo "    Restarts: ${RESTARTS}"

            # Show recent events if not running
            if [ "$STATUS" != "Running" ] || [ "$READY" != "true" ]; then
                echo "    Recent events:"
                kubectl get events -n "$NAMESPACE" --field-selector involvedObject.name="$pod" --sort-by='.lastTimestamp' | tail -3 | sed 's/^/      /' || echo "      (no events)"
            fi
        done
    fi
fi

echo ""
echo "=========================================="
echo "Quick Commands:"
echo "=========================================="
echo ""
echo "View logs:"
echo "  kubectl logs -n ${NAMESPACE:-aura-dev} <pod-name>"
echo ""
echo "Describe pod:"
echo "  kubectl describe pod -n ${NAMESPACE:-aura-dev} <pod-name>"
echo ""
echo "Watch pods:"
echo "  kubectl get pods -n ${NAMESPACE:-aura-dev} -w"
echo ""
