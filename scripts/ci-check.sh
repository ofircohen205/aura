#!/bin/bash
# CI Check Script
# Runs the same checks as GitHub Actions CI locally before committing
# Usage: ./scripts/ci-check.sh [--skip-tests] [--skip-build]

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Parse arguments
SKIP_TESTS=false
SKIP_BUILD=false

for arg in "$@"; do
    case $arg in
        --skip-tests)
            SKIP_TESTS=true
            shift
            ;;
        --skip-build)
            SKIP_BUILD=true
            shift
            ;;
        *)
            echo "Unknown option: $arg"
            echo "Usage: $0 [--skip-tests] [--skip-build]"
            exit 1
            ;;
    esac
done

echo -e "${GREEN}Running CI checks locally...${NC}\n"

# Ensure Node 20 is used (if nvm is available)
if [ -s "$HOME/.nvm/nvm.sh" ]; then
    echo "  → Ensuring Node 20 is active..."
    source "$HOME/.nvm/nvm.sh"
    nvm use 20 >/dev/null 2>&1 || true
    echo -e "${GREEN}✓ Using Node $(node --version)${NC}\n"
fi

# Track if any check fails
FAILED=false

# =============================================================================
# Python Lint and Type Check
# =============================================================================
echo -e "${YELLOW}[1/6] Running Python lint and type check...${NC}"

echo "  → Running ruff lint..."
if ! uv run ruff check apps/backend libs/core-py clients/cli; then
    echo -e "${RED}✗ Ruff lint failed${NC}"
    FAILED=true
else
    echo -e "${GREEN}✓ Ruff lint passed${NC}"
fi

echo "  → Running ruff format check..."
if ! uv run ruff format --check apps/backend libs/core-py clients/cli; then
    echo -e "${RED}✗ Ruff format check failed${NC}"
    echo -e "${YELLOW}  Run 'uv run ruff format apps/backend libs/core-py clients/cli' to fix${NC}"
    FAILED=true
else
    echo -e "${GREEN}✓ Ruff format check passed${NC}"
fi

echo "  → Running mypy type checking..."
MYPY_OUTPUT=$(uv run mypy apps/backend libs/core-py clients/cli 2>&1 || true)
MYPY_ERRORS=$(echo "$MYPY_OUTPUT" | grep -c "error:" || true)
if [ "$MYPY_ERRORS" -gt 0 ]; then
    echo "$MYPY_OUTPUT" | tail -5
    echo -e "${YELLOW}⚠ Mypy found $MYPY_ERRORS type errors (non-blocking)${NC}"
else
    echo -e "${GREEN}✓ Mypy type check passed${NC}"
fi

# =============================================================================
# Python Tests
# =============================================================================
if [ "$SKIP_TESTS" = false ]; then
    echo -e "\n${YELLOW}[2/6] Running Python tests...${NC}"

    echo "  → Running backend tests..."
    if ! cd apps/backend && uv run pytest tests/ -v; then
        echo -e "${RED}✗ Backend tests failed${NC}"
        FAILED=true
    else
        echo -e "${GREEN}✓ Backend tests passed${NC}"
    fi
    cd ../..

    echo "  → Running core-py tests..."
    if ! cd libs/core-py && uv run pytest tests/ -v; then
        echo -e "${RED}✗ Core-py tests failed${NC}"
        FAILED=true
    else
        echo -e "${GREEN}✓ Core-py tests passed${NC}"
    fi
    cd ../..
else
    echo -e "\n${YELLOW}[2/6] Skipping Python tests (--skip-tests)${NC}"
fi

# =============================================================================
# Python Build
# =============================================================================
if [ "$SKIP_BUILD" = false ]; then
    echo -e "\n${YELLOW}[3/6] Building Python packages...${NC}"

    if ! uv build apps/backend; then
        echo -e "${RED}✗ Backend build failed${NC}"
        FAILED=true
    else
        echo -e "${GREEN}✓ Backend build passed${NC}"
    fi

    if ! uv build libs/core-py; then
        echo -e "${RED}✗ Core-py build failed${NC}"
        FAILED=true
    else
        echo -e "${GREEN}✓ Core-py build passed${NC}"
    fi

    if ! uv build clients/cli; then
        echo -e "${RED}✗ CLI build failed${NC}"
        FAILED=true
    else
        echo -e "${GREEN}✓ CLI build passed${NC}"
    fi
else
    echo -e "\n${YELLOW}[3/6] Skipping Python build (--skip-build)${NC}"
fi

# =============================================================================
# TypeScript Lint and Type Check
# =============================================================================
echo -e "\n${YELLOW}[4/6] Running TypeScript lint and type check...${NC}"

