import os
from upstash_redis.asyncio import Redis
from typing import Optional

class RaptorCache:
    """
    SOTA Cache Manager for distributed agentic systems.
    Uses Upstash Redis (HTTP) for edge-friendly performance.
    """
    _instance: Optional['RaptorCache'] = None
    _client: Optional[Redis] = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(RaptorCache, cls).__new__(cls)
        return cls._instance

    @property
    def client(self) -> Redis:
        if self._client is None:
            url = os.getenv("UPSTASH_REDIS_REST_URL")
            token = os.getenv("UPSTASH_REDIS_REST_TOKEN")
            if not url or not token:
                # In SOTA systems, we log a warning but allow degradation if cache is missing
                # For now, we initialize with empty strings which will fail on use
                print("WARNING: Upstash Redis credentials missing.")
            self._client = Redis(url=url, token=token)
        return self._client

def get_cache() -> Redis:
    """Convenience accessor for the global cache client."""
    return RaptorCache().client
