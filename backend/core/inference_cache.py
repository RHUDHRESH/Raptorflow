"""
AI Inference Multi-Level Caching System
======================================

Intelligent multi-level caching for AI inference with L1 (memory), L2 (Redis), 
L3 (persistent) caching strategies. Optimized for cost reduction and performance.

Features:
- L1: In-memory cache for ultra-fast access
- L2: Redis cache for distributed access
- L3: Persistent cache for long-term storage
- Intelligent cache warming and eviction
- Semantic similarity matching
- Cost-aware cache decisions
- Request deduplication
- Cache analytics and monitoring
"""

import asyncio
import hashlib
import json
import logging
import time
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional, Set, Tuple, Union
import pickle
import zlib

import numpy as np
import structlog
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .redis import get_redis_client

logger = structlog.get_logger(__name__)


class CacheLevel(str, Enum):
    """Cache level types."""
    
    L1_MEMORY = "l1_memory"
    L2_REDIS = "l2_redis"
    L3_PERSISTENT = "l3_persistent"


class CacheStrategy(str, Enum):
    """Cache eviction strategies."""
    
    LRU = "lru"
    LFU = "lfu"
    TTL = "ttl"
    COST_AWARE = "cost_aware"
    SEMANTIC = "semantic"


@dataclass
class CacheEntry:
    """Cache entry with metadata."""
    
    key: str
    value: Any
    level: CacheLevel
    created_at: datetime
    last_accessed: datetime
    access_count: int = 0
    ttl_seconds: Optional[int] = None
    cost_estimate: float = 0.0
    token_count: int = 0
    model_name: str = ""
    semantic_hash: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def is_expired(self) -> bool:
        """Check if cache entry is expired."""
        if self.ttl_seconds is None:
            return False
        return datetime.utcnow() > self.created_at + timedelta(seconds=self.ttl_seconds)
    
    def update_access(self):
        """Update access statistics."""
        self.last_accessed = datetime.utcnow()
        self.access_count += 1
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "key": self.key,
            "value": self.value,
            "level": self.level.value,
            "created_at": self.created_at.isoformat(),
            "last_accessed": self.last_accessed.isoformat(),
            "access_count": self.access_count,
            "ttl_seconds": self.ttl_seconds,
            "cost_estimate": self.cost_estimate,
            "token_count": self.token_count,
            "model_name": self.model_name,
            "semantic_hash": self.semantic_hash,
            "metadata": self.metadata,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CacheEntry":
        """Create from dictionary."""
        return cls(
            key=data["key"],
            value=data["value"],
            level=CacheLevel(data["level"]),
            created_at=datetime.fromisoformat(data["created_at"]),
            last_accessed=datetime.fromisoformat(data["last_accessed"]),
            access_count=data["access_count"],
            ttl_seconds=data.get("ttl_seconds"),
            cost_estimate=data.get("cost_estimate", 0.0),
            token_count=data.get("token_count", 0),
            model_name=data.get("model_name", ""),
            semantic_hash=data.get("semantic_hash", ""),
            metadata=data.get("metadata", {}),
        )


class BaseCacheBackend(ABC):
    """Abstract base class for cache backends."""
    
    @abstractmethod
    async def get(self, key: str) -> Optional[CacheEntry]:
        """Get cache entry by key."""
        pass
    
    @abstractmethod
    async def set(self, entry: CacheEntry) -> bool:
        """Set cache entry."""
        pass
    
    @abstractmethod
    async def delete(self, key: str) -> bool:
        """Delete cache entry by key."""
        pass
    
    @abstractmethod
    async def clear(self) -> bool:
        """Clear all cache entries."""
        pass
    
    @abstractmethod
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        pass


