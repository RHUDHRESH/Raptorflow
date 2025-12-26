"""
Part 13: Advanced Caching and Memory Management
RaptorFlow Unified Search System - Industrial Grade AI Agent Search Infrastructure
===============================================================================
This module implements advanced caching strategies, memory management, and
performance optimization for the unified search system.
"""

import asyncio
import hashlib
import json
import logging
import pickle
import threading
import time
import weakref
from collections import OrderedDict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from core.unified_search_part1 import SearchQuery, SearchResult

logger = logging.getLogger("raptorflow.unified_search.cache")


class CacheStrategy(Enum):
    """Caching strategies."""

    LRU = "lru"
    LFU = "lfu"
    TTL = "ttl"
    ADAPTIVE = "adaptive"


@dataclass
class CacheEntry:
    """Cache entry with metadata."""

    key: str
    value: Any
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    size_bytes: int = 0
    ttl_seconds: Optional[float] = None
    priority: float = 1.0

    def is_expired(self) -> bool:
        """Check if entry is expired."""
        if self.ttl_seconds is None:
            return False
        return (datetime.now() - self.created_at).total_seconds() > self.ttl_seconds

    def touch(self):
        """Update access statistics."""
        self.last_accessed = datetime.now()
        self.access_count += 1

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "key": self.key,
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "access_count": self.access_count,
            "size_bytes": self.size_bytes,
            "ttl_seconds": self.ttl_seconds,
            "priority": self.priority,
            "is_expired": self.is_expired(),
        }


class MemoryCache:
    """Advanced in-memory cache with multiple eviction strategies."""

    def __init__(
        self,
        max_size: int = 1000,
        max_memory_mb: int = 512,
        strategy: CacheStrategy = CacheStrategy.LRU,
        default_ttl_seconds: Optional[float] = None,
    ):
        self.max_size = max_size
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.strategy = strategy
        self.default_ttl_seconds = default_ttl_seconds

        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._current_memory_bytes = 0
        self._lock = threading.RLock()
        self._stats = {"hits": 0, "misses": 0, "evictions": 0, "expirations": 0}

    def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        with self._lock:
            if key not in self._cache:
                self._stats["misses"] += 1
                return None

            entry = self._cache[key]

            # Check expiration
            if entry.is_expired():
                del self._cache[key]
                self._current_memory_bytes -= entry.size_bytes
                self._stats["expirations"] += 1
                self._stats["misses"] += 1
                return None

            # Update access
            entry.touch()

            # Move to end for LRU
            if self.strategy == CacheStrategy.LRU:
                self._cache.move_to_end(key)

            self._stats["hits"] += 1
            return entry.value

    def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: Optional[float] = None,
        priority: float = 1.0,
    ) -> bool:
        """Set value in cache."""
        with self._lock:
            # Calculate size
            try:
                size_bytes = len(pickle.dumps(value))
            except Exception:
                size_bytes = len(str(value).encode("utf-8"))

            # Check if single entry exceeds memory limit
            if size_bytes > self.max_memory_bytes:
                logger.warning(f"Cache entry too large: {size_bytes} bytes")
                return False

            # Remove existing entry if present
            if key in self._cache:
                old_entry = self._cache[key]
                self._current_memory_bytes -= old_entry.size_bytes
                del self._cache[key]

            # Create new entry
            ttl = ttl_seconds or self.default_ttl_seconds
            entry = CacheEntry(
                key=key,
                value=value,
                size_bytes=size_bytes,
                ttl_seconds=ttl,
                priority=priority,
            )

            # Evict if necessary
            self._ensure_capacity(size_bytes)

            # Add entry
            self._cache[key] = entry
            self._current_memory_bytes += size_bytes

            # Move to end for LRU
            if self.strategy == CacheStrategy.LRU:
                self._cache.move_to_end(key)

            return True

    def delete(self, key: str) -> bool:
        """Delete entry from cache."""
        with self._lock:
            if key not in self._cache:
                return False

            entry = self._cache.pop(key)
            self._current_memory_bytes -= entry.size_bytes
            return True

    def clear(self):
        """Clear all entries."""
        with self._lock:
            self._cache.clear()
            self._current_memory_bytes = 0

    def _ensure_capacity(self, required_bytes: int):
        """Ensure cache has enough capacity."""
        # Check size limit
        while len(self._cache) >= self.max_size:
            self._evict_entry()

        # Check memory limit
        while (self._current_memory_bytes + required_bytes) > self.max_memory_bytes:
            if not self._cache:
                break
            self._evict_entry()

    def _evict_entry(self):
        """Evict entry based on strategy."""
        if not self._cache:
            return

        if self.strategy == CacheStrategy.LRU:
            # Remove least recently used (first in OrderedDict)
            key, entry = self._cache.popitem(last=False)
        elif self.strategy == CacheStrategy.LFU:
            # Remove least frequently used
            key = min(self._cache.keys(), key=lambda k: self._cache[k].access_count)
            entry = self._cache.pop(key)
        elif self.strategy == CacheStrategy.TTL:
            # Remove expired entries first
            for key, entry in list(self._cache.items()):
                if entry.is_expired():
                    del self._cache[key]
                    self._current_memory_bytes -= entry.size_bytes
                    self._stats["expirations"] += 1
                    return
            # Fall back to LRU
            key, entry = self._cache.popitem(last=False)
        else:  # ADAPTIVE
            # Combine access frequency and recency
            def adaptive_score(entry: CacheEntry) -> float:
                age_hours = (datetime.now() - entry.created_at).total_seconds() / 3600
                frequency = entry.access_count
                return frequency / (age_hours + 1) * entry.priority

            key = min(self._cache.keys(), key=lambda k: adaptive_score(self._cache[k]))
            entry = self._cache.pop(key)

        self._current_memory_bytes -= entry.size_bytes
        self._stats["evictions"] += 1

    def cleanup_expired(self) -> int:
        """Clean up expired entries."""
        with self._lock:
            expired_keys = []
            for key, entry in self._cache.items():
                if entry.is_expired():
                    expired_keys.append(key)

            for key in expired_keys:
                entry = self._cache.pop(key)
                self._current_memory_bytes -= entry.size_bytes
                self._stats["expirations"] += 1

            return len(expired_keys)

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        with self._lock:
            total_requests = self._stats["hits"] + self._stats["misses"]
            hit_rate = self._stats["hits"] / total_requests if total_requests > 0 else 0

            return {
                "entries": len(self._cache),
                "max_entries": self.max_size,
                "memory_bytes": self._current_memory_bytes,
                "max_memory_bytes": self.max_memory_bytes,
                "hit_rate": hit_rate,
                "hits": self._stats["hits"],
                "misses": self._stats["misses"],
                "evictions": self._stats["evictions"],
                "expirations": self._stats["expirations"],
                "strategy": self.strategy.value,
            }

    def get_entries_info(self) -> List[Dict[str, Any]]:
        """Get information about all entries."""
        with self._lock:
            return [entry.to_dict() for entry in self._cache.values()]


