#!/bin/bash
# Script to commit and push changes following the development pipeline
# Usage: ./scripts/commit-and-push.sh [--skip-ci] [--fast-ci]
# Or use as Cursor command: "commit and push"

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
SKIP_CI=false
FAST_CI=false
for arg in "$@"; do
    case $arg in
        --skip-ci)
            SKIP_CI=true
            shift
            ;;
        --fast-ci)
            FAST_CI=true
            shift
            ;;
        *)
            ;;
    esac
done

echo -e "${BLUE}=== Commit & Push (Development Pipeline) ===${NC}\n"

# Check if we're in a git repository
if ! git rev-parse --git-dir > /dev/null 2>&1; then
    echo -e "${RED}Error: Not in a git repository${NC}"
    exit 1
fi

# Check if there are changes to commit
if [ -z "$(git status --porcelain)" ]; then
    echo -e "${YELLOW}No changes to commit${NC}"
    exit 0
fi

# Get current branch
CURRENT_BRANCH=$(git branch --show-current)
echo -e "${BLUE}Current branch: ${CURRENT_BRANCH}${NC}\n"

# Show status
echo -e "${BLUE}Changes to be committed:${NC}"
git status --short
echo ""

# Step 1: Run CI checks (optional)
if [ "$SKIP_CI" = false ]; then
    echo -e "${BLUE}Step 1: Running CI checks...${NC}"
    if [ "$FAST_CI" = true ]; then
        echo -e "${YELLOW}Running fast CI checks (skipping tests and builds)...${NC}"
        if command -v just > /dev/null 2>&1; then
            just ci-check-fast || {
                echo -e "${RED}CI checks failed. Use --skip-ci to skip or fix the issues.${NC}"
                exit 1
            }
        else
            echo -e "${YELLOW}Justfile not found, skipping CI checks${NC}"
        fi
    else
        echo -e "${YELLOW}Running full CI checks...${NC}"
        if command -v just > /dev/null 2>&1; then
            just ci-check || {
                echo -e "${RED}CI checks failed. Use --fast-ci for faster checks or --skip-ci to skip.${NC}"
                exit 1
            }
        else
            echo -e "${YELLOW}Justfile not found, skipping CI checks${NC}"
        fi
    fi
    echo -e "${GREEN}✓ CI checks passed${NC}\n"
else
    echo -e "${YELLOW}Skipping CI checks (--skip-ci flag used)${NC}\n"
fi

# Step 2: Get commit details
echo -e "${BLUE}Step 2: Commit details${NC}"

# Commit types
echo -e "${YELLOW}Commit types:${NC}"
echo "  feat    - New feature"
echo "  fix     - Bug fix"
echo "  refactor - Code refactoring"
echo "  test    - Test additions/changes"
echo "  docs    - Documentation changes"
echo "  chore   - Maintenance tasks"
echo ""

# Prompt for commit type
read -p "Commit type (feat/fix/refactor/test/docs/chore): " COMMIT_TYPE
COMMIT_TYPE=$(echo "$COMMIT_TYPE" | tr '[:upper:]' '[:lower:]' | xargs)

if [[ ! "$COMMIT_TYPE" =~ ^(feat|fix|refactor|test|docs|chore)$ ]]; then
    echo -e "${RED}Error: Invalid commit type. Must be one of: feat, fix, refactor, test, docs, chore${NC}"
    exit 1
fi

# Prompt for scope
read -p "Scope (e.g., api, auth, services, db) [optional]: " SCOPE
SCOPE=$(echo "$SCOPE" | xargs)

# Prompt for description
read -p "Description: " DESCRIPTION
DESCRIPTION=$(echo "$DESCRIPTION" | xargs)

if [ -z "$DESCRIPTION" ]; then
    echo -e "${RED}Error: Description is required${NC}"
    exit 1
fi

# Prompt for Linear issue ID
read -p "Linear issue ID (e.g., AURA-123 or LIN-123): " ISSUE_ID
ISSUE_ID=$(echo "$ISSUE_ID" | tr '[:lower:]' '[:upper:]' | xargs)

if [ -z "$ISSUE_ID" ]; then
    echo -e "${YELLOW}Warning: No Linear issue ID provided${NC}"
    read -p "Continue without Linear ID? (y/N): " CONTINUE
    if [[ ! "$CONTINUE" =~ ^[Yy]$ ]]; then
        echo "Aborted"
        exit 0
    fi
    COMMIT_MSG="${COMMIT_TYPE}"
else
    # Normalize issue ID - ensure it has a prefix
    if [[ ! "$ISSUE_ID" =~ ^(AURA-|LIN-) ]]; then
        # Try to detect which prefix to use based on project
        if [[ "$CURRENT_BRANCH" =~ AURA- ]]; then
            ISSUE_ID="AURA-${ISSUE_ID}"
        else
            ISSUE_ID="LIN-${ISSUE_ID}"
        fi
    fi
    COMMIT_MSG="${COMMIT_TYPE}"
fi

# Build commit message
if [ -n "$SCOPE" ]; then
    COMMIT_MSG="${COMMIT_TYPE}(${SCOPE}): ${DESCRIPTION}"
else
    COMMIT_MSG="${COMMIT_TYPE}: ${DESCRIPTION}"
fi

if [ -n "$ISSUE_ID" ]; then
    COMMIT_MSG="${COMMIT_MSG} [${ISSUE_ID}]"
fi

echo ""
echo -e "${BLUE}Commit message:${NC} ${GREEN}${COMMIT_MSG}${NC}"
echo ""

# Confirm
read -p "Proceed with commit and push? (y/N): " CONFIRM
if [[ ! "$CONFIRM" =~ ^[Yy]$ ]]; then
    echo "Aborted"
    exit 0
fi

# Step 3: Stage changes
echo -e "\n${BLUE}Step 3: Staging changes...${NC}"
git add .
echo -e "${GREEN}✓ Changes staged${NC}"

# Step 4: Commit
echo -e "\n${BLUE}Step 4: Committing...${NC}"
git commit -m "$COMMIT_MSG"
echo -e "${GREEN}✓ Committed${NC}"

# Step 5: Push
echo -e "\n${BLUE}Step 5: Pushing to remote...${NC}"
git push origin "$CURRENT_BRANCH"
echo -e "${GREEN}✓ Pushed to origin/${CURRENT_BRANCH}${NC}"

echo ""
echo -e "${GREEN}=== Success! ===${NC}"
echo -e "${BLUE}Commit:${NC} ${COMMIT_MSG}"
echo -e "${BLUE}Branch:${NC} ${CURRENT_BRANCH}"
echo ""
echo -e "${YELLOW}Next steps:${NC}"
echo "  - Create PR: gh pr create --title \"${COMMIT_TYPE}: ${DESCRIPTION}\" --body \"Closes ${ISSUE_ID:-N/A}\""
echo "  - Or view on GitHub: gh browse"
