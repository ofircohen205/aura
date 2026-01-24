"""
Authentication Service

Business logic for user authentication, authorization, and user management.
"""

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING, Any
from uuid import UUID

from loguru import logger

from core.config import get_settings
from core.security import (
    create_jwt_token,
    create_refresh_token,
    hash_password,
    verify_password,
)
from dao.user import user_dao
from db.database import AsyncSession
from db.models.user import User
from services.auth.cache import UserCache, cache_user, invalidate_user_cache
from services.auth.exceptions import (
    InactiveUserError,
    InvalidCredentialsError,
    RefreshTokenNotFoundError,
    UserAlreadyExistsError,
)
from services.redis import get_redis_client_manager

if TYPE_CHECKING:
    from redis.asyncio import Redis  # type: ignore[import-untyped]

settings = get_settings()


class AuthService:
    """Service for managing authentication and user operations."""

    async def register_user(
        self,
        session: AsyncSession,
        email: str,
        username: str,
        password: str,
    ) -> User:
        """
        Register a new user.

        Args:
            session: Database session
            email: User email address
            username: Username
            password: Plain text password

        Returns:
            Created User object

        Raises:
            UserAlreadyExistsError: If user with email or username already exists
        """
        if await user_dao.exists_by_email(session, email):
            raise UserAlreadyExistsError(email=email)

        if await user_dao.exists_by_username(session, username):
            raise UserAlreadyExistsError(username=username)

        hashed_password = hash_password(password)

        user = User(
            email=email,
            username=username,
            hashed_password=hashed_password,
            is_active=True,
            is_verified=False,
            roles=["user"],
        )

        user = await user_dao.create(session, user)

        logger.info(
            "User registered",
            extra={"user_id": str(user.id), "email": email, "username": username},
        )

        return user

    async def authenticate_user(
        self,
        session: AsyncSession,
        email: str,
        password: str,
    ) -> User:
        """
        Authenticate a user with email and password.

        Args:
            session: Database session
            email: User email address
            password: Plain text password

        Returns:
            Authenticated User object

        Raises:
            InvalidCredentialsError: If credentials are invalid
            InactiveUserError: If user account is inactive
        """
        user = await user_dao.get_by_email(session, email)
        if not user:
            logger.warning("Authentication failed: user not found", extra={"email": email})
            raise InvalidCredentialsError()

        if not verify_password(password, user.hashed_password):
            logger.warning(
                "Authentication failed: invalid password",
                extra={"user_id": str(user.id), "email": email},
            )
            raise InvalidCredentialsError()

        if not user.is_active:
            logger.warning(
                "Authentication failed: inactive user",
                extra={"user_id": str(user.id), "email": email},
            )
            raise InactiveUserError()

        user_cache = UserCache(
            id=str(user.id),
            email=user.email,
            username=user.username,
            is_active=user.is_active,
            is_verified=user.is_verified,
            roles=user.roles,
        )
        await cache_user(user.id, user_cache)

        logger.info("User authenticated", extra={"user_id": str(user.id), "email": email})

        return user

    async def create_access_token(self, user: User) -> str:
        """
        Create a JWT access token for a user.

        Args:
            user: User object

        Returns:
            JWT access token string
        """
        if not settings.jwt_secret_key:
            raise ValueError("JWT_SECRET_KEY must be set in environment variables")

        expires_delta = timedelta(minutes=settings.jwt_access_token_expire_minutes)
        payload = {
            "sub": str(user.id),  # Subject (user ID)
            "email": user.email,
            "username": user.username,
            "roles": user.roles,
        }

        token = create_jwt_token(
            payload=payload,
            secret_key=settings.jwt_secret_key,
            expires_delta=expires_delta,
            algorithm=settings.jwt_algorithm,
        )

        return token

    async def create_refresh_token_record(
        self,
        user: User,
    ) -> str:
        """
        Create and store a refresh token for a user in Redis.

        Args:
            user: User object

        Returns:
            Refresh token string
        """
        # Generate refresh token
        token = create_refresh_token()
        expires_in_seconds = settings.jwt_refresh_token_expire_days * 24 * 60 * 60

        manager = get_redis_client_manager()
        redis_client = await manager.get_client()
        if redis_client:
            try:
                redis_key = f"refresh_token:{token}"
                await redis_client.setex(
                    redis_key,
                    expires_in_seconds,
                    str(user.id),
                )
                logger.info(
                    "Refresh token created in Redis",
                    extra={"user_id": str(user.id), "token": token[:10] + "..."},
                )
            except Exception as e:
                error_msg = str(e).lower()
                if any(
                    phrase in error_msg
                    for phrase in [
                        "event loop is closed",
                        "no running event loop",
                        "loop is closed",
                        "got future attached to a different loop",
                    ]
                ):
                    logger.warning(
                        f"Failed to store refresh token in Redis due to event loop issue: {e}"
                    )
                    raise RuntimeError("Redis operation failed due to event loop issue") from e
                logger.error(f"Failed to store refresh token in Redis: {e}", exc_info=True)
                raise
        else:
            logger.warning("Redis not available, refresh token not stored")
            raise RuntimeError("Redis is not available for storing refresh tokens")

        return token

    async def _get_user_id_from_refresh_token(
        self, refresh_token_str: str, redis_client: "Redis[str]"
    ) -> UUID:
        """
        Extract and validate user ID from refresh token in Redis.

        Args:
            refresh_token_str: Refresh token string
            redis_client: Redis client instance

        Returns:
            User ID from refresh token

        Raises:
            RefreshTokenNotFoundError: If token not found or invalid
        """
        redis_key = f"refresh_token:{refresh_token_str}"
        user_id_str = await redis_client.get(redis_key)

        if not user_id_str:
            logger.warning(
                "Refresh token not found in Redis", extra={"token": refresh_token_str[:10]}
            )
            raise RefreshTokenNotFoundError()

        try:
            return UUID(user_id_str)
        except ValueError as e:
            logger.error("Invalid user ID in refresh token", extra={"user_id": user_id_str})
            raise RefreshTokenNotFoundError() from e

    async def _validate_user_for_token_refresh(
        self,
        session: AsyncSession,
        user_id: UUID,
        refresh_token_str: str,
        redis_client: "Redis[str]",
    ) -> User:
        """
        Validate user exists and is active for token refresh.

        Args:
            session: Database session
            user_id: User ID to validate
            refresh_token_str: Refresh token string (for cleanup)
            redis_client: Redis client instance

        Returns:
            Validated User object

        Raises:
            RefreshTokenNotFoundError: If user not found
            InactiveUserError: If user is inactive
        """
        user: User | None = await user_dao.get_by_id(session, user_id)
        redis_key = f"refresh_token:{refresh_token_str}"

        if not user:
            logger.error("User not found for refresh token", extra={"user_id": str(user_id)})
            await redis_client.delete(redis_key)
            raise RefreshTokenNotFoundError()

        if not user.is_active:
            logger.warning("Inactive user attempted token refresh", extra={"user_id": str(user.id)})
            await redis_client.delete(redis_key)
            raise InactiveUserError()

        return user

    async def refresh_access_token(
        self,
        session: AsyncSession,
        refresh_token_str: str,
    ) -> tuple[str, str]:
        """
        Refresh an access token using a refresh token from Redis.

        Args:
            session: Database session
            refresh_token_str: Refresh token string

        Returns:
            Tuple of (new_access_token, refresh_token_string)

        Raises:
            RefreshTokenNotFoundError: If refresh token is not found or expired
        """
        manager = get_redis_client_manager()
        redis_client: Redis[str] | None = await manager.get_client()
        if not redis_client:
            logger.error("Redis not available for refresh token validation")
            raise RefreshTokenNotFoundError()

        try:
            user_id = await self._get_user_id_from_refresh_token(refresh_token_str, redis_client)

            user = await self._validate_user_for_token_refresh(
                session, user_id, refresh_token_str, redis_client
            )

            access_token = await self.create_access_token(user)

            logger.info("Access token refreshed", extra={"user_id": str(user.id)})

            return access_token, refresh_token_str

        except (RefreshTokenNotFoundError, InactiveUserError):
            raise
        except Exception as e:
            logger.error(f"Error refreshing access token: {e}", exc_info=True)
            raise RefreshTokenNotFoundError() from e

    async def revoke_refresh_token(
        self,
        refresh_token_str: str,
    ) -> None:
        """
        Revoke (delete) a refresh token from Redis (logout).

        Args:
            refresh_token_str: Refresh token string to revoke
        """
        manager = get_redis_client_manager()
        redis_client = await manager.get_client()
        if not redis_client:
            logger.warning("Redis not available, cannot revoke refresh token")
            return

        try:
            redis_key = f"refresh_token:{refresh_token_str}"
            deleted = await redis_client.delete(redis_key)

            if deleted:
                logger.info(
                    "Refresh token revoked from Redis",
                    extra={"token": refresh_token_str[:10] + "..."},
                )
            else:
                logger.warning(
                    "Refresh token not found in Redis for revocation",
                    extra={"token": refresh_token_str[:10] + "..."},
                )
        except Exception as e:
            logger.error(f"Error revoking refresh token: {e}", exc_info=True)

    async def update_user(
        self,
        session: AsyncSession,
        user: User,
        username: str | None = None,
        email: str | None = None,
    ) -> User:
        """
        Update user profile.

        Args:
            session: Database session
            user: User object to update
            username: New username (optional)
            email: New email (optional)

        Returns:
            Updated User object

        Raises:
            UserAlreadyExistsError: If new email or username already exists
        """
        if username and username != user.username:
            existing_user = await user_dao.get_by_username(session, username)
            if existing_user and existing_user.id != user.id:
                raise UserAlreadyExistsError(username=username)
            user.username = username

        if email and email != user.email:
            existing_user = await user_dao.get_by_email(session, email)
            if existing_user and existing_user.id != user.id:
                raise UserAlreadyExistsError(email=email)
            user.email = email

        user.updated_at = datetime.now(UTC)
        user = await user_dao.update(session, user)

        await invalidate_user_cache(user.id)

        logger.info("User updated", extra={"user_id": str(user.id)})

        return user

    async def assign_role(
        self,
        session: AsyncSession,
        user: User,
        role: str,
    ) -> User:
        """
        Assign a role to a user.

        Args:
            session: Database session
            user: User object
            role: Role to assign

        Returns:
            Updated User object
        """
        if role not in user.roles:
            user.roles.append(role)
            user.updated_at = datetime.now(UTC)
            user = await user_dao.update(session, user)

            logger.info(
                "Role assigned to user",
                extra={"user_id": str(user.id), "role": role},
            )

        return user

    def check_permission(self, user: User, permission: str) -> bool:
        """
        Check if a user has a specific permission.

        Args:
            user: User object
            permission: Permission to check

        Returns:
            True if user has permission, False otherwise

        Note:
            This is a placeholder for future permission system implementation.
            Currently checks roles only.
        """
        if permission == "admin":
            return "admin" in user.roles

        return True

    async def bulk_create_users(
        self,
        session: AsyncSession,
        users_data: list[dict[str, str]],
    ) -> tuple[list[User], list[dict[str, str | int]]]:
        """
        Create multiple users in bulk.

        Args:
            session: Database session
            users_data: List of user data dicts with email, username, password

        Returns:
            Tuple of (created users list, errors list)
        """
        created_users: list[User] = []
        errors: list[dict[str, Any]] = []

        for idx, user_data in enumerate(users_data):
            try:
                user = await self.register_user(
                    session=session,
                    email=user_data["email"],
                    username=user_data["username"],
                    password=user_data["password"],
                )
                created_users.append(user)
            except Exception as e:
                errors.append(
                    {
                        "index": idx,
                        "email": user_data.get("email", "unknown"),
                        "error": str(e),
                    }
                )
                logger.warning(
                    "Bulk user creation failed",
                    extra={"index": idx, "email": user_data.get("email"), "error": str(e)},
                )

        logger.info(
            "Bulk user creation completed",
            extra={"success_count": len(created_users), "error_count": len(errors)},
        )

        return created_users, errors

    async def bulk_update_users(
        self,
        session: AsyncSession,
        updates: list[dict[str, Any]],
    ) -> tuple[list[User], list[dict[str, str | int]]]:
        """
        Update multiple users in bulk.

        Args:
            session: Database session
            updates: List of update dicts with 'id' and optional 'username', 'email'

        Returns:
            Tuple of (updated users list, errors list)
        """
        updated_users: list[User] = []
        errors: list[dict[str, Any]] = []

        for idx, update_data in enumerate(updates):
            try:
                user_id = UUID(update_data["id"])
                user: User | None = await user_dao.get_by_id(session, user_id)
                if not user:
                    errors.append(
                        {
                            "index": idx,
                            "user_id": str(user_id),
                            "error": "User not found",
                        }
                    )
                    continue

                updated_user = await self.update_user(
                    session=session,
                    user=user,
                    username=update_data.get("username"),
                    email=update_data.get("email"),
                )
                updated_users.append(updated_user)
            except Exception as e:
                errors.append(
                    {
                        "index": idx,
                        "user_id": str(update_data.get("id", "unknown")),
                        "error": str(e),
                    }
                )
                logger.warning(
                    "Bulk user update failed",
                    extra={"index": idx, "user_id": update_data.get("id"), "error": str(e)},
                )

        logger.info(
            "Bulk user update completed",
            extra={"success_count": len(updated_users), "error_count": len(errors)},
        )

        return updated_users, errors

    async def bulk_delete_users(
        self,
        session: AsyncSession,
        user_ids: list[UUID],
    ) -> tuple[int, list[dict[str, str | int]]]:
        """
        Delete multiple users in bulk.

        Args:
            session: Database session
            user_ids: List of user IDs to delete

        Returns:
            Tuple of (deleted count, errors list)
        """
        deleted_count = 0
        errors: list[dict[str, Any]] = []

        for idx, user_id in enumerate(user_ids):
            try:
                user: User | None = await user_dao.get_by_id(session, user_id)
                if not user:
                    errors.append(
                        {
                            "index": idx,
                            "user_id": str(user_id),
                            "error": "User not found",
                        }
                    )
                    continue

                await user_dao.delete(session, user)
                deleted_count += 1
                logger.info("User deleted in bulk operation", extra={"user_id": str(user_id)})
            except Exception as e:
                errors.append(
                    {
                        "index": idx,
                        "user_id": str(user_id),
                        "error": str(e),
                    }
                )
                logger.warning(
                    "Bulk user deletion failed",
                    extra={"index": idx, "user_id": str(user_id), "error": str(e)},
                )

        logger.info(
            "Bulk user deletion completed",
            extra={"deleted_count": deleted_count, "error_count": len(errors)},
        )

        return deleted_count, errors


auth_service = AuthService()
