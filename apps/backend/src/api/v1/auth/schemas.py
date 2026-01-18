"""
Authentication API Schemas

Request and response models for authentication endpoints.
"""

from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field, field_validator


class UserRegister(BaseModel):
    """Request model for user registration."""

    email: EmailStr = Field(..., description="User email address")
    username: str = Field(..., min_length=3, max_length=100, description="Username")
    password: str = Field(..., min_length=8, max_length=128, description="Password")

    @field_validator("password")
    @classmethod
    def validate_password(cls, v: str) -> str:
        """
        Validate password strength.

        Requirements:
        - Minimum 8 characters
        - At least one uppercase letter
        - At least one lowercase letter
        - At least one digit
        - At least one special character
        """
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters long")

        has_upper = any(c.isupper() for c in v)
        has_lower = any(c.islower() for c in v)
        has_digit = any(c.isdigit() for c in v)
        has_special = any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in v)

        if not (has_upper and has_lower and has_digit and has_special):
            raise ValueError(
                "Password must contain at least one uppercase letter, "
                "one lowercase letter, one digit, and one special character"
            )

        return v


class UserLogin(BaseModel):
    """Request model for user login."""

    email: EmailStr = Field(..., description="User email address")
    password: str = Field(..., description="Password")


class TokenResponse(BaseModel):
    """Response model for authentication tokens."""

    access_token: str = Field(..., description="JWT access token")
    refresh_token: str = Field(..., description="Refresh token")
    token_type: str = Field(default="bearer", description="Token type")


class RefreshTokenRequest(BaseModel):
    """Request model for token refresh."""

    refresh_token: str = Field(..., description="Refresh token")


class UserResponse(BaseModel):
    """Response model for user data (without password)."""

    id: UUID = Field(..., description="User ID", examples=["123e4567-e89b-12d3-a456-426614174000"])
    email: str = Field(..., description="User email", examples=["user@example.com"])
    username: str = Field(..., description="Username", examples=["johndoe"])
    is_active: bool = Field(..., description="Whether user is active", examples=[True])
    is_verified: bool = Field(..., description="Whether user email is verified", examples=[False])
    roles: list[str] = Field(..., description="User roles", examples=[["user"]])
    created_at: datetime = Field(..., description="Account creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    links: dict[str, str] | None = Field(
        default=None,
        description="HATEOAS links for related resources",
        examples=[{"self": "/api/v1/auth/me", "update": "/api/v1/auth/me"}],
    )

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Request model for updating user profile."""

    username: str | None = Field(None, min_length=3, max_length=100, description="Username")
    email: EmailStr | None = Field(None, description="Email address")


class PaginationParams(BaseModel):
    """Pagination parameters for list endpoints."""

    page: int = Field(default=1, ge=1, description="Page number (1-indexed)")
    page_size: int = Field(default=20, ge=1, le=100, description="Number of items per page")

    @property
    def offset(self) -> int:
        """Calculate offset from page number."""
        return (self.page - 1) * self.page_size

    @property
    def limit(self) -> int:
        """Get limit (same as page_size)."""
        return self.page_size


class PaginatedResponse(BaseModel):
    """Paginated response wrapper."""

    items: list[UserResponse] = Field(..., description="List of items in current page")
    total: int = Field(..., description="Total number of items")
    page: int = Field(..., description="Current page number")
    page_size: int = Field(..., description="Number of items per page")
    total_pages: int = Field(..., description="Total number of pages")

    @classmethod
    def create(
        cls,
        items: list[UserResponse],
        total: int,
        page: int,
        page_size: int,
    ) -> "PaginatedResponse":
        """Create a paginated response."""
        total_pages = (total + page_size - 1) // page_size if total > 0 else 0
        return cls(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )


class BulkUserCreate(BaseModel):
    """Request model for bulk user creation."""

    users: list[UserRegister] = Field(
        ..., min_length=1, max_length=100, description="List of users to create"
    )


class BulkUserUpdate(BaseModel):
    """Request model for bulk user update."""

    user_updates: list[dict[str, Any]] = Field(
        ...,
        min_length=1,
        max_length=100,
        description="List of user updates (each must have 'id' and optional 'username', 'email')",
    )


class BulkUserDelete(BaseModel):
    """Request model for bulk user deletion."""

    user_ids: list[UUID] = Field(
        ..., min_length=1, max_length=100, description="List of user IDs to delete"
    )


class BulkOperationResponse(BaseModel):
    """Response model for bulk operations."""

    success_count: int = Field(..., description="Number of successful operations")
    error_count: int = Field(..., description="Number of failed operations")
    errors: list[dict[str, Any]] = Field(
        default_factory=list, description="List of errors encountered"
    )
