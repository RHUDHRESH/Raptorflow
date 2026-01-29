"""
Redis production configuration and optimization for RaptorFlow
Production-ready Redis setup with clustering, persistence, and monitoring
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, Optional

from .core.redis import get_redis_client

logger = logging.getLogger(__name__)


class RedisProductionConfig:
    """Production Redis configuration"""

    def __init__(self):
        # Connection settings
        self.host = os.getenv("REDIS_HOST", "redis")
        self.port = int(os.getenv("REDIS_PORT", "6379"))
        self.db = int(os.getenv("REDIS_DB", "0"))
        self.password = os.getenv("REDIS_PASSWORD")

        # Upstash Redis settings
        self.upstash_url = os.getenv("UPSTASH_REDIS_URL")
        self.upstash_token = os.getenv("UPSTASH_REDIS_TOKEN")

        # Connection pool settings
        self.max_connections = int(os.getenv("REDIS_MAX_CONNECTIONS", "50"))
        self.retry_on_timeout = (
            os.getenv("REDIS_RETRY_ON_TIMEOUT", "true").lower() == "true"
        )
        self.socket_connect_timeout = int(
            os.getenv("REDIS_SOCKET_CONNECT_TIMEOUT", "5")
        )
        self.socket_timeout = int(os.getenv("REDIS_SOCKET_TIMEOUT", "5"))
        self.health_check_interval = int(os.getenv("REDIS_HEALTH_CHECK_INTERVAL", "30"))

        # Performance settings
        self.connection_pool_max_idle = int(os.getenv("REDIS_POOL_MAX_IDLE", "10"))
        self.connection_pool_timeout = int(os.getenv("REDIS_POOL_TIMEOUT", "10"))

        # Persistence settings
        self.save_interval = int(os.getenv("REDIS_SAVE_INTERVAL", "300"))  # 5 minutes
        self.backup_enabled = (
            os.getenv("REDIS_BACKUP_ENABLED", "true").lower() == "true"
        )

        # Memory settings
        self.max_memory = os.getenv("REDIS_MAX_MEMORY", "2gb")
        self.eviction_policy = os.getenv("REDIS_EVICTION_POLICY", "allkeys-lru")

        # Security settings
        self.require_auth = os.getenv("REDIS_REQUIRE_AUTH", "true").lower() == "true"
        self.ssl_enabled = os.getenv("REDIS_SSL_ENABLED", "false").lower() == "true"

        # Monitoring settings
        self.metrics_enabled = (
            os.getenv("REDIS_METRICS_ENABLED", "true").lower() == "true"
        )
        self.slow_log_enabled = (
            os.getenv("REDIS_SLOW_LOG_ENABLED", "true").lower() == "true"
        )
        self.slow_log_threshold = int(
            os.getenv("REDIS_SLOW_LOG_THRESHOLD", "10000")
        )  # 10ms


class RedisProductionManager:
    """Production Redis management with monitoring and optimization"""

    def __init__(self):
        self.config = RedisProductionConfig()
        self.client = None
        self.metrics = {
            "connections": 0,
            "commands": 0,
            "errors": 0,
            "slow_queries": 0,
            "memory_usage": 0,
            "last_health_check": None,
            "uptime": 0,
        }
        self._start_time = datetime.utcnow()

    async def initialize(self) -> bool:
        """Initialize Redis production client"""
        try:
            if self.config.upstash_url and self.config.upstash_token:
                # Use Upstash Redis
                redis_wrapper = await get_redis_client()
                self.client = redis_wrapper.get_client()
                logger.info("Initialized Upstash Redis client")
            else:
                # Use standard Redis
                import redis.asyncio as redis

                connection_kwargs = {
                    "host": self.config.host,
                    "port": self.config.port,
                    "db": self.config.db,
                    "encoding": "utf-8",
                    "decode_responses": True,
                    "retry_on_timeout": self.config.retry_on_timeout,
                    "socket_connect_timeout": self.config.socket_connect_timeout,
                    "socket_timeout": self.config.socket_timeout,
                    "health_check_interval": self.config.health_check_interval,
                    "max_connections": self.config.max_connections,
                }

                if self.config.password:
                    connection_kwargs["password"] = self.config.password

                self.client = redis.Redis(**connection_kwargs)
                logger.info("Initialized standard Redis client")

            # Test connection
            # Check if client is async or sync
            import inspect

            is_async = inspect.iscoroutinefunction(self.client.ping)

            if is_async:
                # For async clients
                await self.client.ping()
                # Start monitoring tasks
                asyncio.create_task(self._monitoring_loop())
                asyncio.create_task(self._health_check_loop())
            else:
                # For sync clients (Upstash)
                self.client.ping()

            logger.info("Redis production manager initialized successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")
            return False

    async def test_connection(self) -> Dict[str, Any]:
        """Test Redis connection and performance"""
        try:
            if not self.client:
                return {"status": "error", "message": "Redis client not initialized"}

            # Basic connectivity test
            start_time = datetime.utcnow()
            if hasattr(self.client, "ping"):
                # Async client
                await self.client.ping()
            else:
                # Sync client (Upstash)
                self.client.ping()
            ping_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            # Performance test
            start_time = datetime.utcnow()
            test_key = "health_check_test"
            if hasattr(self.client, "set"):
                # Async client
                await self.client.set(test_key, "test_value", ex=10)
                value = await self.client.get(test_key)
                await self.client.delete(test_key)
            else:
                # Sync client (Upstash)
                self.client.set(test_key, "test_value", ex=10)
                value = self.client.get(test_key)
                self.client.delete(test_key)
            operation_time = (datetime.utcnow() - start_time).total_seconds() * 1000

            # Memory info (only available with standard Redis)
            memory_usage = "unknown"
            if hasattr(self.client, "info"):
                info = await self.client.info()
                memory_usage = info.get("used_memory_human", "unknown")

            return {
                "status": "healthy",
                "ping_time_ms": ping_time,
                "operation_time_ms": operation_time,
                "memory_usage": memory_usage,
                "test_passed": value == "test_value",
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def optimize_redis(self) -> Dict[str, Any]:
        """Apply Redis optimizations for production"""
        try:
            optimizations = []

            # Set memory policy
            if self.config.max_memory:
                await self.client.config_set("maxmemory", self.config.max_memory)
                await self.client.config_set(
                    "maxmemory-policy", self.config.eviction_policy
                )
                optimizations.append(f"maxmemory={self.config.max_memory}")
                optimizations.append(f"policy={self.config.eviction_policy}")

            # Enable slow log
            if self.config.slow_log_enabled:
                await self.client.config_set(
                    "slowlog-log-slower-than", self.config.slow_log_threshold
                )
                await self.client.config_set("slowlog-max-len", "128")
                optimizations.append("slowlog enabled")

            # Set save policy
            if self.config.save_interval > 0:
                await self.client.config_set("save", f"{self.config.save_interval} 1")
                optimizations.append(f"save interval={self.config.save_interval}s")

            # Enable AOF if backup is enabled
            if self.config.backup_enabled:
                await self.client.config_set("appendonly", "yes")
                await self.client.config_set("appendfsync", "everysec")
                optimizations.append("AOF enabled")

            return {"status": "success", "optimizations": optimizations}

        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def backup_redis(self) -> Dict[str, Any]:
        """Create Redis backup"""
        try:
            if not self.config.backup_enabled:
                return {"status": "skipped", "message": "Backup not enabled"}

            # Trigger background save
            await self.client.bgsave()

            # Get last save time
            info = await self.client.info()
            last_save = info.get("rdb_last_save_time", 0)

            return {
                "status": "success",
                "last_save_time": last_save,
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def get_redis_stats(self) -> Dict[str, Any]:
        """Get comprehensive Redis statistics"""
        try:
            if not self.client:
                return {"status": "error", "message": "Redis client not initialized"}

            info = await self.client.info()

            # Extract key metrics
            stats = {
                "status": "healthy",
                "uptime_seconds": info.get("uptime_in_seconds", 0),
                "connected_clients": info.get("connected_clients", 0),
                "used_memory": info.get("used_memory", 0),
                "used_memory_human": info.get("used_memory_human", "0B"),
                "max_memory": info.get("maxmemory", 0),
                "max_memory_human": info.get("maxmemory_human", "0B"),
                "total_commands_processed": info.get("total_commands_processed", 0),
                "total_connections_received": info.get("total_connections_received", 0),
                "keyspace_hits": info.get("keyspace_hits", 0),
                "keyspace_misses": info.get("keyspace_misses", 0),
                "hit_rate": 0,
                "last_save_time": info.get("rdb_last_save_time", 0),
                "last_save_time_human": (
                    datetime.fromtimestamp(
                        info.get("rdb_last_save_time", 0)
                    ).isoformat()
                    if info.get("rdb_last_save_time")
                    else None
                ),
            }

            # Calculate hit rate
            hits = stats["keyspace_hits"]
            misses = stats["keyspace_misses"]
            if hits + misses > 0:
                stats["hit_rate"] = (hits / (hits + misses)) * 100

            # Add custom metrics
            stats.update(self.metrics)
            stats["manager_uptime"] = (
                datetime.utcnow() - self._start_time
            ).total_seconds()

            return stats

        except Exception as e:
            return {"status": "error", "message": str(e)}

    async def cleanup_expired_keys(self) -> int:
        """Clean up expired keys"""
        try:
            # This is a simplified cleanup - in production you might want to scan specific patterns
            # For now, Redis handles TTL automatically

            # Get slow log to identify slow operations
            slowlog = await self.client.slowlog_get(10)
            slow_operations = len(
                [
                    entry
                    for entry in slowlog
                    if entry[0] > self.config.slow_log_threshold
                ]
            )

            if slow_operations > 0:
                logger.warning(f"Found {slow_operations} slow operations in Redis")
                self.metrics["slow_queries"] += slow_operations

            return 0  # Redis handles TTL automatically

        except Exception as e:
            logger.error(f"Redis cleanup error: {e}")
            return 0

    async def _monitoring_loop(self) -> None:
        """Background monitoring loop"""
        while True:
            try:
                await asyncio.sleep(60)  # Check every minute

                # Update metrics
                if self.client:
                    # Only update basic metrics for Upstash (no info command)
                    if hasattr(self.client, "info"):
                        # Standard Redis
                        info = await self.client.info()
                        self.metrics["connected_clients"] = info.get(
                            "connected_clients", 0
                        )
                        self.metrics["memory_usage"] = info.get("used_memory", 0)
                        self.metrics["uptime"] = info.get("uptime_in_seconds", 0)
                    else:
                        # Upstash Redis - basic metrics only
                        self.metrics["connections"] += 1

            except Exception as e:
                logger.error(f"Redis monitoring error: {e}")
                self.metrics["errors"] += 1

    async def _health_check_loop(self) -> None:
        """Background health check loop"""
        while True:
            try:
                await asyncio.sleep(self.config.health_check_interval)

                if self.client:
                    # Ping Redis
                    if hasattr(self.client, "ping"):
                        # Async client
                        await self.client.ping()
                    else:
                        # Sync client (Upstash)
                        self.client.ping()
                    self.metrics["last_health_check"] = datetime.utcnow().isoformat()

            except Exception as e:
                logger.error(f"Redis health check failed: {e}")
                self.metrics["errors"] += 1

    async def close(self) -> None:
        """Close Redis connection"""
        if self.client:
            if hasattr(self.client, "close"):
                # Async client
                await self.client.close()
            else:
                # Sync client (Upstash) - no explicit close needed
                pass
            logger.info("Redis connection closed")


# Global Redis production manager
_redis_manager: Optional[RedisProductionManager] = None


def get_redis_production_manager() -> RedisProductionManager:
    """Get global Redis production manager"""
    global _redis_manager
    if _redis_manager is None:
        _redis_manager = RedisProductionManager()
    return _redis_manager


async def initialize_redis_production() -> bool:
    """Initialize Redis production manager"""
    manager = get_redis_production_manager()
    return await manager.initialize()


async def get_redis_health_status() -> Dict[str, Any]:
    """Get Redis health status"""
    manager = get_redis_production_manager()
    return await manager.test_connection()


async def get_redis_metrics() -> Dict[str, Any]:
    """Get Redis metrics"""
    manager = get_redis_production_manager()
    return await manager.get_redis_stats()


# Redis utility functions for production
def redis_cache_with_ttl(key: str, value: Any, ttl: int = 3600) -> bool:
    """Cache value with TTL in Redis"""
    try:
        manager = get_redis_production_manager()
        if manager.client:
            import json

            serialized_value = (
                json.dumps(value) if not isinstance(value, str) else value
            )
            manager.client.setex(key, ttl, serialized_value)
            return True
    except Exception as e:
        logger.error(f"Redis cache error: {e}")
    return False


def redis_get_cached(key: str) -> Optional[Any]:
    """Get cached value from Redis"""
    try:
        manager = get_redis_production_manager()
        if manager.client:
            value = manager.client.get(key)
            if value:
                try:
                    return json.loads(value)
                except json.JSONDecodeError:
                    return value
    except Exception as e:
        logger.error(f"Redis get error: {e}")
    return None


def redis_increment_counter(
    key: str, amount: int = 1, ttl: Optional[int] = None
) -> int:
    """Increment counter in Redis"""
    try:
        manager = get_redis_production_manager()
        if manager.client:
            result = manager.client.incrby(key, amount)
            if ttl:
                manager.client.expire(key, ttl)
            return result
    except Exception as e:
        logger.error(f"Redis increment error: {e}")
    return 0
