"""
Postgres Checkpointer for LangGraph Workflows

Provides async context manager for Postgres-based state persistence.
Handles connection pool lifecycle and error recovery.
"""

import logging
import os
from contextlib import asynccontextmanager

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg import OperationalError
from psycopg_pool import AsyncConnectionPool

logger = logging.getLogger(__name__)

# Get DB URI from environment or default to dev setting
# WARNING: Default credentials are for local development only
# In production, always set POSTGRES_DB_URI via environment variable
DB_URI = os.getenv("POSTGRES_DB_URI", "postgresql+psycopg://aura:aura@localhost:5432/aura_db")

# Connection pool configuration
POOL_MAX_SIZE = int(os.getenv("POSTGRES_POOL_MAX_SIZE", "20"))
POOL_MIN_SIZE = int(os.getenv("POSTGRES_POOL_MIN_SIZE", "5"))


def _normalize_connection_string(uri: str) -> str:
    """
    Convert SQLAlchemy-style connection string to standard PostgreSQL format.

    psycopg_pool.AsyncConnectionPool expects standard PostgreSQL format (postgresql://),
    not SQLAlchemy-style format (postgresql+psycopg://).

    Args:
        uri: Connection string, possibly with SQLAlchemy-style prefix

    Returns:
        Normalized connection string in standard PostgreSQL format
    """
    # Convert postgresql+psycopg:// to postgresql://
    if uri.startswith("postgresql+psycopg://"):
        return uri.replace("postgresql+psycopg://", "postgresql://", 1)
    # Already in standard format or other format, return as-is
    return uri


@asynccontextmanager
async def get_checkpointer():
    """
    Context manager that provides an AsyncPostgresSaver.
    Manages the connection pool lifecycle with error handling.

    Yields:
        AsyncPostgresSaver: Checkpointer instance for workflow state persistence

    Raises:
        OperationalError: If database connection fails
        Exception: For other connection pool errors

    Note:
        Assumes tables are created via Flyway migrations.
        Does not call setup() to avoid schema conflicts.
    """
    try:
        logger.debug(
            "Creating checkpointer connection pool",
            extra={
                "max_size": POOL_MAX_SIZE,
                "min_size": POOL_MIN_SIZE,
            },
        )

        # Normalize connection string for psycopg (convert postgresql+psycopg:// to postgresql://)
        normalized_uri = _normalize_connection_string(DB_URI)

        async with AsyncConnectionPool(
            conninfo=normalized_uri,
            max_size=POOL_MAX_SIZE,
            min_size=POOL_MIN_SIZE,
            kwargs={"autocommit": True},
        ) as pool:
            checkpointer = AsyncPostgresSaver(pool)
            logger.debug("Checkpointer pool created successfully")
            yield checkpointer

    except OperationalError as e:
        logger.error(
            "Database connection failed",
            extra={"error": str(e), "db_uri": DB_URI.split("@")[-1] if "@" in DB_URI else "hidden"},
        )
        raise
    except Exception as e:
        logger.error(
            "Checkpointer initialization failed",
            extra={"error": str(e), "error_type": type(e).__name__},
        )
        raise
