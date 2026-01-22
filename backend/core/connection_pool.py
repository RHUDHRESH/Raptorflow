"""
Optimized database connection pooling for RaptorFlow
Manages Supabase client connections with pooling and health checks
"""

import asyncio
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional
from weakref import WeakSet

from .database_config import DB_CONFIG
from supabase import Client, create_client

logger = logging.getLogger(__name__)


class ConnectionPool:
    """Generic connection pool for database clients"""

    def __init__(
        self,
        min_connections: int = 2,
        max_connections: int = 20,
        connection_timeout: float = 30.0,
        idle_timeout: float = 300.0,
        max_lifetime: float = 3600.0,
        health_check_interval: float = 60.0,
    ):
        self.min_connections = min_connections
        self.max_connections = max_connections
        self.connection_timeout = connection_timeout
        self.idle_timeout = idle_timeout
        self.max_lifetime = max_lifetime
        self.health_check_interval = health_check_interval

        self._pool: List[Dict[str, Any]] = []
        self._active_connections: WeakSet = WeakSet()
        self._lock = asyncio.Lock()
        self._last_health_check = datetime.utcnow()

        # Pool statistics
        self.stats = {
            "created": 0,
            "destroyed": 0,
            "acquired": 0,
            "released": 0,
            "health_checks": 0,
            "failed_health_checks": 0,
        }

    async def initialize(self) -> None:
        """Initialize the connection pool with minimum connections"""
        async with self._lock:
            # Create minimum connections
            for _ in range(self.min_connections):
                await self._create_connection()

            # Start health check task
            asyncio.create_task(self._health_check_loop())

            logger.info(
                f"Connection pool initialized with {self.min_connections} connections"
            )

    async def acquire(self) -> Any:
        """Acquire a connection from the pool"""
        async with self._lock:
            # Clean up expired connections
            await self._cleanup_expired_connections()

            # Find available connection
            for conn_info in self._pool:
                if not conn_info["in_use"] and self._is_connection_healthy(conn_info):
                    conn_info["in_use"] = True
                    conn_info["last_acquired"] = datetime.utcnow()
                    self._active_connections.add(conn_info["connection"])
                    self.stats["acquired"] += 1
                    return conn_info["connection"]

            # No available connection, create new one if under max
            if len(self._pool) < self.max_connections:
                conn = await self._create_connection()
                conn_info = next(c for c in self._pool if c["connection"] == conn)
                conn_info["in_use"] = True
                conn_info["last_acquired"] = datetime.utcnow()
                self._active_connections.add(conn)
                self.stats["acquired"] += 1
                return conn

            # Pool is full, wait for available connection
            raise Exception("Connection pool exhausted")

    async def release(self, connection: Any) -> None:
        """Release a connection back to the pool"""
        async with self._lock:
            for conn_info in self._pool:
                if conn_info["connection"] == connection:
                    conn_info["in_use"] = False
                    conn_info["last_released"] = datetime.utcnow()
                    self._active_connections.discard(connection)
                    self.stats["released"] += 1
                    return

            # Connection not found in pool, close it
            await self._close_connection(connection)

    async def _create_connection(self) -> Any:
        """Create a new database connection"""
        try:
            # This would be implemented by specific pool classes
            connection = await self._create_connection_impl()

            conn_info = {
                "connection": connection,
                "created_at": datetime.utcnow(),
                "last_acquired": None,
                "last_released": None,
                "in_use": False,
                "health_status": "healthy",
            }

            self._pool.append(conn_info)
            self.stats["created"] += 1

            return connection

        except Exception as e:
            logger.error(f"Failed to create connection: {e}")
            raise

    async def _create_connection_impl(self) -> Any:
        """Override in subclasses to create specific connection type"""
        raise NotImplementedError

    async def _close_connection(self, connection: Any) -> None:
        """Close a database connection"""
        try:
            # This would be implemented by specific pool classes
            await self._close_connection_impl(connection)

            # Remove from pool
            self._pool = [c for c in self._pool if c["connection"] != connection]
            self.stats["destroyed"] += 1

        except Exception as e:
            logger.error(f"Failed to close connection: {e}")

    async def _close_connection_impl(self, connection: Any) -> None:
        """Override in subclasses to close specific connection type"""
        raise NotImplementedError

    def _is_connection_healthy(self, conn_info: Dict[str, Any]) -> bool:
        """Check if connection is healthy"""
        return conn_info["health_status"] == "healthy"

    async def _cleanup_expired_connections(self) -> None:
        """Remove expired connections from pool"""
        now = datetime.utcnow()
        to_remove = []

        for conn_info in self._pool:
            if conn_info["in_use"]:
                continue

            # Check idle timeout
            if conn_info["last_released"]:
                idle_time = (now - conn_info["last_released"]).total_seconds()
                if idle_time > self.idle_timeout:
                    to_remove.append(conn_info)
                    continue

            # Check max lifetime
            lifetime = (now - conn_info["created_at"]).total_seconds()
            if lifetime > self.max_lifetime:
                to_remove.append(conn_info)

        # Remove expired connections
        for conn_info in to_remove:
            await self._close_connection(conn_info["connection"])

        # Ensure minimum connections
        current_count = len(self._pool)
        if current_count < self.min_connections:
            for _ in range(self.min_connections - current_count):
                await self._create_connection()

    async def _health_check_loop(self) -> None:
        """Periodic health check for all connections"""
        while True:
            try:
                await asyncio.sleep(self.health_check_interval)
                await self._perform_health_checks()
            except Exception as e:
                logger.error(f"Health check error: {e}")

    async def _perform_health_checks(self) -> None:
        """Perform health checks on all connections"""
        now = datetime.utcnow()

        for conn_info in self._pool:
            if conn_info["in_use"]:
                continue

            try:
                # Perform health check
                is_healthy = await self._check_connection_health(
                    conn_info["connection"]
                )
                conn_info["health_status"] = "healthy" if is_healthy else "unhealthy"

                if not is_healthy:
                    logger.warning(
                        f"Connection failed health check, removing from pool"
                    )
                    await self._close_connection(conn_info["connection"])

                self.stats["health_checks"] += 1

            except Exception as e:
                conn_info["health_status"] = "unhealthy"
                self.stats["failed_health_checks"] += 1
                logger.error("Health check failed")

    async def _check_connection_health(self, connection: Any) -> bool:
        """Override in subclasses to check connection health"""
        raise NotImplementedError

    def get_stats(self) -> Dict[str, Any]:
        """Get pool statistics"""
        return {
            **self.stats,
            "pool_size": len(self._pool),
            "active_connections": len(self._active_connections),
            "available_connections": len([c for c in self._pool if not c["in_use"]]),
            "min_connections": self.min_connections,
            "max_connections": self.max_connections,
        }

    async def close(self) -> None:
        """Close all connections in the pool"""
        async with self._lock:
            for conn_info in self._pool:
                await self._close_connection(conn_info["connection"])

            self._pool.clear()
            logger.info("Connection pool closed")


