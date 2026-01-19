"""
Connection pooling for database and Redis connections.
Provides efficient connection management with proper resource cleanup.
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

try:
    import asyncpg
    ASYNCPG_AVAILABLE = True
except ImportError:
    ASYNCPG_AVAILABLE = False

try:
    import redis.asyncio as redis
    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False

try:
    import aioredis
    AIOREDIS_AVAILABLE = True
except ImportError:
    AIOREDIS_AVAILABLE = False

logger = logging.getLogger(__name__)


class DatabasePool:
    """PostgreSQL connection pool manager."""
    
    def __init__(self):
        self._pool: Optional[asyncpg.Pool] = None
        self._initialized = False
    
    async def initialize(self) -> bool:
        """Initialize the database connection pool."""
        if self._initialized:
            return True
        
        if not ASYNCPG_AVAILABLE:
            logger.warning("asyncpg not available, database pooling disabled")
            return False
        
        try:
            database_url = os.getenv("DATABASE_URL")
            if not database_url:
                logger.warning("DATABASE_URL not set, using SQLite fallback")
                return False
            
            # Parse connection parameters
            min_size = int(os.getenv("DB_POOL_MIN_SIZE", "5"))
            max_size = int(os.getenv("DB_POOL_MAX_SIZE", "20"))
            
            self._pool = await asyncpg.create_pool(
                database_url,
                min_size=min_size,
                max_size=max_size,
                command_timeout=60,
                server_settings={
                    "application_name": "raptorflow_backend",
                    "timezone": "UTC",
                }
            )
            
            self._initialized = True
            logger.info(f"Database pool initialized: min={min_size}, max={max_size}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize database pool: {e}")
            return False
    
    async def close(self):
        """Close the database connection pool."""
        if self._pool:
            await self._pool.close()
            self._pool = None
            self._initialized = False
            logger.info("Database pool closed")
    
    @asynccontextmanager
    async def get_connection(self) -> AsyncGenerator[asyncpg.Connection, None]:
        """Get a database connection from the pool."""
        if not self._initialized or not self._pool:
            raise RuntimeError("Database pool not initialized")
        
        async with self._pool.acquire() as connection:
            yield connection
    
    async def execute(self, query: str, *args) -> str:
        """Execute a query and return the result."""
        async with self.get_connection() as conn:
            return await conn.execute(query, *args)
    
    async def fetch(self, query: str, *args) -> list:
        """Execute a query and fetch all results."""
        async with self.get_connection() as conn:
            return await conn.fetch(query, *args)
    
    async def fetchrow(self, query: str, *args) -> Optional[dict]:
        """Execute a query and fetch a single row."""
        async with self.get_connection() as conn:
            return await conn.fetchrow(query, *args)
    
    def get_pool_stats(self) -> dict:
        """Get pool statistics."""
        if not self._pool:
            return {"initialized": False}
        
        return {
            "initialized": self._initialized,
            "size": self._pool.get_size(),
            "min_size": self._pool.get_min_size(),
            "max_size": self._pool.get_max_size(),
            "idle_connections": self._pool.get_idle_size(),
        }


class RedisPool:
    """Redis connection pool manager."""
    
    def __init__(self):
        self._pool: Optional[redis.ConnectionPool] = None
        self._redis_client: Optional[redis.Redis] = None
        self._initialized = False
    
    async def initialize(self) -> bool:
        """Initialize the Redis connection pool."""
        if self._initialized:
            return True
        
        if not REDIS_AVAILABLE:
            logger.warning("redis not available, Redis pooling disabled")
            return False
        
        try:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
            max_connections = int(os.getenv("REDIS_MAX_CONNECTIONS", "20"))
            
            # Create connection pool
            self._pool = redis.ConnectionPool.from_url(
                redis_url,
                max_connections=max_connections,
                retry_on_timeout=True,
                socket_timeout=5,
                socket_connect_timeout=5,
                health_check_interval=30,
            )
            
            # Create Redis client with pool
            self._redis_client = redis.Redis(connection_pool=self._pool)
            
            # Test connection
            await self._redis_client.ping()
            
            self._initialized = True
            logger.info(f"Redis pool initialized: max_connections={max_connections}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to initialize Redis pool: {e}")
            return False
    
    async def close(self):
        """Close the Redis connection pool."""
        if self._redis_client:
            await self._redis_client.close()
        if self._pool:
            await self._pool.disconnect()
        
        self._redis_client = None
        self._pool = None
        self._initialized = False
        logger.info("Redis pool closed")
    
    async def get_client(self) -> redis.Redis:
        """Get a Redis client from the pool."""
        if not self._initialized or not self._redis_client:
            raise RuntimeError("Redis pool not initialized")
        
        return self._redis_client
    
    async def execute_command(self, command: str, *args):
        """Execute a Redis command."""
        client = await self.get_client()
        return await client.execute_command(command, *args)
    
    async def set(self, key: str, value: str, ex: Optional[int] = None) -> bool:
        """Set a key-value pair."""
        client = await self.get_client()
        return await client.set(key, value, ex=ex)
    
    async def get(self, key: str) -> Optional[str]:
        """Get a value by key."""
        client = await self.get_client()
        return await client.get(key)
    
    async def delete(self, key: str) -> int:
        """Delete a key."""
        client = await self.get_client()
        return await client.delete(key)
    
    async def exists(self, key: str) -> bool:
        """Check if a key exists."""
        client = await self.get_client()
        return await client.exists(key)
    
    def get_pool_stats(self) -> dict:
        """Get pool statistics."""
        if not self._pool:
            return {"initialized": False}
        
        return {
            "initialized": self._initialized,
            "max_connections": self._pool.max_connections,
            "created_connections": len(self._pool._created_connections),
            "available_connections": len(self._pool._available_connections),
            "in_use_connections": len(self._pool._in_use_connections),
        }


class ConnectionManager:
    """Manages all connection pools."""
    
    def __init__(self):
        self.db_pool = DatabasePool()
        self.redis_pool = RedisPool()
        self._initialized = False
    
    async def initialize(self) -> bool:
        """Initialize all connection pools."""
        if self._initialized:
            return True
        
        logger.info("Initializing connection pools...")
        
        # Initialize database pool
        db_success = await self.db_pool.initialize()
        
        # Initialize Redis pool
        redis_success = await self.redis_pool.initialize()
        
        self._initialized = db_success or redis_success
        
        if self._initialized:
            logger.info("Connection pools initialized successfully")
        else:
            logger.error("Failed to initialize any connection pools")
        
        return self._initialized
    
    async def close(self):
        """Close all connection pools."""
        await self.db_pool.close()
        await self.redis_pool.close()
        self._initialized = False
        logger.info("All connection pools closed")
    
    def get_stats(self) -> dict:
        """Get statistics for all pools."""
        return {
            "database": self.db_pool.get_pool_stats(),
            "redis": self.redis_pool.get_pool_stats(),
            "initialized": self._initialized,
        }


# Global connection manager instance
_connection_manager: Optional[ConnectionManager] = None


async def get_connection_manager() -> ConnectionManager:
    """Get the global connection manager instance."""
    global _connection_manager
    if _connection_manager is None:
        _connection_manager = ConnectionManager()
        await _connection_manager.initialize()
    return _connection_manager


async def close_connection_manager():
    """Close the global connection manager."""
    global _connection_manager
    if _connection_manager:
        await _connection_manager.close()
        _connection_manager = None


# Convenience functions
async def get_db_pool() -> DatabasePool:
    """Get the database pool."""
    manager = await get_connection_manager()
    return manager.db_pool


async def get_redis_pool() -> RedisPool:
    """Get the Redis pool."""
    manager = await get_connection_manager()
    return manager.redis_pool


# Health check functions
async def check_database_health() -> dict:
    """Check database connection health."""
    try:
        # Try new database system first
        from .database_integration import get_database_integration
        integration = get_database_integration()
        
        if integration._initialized:
            status = await integration.get_system_status()
            return {
                "status": status.get("overall_health", "healthy"),
                "details": status
            }
        
        # Fallback to legacy pool
        pool = await get_db_pool()
        if not pool._initialized:
            return {"status": "unhealthy", "reason": "Pool not initialized"}
        
        # Test connection with simple query
        async with pool.get_connection() as conn:
            await conn.execute("SELECT 1")
        
        stats = pool.get_pool_stats()
        return {
            "status": "healthy",
            "pool_stats": stats,
        }
    except Exception as e:
        return {"status": "unhealthy", "reason": str(e)}


async def check_redis_health() -> dict:
    """Check Redis connection health."""
    try:
        pool = await get_redis_pool()
        if not pool._initialized:
            return {"status": "unhealthy", "reason": "Pool not initialized"}
        
        # Test connection
        client = await pool.get_client()
        await client.ping()
        
        stats = pool.get_pool_stats()
        return {
            "status": "healthy",
            "pool_stats": stats,
        }
    except Exception as e:
        return {"status": "unhealthy", "reason": str(e)}


async def check_all_connections() -> dict:
    """Check health of all connection pools."""
    db_health = await check_database_health()
    redis_health = await check_redis_health()
    
    overall_status = "healthy"
    if db_health["status"] != "healthy" and redis_health["status"] != "healthy":
        overall_status = "unhealthy"
    elif db_health["status"] != "healthy" or redis_health["status"] != "healthy":
        overall_status = "degraded"
    
    return {
        "overall_status": overall_status,
        "database": db_health,
        "redis": redis_health,
    }
