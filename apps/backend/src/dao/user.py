"""
User DAO

Data Access Object for user database operations.
"""

import time

from loguru import logger
from sqlmodel import select

from dao.base import BaseDAO
from db.database import AsyncSession
from db.models.user import User


class UserDAO(BaseDAO):
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
        start_time = time.time()
        logger.debug(
            "Executing database query: get_by_email",
            extra={
                "operation": "get_by_email",
                "model": "User",
                "email": email,
            },
        )

        try:
            stmt = select(User).where(User.email == email)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            duration = time.time() - start_time
            logger.debug(
                "Database query completed: get_by_email",
                extra={
                    "operation": "get_by_email",
                    "model": "User",
                    "email": email,
                    "found": user is not None,
                    "user_id": str(user.id) if user else None,
                    "duration_ms": duration * 1000,
                },
            )

            return user
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                "Database query failed: get_by_email",
                extra={
                    "operation": "get_by_email",
                    "model": "User",
                    "email": email,
                    "duration_ms": duration * 1000,
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
                exc_info=True,
            )
            raise

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
        start_time = time.time()
        logger.debug(
            "Executing database query: get_by_username",
            extra={
                "operation": "get_by_username",
                "model": "User",
                "username": username,
            },
        )

        try:
            stmt = select(User).where(User.username == username)
            result = await session.execute(stmt)
            user = result.scalar_one_or_none()

            duration = time.time() - start_time
            logger.debug(
                "Database query completed: get_by_username",
                extra={
                    "operation": "get_by_username",
                    "model": "User",
                    "username": username,
                    "found": user is not None,
                    "user_id": str(user.id) if user else None,
                    "duration_ms": duration * 1000,
                },
            )

            return user
        except Exception as e:
            duration = time.time() - start_time
            logger.error(
                "Database query failed: get_by_username",
                extra={
                    "operation": "get_by_username",
                    "model": "User",
                    "username": username,
                    "duration_ms": duration * 1000,
                    "error": str(e),
                    "error_type": type(e).__name__,
                },
                exc_info=True,
            )
            raise

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
