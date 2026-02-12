"""Auth service for Supabase token verification."""

from __future__ import annotations

import logging
import os
from typing import Any, Dict, Optional

import httpx

from backend.config import settings
from backend.services.base_service import BaseService
from backend.services.exceptions import ServiceUnavailableError
from backend.services.registry import registry

logger = logging.getLogger(__name__)


class AuthService(BaseService):
    """Supabase Auth integration in no-auth reconstruction mode.

    This service does not enforce auth globally. It provides explicit token
    verification endpoints so auth can be progressively integrated.
    """

    def __init__(self) -> None:
        super().__init__("auth_service")
        self.supabase_url = settings.SUPABASE_URL or os.getenv("NEXT_PUBLIC_SUPABASE_URL") or ""
        self.anon_key = (
            os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
            or os.getenv("SUPABASE_ANON_KEY")
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

    async def initialize(self) -> None:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=10.0)
        await super().initialize()

    async def shutdown(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None
        await super().shutdown()

    def _is_configured(self) -> bool:
        return bool(self.supabase_url and (self.anon_key or self.service_role_key))

    async def check_health(self) -> Dict[str, Any]:
        if not self.supabase_url:
            return {"status": "disabled", "detail": "Supabase auth URL not configured"}

        client = self._client or httpx.AsyncClient(timeout=10.0)
        own_client = self._client is None
        try:
            if self.service_role_key:
                response = await client.get(
                    f"{self.supabase_url}/auth/v1/settings",
                    headers={"apikey": self.service_role_key},
                )
                if response.status_code == 200:
                    return {"status": "healthy", "provider": "supabase"}
                return {
                    "status": "unhealthy",
                    "provider": "supabase",
                    "detail": f"/settings returned {response.status_code}",
                }

            if not self.anon_key:
                return {
                    "status": "disabled",
                    "provider": "supabase",
                    "detail": "Supabase auth keys not configured",
                }

            # Anon keys cannot call /settings on newer GoTrue.
            # Probe /user and treat auth-required responses as reachable.
            probe = await client.get(
                f"{self.supabase_url}/auth/v1/user",
                headers={"apikey": self.anon_key},
            )
            if probe.status_code in (200, 401, 403):
                return {
                    "status": "healthy",
                    "provider": "supabase",
                    "detail": "/user reachable (auth required)",
                }
            return {
                "status": "unhealthy",
                "provider": "supabase",
                "detail": f"/user returned {probe.status_code}",
            }
        except Exception as exc:
            return {"status": "unhealthy", "provider": "supabase", "error": str(exc)}
        finally:
            if own_client:
                await client.aclose()

    async def verify_access_token(self, access_token: str) -> Dict[str, Any]:
        if not self._is_configured():
            raise ServiceUnavailableError("Auth service is not configured")

        token = (access_token or "").strip()
        if not token:
            return {"valid": False, "error": "Missing access token"}

        client = self._client or httpx.AsyncClient(timeout=10.0)
        own_client = self._client is None
        try:
            response = await client.get(
                f"{self.supabase_url}/auth/v1/user",
                headers={
                    "apikey": self.anon_key or self.service_role_key,
                    "Authorization": f"Bearer {token}",
                },
            )
            if response.status_code == 200:
                payload = response.json()
                return {
                    "valid": True,
                    "user": payload,
                    "user_id": payload.get("id"),
                    "email": payload.get("email"),
                    "role": payload.get("role"),
                }
            if response.status_code in (401, 403):
                return {"valid": False, "error": "Invalid or expired token"}
            return {
                "valid": False,
                "error": f"Auth server returned {response.status_code}",
                "detail": response.text[:500],
            }
        except Exception as exc:
            return {"valid": False, "error": str(exc)}
        finally:
            if own_client:
                await client.aclose()


auth_service = AuthService()
registry.register(auth_service)
