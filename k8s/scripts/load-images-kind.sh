#!/bin/bash
# Load Docker images into kind cluster
# Usage: ./load-images-kind.sh [CLUSTER_NAME] [IMAGE_TAG]
# Example: ./load-images-kind.sh aura-dev dev

set -e

CLUSTER_NAME="${1:-aura-dev}"
IMAGE_TAG="${2:-dev}"

echo "Loading images into kind cluster: $CLUSTER_NAME"
echo "Image tag: $IMAGE_TAG"
echo ""

# Check if kind is installed
if ! command -v kind &> /dev/null; then
    echo "Error: kind is not installed"
    echo "Install with: brew install kind (macOS) or see https://kind.sigs.k8s.io/docs/user/quick-start/"
    exit 1
fi

# Check if cluster exists
if ! kind get clusters | grep -q "^${CLUSTER_NAME}$"; then
    echo "Error: kind cluster '$CLUSTER_NAME' not found"
    echo "Create it with: kind create cluster --name $CLUSTER_NAME"
    exit 1
fi

# Load backend image
BACKEND_IMAGE="aura-backend:${IMAGE_TAG}"
if docker image inspect "$BACKEND_IMAGE" &> /dev/null; then
    echo "Loading $BACKEND_IMAGE..."
    kind load docker-image "$BACKEND_IMAGE" --name "$CLUSTER_NAME"
    echo "✓ Backend image loaded"
else
    echo "Warning: Image $BACKEND_IMAGE not found. Build it first with:"
    echo "  ./build-images.sh --dev --tag $IMAGE_TAG"
fi

# Load web dashboard image
WEB_IMAGE="aura-web-dashboard:${IMAGE_TAG}"
if docker image inspect "$WEB_IMAGE" &> /dev/null; then
    echo "Loading $WEB_IMAGE..."
    kind load docker-image "$WEB_IMAGE" --name "$CLUSTER_NAME"
    echo "✓ Web dashboard image loaded"
else
    echo "Warning: Image $WEB_IMAGE not found. Build it first with:"
    echo "  ./build-images.sh --dev --tag $IMAGE_TAG"
fi

echo ""
echo "✓ Images loaded into kind cluster: $CLUSTER_NAME"
