"""
User Database Models

SQLModel definitions for user authentication and authorization.
"""

from datetime import UTC, datetime
from uuid import UUID, uuid4

from sqlalchemy import ARRAY, Column, Index, String, UniqueConstraint
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
        default_factory=lambda: ["user"],
        sa_column=Column(ARRAY(String), nullable=False),
    )
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC), nullable=False)

    # Note: Refresh tokens are stored in Redis, not in the database

    __table_args__ = (
        UniqueConstraint("email", name="uq_users_email"),
        UniqueConstraint("username", name="uq_users_username"),
        Index("idx_users_email", "email"),
        Index("idx_users_username", "username"),
    )
