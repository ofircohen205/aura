#!/bin/bash
# Health check verification for Aura services
# Usage: ./health-check.sh <environment> [namespace] [timeout] [retries]
# Example: ./health-check.sh staging aura-staging 30 5

set -e

ENVIRONMENT="${1:-dev}"
NAMESPACE="${2:-aura-${ENVIRONMENT}}"
TIMEOUT="${3:-30}"
MAX_RETRIES="${4:-5}"

# Service configuration
BACKEND_SERVICE="backend"
BACKEND_PORT="8000"
BACKEND_HEALTH_PATH="/health"
BACKEND_CACHE_HEALTH_PATH="/health/cache"

WEB_DASHBOARD_SERVICE="web-dashboard"
WEB_DASHBOARD_PORT="3000"
WEB_DASHBOARD_PATH="/"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    local status=$1
    local message=$2
    if [ "$status" = "success" ]; then
        echo -e "${GREEN}✓${NC} $message"
    elif [ "$status" = "error" ]; then
        echo -e "${RED}✗${NC} $message"
    elif [ "$status" = "info" ]; then
        echo -e "${YELLOW}ℹ${NC} $message"
    else
        echo "$message"
    fi
}

# Function to check if kubectl is available
check_kubectl() {
    if ! command -v kubectl &> /dev/null; then
        print_status "error" "kubectl is not installed or not in PATH"
        exit 1
    fi
}

# Function to check if cluster is accessible
check_cluster() {
    if ! kubectl cluster-info &> /dev/null; then
        print_status "error" "Cannot connect to Kubernetes cluster"
        exit 1
    fi
}

# Function to check if namespace exists
check_namespace() {
    if ! kubectl get namespace "${NAMESPACE}" &> /dev/null; then
        print_status "error" "Namespace ${NAMESPACE} does not exist"
        exit 1
    fi
}

# Function to check if service exists
check_service() {
    local service=$1
    if ! kubectl get service "${service}" -n "${NAMESPACE}" &> /dev/null; then
        print_status "error" "Service ${service} does not exist in namespace ${NAMESPACE}"
        return 1
    fi
    return 0
}

# Function to wait for pods to be ready
wait_for_pods() {
    local service=$1
    local label_selector=$2

    print_status "info" "Waiting for ${service} pods to be ready..."

    if ! kubectl wait --for=condition=ready --timeout="${TIMEOUT}s" \
        pod -l "${label_selector}" \
        -n "${NAMESPACE}" &> /dev/null; then
        print_status "error" "${service} pods are not ready"
        return 1
    fi

    return 0
}

# Function to check HTTP endpoint with retries
check_http_endpoint() {
    local url=$1
    local expected_status=$2
    local description=$3
    local retry_count=0

    while [ $retry_count -lt $MAX_RETRIES ]; do
        if response=$(curl -s -w "\n%{http_code}" --max-time 10 "${url}" 2>/dev/null); then
            http_code=$(echo "$response" | tail -n1)
            body=$(echo "$response" | sed '$d')

            if [ "$http_code" = "$expected_status" ]; then
                print_status "success" "${description} - HTTP ${http_code}"
                return 0
            else
                print_status "info" "${description} - HTTP ${http_code} (retrying...)"
            fi
        else
            print_status "info" "${description} - Connection failed (retrying...)"
        fi

        retry_count=$((retry_count + 1))
        if [ $retry_count -lt $MAX_RETRIES ]; then
            sleep 2
        fi
    done

    print_status "error" "${description} - Failed after ${MAX_RETRIES} attempts"
    return 1
}

