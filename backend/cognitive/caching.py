"""
Cognitive Cache for Integration Components

Intelligent caching system for cognitive processing results.
Implements PROMPT 67 from STREAM_3_COGNITIVE_ENGINE.
"""

import asyncio
import hashlib
import json
import time
import uuid
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Union

from ..models import ExecutionPlan, PerceivedInput, ReflectionResult


class CachePolicy(Enum):
    """Cache eviction policies."""

    LRU = "lru"
    LFU = "lfu"
    FIFO = "fifo"
    TTL = "ttl"


class CacheStatus(Enum):
    """Status of cache entries."""

    ACTIVE = "active"
    EXPIRED = "expired"
    EVICTED = "evicted"
    INVALIDATED = "invalidated"


@dataclass
class CacheEntry:
    """A cache entry."""

    key: str
    value: Any
    created_at: datetime
    last_accessed: datetime
    access_count: int
    size_bytes: int
    ttl_seconds: Optional[int]
    metadata: Dict[str, Any] = field(default_factory=dict)
    status: CacheStatus = CacheStatus.ACTIVE

    def __post_init__(self):
        if self.ttl_seconds:
            self.expires_at = self.created_at + timedelta(seconds=self.ttl_seconds)
        else:
            self.expires_at = None

    @property
    def expires_at(self) -> Optional[datetime]:
        return self._expires_at

    @expires_at.setter
    def expires_at(self, value: Optional[datetime]):
        self._expires_at = value


@dataclass
class CacheStats:
    """Cache statistics."""

    total_entries: int = 0
    active_entries: int = 0
    expired_entries: int = 0
    evicted_entries: int = 0
    hit_count: int = 0
    miss_count: int = 0
    total_size_bytes: int = 0
    oldest_entry_age_seconds: float = 0.0
    newest_entry_age_seconds: float = 0.0


