from upstash_redis import Redis


from backend.core.config import get_settings


def get_cache_client() -> Redis:
    """
    Returns an initialized Upstash Redis client.
    Uses GCP Secret Manager support via get_settings().
    """
    settings = get_settings()
    return Redis(
        url=settings.UPSTASH_REDIS_REST_URL, token=settings.UPSTASH_REDIS_REST_TOKEN
    )


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