# Function to check backend health via port-forward
check_backend_health() {
    print_status "info" "Checking backend health endpoint..."

    # Start port-forward in background
    kubectl port-forward -n "${NAMESPACE}" "svc/${BACKEND_SERVICE}" \
        "${BACKEND_PORT}:${BACKEND_PORT}" > /dev/null 2>&1 &
    local pf_pid=$!

    # Wait for port-forward to be ready
    sleep 2

    # Check if port-forward is still running
    if ! kill -0 $pf_pid 2>/dev/null; then
        print_status "error" "Failed to establish port-forward to backend service"
        return 1
    fi

    local health_check_passed=false
    local cache_check_passed=false

    # Check main health endpoint
    if check_http_endpoint "http://localhost:${BACKEND_PORT}${BACKEND_HEALTH_PATH}" \
        200 "Backend health check"; then
        health_check_passed=true
    fi

    # Check cache health endpoint (optional, don't fail if it fails)
    if check_http_endpoint "http://localhost:${BACKEND_PORT}${BACKEND_CACHE_HEALTH_PATH}" \
        200 "Backend cache health check"; then
        cache_check_passed=true
    else
        print_status "info" "Backend cache health check failed (non-critical)"
    fi

    # Stop port-forward
    kill $pf_pid 2>/dev/null || true
    wait $pf_pid 2>/dev/null || true

    if [ "$health_check_passed" = true ]; then
        return 0
    else
        return 1
    fi
}

# Function to check web dashboard via port-forward
check_web_dashboard_health() {
    print_status "info" "Checking web dashboard availability..."

    # Start port-forward in background
    kubectl port-forward -n "${NAMESPACE}" "svc/${WEB_DASHBOARD_SERVICE}" \
        "${WEB_DASHBOARD_PORT}:${WEB_DASHBOARD_PORT}" > /dev/null 2>&1 &
    local pf_pid=$!

    # Wait for port-forward to be ready
    sleep 2

    # Check if port-forward is still running
    if ! kill -0 $pf_pid 2>/dev/null; then
        print_status "error" "Failed to establish port-forward to web dashboard service"
        return 1
    fi

    # Check web dashboard
    local dashboard_check_passed=false
    if check_http_endpoint "http://localhost:${WEB_DASHBOARD_PORT}${WEB_DASHBOARD_PATH}" \
        200 "Web dashboard health check"; then
        dashboard_check_passed=true
    fi

    # Stop port-forward
    kill $pf_pid 2>/dev/null || true
    wait $pf_pid 2>/dev/null || true

    if [ "$dashboard_check_passed" = true ]; then
        return 0
    else
        return 1
    fi
}

# Function to check HPA status (production only)
check_hpa_status() {
    if [ "$ENVIRONMENT" != "production" ]; then
        return 0
    fi

    print_status "info" "Checking HPA status..."

    local hpa_errors=0

    # Check backend HPA
    if kubectl get hpa backend -n "${NAMESPACE}" &> /dev/null; then
        local backend_hpa_status=$(kubectl get hpa backend -n "${NAMESPACE}" -o jsonpath='{.status.conditions[?(@.type=="AbleToScale")].status}' 2>/dev/null || echo "Unknown")
        if [ "$backend_hpa_status" = "True" ]; then
            print_status "success" "Backend HPA is functioning"
        else
            print_status "error" "Backend HPA is not functioning properly"
            hpa_errors=$((hpa_errors + 1))
        fi
    else
        print_status "info" "Backend HPA not found (may not be configured)"
    fi

    # Check web dashboard HPA
    if kubectl get hpa web-dashboard -n "${NAMESPACE}" &> /dev/null; then
        local web_hpa_status=$(kubectl get hpa web-dashboard -n "${NAMESPACE}" -o jsonpath='{.status.conditions[?(@.type=="AbleToScale")].status}' 2>/dev/null || echo "Unknown")
        if [ "$web_hpa_status" = "True" ]; then
            print_status "success" "Web dashboard HPA is functioning"
        else
            print_status "error" "Web dashboard HPA is not functioning properly"
            hpa_errors=$((hpa_errors + 1))
        fi
    else
        print_status "info" "Web dashboard HPA not found (may not be configured)"
    fi

    if [ $hpa_errors -gt 0 ]; then
        return 1
    fi

    return 0
}

