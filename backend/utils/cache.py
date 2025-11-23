"""
Redis-based caching layer for RaptorFlow
"""

import json
import hashlib
from typing import Any, Optional
import redis.asyncio as redis
from backend.config.settings import get_settings
import structlog

settings = get_settings()

logger = structlog.get_logger()


class CacheClient:
    """Async Redis cache client"""
    
    def __init__(self):
        self.redis: Optional[redis.Redis] = None
        
    async def connect(self):
        """Establish Redis connection"""
        try:
            self.redis = await redis.from_url(
                settings.REDIS_URL,
                max_connections=settings.REDIS_MAX_CONNECTIONS,
                socket_timeout=settings.REDIS_SOCKET_TIMEOUT,
                decode_responses=True
            )
            await self.redis.ping()
            logger.info("Redis cache connected")
        except Exception as e:
            logger.error("Failed to connect to Redis", error=str(e))
            raise
            
    async def disconnect(self):
        """Close Redis connection"""
        if self.redis:
            await self.redis.close()
            logger.info("Redis cache disconnected")
    
    def _generate_key(self, prefix: str, identifier: str) -> str:
        """Generate cache key with prefix"""
        # Hash long identifiers to keep keys manageable
        if len(identifier) > 100:
            identifier = hashlib.md5(identifier.encode()).hexdigest()
        return f"raptorflow:{prefix}:{identifier}"
    
    async def get(self, prefix: str, identifier: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.redis:
            return None
            
        key = self._generate_key(prefix, identifier)
        try:
            value = await self.redis.get(key)
            if value:
                logger.debug("Cache hit", key=key)
                return json.loads(value)
            logger.debug("Cache miss", key=key)
            return None
        except Exception as e:
            logger.warning("Cache get failed", key=key, error=str(e))
            return None
    
    async def set(
        self, 
        prefix: str, 
        identifier: str, 
        value: Any, 
        ttl: Optional[int] = None
    ) -> bool:
        """Set value in cache with optional TTL (seconds)"""
        if not self.redis:
            return False
            
        key = self._generate_key(prefix, identifier)
        try:
            serialized = json.dumps(value)
            if ttl:
                await self.redis.setex(key, ttl, serialized)
            else:
                await self.redis.set(key, serialized)
            logger.debug("Cache set", key=key, ttl=ttl)
            return True
        except Exception as e:
            logger.warning("Cache set failed", key=key, error=str(e))
            return False
    
    async def delete(self, prefix: str, identifier: str) -> bool:
        """Delete value from cache"""
        if not self.redis:
            return False
            
        key = self._generate_key(prefix, identifier)
        try:
            await self.redis.delete(key)
            logger.debug("Cache deleted", key=key)
            return True
        except Exception as e:
            logger.warning("Cache delete failed", key=key, error=str(e))
            return False
    
    async def exists(self, prefix: str, identifier: str) -> bool:
        """Check if key exists in cache"""
        if not self.redis:
            return False
            
        key = self._generate_key(prefix, identifier)
        try:
            return await self.redis.exists(key) > 0
        except Exception as e:
            logger.warning("Cache exists check failed", key=key, error=str(e))
            return False


# Global cache instance
<<<<<<< HEAD
cache = CacheClient()
redis_cache = cache  # Alias for backward compatibility
=======
redis_cache = CacheClient()
# Legacy alias for backward compatibility
cache = redis_cache
>>>>>>> main


# Convenience functions for specific cache types
async def cache_research(query: str, result: Any) -> bool:
    """Cache research results for 7 days"""
    return await redis_cache.set("research", query, result, settings.CACHE_TTL_RESEARCH)


async def get_cached_research(query: str) -> Optional[Any]:
    """Get cached research results"""
    return await redis_cache.get("research", query)


async def cache_persona(icp_id: str, persona: Any) -> bool:
    """Cache persona data for 30 days"""
    return await redis_cache.set("persona", icp_id, persona, settings.CACHE_TTL_PERSONA)


async def get_cached_persona(icp_id: str) -> Optional[Any]:
    """Get cached persona data"""
    return await redis_cache.get("persona", icp_id)


async def cache_content(content_id: str, content: Any) -> bool:
    """Cache generated content for 24 hours"""
    return await redis_cache.set("content", content_id, content, settings.CACHE_TTL_CONTENT)


async def get_cached_content(content_id: str) -> Optional[Any]:
    """Get cached content"""
    return await redis_cache.get("content", content_id)


class RedisCache:
    """
    Convenience wrapper for redis cache with simplified API.
    Used by content agents for caching generated content.
    """

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache using full key"""
        if not cache.redis:
            return None
        try:
            value = await cache.redis.get(f"raptorflow:{key}")
            if value:
                return json.loads(value)
            return None
        except Exception as e:
            logger.warning("Redis get failed", key=key, error=str(e))
            return None

    async def set(self, key: str, value: Any, ttl: Optional[int] = None) -> bool:
        """Set value in cache with optional TTL"""
        if not cache.redis:
            return False
        try:
            serialized = json.dumps(value)
            full_key = f"raptorflow:{key}"
            if ttl:
                await cache.redis.setex(full_key, ttl, serialized)
            else:
                await cache.redis.set(full_key, serialized)
            return True
        except Exception as e:
            logger.warning("Redis set failed", key=key, error=str(e))
            return False

    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        if not cache.redis:
            return False
        try:
            await cache.redis.delete(f"raptorflow:{key}")
            return True
        except Exception as e:
            logger.warning("Redis delete failed", key=key, error=str(e))
            return False


# Global redis_cache instance for content agents
redis_cache = RedisCache()

