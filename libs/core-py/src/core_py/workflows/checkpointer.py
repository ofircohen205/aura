"""
Postgres Checkpointer for LangGraph Workflows

Provides async context manager for Postgres-based state persistence.
Handles connection pool lifecycle and error recovery.
"""
import os
import logging
from contextlib import asynccontextmanager
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg_pool import AsyncConnectionPool
from psycopg import OperationalError

logger = logging.getLogger(__name__)

# Get DB URI from environment or default to dev setting
DB_URI = os.getenv("POSTGRES_DB_URI", "postgresql+psycopg://aura:aura@localhost:5432/aura_db")

# Connection pool configuration
POOL_MAX_SIZE = int(os.getenv("POSTGRES_POOL_MAX_SIZE", "20"))
POOL_MIN_SIZE = int(os.getenv("POSTGRES_POOL_MIN_SIZE", "5"))

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
            }
        )
        
        async with AsyncConnectionPool(
            conninfo=DB_URI,
            max_size=POOL_MAX_SIZE,
            min_size=POOL_MIN_SIZE,
            kwargs={"autocommit": True}
        ) as pool:
            checkpointer = AsyncPostgresSaver(pool)
            logger.debug("Checkpointer pool created successfully")
            yield checkpointer
            
    except OperationalError as e:
        logger.error(
            "Database connection failed",
            extra={"error": str(e), "db_uri": DB_URI.split("@")[-1] if "@" in DB_URI else "hidden"}
        )
        raise
    except Exception as e:
        logger.error(
            "Checkpointer initialization failed",
            extra={"error": str(e), "error_type": type(e).__name__}
        )
        raise
