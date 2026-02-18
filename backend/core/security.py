"""
Core security utilities.

Provides common security functions for password hashing, JWT, and encryption.
"""

import hashlib
import hmac
import secrets
from datetime import datetime, timedelta
from typing import Optional


def generate_secure_token(length: int = 32) -> str:
    """
    Generate a cryptographically secure random token.

    Args:
        length: Length of the token in bytes (default 32)

    Returns:
        Hex-encoded secure token
    """
    return secrets.token_hex(length)


def generate_csrf_token() -> str:
    """Generate a CSRF protection token."""
    return secrets.token_hex(32)


def hash_password(password: str) -> str:
    """
    Hash a password using SHA-256 with a random salt.

    Note: For production, use bcrypt or argon2.

    Args:
        password: Plain text password

    Returns:
        Hashed password with salt
    """
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((salt + password).encode()).hexdigest()
    return f"{salt}${password_hash}"


def verify_password(password: str, hashed: str) -> bool:
    """
    Verify a password against a hash.

    Args:
        password: Plain text password
        hashed: Hashed password

    Returns:
        True if password matches
    """
    try:
        salt, password_hash = hashed.split("$")
        computed_hash = hashlib.sha256((salt + password).encode()).hexdigest()
        return hmac.compare_digest(computed_hash, password_hash)
    except ValueError:
        return False


def constant_time_compare(a: str, b: str) -> bool:
    """
    Compare two strings in constant time to prevent timing attacks.

    Args:
        a: First string
        b: Second string

    Returns:
        True if strings are equal
    """
    return hmac.compare_digest(a, b)


class RateLimiter:
    """Simple in-memory rate limiter."""

    def __init__(self, max_requests: int = 100, window_seconds: int = 60):
        """
        Initialize rate limiter.

        Args:
            max_requests: Maximum requests allowed in the window
            window_seconds: Time window in seconds
        """
        self._max_requests = max_requests
        self._window_seconds = window_seconds
        self._requests: dict[str, list[datetime]] = {}

    def is_allowed(self, key: str) -> bool:
        """
        Check if a request is allowed.

        Args:
            key: Unique identifier (e.g., IP address, user ID)

        Returns:
            True if request is allowed
        """
        now = datetime.utcnow()
        cutoff = now - timedelta(seconds=self._window_seconds)

        if key not in self._requests:
            self._requests[key] = []

        self._requests[key] = [ts for ts in self._requests[key] if ts > cutoff]

        if len(self._requests[key]) >= self._max_requests:
            return False

        self._requests[key].append(now)
        return True

    def reset(self, key: str) -> None:
        """Reset rate limit for a key."""
        if key in self._requests:
            del self._requests[key]
