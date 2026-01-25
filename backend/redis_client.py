"""
Redis Client Configuration and Connection Management
Provides proper Redis connection pooling and lifecycle management
"""

import os
import json
import asyncio
from typing import Any, Optional, Union
from contextlib import asynccontextmanager

import redis.asyncio as redis
from redis.asyncio import ConnectionPool, Redis
from redis.exceptions import RedisError, ConnectionError

from config_clean import get_settings

settings = get_settings()

class RedisManager:
    """Manages Redis connections with proper lifecycle management"""
    
    def __init__(self):
        self._pool: Optional[ConnectionPool] = None
        self._client: Optional[Redis] = None
        self._connected = False
    
    async def connect(self) -> None:
        """Initialize Redis connection pool"""
        try:
            self._pool = ConnectionPool.from_url(
                settings.redis_url,
                max_connections=20,
                retry_on_timeout=True,
                retry_on_error=[ConnectionError],
                socket_timeout=5,
                socket_connect_timeout=5,
                health_check_interval=30,
            )
            
            self._client = Redis(connection_pool=self._pool)
            
            # Test connection
            await self._client.ping()
            self._connected = True
            
        except Exception as e:
            print(f"Failed to connect to Redis: {e}")
            self._connected = False
    
    async def disconnect(self) -> None:
        """Close Redis connections"""
        if self._client:
            await self._client.close()
        if self._pool:
            await self._pool.disconnect()
        self._connected = False
    
    @property
    def client(self) -> Optional[Redis]:
        """Get Redis client"""
        return self._client if self._connected else None
    
    @property
    def is_connected(self) -> bool:
        """Check if Redis is connected"""
        return self._connected

# Global Redis manager instance
redis_manager = RedisManager()

async def get_redis() -> Optional[Redis]:
    """Dependency for getting Redis client"""
    if not redis_manager.is_connected:
        await redis_manager.connect()
    return redis_manager.client

@asynccontextmanager
async def get_redis_client() -> Redis:
    """Context manager for Redis client"""
    client = await get_redis()
    if not client:
        raise RedisError("Redis not available")
    try:
        yield client
    finally:
        pass

class RedisCache:
    """High-level cache operations with error handling"""
    
    def __init__(self, prefix: str = "raptorflow"):
        self.prefix = prefix
    
    def _make_key(self, key: str) -> str:
        return f"{self.prefix}:{key}"
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        client = await get_redis()
        if not client:
            return None
        
        try:
            value = await client.get(self._make_key(key))
            return json.loads(value) if value else None
        except (RedisError, json.JSONDecodeError):
            return None
    
    async def set(self, key: str, value: Any, ttl: int = 3600) -> bool:
        """Set value in cache with TTL"""
        client = await get_redis()
        if not client:
            return False
        
        try:
            serialized = json.dumps(value, default=str)
            await client.setex(self._make_key(key), ttl, serialized)
            return True
        except (RedisError, json.JSONEncodeError):
            return False
    
    async def delete(self, key: str) -> bool:
        """Delete value from cache"""
        client = await get_redis()
        if not client:
            return False
        
        try:
            await client.delete(self._make_key(key))
            return True
        except RedisError:
            return False
    
    async def clear(self) -> bool:
        """Clear all cache entries with prefix"""
        client = await get_redis()
        if not client:
            return False
        
        try:
            pattern = f"{self.prefix}:*"
            keys = await client.keys(pattern)
            if keys:
                await client.delete(*keys)
            return True
        except RedisError:
            return False

# Global cache instance
cache = RedisCache()
