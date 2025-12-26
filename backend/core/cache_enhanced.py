import asyncio
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime, timedelta

logger = logging.getLogger("raptorflow.cache.enhanced")


class EnhancedCacheManager:
    """
    Enhanced caching with advanced features built on existing cache infrastructure.
    """
    
    def __init__(self):
        from core.cache import get_cache_client
        self.client = get_cache_client()
        self.stats = {
            "hits": 0,
            "misses": 0,
            "sets": 0,
            "evictions": 0
        }
    
    async def get_with_stats(self, key: str) -> Optional[Dict[str, Any]]:
        """Get value with statistics tracking."""
        try:
            from core.cache import CacheManager
            cache_manager = CacheManager(self.client)
            result = cache_manager.get_json(key)
            
            if result:
                self.stats["hits"] += 1
                return result
            else:
                self.stats["misses"] += 1
                return None
        except Exception as e:
            logger.error(f"Cache get error for key {key}: {e}")
            self.stats["misses"] += 1
            return None
    
    async def set_with_stats(self, key: str, value: Any, expiry_seconds: int = 3600) -> bool:
        """Set value with statistics tracking."""
        try:
            from core.cache import CacheManager
            cache_manager = CacheManager(self.client)
            result = cache_manager.set_json(key, value, expiry_seconds)
            
            if result:
                self.stats["sets"] += 1
                return True
            return False
        except Exception as e:
            logger.error(f"Cache set error for key {key}: {e}")
            return False
    
    async def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate keys matching a pattern."""
        try:
            # Get all keys matching pattern
            keys = self.client.keys(pattern)
            if keys:
                deleted = self.client.delete(*keys)
                self.stats["evictions"] += deleted
                return deleted
            return 0
        except Exception as e:
            logger.error(f"Error invalidating pattern {pattern}: {e}")
            return 0
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get cache statistics."""
        total_requests = self.stats["hits"] + self.stats["misses"]
        hit_rate = (self.stats["hits"] / total_requests * 100) if total_requests > 0 else 0
        
        return {
            **self.stats,
            "hit_rate_percent": round(hit_rate, 2),
            "total_requests": total_requests
        }


# Global enhanced cache manager
_enhanced_cache_manager: Optional[EnhancedCacheManager] = None


def get_enhanced_cache_manager() -> EnhancedCacheManager:
    """Get the global enhanced cache manager instance."""
    global _enhanced_cache_manager
    if _enhanced_cache_manager is None:
        _enhanced_cache_manager = EnhancedCacheManager()
    return _enhanced_cache_manager


def cache_response(ttl: int = 300, key_prefix: str = None):
    """Decorator for caching function responses."""
    def decorator(func):
        async def wrapper(*args, **kwargs):
            cache_manager = get_enhanced_cache_manager()
            
            # Generate cache key
            func_name = func.__name__
            prefix = key_prefix or f"func:{func_name}"
            
            # Create simple params hash
            params_str = f"{args}_{kwargs}"
            import hashlib
            params_hash = hashlib.md5(params_str.encode()).hexdigest()[:8]
            cache_key = f"{prefix}:params:{params_hash}"
            
            # Try to get from cache
            cached_result = await cache_manager.get_with_stats(cache_key)
            if cached_result is not None:
                return cached_result
            
            # Execute function and cache result
            result = await func(*args, **kwargs)
            
            await cache_manager.set_with_stats(cache_key, result, ttl)
            
            return result
        
        return wrapper
    return decorator
