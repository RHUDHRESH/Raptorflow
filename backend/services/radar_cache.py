"""
Radar Cache - Redis-backed state management for signal discovery
"""

import logging
from typing import Any, Dict, Optional

from core.cache import get_cache_manager

logger = logging.getLogger("raptorflow.radar_cache")


class RadarCache:
    """
    Cache manager for competitive intelligence radar.
    Handles ephemeral state like crawl results, deduplication hashes, and scheduler status.
    """

    def __init__(self):
        self.client = get_cache_manager()

    async def get_source_content(self, tenant_id: str, source_id: str) -> Optional[str]:
        """Retrieves cached content hash for change detection."""
        key = f"radar:{tenant_id}:source:{source_id}:content"
        return self.client.get(key)

    async def set_source_content(
        self, tenant_id: str, source_id: str, content: str, ttl: int = 86400 * 7
    ):
        """Caches content hash for change detection."""
        key = f"radar:{tenant_id}:source:{source_id}:content"
        self.client.set_with_expiry(key, content, expiry_seconds=ttl)

    async def get_scheduler_status(self, tenant_id: str) -> Optional[Dict[str, Any]]:
        """Retrieves automated scan scheduler status."""
        key = f"radar:{tenant_id}:scheduler:status"
        return self.client.get_json(key)

    async def set_scheduler_status(
        self, tenant_id: str, status: Dict[str, Any], ttl: int = 3600
    ):
        """Updates automated scan scheduler status."""
        key = f"radar:{tenant_id}:scheduler:status"
        self.client.set_json(key, status, expiry_seconds=ttl)