class CognitiveCache:
    """
    Intelligent caching system for cognitive processing results.

    Provides LRU, LFU, and TTL-based caching with intelligent invalidation.
    """

    def __init__(
        self,
        max_size_mb: int = 100,
        max_entries: int = 10000,
        default_ttl_seconds: int = 3600,
        policy: CachePolicy = CachePolicy.LRU,
    ):
        """
        Initialize the cognitive cache.

        Args:
            max_size_mb: Maximum cache size in MB
            max_entries: Maximum number of entries
            default_ttl_seconds: Default TTL for entries
            policy: Cache eviction policy
        """
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.max_entries = max_entries
        self.default_ttl_seconds = default_ttl_seconds
        self.policy = policy

        # Cache storage
        self.cache: OrderedDict[str, CacheEntry] = OrderedDict()

        # Statistics
        self.stats = CacheStats()

        # Configuration
        self.config = {
            "enable_compression": True,
            "compression_threshold_bytes": 1024,
            "enable_background_cleanup": True,
            "cleanup_interval_seconds": 300,
            "enable_metrics": True,
            "enable_invalidation": True,
        }

        # Background tasks
        self._cleanup_task: Optional[asyncio.Task] = None

        # Invalidation callbacks
        self.invalidation_callbacks: List[Callable] = []

        # Start background cleanup
        if self.config["enable_background_cleanup"]:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def get(self, key: str, default: Any = None) -> Any:
        """Get a value from cache."""
        entry = self.cache.get(key)

        if not entry:
            self.stats.miss_count += 1
            return default

        # Check if expired
        if self._is_expired(entry):
            await self._remove_entry(key, CacheStatus.EXPIRED)
            self.stats.miss_count += 1
            return default

        # Update access information
        entry.last_accessed = datetime.now()
        entry.access_count += 1

        # Move to end for LRU
        if self.policy == CachePolicy.LRU:
            self.cache.move_to_end(key)

        self.stats.hit_count += 1
        return entry.value

    async def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: int = None,
        metadata: Dict[str, Any] = None,
    ) -> None:
        """Set a value in cache."""
        # Calculate size
        size_bytes = self._calculate_size(value)

        # Check if we need to make space
        await self._ensure_space(size_bytes)

        # Create cache entry
        entry = CacheEntry(
            key=key,
            value=self._prepare_value(value),
            created_at=datetime.now(),
            last_accessed=datetime.now(),
            access_count=1,
            size_bytes=size_bytes,
            ttl_seconds=ttl_seconds or self.default_ttl_seconds,
            metadata=metadata or {},
        )

        # Add to cache
        self.cache[key] = entry
        self._update_stats()

        # Trigger invalidation callbacks if needed
        await self._trigger_invalidation_callbacks("set", key, entry)

    async def delete(self, key: str) -> bool:
        """Delete a key from cache."""
        if key in self.cache:
            await self._remove_entry(key, CacheStatus.INVALIDATED)
            return True
        return False

    async def clear(self) -> None:
        """Clear all cache entries."""
        self.cache.clear()
        self._reset_stats()

    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate entries matching a pattern."""
        keys_to_remove = []

        for key in self.cache.keys():
            if self._matches_pattern(key, pattern):
                keys_to_remove.append(key)

        for key in keys_to_remove:
            await self._remove_entry(key, CacheStatus.INVALIDATED)

        return len(keys_to_remove)

    async def invalidate_tag(self, tag: str) -> int:
        """Invalidate entries with a specific tag."""
        keys_to_remove = []

        for key, entry in self.cache.items():
            if tag in entry.metadata.get("tags", []):
                keys_to_remove.append(key)

        for key in keys_to_remove:
            await self._remove_entry(key, CacheStatus.INVALIDATED)

        return len(keys_to_remove)

    async def get_or_set(
        self,
        key: str,
        value_factory: Callable[[], Any],
        ttl_seconds: int = None,
        metadata: Dict[str, Any] = None,
    ) -> Any:
        """Get value or set using factory function."""
        value = await self.get(key)

        if value is not None:
            return value

        # Generate value
        if asyncio.iscoroutinefunction(value_factory):
            value = await value_factory()
        else:
            value = value_factory()

        await self.set(key, value, ttl_seconds, metadata)
        return value

    async def warm_up(
        self,
        keys: List[str],
        value_factory: Callable[[str], Any],
        ttl_seconds: int = None,
    ) -> Dict[str, Any]:
        """Warm up cache with multiple keys."""
        results = {}

        # Check which keys are missing
        missing_keys = [key for key in keys if key not in self.cache]

        if not missing_keys:
            return results

        # Generate values for missing keys
        tasks = []
        for key in missing_keys:
            if asyncio.iscoroutinefunction(value_factory):
                task = self._generate_and_set(key, value_factory, ttl_seconds)
            else:
                task = self._generate_and_set_sync(key, value_factory, ttl_seconds)
            tasks.append(task)

        # Wait for all tasks
        await asyncio.gather(*tasks)

        # Get all values
        for key in keys:
            results[key] = await self.get(key)

        return results

    async def _generate_and_set(
        self, key: str, value_factory: Callable[[str], Any], ttl_seconds: int
    ) -> None:
        """Generate and set value for a key."""
        value = await value_factory(key)
        await self.set(key, value, ttl_seconds)

    async def _generate_and_set_sync(
        self, key: str, value_factory: Callable[[str], Any], ttl_seconds: int
    ) -> None:
        """Generate and set value for a key (synchronous)."""
        value = value_factory(key)
        await self.set(key, value, ttl_seconds)

    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        self._update_stats()
        return self.stats

    def get_keys(self) -> List[str]:
        """Get all cache keys."""
        return list(self.cache.keys())

    def get_size_bytes(self) -> int:
        """Get current cache size in bytes."""
        return sum(entry.size_bytes for entry in self.cache.values())

    def get_hit_rate(self) -> float:
        """Get cache hit rate."""
        total_requests = self.stats.hit_count + self.stats.miss_count
        return self.stats.hit_count / max(total_requests, 1)

    def _calculate_size(self, value: Any) -> int:
        """Calculate size of a value."""
        if self.config["enable_compression"]:
            # Estimate size after compression
            serialized = json.dumps(value, default=str)
            if len(serialized) > self.config["compression_threshold_bytes"]:
                return len(serialized) // 2  # Rough compression estimate
            else:
                return len(serialized.encode("utf-8"))
        else:
            return len(json.dumps(value, default=str).encode("utf-8"))

    def _prepare_value(self, value: Any) -> Any:
        """Prepare value for storage."""
        if self.config["enable_compression"]:
            serialized = json.dumps(value, default=str)
            if len(serialized) > self.config["compression_threshold_bytes"]:
                # Simple compression (in production, use real compression)
                return {
                    "_compressed": True,
                    "_original_type": type(value).__name__,
                    "_data": serialized[:100] + "...",  # Truncated for demo
                }

        return value

    def _restore_value(self, prepared_value: Any) -> Any:
        """Restore value from prepared format."""
        if isinstance(prepared_value, dict) and prepared_value.get("_compressed"):
            # In production, decompress the data
            return json.loads(prepared_value["_data"] + "...")  # Simplified

        return prepared_value

    def _is_expired(self, entry: CacheEntry) -> bool:
        """Check if entry is expired."""
        if entry.expires_at is None:
            return False
        return datetime.now() > entry.expires_at

    async def _ensure_space(self, required_bytes: int) -> None:
        """Ensure cache has enough space."""
        current_size = self.get_size_bytes()

        while (
            current_size + required_bytes > self.max_size_bytes
            or len(self.cache) >= self.max_entries
        ):

            if not self.cache:
                break

            # Select entry to evict based on policy
            if self.policy == CachePolicy.LRU:
                # Remove least recently used
                oldest_key = next(iter(self.cache))
            elif self.policy == CachePolicy.LFU:
                # Remove least frequently used
                oldest_key = min(self.cache.items(), key=lambda x: x[1].access_count)[0]
            elif self.policy == CachePolicy.FIFO:
                # Remove oldest entry
                oldest_key = next(iter(self.cache))
            else:  # TTL
                # Remove expired entries first
                expired_key = None
                for key, entry in self.cache.items():
                    if self._is_expired(entry):
                        expired_key = key
                        break

                if expired_key:
                    oldest_key = expired_key

            if oldest_key:
                await self._remove_entry(oldest_key, CacheStatus.EVICTED)
                current_size = self.get_size_bytes()
            else:
                break

    async def _remove_entry(self, key: str, status: CacheStatus) -> None:
        """Remove an entry from cache."""
        if key in self.cache:
            entry = self.cache[key]
            entry.status = status
            del self.cache[key]
            self._update_stats()

            # Trigger invalidation callbacks
            await self._trigger_invalidation_callbacks("remove", key, entry)

    def _matches_pattern(self, key: str, pattern: str) -> bool:
        """Check if key matches a pattern."""
        # Simple pattern matching (in production, use regex)
        if "*" in pattern:
            # Wildcard pattern
            pattern_parts = pattern.split("*")
            if len(pattern_parts) == 2:
                return key.startswith(pattern_parts[0]) and key.endswith(
                    pattern_parts[1]
                )
            elif pattern.startswith("*"):
                return key.endswith(pattern[1:])
            elif pattern.endswith("*"):
                return key.startswith(pattern[0])

        return key == pattern

    def _update_stats(self) -> None:
        """Update cache statistics."""
        self.stats.total_entries = len(self.cache)
        self.stats.active_entries = sum(
            1 for e in self.cache.values() if e.status == CacheStatus.ACTIVE
        )
        self.stats.expired_entries = sum(
            1 for e in self.cache.values() if e.status == CacheStatus.EXPIRED
        )
        self.stats.evicted_entries = sum(
            1 for e in self.cache.values() if e.status == CacheStatus.EVICTED
        )
        self.stats.total_size_bytes = self.get_size_bytes()

        # Calculate entry ages
        if self.cache:
            now = datetime.now()
            ages = [(now - e.created_at).total_seconds() for e in self.cache.values()]
            self.stats.oldest_entry_age_seconds = max(ages) if ages else 0
            self.stats.newest_entry_age_seconds = min(ages) if ages else 0

    def _reset_stats(self) -> None:
        """Reset cache statistics."""
        self.stats = CacheStats()

    async def _trigger_invalidation_callbacks(
        self, action: str, key: str, entry: CacheEntry
    ) -> None:
        """Trigger invalidation callbacks."""
        for callback in self.invalidation_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(action, key, entry)
                else:
                    callback(action, key, entry)
            except Exception as e:
                print(f"Invalidation callback error: {e}")

    def add_invalidation_callback(self, callback: Callable) -> None:
        """Add an invalidation callback."""
        self.invalidation_callbacks.append(callback)

    def remove_invalidation_callback(self, callback: Callable) -> None:
        """Remove an invalidation callback."""
        if callback in self.invalidation_callbacks:
            self.invalidation_callbacks.remove(callback)

    async def _cleanup_loop(self) -> None:
        """Background cleanup loop."""
        while True:
            try:
                await self._cleanup_expired_entries()
                await asyncio.sleep(self.config["cleanup_interval_seconds"])
            except asyncio.CancelledError:
                break
            except Exception as e:
                print(f"Cache cleanup error: {e}")
                await asyncio.sleep(60)

    async def _cleanup_expired_entries(self) -> None:
        """Clean up expired entries."""
        expired_keys = [
            key for key, entry in self.cache.items() if self._is_expired(entry)
        ]

        for key in expired_keys:
            await self._remove_entry(key, CacheStatus.EXPIRED)

    async def stop(self) -> None:
        """Stop the cache and cleanup resources."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

        await self.clear()


