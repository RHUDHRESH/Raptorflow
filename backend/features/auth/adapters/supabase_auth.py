"""
Auth adapters - Supabase implementation.
"""

from typing import Any, Dict, Optional

from backend.features.auth.application.ports import AuthService


class SupabaseAuthServiceAdapter:
    """Adapter that wraps the existing Supabase auth service."""

    def __init__(self, supabase_auth_service):
        self._service = supabase_auth_service

    async def sign_up(
        self, email: str, password: str, options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Sign up a new user."""
        return await self._service.sign_up(email, password, options)

    async def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """Sign in with email/password."""
        return await self._service.sign_in(email, password)

    async def sign_out(self, access_token: str) -> Dict[str, Any]:
        """Sign out - invalidate session."""
        return await self._service.sign_out(access_token)

    async def verify_token(self, access_token: str) -> Dict[str, Any]:
        """Verify an access token."""
        return await self._service.verify_token(access_token)

    async def refresh_session(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh a session."""
        return await self._service.refresh_session(refresh_token)

    async def check_health(self) -> Dict[str, Any]:
        """Check if auth service is healthy."""
        return await self._service.check_health()
