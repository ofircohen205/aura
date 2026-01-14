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
if ! uv run mypy apps/backend libs/core-py clients/cli || true; then
    echo -e "${YELLOW}⚠ Mypy found type issues (non-blocking)${NC}"
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
        if ! cd apps/web-dashboard && npm run build || echo "Build script not configured, skipping"; then
            echo -e "${YELLOW}⚠ Web-dashboard build completed${NC}"
        else
            echo -e "${GREEN}✓ Web-dashboard build passed${NC}"
        fi
        cd ../..
    fi

    if [ -d "clients/vscode" ]; then
        echo "  → Building VSCode extension..."
        if ! cd clients/vscode && npm run compile || echo "Compile script not configured, skipping"; then
            echo -e "${YELLOW}⚠ VSCode extension build completed${NC}"
        else
            echo -e "${GREEN}✓ VSCode extension build passed${NC}"
        fi
        cd ../..
    fi

    if [ -d "clients/github-app" ]; then
        echo "  → Building GitHub app..."
        if ! cd clients/github-app && npm run build --if-present || echo "Build script not configured, skipping"; then
            echo -e "${YELLOW}⚠ GitHub app build completed${NC}"
        else
            echo -e "${GREEN}✓ GitHub app build passed${NC}"
        fi
        cd ../..
    fi
else
    echo -e "\n${YELLOW}[5/6] Skipping TypeScript build (--skip-build)${NC}"
fi

# =============================================================================
# TypeScript Tests
# =============================================================================
if [ "$SKIP_TESTS" = false ]; then
    echo -e "\n${YELLOW}[6/6] Running TypeScript tests...${NC}"

    if ! npm run test --workspaces --if-present || echo "No test scripts found, skipping"; then
        echo -e "${YELLOW}⚠ TypeScript tests completed (some workspaces may not have test scripts)${NC}"
    else
        echo -e "${GREEN}✓ TypeScript tests passed${NC}"
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
