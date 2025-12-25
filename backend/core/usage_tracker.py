import logging
import time

from backend.core.config import get_settings

logger = logging.getLogger("raptorflow.core.usage_tracker")


class UsageTracker:
    """
    Industrial Usage Tracking for AI Services.
    Tracks image generation and token usage.
    """

    def __init__(self):
        self.settings = get_settings()
        self._redis = None
        # Placeholder for local usage cache
        self._local_cache = {}

    async def _get_redis(self):
        if not self._redis and self.settings.UPSTASH_REDIS_REST_URL:
            try:
                from upstash_redis import Redis

                self._redis = Redis(
                    url=self.settings.UPSTASH_REDIS_REST_URL,
                    token=self.settings.UPSTASH_REDIS_REST_TOKEN,
                )
            except ImportError:
                logger.warning(
                    "upstash-redis not installed. Usage tracking will be local-only."
                )
        return self._redis

    async def check_quota(self, tenant_id: str, service_type: str = "image") -> bool:
        """Checks if the tenant has remaining quota for the service."""
        if not self.settings.ENABLE_USAGE_TRACKING:
            return True

        if service_type == "image":
            limit = self.settings.MONTHLY_IMAGE_QUOTA
            usage = await self.get_usage(tenant_id, service_type)
            return usage < limit

        return True

    async def get_usage(self, tenant_id: str, service_type: str = "image") -> int:
        """Retrieves current usage for a tenant."""
        redis = await self._get_redis()
        current_month = time.strftime("%Y-%m")
        key = f"usage:{tenant_id}:{service_type}:{current_month}"

        if redis:
            usage = redis.get(key)
            return int(usage) if usage else 0
        else:
            return self._local_cache.get(key, 0)

    async def track_usage(
        self, tenant_id: str, amount: int = 1, service_type: str = "image"
    ):
        """Increments usage for a tenant."""
        if not self.settings.ENABLE_USAGE_TRACKING:
            return

        redis = await self._get_redis()
        current_month = time.strftime("%Y-%m")
        key = f"usage:{tenant_id}:{service_type}:{current_month}"

        if redis:
            if amount == 1:
                redis.incr(key)
            else:
                redis.incrby(key, amount)
        else:
            self._local_cache[key] = self._local_cache.get(key, 0) + amount

        logger.info(
            f"Tracked {amount} {service_type} usage for tenant {tenant_id}. "
            f"New total: {await self.get_usage(tenant_id, service_type)}"
        )


# Global instance
usage_tracker = UsageTracker()