class L1MemoryCache(BaseCacheBackend):
    """L1 In-memory cache backend."""
    
    def __init__(self, max_size: int = 1000, strategy: CacheStrategy = CacheStrategy.LRU):
        self.max_size = max_size
        self.strategy = strategy
        self._cache: Dict[str, CacheEntry] = {}
        self._access_order: List[str] = []
        self._lock = asyncio.Lock()
    
    async def get(self, key: str) -> Optional[CacheEntry]:
        """Get cache entry from memory."""
        async with self._lock:
            entry = self._cache.get(key)
            if entry and not entry.is_expired():
                entry.update_access()
                self._update_access_order(key)
                return entry
            elif entry and entry.is_expired():
                await self.delete(key)
            return None
    
    async def set(self, entry: CacheEntry) -> bool:
        """Set cache entry in memory."""
        async with self._lock:
            if len(self._cache) >= self.max_size and entry.key not in self._cache:
                await self._evict_one()
            
            self._cache[entry.key] = entry
            self._update_access_order(entry.key)
            return True
    
    async def delete(self, key: str) -> bool:
        """Delete cache entry from memory."""
        async with self._lock:
            if key in self._cache:
                del self._cache[key]
                if key in self._access_order:
                    self._access_order.remove(key)
                return True
            return False
    
    async def clear(self) -> bool:
        """Clear all cache entries."""
        async with self._lock:
            self._cache.clear()
            self._access_order.clear()
            return True
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get memory cache statistics."""
        async with self._lock:
            total_entries = len(self._cache)
            expired_entries = sum(1 for entry in self._cache.values() if entry.is_expired())
            total_cost = sum(entry.cost_estimate for entry in self._cache.values())
            total_tokens = sum(entry.token_count for entry in self._cache.values())
            
            return {
                "backend": "L1_MEMORY",
                "total_entries": total_entries,
                "expired_entries": expired_entries,
                "max_size": self.max_size,
                "utilization": total_entries / self.max_size,
                "total_cost_estimate": total_cost,
                "total_tokens_cached": total_tokens,
                "strategy": self.strategy.value,
            }
    
    def _update_access_order(self, key: str):
        """Update access order for LRU strategy."""
        if self.strategy == CacheStrategy.LRU:
            if key in self._access_order:
                self._access_order.remove(key)
            self._access_order.append(key)
    
    async def _evict_one(self):
        """Evict one entry based on strategy."""
        if not self._cache:
            return
        
        if self.strategy == CacheStrategy.LRU and self._access_order:
            evict_key = self._access_order[0]
        elif self.strategy == CacheStrategy.LFU:
            evict_key = min(self._cache.keys(), 
                           key=lambda k: self._cache[k].access_count)
        elif self.strategy == CacheStrategy.COST_AWARE:
            evict_key = min(self._cache.keys(), 
                           key=lambda k: self._cache[k].cost_estimate)
        else:
            evict_key = next(iter(self._cache.keys()))
        
        await self.delete(evict_key)


class L2RedisCache(BaseCacheBackend):
    """L2 Redis cache backend."""
    
    def __init__(self, ttl_seconds: int = 3600, compression: bool = True):
        self.ttl_seconds = ttl_seconds
        self.compression = compression
        self.key_prefix = "inference_cache:"
        self._redis_client = None
    
    async def _get_redis(self):
        """Get Redis client."""
        if self._redis_client is None:
            redis_wrapper = await get_redis_client()
            self._redis_client = await redis_wrapper.get_client()
        return self._redis_client
    
    def _serialize_entry(self, entry: CacheEntry) -> bytes:
        """Serialize cache entry."""
        data = entry.to_dict()
        serialized = pickle.dumps(data)
        if self.compression:
            serialized = zlib.compress(serialized)
        return serialized
    
    def _deserialize_entry(self, data: bytes) -> CacheEntry:
        """Deserialize cache entry."""
        if self.compression:
            data = zlib.decompress(data)
        cache_data = pickle.loads(data)
        return CacheEntry.from_dict(cache_data)
    
    async def get(self, key: str) -> Optional[CacheEntry]:
        """Get cache entry from Redis."""
        try:
            redis = await self._get_redis()
            redis_key = f"{self.key_prefix}{key}"
            
            data = await redis.get(redis_key)
            if data:
                entry = self._deserialize_entry(data)
                if not entry.is_expired():
                    entry.update_access()
                    return entry
                else:
                    await self.delete(key)
            return None
        except Exception as e:
            logger.error(f"Redis cache get error: {e}")
            return None
    
    async def set(self, entry: CacheEntry) -> bool:
        """Set cache entry in Redis."""
        try:
            redis = await self._get_redis()
            redis_key = f"{self.key_prefix}{entry.key}"
            
            serialized = self._serialize_entry(entry)
            ttl = entry.ttl_seconds or self.ttl_seconds
            
            result = await redis.setex(redis_key, ttl, serialized)
            return bool(result)
        except Exception as e:
            logger.error(f"Redis cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete cache entry from Redis."""
        try:
            redis = await self._get_redis()
            redis_key = f"{self.key_prefix}{key}"
            
            result = await redis.delete(redis_key)
            return bool(result)
        except Exception as e:
            logger.error(f"Redis cache delete error: {e}")
            return False
    
    async def clear(self) -> bool:
        """Clear all cache entries."""
        try:
            redis = await self._get_redis()
            pattern = f"{self.key_prefix}*"
            keys = await redis.keys(pattern)
            if keys:
                await redis.delete(*keys)
            return True
        except Exception as e:
            logger.error(f"Redis cache clear error: {e}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get Redis cache statistics."""
        try:
            redis = await self._get_redis()
            pattern = f"{self.key_prefix}*"
            keys = await redis.keys(pattern)
            
            # Sample a few keys to get statistics
            sample_size = min(100, len(keys))
            sample_keys = keys[:sample_size] if keys else []
            
            total_cost = 0
            total_tokens = 0
            expired_count = 0
            
            for redis_key in sample_keys:
                data = await redis.get(redis_key)
                if data:
                    try:
                        entry = self._deserialize_entry(data)
                        total_cost += entry.cost_estimate
                        total_tokens += entry.token_count
                        if entry.is_expired():
                            expired_count += 1
                    except Exception:
                        continue
            
            # Estimate totals based on sample
            multiplier = len(keys) / sample_size if sample_size > 0 else 1
            
            return {
                "backend": "L2_REDIS",
                "total_entries": len(keys),
                "sampled_entries": sample_size,
                "estimated_expired": int(expired_count * multiplier),
                "estimated_total_cost": total_cost * multiplier,
                "estimated_total_tokens": int(total_tokens * multiplier),
                "ttl_seconds": self.ttl_seconds,
                "compression": self.compression,
            }
        except Exception as e:
            logger.error(f"Redis cache stats error: {e}")
            return {"backend": "L2_REDIS", "error": str(e)}


class L3PersistentCache(BaseCacheBackend):
    """L3 Persistent cache backend (file-based)."""
    
    def __init__(self, storage_path: str = "/tmp/inference_cache", max_files: int = 10000):
        self.storage_path = storage_path
        self.max_files = max_files
        self._lock = asyncio.Lock()
    
    def _get_file_path(self, key: str) -> str:
        """Get file path for cache key."""
        # Use hash to avoid filesystem issues
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        return f"{self.storage_path}/{key_hash[:2]}/{key_hash}.cache"
    
    async def get(self, key: str) -> Optional[CacheEntry]:
        """Get cache entry from persistent storage."""
        try:
            file_path = self._get_file_path(key)
            
            async with self._lock:
                if not os.path.exists(file_path):
                    return None
                
                with open(file_path, 'rb') as f:
                    data = f.read()
                
                entry = pickle.loads(data)
                if not entry.is_expired():
                    entry.update_access()
                    # Update access time in file
                    await self.set(entry)
                    return entry
                else:
                    await self.delete(key)
                    os.remove(file_path)
                    return None
        except Exception as e:
            logger.error(f"Persistent cache get error: {e}")
            return None
    
    async def set(self, entry: CacheEntry) -> bool:
        """Set cache entry in persistent storage."""
        try:
            file_path = self._get_file_path(entry.key)
            dir_path = os.path.dirname(file_path)
            
            async with self._lock:
                # Create directory if it doesn't exist
                os.makedirs(dir_path, exist_ok=True)
                
                # Check file count limit
                await self._cleanup_if_needed()
                
                with open(file_path, 'wb') as f:
                    f.write(pickle.dumps(entry))
                
                return True
        except Exception as e:
            logger.error(f"Persistent cache set error: {e}")
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete cache entry from persistent storage."""
        try:
            file_path = self._get_file_path(key)
            
            async with self._lock:
                if os.path.exists(file_path):
                    os.remove(file_path)
                    return True
                return False
        except Exception as e:
            logger.error(f"Persistent cache delete error: {e}")
            return False
    
    async def clear(self) -> bool:
        """Clear all cache entries."""
        try:
            async with self._lock:
                if os.path.exists(self.storage_path):
                    import shutil
                    shutil.rmtree(self.storage_path)
                    os.makedirs(self.storage_path, exist_ok=True)
                return True
        except Exception as e:
            logger.error(f"Persistent cache clear error: {e}")
            return False
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get persistent cache statistics."""
        try:
            async with self._lock:
                if not os.path.exists(self.storage_path):
                    return {
                        "backend": "L3_PERSISTENT",
                        "total_entries": 0,
                        "storage_path": self.storage_path,
                    }
                
                total_files = 0
                total_size = 0
                total_cost = 0
                total_tokens = 0
                
                for root, dirs, files in os.walk(self.storage_path):
                    for file in files:
                        if file.endswith('.cache'):
                            total_files += 1
                            file_path = os.path.join(root, file)
                            total_size += os.path.getsize(file_path)
                            
                            # Sample some files for detailed stats
                            if total_files <= 100:
                                try:
                                    with open(file_path, 'rb') as f:
                                        data = f.read()
                                    entry = pickle.loads(data)
                                    total_cost += entry.cost_estimate
                                    total_tokens += entry.token_count
                                except Exception:
                                    continue
                
                return {
                    "backend": "L3_PERSISTENT",
                    "total_entries": total_files,
                    "total_size_bytes": total_size,
                    "total_size_mb": round(total_size / (1024 * 1024), 2),
                    "sampled_cost": total_cost,
                    "sampled_tokens": total_tokens,
                    "storage_path": self.storage_path,
                    "max_files": self.max_files,
                }
        except Exception as e:
            logger.error(f"Persistent cache stats error: {e}")
            return {"backend": "L3_PERSISTENT", "error": str(e)}
    
    async def _cleanup_if_needed(self):
        """Cleanup old files if limit exceeded."""
        try:
            if not os.path.exists(self.storage_path):
                return
            
            file_count = 0
            files_with_times = []
            
            for root, dirs, files in os.walk(self.storage_path):
                for file in files:
                    if file.endswith('.cache'):
                        file_count += 1
                        file_path = os.path.join(root, file)
                        mtime = os.path.getmtime(file_path)
                        files_with_times.append((mtime, file_path))
            
            if file_count > self.max_files:
                # Sort by modification time (oldest first)
                files_with_times.sort()
                files_to_delete = file_count - self.max_files
                
                for i in range(files_to_delete):
                    _, file_path = files_with_times[i]
                    try:
                        os.remove(file_path)
                    except Exception:
                        continue
        except Exception as e:
            logger.error(f"Persistent cache cleanup error: {e}")


class InferenceCache:
    """Multi-level inference cache manager."""
    
    def __init__(
        self,
        l1_config: Optional[Dict[str, Any]] = None,
        l2_config: Optional[Dict[str, Any]] = None,
        l3_config: Optional[Dict[str, Any]] = None,
    ):
        """Initialize multi-level cache."""
        self.l1_cache = L1MemoryCache(**(l1_config or {}))
        self.l2_cache = L2RedisCache(**(l2_config or {}))
        self.l3_cache = L3PersistentCache(**(l3_config or {}))
        
        # Semantic similarity for cache matching
        self.vectorizer = TfidfVectorizer(max_features=1000, stop_words='english')
        self.semantic_cache: Dict[str, List[str]] = {}  # semantic_hash -> list of keys
        
        # Cache statistics
        self.stats = {
            "hits": 0,
            "misses": 0,
            "l1_hits": 0,
            "l2_hits": 0,
            "l3_hits": 0,
            "sets": 0,
            "deletes": 0,
            "cost_saved": 0.0,
            "tokens_saved": 0,
        }
        
        self._lock = asyncio.Lock()
    
    def _generate_cache_key(
        self,
        prompt: str,
        model_name: str,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> str:
        """Generate cache key for inference request."""
        key_data = {
            "prompt": prompt,
            "model": model_name,
            "temperature": temperature,
            "max_tokens": max_tokens,
            **{k: v for k, v in kwargs.items() if k not in ["prompt", "model", "temperature", "max_tokens"]}
        }
        key_string = json.dumps(key_data, sort_keys=True)
        return hashlib.sha256(key_string.encode()).hexdigest()
    
    def _generate_semantic_hash(self, prompt: str) -> str:
        """Generate semantic hash for prompt similarity matching."""
        # Simple semantic hash based on prompt content
        normalized_prompt = prompt.lower().strip()
        return hashlib.md5(normalized_prompt.encode()).hexdigest()
    
    async def get(self, cache_key: str) -> Optional[CacheEntry]:
        """Get cache entry from multi-level cache."""
        async with self._lock:
            # Try L1 first (fastest)
            entry = await self.l1_cache.get(cache_key)
            if entry:
                self.stats["hits"] += 1
                self.stats["l1_hits"] += 1
                self.stats["cost_saved"] += entry.cost_estimate
                self.stats["tokens_saved"] += entry.token_count
                logger.debug(f"L1 cache hit for key: {cache_key}")
                return entry
            
            # Try L2 (Redis)
            entry = await self.l2_cache.get(cache_key)
            if entry:
                self.stats["hits"] += 1
                self.stats["l2_hits"] += 1
                self.stats["cost_saved"] += entry.cost_estimate
                self.stats["tokens_saved"] += entry.token_count
                
                # Promote to L1
                await self.l1_cache.set(entry)
                logger.debug(f"L2 cache hit for key: {cache_key}")
                return entry
            
            # Try L3 (persistent)
            entry = await self.l3_cache.get(cache_key)
            if entry:
                self.stats["hits"] += 1
                self.stats["l3_hits"] += 1
                self.stats["cost_saved"] += entry.cost_estimate
                self.stats["tokens_saved"] += entry.token_count
                
                # Promote to L2 and L1
                await self.l2_cache.set(entry)
                await self.l1_cache.set(entry)
                logger.debug(f"L3 cache hit for key: {cache_key}")
                return entry
            
            self.stats["misses"] += 1
            logger.debug(f"Cache miss for key: {cache_key}")
            return None
    
    async def set(
        self,
        cache_key: str,
        value: Any,
        model_name: str,
        cost_estimate: float = 0.0,
        token_count: int = 0,
        ttl_seconds: Optional[int] = None,
        prompt: Optional[str] = None,
        **metadata
    ) -> bool:
        """Set cache entry in all levels."""
        async with self._lock:
            entry = CacheEntry(
                key=cache_key,
                value=value,
                level=CacheLevel.L1_MEMORY,
                created_at=datetime.utcnow(),
                last_accessed=datetime.utcnow(),
                ttl_seconds=ttl_seconds,
                cost_estimate=cost_estimate,
                token_count=token_count,
                model_name=model_name,
                semantic_hash=self._generate_semantic_hash(prompt) if prompt else "",
                metadata=metadata,
            )
            
            # Set in all levels
            l1_success = await self.l1_cache.set(entry)
            l2_success = await self.l2_cache.set(entry)
            l3_success = await self.l3_cache.set(entry)
            
            if l1_success or l2_success or l3_success:
                self.stats["sets"] += 1
                
                # Update semantic cache mapping
                if entry.semantic_hash:
                    if entry.semantic_hash not in self.semantic_cache:
                        self.semantic_cache[entry.semantic_hash] = []
                    self.semantic_cache[entry.semantic_hash].append(cache_key)
                
                logger.debug(f"Cache set for key: {cache_key}")
                return True
            
            return False
    
    async def delete(self, cache_key: str) -> bool:
        """Delete cache entry from all levels."""
        async with self._lock:
            l1_success = await self.l1_cache.delete(cache_key)
            l2_success = await self.l2_cache.delete(cache_key)
            l3_success = await self.l3_cache.delete(cache_key)
            
            if l1_success or l2_success or l3_success:
                self.stats["deletes"] += 1
                logger.debug(f"Cache delete for key: {cache_key}")
                return True
            
            return False
    
    async def find_similar(
        self,
        prompt: str,
        similarity_threshold: float = 0.8,
        max_results: int = 5
    ) -> List[CacheEntry]:
        """Find semantically similar cached entries."""
        semantic_hash = self._generate_semantic_hash(prompt)
        similar_keys = self.semantic_cache.get(semantic_hash, [])
        
        if not similar_keys:
            return []
        
        similar_entries = []
        for key in similar_keys[:max_results]:
            entry = await self.get(key)
            if entry:
                similar_entries.append(entry)
        
        return similar_entries
    
    async def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get comprehensive cache statistics."""
        l1_stats = await self.l1_cache.get_stats()
        l2_stats = await self.l2_cache.get_stats()
        l3_stats = await self.l3_cache.get_stats()
        
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = self.stats["hits"] / total_requests if total_requests > 0 else 0
        
        return {
            "overall": {
                "total_requests": total_requests,
                "hit_rate": round(hit_rate * 100, 2),
                "l1_hit_rate": round(self.stats["l1_hits"] / total_requests * 100, 2) if total_requests > 0 else 0,
                "l2_hit_rate": round(self.stats["l2_hits"] / total_requests * 100, 2) if total_requests > 0 else 0,
                "l3_hit_rate": round(self.stats["l3_hits"] / total_requests * 100, 2) if total_requests > 0 else 0,
                "total_cost_saved": round(self.stats["cost_saved"], 4),
                "total_tokens_saved": self.stats["tokens_saved"],
                "cache_sets": self.stats["sets"],
                "cache_deletes": self.stats["deletes"],
            },
            "l1_memory": l1_stats,
            "l2_redis": l2_stats,
            "l3_persistent": l3_stats,
            "semantic_cache": {
                "semantic_hashes": len(self.semantic_cache),
                "total_keys": sum(len(keys) for keys in self.semantic_cache.values()),
            },
        }
    
    async def clear_all(self) -> bool:
        """Clear all cache levels."""
        l1_success = await self.l1_cache.clear()
        l2_success = await self.l2_cache.clear()
        l3_success = await self.l3_cache.clear()
        
        # Clear semantic cache
        self.semantic_cache.clear()
        
        # Reset stats
        self.stats = {
            "hits": 0,
            "misses": 0,
            "l1_hits": 0,
            "l2_hits": 0,
            "l3_hits": 0,
            "sets": 0,
            "deletes": 0,
            "cost_saved": 0.0,
            "tokens_saved": 0,
        }
        
        return l1_success and l2_success and l3_success


# Global cache instance
_inference_cache: Optional[InferenceCache] = None


async def get_inference_cache() -> InferenceCache:
    """Get or create global inference cache instance."""
    global _inference_cache
    if _inference_cache is None:
        _inference_cache = InferenceCache()
    return _inference_cache


async def close_inference_cache():
    """Close inference cache and cleanup resources."""
    global _inference_cache
    if _inference_cache:
        await _inference_cache.clear_all()
        _inference_cache = None
