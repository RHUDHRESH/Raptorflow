import os
import json
from datetime import datetime, timedelta
from typing import Optional

import httpx
from pydantic import BaseModel
from .services.upstash_client import upstash_redis


class AuthToken(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    created_at: datetime

    @property
    def is_expired(self) -> bool:
        return datetime.now() > self.created_at + timedelta(
            seconds=self.expires_in - 60
        )


class PhonePeAuthClient:
    """Production-ready PhonePe authentication client with caching"""

    def __init__(self):
        self._token: Optional[AuthToken] = None
        self._auth_mode = self._determine_auth_mode()

    def _determine_auth_mode(self) -> str:
        """Determine auth mode based on configuration"""
        if os.getenv("PHONEPE_OAUTH_CLIENT_ID"):
            return "oauth"
        elif os.getenv("PHONEPE_API_KEY"):
            return "api_key"
        else:
            raise ValueError("No PhonePe authentication credentials configured")

    async def get_auth_header(self) -> dict:
        """Get auth header with cached token"""
        token = await self.get_token()
        return (
            {"Authorization": f"Bearer {token}"}
            if self._auth_mode == "oauth"
            else {"X-API-KEY": token}
        )

    async def get_token(self) -> str:
        """Get token with caching"""
        # Check Redis cache first
        if cached_token := await upstash_redis.get("phonepe_auth_token"):
            return cached_token

        # Fetch new token
        token = await self._fetch_new_token()

        # Cache with TTL (expires_in - 60 seconds buffer)
        await upstash_redis.set(
            "phonepe_auth_token", token, ex=self._token.expires_in - 60
        )
        return token

    async def _fetch_new_token(self) -> str:
        """Fetch new token from appropriate source"""
        if self._auth_mode == "oauth":
            return await self._get_oauth_token()
        return os.getenv("PHONEPE_API_KEY")

    async def _get_oauth_token(self) -> str:
        """Get OAuth token"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.phonepe.com/oauth/token",
                data={
                    "client_id": os.getenv("PHONEPE_OAUTH_CLIENT_ID"),
                    "client_secret": os.getenv("PHONEPE_OAUTH_SECRET"),
                    "grant_type": "client_credentials",
                },
            )
            response.raise_for_status()
            token_data = response.json()
            self._token = AuthToken(
                access_token=token_data["access_token"],
                token_type=token_data["token_type"],
                expires_in=token_data["expires_in"],
                created_at=datetime.now(),
            )
            return self._token.access_token

    async def validate_config(self) -> bool:
        """Validate auth configuration"""
        try:
            headers = await self.get_auth_header()
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://api.phonepe.com/v1/auth/ping", headers=headers
                )
                return response.status_code == 200
        except Exception:
            return False
