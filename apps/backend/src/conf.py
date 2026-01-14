"""
Project Configuration

Centralized path configuration and project root definition.
Use this for consistent path handling and imports.
"""

import sys
from pathlib import Path

# Project root: apps/backend directory
PROJECT_ROOT = Path(__file__).parent

# Source root: apps/backend/src directory
SRC_ROOT = PROJECT_ROOT

# Tests root: apps/backend/tests directory
TESTS_ROOT = PROJECT_ROOT.parent / "tests"

# Workspace root: aura/ directory (monorepo root)
WORKSPACE_ROOT = PROJECT_ROOT.parent.parent.parent

# Ensure src directory is on Python path for imports
if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))
