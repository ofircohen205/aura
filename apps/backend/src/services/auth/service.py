"""
Authentication Service

Business logic for user authentication, authorization, and user management.
"""

from datetime import UTC, datetime, timedelta
from uuid import UUID

from loguru import logger
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import get_settings
from core.security import (
    create_jwt_token,
    create_refresh_token,
    hash_password,
    is_token_expired,
    verify_password,
)
from db.models.user import RefreshToken, User
from services.auth.exceptions import (
    InactiveUserError,
    InvalidCredentialsError,
    RefreshTokenNotFoundError,
    UserAlreadyExistsError,
)

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
        # Check if user with email already exists
        existing_user = await self.get_user_by_email(session, email)
        if existing_user:
            raise UserAlreadyExistsError(email=email)

        # Check if user with username already exists
        stmt = select(User).where(User.username == username)
        result = await session.execute(stmt)
        existing_username = result.scalar_one_or_none()
        if existing_username:
            raise UserAlreadyExistsError(username=username)

        # Hash password
        hashed_password = hash_password(password)

        # Create user
        user = User(
            email=email,
            username=username,
            hashed_password=hashed_password,
            is_active=True,
            is_verified=False,
            roles=["user"],
        )

        session.add(user)
        await session.commit()
        await session.refresh(user)

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
        user = await self.get_user_by_email(session, email)
        if not user:
            logger.warning("Authentication failed: user not found", extra={"email": email})
            raise InvalidCredentialsError()

        # Verify password
        if not verify_password(password, user.hashed_password):
            logger.warning(
                "Authentication failed: invalid password",
                extra={"user_id": str(user.id), "email": email},
            )
            raise InvalidCredentialsError()

        # Check if user is active
        if not user.is_active:
            logger.warning(
                "Authentication failed: inactive user",
                extra={"user_id": str(user.id), "email": email},
            )
            raise InactiveUserError()

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
        # Ensure secret key is set
        if not settings.jwt_secret_key:
            raise ValueError("JWT_SECRET_KEY must be set in environment variables")

        # Create token payload
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
        session: AsyncSession,
        user: User,
    ) -> RefreshToken:
        """
        Create and store a refresh token for a user.

        Args:
            session: Database session
            user: User object

        Returns:
            Created RefreshToken object
        """
        # Generate refresh token
        token = create_refresh_token()
        expires_at = datetime.now(UTC) + timedelta(days=settings.jwt_refresh_token_expire_days)

        # Create refresh token record
        refresh_token = RefreshToken(
            user_id=user.id,
            token=token,
            expires_at=expires_at,
        )

        session.add(refresh_token)
        await session.commit()
        await session.refresh(refresh_token)

        logger.info(
            "Refresh token created",
            extra={"user_id": str(user.id), "token_id": str(refresh_token.id)},
        )

        return refresh_token

    async def refresh_access_token(
        self,
        session: AsyncSession,
        refresh_token_str: str,
    ) -> tuple[str, RefreshToken]:
        """
        Refresh an access token using a refresh token.

        Args:
            session: Database session
            refresh_token_str: Refresh token string

        Returns:
            Tuple of (new_access_token, refresh_token_record)

        Raises:
            RefreshTokenNotFoundError: If refresh token is not found or expired
        """
        # Find refresh token
        stmt = select(RefreshToken).where(RefreshToken.token == refresh_token_str)
        result = await session.execute(stmt)
        refresh_token = result.scalar_one_or_none()

        if not refresh_token:
            logger.warning("Refresh token not found", extra={"token": refresh_token_str[:10]})
            raise RefreshTokenNotFoundError()

        # Check if token is expired
        if is_token_expired(refresh_token.expires_at):
            logger.warning(
                "Refresh token expired",
                extra={"token_id": str(refresh_token.id), "user_id": str(refresh_token.user_id)},
            )
            # Delete expired token
            await session.delete(refresh_token)
            await session.commit()
            raise RefreshTokenNotFoundError()

        # Get user
        user = await self.get_user_by_id(session, refresh_token.user_id)
        if not user:
            logger.error(
                "User not found for refresh token",
                extra={"token_id": str(refresh_token.id), "user_id": str(refresh_token.user_id)},
            )
            raise RefreshTokenNotFoundError()

        # Check if user is active
        if not user.is_active:
            logger.warning(
                "Inactive user attempted token refresh",
                extra={"user_id": str(user.id)},
            )
            raise InactiveUserError()

        # Create new access token
        access_token = await self.create_access_token(user)

        logger.info(
            "Access token refreshed",
            extra={"user_id": str(user.id), "token_id": str(refresh_token.id)},
        )

        return access_token, refresh_token

    async def revoke_refresh_token(
        self,
        session: AsyncSession,
        refresh_token_str: str,
    ) -> None:
        """
        Revoke (delete) a refresh token (logout).

        Args:
            session: Database session
            refresh_token_str: Refresh token string to revoke
        """
        stmt = select(RefreshToken).where(RefreshToken.token == refresh_token_str)
        result = await session.execute(stmt)
        refresh_token = result.scalar_one_or_none()

        if refresh_token:
            await session.delete(refresh_token)
            await session.commit()
            logger.info(
                "Refresh token revoked",
                extra={"token_id": str(refresh_token.id), "user_id": str(refresh_token.user_id)},
            )

    async def get_user_by_id(self, session: AsyncSession, user_id: UUID) -> User | None:
        """
        Get a user by ID.

        Args:
            session: Database session
            user_id: User ID

        Returns:
            User object or None if not found
        """
        stmt = select(User).where(User.id == user_id)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_by_email(self, session: AsyncSession, email: str) -> User | None:
        """
        Get a user by email.

        Args:
            session: Database session
            email: User email address

        Returns:
            User object or None if not found
        """
        stmt = select(User).where(User.email == email)
        result = await session.execute(stmt)
        return result.scalar_one_or_none()

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
            # Check if username is taken
            stmt = select(User).where(User.username == username, User.id != user.id)
            result = await session.execute(stmt)
            if result.scalar_one_or_none():
                raise UserAlreadyExistsError(username=username)
            user.username = username

        if email and email != user.email:
            # Check if email is taken
            existing_user = await self.get_user_by_email(session, email)
            if existing_user and existing_user.id != user.id:
                raise UserAlreadyExistsError(email=email)
            user.email = email

        user.updated_at = datetime.now(UTC)
        await session.commit()
        await session.refresh(user)

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
            await session.commit()
            await session.refresh(user)

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
        # For now, check if user has 'admin' role for admin permissions
        if permission == "admin":
            return "admin" in user.roles

        # Default: all authenticated users have basic permissions
        return True


# Global service instance
auth_service = AuthService()
