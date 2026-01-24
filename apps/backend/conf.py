"""
Project Configuration

Centralized path configuration and project root definition.
Use this for consistent path handling and imports.
"""

import os
import sys

# Project root: apps/backend directory
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))

# Source root: apps/backend/src directory
SRC_ROOT = os.path.join(PROJECT_ROOT, "src")


# Ensure src directory is on Python path for imports
if SRC_ROOT not in sys.path:
    sys.path.insert(0, SRC_ROOT)
