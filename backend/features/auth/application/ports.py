"""
Auth application layer - Ports.
"""

from typing import Any, Dict, Optional, Protocol
from backend.features.auth.domain.entities import User, Session


class AuthService(Protocol):
    """Port for authentication services."""

    async def sign_up(
        self, email: str, password: str, options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Sign up a new user."""
        ...

    async def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """Sign in with email/password."""
        ...

    async def sign_out(self, access_token: str) -> Dict[str, Any]:
        """Sign out - invalidate session."""
        ...

    async def verify_token(self, access_token: str) -> Dict[str, Any]:
        """Verify an access token."""
        ...

    async def refresh_session(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh a session."""
        ...

    async def check_health(self) -> Dict[str, Any]:
        """Check if auth service is healthy."""
        ...


class TokenService(Protocol):
    """Port for token operations."""

    async def create_token(self, user_id: str) -> str:
        """Create an access token for a user."""
        ...

    async def verify_token(self, token: str) -> Optional[str]:
        """Verify a token and return user_id if valid."""
        ...

    async def blacklist_token(self, token: str) -> None:
        """Add a token to the blacklist."""
        ...

    async def is_blacklisted(self, token: str) -> bool:
        """Check if a token is blacklisted."""
        ...
