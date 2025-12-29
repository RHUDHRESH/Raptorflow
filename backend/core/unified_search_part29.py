"""
Part 29: Advanced Caching and Memory Management
RaptorFlow Unified Search System - Industrial Grade AI Agent Search Infrastructure
===============================================================================
This module implements advanced caching strategies, intelligent memory management,
and distributed caching for optimal performance and resource utilization.
"""

import asyncio
import hashlib
import json
import logging
import pickle
import time
import uuid
from collections import OrderedDict, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union

import aiofiles
import aiofiles.os
import redis.asyncio as redis

from core.unified_search_part1 import ContentType, SearchMode, SearchQuery, SearchResult
from core.unified_search_part2 import SearchProvider

logger = logging.getLogger("raptorflow.unified_search.caching")


class CacheStrategy(Enum):
    """Caching strategies."""

    LRU = "lru"
    LFU = "lfu"
    FIFO = "fifo"
    RANDOM = "random"
    TTL = "ttl"
    ADAPTIVE = "adaptive"
    WRITE_THROUGH = "write_through"
    WRITE_BEHIND = "write_behind"
    WRITE_AROUND = "write_around"


class CacheLevel(Enum):
    """Cache levels."""

    MEMORY = "memory"
    DISK = "disk"
    DISTRIBUTED = "distributed"
    HYBRID = "hybrid"


class EvictionPolicy(Enum):
    """Cache eviction policies."""

    LRU = "lru"
    LFU = "lfu"
    FIFO = "fifo"
    RANDOM = "random"
    TTL_EXPIRED = "ttl_expired"
    SIZE_BASED = "size_based"


