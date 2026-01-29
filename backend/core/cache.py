"""
Agent response caching system.
Provides intelligent caching for agent responses to identical requests.
"""

import hashlib
import json
import logging
import pickle
import time
import zlib
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set

try:
    import redis.asyncio as redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

logger = logging.getLogger(__name__)


class CacheInvalidationStrategy(Enum):
    """Cache invalidation strategies."""

    TTL_BASED = "ttl_based"
    EVENT_DRIVEN = "event_driven"
    MANUAL = "manual"
    SIZE_BASED = "size_based"
    INTELLIGENT = "intelligent"


class CacheCompressionType(Enum):
    """Cache compression types."""

    NONE = "none"
    ZLIB = "zlib"
    GZIP = "gzip"


class CacheEntryPriority(Enum):
    """Cache entry priority levels."""

    LOW = 1
    NORMAL = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class CacheEntry:
    """Enhanced cache entry for agent responses."""

    response: Dict[str, Any]
    timestamp: datetime
    ttl: int  # Time to live in seconds
    hit_count: int = 0
    last_accessed: datetime = None
    priority: CacheEntryPriority = CacheEntryPriority.NORMAL
    size_bytes: int = 0
    access_frequency: float = 0.0  # Hits per hour
    agent_version: str = "1.0.0"
    tags: Set[str] = None

    def __post_init__(self):
        if self.last_accessed is None:
            self.last_accessed = self.timestamp
        if self.tags is None:
            self.tags = set()
        # Calculate size
        self.size_bytes = len(json.dumps(self.response, default=str).encode())

    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        return (datetime.now() - self.timestamp).total_seconds() > self.ttl

    def access(self) -> Dict[str, Any]:
        """Access the cache entry and update stats."""
        self.hit_count += 1
        self.last_accessed = datetime.now()
        # Update access frequency (simple moving average)
        time_diff = (
            self.last_accessed - self.timestamp
        ).total_seconds() / 3600  # hours
        if time_diff > 0:
            self.access_frequency = (
                self.access_frequency + (self.hit_count / time_diff)
            ) / 2
        return self.response

    def get_score(self) -> float:
        """Get cache entry score for eviction decisions."""
        # Consider hit count, recency, size, and priority
        age_hours = (datetime.now() - self.timestamp).total_seconds() / 3600
        recency_score = 1.0 / (1.0 + age_hours)
        frequency_score = min(self.access_frequency, 10.0) / 10.0
        priority_score = self.priority.value / 4.0
        size_penalty = min(self.size_bytes / 1024 / 1024, 1.0)  # MB penalty

        return (
            recency_score * 0.3
            + frequency_score * 0.4
            + priority_score * 0.2
            - size_penalty * 0.1
        )


class CacheConfig:
    """Enhanced configuration for agent caching."""

    def __init__(
        self,
        default_ttl: int = 3600,  # 1 hour
        max_ttl: int = 86400,  # 24 hours
        max_entries: int = 10000,
        cleanup_interval: int = 300,  # 5 minutes
        compression_threshold: int = 1024,  # 1KB
        enable_compression: bool = True,
        compression_type: CacheCompressionType = CacheCompressionType.ZLIB,
        invalidation_strategy: CacheInvalidationStrategy = CacheInvalidationStrategy.INTELLIGENT,
        cache_warmup_enabled: bool = True,
        preload_agents: List[str] = None,
        max_memory_mb: int = 512,  # Maximum cache size in MB
        eviction_policy: str = "score_based",  # score_based, lru, lfu
        enable_metrics: bool = True,
    ):
        self.default_ttl = default_ttl
        self.max_ttl = max_ttl
        self.max_entries = max_entries
        self.cleanup_interval = cleanup_interval
        self.compression_threshold = compression_threshold
        self.enable_compression = enable_compression
        self.compression_type = compression_type
        self.invalidation_strategy = invalidation_strategy
        self.cache_warmup_enabled = cache_warmup_enabled
        self.preload_agents = preload_agents or []
        self.max_memory_mb = max_memory_mb
        self.eviction_policy = eviction_policy
        self.enable_metrics = enable_metrics


