"""
Redis-based caching layer for RaptorFlow
Includes distributed locks, rate limiting, and cache management.
"""

import json
import hashlib
import uuid
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

    async def incr(self, key: str, expire: Optional[int] = None) -> int:
        """
        Increment counter in cache (for rate limiting). Returns new count.

        SECURITY: Uses Lua script for atomic increment with expiry to prevent race conditions.
        Ensures expiry is set atomically on first increment without gap vulnerabilities.
        """
        if not self.redis:
            return 1

        try:
            if expire:
                # Use Lua script for atomic increment with expiry
                # This prevents race condition between INCR and EXPIRE
                lua_script = """
local count = redis.call('incr', KEYS[1])
if count == 1 then
    redis.call('expire', KEYS[1], ARGV[1])
end
return count
"""
                # Register and execute Lua script atomically
                script = self.redis.register_script(lua_script)
                count = await script(keys=[key], args=[expire])
                return int(count)
            else:
                # Simple increment without expiry
                count = await self.redis.incr(key)
                return count
        except Exception as e:
            logger.warning("Cache incr failed", key=key, error=str(e))
            return 1

    async def ping(self) -> bool:
        """Check Redis connection"""
        if not self.redis:
            return False
        try:
            await self.redis.ping()
            return True
        except Exception as e:
            logger.warning("Redis ping failed", error=str(e))
            return False

    # ==================== DISTRIBUTED LOCKS ====================
    # For preventing race conditions in payment processing, webhooks, etc.

    async def acquire_lock(self, key: str, ttl: int = 30, token: Optional[str] = None) -> Optional[str]:
        """
        Acquire a distributed lock with atomic SET NX.

        Args:
            key: Lock key (e.g., 'lock:webhook:transaction_id')
            ttl: Lock TTL in seconds (default 30)
            token: Optional unique token. If None, generates UUID.

        Returns:
            Lock token if acquired, None if lock already held by another process

        Usage:
            lock_token = await redis_cache.acquire_lock('lock:webhook:MT123', ttl=30)
            if lock_token:
                try:
                    # Process payment webhook
                finally:
                    await redis_cache.release_lock('lock:webhook:MT123', lock_token)
        """
        if not self.redis:
            return None

        try:
            # Generate unique token if not provided
            if not token:
                token = str(uuid.uuid4())

            # Use SET NX EX for atomic lock acquisition
            # SET (set), NX (only if not exists), EX (expire in seconds)
            lock_key = f"raptorflow:lock:{key}"
            acquired = await self.redis.set(
                lock_key,
                token,
                nx=True,  # Only set if key doesn't exist
                ex=ttl    # Expire in ttl seconds
            )

            if acquired:
                logger.debug("Lock acquired", key=key, token=token[:8], ttl=ttl)
                return token
            else:
                logger.debug("Lock already held", key=key)
                return None

        except Exception as e:
            logger.error("Failed to acquire lock", key=key, error=str(e))
            return None

    async def release_lock(self, key: str, token: str) -> bool:
        """
        Release a distributed lock (only if token matches).

        SECURITY: Uses Lua script to prevent accidental/malicious unlock by wrong process.

        Args:
            key: Lock key
            token: Lock token (must match to release)

        Returns:
            True if lock was released, False if token didn't match or lock doesn't exist
        """
        if not self.redis:
            return False

        try:
            lock_key = f"raptorflow:lock:{key}"

            # Lua script ensures atomic check-and-delete
            # Prevents process A from releasing process B's lock
            lua_script = """
if redis.call('get', KEYS[1]) == ARGV[1] then
    return redis.call('del', KEYS[1])
else
    return 0
end
"""
            script = self.redis.register_script(lua_script)
            deleted = await script(keys=[lock_key], args=[token])

            if deleted:
                logger.debug("Lock released", key=key, token=token[:8])
                return True
            else:
                logger.warning("Lock release failed - token mismatch or lock expired", key=key)
                return False

        except Exception as e:
            logger.error("Failed to release lock", key=key, error=str(e))
            return False

    async def lock_exists(self, key: str) -> bool:
        """
        Check if a lock exists.

        Args:
            key: Lock key

        Returns:
            True if lock is currently held, False otherwise
        """
        if not self.redis:
            return False

        try:
            lock_key = f"raptorflow:lock:{key}"
            exists = await self.redis.exists(lock_key)
            return exists > 0
        except Exception as e:
            logger.warning("Lock exists check failed", key=key, error=str(e))
            return False

    async def extend_lock(self, key: str, token: str, additional_ttl: int = 10) -> bool:
        """
        Extend a lock's TTL (only if token matches).

        Args:
            key: Lock key
            token: Lock token (must match to extend)
            additional_ttl: Additional seconds to extend

        Returns:
            True if lock was extended, False if token didn't match
        """
        if not self.redis:
            return False

        try:
            lock_key = f"raptorflow:lock:{key}"

            # Lua script: check token and extend expire time
            lua_script = """
if redis.call('get', KEYS[1]) == ARGV[1] then
    return redis.call('expire', KEYS[1], ARGV[2])
else
    return 0
end
"""
            script = self.redis.register_script(lua_script)
            extended = await script(keys=[lock_key], args=[token, additional_ttl])

            if extended:
                logger.debug("Lock extended", key=key, token=token[:8], additional_ttl=additional_ttl)
                return True
            else:
                logger.warning("Lock extend failed - token mismatch or lock expired", key=key)
                return False

        except Exception as e:
            logger.error("Failed to extend lock", key=key, error=str(e))
            return False


redis_cache = CacheClient()
# Legacy alias for backward compatibility
cache = redis_cache


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