@dataclass
class CacheEntry:
    """Cache entry with metadata."""

    key: str
    value: Any
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    size_bytes: int = 0
    ttl_seconds: Optional[int] = None
    expires_at: Optional[datetime] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Set expiration time if TTL is specified."""
        if self.ttl_seconds:
            self.expires_at = self.created_at + timedelta(seconds=self.ttl_seconds)

        # Calculate size if not provided
        if self.size_bytes == 0:
            self.size_bytes = self._calculate_size()

    def _calculate_size(self) -> int:
        """Calculate approximate size of cache entry."""
        try:
            return len(pickle.dumps(self.value))
        except Exception:
            return len(str(self.value).encode("utf-8"))

    def is_expired(self) -> bool:
        """Check if entry is expired."""
        if self.expires_at:
            return datetime.now() > self.expires_at
        return False

    def access(self):
        """Update access information."""
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
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "metadata": self.metadata,
        }


@dataclass
class CacheStats:
    """Cache statistics."""

    total_entries: int = 0
    total_size_bytes: int = 0
    hit_count: int = 0
    miss_count: int = 0
    eviction_count: int = 0
    hit_rate: float = 0.0
    avg_access_time_ms: float = 0.0
    memory_usage_mb: float = 0.0
    disk_usage_mb: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "total_entries": self.total_entries,
            "total_size_bytes": self.total_size_bytes,
            "hit_count": self.hit_count,
            "miss_count": self.miss_count,
            "eviction_count": self.eviction_count,
            "hit_rate": self.hit_rate,
            "avg_access_time_ms": self.avg_access_time_ms,
            "memory_usage_mb": self.memory_usage_mb,
            "disk_usage_mb": self.disk_usage_mb,
            "timestamp": self.timestamp.isoformat(),
        }

    @property
    def total_requests(self) -> int:
        """Get total requests."""
        return self.hit_count + self.miss_count


class MemoryCache:
    """In-memory cache with multiple eviction policies."""

    def __init__(
        self,
        max_size_mb: int = 512,
        max_entries: int = 10000,
        eviction_policy: EvictionPolicy = EvictionPolicy.LRU,
        default_ttl_seconds: Optional[int] = None,
    ):
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.max_entries = max_entries
        self.eviction_policy = eviction_policy
        self.default_ttl_seconds = default_ttl_seconds

        self.cache: Dict[str, CacheEntry] = {}
        self.access_order = OrderedDict()  # For LRU
        self.frequency_order = {}  # For LFU
        self.stats = CacheStats()
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache."""
        start_time = time.time()

        async with self._lock:
            entry = self.cache.get(key)

            if entry is None:
                self.stats.miss_count += 1
                self._update_hit_rate()
                return None

            if entry.is_expired():
                await self._remove_entry(key)
                self.stats.miss_count += 1
                self._update_hit_rate()
                return None

            # Update access information
            entry.access()
            self._update_access_order(key)
            self._update_frequency_order(key)

            self.stats.hit_count += 1
            self._update_hit_rate()

            # Update access time
            access_time_ms = (time.time() - start_time) * 1000
            self.stats.avg_access_time_ms = (
                self.stats.avg_access_time_ms * (self.stats.total_requests - 1)
                + access_time_ms
            ) / self.stats.total_requests

            return entry.value

    async def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Set value in cache."""
        async with self._lock:
            # Create cache entry
            entry = CacheEntry(
                key=key,
                value=value,
                ttl_seconds=ttl_seconds or self.default_ttl_seconds,
                metadata=metadata or {},
            )

            # Check if eviction is needed
            if not await self._ensure_capacity(entry.size_bytes):
                return False

            # Remove existing entry if present
            if key in self.cache:
                await self._remove_entry(key)

            # Add new entry
            self.cache[key] = entry
            self._update_access_order(key)
            self._update_frequency_order(key)

            self._update_stats()

            return True

    async def delete(self, key: str) -> bool:
        """Delete entry from cache."""
        async with self._lock:
            if key in self.cache:
                await self._remove_entry(key)
                return True
            return False

    async def clear(self):
        """Clear all cache entries."""
        async with self._lock:
            self.cache.clear()
            self.access_order.clear()
            self.frequency_order.clear()
            self._update_stats()

    async def _ensure_capacity(self, required_size: int) -> bool:
        """Ensure cache has enough capacity."""
        # Check entry count limit
        while len(self.cache) >= self.max_entries:
            if not await self._evict_entry():
                return False

        # Check size limit
        while self._get_total_size() + required_size > self.max_size_bytes:
            if not await self._evict_entry():
                return False

        return True

    async def _evict_entry(self) -> bool:
        """Evict entry based on policy."""
        if not self.cache:
            return False

        key_to_evict = None

        if self.eviction_policy == EvictionPolicy.LRU:
            key_to_evict = next(iter(self.access_order))
        elif self.eviction_policy == EvictionPolicy.LFU:
            key_to_evict = min(
                self.frequency_order.keys(), key=lambda k: self.frequency_order[k]
            )
        elif self.eviction_policy == EvictionPolicy.FIFO:
            key_to_evict = next(iter(self.cache))
        elif self.eviction_policy == EvictionPolicy.TTL_EXPIRED:
            # Find expired entry
            for key, entry in self.cache.items():
                if entry.is_expired():
                    key_to_evict = key
                    break
        elif self.eviction_policy == EvictionPolicy.SIZE_BASED:
            # Evict largest entry
            key_to_evict = max(
                self.cache.keys(), key=lambda k: self.cache[k].size_bytes
            )
        elif self.eviction_policy == EvictionPolicy.RANDOM:
            import random

            key_to_evict = random.choice(list(self.cache.keys()))

        if key_to_evict:
            await self._remove_entry(key_to_evict)
            self.stats.eviction_count += 1
            return True

        return False

    async def _remove_entry(self, key: str):
        """Remove entry from cache."""
        if key in self.cache:
            del self.cache[key]

        if key in self.access_order:
            del self.access_order[key]

        if key in self.frequency_order:
            del self.frequency_order[key]

        self._update_stats()

    def _update_access_order(self, key: str):
        """Update access order for LRU."""
        if key in self.access_order:
            self.access_order.move_to_end(key)
        else:
            self.access_order[key] = None

    def _update_frequency_order(self, key: str):
        """Update frequency order for LFU."""
        if key in self.cache:
            self.frequency_order[key] = self.cache[key].access_count

    def _get_total_size(self) -> int:
        """Get total cache size."""
        return sum(entry.size_bytes for entry in self.cache.values())

    def _update_stats(self):
        """Update cache statistics."""
        self.stats.total_entries = len(self.cache)
        self.stats.total_size_bytes = self._get_total_size()
        self.stats.memory_usage_mb = self.stats.total_size_bytes / (1024 * 1024)

    def _update_hit_rate(self):
        """Update hit rate."""
        if self.stats.total_requests > 0:
            self.stats.hit_rate = self.stats.hit_count / self.stats.total_requests

    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        return self.stats


class DiskCache:
    """Disk-based cache with async I/O."""

    def __init__(
        self,
        cache_dir: str = "./cache",
        max_size_mb: int = 1024,
        compression_enabled: bool = True,
    ):
        self.cache_dir = cache_dir
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.compression_enabled = compression_enabled
        self.stats = CacheStats()
        self._lock = asyncio.Lock()

    async def initialize(self):
        """Initialize disk cache."""
        try:
            await aiofiles.os.makedirs(self.cache_dir, exist_ok=True)
            logger.info(f"Disk cache initialized at {self.cache_dir}")
        except Exception as e:
            logger.error(f"Failed to initialize disk cache: {e}")
            raise

    async def get(self, key: str) -> Optional[Any]:
        """Get value from disk cache."""
        start_time = time.time()

        async with self._lock:
            file_path = self._get_file_path(key)

            try:
                async with aiofiles.open(file_path, "rb") as f:
                    data = await f.read()

                # Decompress if enabled
                if self.compression_enabled:
                    import gzip

                    data = gzip.decompress(data)

                # Deserialize
                entry = pickle.loads(data)

                # Check expiration
                if entry.is_expired():
                    await aiofiles.os.remove(file_path)
                    self.stats.miss_count += 1
                    self._update_hit_rate()
                    return None

                # Update access
                entry.access()

                # Write back updated metadata
                await self._write_entry(key, entry)

                self.stats.hit_count += 1
                self._update_hit_rate()

                # Update access time
                access_time_ms = (time.time() - start_time) * 1000
                self.stats.avg_access_time_ms = (
                    self.stats.avg_access_time_ms * (self.stats.total_requests - 1)
                    + access_time_ms
                ) / self.stats.total_requests

                return entry.value

            except FileNotFoundError:
                self.stats.miss_count += 1
                self._update_hit_rate()
                return None
            except Exception as e:
                logger.error(f"Error reading from disk cache: {e}")
                self.stats.miss_count += 1
                self._update_hit_rate()
                return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Set value in disk cache."""
        async with self._lock:
            try:
                # Create cache entry
                entry = CacheEntry(
                    key=key,
                    value=value,
                    ttl_seconds=ttl_seconds,
                    metadata=metadata or {},
                )

                # Check capacity
                if not await self._ensure_capacity(entry.size_bytes):
                    return False

                # Write entry
                await self._write_entry(key, entry)

                self._update_stats()

                return True

            except Exception as e:
                logger.error(f"Error writing to disk cache: {e}")
                return False

    async def delete(self, key: str) -> bool:
        """Delete entry from disk cache."""
        async with self._lock:
            file_path = self._get_file_path(key)

            try:
                await aiofiles.os.remove(file_path)
                self._update_stats()
                return True
            except FileNotFoundError:
                return False
            except Exception as e:
                logger.error(f"Error deleting from disk cache: {e}")
                return False

    async def clear(self):
        """Clear all disk cache entries."""
        async with self._lock:
            try:
                for filename in await aiofiles.os.listdir(self.cache_dir):
                    file_path = f"{self.cache_dir}/{filename}"
                    await aiofiles.os.remove(file_path)

                self._update_stats()

            except Exception as e:
                logger.error(f"Error clearing disk cache: {e}")

    def _get_file_path(self, key: str) -> str:
        """Get file path for cache key."""
        # Hash key to create safe filename
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return f"{self.cache_dir}/{key_hash}.cache"

    async def _write_entry(self, key: str, entry: CacheEntry):
        """Write cache entry to disk."""
        file_path = self._get_file_path(key)

        # Serialize
        data = pickle.dumps(entry)

        # Compress if enabled
        if self.compression_enabled:
            import gzip

            data = gzip.compress(data)

        # Write to file
        async with aiofiles.open(file_path, "wb") as f:
            await f.write(data)

    async def _ensure_capacity(self, required_size: int) -> bool:
        """Ensure disk cache has enough capacity."""
        current_size = await self._get_disk_usage()

        if current_size + required_size <= self.max_size_bytes:
            return True

        # Need to evict some entries
        entries_to_remove = await self._get_entries_for_eviction(required_size)

        for key in entries_to_remove:
            await self.delete(key)

            # Check if we have enough space now
            current_size = await self._get_disk_usage()
            if current_size + required_size <= self.max_size_bytes:
                return True

        return False

    async def _get_disk_usage(self) -> int:
        """Get current disk usage."""
        total_size = 0

        try:
            for filename in await aiofiles.os.listdir(self.cache_dir):
                file_path = f"{self.cache_dir}/{filename}"
                stat = await aiofiles.os.stat(file_path)
                total_size += stat.st_size
        except Exception:
            pass

        return total_size

    async def _get_entries_for_eviction(self, required_size: int) -> List[str]:
        """Get entries to evict based on LRU."""
        entries = []

        try:
            for filename in await aiofiles.os.listdir(self.cache_dir):
                if filename.endswith(".cache"):
                    file_path = f"{self.cache_dir}/{filename}"
                    stat = await aiofiles.os.stat(file_path)

                    # Read entry metadata (simplified)
                    try:
                        async with aiofiles.open(file_path, "rb") as f:
                            data = await f.read()

                        if self.compression_enabled:
                            import gzip

                            data = gzip.decompress(data)

                        entry = pickle.loads(data)
                        entries.append((entry.key, entry.last_accessed, stat.st_size))

                    except Exception:
                        # If we can't read the entry, add it for removal
                        entries.append((filename, datetime.min, stat.st_size))

        except Exception:
            pass

        # Sort by last accessed time
        entries.sort(key=lambda x: x[1])

        # Select entries for eviction
        keys_to_remove = []
        size_freed = 0

        for key, _, size in entries:
            keys_to_remove.append(key)
            size_freed += size

            if size_freed >= required_size:
                break

        return keys_to_remove

    def _update_stats(self):
        """Update cache statistics."""
        # Update stats (simplified)
        self.stats.disk_usage_mb = self._get_disk_usage() / (1024 * 1024)

    def _update_hit_rate(self):
        """Update hit rate."""
        if self.stats.total_requests > 0:
            self.stats.hit_rate = self.stats.hit_count / self.stats.total_requests

    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        return self.stats


