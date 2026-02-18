"""Disabled Auth Service - No authentication required."""

from __future__ import annotations

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class DisabledAuthService:
    """No authentication - all requests are allowed.

    WARNING: This mode is insecure and should only be used for
    development/testing, never in production.
    """

    def __init__(self):
        logger.warning("Auth DISABLED - all requests allowed (DEV ONLY)")

    def create_session(self) -> Dict[str, Any]:
        return {
            "access_token": "disabled-token",
            "token_type": "bearer",
            "user": {"id": "anonymous", "email": "anonymous@disabled.local"},
        }

    def verify_token(self, token: Optional[str]) -> Dict[str, Any]:
        return {
            "valid": True,
            "user": {"id": "anonymous", "email": "anonymous@disabled.local"},
            "user_id": "anonymous",
            "email": "anonymous@disabled.local",
        }

    def get_user(self, token: Optional[str]) -> Optional[Dict[str, Any]]:
        return {"id": "anonymous", "email": "anonymous@disabled.local"}

    async def check_health(self) -> Dict[str, Any]:
        return {
            "status": "healthy",
            "provider": "disabled",
            "warning": "Auth disabled - not secure!",
        }

    async def sign_up(self, email: str, password: str) -> Dict[str, Any]:
        return self.create_session()

    async def sign_in(self, email: str, password: str) -> Dict[str, Any]:
        return self.create_session()


_disabled_auth_service: Optional[DisabledAuthService] = None


def get_disabled_auth_service() -> DisabledAuthService:
    global _disabled_auth_service
    if _disabled_auth_service is None:
        _disabled_auth_service = DisabledAuthService()
    return _disabled_auth_service
