"""
User Database Models

SQLModel definitions for user authentication and authorization.
"""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import Index, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel


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

    # Relationships
    refresh_tokens: list["RefreshToken"] = Relationship(back_populates="user", cascade_delete=True)

    __table_args__ = (
        UniqueConstraint("email", name="uq_users_email"),
        UniqueConstraint("username", name="uq_users_username"),
        Index("idx_users_email", "email"),
        Index("idx_users_username", "username"),
    )


class RefreshToken(SQLModel, table=True):  # type: ignore[call-arg]
    """
    Refresh token model for JWT token refresh mechanism.

    Attributes:
        id: Unique token identifier
        user_id: Foreign key to user
        token: Refresh token string (unique)
        expires_at: Token expiration timestamp
        created_at: Token creation timestamp
    """

    __tablename__ = "refresh_tokens"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: UUID = Field(foreign_key="users.id", nullable=False, index=True)
    token: str = Field(max_length=255, unique=True, index=True, nullable=False)
    expires_at: datetime = Field(nullable=False)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)

    # Relationships
    user: User = Relationship(back_populates="refresh_tokens")

    __table_args__ = (
        UniqueConstraint("token", name="uq_refresh_tokens_token"),
        Index("idx_refresh_tokens_user_id", "user_id"),
        Index("idx_refresh_tokens_token", "token"),
        Index("idx_refresh_tokens_expires_at", "expires_at"),
    )
