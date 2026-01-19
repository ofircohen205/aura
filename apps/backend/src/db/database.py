"""
Database Connection Management

Provides async database connection pool and session handling for SQLModel.
Includes FastAPI dependency for dependency injection.
"""

from collections.abc import AsyncGenerator

from fastapi import Depends
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession as _AsyncSession
from sqlalchemy.ext.asyncio import create_async_engine
from sqlmodel import SQLModel, create_engine  # noqa: F401

from core.config import get_settings

# Re-export AsyncSession for centralized imports
AsyncSession = _AsyncSession

settings = get_settings()

# Convert postgresql+psycopg:// to postgresql+asyncpg:// for async engine
# Also handle case where URI is already in asyncpg format
if "postgresql+psycopg://" in settings.postgres_db_uri:
    async_db_uri = settings.postgres_db_uri.replace(
        "postgresql+psycopg://", "postgresql+asyncpg://"
    )
elif "postgresql+asyncpg://" not in settings.postgres_db_uri:
    # If neither format is present, assume psycopg and convert
    async_db_uri = settings.postgres_db_uri.replace("postgresql://", "postgresql+asyncpg://")
else:
    async_db_uri = settings.postgres_db_uri

# Create async engine
# Note: SQLModel's create_engine is for synchronous engines.
# For async operations, we use create_async_engine from SQLAlchemy.
# See: https://sqlmodel.tiangolo.com/tutorial/create-db-and-table/
async_engine = create_async_engine(
    async_db_uri,
    echo=settings.log_level == "DEBUG",
    pool_size=settings.postgres_pool_max_size,
    max_overflow=0,
    pool_pre_ping=True,  # Verify connections before using
)


async def get_session() -> AsyncGenerator[_AsyncSession]:
    """
    Dependency for getting async database session.

    Yields:
        AsyncSession: Database session for the request

    Example:
        ```python
        @router.get("/items")
        async def get_items(session: AsyncSession = Depends(get_session)):
            # Use session here
            pass
        ```
    """
    async with _AsyncSession(async_engine) as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            logger.error("Database session rollback due to error", exc_info=True)
            raise
        # Context manager handles session.close() automatically


# FastAPI dependency alias
SessionDep = Depends(get_session)

# Re-export for type hints
__all__ = ["AsyncSession", "SessionDep", "get_session", "async_engine", "init_db", "close_db"]


async def init_db() -> None:
    """
    Initialize database tables (development only).

    Creates all tables defined in SQLModel models.
    In production, use migrations instead of this function.
    """
    from core.config import get_settings

    settings = get_settings()

    # Only auto-create tables in local/development environment
    if settings.environment.value == "local":
        logger.info("Initializing database tables (dev mode)")
        async with async_engine.begin() as conn:
            await conn.run_sync(SQLModel.metadata.create_all)
        logger.info("Database tables initialized")
    else:
        logger.info("Skipping database table initialization (use migrations in production)")


async def close_db() -> None:
    """
    Close database connections.

    Should be called on application shutdown.
    """
    logger.info("Closing database connections")
    await async_engine.dispose()
    logger.info("Database connections closed")