class DistributedCache:
    """Distributed cache using Redis."""

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        key_prefix: str = "raptorflow:",
        default_ttl_seconds: int = 3600,
    ):
        self.redis_url = redis_url
        self.key_prefix = key_prefix
        self.default_ttl_seconds = default_ttl_seconds
        self.redis_client: Optional[redis.Redis] = None
        self.stats = CacheStats()
        self._lock = asyncio.Lock()

    async def connect(self):
        """Connect to Redis."""
        try:
            self.redis_client = redis.from_url(self.redis_url, decode_responses=False)
            # Test connection
            await self.redis_client.ping()
            logger.info("Connected to Redis for distributed caching")
        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise

    async def disconnect(self):
        """Disconnect from Redis."""
        if self.redis_client:
            await self.redis_client.close()

    async def get(self, key: str) -> Optional[Any]:
        """Get value from distributed cache."""
        start_time = time.time()

        async with self._lock:
            if not self.redis_client:
                return None

            try:
                full_key = f"{self.key_prefix}{key}"
                data = await self.redis_client.get(full_key)

                if data is None:
                    self.stats.miss_count += 1
                    self._update_hit_rate()
                    return None

                # Deserialize
                entry = pickle.loads(data)

                # Check expiration
                if entry.is_expired():
                    await self.redis_client.delete(full_key)
                    self.stats.miss_count += 1
                    self._update_hit_rate()
                    return None

                # Update access
                entry.access()

                # Write back updated metadata (optional)
                await self.redis_client.setex(
                    full_key,
                    entry.ttl_seconds or self.default_ttl_seconds,
                    pickle.dumps(entry),
                )

                self.stats.hit_count += 1
                self._update_hit_rate()

                # Update access time
                access_time_ms = (time.time() - start_time) * 1000
                self.stats.avg_access_time_ms = (
                    self.stats.avg_access_time_ms * (self.stats.total_requests - 1)
                    + access_time_ms
                ) / self.stats.total_requests

                return entry.value

            except Exception as e:
                logger.error(f"Error reading from distributed cache: {e}")
                self.stats.miss_count += 1
                self._update_hit_rate()
                return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Set value in distributed cache."""
        async with self._lock:
            if not self.redis_client:
                return False

            try:
                # Create cache entry
                entry = CacheEntry(
                    key=key,
                    value=value,
                    ttl_seconds=ttl_seconds or self.default_ttl_seconds,
                    metadata=metadata or {},
                )

                # Serialize and store
                full_key = f"{self.key_prefix}{key}"
                data = pickle.dumps(entry)

                await self.redis_client.setex(
                    full_key, entry.ttl_seconds or self.default_ttl_seconds, data
                )

                return True

            except Exception as e:
                logger.error(f"Error writing to distributed cache: {e}")
                return False

    async def delete(self, key: str) -> bool:
        """Delete entry from distributed cache."""
        async with self._lock:
            if not self.redis_client:
                return False

            try:
                full_key = f"{self.key_prefix}{key}"
                result = await self.redis_client.delete(full_key)
                return result > 0
            except Exception as e:
                logger.error(f"Error deleting from distributed cache: {e}")
                return False

    async def clear(self):
        """Clear all entries with our prefix."""
        async with self._lock:
            if not self.redis_client:
                return

            try:
                pattern = f"{self.key_prefix}*"
                keys = await self.redis_client.keys(pattern)

                if keys:
                    await self.redis_client.delete(*keys)

            except Exception as e:
                logger.error(f"Error clearing distributed cache: {e}")

    def _update_hit_rate(self):
        """Update hit rate."""
        if self.stats.total_requests > 0:
            self.stats.hit_rate = self.stats.hit_count / self.stats.total_requests

    def get_stats(self) -> CacheStats:
        """Get cache statistics."""
        return self.stats


class HybridCache:
    """Hybrid cache combining memory, disk, and distributed caching."""

    def __init__(
        self,
        memory_cache: MemoryCache,
        disk_cache: DiskCache,
        distributed_cache: Optional[DistributedCache] = None,
    ):
        self.memory_cache = memory_cache
        self.disk_cache = disk_cache
        self.distributed_cache = distributed_cache
        self.stats = CacheStats()
        self._lock = asyncio.Lock()

    async def initialize(self):
        """Initialize hybrid cache."""
        await self.disk_cache.initialize()

        if self.distributed_cache:
            await self.distributed_cache.connect()

        logger.info("Hybrid cache initialized")

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache (L1 -> L2 -> L3)."""
        start_time = time.time()

        # Try memory cache first (L1)
        value = await self.memory_cache.get(key)
        if value is not None:
            return value

        # Try disk cache (L2)
        value = await self.disk_cache.get(key)
        if value is not None:
            # Promote to memory cache
            await self.memory_cache.set(key, value)
            return value

        # Try distributed cache (L3)
        if self.distributed_cache:
            value = await self.distributed_cache.get(key)
            if value is not None:
                # Promote to memory and disk caches
                await self.memory_cache.set(key, value)
                await self.disk_cache.set(key, value)
                return value

        # Update combined stats
        async with self._lock:
            self.stats.miss_count += 1
            self._update_hit_rate()

        return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl_seconds: Optional[int] = None,
        metadata: Optional[Dict[str, Any]] = None,
        cache_levels: Set[CacheLevel] = None,
    ) -> bool:
        """Set value in cache levels."""
        if cache_levels is None:
            cache_levels = {CacheLevel.MEMORY, CacheLevel.DISK}

        success = True

        # Set in memory cache
        if CacheLevel.MEMORY in cache_levels:
            success &= await self.memory_cache.set(key, value, ttl_seconds, metadata)

        # Set in disk cache
        if CacheLevel.DISK in cache_levels:
            success &= await self.disk_cache.set(key, value, ttl_seconds, metadata)

        # Set in distributed cache
        if CacheLevel.DISTRIBUTED in cache_levels and self.distributed_cache:
            success &= await self.distributed_cache.set(
                key, value, ttl_seconds, metadata
            )

        # Update combined stats
        async with self._lock:
            self.stats.hit_count += 1
            self._update_hit_rate()

        return success

    async def delete(self, key: str) -> bool:
        """Delete from all cache levels."""
        success = True

        success &= await self.memory_cache.delete(key)
        success &= await self.disk_cache.delete(key)

        if self.distributed_cache:
            success &= await self.distributed_cache.delete(key)

        return success

    async def clear(self):
        """Clear all cache levels."""
        await self.memory_cache.clear()
        await self.disk_cache.clear()

        if self.distributed_cache:
            await self.distributed_cache.clear()

    def _update_hit_rate(self):
        """Update combined hit rate."""
        if self.stats.total_requests > 0:
            self.stats.hit_rate = self.stats.hit_count / self.stats.total_requests

    def get_combined_stats(self) -> Dict[str, Any]:
        """Get combined statistics from all cache levels."""
        memory_stats = self.memory_cache.get_stats()
        disk_stats = self.disk_cache.get_stats()
        distributed_stats = (
            self.distributed_cache.get_stats() if self.distributed_cache else None
        )

        return {
            "memory": memory_stats.to_dict(),
            "disk": disk_stats.to_dict(),
            "distributed": distributed_stats.to_dict() if distributed_stats else None,
            "combined": {
                "total_entries": memory_stats.total_entries + disk_stats.total_entries,
                "total_size_mb": memory_stats.memory_usage_mb
                + disk_stats.disk_usage_mb,
                "total_hit_rate": self.stats.hit_rate,
                "total_requests": self.stats.total_requests,
            },
        }


