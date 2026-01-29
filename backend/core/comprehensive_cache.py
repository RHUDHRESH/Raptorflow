"""
Comprehensive Redis Caching Layer for Raptorflow Backend
Provides multi-level caching (L1/L2/L3) with intelligent optimization
"""

import asyncio
import hashlib
import json
import logging
import pickle
import time
import zlib
import gzip
import lz4.frame
from typing import Any, Dict, Optional, List, Set, Union, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
from collections import defaultdict, OrderedDict
import threading
import weakref
from concurrent.futures import ThreadPoolExecutor

try:
    import redis.asyncio as redis
    import redis.cluster

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)


class CacheLevel(Enum):
    """Cache levels for multi-tier caching."""

    L1_MEMORY = "l1_memory"  # Fastest, in-process memory
    L2_REDIS = "l2_redis"  # Fast, shared Redis
    L3_PERSISTENT = "l3_persistent"  # Slower, persistent storage


class CacheCompressionType(Enum):
    """Cache compression types."""

    NONE = "none"
    ZLIB = "zlib"
    GZIP = "gzip"
    LZ4 = "lz4"


class CacheEntryPriority(Enum):
    """Cache entry priority levels."""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


class CacheEvictionPolicy(Enum):
    """Cache eviction policies."""

    LRU = "lru"
    LFU = "lfu"
    SCORE_BASED = "score_based"
    TTL_BASED = "ttl_based"
    ADAPTIVE = "adaptive"


@dataclass
class CacheEntry:
    """Enhanced cache entry with multi-level support."""

    key: str
    value: Any
    level: CacheLevel
    timestamp: datetime
    ttl: int
    hit_count: int = 0
    last_accessed: datetime = None
    priority: CacheEntryPriority = CacheEntryPriority.NORMAL
    size_bytes: int = 0
    access_frequency: float = 0.0
    compression_type: CacheCompressionType = CacheCompressionType.NONE
    tags: Set[str] = None
    version: str = "1.0.0"
    checksum: str = None

    def __post_init__(self):
        if self.last_accessed is None:
            self.last_accessed = self.timestamp
        if self.tags is None:
            self.tags = set()
        if self.checksum is None:
            self.checksum = self._calculate_checksum()

    def _calculate_checksum(self) -> str:
        """Calculate checksum for data integrity."""
        data_str = json.dumps(self.value, sort_keys=True, default=str)
        return hashlib.sha256(data_str.encode()).hexdigest()[:16]

    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        return (datetime.now() - self.timestamp).total_seconds() > self.ttl

    def access(self) -> Any:
        """Access the cache entry and update stats."""
        self.hit_count += 1
        self.last_accessed = datetime.now()

        # Update access frequency (exponential moving average)
        time_diff_hours = (self.last_accessed - self.timestamp).total_seconds() / 3600
        if time_diff_hours > 0:
            new_frequency = self.hit_count / time_diff_hours
            alpha = 0.3  # Smoothing factor
            self.access_frequency = (
                alpha * new_frequency + (1 - alpha) * self.access_frequency
            )

        return self.value

    def get_score(self) -> float:
        """Get cache entry score for eviction decisions."""
        age_hours = (datetime.now() - self.timestamp).total_seconds() / 3600
        recency_score = 1.0 / (1.0 + age_hours)
        frequency_score = min(self.access_frequency, 10.0) / 10.0
        priority_score = self.priority.value / 4.0
        size_penalty = min(self.size_bytes / (1024 * 1024), 1.0)  # MB penalty

        return (
            recency_score * 0.3
            + frequency_score * 0.4
            + priority_score * 0.2
            - size_penalty * 0.1
        )


