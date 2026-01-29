"""
Distributed Locks Service using Redis
Provides distributed locking mechanisms for critical sections
"""

import asyncio
import logging
import time
import uuid
from contextlib import asynccontextmanager
from datetime import datetime, timedelta
from typing import AsyncGenerator, Optional

from .redis_core.client import get_redis

logger = logging.getLogger(__name__)


class DistributedLock:
    """
    Distributed lock implementation using Redis

    Provides mutex-like behavior across multiple processes/instances
    """

    def __init__(
        self,
        key: str,
        timeout: int = 30,
        retry_delay: float = 0.1,
        max_retries: int = 50,
    ):
        """
        Initialize distributed lock

        Args:
            key: Lock key (must be unique per resource)
            timeout: Lock timeout in seconds
            retry_delay: Delay between retry attempts in seconds
            max_retries: Maximum number of retry attempts
        """
        self.key = f"lock:{key}"
        self.timeout = timeout
        self.retry_delay = retry_delay
        self.max_retries = max_retries
        self.redis = get_redis()
        self.identifier = str(uuid.uuid4())
        self.acquired = False

    async def acquire(self) -> bool:
        """
        Acquire the lock

        Returns:
            True if lock acquired successfully, False otherwise
        """
        start_time = time.time()

        for attempt in range(self.max_retries):
            try:
                # Try to acquire lock using SET NX EX
                result = await self.redis.set(
                    self.key, self.identifier, ex=self.timeout
                )

                if result:  # Lock acquired
                    self.acquired = True
                    logger.info(
                        f"Lock acquired: {self.key} "
                        f"(attempt {attempt + 1}, {time.time() - start_time:.2f}s)"
                    )
                    return True

                # Check if we already own the lock
                current_value = await self.redis.get(self.key)
                if current_value == self.identifier:
                    self.acquired = True
                    return True

                # Lock not acquired, wait and retry
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)

            except Exception as e:
                logger.error(f"Error acquiring lock (attempt {attempt + 1}): {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay)

        logger.warning(
            f"Failed to acquire lock: {self.key} "
            f"after {self.max_retries} attempts ({time.time() - start_time:.2f}s)"
        )
        return False

    async def release(self) -> bool:
        """
        Release the lock

        Returns:
            True if lock released successfully, False otherwise
        """
        if not self.acquired:
            logger.warning(f"Attempting to release unacquired lock: {self.key}")
            return False

        try:
            # Use Lua script for atomic release
            lua_script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            else
                return 0
            end
            """

            # For Upstash Redis, we'll use a simpler approach
            current_value = await self.redis.get(self.key)
            if current_value == self.identifier:
                await self.redis.delete(self.key)
                self.acquired = False
                logger.info(f"Lock released: {self.key}")
                return True
            else:
                logger.warning(
                    f"Lock release failed - not owner: {self.key} "
                    f"(expected: {self.identifier}, got: {current_value})"
                )
                return False

        except Exception as e:
            logger.error(f"Error releasing lock: {e}")
            return False

    async def extend(self, additional_time: int = 30) -> bool:
        """
        Extend the lock timeout

        Args:
            additional_time: Additional time in seconds

        Returns:
            True if extended successfully, False otherwise
        """
        if not self.acquired:
            logger.warning(f"Attempting to extend unacquired lock: {self.key}")
            return False

        try:
            current_value = await self.redis.get(self.key)
            if current_value == self.identifier:
                # Set new expiration
                await self.redis.expire(self.key, additional_time)
                logger.info(f"Lock extended: {self.key} (+{additional_time}s)")
                return True
            else:
                logger.warning(f"Lock extend failed - not owner: {self.key}")
                return False

        except Exception as e:
            logger.error(f"Error extending lock: {e}")
            return False

    async def is_locked(self) -> bool:
        """Check if the lock is currently held"""
        try:
            value = await self.redis.get(self.key)
            return value is not None
        except Exception as e:
            logger.error(f"Error checking lock status: {e}")
            return False

    async def get_lock_info(self) -> Optional[dict]:
        """Get information about the current lock"""
        try:
            value = await self.redis.get(self.key)
            ttl = await self.redis.ttl(self.key)

            if value:
                return {
                    "key": self.key,
                    "owner": value,
                    "is_mine": value == self.identifier,
                    "ttl_seconds": ttl,
                    "timestamp": datetime.now().isoformat(),
                }
            return None

        except Exception as e:
            logger.error(f"Error getting lock info: {e}")
            return None

    async def __aenter__(self):
        """Async context manager entry"""
        if await self.acquire():
            return self
        else:
            raise TimeoutError(f"Failed to acquire lock: {self.key}")

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.release()


class LockManager:
    """
    Manager for multiple distributed locks
    """

    def __init__(self):
        self.redis = get_redis()
        self.active_locks: dict[str, DistributedLock] = {}

    async def create_lock(
        self,
        resource: str,
        timeout: int = 30,
        retry_delay: float = 0.1,
        max_retries: int = 50,
    ) -> DistributedLock:
        """Create a new distributed lock"""
        lock = DistributedLock(
            key=resource,
            timeout=timeout,
            retry_delay=retry_delay,
            max_retries=max_retries,
        )
        self.active_locks[resource] = lock
        return lock

    async def acquire_lock(self, resource: str, timeout: int = 30) -> bool:
        """Acquire a lock for a resource"""
        if resource not in self.active_locks:
            await self.create_lock(resource, timeout)

        return await self.active_locks[resource].acquire()

    async def release_lock(self, resource: str) -> bool:
        """Release a lock for a resource"""
        if resource in self.active_locks:
            success = await self.active_locks[resource].release()
            if success:
                del self.active_locks[resource]
            return success
        return False

    async def release_all_locks(self) -> int:
        """Release all active locks"""
        released_count = 0
        for resource in list(self.active_locks.keys()):
            if await self.release_lock(resource):
                released_count += 1
        return released_count

    async def get_active_locks(self) -> dict[str, dict]:
        """Get information about all active locks"""
        locks_info = {}
        for resource, lock in self.active_locks.items():
            info = await lock.get_lock_info()
            if info:
                locks_info[resource] = info
        return locks_info

    async def cleanup_expired_locks(self) -> int:
        """Clean up expired locks (maintenance task)"""
        try:
            # Find all lock keys
            lock_keys = await self.redis.keys("lock:*")
            cleaned = 0

            for key in lock_keys:
                ttl = await self.redis.ttl(key)
                if ttl == -1:  # No expiration set, set one
                    await self.redis.expire(key, 3600)  # 1 hour default
                elif ttl == -2:  # Key doesn't exist (shouldn't happen)
                    continue
                elif ttl <= 0:  # Expired
                    await self.redis.delete(key)
                    cleaned += 1

            logger.info(f"Cleaned up {cleaned} expired locks")
            return cleaned

        except Exception as e:
            logger.error(f"Error cleaning up expired locks: {e}")
            return 0


# Global lock manager instance
_lock_manager: Optional[LockManager] = None


def get_lock_manager() -> LockManager:
    """Get the global lock manager instance"""
    global _lock_manager
    if _lock_manager is None:
        _lock_manager = LockManager()
    return _lock_manager


# Convenience functions
async def with_lock(resource: str, timeout: int = 30, func=None, *args, **kwargs):
    """
    Execute a function within a distributed lock

    Args:
        resource: Resource to lock
        timeout: Lock timeout in seconds
        func: Function to execute
        *args, **kwargs: Arguments to pass to function

    Returns:
        Function result if lock acquired, None otherwise
    """
    lock_manager = get_lock_manager()

    async with await lock_manager.create_lock(resource, timeout) as lock:
        if func:
            if asyncio.iscoroutinefunction(func):
                return await func(*args, **kwargs)
            else:
                return func(*args, **kwargs)
        return lock


@asynccontextmanager
async def distributed_lock(resource: str, timeout: int = 30):
    """
    Context manager for distributed locks

    Usage:
        async with distributed_lock("my_resource", timeout=30):
            # Critical section code
            pass
    """
    lock_manager = get_lock_manager()
    lock = await lock_manager.create_lock(resource, timeout)

    try:
        if await lock.acquire():
            yield lock
        else:
            raise TimeoutError(f"Failed to acquire lock for resource: {resource}")
    finally:
        await lock.release()