class CacheManager:
    """Advanced cache manager with intelligent strategies."""

    def __init__(self):
        self.memory_cache = MemoryCache(
            max_size_mb=256, eviction_policy=EvictionPolicy.LRU
        )
        self.disk_cache = DiskCache(max_size_mb=1024, compression_enabled=True)
        self.distributed_cache = DistributedCache()
        self.hybrid_cache = HybridCache(
            self.memory_cache, self.disk_cache, self.distributed_cache
        )

        # Specialized caches for different data types
        self.search_cache = MemoryCache(
            max_size_mb=128, eviction_policy=EvictionPolicy.LFU
        )
        self.result_cache = MemoryCache(
            max_size_mb=256, eviction_policy=EvictionPolicy.TTL_EXPIRED
        )
        self.metadata_cache = MemoryCache(
            max_size_mb=64, eviction_policy=EvictionPolicy.LRU
        )

        self._initialized = False

    async def initialize(self):
        """Initialize cache manager."""
        if self._initialized:
            return

        await self.hybrid_cache.initialize()
        self._initialized = True

        logger.info("Cache manager initialized")

    async def shutdown(self):
        """Shutdown cache manager."""
        if self.distributed_cache:
            await self.distributed_cache.disconnect()

        logger.info("Cache manager shutdown")

    def _generate_cache_key(
        self, query: SearchQuery, provider: Optional[SearchProvider] = None
    ) -> str:
        """Generate cache key for search query."""
        key_data = {
            "query": query.text,
            "mode": query.mode.value,
            "max_results": query.max_results,
            "content_types": [ct.value for ct in query.content_types],
            "provider": provider.value if provider else "all",
        }

        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.md5(key_string.encode()).hexdigest()

    async def cache_search_results(
        self,
        query: SearchQuery,
        results: List[SearchResult],
        provider: Optional[SearchProvider] = None,
        ttl_seconds: int = 1800,  # 30 minutes
    ):
        """Cache search results."""
        if not self._initialized:
            await self.initialize()

        cache_key = self._generate_cache_key(query, provider)

        # Cache in multiple levels
        await self.hybrid_cache.set(
            cache_key,
            results,
            ttl_seconds=ttl_seconds,
            metadata={
                "query": query.text,
                "provider": provider.value if provider else "all",
                "result_count": len(results),
                "cached_at": datetime.now().isoformat(),
            },
            cache_levels={CacheLevel.MEMORY, CacheLevel.DISK},
        )

        # Also cache in specialized search cache
        await self.search_cache.set(cache_key, results, ttl_seconds=ttl_seconds)

    async def get_cached_search_results(
        self, query: SearchQuery, provider: Optional[SearchProvider] = None
    ) -> Optional[List[SearchResult]]:
        """Get cached search results."""
        if not self._initialized:
            await self.initialize()

        cache_key = self._generate_cache_key(query, provider)

        # Try specialized search cache first
        results = await self.search_cache.get(cache_key)
        if results:
            return results

        # Try hybrid cache
        return await self.hybrid_cache.get(cache_key)

    async def cache_query_metadata(
        self, query: SearchQuery, metadata: Dict[str, Any], ttl_seconds: int = 3600
    ):
        """Cache query metadata."""
        if not self._initialized:
            await self.initialize()

        cache_key = f"metadata:{self._generate_cache_key(query)}"

        await self.metadata_cache.set(cache_key, metadata, ttl_seconds=ttl_seconds)

    async def get_cached_query_metadata(
        self, query: SearchQuery
    ) -> Optional[Dict[str, Any]]:
        """Get cached query metadata."""
        if not self._initialized:
            await self.initialize()

        cache_key = f"metadata:{self._generate_cache_key(query)}"

        return await self.metadata_cache.get(cache_key)

    async def invalidate_query_cache(self, query: SearchQuery):
        """Invalidate cache for specific query."""
        if not self._initialized:
            await self.initialize()

        cache_key = self._generate_cache_key(query)

        await self.hybrid_cache.delete(cache_key)
        await self.search_cache.delete(cache_key)

        metadata_key = f"metadata:{cache_key}"
        await self.metadata_cache.delete(metadata_key)

    async def get_cache_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive cache performance report."""
        if not self._initialized:
            await self.initialize()

        hybrid_stats = self.hybrid_cache.get_combined_stats()
        search_stats = self.search_cache.get_stats()
        result_stats = self.result_cache.get_stats()
        metadata_stats = self.metadata_cache.get_stats()

        return {
            "timestamp": datetime.now().isoformat(),
            "hybrid_cache": hybrid_stats,
            "specialized_caches": {
                "search": search_stats.to_dict(),
                "results": result_stats.to_dict(),
                "metadata": metadata_stats.to_dict(),
            },
            "performance_metrics": {
                "overall_hit_rate": hybrid_stats["combined"]["total_hit_rate"],
                "total_cached_items": hybrid_stats["combined"]["total_entries"],
                "total_cache_size_mb": hybrid_stats["combined"]["total_size_mb"],
                "memory_efficiency": self._calculate_memory_efficiency(),
                "cache_utilization": self._calculate_cache_utilization(),
            },
        }

    def _calculate_memory_efficiency(self) -> float:
        """Calculate memory efficiency metric."""
        # Simplified calculation based on hit rates
        memory_stats = self.memory_cache.get_stats()
        return memory_stats.hit_rate if memory_stats.total_requests > 0 else 0.0

    def _calculate_cache_utilization(self) -> float:
        """Calculate cache utilization."""
        # Simplified calculation
        memory_stats = self.memory_cache.get_stats()
        disk_stats = self.disk_cache.get_stats()

        memory_util = memory_stats.memory_usage_mb / 256  # Max 256MB
        disk_util = disk_stats.disk_usage_mb / 1024  # Max 1GB

        return (memory_util + disk_util) / 2


# Global cache manager
cache_manager = CacheManager()
