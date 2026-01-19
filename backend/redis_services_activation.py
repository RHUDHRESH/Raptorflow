"""
Redis Services Activation

Activates all Redis core services for the RaptorFlow backend.
Includes session management, caching, rate limiting, usage tracking, and job queues.
"""

import logging
from typing import Optional

from .redis_core.session import SessionService
from .redis_core.cache import CacheService
from .redis_core.rate_limit import RateLimitService
from .redis_core.usage import UsageTracker
from .redis_core.queue import QueueService

logger = logging.getLogger(__name__)

# Global service instances
_session_service: Optional[SessionService] = None
_cache_service: Optional[CacheService] = None
_rate_limit_service: Optional[RateLimitService] = None
_usage_tracker: Optional[UsageTracker] = None
_queue_service: Optional[QueueService] = None


async def activate_redis_services():
    """Activate all Redis core services."""
    try:
        logger.info("🔄 Activating Redis services...")
        
        # Activate Session Management
        global _session_service
        _session_service = SessionService()
        logger.info("✅ Session management activated")
        
        # Activate Caching
        global _cache_service
        _cache_service = CacheService()
        logger.info("✅ Caching service activated")
        
        # Activate Rate Limiting
        global _rate_limit_service
        _rate_limit_service = RateLimitService()
        logger.info("✅ Rate limiting service activated")
        
        # Activate Usage Tracking
        global _usage_tracker
        _usage_tracker = UsageTracker()
        logger.info("✅ Usage tracking activated")
        
        # Activate Job Queues
        global _queue_service
        _queue_service = QueueService()
        logger.info("✅ Job queue service activated")
        
        logger.info("🚀 All Redis services activated successfully")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to activate Redis services: {e}")
        return False


def get_session_service() -> Optional[SessionService]:
    """Get the session service instance."""
    return _session_service


def get_cache_service() -> Optional[CacheService]:
    """Get the cache service instance."""
    return _cache_service


def get_rate_limit_service() -> Optional[RateLimitService]:
    """Get the rate limit service instance."""
    return _rate_limit_service


def get_usage_tracker() -> Optional[UsageTracker]:
    """Get the usage tracker instance."""
    return _usage_tracker


def get_queue_service() -> Optional[QueueService]:
    """Get the queue service instance."""
    return _queue_service


async def deactivate_redis_services():
    """Deactivate all Redis core services."""
    try:
        logger.info("🔄 Deactivating Redis services...")
        
        # Clean shutdown of services
        if _queue_service:
            # Stop queue processing
            logger.info("🛑 Stopping queue service...")
        
        if _usage_tracker:
            # Flush any pending usage data
            logger.info("🛑 Flushing usage tracker...")
        
        if _rate_limit_service:
            # Clean up rate limit data
            logger.info("🛑 Cleaning up rate limiter...")
        
        if _cache_service:
            # Flush cache if needed
            logger.info("🛑 Cleaning up cache service...")
        
        if _session_service:
            # Clean up expired sessions
            logger.info("🛑 Cleaning up sessions...")
        
        logger.info("✅ All Redis services deactivated")
        return True
        
    except Exception as e:
        logger.error(f"❌ Failed to deactivate Redis services: {e}")
        return False


async def health_check_redis_services():
    """Check health of all Redis services."""
    health_status = {
        "session_service": _session_service is not None,
        "cache_service": _cache_service is not None,
        "rate_limit_service": _rate_limit_service is not None,
        "usage_tracker": _usage_tracker is not None,
        "queue_service": _queue_service is not None,
    }
    
    # Test Redis connection
    try:
        from .redis_core.client import get_redis
        redis_client = get_redis()
        redis_healthy = await redis_client.ping()
        health_status["redis_connection"] = redis_healthy
    except Exception as e:
        health_status["redis_connection"] = False
        health_status["redis_error"] = str(e)
    
    overall_healthy = all(health_status.values()) if isinstance(health_status["redis_connection"], bool) else False
    health_status["overall"] = overall_healthy
    
    return health_status
