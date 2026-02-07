import asyncio
import hashlib
import json
import logging
from typing import Any, Dict, List, Optional

from services.search.reddit_native import RedditNativeScraper
from services.search.searxng import SearXNGClient
from upstash_redis import Redis

from backend.config.settings import get_settings

logger = logging.getLogger("raptorflow.services.search.orchestrator")


class SOTASearchOrchestrator:
    """
    SOTA Search Orchestrator that aggregates results from multiple native sources.
    Includes deduplication and edge caching via Upstash Redis.
    """

    def __init__(self):
        self.settings = get_settings()
        self.searxng = SearXNGClient(base_url=self.settings.SEARXNG_URL)
        self.reddit = RedditNativeScraper()

        self.redis = None
        if self.settings.UPSTASH_REDIS_URL and self.settings.UPSTASH_REDIS_TOKEN:
            try:
                self.redis = Redis(
                    url=self.settings.UPSTASH_REDIS_URL,
                    token=self.settings.UPSTASH_REDIS_TOKEN,
                )
            except Exception as e:
                logger.warning(f"Failed to initialize Redis for Search: {e}")

    def _get_cache_key(self, query: str, limit: int) -> str:
        q_hash = hashlib.md5(f"{query}:{limit}".lower().strip().encode()).hexdigest()
        return f"sota_search:{q_hash}"

    async def query(self, text: str, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Aggregates results from SearXNG and Reddit in parallel.
        """
        if not text:
            return []

        # 1. Cache Check
        cache_key = self._get_cache_key(text, limit)
        if self.redis:
            try:
                cached = self.redis.get(cache_key)
                if cached:
                    return json.loads(cached) if isinstance(cached, str) else cached
            except Exception as e:
                logger.debug(f"Cache read failed: {e}")

        # 2. Parallel Aggregation
        tasks = [
            self.searxng.query(text, limit=limit),
            self.reddit.query(
                text, limit=limit // 2
            ),  # Reddit results are supplementary
        ]

        responses = await asyncio.gather(*tasks, return_exceptions=True)

        # 3. Deduplication & Merging
        all_results = []
        seen_urls = set()

        for engine_results in responses:
            if isinstance(engine_results, list):
                for res in engine_results:
                    # Normalize URL for deduplication
                    url = res.get("url", "").split("?")[0].rstrip("/")
                    if url and url not in seen_urls:
                        all_results.append(res)
                        seen_urls.add(url)
            elif isinstance(engine_results, Exception):
                logger.error(f"Engine query failed: {engine_results}")

        final_results = all_results[:limit]

        # 4. Cache Save (24h)
        if final_results and self.redis:
            try:
                self.redis.set(cache_key, json.dumps(final_results), ex=86400)
            except Exception as e:
                logger.debug(f"Cache write failed: {e}")

        return final_results

    async def close(self):
        await self.searxng.close()
        await self.reddit.close()
