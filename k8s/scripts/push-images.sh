#!/bin/bash
# Push Docker images to GitHub Container Registry
# Usage: ./push-images.sh [--tag TAG] [--owner OWNER]
# Example: ./push-images.sh --tag v1.0.0 --owner ofircohen205

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

TAG="latest"
OWNER="ofircohen205"
REGISTRY="ghcr.io"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --tag)
            TAG="$2"
            shift 2
            ;;
        --owner)
            OWNER="$2"
            shift 2
            ;;
        --registry)
            REGISTRY="$2"
            shift 2
            ;;
        *)
            echo "Unknown option: $1"
            echo "Usage: $0 [--tag TAG] [--owner OWNER] [--registry REGISTRY]"
            exit 1
            ;;
    esac
done

IMAGE_PREFIX="${REGISTRY}/${OWNER}/aura-"

echo "Pushing images to ${REGISTRY}..."
echo "Owner: $OWNER"
echo "Tag: $TAG"
echo ""

# Check for authentication
if [ -z "$GITHUB_TOKEN" ]; then
    echo "Warning: GITHUB_TOKEN not set"
    echo "Attempting docker login to ${REGISTRY}..."
    echo "If this fails, set GITHUB_TOKEN or run:"
    echo "  echo \$GITHUB_TOKEN | docker login ${REGISTRY} -u USERNAME --password-stdin"
    docker login "${REGISTRY}" || {
        echo "Error: Failed to authenticate with ${REGISTRY}"
        echo "Set GITHUB_TOKEN environment variable or login manually"
        exit 1
    }
else
    echo "$GITHUB_TOKEN" | docker login "${REGISTRY}" -u "$OWNER" --password-stdin
fi

cd "$PROJECT_ROOT"

# Tag and push backend image
BACKEND_LOCAL="aura-backend:${TAG}"
BACKEND_REMOTE="${IMAGE_PREFIX}backend:${TAG}"

if docker image inspect "$BACKEND_LOCAL" &> /dev/null; then
    echo "Tagging $BACKEND_LOCAL as $BACKEND_REMOTE..."
    docker tag "$BACKEND_LOCAL" "$BACKEND_REMOTE"

    echo "Pushing $BACKEND_REMOTE..."
    docker push "$BACKEND_REMOTE"
    echo "✓ Backend image pushed"
else
    echo "Error: Image $BACKEND_LOCAL not found"
    echo "Build it first with: ./build-images.sh --prod --tag $TAG"
    exit 1
fi

# Tag and push web dashboard image
WEB_LOCAL="aura-web-dashboard:${TAG}"
WEB_REMOTE="${IMAGE_PREFIX}web-dashboard:${TAG}"

if docker image inspect "$WEB_LOCAL" &> /dev/null; then
    echo "Tagging $WEB_LOCAL as $WEB_REMOTE..."
    docker tag "$WEB_LOCAL" "$WEB_REMOTE"

    echo "Pushing $WEB_REMOTE..."
    docker push "$WEB_REMOTE"
    echo "✓ Web dashboard image pushed"
else
    echo "Error: Image $WEB_LOCAL not found"
    echo "Build it first with: ./build-images.sh --prod --tag $TAG"
    exit 1
fi

echo ""
echo "✓ All images pushed to ${REGISTRY}/${OWNER}/"
echo ""
echo "Images available at:"
echo "  ${BACKEND_REMOTE}"
echo "  ${WEB_REMOTE}"
