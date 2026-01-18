"""
User Database Models

SQLModel definitions for user authentication and authorization.
"""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import Index, UniqueConstraint
from sqlmodel import Field, SQLModel


class User(SQLModel, table=True):  # type: ignore[call-arg]
    """
    User model for authentication and authorization.

    Attributes:
        id: Unique user identifier
        email: User email address (unique)
        username: User username (unique)
        hashed_password: Bcrypt hashed password
        is_active: Whether the user account is active
        is_verified: Whether the user email is verified
        roles: List of user roles (default: ['user'])
        created_at: Account creation timestamp
        updated_at: Last update timestamp
    """

    __tablename__ = "users"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(max_length=255, unique=True, index=True, nullable=False)
    username: str = Field(max_length=100, unique=True, index=True, nullable=False)
    hashed_password: str = Field(max_length=255, nullable=False)
    is_active: bool = Field(default=True, nullable=False)
    is_verified: bool = Field(default=False, nullable=False)
    roles: list[str] = Field(
        default_factory=lambda: ["user"], sa_column_kwargs={"type_": "ARRAY(TEXT)"}
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)

    # Note: Refresh tokens are now stored in Redis, not in the database

    __table_args__ = (
        UniqueConstraint("email", name="uq_users_email"),
        UniqueConstraint("username", name="uq_users_username"),
        Index("idx_users_email", "email"),
        Index("idx_users_username", "username"),
    )


# Note: RefreshToken model is kept for backward compatibility but is no longer used.
# Refresh tokens are now stored in Redis for better performance and automatic expiration.
# The refresh_tokens table can be removed in a future migration if not needed.
class RefreshToken(SQLModel, table=True):  # type: ignore[call-arg]
    """
    Refresh token model (DEPRECATED - now using Redis).

    This model is kept for backward compatibility but refresh tokens
    are now stored in Redis. The table can be removed in a future migration.
    """

    __tablename__ = "refresh_tokens"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True)
    token: str = Field(max_length=255, unique=True, index=True, nullable=False)
    expires_at: datetime = Field(nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)

    __table_args__ = (
        UniqueConstraint("token", name="uq_refresh_tokens_token"),
        Index("idx_refresh_tokens_user_id", "user_id"),
        Index("idx_refresh_tokens_token", "token"),
        Index("idx_refresh_tokens_expires_at", "expires_at"),
    )