class AgentCache:
    """Intelligent caching system for agent responses."""

    def __init__(self, config: Optional[CacheConfig] = None, redis_client=None):
        self.config = config or CacheConfig()
        self.redis_client = redis_client
        self._local_cache: Dict[str, CacheEntry] = {}
        self._last_cleanup = time.time()
        self._cache_hits = 0
        self._cache_misses = 0
        self._cache_sets = 0
        self._cache_evictions = 0
        self._cache_errors = 0
        self._total_memory_bytes = 0
        self._preload_tasks: List[asyncio.Task] = []
        self._warming_up = False

        # Performance metrics
        self._metrics = {
            "avg_response_time": 0.0,
            "compression_ratio": 0.0,
            "hit_rate_by_agent": {},
            "memory_usage_history": [],
            "access_patterns": {},
        }

    def _compress_data(self, data: bytes) -> bytes:
        """Compress data based on configuration."""
        if (
            not self.config.enable_compression
            or len(data) < self.config.compression_threshold
        ):
            return data

        if self.config.compression_type == CacheCompressionType.ZLIB:
            return zlib.compress(data, level=6)
        elif self.config.compression_type == CacheCompressionType.GZIP:
            import gzip

            return gzip.compress(data)
        else:
            return data

    def _decompress_data(self, data: bytes) -> bytes:
        """Decompress data based on configuration."""
        if (
            not self.config.enable_compression
            or len(data) < self.config.compression_threshold
        ):
            return data

        try:
            if self.config.compression_type == CacheCompressionType.ZLIB:
                return zlib.decompress(data)
            elif self.config.compression_type == CacheCompressionType.GZIP:
                import gzip

                return gzip.decompress(data)
            else:
                return data
        except Exception as e:
            logger.warning(f"Decompression failed: {e}")
            return data

    def _update_memory_usage(self, delta_bytes: int):
        """Update total memory usage."""
        self._total_memory_bytes += delta_bytes

        # Record memory usage history
        if self.config.enable_metrics:
            self._metrics["memory_usage_history"].append(
                {
                    "timestamp": datetime.now().isoformat(),
                    "bytes": self._total_memory_bytes,
                    "mb": self._total_memory_bytes / (1024 * 1024),
                }
            )

            # Keep only last 100 entries
            if len(self._metrics["memory_usage_history"]) > 100:
                self._metrics["memory_usage_history"] = self._metrics[
                    "memory_usage_history"
                ][-100:]

    def _should_evict_for_memory(self, entry_size: int) -> bool:
        """Check if we should evict entries for memory constraints."""
        max_memory_bytes = self.config.max_memory_mb * 1024 * 1024
        return (self._total_memory_bytes + entry_size) > max_memory_bytes

    def _get_eviction_candidates(self, count: int = 1) -> List[str]:
        """Get candidates for eviction based on policy."""
        if self.config.eviction_policy == "score_based":
            # Sort by score (lowest first)
            sorted_entries = sorted(
                self._local_cache.items(), key=lambda x: x[1].get_score()
            )
            return [key for key, _ in sorted_entries[:count]]

        elif self.config.eviction_policy == "lru":
            # Sort by last accessed (oldest first)
            sorted_entries = sorted(
                self._local_cache.items(), key=lambda x: x[1].last_accessed
            )
            return [key for key, _ in sorted_entries[:count]]

        elif self.config.eviction_policy == "lfu":
            # Sort by hit count (lowest first)
            sorted_entries = sorted(
                self._local_cache.items(), key=lambda x: x[1].hit_count
            )
            return [key for key, _ in sorted_entries[:count]]

        else:
            # Default to score_based
            return self._get_eviction_candidates(count)

    def _generate_cache_key(
        self,
        agent_name: str,
        request: str,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
    ) -> str:
        """Generate a cache key for the request."""
        # Create a normalized key
        key_data = {
            "agent": agent_name,
            "request": request.strip().lower(),
            "context": context or {},
            "user_id": user_id,
            "workspace_id": workspace_id,
        }

        # Sort context keys for consistency
        if key_data["context"]:
            key_data["context"] = dict(sorted(key_data["context"].items()))

        # Generate hash
        key_string = json.dumps(key_data, sort_keys=True, separators=(",", ":"))
        return hashlib.sha256(key_string.encode()).hexdigest()

    async def get(
        self,
        agent_name: str,
        request: str,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        priority: CacheEntryPriority = CacheEntryPriority.NORMAL,
    ) -> Optional[Dict[str, Any]]:
        """Get cached response for the request."""
        start_time = time.time()

        try:
            cache_key = self._generate_cache_key(
                agent_name, request, context, user_id, workspace_id
            )

            # Try Redis first
            if self.redis_client:
                cached = await self._get_from_redis(cache_key)
                if cached:
                    self._cache_hits += 1
                    self._update_hit_rate_metrics(agent_name, True)

                    # Update response time metrics
                    response_time = time.time() - start_time
                    self._update_response_time_metrics(response_time)

                    return cached

            # Fall back to local cache
            if cache_key in self._local_cache:
                entry = self._local_cache[cache_key]
                if not entry.is_expired():
                    self._cache_hits += 1
                    self._update_hit_rate_metrics(agent_name, True)

                    # Update response time metrics
                    response_time = time.time() - start_time
                    self._update_response_time_metrics(response_time)

                    return entry.access()
                else:
                    # Remove expired entry
                    del self._local_cache[cache_key]
                    self._cache_evictions += 1
                    self._update_memory_usage(-entry.size_bytes)

            self._cache_misses += 1
            self._update_hit_rate_metrics(agent_name, False)
            return None

        except Exception as e:
            logger.error(f"Cache get error: {e}")
            self._cache_errors += 1
            return None

    def _update_hit_rate_metrics(self, agent_name: str, hit: bool):
        """Update hit rate metrics for agent."""
        if not self.config.enable_metrics:
            return

        if agent_name not in self._metrics["hit_rate_by_agent"]:
            self._metrics["hit_rate_by_agent"][agent_name] = {"hits": 0, "total": 0}

        self._metrics["hit_rate_by_agent"][agent_name]["total"] += 1
        if hit:
            self._metrics["hit_rate_by_agent"][agent_name]["hits"] += 1

    def _update_response_time_metrics(self, response_time: float):
        """Update response time metrics."""
        if not self.config.enable_metrics:
            return

        # Simple moving average
        current_avg = self._metrics["avg_response_time"]
        self._metrics["avg_response_time"] = (current_avg + response_time) / 2

    async def set(
        self,
        agent_name: str,
        request: str,
        response: Dict[str, Any],
        ttl: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None,
        user_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        priority: CacheEntryPriority = CacheEntryPriority.NORMAL,
        tags: Set[str] = None,
    ) -> bool:
        """Cache the agent response."""
        start_time = time.time()

        try:
            cache_key = self._generate_cache_key(
                agent_name, request, context, user_id, workspace_id
            )
            ttl = ttl or self.config.default_ttl

            # Limit TTL
            ttl = min(ttl, self.config.max_ttl)

            # Create cache entry
            entry = CacheEntry(
                response=response,
                timestamp=datetime.now(),
                ttl=ttl,
                priority=priority,
                tags=tags or set(),
            )

            # Check if we need to evict for memory
            if self._should_evict_for_memory(entry.size_bytes):
                await self._evict_for_memory(entry.size_bytes)

            # Store in Redis if available
            if self.redis_client:
                await self._set_in_redis(cache_key, entry, ttl)

            # Store in local cache
            old_size = 0
            if cache_key in self._local_cache:
                old_size = self._local_cache[cache_key].size_bytes

            self._local_cache[cache_key] = entry
            self._cache_sets += 1

            # Update memory usage
            size_delta = entry.size_bytes - old_size
            self._update_memory_usage(size_delta)

            # Cleanup if needed
            await self._cleanup_if_needed()

            # Update compression metrics
            if self.config.enable_metrics:
                original_size = len(json.dumps(response, default=str).encode())
                if original_size > 0:
                    compression_ratio = 1.0 - (entry.size_bytes / original_size)
                    self._metrics["compression_ratio"] = (
                        self._metrics["compression_ratio"] + compression_ratio
                    ) / 2

            return True

        except Exception as e:
            logger.error(f"Cache set error: {e}")
            self._cache_errors += 1
            return False

    async def _evict_for_memory(self, required_bytes: int):
        """Evict entries to free up memory."""
        freed_bytes = 0
        evicted_count = 0

        while freed_bytes < required_bytes and self._local_cache:
            candidates = self._get_eviction_candidates(5)  # Get 5 candidates

            for cache_key in candidates:
                if cache_key in self._local_cache:
                    entry = self._local_cache[cache_key]
                    freed_bytes += entry.size_bytes
                    del self._local_cache[cache_key]
                    self._cache_evictions += 1
                    evicted_count += 1

                    # Also remove from Redis if available
                    if self.redis_client:
                        try:
                            await self.redis_client.delete(cache_key)
                        except Exception:
                            pass

                    if freed_bytes >= required_bytes:
                        break

        self._update_memory_usage(-freed_bytes)
        logger.info(
            f"Evicted {evicted_count} cache entries, freed {freed_bytes / 1024:.1f} KB"
        )

    async def warmup_cache(self, agent_names: List[str] = None):
        """Warm up cache with frequently used agents."""
        if self._warming_up:
            logger.warning("Cache warmup already in progress")
            return

        self._warming_up = True
        agent_names = agent_names or self.config.preload_agents

        try:
            logger.info(f"Starting cache warmup for {len(agent_names)} agents")

            for agent_name in agent_names:
                try:
                    # Create warmup task for each agent
                    task = asyncio.create_task(self._warmup_agent(agent_name))
                    self._preload_tasks.append(task)
                except Exception as e:
                    logger.error(f"Failed to start warmup for {agent_name}: {e}")

            # Wait for all warmup tasks to complete
            if self._preload_tasks:
                await asyncio.gather(*self._preload_tasks, return_exceptions=True)

            logger.info("Cache warmup completed")

        finally:
            self._warming_up = False
            self._preload_tasks.clear()

    async def _warmup_agent(self, agent_name: str):
        """Warm up cache for a specific agent."""
        try:
            # Get common requests for this agent from access patterns
            common_requests = self._get_common_requests_for_agent(agent_name)

            for request_data in common_requests:
                request = request_data["request"]
                context = request_data.get("context", {})

                # Check if already cached
                cached = await self.get(agent_name, request, context)
                if cached:
                    continue

                # Simulate agent execution to warm cache
                # In a real implementation, you'd call the actual agent
                mock_response = {
                    "agent": agent_name,
                    "request": request,
                    "response": f"Warmed up response for {agent_name}",
                    "timestamp": datetime.now().isoformat(),
                    "warmup": True,
                }

                # Cache the response with higher priority
                await self.set(
                    agent_name=agent_name,
                    request=request,
                    response=mock_response,
                    ttl=self.config.default_ttl,
                    context=context,
                    priority=CacheEntryPriority.HIGH,
                    tags={"warmup", "preloaded"},
                )

                # Small delay to avoid overwhelming the system
                await asyncio.sleep(0.1)

            logger.info(
                f"Warmed up cache for agent {agent_name} with {len(common_requests)} requests"
            )

        except Exception as e:
            logger.error(f"Failed to warm up agent {agent_name}: {e}")

    def _get_common_requests_for_agent(self, agent_name: str) -> List[Dict[str, Any]]:
        """Get common requests for an agent based on access patterns."""
        # In a real implementation, this would analyze historical access patterns
        # For now, return some common mock requests
        common_requests = {
            "icp_architect": [
                {
                    "request": "Generate ICP profile for tech startup",
                    "context": {"industry": "technology"},
                },
                {
                    "request": "Create customer persona",
                    "context": {"business_type": "B2B"},
                },
                {"request": "Analyze market segment", "context": {"region": "US"}},
            ],
            "content_generator": [
                {
                    "request": "Generate blog post",
                    "context": {"topic": "AI", "length": "medium"},
                },
                {
                    "request": "Create social media content",
                    "context": {"platform": "twitter"},
                },
                {
                    "request": "Write email newsletter",
                    "context": {"audience": "developers"},
                },
            ],
            "data_analyzer": [
                {"request": "Analyze sales data", "context": {"period": "monthly"}},
                {
                    "request": "Generate insights report",
                    "context": {"type": "executive"},
                },
                {"request": "Predict trends", "context": {"horizon": "quarterly"}},
            ],
        }

        return common_requests.get(
            agent_name,
            [{"request": f"Default request for {agent_name}", "context": {}}],
        )

    async def _get_from_redis(self, cache_key: str) -> Optional[Dict[str, Any]]:
        """Get cached response from Redis."""
        try:
            data = await self.redis_client.get(cache_key)
            if data:
                # Decompress if needed
                decompressed_data = self._decompress_data(data)
                entry_data = json.loads(decompressed_data)
                entry = CacheEntry(**entry_data)

                if not entry.is_expired():
                    return entry.access()
                else:
                    # Remove expired entry
                    await self.redis_client.delete(cache_key)
                    return None
            return None
        except Exception as e:
            logger.error(f"Redis get error: {e}")
            return None

    async def _set_in_redis(self, cache_key: str, entry: CacheEntry, ttl: int):
        """Store cache entry in Redis."""
        try:
            entry_data = json.dumps(asdict(entry), default=str)
            compressed_data = self._compress_data(entry_data.encode())
            await self.redis_client.setex(cache_key, ttl, compressed_data)
        except Exception as e:
            logger.error(f"Redis set error: {e}")

    async def _cleanup_if_needed(self):
        """Cleanup cache if needed."""
        current_time = time.time()

        # Check if cleanup is needed
        if current_time - self._last_cleanup < self.config.cleanup_interval:
            return

        self._last_cleanup = current_time

        # Remove expired entries
        expired_keys = []
        for key, entry in self._local_cache.items():
            if entry.is_expired():
                expired_keys.append(key)

        for key in expired_keys:
            entry = self._local_cache[key]
            del self._local_cache[key]
            self._cache_evictions += 1
            self._update_memory_usage(-entry.size_bytes)

        # Limit cache size
        if len(self._local_cache) > self.config.max_entries:
            entries_to_remove = len(self._local_cache) - self.config.max_entries
            candidates = self._get_eviction_candidates(entries_to_remove)

            for key in candidates:
                if key in self._local_cache:
                    entry = self._local_cache[key]
                    del self._local_cache[key]
                    self._cache_evictions += 1
                    self._update_memory_usage(-entry.size_bytes)

        if expired_keys or len(self._local_cache) > self.config.max_entries:
            logger.info(f"Cache cleanup: removed {len(expired_keys)} expired entries")

    def get_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        total_requests = self._cache_hits + self._cache_misses
        hit_rate = self._cache_hits / total_requests if total_requests > 0 else 0

        # Calculate hit rates by agent
        agent_hit_rates = {}
        for agent_name, stats in self._metrics["hit_rate_by_agent"].items():
            agent_total = stats["total"]
            agent_hits = stats["hits"]
            agent_hit_rates[agent_name] = (
                agent_hits / agent_total if agent_total > 0 else 0
            )

        return {
            "basic_stats": {
                "hits": self._cache_hits,
                "misses": self._cache_misses,
                "sets": self._cache_sets,
                "evictions": self._cache_evictions,
                "errors": self._cache_errors,
                "hit_rate": hit_rate,
            },
            "local_cache_size": len(self._local_cache),
            "memory_usage_mb": self._total_memory_bytes / (1024 * 1024),
            "redis_available": self.redis_client is not None,
            "warming_up": self._warming_up,
            "config": {
                "default_ttl": self.config.default_ttl,
                "max_ttl": self.config.max_ttl,
                "max_entries": self.config.max_entries,
                "max_memory_mb": self.config.max_memory_mb,
                "compression_enabled": self.config.enable_compression,
                "eviction_policy": self.config.eviction_policy,
            },
            "performance_metrics": self._metrics if self.config.enable_metrics else {},
            "agent_hit_rates": agent_hit_rates,
        }

    async def invalidate(
        self,
        agent_name: Optional[str] = None,
        user_id: Optional[str] = None,
        workspace_id: Optional[str] = None,
        pattern: Optional[str] = None,
        tags: Optional[Set[str]] = None,
    ) -> int:
        """Invalidate cache entries matching criteria."""
        invalidated = 0

        try:
            # Invalidate local cache
            keys_to_remove = []
            for cache_key, entry in self._local_cache.items():
                should_remove = False

                if agent_name and agent_name in cache_key:
                    should_remove = True
                if user_id and user_id in cache_key:
                    should_remove = True
                if workspace_id and workspace_id in cache_key:
                    should_remove = True
                if pattern and pattern in cache_key:
                    should_remove = True
                if tags and entry.tags.intersection(tags):
                    should_remove = True

                if should_remove:
                    keys_to_remove.append(cache_key)

            for key in keys_to_remove:
                if key in self._local_cache:
                    entry = self._local_cache[key]
                    del self._local_cache[key]
                    self._cache_evictions += 1
                    self._update_memory_usage(-entry.size_bytes)
                    invalidated += 1

            # Invalidate Redis cache
            if self.redis_client:
                redis_pattern = f"*{pattern}*" if pattern else "*"
                keys = await self.redis_client.keys(redis_pattern)
                if keys:
                    await self.redis_client.delete(*keys)
                    invalidated += len(keys)

            logger.info(f"Invalidated {invalidated} cache entries")
            return invalidated

        except Exception as e:
            logger.error(f"Cache invalidation error: {e}")
            return 0

    def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self._stats["hits"] + self._stats["misses"]
        hit_rate = self._stats["hits"] / total_requests if total_requests > 0 else 0

        return {
            "stats": self._stats.copy(),
            "hit_rate": hit_rate,
            "local_cache_size": len(self._local_cache),
            "redis_available": self.redis_client is not None,
            "config": {
                "default_ttl": self.config.default_ttl,
                "max_ttl": self.config.max_ttl,
                "max_entries": self.config.max_entries,
            },
        }


