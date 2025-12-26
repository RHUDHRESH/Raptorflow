import asyncio
import logging
import time
from contextlib import asynccontextmanager
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

import psycopg
from psycopg_pool import AsyncConnectionPool

logger = logging.getLogger("raptorflow.db.monitor")


@dataclass
class ConnectionPoolStats:
    """Database connection pool statistics."""

    total_connections: int = 0
    active_connections: int = 0
    idle_connections: int = 0
    failed_connections: int = 0
    avg_connection_time_ms: float = 0.0
    max_connection_time_ms: float = 0.0
    min_connection_time_ms: float = float("inf")
    pool_utilization_percent: float = 0.0
    last_health_check: Optional[datetime] = None
    connection_errors: List[str] = field(default_factory=list)


class DatabasePoolMonitor:
    """
    Production-grade database connection pool monitoring and optimization.
    """

    def __init__(self, pool: AsyncConnectionPool):
        self.pool = pool
        self.stats = ConnectionPoolStats()
        self.connection_times: List[float] = []
        self.monitoring_enabled = True
        self._lock = asyncio.Lock()

    async def get_pool_stats(self) -> ConnectionPoolStats:
        """Get current pool statistics."""
        async with self._lock:
            try:
                # Get pool size information
                pool_size = self.pool.get_size()
                pool_idle = self.pool.get_idle_size()

                self.stats.total_connections = pool_size
                self.stats.idle_connections = pool_idle
                self.stats.active_connections = pool_size - pool_idle

                # Calculate utilization
                max_size = getattr(self.pool, "max_size", 50)
                self.stats.pool_utilization_percent = (pool_size / max_size) * 100

                # Calculate connection time statistics
                if self.connection_times:
                    self.stats.avg_connection_time_ms = sum(
                        self.connection_times
                    ) / len(self.connection_times)
                    self.stats.max_connection_time_ms = max(self.connection_times)
                    self.stats.min_connection_time_ms = min(self.connection_times)

                self.stats.last_health_check = datetime.utcnow()

                return self.stats

            except Exception as e:
                logger.error(f"Error getting pool stats: {e}")
                return self.stats

    async def record_connection_time(self, connection_time_ms: float):
        """Record connection time for monitoring."""
        async with self._lock:
            self.connection_times.append(connection_time_ms)

            # Keep only last 1000 measurements
            if len(self.connection_times) > 1000:
                self.connection_times = self.connection_times[-1000:]

    async def record_connection_error(self, error: str):
        """Record connection error."""
        async with self._lock:
            self.stats.failed_connections += 1
            self.stats.connection_errors.append(error)

            # Keep only last 100 errors
            if len(self.stats.connection_errors) > 100:
                self.stats.connection_errors = self.stats.connection_errors[-100:]

    async def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive pool health check."""
        health_status = {"healthy": True, "issues": [], "recommendations": []}

        try:
            stats = await self.get_pool_stats()

            # Check pool utilization
            if stats.pool_utilization_percent > 80:
                health_status["healthy"] = False
                health_status["issues"].append(
                    f"High pool utilization: {stats.pool_utilization_percent:.1f}%"
                )
                health_status["recommendations"].append(
                    "Consider increasing max_pool_size"
                )

            # Check failed connections
            if stats.failed_connections > 10:
                health_status["healthy"] = False
                health_status["issues"].append(
                    f"High failure rate: {stats.failed_connections} failed connections"
                )
                health_status["recommendations"].append(
                    "Check database connectivity and configuration"
                )

            # Check connection times
            if stats.avg_connection_time_ms > 1000:  # 1 second
                health_status["issues"].append(
                    f"Slow connection times: {stats.avg_connection_time_ms:.1f}ms avg"
                )
                health_status["recommendations"].append(
                    "Optimize database network or increase timeouts"
                )

            # Check if pool is at capacity
            if stats.active_connections >= getattr(self.pool, "max_size", 50) * 0.9:
                health_status["issues"].append("Pool near maximum capacity")
                health_status["recommendations"].append(
                    "Monitor for potential connection exhaustion"
                )

            # Add recent errors if any
            if stats.connection_errors:
                health_status["recent_errors"] = stats.connection_errors[
                    -5:
                ]  # Last 5 errors

            health_status["stats"] = {
                "total_connections": stats.total_connections,
                "active_connections": stats.active_connections,
                "idle_connections": stats.idle_connections,
                "pool_utilization_percent": stats.pool_utilization_percent,
                "avg_connection_time_ms": stats.avg_connection_time_ms,
                "failed_connections": stats.failed_connections,
            }

        except Exception as e:
            health_status["healthy"] = False
            health_status["issues"].append(f"Health check failed: {str(e)}")
            logger.error(f"Database pool health check failed: {e}")

        return health_status

    async def optimize_pool_settings(self) -> Dict[str, Any]:
        """Suggest optimal pool settings based on current usage."""
        stats = await self.get_pool_stats()

        recommendations = {
            "current_settings": {
                "min_size": getattr(self.pool, "min_size", 5),
                "max_size": getattr(self.pool, "max_size", 50),
                "max_lifetime": getattr(self.pool, "max_lifetime", 3600),
                "max_idle": getattr(self.pool, "max_idle", 600),
            },
            "recommended_settings": {},
            "reasoning": [],
        }

        # Analyze utilization patterns
        if stats.pool_utilization_percent > 80:
            recommendations["recommended_settings"]["max_size"] = (
                getattr(self.pool, "max_size", 50) + 10
            )
            recommendations["reasoning"].append(
                "High utilization suggests increasing max_size"
            )

        if stats.avg_connection_time_ms > 500:
            recommendations["recommended_settings"]["min_size"] = min(
                getattr(self.pool, "min_size", 5) + 2,
                getattr(self.pool, "max_size", 50) - 5,
            )
            recommendations["reasoning"].append(
                "Slow connection times suggest more warm connections"
            )

        if stats.failed_connections > 5:
            recommendations["recommended_settings"]["max_lifetime"] = 1800  # 30 minutes
            recommendations["reasoning"].append(
                "High failure rate may indicate stale connections"
            )

        return recommendations

    @asynccontextmanager
    async def monitored_connection(self):
        """Get a connection with monitoring."""
        start_time = time.time()
        connection = None

        try:
            connection = await self.pool.getconn()
            connection_time_ms = (time.time() - start_time) * 1000
            await self.record_connection_time(connection_time_ms)

            yield connection

        except Exception as e:
            error_msg = f"Connection failed: {str(e)}"
            await self.record_connection_error(error_msg)
            raise
        finally:
            if connection:
                try:
                    await self.pool.putconn(connection)
                except Exception as e:
                    logger.error(f"Error returning connection to pool: {e}")


class DatabasePoolOptimizer:
    """
    Automatic database pool optimization and management.
    """

    def __init__(self, pool: AsyncConnectionPool):
        self.pool = pool
        self.monitor = DatabasePoolMonitor(pool)
        self.optimization_enabled = True
        self.last_optimization: Optional[datetime] = None

    async def start_monitoring(self):
        """Start continuous pool monitoring."""
        if self.optimization_enabled:
            asyncio.create_task(self._monitoring_loop())
            logger.info("Database pool monitoring started")

    async def stop_monitoring(self):
        """Stop pool monitoring."""
        self.optimization_enabled = False
        logger.info("Database pool monitoring stopped")

    async def _monitoring_loop(self):
        """Continuous monitoring loop."""
        while self.optimization_enabled:
            try:
                # Perform health check every 30 seconds
                health = await self.monitor.health_check()

                if not health["healthy"]:
                    logger.warning(
                        f"Database pool health issues detected: {health['issues']}"
                    )

                # Optimize settings every 5 minutes
                if (
                    self.last_optimization is None
                    or datetime.utcnow() - self.last_optimization > timedelta(minutes=5)
                ):
                    await self._auto_optimize()
                    self.last_optimization = datetime.utcnow()

                await asyncio.sleep(30)  # Check every 30 seconds

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in pool monitoring loop: {e}")
                await asyncio.sleep(60)  # Wait longer on error

    async def _auto_optimize(self):
        """Perform automatic optimization based on current metrics."""
        try:
            recommendations = await self.monitor.optimize_pool_settings()

            if recommendations["recommended_settings"]:
                logger.info(
                    f"Pool optimization recommendations: {recommendations['reasoning']}"
                )

                # Note: Actual pool size changes would require pool recreation
                # This is for monitoring and alerting purposes
                for setting, value in recommendations["recommended_settings"].items():
                    current_value = recommendations["current_settings"][setting]
                    if value != current_value:
                        logger.info(
                            f"Recommended {setting}: {current_value} -> {value}"
                        )

        except Exception as e:
            logger.error(f"Error in auto-optimization: {e}")

    async def get_comprehensive_stats(self) -> Dict[str, Any]:
        """Get comprehensive pool statistics and health."""
        stats = await self.monitor.get_pool_stats()
        health = await self.monitor.health_check()
        recommendations = await self.monitor.optimize_pool_settings()

        return {
            "timestamp": datetime.utcnow().isoformat(),
            "pool_stats": {
                "total_connections": stats.total_connections,
                "active_connections": stats.active_connections,
                "idle_connections": stats.idle_connections,
                "pool_utilization_percent": stats.pool_utilization_percent,
                "avg_connection_time_ms": stats.avg_connection_time_ms,
                "max_connection_time_ms": stats.max_connection_time_ms,
                "failed_connections": stats.failed_connections,
            },
            "health_status": health,
            "optimization_recommendations": recommendations,
            "monitoring_enabled": self.optimization_enabled,
        }


# Global pool optimizer
_pool_optimizer: Optional[DatabasePoolOptimizer] = None


def get_pool_optimizer() -> DatabasePoolOptimizer:
    """Get the global pool optimizer instance."""
    global _pool_optimizer
    return _pool_optimizer


def set_pool_optimizer(optimizer: DatabasePoolOptimizer):
    """Set the global pool optimizer instance."""
    global _pool_optimizer
    _pool_optimizer = optimizer


async def start_pool_monitoring(pool: AsyncConnectionPool):
    """Start database pool monitoring."""
    optimizer = DatabasePoolOptimizer(pool)
    set_pool_optimizer(optimizer)
    await optimizer.start_monitoring()


async def stop_pool_monitoring():
    """Stop database pool monitoring."""
    optimizer = get_pool_optimizer()
    if optimizer:
        await optimizer.stop_monitoring()


@asynccontextmanager
async def get_monitored_db_connection():
    """Get a database connection with monitoring."""
    optimizer = get_pool_optimizer()
    if optimizer:
        async with optimizer.monitor.monitored_connection() as conn:
            yield conn
    else:
        # Fallback to regular connection
        from db import get_pool

        pool = get_pool()
        async with pool.connection() as conn:
            yield conn


async def get_database_pool_health() -> Dict[str, Any]:
    """Get comprehensive database pool health status."""
    optimizer = get_pool_optimizer()
    if optimizer:
        return await optimizer.get_comprehensive_stats()
    else:
        return {"error": "Pool monitoring not initialized"}