class CacheKeyGenerator:
    """Generates cache keys for cognitive processing."""

    @staticmethod
    def perception_key(text: str, context: Dict[str, Any] = None) -> str:
        """Generate key for perception results."""
        # Create a hash of the text and context
        content = text
        if context:
            content += json.dumps(context, sort_keys=True)

        return f"perception:{hashlib.md5(content.encode()).hexdigest()}"

    @staticmethod
    def planning_key(goal: str, context: Dict[str, Any] = None) -> str:
        """Generate key for planning results."""
        content = goal
        if context:
            content += json.dumps(context, sort_keys=True)

        return f"planning:{hashlib.md5(content.encode()).hexdigest()}"

    @staticmethod
    def reflection_key(
        output: str, criteria: List[str], context: Dict[str, Any] = None
    ) -> str:
        """Generate key for reflection results."""
        content = output + "".join(criteria)
        if context:
            content += json.dumps(context, sort_keys=True)

        return f"reflection:{hashlib.md5(content.encode()).hexdigest()}"

    @staticmethod
    def execution_key(plan_id: str, context: Dict[str, Any] = None) -> str:
        """Generate key for execution results."""
        content = plan_id
        if context:
            content += json.dumps(context, sort_keys=True)

        return f"execution:{hashlib.md5(content.encode()).hexdigest()}"

    @staticmethod
    def user_context_key(user_id: str, workspace_id: str) -> str:
        """Generate key for user context."""
        return f"user_context:{user_id}:{workspace_id}"

    @staticmethod
    def icp_key(workspace_id: str, icp_id: str = None) -> str:
        """Generate key for ICP data."""
        if icp_id:
            return f"icp:{workspace_id}:{icp_id}"
        return f"icp:{workspace_id}:all"

    @staticmethod
    def foundation_key(workspace_id: str) -> str:
        """Generate key for foundation data."""
        return f"foundation:{workspace_id}"
