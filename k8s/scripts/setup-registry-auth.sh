#!/bin/bash
# Setup Docker authentication for GitHub Container Registry
# Usage: ./setup-registry-auth.sh [GITHUB_TOKEN]

set -e

REGISTRY="ghcr.io"
OWNER="ofircohen205"

# Get token from argument or environment variable
if [ -n "$1" ]; then
    GITHUB_TOKEN="$1"
elif [ -z "$GITHUB_TOKEN" ]; then
    echo "Error: GITHUB_TOKEN not provided"
    echo "Usage: $0 [GITHUB_TOKEN]"
    echo "Or set GITHUB_TOKEN environment variable"
    exit 1
fi

echo "Setting up authentication for ${REGISTRY}..."
echo "Owner: $OWNER"
echo ""

# Login to GHCR
echo "$GITHUB_TOKEN" | docker login "${REGISTRY}" -u "$OWNER" --password-stdin

if [ $? -eq 0 ]; then
    echo "✓ Successfully authenticated with ${REGISTRY}"
    echo ""
    echo "You can now push images with:"
    echo "  ./push-images.sh --tag latest --owner $OWNER"
else
    echo "✗ Failed to authenticate with ${REGISTRY}"
    exit 1
fi