# Global cache instance
_agent_cache: Optional[AgentCache] = None


async def get_agent_cache() -> AgentCache:
    """Get the global agent cache instance."""
    global _agent_cache
    if _agent_cache is None:
        # Try to get Redis client
        redis_client = None
        try:
            from connections import get_redis_pool

            redis_pool = await get_redis_pool()
            if redis_pool._initialized:
                redis_client = redis_pool._redis_client
        except ImportError:
            pass

        _agent_cache = AgentCache(redis_client=redis_client)
    return _agent_cache


async def cache_agent_response(
    agent_name: str,
    request: str,
    response: Dict[str, Any],
    ttl: Optional[int] = None,
    context: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None,
    workspace_id: Optional[str] = None,
) -> bool:
    """Cache agent response (convenience function)."""
    cache = await get_agent_cache()
    return await cache.set(
        agent_name, request, response, ttl, context, user_id, workspace_id
    )


async def get_cached_response(
    agent_name: str,
    request: str,
    context: Optional[Dict[str, Any]] = None,
    user_id: Optional[str] = None,
    workspace_id: Optional[str] = None,
) -> Optional[Dict[str, Any]]:
    """Get cached agent response (convenience function)."""
    cache = await get_agent_cache()
    return await cache.get(agent_name, request, context, user_id, workspace_id)


