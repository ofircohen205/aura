#!/bin/bash
# Script to create a branch with Linear issue linking
# Usage: ./scripts/branch-with-linear.sh <linear-issue-id> [description]

set -e

ISSUE_ID="${1}"
DESCRIPTION="${2}"

if [ -z "$ISSUE_ID" ]; then
    echo "Error: Linear issue ID is required"
    echo "Usage: $0 <linear-issue-id> [description]"
    echo "Example: $0 AURA-123 'implement feature'"
    exit 1
fi

# Normalize issue ID - ensure it has AURA- prefix
if [[ ! "$ISSUE_ID" =~ ^AURA- ]]; then
    ISSUE_ID="AURA-${ISSUE_ID}"
fi

BRANCH_NAME="feature/${ISSUE_ID}-${DESCRIPTION:-$(echo "$ISSUE_ID" | tr '[:upper:]' '[:lower:]')}"

# Replace spaces with hyphens in branch name
BRANCH_NAME=$(echo "$BRANCH_NAME" | tr ' ' '-')

echo "Creating branch: $BRANCH_NAME"
echo "Linked to Linear issue: $ISSUE_ID"

# Ensure we're on main and up to date
git checkout main
git pull origin main

# Create and checkout new branch
git checkout -b "$BRANCH_NAME"

echo "✓ Branch $BRANCH_NAME created and checked out"
echo ""
echo "Next steps:"
echo "1. Start working on the issue"
echo "2. Commit with: git commit -m \"feat(scope): description [$ISSUE_ID]\""
echo "3. Push with: git push origin $BRANCH_NAME"
echo "4. Create PR with: gh pr create --title \"Title\" --body \"Closes $ISSUE_ID\""
