"""
Pytest configuration and fixtures for backend tests.
"""

import os

# Disable rate limiting for all tests
os.environ["RATE_LIMIT_ENABLED"] = "false"
os.environ["RATE_LIMIT_REDIS_ENABLED"] = "false"