async def invalidate_cache(
    agent_name: Optional[str] = None,
    user_id: Optional[str] = None,
    workspace_id: Optional[str] = None,
    pattern: Optional[str] = None,
) -> int:
    """Invalidate cache entries (convenience function)."""
    cache = await get_agent_cache()
    return await cache.invalidate(agent_name, user_id, workspace_id, pattern)


def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics (convenience function)."""
    if _agent_cache:
        return _agent_cache.get_stats()
    return {"error": "Cache not initialized"}


# Cache decorator for agent methods
def cached_response(ttl: int = 3600, key_prefix: str = ""):
    """Decorator for caching agent method responses."""

    def decorator(func):
        async def wrapper(self, *args, **kwargs):
            # Generate cache key
            agent_name = getattr(self, "name", self.__class__.__name__)
            request = str(args) + str(sorted(kwargs.items()))

            # Try to get from cache
            cached = await get_cached_response(
                f"{key_prefix}{agent_name}",
                request,
                user_id=kwargs.get("user_id"),
                workspace_id=kwargs.get("workspace_id"),
            )

            if cached:
                return cached

            # Execute function
            result = await func(self, *args, **kwargs)

            # Cache the result
            if isinstance(result, dict):
                await cache_agent_response(
                    f"{key_prefix}{agent_name}",
                    request,
                    result,
                    ttl=ttl,
                    user_id=kwargs.get("user_id"),
                    workspace_id=kwargs.get("workspace_id"),
                )

            return result

        return wrapper

    return decorator
