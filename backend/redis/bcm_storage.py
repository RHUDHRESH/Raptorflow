"""
BCM Redis Storage Module

Provides tiered caching for Business Context Manifests with three tiers:
- tier0 (hot): 1 hour TTL - frequently accessed BCNs
- tier1 (warm): 24 hour TTL - recently accessed BCNs
- tier2 (cold): 7 day TTL - archive storage

Includes connection pooling, retry logic, and comprehensive error handling.
"""

import asyncio
import json
import logging
import time
from datetime import datetime, timedelta
from threading import Lock
from typing import Any, Dict, List, Optional

try:
    import redis
    from redis.connection import ConnectionPool
    from redis.exceptions import ConnectionError, RedisError, TimeoutError

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False
    logging.warning("Redis not available, BCM storage will be disabled")

from ..integration.bcm_reducer import BusinessContextManifest


class BCMStorage:
    """
    Redis storage client for Business Context Manifests with tiered caching.

    Provides intelligent caching with automatic fallback and performance monitoring.
    """

    def __init__(self, redis_url: str = None, max_connections: int = 10):
        """
        Initialize BCM Redis storage client.

        Args:
            redis_url: Redis connection URL
            max_connections: Maximum connection pool size
        """
        self.redis_url = redis_url or "redis://localhost:6379/0"
        self.max_connections = max_connections
        self.redis_client = None
        self.connection_pool = None

        # Connection management
        self.connection_lock = Lock()
        self.last_health_check = 0
        self.health_check_interval = 30  # seconds
        self.connection_retry_count = 0
        self.max_retries = 3
        self.retry_delay = 1  # seconds

        # TTL configurations (in seconds)
        self.ttl_config = {
            "tier0": 3600,  # 1 hour
            "tier1": 86400,  # 24 hours
            "tier2": 604800,  # 7 days
        }

        # Performance metrics
        self.metrics = {
            "cache_hits": 0,
            "cache_misses": 0,
            "connection_errors": 0,
            "storage_errors": 0,
            "total_operations": 0,
            "reconnections": 0,
            "health_checks": 0,
        }

        # Initialize Redis connection
        self._initialize_redis()

    def _initialize_redis(self) -> bool:
        """
        Initialize Redis connection with connection pooling and retry logic.

        Returns:
            True if connection successful, False otherwise
        """
        if not REDIS_AVAILABLE:
            logging.error("Redis not available - cannot initialize BCM storage")
            return False

        with self.connection_lock:
            try:
                # Create connection pool with enhanced settings
                self.connection_pool = ConnectionPool.from_url(
                    self.redis_url,
                    max_connections=self.max_connections,
                    retry_on_timeout=True,
                    socket_connect_timeout=5,
                    socket_timeout=5,
                    socket_keepalive=True,
                    socket_keepalive_options={},
                    health_check_interval=30,
                    max_connections_per_node=20,
                )

                # Create Redis client
                self.redis_client = redis.Redis(
                    connection_pool=self.connection_pool,
                    decode_responses=True,
                    socket_timeout=5,
                    socket_connect_timeout=5,
                    retry_on_timeout=True,
                    health_check_interval=30,
                )

                # Test connection
                self.redis_client.ping()

                # Reset retry count on successful connection
                self.connection_retry_count = 0

                logging.info(f"BCM Redis storage initialized: {self.redis_url}")
                return True

            except Exception as e:
                logging.error(f"Failed to initialize Redis connection: {e}")
                self.connection_retry_count += 1

                # Implement exponential backoff
                if self.connection_retry_count <= self.max_retries:
                    delay = self.retry_delay * (2 ** (self.connection_retry_count - 1))
                    logging.info(
                        f"Retrying Redis connection in {delay} seconds (attempt {self.connection_retry_count})"
                    )
                    time.sleep(delay)
                    return self._initialize_redis()
                else:
                    logging.error("Max Redis connection retries exceeded")
                    self.redis_client = None
                    self.connection_pool = None
                    return False

    def _ensure_connection(self) -> bool:
        """
        Ensure Redis connection is active, reconnect if necessary.

        Returns:
            True if connection is active, False otherwise
        """
        if not self.redis_client:
            return self._initialize_redis()

        # Check if health check is needed
        current_time = time.time()
        if current_time - self.last_health_check > self.health_check_interval:
            return self._perform_health_check()

        return True

    def _perform_health_check(self) -> bool:
        """
        Perform health check and reconnect if needed.

        Returns:
            True if healthy, False otherwise
        """
        try:
            self.redis_client.ping()
            self.last_health_check = time.time()
            self.metrics["health_checks"] += 1
            return True
        except Exception as e:
            logging.warning(f"Redis health check failed: {e}")
            self.metrics["connection_errors"] += 1

            # Attempt reconnection
            logging.info("Attempting to reconnect to Redis...")
            return self._reconnect()

    def _reconnect(self) -> bool:
        """
        Reconnect to Redis.

        Returns:
            True if reconnection successful, False otherwise
        """
        try:
            # Close existing connections
            self._close_connections()

            # Reinitialize
            success = self._initialize_redis()
            if success:
                self.metrics["reconnections"] += 1
                logging.info("Redis reconnection successful")

            return success
        except Exception as e:
            logging.error(f"Redis reconnection failed: {e}")
            return False

    def _close_connections(self) -> None:
        """
        Close Redis connections safely.
        """
        try:
            if self.connection_pool:
                self.connection_pool.disconnect()
                self.connection_pool = None

            if self.redis_client:
                self.redis_client = None

        except Exception as e:
            logging.error(f"Error closing Redis connections: {e}")

    def store_bcm(
        self,
        workspace_id: str,
        bcm: BusinessContextManifest,
        store_all_tiers: bool = True,
    ) -> bool:
        """
        Store BCM in Redis with tiered caching and connection management.

        Args:
            workspace_id: Workspace identifier
            bcm: Business Context Manifest to store
            store_all_tiers: Whether to store in all tiers simultaneously

        Returns:
            True if storage successful, False otherwise
        """
        if not self._ensure_connection():
            logging.warning("Redis not available - cannot store BCM")
            return False

        try:
            # Serialize BCM to JSON
            bcm_dict = bcm.dict()
            bcm_json = json.dumps(bcm_dict, separators=(",", ":"))

            # Create storage keys
            keys = {
                "tier0": f"bcm:tier0:{workspace_id}",
                "tier1": f"bcm:tier1:{workspace_id}",
                "tier2": f"bcm:tier2:{workspace_id}",
            }

            # Store in specified tiers
            if store_all_tiers:
                # Store in all tiers simultaneously
                pipe = self.redis_client.pipeline()

                for tier, key in keys.items():
                    pipe.setex(key, self.ttl_config[tier], bcm_json)

                # Add to tier index for tracking
                pipe.sadd("bcm:tiers", workspace_id)
                pipe.execute()

                logging.info(f"BCM stored for workspace {workspace_id} in all tiers")
            else:
                # Store only in tier0 (hot cache)
                self.redis_client.setex(
                    keys["tier0"], self.ttl_config["tier0"], bcm_json
                )
                logging.info(f"BCM stored for workspace {workspace_id} in tier0 only")

            self.metrics["total_operations"] += 1
            return True

        except RedisError as e:
            logging.error(f"Redis error storing BCM for {workspace_id}: {e}")
            self.metrics["storage_errors"] += 1

            # Try to reconnect on Redis errors
            self._perform_health_check()
            return False
        except Exception as e:
            logging.error(f"Unexpected error storing BCM for {workspace_id}: {e}")
            self.metrics["storage_errors"] += 1
            return False

    def get_bcm(
        self, workspace_id: str, use_fallback: bool = True
    ) -> Optional[BusinessContextManifest]:
        """
        Retrieve BCM from Redis with tier fallback and connection management.

        Args:
            workspace_id: Workspace identifier
            use_fallback: Whether to try lower tiers if higher tier misses

        Returns:
            BCM if found, None otherwise
        """
        if not self._ensure_connection():
            logging.warning("Redis not available - cannot retrieve BCM")
            return None

        try:
            # Try tiers in order: tier0 -> tier1 -> tier2
            tiers_to_try = ["tier0", "tier1", "tier2"] if use_fallback else ["tier0"]

            for tier in tiers_to_try:
                key = f"bcm:{tier}:{workspace_id}"
                bcm_json = self.redis_client.get(key)

                if bcm_json:
                    # Parse BCM from JSON
                    bcm_dict = json.loads(bcm_json)

                    # Convert back to BusinessContextManifest
                    bcm = self._dict_to_bcm(bcm_dict)

                    # Cache hit - promote to higher tier if needed
                    if tier != "tier0" and use_fallback:
                        self._promote_to_tier(workspace_id, bcm, tier)

                    self.metrics["cache_hits"] += 1
                    logging.debug(f"BCM cache hit for {workspace_id} from {tier}")
                    return bcm

            # Cache miss
            self.metrics["cache_misses"] += 1
            logging.debug(f"BCM cache miss for {workspace_id}")
            return None

        except RedisError as e:
            logging.error(f"Redis error retrieving BCM for {workspace_id}: {e}")
            self.metrics["storage_errors"] += 1

            # Try to reconnect on Redis errors
            self._perform_health_check()
            return None
        except Exception as e:
            logging.error(f"Unexpected error retrieving BCM for {workspace_id}: {e}")
            self.metrics["storage_errors"] += 1
            return None

    def _promote_to_tier(
        self, workspace_id: str, bcm: BusinessContextManifest, current_tier: str
    ) -> None:
        """
        Promote BCM to a higher tier (cache warming).

        Args:
            workspace_id: Workspace identifier
            bcm: Business Context Manifest
            current_tier: Current tier where BCM was found
        """
        try:
            if current_tier == "tier1":
                # Promote to tier0
                key = f"bcm:tier0:{workspace_id}"
                bcm_json = json.dumps(bcm.dict(), separators=(",", ":"))
                self.redis_client.setex(key, self.ttl_config["tier0"], bcm_json)
                logging.debug(f"Promoted BCM for {workspace_id} from tier1 to tier0")
            elif current_tier == "tier2":
                # Promote to tier1
                key = f"bcm:tier1:{workspace_id}"
                bcm_json = json.dumps(bcm.dict(), separators=(",", ":"))
                self.redis_client.setex(key, self.ttl_config["tier1"], bcm_json)
                logging.debug(f"Promoted BCM for {workspace_id} from tier2 to tier1")

        except Exception as e:
            logging.error(f"Error promoting BCM for {workspace_id}: {e}")

    def invalidate_bcm(self, workspace_id: str) -> bool:
        """
        Remove BCM from all tiers.

        Args:
            workspace_id: Workspace identifier

        Returns:
            True if invalidation successful, False otherwise
        """
        if not self.redis_client:
            logging.warning("Redis not available - cannot invalidate BCM")
            return False

        try:
            # Remove from all tiers
            keys = [
                f"bcm:tier0:{workspace_id}",
                f"bcm:tier1:{workspace_id}",
                f"bcm:tier2:{workspace_id}",
            ]

            # Delete keys and remove from tier index
            pipe = self.redis_client.pipeline()
            pipe.delete(*keys)
            pipe.srem("bcm:tiers", workspace_id)
            pipe.execute()

            logging.info(f"BCM invalidated for workspace {workspace_id}")
            return True

        except Exception as e:
            logging.error(f"Error invalidating BCM for {workspace_id}: {e}")
            return False

    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Get cache performance statistics.

        Returns:
            Dictionary with cache statistics
        """
        total_ops = self.metrics["total_operations"]
        hit_rate = (
            (self.metrics["cache_hits"] / total_ops * 100) if total_ops > 0 else 0
        )

        stats = {
            "cache_hits": self.metrics["cache_hits"],
            "cache_misses": self.metrics["cache_misses"],
            "hit_rate_percent": round(hit_rate, 2),
            "connection_errors": self.metrics["connection_errors"],
            "storage_errors": self.metrics["storage_errors"],
            "total_operations": total_ops,
        }

        # Add Redis info if available
        if self.redis_client:
            try:
                redis_info = self.redis_client.info()
                stats["redis_memory_used"] = redis_info.get("used_memory_human")
                stats["redis_connected_clients"] = redis_info.get("connected_clients")
                stats["redis_keyspace_hits"] = redis_info.get("keyspace_hits", 0)
                stats["redis_keyspace_misses"] = redis_info.get("keyspace_misses", 0)
            except Exception as e:
                logging.error(f"Error getting Redis info: {e}")

        return stats

    def cleanup_expired(self) -> int:
        """
        Clean up expired BCM entries.

        Returns:
            Number of entries cleaned up
        """
        if not self.redis_client:
            logging.warning("Redis not available - cannot cleanup")
            return 0

        try:
            # Get all workspace IDs in tier index
            workspace_ids = self.redis_client.smembers("bcm:tiers")
            cleaned = 0

            for workspace_id in workspace_ids:
                # Check if all tiers are expired
                tiers_exist = []
                for tier in ["tier0", "tier1", "tier2"]:
                    key = f"bcm:{tier}:{workspace_id}"
                    if self.redis_client.exists(key):
                        tiers_exist.append(tier)

                # If no tiers exist, remove from index
                if not tiers_exist:
                    self.redis_client.srem("bcm:tiers", workspace_id)
                    cleaned += 1

            logging.info(f"Cleaned up {cleaned} expired BCM entries")
            return cleaned

        except Exception as e:
            logging.error(f"Error during cleanup: {e}")
            return 0

    def health_check(self) -> Dict[str, Any]:
        """
        Perform comprehensive health check on Redis connection.

        Returns:
            Health check results with detailed metrics
        """
        health = {
            "redis_available": False,
            "connection_status": "disconnected",
            "response_time_ms": None,
            "error": None,
            "pool_stats": {},
            "connection_info": {},
        }

        if not self.redis_client:
            health["error"] = "Redis client not initialized"
            return health

        try:
            start_time = time.time()
            self.redis_client.ping()
            response_time = (time.time() - start_time) * 1000

            health["redis_available"] = True
            health["connection_status"] = "connected"
            health["response_time_ms"] = round(response_time, 2)

            # Get connection pool stats
            if self.connection_pool:
                pool_stats = self.connection_pool.get_connection_pool_stats()
                health["pool_stats"] = {
                    "created_connections": pool_stats.get("created_connections", 0),
                    "available_connections": pool_stats.get("available_connections", 0),
                    "in_use_connections": pool_stats.get("in_use_connections", 0),
                }

            # Get Redis info
            redis_info = self.redis_client.info()
            health["connection_info"] = {
                "redis_version": redis_info.get("redis_version"),
                "uptime_in_seconds": redis_info.get("uptime_in_seconds"),
                "connected_clients": redis_info.get("connected_clients"),
                "used_memory_human": redis_info.get("used_memory_human"),
                "keyspace_hits": redis_info.get("keyspace_hits", 0),
                "keyspace_misses": redis_info.get("keyspace_misses", 0),
            }

        except Exception as e:
            health["error"] = str(e)
            logging.error(f"Redis health check failed: {e}")

            # Attempt reconnection
            self._perform_health_check()

        return health

    def get_connection_metrics(self) -> Dict[str, Any]:
        """
        Get detailed connection and performance metrics.

        Returns:
            Dictionary with connection metrics
        """
        metrics = self.metrics.copy()

        # Add connection-specific metrics
        metrics.update(
            {
                "last_health_check": self.last_health_check,
                "connection_retry_count": self.connection_retry_count,
                "max_retries": self.max_retries,
                "health_check_interval": self.health_check_interval,
                "redis_url": self.redis_url,
            }
        )

        # Add pool stats if available
        if self.connection_pool:
            try:
                pool_stats = self.connection_pool.get_connection_pool_stats()
                metrics["connection_pool"] = {
                    "created_connections": pool_stats.get("created_connections", 0),
                    "available_connections": pool_stats.get("available_connections", 0),
                    "in_use_connections": pool_stats.get("in_use_connections", 0),
                    "max_connections": self.max_connections,
                }
            except Exception as e:
                logging.error(f"Error getting pool stats: {e}")

        return metrics

    def _dict_to_bcm(self, bcm_dict: Dict[str, Any]) -> BusinessContextManifest:
        """
        Convert dictionary back to BusinessContextManifest.

        Args:
            bcm_dict: BCM dictionary

        Returns:
            BusinessContextManifest object
        """
        # This is a simplified conversion - in a real implementation,
        # you'd need proper deserialization logic
        try:
            return BusinessContextManifest(**bcm_dict)
        except Exception as e:
            logging.error(f"Error converting dict to BCM: {e}")
            # Return a minimal BCM as fallback
            return BusinessContextManifest(
                version="2.0",
                generated_at=datetime.utcnow().isoformat(),
                workspace_id=bcm_dict.get("workspace_id", "unknown"),
                user_id=bcm_dict.get("user_id"),
            )

    def close(self) -> None:
        """Close Redis connections safely."""
        with self.connection_lock:
            self._close_connections()
            logging.info("BCM Redis storage connections closed")

    def __del__(self):
        """Cleanup on deletion."""
        self.close()