class DistributedCache:
    """Distributed cache interface for future Redis/memcached integration."""

    def __init__(self, local_cache: MemoryCache):
        self.local_cache = local_cache
        self._distributed_enabled = False

    async def get(self, key: str) -> Optional[Any]:
        """Get value from distributed cache."""
        # Try local cache first
        value = self.local_cache.get(key)
        if value is not None:
            return value

        # TODO: Implement distributed cache lookup
        return None

    async def set(
        self, key: str, value: Any, ttl_seconds: Optional[float] = None
    ) -> bool:
        """Set value in distributed cache."""
        # Set in local cache
        return self.local_cache.set(key, value, ttl_seconds)

    async def delete(self, key: str) -> bool:
        """Delete from distributed cache."""
        return self.local_cache.delete(key)

    async def clear(self):
        """Clear distributed cache."""
        self.local_cache.clear()


class SearchCache:
    """Specialized cache for search results and queries."""

    def __init__(self, cache: MemoryCache):
        self.cache = cache
        self._query_cache = MemoryCache(max_size=500, max_memory_mb=256)
        self._result_cache = MemoryCache(max_size=1000, max_memory_mb=512)

    def generate_query_key(self, query: SearchQuery) -> str:
        """Generate cache key for search query."""
        # Create normalized query representation
        query_data = {
            "text": query.text.lower().strip(),
            "mode": query.mode.value,
            "content_types": sorted([ct.value for ct in query.content_types]),
            "max_results": query.max_results,
            "language": query.language,
            "region": query.region,
            "time_range": query.time_range,
            "safe_search": query.safe_search,
        }

        # Create hash
        query_str = json.dumps(query_data, sort_keys=True)
        return hashlib.sha256(query_str.encode("utf-8")).hexdigest()

    def get_cached_results(self, query: SearchQuery) -> Optional[List[SearchResult]]:
        """Get cached search results."""
        key = self.generate_query_key(query)
        return self._query_cache.get(key)

    def cache_results(
        self, query: SearchQuery, results: List[SearchResult], ttl_seconds: float = 3600
    ):
        """Cache search results."""
        key = self.generate_query_key(query)
        self._query_cache.set(key, results, ttl_seconds, priority=2.0)

    def cache_content(self, url: str, content: Any, ttl_seconds: float = 7200):
        """Cache crawled content."""
        self._result_cache.set(url, content, ttl_seconds, priority=1.5)

    def get_cached_content(self, url: str) -> Optional[Any]:
        """Get cached content."""
        return self._result_cache.get(url)

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        return {
            "query_cache": self._query_cache.get_stats(),
            "result_cache": self._result_cache.get_stats(),
            "combined": self.cache.get_stats(),
        }

    def cleanup(self) -> Dict[str, int]:
        """Clean up expired entries."""
        return {
            "query_cache": self._query_cache.cleanup_expired(),
            "result_cache": self._result_cache.cleanup_expired(),
            "combined": self.cache.cleanup_expired(),
        }