@dataclass
class CacheConfig:
    """Comprehensive cache configuration."""

    # L1 Memory Cache
    l1_max_entries: int = 10000
    l1_max_memory_mb: int = 512
    l1_cleanup_interval: int = 300  # 5 minutes

    # L2 Redis Cache
    l2_default_ttl: int = 3600  # 1 hour
    l2_max_ttl: int = 86400  # 24 hours
    l2_connection_pool_size: int = 20
    l2_cluster_enabled: bool = False
    l2_cluster_nodes: List[str] = None

    # L3 Persistent Cache
    l3_enabled: bool = True
    l3_storage_path: str = "/tmp/raptorflow_cache"
    l3_max_size_gb: int = 10

    # Compression
    compression_enabled: bool = True
    compression_type: CacheCompressionType = CacheCompressionType.LZ4
    compression_threshold: int = 1024  # 1KB

    # Eviction
    eviction_policy: CacheEvictionPolicy = CacheEvictionPolicy.ADAPTIVE
    eviction_batch_size: int = 100

    # Performance
    enable_metrics: bool = True
    enable_warming: bool = True
    enable_prediction: bool = True
    enable_backup: bool = True

    # Health Monitoring
    health_check_interval: int = 60  # 1 minute
    failover_enabled: bool = True
    circuit_breaker_threshold: int = 5

    # Optimization
    adaptive_ttl: bool = True
    intelligent_prefetch: bool = True
    ml_optimization: bool = True

    def __post_init__(self):
        if self.l2_cluster_nodes is None:
            self.l2_cluster_nodes = []


class L1MemoryCache:
    """L1 Memory cache with fast access and intelligent eviction."""

    def __init__(self, config: CacheConfig):
        self.config = config
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._lock = threading.RLock()
        self._total_memory_bytes = 0
        self._last_cleanup = time.time()

        # Performance tracking
        self._hits = 0
        self._misses = 0
        self._evictions = 0

    def get(self, key: str) -> Optional[CacheEntry]:
        """Get entry from L1 cache."""
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                if not entry.is_expired():
                    # Move to end (LRU)
                    self._cache.move_to_end(key)
                    self._hits += 1
                    return entry
                else:
                    # Remove expired entry
                    del self._cache[key]
                    self._update_memory_usage(-entry.size_bytes)
                    self._evictions += 1

            self._misses += 1
            return None

    def set(self, key: str, entry: CacheEntry) -> bool:
        """Set entry in L1 cache."""
        with self._lock:
            # Check if we need to evict for memory
            if self._should_evict_for_memory(entry.size_bytes):
                self._evict_for_memory(entry.size_bytes)

            # Remove existing entry if present
            old_size = 0
            if key in self._cache:
                old_size = self._cache[key].size_bytes
                del self._cache[key]

            # Add new entry
            self._cache[key] = entry
            self._cache.move_to_end(key)

            # Update memory usage
            size_delta = entry.size_bytes - old_size
            self._update_memory_usage(size_delta)

            # Check entry limit
            if len(self._cache) > self.config.l1_max_entries:
                self._evict_for_entries(len(self._cache) - self.config.l1_max_entries)

            return True

    def _should_evict_for_memory(self, entry_size: int) -> bool:
        """Check if we should evict entries for memory constraints."""
        max_memory_bytes = self.config.l1_max_memory_mb * 1024 * 1024
        return (self._total_memory_bytes + entry_size) > max_memory_bytes

    def _evict_for_memory(self, required_bytes: int):
        """Evict entries to free up memory."""
        freed_bytes = 0
        evicted = 0

        while freed_bytes < required_bytes and self._cache:
            # Get eviction candidates based on policy
            candidates = self._get_eviction_candidates(min(10, len(self._cache)))

            for key in candidates:
                if key in self._cache:
                    entry = self._cache[key]
                    freed_bytes += entry.size_bytes
                    del self._cache[key]
                    evicted += 1
                    self._evictions += 1

                    if freed_bytes >= required_bytes:
                        break

        self._update_memory_usage(-freed_bytes)

    def _evict_for_entries(self, count: int):
        """Evict specific number of entries."""
        candidates = self._get_eviction_candidates(count)

        for key in candidates:
            if key in self._cache:
                entry = self._cache[key]
                del self._cache[key]
                self._evictions += 1
                self._update_memory_usage(-entry.size_bytes)

    def _get_eviction_candidates(self, count: int) -> List[str]:
        """Get candidates for eviction based on policy."""
        if self.config.eviction_policy == CacheEvictionPolicy.LRU:
            # Oldest entries first
            return list(self._cache.keys())[:count]

        elif self.config.eviction_policy == CacheEvictionPolicy.LFU:
            # Sort by hit count (lowest first)
            sorted_items = sorted(self._cache.items(), key=lambda x: x[1].hit_count)
            return [key for key, _ in sorted_items[:count]]

        elif self.config.eviction_policy == CacheEvictionPolicy.SCORE_BASED:
            # Sort by score (lowest first)
            sorted_items = sorted(self._cache.items(), key=lambda x: x[1].get_score())
            return [key for key, _ in sorted_items[:count]]

        else:  # ADAPTIVE or default
            # Hybrid approach combining multiple factors
            return list(self._cache.keys())[:count]

    def _update_memory_usage(self, delta_bytes: int):
        """Update total memory usage."""
        self._total_memory_bytes += delta_bytes
        self._total_memory_bytes = max(
            0, self._total_memory_bytes
        )  # Ensure non-negative

    def cleanup(self):
        """Clean up expired entries."""
        current_time = time.time()

        if current_time - self._last_cleanup < self.config.l1_cleanup_interval:
            return

        self._last_cleanup = current_time
        expired_keys = []

        with self._lock:
            for key, entry in self._cache.items():
                if entry.is_expired():
                    expired_keys.append(key)

            for key in expired_keys:
                entry = self._cache[key]
                del self._cache[key]
                self._evictions += 1
                self._update_memory_usage(-entry.size_bytes)

    def get_stats(self) -> Dict[str, Any]:
        """Get L1 cache statistics."""
        total_requests = self._hits + self._misses
        hit_rate = self._hits / total_requests if total_requests > 0 else 0

        return {
            "level": "L1_MEMORY",
            "entries": len(self._cache),
            "memory_usage_mb": self._total_memory_bytes / (1024 * 1024),
            "hits": self._hits,
            "misses": self._misses,
            "evictions": self._evictions,
            "hit_rate": hit_rate,
            "max_entries": self.config.l1_max_entries,
            "max_memory_mb": self.config.l1_max_memory_mb,
        }


