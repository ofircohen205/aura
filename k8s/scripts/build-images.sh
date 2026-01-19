#!/bin/bash
# Build Docker images for Aura services
# Usage: ./build-images.sh [--dev] [--prod] [--tag TAG] [--registry REGISTRY]
# Example: ./build-images.sh --dev --tag v1.0.0
# Example: ./build-images.sh --prod --registry ghcr.io/ofircohen205

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

BUILD_DEV=false
BUILD_PROD=false
TAG=""
REGISTRY=""
VERSION_TAG=""

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --dev)
            BUILD_DEV=true
            shift
            ;;
        --prod)
            BUILD_PROD=true
            shift
            ;;
        --tag)
            TAG="$2"
            shift 2
            ;;
        --registry)
            REGISTRY="$2"
            shift 2
            ;;
        --version)
            VERSION_TAG="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--dev] [--prod] [--tag TAG] [--registry REGISTRY] [--version VERSION]"
            exit 1
            ;;
    esac
done

# Default to building both if neither specified
if [ "$BUILD_DEV" = false ] && [ "$BUILD_PROD" = false ]; then
    BUILD_DEV=true
    BUILD_PROD=true
fi

# Determine tag
if [ -z "$TAG" ]; then
    if [ -n "$VERSION_TAG" ]; then
        TAG="$VERSION_TAG"
    elif [ -n "$(git rev-parse --git-dir 2>/dev/null)" ]; then
        TAG="$(git rev-parse --short HEAD)"
    else
        TAG="latest"
    fi
fi

# Build image name prefix
if [ -n "$REGISTRY" ]; then
    IMAGE_PREFIX="${REGISTRY}/"
else
    IMAGE_PREFIX=""
fi

echo "Building Docker images..."
echo "Tag: $TAG"
echo "Registry: ${REGISTRY:-local}"
echo ""

cd "$PROJECT_ROOT"

# Build backend images
if [ "$BUILD_DEV" = true ]; then
    echo "Building backend:dev image..."
    docker build -t "${IMAGE_PREFIX}aura-backend:dev" \
        --target development \
        -f apps/backend/Dockerfile .
    echo "✓ Backend dev image built: ${IMAGE_PREFIX}aura-backend:dev"
fi

if [ "$BUILD_PROD" = true ]; then
    echo "Building backend:${TAG} image..."
    docker build -t "${IMAGE_PREFIX}aura-backend:${TAG}" \
        --target production \
        -f apps/backend/Dockerfile .
    echo "✓ Backend prod image built: ${IMAGE_PREFIX}aura-backend:${TAG}"

    # Also tag as latest if not using version tag
    if [ -z "$VERSION_TAG" ]; then
        docker tag "${IMAGE_PREFIX}aura-backend:${TAG}" "${IMAGE_PREFIX}aura-backend:latest"
    fi
fi

# Build web dashboard images
if [ "$BUILD_DEV" = true ]; then
    echo "Building web-dashboard:dev image..."
    docker build -t "${IMAGE_PREFIX}aura-web-dashboard:dev" \
        -f apps/web-dashboard/Dockerfile.dev \
        .
    echo "✓ Web dashboard dev image built: ${IMAGE_PREFIX}aura-web-dashboard:dev"
fi

if [ "$BUILD_PROD" = true ]; then
    echo "Building web-dashboard:${TAG} image..."
    docker build -t "${IMAGE_PREFIX}aura-web-dashboard:${TAG}" \
        -f apps/web-dashboard/Dockerfile.prod \
        apps/web-dashboard/
    echo "✓ Web dashboard prod image built: ${IMAGE_PREFIX}aura-web-dashboard:${TAG}"

    # Also tag as latest if not using version tag
    if [ -z "$VERSION_TAG" ]; then
        docker tag "${IMAGE_PREFIX}aura-web-dashboard:${TAG}" "${IMAGE_PREFIX}aura-web-dashboard:latest"
    fi
fi

echo ""
echo "✓ All images built successfully!"
echo ""
echo "Built images:"
docker images | grep -E "aura-backend|aura-web-dashboard" | head -10
