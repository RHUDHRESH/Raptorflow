"""
RaptorFlow Database Connection Pool Management
Provides robust connection pool handling with proper error recovery and monitoring.
"""

import asyncio
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

import asyncpg
from sqlalchemy.exc import DisconnectionError, SQLAlchemyError, TimeoutError
from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, create_async_engine
from sqlalchemy.pool import QueuePool

from core.enhanced_exceptions import (
    DatabaseError,
    handle_database_error,
    handle_system_error,
    handle_timeout_error,
)

logger = logging.getLogger("raptorflow.database_pool")


class PoolStatus(Enum):
    """Connection pool status."""

    HEALTHY = "healthy"
    DEGRADED = "degraded"
    UNHEALTHY = "unhealthy"
    RECOVERING = "recovering"
    FAILED = "failed"


@dataclass
class PoolMetrics:
    """Connection pool metrics."""

    total_connections: int = 0
    active_connections: int = 0
    idle_connections: int = 0
    overflow_connections: int = 0
    invalid_connections: int = 0
    checkout_timeout_count: int = 0
    connection_errors: int = 0
    recovery_attempts: int = 0
    last_error: Optional[str] = None
    last_error_time: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class PoolConfig:
    """Connection pool configuration."""

    min_size: int = 5
    max_size: int = 20
    max_overflow: int = 10
    pool_timeout: int = 30
    pool_recycle: int = 3600
    pool_pre_ping: bool = True
    connect_args: Dict[str, Any] = field(default_factory=dict)

    # Health check configuration
    health_check_interval: int = 60
    health_check_timeout: int = 10
    max_retries: int = 3
    retry_delay: float = 1.0

    # Circuit breaker configuration
    circuit_breaker_threshold: int = 5
    circuit_breaker_timeout: int = 300


