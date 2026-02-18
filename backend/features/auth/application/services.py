"""
Auth application services.
"""

from typing import Any, Dict, Optional

from backend.features.auth.application.ports import AuthService, TokenService
from backend.features.auth.domain.entities import User, Session


class AuthenticationService:
    """Application service for authentication operations."""

    def __init__(
        self, auth_service: AuthService, token_service: Optional[TokenService] = None
    ):
        self._auth_service = auth_service
        self._token_service = token_service

    async def register(
        self, email: str, password: str, options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Register a new user."""
        return await self._auth_service.sign_up(email, password, options)

    async def login(self, email: str, password: str) -> Dict[str, Any]:
        """Login with email/password."""
        return await self._auth_service.sign_in(email, password)

    async def logout(self, access_token: str) -> Dict[str, Any]:
        """Logout and invalidate session."""
        result = await self._auth_service.sign_out(access_token)

        if result.get("success") and self._token_service:
            await self._token_service.blacklist_token(access_token)

        return result

    async def verify_session(self, access_token: str) -> Optional[User]:
        """Verify a session and return the user."""
        result = await self._auth_service.verify_token(access_token)

        if result.get("valid"):
            user_data = result.get("user")
            if user_data:
                return User.from_dict(user_data)

        return None

    async def refresh_token(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh an access token."""
        return await self._auth_service.refresh_session(refresh_token)

    async def check_health(self) -> Dict[str, Any]:
        """Check authentication service health."""
        return await self._auth_service.check_health()
