"""
Base DAO

Abstract base class for Data Access Objects.
Provides common CRUD operations for SQLModel entities.
"""

from typing import Generic, TypeVar
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import SQLModel

# Type variables for generic DAO
TModel = TypeVar("TModel", bound=SQLModel)


class BaseDAO(Generic[TModel]):
    """
    Base Data Access Object for database operations.

    Provides common CRUD operations that can be inherited by specific DAOs.
    Each model should have its own DAO class that inherits from this base class.

    Args:
        model: SQLModel class for this DAO

    Example:
        ```python
        class UserDAO(BaseDAO[User]):
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
        stmt = select(self.model).where(self.model.id == entity_id)  # type: ignore[attr-defined]
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

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
        session.add(entity)
        await session.commit()
        await session.refresh(entity)
        return entity

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
        await session.commit()
        await session.refresh(entity)
        return entity

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
        await session.delete(entity)
        await session.commit()

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
        stmt = select(self.model)
        if limit:
            stmt = stmt.limit(limit).offset(offset)
        result = await session.execute(stmt)
        return list(result.scalars().all())