# Function to check ingress (production only)
check_ingress() {
    if [ "$ENVIRONMENT" != "production" ]; then
        return 0
    fi

    print_status "info" "Checking ingress configuration..."

    if kubectl get ingress -n "${NAMESPACE}" &> /dev/null; then
        local ingress_count=$(kubectl get ingress -n "${NAMESPACE}" --no-headers 2>/dev/null | wc -l)
        if [ "$ingress_count" -gt 0 ]; then
            print_status "success" "Ingress configured (${ingress_count} ingress(es) found)"
            return 0
        else
            print_status "error" "No ingress resources found"
            return 1
        fi
    else
        print_status "info" "Ingress not configured (may not be required)"
        return 0
    fi
}

# Function to check pod readiness across all replicas
check_pod_readiness() {
    print_status "info" "Checking pod readiness..."

    local all_ready=true

    # Check backend pods
    local backend_ready=$(kubectl get pods -n "${NAMESPACE}" -l app=backend \
        -o jsonpath='{.items[*].status.conditions[?(@.type=="Ready")].status}' 2>/dev/null || echo "")
    local backend_not_ready=$(echo "$backend_ready" | grep -c "False" || echo "0")

    if [ "$backend_not_ready" -gt 0 ]; then
        print_status "error" "Some backend pods are not ready"
        all_ready=false
    else
        print_status "success" "All backend pods are ready"
    fi

    # Check web dashboard pods
    local web_ready=$(kubectl get pods -n "${NAMESPACE}" -l app=web-dashboard \
        -o jsonpath='{.items[*].status.conditions[?(@.type=="Ready")].status}' 2>/dev/null || echo "")
    local web_not_ready=$(echo "$web_ready" | grep -c "False" || echo "0")

    if [ "$web_not_ready" -gt 0 ]; then
        print_status "error" "Some web dashboard pods are not ready"
        all_ready=false
    else
        print_status "success" "All web dashboard pods are ready"
    fi

    if [ "$all_ready" = true ]; then
        return 0
    else
        return 1
    fi
}

# Main execution
main() {
    echo "=========================================="
    echo "Aura Health Check - ${ENVIRONMENT} Environment"
    echo "Namespace: ${NAMESPACE}"
    echo "=========================================="
    echo ""

    # Pre-flight checks
    check_kubectl
    check_cluster
    check_namespace

    # Check services exist
    if ! check_service "${BACKEND_SERVICE}"; then
        exit 1
    fi

    if ! check_service "${WEB_DASHBOARD_SERVICE}"; then
        exit 1
    fi

    # Wait for pods to be ready
    wait_for_pods "${BACKEND_SERVICE}" "app=backend" || exit 1
    wait_for_pods "${WEB_DASHBOARD_SERVICE}" "app=web-dashboard" || exit 1

    local errors=0

    # Health checks
    echo ""
    print_status "info" "Running health checks..."
    echo ""

    if ! check_backend_health; then
        errors=$((errors + 1))
    fi

    if ! check_web_dashboard_health; then
        errors=$((errors + 1))
    fi

    # Production-specific checks
    if [ "$ENVIRONMENT" = "production" ]; then
        echo ""
        print_status "info" "Running production-specific checks..."
        echo ""

        if ! check_hpa_status; then
            errors=$((errors + 1))
        fi

        if ! check_ingress; then
            errors=$((errors + 1))
        fi

        if ! check_pod_readiness; then
            errors=$((errors + 1))
        fi
    fi

    # Summary
    echo ""
    echo "=========================================="
    if [ $errors -eq 0 ]; then
        print_status "success" "All health checks passed!"
        echo "=========================================="
        exit 0
    else
        print_status "error" "Health checks failed with ${errors} error(s)"
        echo "=========================================="
        exit 1
    fi
}

# Run main function
main