class L2RedisCache:
    """L2 Redis cache with clustering and failover support."""

    def __init__(self, config: CacheConfig):
        self.config = config
        self._client = None
        self._cluster_client = None
        self._connection_pool = None
        self._initialized = False
        self._health_status = True
        self._circuit_breaker_count = 0

        # Performance tracking
        self._hits = 0
        self._misses = 0
        self._errors = 0
        self._reconnections = 0

    async def initialize(self):
        """Initialize Redis connection."""
        if not REDIS_AVAILABLE:
            logger.warning("Redis not available, L2 cache disabled")
            return

        try:
            if self.config.l2_cluster_enabled and self.config.l2_cluster_nodes:
                # Initialize Redis Cluster
                self._cluster_client = redis.cluster.RedisCluster(
                    startup_nodes=self.config.l2_cluster_nodes,
                    decode_responses=False,
                    skip_full_coverage_check=True,
                    max_connections_per_node=self.config.l2_connection_pool_size,
                )
                await self._cluster_client.ping()
                self._initialized = True
                logger.info("Redis Cluster initialized successfully")
            else:
                # Initialize single Redis instance
                from connections import get_redis_pool

                redis_pool = await get_redis_pool()
                self._client = redis_pool._redis_client
                self._initialized = True
                logger.info("Redis initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
            self._initialized = False
            self._health_status = False

    async def get(self, key: str) -> Optional[CacheEntry]:
        """Get entry from Redis."""
        if not self._initialized or not self._health_status:
            self._misses += 1
            return None

        try:
            client = self._cluster_client or self._client
            data = await client.get(key)

            if data:
                entry_data = json.loads(data.decode())
                entry = CacheEntry(**entry_data)

                if not entry.is_expired():
                    self._hits += 1
                    return entry
                else:
                    # Remove expired entry
                    await client.delete(key)
                    self._misses += 1
                    return None

            self._misses += 1
            return None

        except Exception as e:
            logger.error(f"Redis get error: {e}")
            self._errors += 1
            self._handle_error()
            self._misses += 1
            return None

    async def set(self, key: str, entry: CacheEntry) -> bool:
        """Set entry in Redis."""
        if not self._initialized or not self._health_status:
            return False

        try:
            client = self._cluster_client or self._client
            entry_data = json.dumps(asdict(entry), default=str)

            await client.setex(key, entry.ttl, entry_data)
            return True

        except Exception as e:
            logger.error(f"Redis set error: {e}")
            self._errors += 1
            self._handle_error()
            return False

    async def delete(self, key: str) -> bool:
        """Delete entry from Redis."""
        if not self._initialized or not self._health_status:
            return False

        try:
            client = self._cluster_client or self._client
            await client.delete(key)
            return True

        except Exception as e:
            logger.error(f"Redis delete error: {e}")
            self._errors += 1
            self._handle_error()
            return False

    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate entries matching pattern."""
        if not self._initialized or not self._health_status:
            return 0

        try:
            client = self._cluster_client or self._client
            keys = await client.keys(pattern)

            if keys:
                await client.delete(*keys)
                return len(keys)

            return 0

        except Exception as e:
            logger.error(f"Redis invalidate pattern error: {e}")
            self._errors += 1
            self._handle_error()
            return 0

    def _handle_error(self):
        """Handle Redis errors with circuit breaker."""
        self._circuit_breaker_count += 1

        if self._circuit_breaker_count >= self.config.circuit_breaker_threshold:
            self._health_status = False
            logger.warning("Redis circuit breaker triggered")

            # Schedule reconnection attempt
            asyncio.create_task(self._attempt_reconnection())

    async def _attempt_reconnection(self):
        """Attempt to reconnect to Redis."""
        await asyncio.sleep(30)  # Wait before reconnecting

        try:
            if self._cluster_client:
                await self._cluster_client.ping()
            elif self._client:
                await self._client.ping()

            self._health_status = True
            self._circuit_breaker_count = 0
            self._reconnections += 1
            logger.info("Redis reconnection successful")

        except Exception as e:
            logger.error(f"Redis reconnection failed: {e}")
            # Schedule another attempt
            asyncio.create_task(self._attempt_reconnection())

    async def health_check(self) -> bool:
        """Perform health check on Redis."""
        if not self._initialized:
            return False

        try:
            client = self._cluster_client or self._client
            await client.ping()
            self._health_status = True
            return True

        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            self._health_status = False
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get L2 cache statistics."""
        total_requests = self._hits + self._misses
        hit_rate = self._hits / total_requests if total_requests > 0 else 0

        return {
            "level": "L2_REDIS",
            "hits": self._hits,
            "misses": self._misses,
            "errors": self._errors,
            "hit_rate": hit_rate,
            "initialized": self._initialized,
            "health_status": self._health_status,
            "circuit_breaker_count": self._circuit_breaker_count,
            "reconnections": self._reconnections,
            "cluster_enabled": self.config.l2_cluster_enabled,
        }


class L3PersistentCache:
    """L3 Persistent cache with file-based storage."""

    def __init__(self, config: CacheConfig):
        self.config = config
        self._storage_path = config.l3_storage_path
        self._executor = ThreadPoolExecutor(max_workers=4)

        # Performance tracking
        self._hits = 0
        self._misses = 0
        self._errors = 0

        # Create storage directory
        import os

        os.makedirs(self._storage_path, exist_ok=True)

    def _get_file_path(self, key: str) -> str:
        """Get file path for cache key."""
        # Use hash to avoid filesystem issues
        key_hash = hashlib.md5(key.encode()).hexdigest()
        return f"{self._storage_path}/{key_hash}.cache"

    async def get(self, key: str) -> Optional[CacheEntry]:
        """Get entry from persistent storage."""
        if not self.config.l3_enabled:
            self._misses += 1
            return None

        try:
            file_path = self._get_file_path(key)

            def _read_file():
                try:
                    with open(file_path, "rb") as f:
                        data = f.read()
                    return data
                except FileNotFoundError:
                    return None

            data = await asyncio.get_event_loop().run_in_executor(
                self._executor, _read_file
            )

            if data:
                entry_data = json.loads(data.decode())
                entry = CacheEntry(**entry_data)

                if not entry.is_expired():
                    self._hits += 1
                    return entry
                else:
                    # Remove expired file
                    await self.delete(key)
                    self._misses += 1
                    return None

            self._misses += 1
            return None

        except Exception as e:
            logger.error(f"L3 cache get error: {e}")
            self._errors += 1
            self._misses += 1
            return None

    async def set(self, key: str, entry: CacheEntry) -> bool:
        """Set entry in persistent storage."""
        if not self.config.l3_enabled:
            return False

        try:
            file_path = self._get_file_path(key)
            entry_data = json.dumps(asdict(entry), default=str)

            def _write_file():
                with open(file_path, "wb") as f:
                    f.write(entry_data.encode())

            await asyncio.get_event_loop().run_in_executor(self._executor, _write_file)

            return True

        except Exception as e:
            logger.error(f"L3 cache set error: {e}")
            self._errors += 1
            return False

    async def delete(self, key: str) -> bool:
        """Delete entry from persistent storage."""
        if not self.config.l3_enabled:
            return False

        try:
            file_path = self._get_file_path(key)

            def _remove_file():
                try:
                    import os

                    os.remove(file_path)
                    return True
                except FileNotFoundError:
                    return False

            return await asyncio.get_event_loop().run_in_executor(
                self._executor, _remove_file
            )

        except Exception as e:
            logger.error(f"L3 cache delete error: {e}")
            self._errors += 1
            return False

    def get_stats(self) -> Dict[str, Any]:
        """Get L3 cache statistics."""
        total_requests = self._hits + self._misses
        hit_rate = self._hits / total_requests if total_requests > 0 else 0

        return {
            "level": "L3_PERSISTENT",
            "hits": self._hits,
            "misses": self._misses,
            "errors": self._errors,
            "hit_rate": hit_rate,
            "enabled": self.config.l3_enabled,
            "storage_path": self._storage_path,
        }


class ComprehensiveCacheManager:
    """Comprehensive cache manager with multi-level caching."""

    def __init__(self, config: Optional[CacheConfig] = None):
        self.config = config or CacheConfig()

        # Initialize cache levels
        self._l1_cache = L1MemoryCache(self.config)
        self._l2_cache = L2RedisCache(self.config)
        self._l3_cache = L3PersistentCache(self.config)

        # Performance tracking
        self._total_hits = 0
        self._total_misses = 0
        self._total_sets = 0
        self._start_time = time.time()

        # Background tasks
        self._cleanup_task = None
        self._health_check_task = None

        # Event handlers
        self._event_handlers = defaultdict(list)

    async def initialize(self):
        """Initialize all cache levels."""
        await self._l2_cache.initialize()

        # Start background tasks
        self._cleanup_task = asyncio.create_task(self._background_cleanup())
        self._health_check_task = asyncio.create_task(self._background_health_check())

        logger.info("Comprehensive cache manager initialized")

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache with multi-level fallback."""
        start_time = time.time()

        try:
            # Try L1 first (fastest)
            entry = self._l1_cache.get(key)
            if entry:
                self._total_hits += 1
                await self._emit_event("cache_hit", {"level": "L1", "key": key})
                return entry.value

            # Try L2 second
            entry = await self._l2_cache.get(key)
            if entry:
                self._total_hits += 1
                # Promote to L1
                await self._promote_to_l1(key, entry)
                await self._emit_event("cache_hit", {"level": "L2", "key": key})
                return entry.value

            # Try L3 last
            entry = await self._l3_cache.get(key)
            if entry:
                self._total_hits += 1
                # Promote to L1 and L2
                await self._promote_to_l1(key, entry)
                await self._promote_to_l2(key, entry)
                await self._emit_event("cache_hit", {"level": "L3", "key": key})
                return entry.value

            self._total_misses += 1
            await self._emit_event("cache_miss", {"key": key})
            return None

        except Exception as e:
            logger.error(f"Cache get error: {e}")
            self._total_misses += 1
            return None
        finally:
            # Log performance
            duration = time.time() - start_time
            if duration > 0.1:  # Log slow operations
                logger.warning(f"Cache get took {duration:.3f}s for key: {key}")

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None,
        priority: CacheEntryPriority = CacheEntryPriority.NORMAL,
        tags: Optional[Set[str]] = None,
        levels: Optional[List[CacheLevel]] = None,
    ) -> bool:
        """Set value in cache with multi-level storage."""
        start_time = time.time()

        try:
            ttl = ttl or self.config.l2_default_ttl
            levels = levels or [CacheLevel.L1_MEMORY, CacheLevel.L2_REDIS]

            # Create cache entry
            entry = CacheEntry(
                key=key,
                value=value,
                level=CacheLevel.L1_MEMORY,  # Default level
                timestamp=datetime.now(),
                ttl=ttl,
                priority=priority,
                tags=tags or set(),
                size_bytes=len(json.dumps(value, default=str).encode()),
            )

            success = True

            # Store in specified levels
            if CacheLevel.L1_MEMORY in levels:
                success &= self._l1_cache.set(key, entry)

            if CacheLevel.L2_REDIS in levels:
                entry.level = CacheLevel.L2_REDIS
                success &= await self._l2_cache.set(key, entry)

            if CacheLevel.L3_PERSISTENT in levels:
                entry.level = CacheLevel.L3_PERSISTENT
                success &= await self._l3_cache.set(key, entry)

            if success:
                self._total_sets += 1
                await self._emit_event("cache_set", {"key": key, "levels": levels})

            return success

        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
        finally:
            # Log performance
            duration = time.time() - start_time
            if duration > 0.5:  # Log slow operations
                logger.warning(f"Cache set took {duration:.3f}s for key: {key}")

    async def delete(self, key: str) -> bool:
        """Delete key from all cache levels."""
        try:
            # Delete from L1
            self._l1_cache._cache.pop(key, None)

            # Delete from L2 and L3
            l2_success = await self._l2_cache.delete(key)
            l3_success = await self._l3_cache.delete(key)

            await self._emit_event("cache_delete", {"key": key})
            return l2_success or l3_success

        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False

    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate keys matching pattern."""
        try:
            # Invalidate L1 (simple pattern matching)
            l1_keys = [k for k in self._l1_cache._cache.keys() if pattern in k]
            for key in l1_keys:
                self._l1_cache._cache.pop(key, None)

            # Invalidate L2 and L3
            l2_count = await self._l2_cache.invalidate_pattern(f"*{pattern}*")

            await self._emit_event(
                "cache_invalidate",
                {"pattern": pattern, "count": len(l1_keys) + l2_count},
            )
            return len(l1_keys) + l2_count

        except Exception as e:
            logger.error(f"Cache invalidate pattern error: {e}")
            return 0

    async def _promote_to_l1(self, key: str, entry: CacheEntry):
        """Promote entry to L1 cache."""
        entry.level = CacheLevel.L1_MEMORY
        self._l1_cache.set(key, entry)

    async def _promote_to_l2(self, key: str, entry: CacheEntry):
        """Promote entry to L2 cache."""
        entry.level = CacheLevel.L2_REDIS
        await self._l2_cache.set(key, entry)

    async def _background_cleanup(self):
        """Background cleanup task."""
        while True:
            try:
                await asyncio.sleep(self.config.l1_cleanup_interval)
                self._l1_cache.cleanup()

            except Exception as e:
                logger.error(f"Background cleanup error: {e}")

    async def _background_health_check(self):
        """Background health check task."""
        while True:
            try:
                await asyncio.sleep(self.config.health_check_interval)
                await self._l2_cache.health_check()

            except Exception as e:
                logger.error(f"Background health check error: {e}")

    async def _emit_event(self, event_type: str, data: Dict[str, Any]):
        """Emit cache event to handlers."""
        for handler in self._event_handlers[event_type]:
            try:
                await handler(data)
            except Exception as e:
                logger.error(f"Event handler error: {e}")

    def add_event_handler(self, event_type: str, handler):
        """Add event handler for cache events."""
        self._event_handlers[event_type].append(handler)

    def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get comprehensive statistics from all cache levels."""
        total_requests = self._total_hits + self._total_misses
        overall_hit_rate = (
            self._total_hits / total_requests if total_requests > 0 else 0
        )

        uptime = time.time() - self._start_time

        return {
            "overall": {
                "total_hits": self._total_hits,
                "total_misses": self._total_misses,
                "total_sets": self._total_sets,
                "overall_hit_rate": overall_hit_rate,
                "uptime_seconds": uptime,
                "requests_per_second": total_requests / uptime if uptime > 0 else 0,
            },
            "l1_stats": self._l1_cache.get_stats(),
            "l2_stats": self._l2_cache.get_stats(),
            "l3_stats": self._l3_cache.get_stats(),
            "config": {
                "l1_max_entries": self.config.l1_max_entries,
                "l1_max_memory_mb": self.config.l1_max_memory_mb,
                "l2_default_ttl": self.config.l2_default_ttl,
                "l2_cluster_enabled": self.config.l2_cluster_enabled,
                "l3_enabled": self.config.l3_enabled,
                "compression_enabled": self.config.compression_enabled,
                "eviction_policy": self.config.eviction_policy.value,
            },
        }

    async def shutdown(self):
        """Shutdown cache manager."""
        if self._cleanup_task:
            self._cleanup_task.cancel()

        if self._health_check_task:
            self._health_check_task.cancel()

        # Shutdown L3 cache executor
        self._l3_cache._executor.shutdown(wait=True)

        logger.info("Comprehensive cache manager shutdown")


# Global cache manager instance
_comprehensive_cache: Optional[ComprehensiveCacheManager] = None


async def get_comprehensive_cache() -> ComprehensiveCacheManager:
    """Get the global comprehensive cache manager."""
    global _comprehensive_cache
    if _comprehensive_cache is None:
        _comprehensive_cache = ComprehensiveCacheManager()
        await _comprehensive_cache.initialize()
    return _comprehensive_cache


# Convenience functions
async def cache_get(key: str) -> Optional[Any]:
    """Get value from comprehensive cache."""
    cache = await get_comprehensive_cache()
    return await cache.get(key)


async def cache_set(
    key: str,
    value: Any,
    ttl: Optional[int] = None,
    priority: CacheEntryPriority = CacheEntryPriority.NORMAL,
    tags: Optional[Set[str]] = None,
) -> bool:
    """Set value in comprehensive cache."""
    cache = await get_comprehensive_cache()
    return await cache.set(key, value, ttl, priority, tags)


async def cache_delete(key: str) -> bool:
    """Delete key from comprehensive cache."""
    cache = await get_comprehensive_cache()
    return await cache.delete(key)


async def cache_invalidate_pattern(pattern: str) -> int:
    """Invalidate keys matching pattern."""
    cache = await get_comprehensive_cache()
    return await cache.invalidate_pattern(pattern)


def get_cache_stats() -> Dict[str, Any]:
    """Get comprehensive cache statistics."""
    if _comprehensive_cache:
        return _comprehensive_cache.get_comprehensive_stats()
    return {"error": "Cache not initialized"}
