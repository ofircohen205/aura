"""
User DAO

Data Access Object for user database operations.
"""

from sqlalchemy.ext.asyncio import AsyncSession
from sqlmodel import select

from dao.base import BaseDAO
from db.models.user import User


class UserDAO(BaseDAO[User]):
    """
    Data Access Object for User model.

    Provides database operations for user management.
    Inherits common CRUD operations from BaseDAO and adds user-specific queries.
    """

    async def get_by_email(
        self,
        session: AsyncSession,
        email: str,
    ) -> User | None:
        """
        Get a user by email address.

        Args:
            session: Database session
            email: User email address

        Returns:
            User object or None if not found
        """
        stmt = select(User).where(User.email == email)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_username(
        self,
        session: AsyncSession,
        username: str,
    ) -> User | None:
        """
        Get a user by username.

        Args:
            session: Database session
            username: Username

        Returns:
            User object or None if not found
        """
        stmt = select(User).where(User.username == username)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def exists_by_email(
        self,
        session: AsyncSession,
        email: str,
    ) -> bool:
        """
        Check if a user exists with the given email.

        Args:
            session: Database session
            email: Email address to check

        Returns:
            True if user exists, False otherwise
        """
        user = await self.get_by_email(session, email)
        return user is not None

    async def exists_by_username(
        self,
        session: AsyncSession,
        username: str,
    ) -> bool:
        """
        Check if a user exists with the given username.

        Args:
            session: Database session
            username: Username to check

        Returns:
            True if user exists, False otherwise
        """
        user = await self.get_by_username(session, username)
        return user is not None


# Global DAO instance
user_dao = UserDAO(User)