class MemoryManager:
    """Advanced memory management for the search system."""

    def __init__(self):
        self.caches: Dict[str, MemoryCache] = {}
        self.weak_refs: Dict[str, weakref.ref] = {}
        self._cleanup_interval = 300  # 5 minutes
        self._cleanup_task: Optional[asyncio.Task] = None
        self._monitoring_enabled = False

    def register_cache(self, name: str, cache: MemoryCache):
        """Register a cache for monitoring."""
        self.caches[name] = cache

    def register_object(self, name: str, obj: Any):
        """Register object for weak reference tracking."""
        self.weak_refs[name] = weakref.ref(obj, self._object_callback)

    def _object_callback(self, ref):
        """Callback for weak reference cleanup."""
        # Find and remove dead references
        dead_keys = [
            key for key, weak_ref in self.weak_refs.items() if weak_ref() is None
        ]
        for key in dead_keys:
            del self.weak_refs[key]

    async def start_monitoring(self):
        """Start memory monitoring."""
        if self._monitoring_enabled:
            return

        self._monitoring_enabled = True
        self._cleanup_task = asyncio.create_task(self._monitoring_loop())
        logger.info("Memory monitoring started")

    async def stop_monitoring(self):
        """Stop memory monitoring."""
        self._monitoring_enabled = False
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        logger.info("Memory monitoring stopped")

    async def _monitoring_loop(self):
        """Main monitoring loop."""
        while self._monitoring_enabled:
            try:
                await self._perform_cleanup()
                await asyncio.sleep(self._cleanup_interval)
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Memory monitoring error: {e}")
                await asyncio.sleep(60)  # Wait before retry

    async def _perform_cleanup(self):
        """Perform memory cleanup."""
        total_cleaned = 0

        # Clean up caches
        for name, cache in self.caches.items():
            cleaned = cache.cleanup_expired()
            total_cleaned += cleaned
            if cleaned > 0:
                logger.debug(f"Cache {name}: cleaned {cleaned} expired entries")

        # Clean up weak references
        dead_count = len([key for key, ref in self.weak_refs.items() if ref() is None])
        if dead_count > 0:
            self._object_callback(None)  # Trigger cleanup

        # Log memory usage
        if total_cleaned > 0:
            logger.info(f"Memory cleanup completed: {total_cleaned} entries removed")

    def get_memory_report(self) -> Dict[str, Any]:
        """Get comprehensive memory report."""
        report = {
            "timestamp": datetime.now().isoformat(),
            "caches": {},
            "weak_refs": len(self.weak_refs),
            "monitoring_active": self._monitoring_enabled,
        }

        total_memory = 0
        total_entries = 0

        for name, cache in self.caches.items():
            stats = cache.get_stats()
            report["caches"][name] = stats
            total_memory += stats["memory_bytes"]
            total_entries += stats["entries"]

        report["total_memory_bytes"] = total_memory
        report["total_entries"] = total_entries
        report["total_memory_mb"] = total_memory / (1024 * 1024)

        return report

    def optimize_memory(self) -> Dict[str, Any]:
        """Optimize memory usage."""
        optimizations = {"cache_cleanups": {}, "memory_freed": 0}

        for name, cache in self.caches.items():
            # Clean expired entries
            cleaned = cache.cleanup_expired()
            optimizations["cache_cleanups"][name] = cleaned

            # Force eviction if memory usage is high
            stats = cache.get_stats()
            if stats["memory_bytes"] > cache.max_memory_bytes * 0.8:
                # Evict 20% of entries
                target_evictions = max(1, len(cache._cache) // 5)
                for _ in range(target_evictions):
                    cache._evict_entry()
                optimizations["cache_cleanups"][f"{name}_forced"] = target_evictions

        # Recalculate total memory
        report = self.get_memory_report()
        optimizations["memory_freed"] = (
            optimizations.get("previous_memory", 0) - report["total_memory_bytes"]
        )
        optimizations["current_memory_mb"] = report["total_memory_mb"]

        return optimizations


# Global cache instances
main_cache = MemoryCache(
    max_size=2000, max_memory_mb=1024, strategy=CacheStrategy.ADAPTIVE
)
distributed_cache = DistributedCache(main_cache)
search_cache = SearchCache(main_cache)
memory_manager = MemoryManager()

# Register caches with memory manager
memory_manager.register_cache("main", main_cache)
memory_manager.register_cache("search_query", search_cache._query_cache)
memory_manager.register_cache("search_result", search_cache._result_cache)
