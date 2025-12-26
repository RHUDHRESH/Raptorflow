import json
import logging
import os
from typing import Optional

import redis.asyncio as redis

from core.config import get_settings

logger = logging.getLogger("raptorflow.radar_cache")


class RadarCache:
    """Redis-backed cache for radar scan state and content snapshots."""

    def __init__(self):
        settings = get_settings()
        self.redis_url = settings.REDIS_URL or os.getenv("REDIS_URL")
        self.client = (
            redis.from_url(self.redis_url, decode_responses=True)
            if self.redis_url
            else None
        )

    async def get_source_content(self, tenant_id: str, source_id: str) -> Optional[str]:
        if not self.client:
            return None
        return await self.client.get(self._source_content_key(tenant_id, source_id))

    async def set_source_content(
        self,
        tenant_id: str,
        source_id: str,
        content: str,
        ttl_seconds: int = 7 * 24 * 3600,
    ) -> None:
        if not self.client:
            return
        await self.client.setex(
            self._source_content_key(tenant_id, source_id), ttl_seconds, content
        )

    async def set_scheduler_status(
        self, tenant_id: str, payload: dict, ttl_seconds: int = 3600
    ) -> None:
        if not self.client:
            return
        await self.client.setex(
            self._scheduler_status_key(tenant_id),
            ttl_seconds,
            json.dumps(payload),
        )

    async def get_scheduler_status(self, tenant_id: str) -> Optional[dict]:
        if not self.client:
            return None
        raw = await self.client.get(self._scheduler_status_key(tenant_id))
        if not raw:
            return None
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            logger.warning(
                "Failed to decode scheduler status payload for %s", tenant_id
            )
            return None

    async def close(self) -> None:
        if self.client:
            await self.client.close()

    @staticmethod
    def _source_content_key(tenant_id: str, source_id: str) -> str:
        return f"radar:source:content:{tenant_id}:{source_id}"

    @staticmethod
    def _scheduler_status_key(tenant_id: str) -> str:
        return f"radar:scheduler:status:{tenant_id}"