class DatabaseConnectionPool:
    """
    Enhanced database connection pool with robust error handling and monitoring.
    """

    def __init__(self, database_url: str, config: Optional[PoolConfig] = None):
        self.database_url = database_url
        self.config = config or PoolConfig()
        self.engine: Optional[AsyncEngine] = None
        self.pool_status = PoolStatus.HEALTHY
        self.metrics = PoolMetrics()
        self._health_check_task: Optional[asyncio.Task] = None
        self._circuit_breaker_open = False
        self._circuit_breaker_time: Optional[datetime] = None
        self._connection_lock = asyncio.Lock()

    async def initialize(self) -> bool:
        """Initialize the database connection pool."""
        try:
            logger.info("Initializing database connection pool...")

            # Create async engine with enhanced pool configuration
            self.engine = create_async_engine(
                self.database_url,
                poolclass=QueuePool,
                pool_size=self.config.min_size,
                max_overflow=self.config.max_overflow,
                pool_timeout=self.config.pool_timeout,
                pool_recycle=self.config.pool_recycle,
                pool_pre_ping=self.config.pool_pre_ping,
                connect_args=self.config.connect_args,
                echo=False,  # Set to True for SQL debugging
            )

            # Test the connection
            async with self.engine.begin() as conn:
                await conn.execute("SELECT 1")

            self.pool_status = PoolStatus.HEALTHY
            self.metrics.created_at = datetime.utcnow()

            # Start health check task
            self._health_check_task = asyncio.create_task(self._health_check_loop())

            logger.info(
                f"Database pool initialized successfully (min={self.config.min_size}, max={self.config.max_size})"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to initialize database pool: {e}")
            self.pool_status = PoolStatus.FAILED
            await self._handle_pool_error("pool_initialization", e)
            return False

    async def get_session(self) -> AsyncSession:
        """Get a database session with error handling."""
        if self.engine is None:
            raise DatabaseError(
                "Database pool not initialized", operation="get_session"
            )

        # Check circuit breaker
        if self._is_circuit_breaker_open():
            raise DatabaseError(
                "Database pool circuit breaker is open",
                operation="get_session",
                retry_after=self._get_circuit_breaker_retry_after(),
            )

        try:
            async with self._connection_lock:
                session = AsyncSession(self.engine)

                # Update metrics
                pool = self.engine.pool
                self.metrics.total_connections = pool.size() + pool.overflow()
                self.metrics.active_connections = pool.checkedout()
                self.metrics.idle_connections = pool.checkedin()
                self.metrics.overflow_connections = pool.overflow()

                return session

        except TimeoutError as e:
            self.metrics.checkout_timeout_count += 1
            await self._handle_pool_error("checkout_timeout", e)
            raise handle_timeout_error(
                "Database connection checkout timeout",
                timeout_seconds=self.config.pool_timeout,
                operation="get_session",
            )
        except DisconnectionError as e:
            self.metrics.connection_errors += 1
            await self._handle_pool_error("disconnection", e)
            raise handle_database_error(
                "Database connection lost",
                operation="get_session",
                original_error=str(e),
            )
        except Exception as e:
            self.metrics.connection_errors += 1
            await self._handle_pool_error("connection_error", e)
            raise handle_database_error(
                "Failed to get database session",
                operation="get_session",
                original_error=str(e),
            )

    async def execute_query(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> Any:
        """Execute a database query with error handling and retry logic."""
        if self.engine is None:
            raise DatabaseError(
                "Database pool not initialized", operation="execute_query"
            )

        timeout = timeout or self.config.pool_timeout
        last_error = None

        for attempt in range(self.config.max_retries):
            try:
                async with asyncio.timeout(timeout):
                    async with self.engine.begin() as conn:
                        if params:
                            result = await conn.execute(query, params)
                        else:
                            result = await conn.execute(query)
                        return result

            except asyncio.TimeoutError as e:
                last_error = e
                logger.warning(
                    f"Query timeout (attempt {attempt + 1}/{self.config.max_retries}): {query[:100]}..."
                )
                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(self.config.retry_delay * (2**attempt))
                    continue
                break
            except SQLAlchemyError as e:
                last_error = e
                logger.warning(
                    f"Query failed (attempt {attempt + 1}/{self.config.max_retries}): {e}"
                )
                if attempt < self.config.max_retries - 1:
                    await asyncio.sleep(self.config.retry_delay * (2**attempt))
                    continue
                break
            except Exception as e:
                last_error = e
                logger.error(f"Unexpected query error: {e}")
                break

        # Handle final error
        if isinstance(last_error, asyncio.TimeoutError):
            raise handle_timeout_error(
                f"Query execution timed out after {timeout}s",
                timeout_seconds=timeout,
                operation="execute_query",
                query=query[:100],
            )
        elif isinstance(last_error, SQLAlchemyError):
            raise handle_database_error(
                f"Query execution failed: {str(last_error)}",
                operation="execute_query",
                query=query[:100],
                original_error=str(last_error),
            )
        else:
            raise handle_system_error(
                f"Unexpected error during query execution: {str(last_error)}",
                component="database_query",
                operation="execute_query",
                original_error=str(last_error),
            )

    async def close(self):
        """Close the database connection pool."""
        try:
            if self._health_check_task:
                self._health_check_task.cancel()
                try:
                    await self._health_check_task
                except asyncio.CancelledError:
                    pass

            if self.engine:
                await self.engine.dispose()
                self.engine = None

            self.pool_status = PoolStatus.FAILED
            logger.info("Database connection pool closed")

        except Exception as e:
            logger.error(f"Error closing database pool: {e}")

    async def _health_check_loop(self):
        """Periodic health check for the connection pool."""
        while True:
            try:
                await asyncio.sleep(self.config.health_check_interval)
                await self._perform_health_check()
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Health check error: {e}")
                await self._handle_pool_error("health_check", e)

    async def _perform_health_check(self):
        """Perform a health check on the connection pool."""
        if self.engine is None:
            return

        try:
            async with asyncio.timeout(self.config.health_check_timeout):
                async with self.engine.begin() as conn:
                    await conn.execute("SELECT 1")

            # Health check passed
            if self.pool_status != PoolStatus.HEALTHY:
                logger.info("Database pool health check passed - marking as healthy")
                self.pool_status = PoolStatus.HEALTHY

            # Reset circuit breaker if it was open
            if self._circuit_breaker_open:
                self._circuit_breaker_open = False
                self._circuit_breaker_time = None
                logger.info("Database pool circuit breaker reset")

        except asyncio.TimeoutError:
            logger.warning("Database pool health check timeout")
            await self._handle_pool_error(
                "health_check_timeout", TimeoutError("Health check timeout")
            )
        except Exception as e:
            logger.warning(f"Database pool health check failed: {e}")
            await self._handle_pool_error("health_check_failed", e)

    async def _handle_pool_error(self, error_type: str, error: Exception):
        """Handle pool errors and update metrics."""
        self.metrics.last_error = f"{error_type}: {str(error)}"
        self.metrics.last_error_time = datetime.utcnow()

        # Update pool status based on error
        if error_type in ["checkout_timeout", "disconnection", "connection_error"]:
            self.metrics.connection_errors += 1

            # Check if we need to open circuit breaker
            if self.metrics.connection_errors >= self.config.circuit_breaker_threshold:
                self._open_circuit_breaker()

        # Update pool status
        if self.pool_status == PoolStatus.HEALTHY:
            self.pool_status = PoolStatus.DEGRADED
        elif self.pool_status == PoolStatus.DEGRADED:
            self.pool_status = PoolStatus.UNHEALTHY

        logger.warning(f"Pool error handled: {error_type} - {error}")

    def _is_circuit_breaker_open(self) -> bool:
        """Check if circuit breaker is open."""
        if not self._circuit_breaker_open:
            return False

        if self._circuit_breaker_time is None:
            return True

        # Check if circuit breaker timeout has passed
        time_since_open = datetime.utcnow() - self._circuit_breaker_time
        if time_since_open.total_seconds() > self.config.circuit_breaker_timeout:
            return False

        return True

    def _get_circuit_breaker_retry_after(self) -> int:
        """Get retry after seconds for circuit breaker."""
        if not self._circuit_breaker_open or self._circuit_breaker_time is None:
            return 0

        time_since_open = datetime.utcnow() - self._circuit_breaker_time
        retry_after = self.config.circuit_breaker_timeout - int(
            time_since_open.total_seconds()
        )
        return max(0, retry_after)

    def _open_circuit_breaker(self):
        """Open the circuit breaker."""
        if not self._circuit_breaker_open:
            self._circuit_breaker_open = True
            self._circuit_breaker_time = datetime.utcnow()
            self.pool_status = PoolStatus.FAILED
            logger.warning("Database pool circuit breaker opened")

    async def recover_pool(self) -> bool:
        """Attempt to recover the connection pool."""
        logger.info("Attempting to recover database connection pool...")
        self.metrics.recovery_attempts += 1
        self.pool_status = PoolStatus.RECOVERING

        try:
            # Close existing engine
            if self.engine:
                await self.engine.dispose()

            # Reinitialize pool
            return await self.initialize()

        except Exception as e:
            logger.error(f"Pool recovery failed: {e}")
            self.pool_status = PoolStatus.FAILED
            await self._handle_pool_error("recovery_failed", e)
            return False

    def get_pool_status(self) -> Dict[str, Any]:
        """Get current pool status and metrics."""
        return {
            "status": self.pool_status.value,
            "circuit_breaker_open": self._circuit_breaker_open,
            "circuit_breaker_retry_after": self._get_circuit_breaker_retry_after(),
            "metrics": {
                "total_connections": self.metrics.total_connections,
                "active_connections": self.metrics.active_connections,
                "idle_connections": self.metrics.idle_connections,
                "overflow_connections": self.metrics.overflow_connections,
                "checkout_timeout_count": self.metrics.checkout_timeout_count,
                "connection_errors": self.metrics.connection_errors,
                "recovery_attempts": self.metrics.recovery_attempts,
                "last_error": self.metrics.last_error,
                "last_error_time": (
                    self.metrics.last_error_time.isoformat()
                    if self.metrics.last_error_time
                    else None
                ),
                "created_at": self.metrics.created_at.isoformat(),
            },
            "config": {
                "min_size": self.config.min_size,
                "max_size": self.config.max_size,
                "max_overflow": self.config.max_overflow,
                "pool_timeout": self.config.pool_timeout,
                "health_check_interval": self.config.health_check_interval,
                "circuit_breaker_threshold": self.config.circuit_breaker_threshold,
            },
        }


# Global database pool instance
_database_pool: Optional[DatabaseConnectionPool] = None


async def get_database_pool() -> DatabaseConnectionPool:
    """Get the global database connection pool instance."""
    global _database_pool
    if _database_pool is None:
        from core.config import get_settings

        settings = get_settings()

        config = PoolConfig(
            min_size=settings.DB_POOL_MIN_SIZE,
            max_size=settings.DB_POOL_MAX_SIZE,
            max_overflow=settings.DB_POOL_MAX_OVERFLOW,
            pool_timeout=settings.DB_POOL_TIMEOUT,
            health_check_interval=settings.DB_HEALTH_CHECK_INTERVAL,
        )

        _database_pool = DatabaseConnectionPool(settings.DATABASE_URL, config)
        await _database_pool.initialize()

    return _database_pool


async def get_db_session() -> AsyncSession:
    """Get a database session with automatic error handling."""
    pool = await get_database_pool()
    return await pool.get_session()


# Utility functions
async def execute_with_retry(
    query: str, params: Optional[Dict[str, Any]] = None, timeout: Optional[float] = None
) -> Any:
    """Execute query with automatic retry and error handling."""
    pool = await get_database_pool()
    return await pool.execute_query(query, params, timeout)


async def check_database_health() -> Dict[str, Any]:
    """Check database health status."""
    try:
        pool = await get_database_pool()
        return pool.get_pool_status()
    except Exception as e:
        return {
            "status": "failed",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


if __name__ == "__main__":
    # Test database pool
    async def test_pool():
        pool = DatabaseConnectionPool("postgresql://test:test@localhost/test")
        success = await pool.initialize()
        print(f"Pool initialized: {success}")
        print(pool.get_pool_status())
        await pool.close()

    asyncio.run(test_pool())
