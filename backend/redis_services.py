"""
Redis services wrapper to avoid import conflicts.
This file prevents collision with the standard redis package.
"""

from backend.redis_core.cache import CacheService

# Import our Redis services with explicit paths to avoid conflicts
from backend.redis_core.client import RedisClient, get_redis
from backend.redis_core.queue import QueueService
from backend.redis_core.rate_limit import RateLimitService
from backend.redis_core.session import SessionService
from backend.redis_core.usage import UsageTracker

# Re-export with clear names to avoid confusion
__all__ = [
    "RedisClient",
    "get_redis_client",  # Renamed to avoid conflict
    "SessionService",
    "CacheService",
    "RateLimitService",
    "QueueService",
    "UsageTracker",
]


def get_redis_client():
    """Get Redis client - renamed to avoid import conflicts"""
    return get_redis()
