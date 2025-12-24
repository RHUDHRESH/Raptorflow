import logging
from typing import Any

from backend.core.cache import get_cache_manager

logger = logging.getLogger("raptorflow.core.governance")


class RateLimiter:
    """
    Industrial-grade Rate Limiter.
    Uses Upstash Redis for distributed fixed-window limiting.
    """

    def __init__(self, cache: Any = None, limit: int = 100, window: int = 60):
        # Use .client from CacheManager to get the raw upstash-redis client
        manager = get_cache_manager()
        self.cache = cache or (manager.client if manager else None)
        self.limit = limit
        self.window = window  # In seconds

    async def check_rate_limit(self, tenant_id: str, action: str):
        """Checks if the rate limit is exceeded for a given tenant/action."""
        if not self.cache:
            return  # Degrade gracefully

        key = f"ratelimit:{tenant_id}:{action}"

        current_val_raw = self.cache.get(key)
        current_val = int(current_val_raw) if current_val_raw else 0

        if current_val >= self.limit:
            logger.warning(f"Rate limit exceeded for {tenant_id} on {action}")
            raise Exception(
                f"Rate limit exceeded: {current_val}/{self.limit} for {action}"
            )

        # Increment and set TTL if new
        self.cache.incr(key)
        if current_val == 0:
            self.cache.expire(key, self.window)


class CostGovernor:
    """
    SOTA Cost Governance.
    Tracks token usage and estimated dollar burn per tenant.
    """

    PRICING = {
        "gemini-2.0-flash": {"input": 0.0000001, "output": 0.0000004},
        "gemini-2.0-flash-lite": {"input": 0.000000075, "output": 0.0000003},
        "gemini-2.5-flash-lite": {
            "input": 0.000000075,
            "output": 0.0000003,
        },
        "gemini-2.5-flash": {"input": 0.0000001, "output": 0.0000004},
        "default": {"input": 0.000001, "output": 0.000002},
    }

    def __init__(self, cache: Any = None):
        manager = get_cache_manager()
        self.cache = cache or (manager.client if manager else None)

    async def log_cost(self, tenant_id: str, tokens: int, model: str = "default"):
        """Logs estimated cost to Redis for real-time monitoring."""
        if not self.cache:
            return

        pricing = self.PRICING.get(model, self.PRICING["default"])
        # Simplified estimate: assume 70% input / 30% output
        est_cost = (tokens * 0.7 * pricing["input"]) + (
            tokens * 0.3 * pricing["output"]
        )

        key = f"cost:{tenant_id}:total"
        # Store as micro-dollars to avoid float precision issues in Redis incr
        micro_cost = int(est_cost * 1_000_000)
        self.cache.incrby(key, micro_cost)

        logger.info(f"Logged cost for {tenant_id}: {est_cost:.6f} USD")

    async def get_total_cost(self, tenant_id: str) -> float:
        """Retrieves total estimated cost in USD."""
        if not self.cache:
            return 0.0

        key = f"cost:{tenant_id}:total"
        micro_cost_raw = self.cache.get(key)
        micro_cost = int(micro_cost_raw) if micro_cost_raw else 0
        return micro_cost / 1_000_000.0
