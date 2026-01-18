"""
Security Utilities

JWT utilities, password hashing, and other security-related functions.
Currently provides placeholders for future authentication implementation.
"""

import secrets
from datetime import UTC, datetime, timedelta
from typing import Any

import bcrypt
from jose import JWTError, jwt
from loguru import logger


def generate_secret_key(length: int = 32) -> str:
    """
    Generate a cryptographically secure random secret key.

    Args:
        length: Length of the secret key in bytes

    Returns:
        Hex-encoded secret key string
    """
    return secrets.token_hex(length)


def hash_password(password: str) -> str:
    """
    Hash a password using bcrypt.

    Uses bcrypt for secure password hashing with:
    - Built-in salting (automatic, unique per password)
    - Configurable cost factor (default: 12 rounds)
    - Resistance to rainbow table attacks
    - Resistance to brute force attacks

    Args:
        password: Plain text password

    Returns:
        Bcrypt hashed password string (includes salt)

    Example:
        ```python
        hashed = hash_password("my_password")
        # Store hashed in database
        ```
    """
    # Encode password to bytes
    password_bytes = password.encode("utf-8")

    # Generate salt and hash password (bcrypt handles salting internally)
    # Cost factor of 12 is a good balance between security and performance
    hashed = bcrypt.hashpw(password_bytes, bcrypt.gensalt(rounds=12))

    # Return as string (bcrypt hash includes salt)
    return hashed.decode("utf-8")


def verify_password(password: str, hashed_password: str) -> bool:
    """
    Verify a password against a bcrypt hash.

    Args:
        password: Plain text password to verify
        hashed_password: Stored bcrypt password hash (includes salt)

    Returns:
        True if password matches, False otherwise
    """
    try:
        password_bytes = password.encode("utf-8")
        hashed_bytes = hashed_password.encode("utf-8")
        return bcrypt.checkpw(password_bytes, hashed_bytes)
    except Exception as e:
        logger.warning(f"Password verification failed: {e}")
        return False


def create_jwt_token(
    payload: dict[str, Any],
    secret_key: str,
    expires_delta: timedelta | None = None,
    algorithm: str = "HS256",
) -> str:
    """
    Create a JWT token.

    Args:
        payload: Token payload data (should include 'sub' for subject/user ID)
        secret_key: Secret key for signing
        expires_delta: Optional expiration time delta (defaults to 30 minutes if not provided)
        algorithm: JWT signing algorithm (default: HS256)

    Returns:
        JWT token string

        Example:
        ```python
        payload = {"sub": "user_id", "email": "user@example.com"}
        token = create_jwt_token(payload, secret_key, expires_delta=timedelta(minutes=30))
        ```
    """
    # Create a copy of the payload to avoid mutating the original
    to_encode = payload.copy()

    # Set expiration time
    if expires_delta:
        expire = get_current_timestamp() + expires_delta
    else:
        # Default to 30 minutes if not specified
        expire = get_current_timestamp() + timedelta(minutes=30)

    # Add standard JWT claims
    to_encode.update({"exp": expire, "iat": get_current_timestamp()})

    # Encode and return the token
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algorithm)
    return encoded_jwt


def verify_jwt_token(
    token: str, secret_key: str, algorithm: str = "HS256"
) -> dict[str, Any] | None:
    """
    Verify and decode a JWT token.

    Args:
        token: JWT token string
        secret_key: Secret key for verification
        algorithm: JWT signing algorithm (default: HS256)

    Returns:
        Decoded payload if valid, None if invalid or expired

        Example:
        ```python
        payload = verify_jwt_token(token, secret_key)
        if payload:
            user_id = payload.get("sub")
        ```
    """
    try:
        # Decode and verify the token
        payload = jwt.decode(token, secret_key, algorithms=[algorithm])
        return payload
    except JWTError as e:
        logger.warning(f"JWT token verification failed: {e}")
        return None
    except Exception as e:
        logger.error(f"Unexpected error during JWT verification: {e}")
        return None


def get_current_timestamp() -> datetime:
    """
    Get current timestamp in UTC.

    Returns:
        Current datetime in UTC timezone
    """
    return datetime.now(UTC)


def is_token_expired(expires_at: datetime) -> bool:
    """
    Check if a token is expired.

    Args:
        expires_at: Expiration timestamp

    Returns:
        True if expired, False otherwise
    """
    return get_current_timestamp() >= expires_at


def create_refresh_token() -> str:
    """
    Create a cryptographically secure refresh token.

    Returns:
        Hex-encoded random token string suitable for use as a refresh token
    """
    return secrets.token_urlsafe(32)
