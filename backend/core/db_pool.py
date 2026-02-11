"""
Database Connection Pool Manager
Implements asyncpg connection pooling for optimal database performance
"""

import asyncpg
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)

_pool: Optional[asyncpg.Pool] = None


async def create_pool(
    min_size: int = 10,
    max_size: int = 20,
    command_timeout: float = 60.0,
    max_queries: int = 50000,
    max_inactive_connection_lifetime: float = 300.0,
) -> asyncpg.Pool:
    """
    Create database connection pool with optimal settings.
    
    Args:
        min_size: Minimum number of connections in pool
        max_size: Maximum number of connections in pool
        command_timeout: Timeout for queries in seconds
        max_queries: Max queries per connection before recycling
        max_inactive_connection_lifetime: Max idle time before closing connection
        
    Returns:
        asyncpg.Pool instance
    """
    global _pool
    
    if _pool is not None:
        return _pool
    
    # Get database URL from environment
    database_url = (
        os.getenv("DATABASE_URL")
        or os.getenv("SUPABASE_DB_URL")
        or os.getenv("POSTGRES_URL")
    )
    
    if not database_url:
        raise ValueError("DATABASE_URL not configured")
    
    logger.info(
        f"Creating connection pool: min={min_size}, max={max_size}, "
        f"timeout={command_timeout}s"
    )
    
    try:
        _pool = await asyncpg.create_pool(
            database_url,
            min_size=min_size,
            max_size=max_size,
            command_timeout=command_timeout,
            max_queries=max_queries,
            max_inactive_connection_lifetime=max_inactive_connection_lifetime,
            # Connection initialization
            init=_init_connection,
        )
        
        logger.info("Database connection pool created successfully")
        return _pool
        
    except Exception as e:
        logger.error(f"Failed to create connection pool: {e}")
        raise


async def _init_connection(conn: asyncpg.Connection) -> None:
    """Initialize connection with custom settings"""
    # Set timezone
    await conn.execute("SET timezone TO 'UTC'")
    
    # Set statement timeout (30 seconds)
    await conn.execute("SET statement_timeout TO '30s'")
    
    # Set application name for monitoring
    await conn.execute("SET application_name TO 'raptorflow-backend'")


async def get_pool() -> Optional[asyncpg.Pool]:
    """Get the database connection pool"""
    global _pool
    
    if _pool is None:
        _pool = await create_pool()
    
    return _pool


async def close_pool() -> None:
    """Close the database connection pool"""
    global _pool
    
    if _pool is not None:
        await _pool.close()
        _pool = None
        logger.info("Database connection pool closed")


async def execute_query(query: str, *args, timeout: Optional[float] = None):
    """
    Execute a query using the connection pool.
    
    Args:
        query: SQL query string
        *args: Query parameters
        timeout: Optional query timeout override
        
    Returns:
        Query result
    """
    pool = await get_pool()
    
    async with pool.acquire() as conn:
        return await conn.fetch(query, *args, timeout=timeout)


async def execute_one(query: str, *args, timeout: Optional[float] = None):
    """
    Execute a query and return single row.
    
    Args:
        query: SQL query string
        *args: Query parameters
        timeout: Optional query timeout override
        
    Returns:
        Single row result or None
    """
    pool = await get_pool()
    
    async with pool.acquire() as conn:
        return await conn.fetchrow(query, *args, timeout=timeout)


async def execute_write(query: str, *args, timeout: Optional[float] = None):
    """
    Execute a write query (INSERT, UPDATE, DELETE).
    
    Args:
        query: SQL query string
        *args: Query parameters
        timeout: Optional query timeout override
        
    Returns:
        Status string
    """
    pool = await get_pool()
    
    async with pool.acquire() as conn:
        return await conn.execute(query, *args, timeout=timeout)


async def get_pool_stats() -> dict:
    """
    Get connection pool statistics.
    
    Returns:
        Dictionary with pool stats
    """
    pool = await get_pool()
    
    if pool is None:
        return {"status": "not_initialized"}
    
    return {
        "size": pool.get_size(),
        "free_size": pool.get_idle_size(),
        "min_size": pool.get_min_size(),
        "max_size": pool.get_max_size(),
        "status": "healthy" if pool.get_size() > 0 else "degraded",
    }
