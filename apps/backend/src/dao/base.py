"""
Base DAO

Abstract base class for Data Access Objects.
Provides common CRUD operations for SQLModel entities.
"""

import time
from typing import TypeVar
from uuid import UUID

from loguru import logger
from sqlmodel import SQLModel, func, select

from db.database import AsyncSession

# Type variables for generic DAO
TModel = TypeVar("TModel", bound=SQLModel)


class BaseDAO:
    """
    Base Data Access Object for database operations.

    Provides common CRUD operations that can be inherited by specific DAOs.
    Each model should have its own DAO class that inherits from this base class.

    Args:
        model: SQLModel class for this DAO

    Example:
        ```python
        class UserDAO(BaseDAO):
            async def get_by_email(self, session: AsyncSession, email: str) -> User | None:
                stmt = select(User).where(User.email == email)
                result = await session.execute(stmt)
                return result.scalar_one_or_none()

        user_dao = UserDAO(User)
        ```
    """

    def __init__(self, model: type[TModel]) -> None:
        """
        Initialize DAO with a model class.

        Args:
            model: SQLModel class for this DAO
        """
        self.model = model

    async def get_by_id(
        self,
        session: AsyncSession,
        entity_id: UUID,
    ) -> TModel | None:
        """
        Get an entity by its ID.

        Args:
            session: Database session
            entity_id: Entity ID

        Returns:
            Entity object or None if not found
        """
        start_time = time.time()
        logger.debug(
            "Executing database query: get_by_id",
            extra={
                "operation": "get_by_id",
                "model": self.model.__name__,
                "entity_id": str(entity_id),
            },
        )

        try:
            stmt = select(self.model).where(self.model.id == entity_id)  # type: ignore[attr-defined]
            result = await session.execute(stmt)
            entity = result.scalar_one_or_none()

            duration = time.time() - start_time
            logger.debug(
                "Database query completed: get_by_id",
                extra={
                    "operation": "get_by_id",
                    "model": self.model.__name__,
                    "entity_id": str(entity_id),
                    "found": entity is not None,
                    "duration_ms": duration * 1000,
                },
            )

            return entity
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                "Database query failed: get_by_id",
                extra={
                    "operation": "get_by_id",
                    "model": self.model.__name__,
                    "entity_id": str(entity_id),
                    "duration_ms": duration * 1000,
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
                exc_info=True,
            )
            raise

    async def create(
        self,
        session: AsyncSession,
        entity: TModel,
    ) -> TModel:
        """
        Create a new entity.

        Args:
            session: Database session
            entity: Entity object to create

        Returns:
            Created entity object
        """
        start_time = time.time()
        entity_id = getattr(entity, "id", None)
        logger.debug(
            "Executing database query: create",
            extra={
                "operation": "create",
                "model": self.model.__name__,
                "entity_id": str(entity_id) if entity_id else None,
            },
        )

        try:
            session.add(entity)
            await session.commit()
            await session.refresh(entity)

            duration = time.time() - start_time
            entity_id = getattr(entity, "id", None)
            logger.info(
                "Database query completed: create",
                extra={
                    "operation": "create",
                    "model": self.model.__name__,
                    "entity_id": str(entity_id) if entity_id else None,
                    "duration_ms": duration * 1000,
                },
            )

            return entity
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                "Database query failed: create",
                extra={
                    "operation": "create",
                    "model": self.model.__name__,
                    "duration_ms": duration * 1000,
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
                exc_info=True,
            )
            raise

    async def update(
        self,
        session: AsyncSession,
        entity: TModel,
    ) -> TModel:
        """
        Update an existing entity.

        Args:
            session: Database session
            entity: Entity object to update (must be attached to session)

        Returns:
            Updated entity object
        """
        start_time = time.time()
        entity_id = getattr(entity, "id", None)
        logger.debug(
            "Executing database query: update",
            extra={
                "operation": "update",
                "model": self.model.__name__,
                "entity_id": str(entity_id) if entity_id else None,
            },
        )

        try:
            await session.commit()
            await session.refresh(entity)

            duration = time.time() - start_time
            logger.info(
                "Database query completed: update",
                extra={
                    "operation": "update",
                    "model": self.model.__name__,
                    "entity_id": str(entity_id) if entity_id else None,
                    "duration_ms": duration * 1000,
                },
            )

            return entity
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                "Database query failed: update",
                extra={
                    "operation": "update",
                    "model": self.model.__name__,
                    "entity_id": str(entity_id) if entity_id else None,
                    "duration_ms": duration * 1000,
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
                exc_info=True,
            )
            raise

    async def delete(
        self,
        session: AsyncSession,
        entity: TModel,
    ) -> None:
        """
        Delete an entity.

        Args:
            session: Database session
            entity: Entity object to delete
        """
        start_time = time.time()
        entity_id = getattr(entity, "id", None)
        logger.debug(
            "Executing database query: delete",
            extra={
                "operation": "delete",
                "model": self.model.__name__,
                "entity_id": str(entity_id) if entity_id else None,
            },
        )

        try:
            await session.delete(entity)
            await session.commit()

            duration = time.time() - start_time
            logger.info(
                "Database query completed: delete",
                extra={
                    "operation": "delete",
                    "model": self.model.__name__,
                    "entity_id": str(entity_id) if entity_id else None,
                    "duration_ms": duration * 1000,
                },
            )
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                "Database query failed: delete",
                extra={
                    "operation": "delete",
                    "model": self.model.__name__,
                    "entity_id": str(entity_id) if entity_id else None,
                    "duration_ms": duration * 1000,
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
                exc_info=True,
            )
            raise

    async def get_all(
        self,
        session: AsyncSession,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[TModel]:
        """
        Get all entities with optional pagination.

        Args:
            session: Database session
            limit: Maximum number of entities to return
            offset: Number of entities to skip

        Returns:
            List of entities
        """
        start_time = time.time()
        logger.debug(
            "Executing database query: get_all",
            extra={
                "operation": "get_all",
                "model": self.model.__name__,
                "limit": limit,
                "offset": offset,
            },
        )

        try:
            stmt = select(self.model)
            if limit:
                stmt = stmt.limit(limit).offset(offset)
            result = await session.execute(stmt)
            entities = list(result.scalars().all())

            duration = time.time() - start_time
            logger.debug(
                "Database query completed: get_all",
                extra={
                    "operation": "get_all",
                    "model": self.model.__name__,
                    "limit": limit,
                    "offset": offset,
                    "count": len(entities),
                    "duration_ms": duration * 1000,
                },
            )

            return entities  # type: ignore[return-value]
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                "Database query failed: get_all",
                extra={
                    "operation": "get_all",
                    "model": self.model.__name__,
                    "limit": limit,
                    "offset": offset,
                    "duration_ms": duration * 1000,
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
                exc_info=True,
            )
            raise

    async def count(self, session: AsyncSession) -> int:
        """
        Count total number of entities.

        Args:
            session: Database session

        Returns:
            Total count of entities
        """
        start_time = time.time()
        logger.debug(
            "Executing database query: count",
            extra={
                "operation": "count",
                "model": self.model.__name__,
            },
        )

        try:
            stmt = select(func.count()).select_from(self.model)  # type: ignore[arg-type]
            result = await session.execute(stmt)
            count = result.scalar_one() or 0

            duration = time.time() - start_time
            logger.debug(
                "Database query completed: count",
                extra={
                    "operation": "count",
                    "model": self.model.__name__,
                    "count": count,
                    "duration_ms": duration * 1000,
                },
            )

            return count
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                "Database query failed: count",
                extra={
                    "operation": "count",
                    "model": self.model.__name__,
                    "duration_ms": duration * 1000,
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
                exc_info=True,
            )
            raise