class SupabaseConnectionPool(ConnectionPool):
    """Connection pool specifically for Supabase clients"""

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.url = os.getenv("SUPABASE_URL")
        self.key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    async def _create_connection_impl(self) -> Client:
        """Create a new Supabase client"""
        return create_client(self.url, self.key)

    async def _close_connection_impl(self, connection: Client) -> None:
        """Close Supabase client (cleanup)"""
        # Supabase client doesn't have explicit close method
        # Just remove references
        pass

    async def _check_connection_health(self, connection: Client) -> bool:
        """Check Supabase connection health"""
        try:
            # Simple health check - try to query users table
            result = connection.table("users").select("id").limit(1).execute()
            return True
        except Exception as e:
            logger.error(f"Connection health check failed: {e}")
            return False


class DatabaseConnectionManager:
    """Manages multiple connection pools for different database types"""

    def __init__(self):
        self.pools: Dict[str, ConnectionPool] = {}
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize all connection pools"""
        if self._initialized:
            return

        # Initialize Supabase pool with production configuration
        pool_settings = DB_CONFIG.get_pool_settings()
        supabase_pool = SupabaseConnectionPool(
            min_connections=pool_settings["min_connections"],
            max_connections=pool_settings["max_connections"],
            connection_timeout=pool_settings["connection_timeout"],
            idle_timeout=pool_settings["idle_timeout"],
            max_lifetime=pool_settings["max_lifetime"],
            health_check_interval=pool_settings["health_check_interval"],
        )

        await supabase_pool.initialize()
        self.pools["supabase"] = supabase_pool

        self._initialized = True
        logger.info("Database connection manager initialized")

    async def get_connection(self, pool_name: str = "supabase") -> Any:
        """Get a connection from the specified pool"""
        if not self._initialized:
            await self.initialize()

        if pool_name not in self.pools:
            raise ValueError(f"Unknown connection pool: {pool_name}")

        return await self.pools[pool_name].acquire()

    async def release_connection(
        self, connection: Any, pool_name: str = "supabase"
    ) -> None:
        """Release a connection back to the specified pool"""
        if pool_name in self.pools:
            await self.pools[pool_name].release(connection)

    async def get_stats(self) -> Dict[str, Any]:
        """Get statistics for all connection pools"""
        stats = {}
        for name, pool in self.pools.items():
            stats[name] = pool.get_stats()
        return stats

    async def close(self) -> None:
        """Close all connection pools"""
        for pool in self.pools.values():
            await pool.close()

        self.pools.clear()
        self._initialized = False
        logger.info("Database connection manager closed")


# Global connection manager
_db_manager: Optional[DatabaseConnectionManager] = None


def get_db_manager() -> DatabaseConnectionManager:
    """Get global database connection manager"""
    global _db_manager
    if _db_manager is None:
        _db_manager = DatabaseConnectionManager()
    return _db_manager


async def get_db_connection(pool_name: str = "supabase") -> Any:
    """Get a database connection from the pool"""
    manager = get_db_manager()
    return await manager.get_connection(pool_name)


async def release_db_connection(connection: Any, pool_name: str = "supabase") -> None:
    """Release a database connection back to the pool"""
    manager = get_db_manager()
    await manager.release_connection(connection, pool_name)


# Context manager for database connections
class DatabaseConnection:
    """Context manager for database connections"""

    def __init__(self, pool_name: str = "supabase"):
        self.pool_name = pool_name
        self.connection = None

    async def __aenter__(self) -> Any:
        self.connection = await get_db_connection(self.pool_name)
        return self.connection

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        if self.connection:
            await release_db_connection(self.connection, self.pool_name)


# Decorator for automatic connection management
def with_db_connection(pool_name: str = "supabase"):
    """Decorator to automatically manage database connections"""

    def decorator(func):
        async def wrapper(*args, **kwargs):
            async with DatabaseConnection(pool_name) as connection:
                # Add connection to kwargs
                kwargs["db_connection"] = connection
                return await func(*args, **kwargs)

        return wrapper

    return decorator


# FastAPI dependency for database connections
async def get_db_connection_dependency() -> Any:
    """FastAPI dependency for database connections"""
    return await get_db_connection()


# Health check for connection pools
async def get_connection_pool_health() -> Dict[str, Any]:
    """Get health status of all connection pools"""
    manager = get_db_manager()
    stats = await manager.get_stats()

    health_status = {
        "status": "healthy",
        "pools": {},
        "total_connections": 0,
        "active_connections": 0,
    }

    for pool_name, pool_stats in stats.items():
        health_status["pools"][pool_name] = {
            "status": (
                "healthy" if pool_stats["available_connections"] > 0 else "unhealthy"
            ),
            "total": pool_stats["pool_size"],
            "active": pool_stats["active_connections"],
            "available": pool_stats["available_connections"],
            "utilization": (
                pool_stats["active_connections"] / pool_stats["pool_size"]
                if pool_stats["pool_size"] > 0
                else 0
            ),
        }

        health_status["total_connections"] += pool_stats["pool_size"]
        health_status["active_connections"] += pool_stats["active_connections"]

    # Overall health status
    if health_status["active_connections"] == health_status["total_connections"]:
        health_status["status"] = "degraded"
    elif any(pool["status"] == "unhealthy" for pool in health_status["pools"].values()):
        health_status["status"] = "unhealthy"

    return health_status
