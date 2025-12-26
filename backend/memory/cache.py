import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple, Union
from dataclasses import dataclass, field
from collections import defaultdict
import time

from backend.memory.consolidated import MemoryFragment
from backend.memory.swarm_coordinator import SwarmMemoryCoordinator

logger = logging.getLogger("raptorflow.memory.cache")


@dataclass
class CacheEntry:
    """Represents a cache entry with metadata."""
    key: str
    value: Any
    created_at: datetime = field(default_factory=datetime.now)
    last_accessed: datetime = field(default_factory=datetime.now)
    access_count: int = 0
    ttl_seconds: int = 300
    size_bytes: int = 0
    tags: Set[str] = field(default_factory=set)
    
    @property
    def is_expired(self) -> bool:
        """Check if the cache entry is expired."""
        return datetime.now() - self.created_at > timedelta(seconds=self.ttl_seconds)
    
    @property
    def age_seconds(self) -> float:
        """Get the age of the cache entry in seconds."""
        return (datetime.now() - self.created_at).total_seconds()


class SwarmMemoryCache:
    """
    High-performance multi-tier cache for swarm memory operations.
    Provides L0 (hot), L1 (warm), and L2 (cold) cache tiers.
    """
    
    def __init__(self, max_memory_mb: int = 100, max_entries: int = 10000):
        self.max_memory_bytes = max_memory_mb * 1024 * 1024
        self.max_entries = max_entries
        
        # Multi-tier cache storage
        self.l0_hot: Dict[str, CacheEntry] = {}  # Most frequently accessed
        self.l1_warm: Dict[str, CacheEntry] = {}  # Moderately accessed
        self.l2_cold: Dict[str, CacheEntry] = {}  # Least frequently accessed
        
        # Cache statistics
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "promotions": 0,
            "demotions": 0,
            "total_requests": 0
        }
        
        # Access tracking for LRU and frequency-based eviction
        self.access_order: List[str] = []  # For LRU
        self.access_frequency: Dict[str, int] = defaultdict(int)
        
        # Cache locks for thread safety
        self._cache_lock = asyncio.Lock()
        self._stats_lock = asyncio.Lock()
        
        # Background cleanup task
        self._cleanup_task = None
        self._start_cleanup_task()
        
        logger.info(f"SwarmMemoryCache initialized: {max_memory_mb}MB, {max_entries} max entries")
    
    def _start_cleanup_task(self):
        """Starts the background cleanup task."""
        self._cleanup_task = asyncio.create_task(self._periodic_cleanup())
    
    async def get(self, key: str) -> Optional[Any]:
        """
        Gets a value from the cache with multi-tier lookup.
        """
        async with self._cache_lock:
            self.stats["total_requests"] += 1
            
            # Check L0 (hot) first
            if key in self.l0_hot:
                entry = self.l0_hot[key]
                if not entry.is_expired:
                    await self._update_access_stats(entry)
                    self.stats["hits"] += 1
                    return entry.value
                else:
                    await self._remove_entry(key, "l0_hot")
            
            # Check L1 (warm)
            if key in self.l1_warm:
                entry = self.l1_warm[key]
                if not entry.is_expired:
                    await self._update_access_stats(entry)
                    # Promote to L0 if frequently accessed
                    if entry.access_count > 5:
                        await self._promote_entry(key, "l1_warm", "l0_hot")
                    self.stats["hits"] += 1
                    return entry.value
                else:
                    await self._remove_entry(key, "l1_warm")
            
            # Check L2 (cold)
            if key in self.l2_cold:
                entry = self.l2_cold[key]
                if not entry.is_expired:
                    await self._update_access_stats(entry)
                    # Promote to L1 if accessed
                    await self._promote_entry(key, "l2_cold", "l1_warm")
                    self.stats["hits"] += 1
                    return entry.value
                else:
                    await self._remove_entry(key, "l2_cold")
            
            self.stats["misses"] += 1
            return None
    
    async def set(
        self, 
        key: str, 
        value: Any, 
        ttl: int = 300,
        tags: Optional[Set[str]] = None,
        tier: str = "l1_warm"
    ) -> bool:
        """
        Sets a value in the cache with intelligent tier placement.
        """
        try:
            # Calculate size
            size_bytes = len(json.dumps(value, default=str).encode())
            
            # Create cache entry
            entry = CacheEntry(
                key=key,
                value=value,
                ttl_seconds=ttl,
                size_bytes=size_bytes,
                tags=tags or set()
            )
            
            async with self._cache_lock:
                # Ensure capacity
                await self._ensure_capacity(entry.size_bytes)
                
                # Remove existing entry if present
                await self._remove_from_all_tiers(key)
                
                # Add to appropriate tier
                tier_dict = getattr(self, tier)
                tier_dict[key] = entry
                
                await self._update_access_stats(entry)
                
            return True
            
        except Exception as e:
            logger.error(f"Cache set failed for key {key}: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Deletes a key from all cache tiers."""
        async with self._cache_lock:
            return await self._remove_from_all_tiers(key)
    
    async def clear_tier(self, tier: str) -> int:
        """Clears a specific cache tier."""
        async with self._cache_lock:
            tier_dict = getattr(self, tier, {})
            count = len(tier_dict)
            tier_dict.clear()
            
            # Update access tracking
            for key in list(tier_dict.keys()):
                self.access_order = [k for k in self.access_order if k != key]
                self.access_frequency.pop(key, None)
            
            return count
    
    async def get_by_tags(self, tags: Set[str], limit: int = 50) -> List[Tuple[str, Any]]:
        """
        Gets cache entries by tags, searching all tiers.
        """
        results = []
        
        async with self._cache_lock:
            all_entries = {**self.l0_hot, **self.l1_warm, **self.l2_cold}
            
            for key, entry in all_entries.items():
                if not entry.is_expired and tags.intersection(entry.tags):
                    results.append((key, entry.value))
                    if len(results) >= limit:
                        break
            
            # Sort by access frequency and recency
            results.sort(key=lambda x: (
                self.access_frequency.get(x[0], 0),
                -all_entries[x[0]].age_seconds
            ), reverse=True)
        
        return results[:limit]
    
    async def get_memory_fragments(
        self, 
        agent_filter: Optional[List[str]] = None,
        tier_filter: Optional[List[str]] = None,
        limit: int = 50
    ) -> List[MemoryFragment]:
        """
        Gets cached memory fragments with filtering.
        """
        fragments = []
        
        async with self._cache_lock:
            all_entries = {**self.l0_hot, **self.l1_warm, **self.l2_cold}
            
            for entry in all_entries.values():
                if entry.is_expired:
                    continue
                
                value = entry.value
                if isinstance(value, MemoryFragment):
                    # Apply filters
                    if agent_filter and value.agent_id not in agent_filter:
                        continue
                    if tier_filter and value.memory_tier not in tier_filter:
                        continue
                    
                    fragments.append(value)
                    if len(fragments) >= limit:
                        break
        
        return fragments
    
    async def _update_access_stats(self, entry: CacheEntry):
        """Updates access statistics for a cache entry."""
        entry.last_accessed = datetime.now()
        entry.access_count += 1
        self.access_frequency[entry.key] = entry.access_count
        
        # Update LRU order
        if entry.key in self.access_order:
            self.access_order.remove(entry.key)
        self.access_order.append(entry.key)
    
    async def _promote_entry(self, key: str, from_tier: str, to_tier: str):
        """Promotes an entry from one tier to another."""
        from_dict = getattr(self, from_tier)
        to_dict = getattr(self, to_tier)
        
        if key in from_dict:
            entry = from_dict.pop(key)
            to_dict[key] = entry
            self.stats["promotions"] += 1
            logger.debug(f"Promoted {key} from {from_tier} to {to_tier}")
    
    async def _demote_entry(self, key: str, from_tier: str, to_tier: str):
        """Demotes an entry from one tier to another."""
        from_dict = getattr(self, from_tier)
        to_dict = getattr(self, to_tier)
        
        if key in from_dict:
            entry = from_dict.pop(key)
            to_dict[key] = entry
            self.stats["demotions"] += 1
            logger.debug(f"Demoted {key} from {from_tier} to {to_tier}")
    
    async def _remove_entry(self, key: str, tier: str):
        """Removes an entry from a specific tier."""
        tier_dict = getattr(self, tier)
        if key in tier_dict:
            del tier_dict[key]
            self.access_order = [k for k in self.access_order if k != key]
            self.access_frequency.pop(key, None)
    
    async def _remove_from_all_tiers(self, key: str) -> bool:
        """Removes an entry from all tiers."""
        removed = False
        for tier_name in ["l0_hot", "l1_warm", "l2_cold"]:
            if key in getattr(self, tier_name, {}):
                await self._remove_entry(key, tier_name)
                removed = True
        return removed
    
    async def _ensure_capacity(self, required_bytes: int):
        """Ensures cache has enough capacity for new entry."""
        current_memory = self._get_current_memory_usage()
        current_entries = len(self.l0_hot) + len(self.l1_warm) + len(self.l2_cold)
        
        # Check if we need to evict entries
        while (current_memory + required_bytes > self.max_memory_bytes or 
               current_entries >= self.max_entries):
            
            # Evict least recently used entry from L2 first
            if self.l2_cold:
                lru_key = self._get_lru_key(self.l2_cold)
                await self._remove_entry(lru_key, "l2_cold")
                self.stats["evictions"] += 1
            elif self.l1_warm:
                # Demote from L1 to L2
                lru_key = self._get_lru_key(self.l1_warm)
                await self._demote_entry(lru_key, "l1_warm", "l2_cold")
            elif self.l0_hot:
                # Demote from L0 to L1
                lru_key = self._get_lru_key(self.l0_hot)
                await self._demote_entry(lru_key, "l0_hot", "l1_warm")
            else:
                break
            
            current_memory = self._get_current_memory_usage()
            current_entries = len(self.l0_hot) + len(self.l1_warm) + len(self.l2_cold)
    
    def _get_lru_key(self, tier_dict: Dict[str, CacheEntry]) -> str:
        """Gets the least recently used key from a tier."""
        if not tier_dict:
            return None
        
        # Find the entry with the oldest last_accessed time
        lru_key = min(tier_dict.keys(), key=lambda k: tier_dict[k].last_accessed)
        return lru_key
    
    def _get_current_memory_usage(self) -> int:
        """Calculates current memory usage in bytes."""
        total = 0
        for tier_dict in [self.l0_hot, self.l1_warm, self.l2_cold]:
            total += sum(entry.size_bytes for entry in tier_dict.values())
        return total
    
    async def _periodic_cleanup(self):
        """Background task for periodic cleanup of expired entries."""
        while True:
            try:
                await asyncio.sleep(60)  # Run every minute
                
                async with self._cache_lock:
                    expired_count = 0
                    
                    # Check all tiers for expired entries
                    for tier_name in ["l0_hot", "l1_warm", "l2_cold"]:
                        tier_dict = getattr(self, tier_name)
                        expired_keys = [
                            key for key, entry in tier_dict.items()
                            if entry.is_expired
                        ]
                        
                        for key in expired_keys:
                            await self._remove_entry(key, tier_name)
                            expired_count += 1
                    
                    if expired_count > 0:
                        logger.info(f"Cleaned up {expired_count} expired cache entries")
                        
            except Exception as e:
                logger.error(f"Cache cleanup failed: {e}")
    
    async def get_cache_stats(self) -> Dict[str, Any]:
        """Returns comprehensive cache statistics."""
        async with self._stats_lock:
            total_requests = self.stats["total_requests"]
            hit_rate = self.stats["hits"] / max(total_requests, 1)
            
            return {
                "hit_rate": hit_rate,
                "total_requests": total_requests,
                "hits": self.stats["hits"],
                "misses": self.stats["misses"],
                "evictions": self.stats["evictions"],
                "promotions": self.stats["promotions"],
                "demotions": self.stats["demotions"],
                "memory_usage_bytes": self._get_current_memory_usage(),
                "memory_usage_mb": self._get_current_memory_usage() / (1024 * 1024),
                "total_entries": len(self.l0_hot) + len(self.l1_warm) + len(self.l2_cold),
                "tier_distribution": {
                    "l0_hot": len(self.l0_hot),
                    "l1_warm": len(self.l1_warm),
                    "l2_cold": len(self.l2_cold)
                }
            }
    
    async def cleanup(self):
        """Cleans up cache resources."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass
        
        async with self._cache_lock:
            self.l0_hot.clear()
            self.l1_warm.clear()
            self.l2_cold.clear()
            self.access_order.clear()
            self.access_frequency.clear()
        
        logger.info("SwarmMemoryCache cleaned up")


class CachedSwarmCoordinator:
    """
    Wrapper around SwarmMemoryCoordinator with intelligent caching.
    Provides high-performance memory operations for active swarms.
    """
    
    def __init__(self, coordinator: SwarmMemoryCoordinator, cache_size_mb: int = 50):
        self.coordinator = coordinator
        self.cache = SwarmMemoryCache(max_memory_mb=cache_size_mb)
        
        # Cache configuration
        self.search_cache_ttl = 300  # 5 minutes
        self.context_cache_ttl = 180  # 3 minutes
        self.metrics_cache_ttl = 60   # 1 minute
        
        logger.info(f"CachedSwarmCoordinator initialized with {cache_size_mb}MB cache")
    
    async def search_swarm_memory(
        self,
        query: str,
        agent_filter: Optional[List[str]] = None,
        tier_filter: Optional[List[str]] = None,
        limit: int = 10,
        use_cache: bool = True
    ) -> List[MemoryFragment]:
        """
        Cached search across swarm memory.
        """
        cache_key = f"search:{hash(query)}_{agent_filter}_{tier_filter}_{limit}"
        
        if use_cache:
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                logger.debug(f"Cache hit for search: {query[:50]}...")
                return cached_result
        
        # Perform search through coordinator
        results = await self.coordinator.search_swarm_memory(
            query=query,
            agent_filter=agent_filter,
            tier_filter=tier_filter,
            limit=limit,
            use_cache=False  # Avoid double caching
        )
        
        # Cache results
        if use_cache and results:
            await self.cache.set(
                cache_key,
                results,
                ttl=self.search_cache_ttl,
                tags={"search", "memory"}
            )
        
        return results
    
    async def get_agent_context(
        self,
        agent_id: str,
        query: Optional[str] = None,
        include_cross_agent: bool = True,
        use_cache: bool = True
    ) -> Dict[str, Any]:
        """
        Cached agent context retrieval.
        """
        cache_key = f"context:{agent_id}:{hash(query or '')}_{include_cross_agent}"
        
        if use_cache:
            cached_context = await self.cache.get(cache_key)
            if cached_context:
                logger.debug(f"Cache hit for agent context: {agent_id}")
                return cached_context
        
        # Get context through coordinator
        context = await self.coordinator.get_agent_context(
            agent_id=agent_id,
            query=query,
            include_cross_agent=include_cross_agent
        )
        
        # Cache context
        if use_cache:
            await self.cache.set(
                cache_key,
                context,
                ttl=self.context_cache_ttl,
                tags={"context", "agent", agent_id}
            )
        
        return context
    
    async def get_memory_statistics(self, use_cache: bool = True) -> Dict[str, Any]:
        """
        Cached memory statistics retrieval.
        """
        cache_key = "memory_stats"
        
        if use_cache:
            cached_stats = await self.cache.get(cache_key)
            if cached_stats:
                return cached_stats
        
        # Get stats through coordinator
        stats = await self.coordinator.get_swarm_memory_metrics()
        
        # Add cache statistics
        cache_stats = await self.cache.get_cache_stats()
        stats["cache_performance"] = cache_stats
        
        # Cache combined stats
        if use_cache:
            await self.cache.set(
                cache_key,
                stats,
                ttl=self.metrics_cache_ttl,
                tags={"metrics", "stats"}
            )
        
        return stats
    
    async def record_agent_memory(
        self,
        agent_id: str,
        content: Any,
        metadata: Optional[Dict[str, Any]] = None,
        importance: float = 0.5,
        thread_id: Optional[str] = None
    ) -> bool:
        """
        Records agent memory and invalidates relevant cache entries.
        """
        # Record through coordinator
        success = await self.coordinator.record_agent_memory(
            agent_id=agent_id,
            content=content,
            metadata=metadata,
            importance=importance,
            thread_id=thread_id
        )
        
        if success:
            # Invalidate relevant cache entries
            await self._invalidate_agent_cache(agent_id)
            
            # Cache the new memory fragment
            if isinstance(content, MemoryFragment):
                cache_key = f"fragment:{content.id}"
                await self.cache.set(
                    cache_key,
                    content,
                    ttl=300,
                    tags={"fragment", "memory", agent_id}
                )
        
        return success
    
    async def _invalidate_agent_cache(self, agent_id: str):
        """Invalidates cache entries related to a specific agent."""
        # Get all entries with agent tag
        agent_entries = await self.cache.get_by_tags({agent_id}, limit=100)
        
        for key, _ in agent_entries:
            await self.cache.delete(key)
        
        logger.debug(f"Invalidated {len(agent_entries)} cache entries for agent {agent_id}")
    
    async def cleanup(self):
        """Cleans up cache resources."""
        await self.cache.cleanup()


# Factory function
def create_cached_coordinator(coordinator: SwarmMemoryCoordinator, cache_size_mb: int = 50) -> CachedSwarmCoordinator:
    """Creates a cached wrapper around a swarm memory coordinator."""
    return CachedSwarmCoordinator(coordinator, cache_size_mb)
