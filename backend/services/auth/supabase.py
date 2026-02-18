"""Supabase Auth Service - Real Supabase authentication."""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional

import httpx

from backend.config import settings

logger = logging.getLogger(__name__)


class SupabaseAuthService:
    """Real Supabase Auth integration.

    This service provides proper Supabase authentication:
    - Sign up with email/password
    - Sign in with email/password
    - Token verification
    - Session management
    - Token refresh
    """

    def __init__(self) -> None:
        import os
        from backend.config import settings

        self.supabase_url = (
            settings.SUPABASE_URL or os.getenv("NEXT_PUBLIC_SUPABASE_URL") or ""
        )
        self.anon_key = (
            os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
            or os.getenv("SUPABASE_ANON_KEY")
            or settings.SUPABASE_ANON_KEY
            or ""
        )
        self.service_role_key = (
            settings.SUPABASE_SERVICE_ROLE_KEY
            or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
            or os.getenv("SUPABASE_SERVICE_KEY")
            or os.getenv("SERVICE_ROLE_KEY")
            or ""
        )
        self._client: Optional[httpx.AsyncClient] = None

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=30.0)
        return self._client

    async def initialize(self) -> None:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=30.0)
        logger.info("SupabaseAuthService initialized")

    async def shutdown(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None
        logger.info("SupabaseAuthService shutdown")

    def _is_configured(self) -> bool:
        return bool(self.supabase_url and (self.anon_key or self.service_role_key))

    async def check_health(self) -> Dict[str, Any]:
        """Check if Supabase auth is healthy."""
        if not self.supabase_url:
            return {"status": "disabled", "detail": "Supabase auth URL not configured"}

        try:
            response = await self.client.get(
                f"{self.supabase_url}/auth/v1/settings",
                headers={"apikey": self.service_role_key or self.anon_key},
            )
            if response.status_code == 200:
                return {
                    "status": "healthy",
                    "provider": "supabase",
                    "url": self.supabase_url,
                }
            return {
                "status": "unhealthy",
                "provider": "supabase",
                "detail": f"Status: {response.status_code}",
            }
        except Exception as exc:
            logger.error(f"Supabase health check failed: {exc}")
            return {"status": "unhealthy", "provider": "supabase", "error": str(exc)}

    async def sign_up(
        self, email: str, password: str, options: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Sign up a new user.

        Args:
            email: User email address
            password: User password (min 6 chars for Supabase)
            options: Optional signup options (e.g., email_confirm)

        Returns:
            Dict with user, session, and optional error
        """
        if not self._is_configured():
            return {"error": "Supabase not configured", "user": None, "session": None}

        if not email or not password:
            return {
                "error": "Email and password are required",
                "user": None,
                "session": None,
            }

        try:
            payload: Dict[str, Any] = {"email": email, "password": password}
            if options:
                payload["options"] = options

            response = await self.client.post(
                f"{self.supabase_url}/auth/v1/signup",
                json=payload,
                headers={"apikey": self.anon_key, "Content-Type": "application/json"},
            )

            if response.status_code == 200:
                data = response.json()

                # Handle different response formats
                user = data.get("user")
                session = data.get("session")

                # If email confirmation is required, there might be no session
                if not session and data.get("confirming"):
                    return {
                        "user": user,
                        "session": None,
                        "requires_email_confirmation": True,
                    }

                return {
                    "user": user,
                    "session": session,
                }
            elif response.status_code == 400:
                error_data = response.json()
                error_msg = error_data.get(
                    "msg", error_data.get("error_description", "Invalid request")
                )
                return {"error": error_msg, "user": None, "session": None}
            else:
                logger.error(f"Signup failed: {response.status_code} - {response.text}")
                return {
                    "error": f"Signup failed: {response.status_code}",
                    "user": None,
                    "session": None,
                }

        except httpx.TimeoutException:
            logger.error("Supabase signup timeout")
            return {"error": "Request timeout", "user": None, "session": None}
        except Exception as exc:
            logger.error(f"Supabase signup error: {exc}")
            return {"error": str(exc), "user": None, "session": None}

    async def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """Sign in with email/password.

        Args:
            email: User email address
            password: User password

        Returns:
            Dict with user, session, and optional error
        """
        if not self._is_configured():
            return {"error": "Supabase not configured", "user": None, "session": None}

        if not email or not password:
            return {
                "error": "Email and password are required",
                "user": None,
                "session": None,
            }

        try:
            response = await self.client.post(
                f"{self.supabase_url}/auth/v1/token?grant_type=password",
                json={
                    "email": email,
                    "password": password,
                },
                headers={"apikey": self.anon_key, "Content-Type": "application/json"},
            )

            if response.status_code == 200:
                data = response.json()

                # Supabase returns session data directly at root level
                access_token = data.get("access_token")
                refresh_token = data.get("refresh_token")
                user = data.get("user")

                if not access_token or not user:
                    return {
                        "error": "Invalid response from Supabase",
                        "user": None,
                        "session": None,
                    }

                return {
                    "user": user,
                    "session": {
                        "access_token": access_token,
                        "refresh_token": refresh_token,
                        "token_type": data.get("token_type", "bearer"),
                        "expires_in": data.get("expires_in", 3600),
                        "expires_at": data.get("expires_at"),
                    },
                }
            elif response.status_code == 400:
                error_data = response.json()
                error_msg = error_data.get("msg", "Invalid email or password")
                return {"error": error_msg, "user": None, "session": None}
            elif response.status_code == 401:
                return {
                    "error": "Invalid email or password",
                    "user": None,
                    "session": None,
                }
            else:
                logger.error(
                    f"Sign in failed: {response.status_code} - {response.text}"
                )
                return {
                    "error": f"Sign in failed: {response.status_code}",
                    "user": None,
                    "session": None,
                }

        except httpx.TimeoutException:
            logger.error("Supabase sign in timeout")
            return {"error": "Request timeout", "user": None, "session": None}
        except Exception as exc:
            logger.error(f"Supabase sign in error: {exc}")
            return {"error": str(exc), "user": None, "session": None}

    async def sign_out(self, access_token: str) -> Dict[str, Any]:
        """Sign out - invalidate session.

        Args:
            access_token: The access token to invalidate

        Returns:
            Dict with success status or error
        """
        if not self._is_configured():
            return {"error": "Supabase not configured"}

        if not access_token:
            return {"error": "Access token required"}

        try:
            response = await self.client.post(
                f"{self.supabase_url}/auth/v1/logout",
                headers={
                    "apikey": self.anon_key,
                    "Authorization": f"Bearer {access_token}",
                },
            )

            # 200 or 204 means success
            if response.status_code in (200, 204):
                logger.info("User signed out successfully")
                return {"success": True}
            else:
                logger.warning(f"Sign out returned: {response.status_code}")
                return {
                    "success": False,
                    "error": f"Logout failed: {response.status_code}",
                }

        except Exception as exc:
            logger.error(f"Supabase sign out error: {exc}")
            return {"error": str(exc)}

    async def verify_token(self, access_token: str) -> Dict[str, Any]:
        """Verify an access token.

        Args:
            access_token: The access token to verify

        Returns:
            Dict with valid status, user info, or error
        """
        if not self._is_configured():
            return {"valid": False, "error": "Supabase not configured"}

        if not access_token:
            return {"valid": False, "error": "Missing access token"}

        try:
            # Use service role key for verification to ensure we can validate properly
            # But prefer anon_key for public verification
            response = await self.client.get(
                f"{self.supabase_url}/auth/v1/user",
                headers={
                    "apikey": self.anon_key,
                    "Authorization": f"Bearer {access_token}",
                },
            )

            if response.status_code == 200:
                user = response.json()

                # Check if user is authenticated
                if not user or not user.get("id"):
                    return {"valid": False, "error": "User not found"}

                return {
                    "valid": True,
                    "user": user,
                    "user_id": user.get("id"),
                    "email": user.get("email"),
                }
            elif response.status_code == 401:
                return {"valid": False, "error": "Invalid or expired token"}
            elif response.status_code == 404:
                return {"valid": False, "error": "User not found"}
            else:
                logger.warning(f"Token verification returned: {response.status_code}")
                return {
                    "valid": False,
                    "error": f"Verification failed: {response.status_code}",
                }

        except httpx.TimeoutException:
            logger.error("Token verification timeout")
            return {"valid": False, "error": "Request timeout"}
        except Exception as exc:
            logger.error(f"Token verification error: {exc}")
            return {"valid": False, "error": str(exc)}

    async def get_user(self, access_token: str) -> Optional[Dict[str, Any]]:
        """Get user from access token.

        Args:
            access_token: The access token

        Returns:
            User dict if valid, None otherwise
        """
        result = await self.verify_token(access_token)
        if result.get("valid"):
            return result.get("user")
        return None

    async def refresh_session(self, refresh_token: str) -> Dict[str, Any]:
        """Refresh a session using refresh token.

        Args:
            refresh_token: The refresh token

        Returns:
            Dict with new session or error
        """
        if not self._is_configured():
            return {"error": "Supabase not configured"}

        if not refresh_token:
            return {"error": "Refresh token required"}

        try:
            response = await self.client.post(
                f"{self.supabase_url}/auth/v1/token?grant_type=refresh_token",
                json={"refresh_token": refresh_token},
                headers={"apikey": self.anon_key, "Content-Type": "application/json"},
            )

            if response.status_code == 200:
                data = response.json()

                access_token = data.get("access_token")
                new_refresh_token = data.get("refresh_token")

                if not access_token:
                    return {"error": "Invalid refresh response"}

                return {
                    "session": {
                        "access_token": access_token,
                        "refresh_token": new_refresh_token,
                        "token_type": data.get("token_type", "bearer"),
                        "expires_in": data.get("expires_in", 3600),
                        "expires_at": data.get("expires_at"),
                    },
                }
            elif response.status_code == 401:
                return {"error": "Invalid or expired refresh token"}
            else:
                logger.error(
                    f"Refresh failed: {response.status_code} - {response.text}"
                )
                return {"error": f"Refresh failed: {response.status_code}"}

        except httpx.TimeoutException:
            logger.error("Token refresh timeout")
            return {"error": "Request timeout"}
        except Exception as exc:
            logger.error(f"Token refresh error: {exc}")
            return {"error": str(exc)}

    async def reset_password(self, email: str) -> Dict[str, Any]:
        """Send password reset email.

        Args:
            email: User email address

        Returns:
            Dict with success status or error
        """
        if not self._is_configured():
            return {"error": "Supabase not configured"}

        if not email:
            return {"error": "Email is required"}

        try:
            response = await self.client.post(
                f"{self.supabase_url}/auth/v1/recover",
                json={"email": email},
                headers={"apikey": self.anon_key, "Content-Type": "application/json"},
            )

            # Supabase returns 200 even if email doesn't exist (for security)
            if response.status_code == 200:
                return {"success": True}
            else:
                logger.warning(f"Password reset returned: {response.status_code}")
                return {"success": False, "error": "Failed to send reset email"}

        except Exception as exc:
            logger.error(f"Password reset error: {exc}")
            return {"error": str(exc)}

    async def update_password(
        self, access_token: str, new_password: str
    ) -> Dict[str, Any]:
        """Update user password.

        Args:
            access_token: Valid access token
            new_password: New password

        Returns:
            Dict with success status or error
        """
        if not self._is_configured():
            return {"error": "Supabase not configured"}

        if not access_token or not new_password:
            return {"error": "Access token and new password required"}

        try:
            response = await self.client.post(
                f"{self.supabase_url}/auth/v1/user",
                json={"password": new_password},
                headers={
                    "apikey": self.anon_key,
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json",
                },
            )

            if response.status_code == 200:
                return {"success": True, "user": response.json()}
            else:
                return {"error": f"Password update failed: {response.status_code}"}

        except Exception as exc:
            logger.error(f"Password update error: {exc}")
            return {"error": str(exc)}


_supabase_auth_service: Optional[SupabaseAuthService] = None


def get_supabase_auth_service() -> SupabaseAuthService:
    """Get the Supabase auth service instance."""
    global _supabase_auth_service
    if _supabase_auth_service is None:
        _supabase_auth_service = SupabaseAuthService()
    return _supabase_auth_service


def reset_supabase_auth_service() -> None:
    """Reset the auth service (useful for testing)."""
    global _supabase_auth_service
    if _supabase_auth_service is not None:
        import asyncio

        asyncio.run(_supabase_auth_service.shutdown())
    _supabase_auth_service = None
