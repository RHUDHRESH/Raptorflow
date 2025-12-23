import os
from upstash_redis import Redis


def get_cache_client() -> Redis:
    """
    Returns an initialized Upstash Redis client.
    Expects UPSTASH_REDIS_REST_URL and UPSTASH_REDIS_REST_TOKEN in env.
    """
    return Redis.from_env()


class CacheManager:
    """
    High-level manager for Blackbox caching, rate limiting, and 
    real-time performance tracking.
    """
    def __init__(self, client: Redis = None):
        self.client = client or get_cache_client()

    def set_with_expiry(self, key: str, value: str, expiry_seconds: int = 3600):
        return self.client.set(key, value, ex=expiry_seconds)

    def get(self, key: str):
        return self.client.get(key)
