"""
Distributed locks using Redis.
Provides mutex-like functionality for distributed systems.

import asyncio
import logging
import time
import uuid
from .contextlib import asynccontextmanager
from typing import Optional
from .client import RedisClient
logger = logging.getLogger(__name__)
class DistributedLock:
    """Redis-based distributed lock implementation."""
    def __init__(self, redis_client: RedisClient = None):
        """Initialize distributed lock."""
        self.redis = redis_client or RedisClient()
        self._locks = {}  # Track active locks
    async def acquire(
        self, resource: str, timeout: int = 30, retry_delay: float = 0.1
    ) -> bool:
        """
        Acquire a lock for the specified resource.
        Args:
            resource: Resource identifier to lock
            timeout: Lock timeout in seconds
            retry_delay: Delay between retry attempts in seconds
        Returns:
            True if lock acquired, False otherwise
        lock_key = f"lock:{resource}"
        lock_value = f"lock:{uuid.uuid4()}"
        start_time = time.time()
        while True:
            try:
                # Try to acquire lock atomically
                acquired = await self.redis.set(
                    lock_key, lock_value, ex=timeout, nx=True
                )
                if acquired:
                    self._locks[resource] = lock_value
                    logger.debug(f"Lock acquired for resource: {resource}")
                    return True
                # Check if we should retry
                if time.time() - start_time >= timeout:
                    logger.debug(
                        f"Failed to acquire lock for resource: {resource} (timeout)"
                    )
                    return False
                # Wait before retrying
                await asyncio.sleep(retry_delay)
            except Exception as e:
                logger.error(f"Error acquiring lock for {resource}: {e}")
                raise
    async def release(self, resource: str) -> bool:
        Release a lock for the specified resource.
            resource: Resource identifier to unlock
            True if lock released, False otherwise
        try:
            # Check if we own this lock
            if resource not in self._locks:
                logger.warning(f"Attempted to release unowned lock: {resource}")
                return False
            lock_value = self._locks[resource]
            # Use Lua script to safely release lock
            script = """
            if redis.call("GET", KEYS[1]) == ARGV[1] then
                return redis.call("DEL", KEYS[1])
            else
                return 0
            end
            """
            result = await self.redis.eval(script, 1, lock_key, lock_value)
            released = bool(result)
            if released:
                del self._locks[resource]
                logger.debug(f"Lock released for resource: {resource}")
            else:
                logger.warning(
                    f"Failed to release lock for {resource} (not owner or expired)"
            return released
        except Exception as e:
            logger.error(f"Error releasing lock for {resource}: {e}")
            raise
    async def extend(self, resource: str, seconds: int) -> bool:
        Extend the timeout of an existing lock.
            resource: Resource identifier
            seconds: Additional seconds to extend
            True if lock extended, False otherwise
                logger.warning(f"Attempted to extend unowned lock: {resource}")
            # Use Lua script to safely extend lock
                return redis.call("EXPIRE", KEYS[1], ARGV[2])
            result = await self.redis.eval(script, 1, lock_key, lock_value, seconds)
            extended = bool(result)
            if extended:
                logger.debug(f"Lock extended for resource: {resource} by {seconds}s")
                    f"Failed to extend lock for {resource} (not owner or expired)"
            return extended
            logger.error(f"Error extending lock for {resource}: {e}")
    async def is_locked(self, resource: str) -> bool:
        Check if a resource is currently locked.
            True if locked, False otherwise
            exists = await self.redis.exists(lock_key)
            return bool(exists)
            logger.error(f"Error checking lock status for {resource}: {e}")
    async def get_lock_info(self, resource: str) -> Optional[dict]:
        Get information about a lock.
            Lock information dict or None if not locked
            lock_value = await self.redis.get(lock_key)
            ttl = await self.redis.ttl(lock_key)
            if lock_value:
                return {
                    "resource": resource,
                    "lock_value": lock_value,
                    "ttl": ttl,
                    "is_owned": resource in self._locks
                    and self._locks[resource] == lock_value,
                }
                return None
            logger.error(f"Error getting lock info for {resource}: {e}")
    async def force_release(self, resource: str) -> bool:
        Force release a lock (dangerous - use only in emergencies).
            result = await self.redis.delete(lock_key)
                # Remove from tracking if present
                self._locks.pop(resource, None)
                logger.warning(f"Force released lock for resource: {resource}")
            logger.error(f"Error force releasing lock for {resource}: {e}")
    async def cleanup_expired_locks(self) -> int:
        Clean up expired locks from tracking.
            Number of locks cleaned up
        cleaned = 0
        expired_resources = []
        for resource, lock_value in self._locks.items():
            lock_key = f"lock:{resource}"
                exists = await self.redis.exists(lock_key)
                if not exists:
                    expired_resources.append(resource)
                logger.error(f"Error checking lock {resource}: {e}")
                expired_resources.append(resource)  # Remove on error
        for resource in expired_resources:
            del self._locks[resource]
            cleaned += 1
        if cleaned > 0:
            logger.info(f"Cleaned up {cleaned} expired locks")
        return cleaned
    def get_active_locks(self) -> dict:
        Get all actively tracked locks.
            Dictionary of resource -> lock_value
        return self._locks.copy()
    @asynccontextmanager
    async def __call__(
    ):
        Context manager for acquiring and releasing locks.
            retry_delay: Delay between retry attempts
        Usage:
            async with distributed_lock("my_resource", timeout=30):
                # Critical section here
                pass
        acquired = await self.acquire(resource, timeout, retry_delay)
        if not acquired:
            raise RuntimeError(f"Failed to acquire lock for resource: {resource}")
            yield
        finally:
            await self.release(resource)
class LockPool:
    """Pool of distributed locks for managing multiple resources."""
    def __init__(self, redis_client: RedisClient = None, max_locks: int = 100):
        """Initialize lock pool."""
        self.max_locks = max_locks
        self.locks = {}
    async def acquire_lock(
        Acquire a lock from the pool.
        if resource in self.locks:
            return self.locks[resource].acquire(resource, timeout, retry_delay)
        if len(self.locks) >= self.max_locks:
            logger.warning(f"Lock pool at maximum capacity: {self.max_locks}")
            return False
        lock = DistributedLock(self.redis)
        acquired = await lock.acquire(resource, timeout, retry_delay)
        if acquired:
            self.locks[resource] = lock
            logger.debug(f"Added lock to pool for resource: {resource}")
        return acquired
    async def release_lock(self, resource: str) -> bool:
        Release a lock and return it to the pool.
        if resource not in self.locks:
        lock = self.locks[resource]
        released = await lock.release(resource)
        if released:
            del self.locks[resource]
            logger.debug(f"Removed lock from pool for resource: {resource}")
        return released
    async def get_pool_status(self) -> dict:
        Get status of the lock pool.
            Pool status information
        return {
            "total_locks": len(self.locks),
            "max_locks": self.max_locks,
            "utilization": len(self.locks) / self.max_locks,
            "active_resources": list(self.locks.keys()),
        }
    async def cleanup_pool(self) -> int:
        Clean up expired locks from the pool.
        for resource, lock in self.locks.items():
                if not await lock.is_locked(resource):
                expired_resources.append(resource)
        if expired_resources:
            logger.info(f"Cleaned up {len(expired_resources)} expired locks from pool")
        return len(expired_resources)
# Global distributed lock instance
_distributed_lock: DistributedLock = None
def get_distributed_lock(redis_client: RedisClient = None) -> DistributedLock:
    """Get the global distributed lock instance."""
    global _distributed_lock
    if _distributed_lock is None or redis_client:
        _distributed_lock = DistributedLock(redis_client)
    return _distributed_lock
# Convenience functions
async def acquire_lock(
    resource: str, timeout: int = 30, retry_delay: float = 0.1
) -> bool:
    """Acquire a distributed lock."""
    lock = get_distributed_lock()
    return await lock.acquire(resource, timeout, retry_delay)
async def release_lock(resource: str) -> bool:
    """Release a distributed lock."""
    return await lock.release(resource)
async def extend_lock(resource: str, seconds: int) -> bool:
    """Extend a distributed lock."""
    return await lock.extend(resource, seconds)
@asynccontextmanager
async def distributed_lock(resource: str, timeout: int = 30, retry_delay: float = 0.1):
    """Context manager for distributed locks."""
    async with lock(resource, timeout, retry_delay):
        yield
