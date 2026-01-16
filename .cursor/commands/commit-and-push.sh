#!/bin/bash
# Cursor command: Commit and push following development pipeline
# This command can be invoked from Cursor's command palette

# Get the project root (assuming script is in .cursor/commands/)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/../.." && pwd)"

# Execute the main script
exec "$PROJECT_ROOT/scripts/commit-and-push.sh" "$@"