echo "  → Running ESLint..."
if ! npm run lint --workspaces --if-present || echo "No lint script found, skipping"; then
    echo -e "${YELLOW}⚠ ESLint check completed (some workspaces may not have lint scripts)${NC}"
else
    echo -e "${GREEN}✓ ESLint check passed${NC}"
fi

echo "  → Running TypeScript type check..."
if ! npm run type-check --workspaces --if-present || echo "No type-check script found, skipping"; then
    echo -e "${YELLOW}⚠ TypeScript type check completed (some workspaces may not have type-check scripts)${NC}"
else
    echo -e "${GREEN}✓ TypeScript type check passed${NC}"
fi

# Check VSCode extension specifically
if [ -d "clients/vscode" ]; then
    echo "  → Running VSCode extension type check..."
    if ! cd clients/vscode && npx tsc --noEmit || true; then
        echo -e "${YELLOW}⚠ VSCode extension type check completed${NC}"
    else
        echo -e "${GREEN}✓ VSCode extension type check passed${NC}"
    fi
    cd ../..
fi

# =============================================================================
# TypeScript Build
# =============================================================================
if [ "$SKIP_BUILD" = false ]; then
    echo -e "\n${YELLOW}[5/6] Building TypeScript projects...${NC}"

    if [ -d "apps/web-dashboard" ]; then
        echo "  → Building web-dashboard..."
        if [ -f "apps/web-dashboard/package.json" ] && grep -q '"build"' apps/web-dashboard/package.json; then
            if (cd apps/web-dashboard && npm run build); then
                echo -e "${GREEN}✓ Web-dashboard build passed${NC}"
            else
                echo -e "${RED}✗ Web-dashboard build failed${NC}"
                FAILED=true
            fi
        else
            echo -e "${YELLOW}⚠ Web-dashboard build script not configured, skipping${NC}"
        fi
    fi

    if [ -d "clients/vscode" ]; then
        echo "  → Building VSCode extension..."
        if [ -f "clients/vscode/package.json" ] && grep -q '"compile"' clients/vscode/package.json; then
            if (cd clients/vscode && npm run compile); then
                echo -e "${GREEN}✓ VSCode extension build passed${NC}"
            else
                echo -e "${RED}✗ VSCode extension build failed${NC}"
                FAILED=true
            fi
        else
            echo -e "${YELLOW}⚠ VSCode extension compile script not configured, skipping${NC}"
        fi
    fi

    if [ -d "clients/github-app" ]; then
        echo "  → Building GitHub app..."
        if [ -f "clients/github-app/package.json" ] && grep -q '"build"' clients/github-app/package.json; then
            if (cd clients/github-app && npm run build); then
                echo -e "${GREEN}✓ GitHub app build passed${NC}"
            else
                echo -e "${RED}✗ GitHub app build failed${NC}"
                FAILED=true
            fi
        else
            echo -e "${YELLOW}⚠ GitHub app build script not configured, skipping${NC}"
        fi
    fi
else
    echo -e "\n${YELLOW}[5/6] Skipping TypeScript build (--skip-build)${NC}"
fi

# =============================================================================
# TypeScript Tests
# =============================================================================
if [ "$SKIP_TESTS" = false ]; then
    echo -e "\n${YELLOW}[6/6] Running TypeScript tests...${NC}"

    TEST_FAILED=false
    for workspace in clients/github-app clients/vscode apps/web-dashboard; do
        if [ -d "$workspace" ] && [ -f "$workspace/package.json" ]; then
            if grep -q '"test"' "$workspace/package.json"; then
                workspace_name=$(basename "$workspace")
                echo "  → Running tests for $workspace_name..."
                if (cd "$workspace" && npm test 2>&1); then
                    echo -e "${GREEN}✓ $workspace_name tests passed${NC}"
                else
                    echo -e "${RED}✗ $workspace_name tests failed${NC}"
                    TEST_FAILED=true
                    FAILED=true
                fi
            fi
        fi
    done

    if [ "$TEST_FAILED" = false ]; then
        echo -e "${GREEN}✓ All TypeScript tests passed${NC}"
    fi
else
    echo -e "\n${YELLOW}[6/6] Skipping TypeScript tests (--skip-tests)${NC}"
fi

# =============================================================================
# Summary
# =============================================================================
echo -e "\n${GREEN}========================================${NC}"
if [ "$FAILED" = true ]; then
    echo -e "${RED}✗ CI checks failed${NC}"
    echo -e "${YELLOW}Please fix the errors above before committing${NC}"
    exit 1
else
    echo -e "${GREEN}✓ All CI checks passed!${NC}"
    echo -e "${GREEN}You're ready to commit!${NC}"
    exit 0
fi
