"""
Database Infrastructure - Supabase client management.
"""

from __future__ import annotations

import logging
from typing import Any, Optional

logger = logging.getLogger(__name__)

from backend.infrastructure.database.pool import (
    create_pool,
    get_pool,
    close_pool,
    execute_query,
    execute_one,
    execute_write,
    get_pool_stats,
)
from backend.infrastructure.database.supabase import (
    get_supabase_client,
    get_supabase_admin,
    reset_supabase_clients,
)
from backend.infrastructure.database.monitor import (
    QueryMonitor,
    QueryStats,
    query_monitor,
    monitored_query,
)


class DatabasePool:
    """
    Database connection pool manager.

    Wraps Supabase client for consistent access patterns.

    Example:
        pool = DatabasePool()
        client = pool.get_client()
        result = client.table("users").select("*").execute()
    """

    def __init__(
        self, supabase_url: Optional[str] = None, supabase_key: Optional[str] = None
    ):
        self._url = supabase_url
        self._key = supabase_key
        self._client = None
        self._initialized = False

    def get_client(self):
        """Get the Supabase client (lazy initialization)."""
        if self._client is None:
            from backend.infrastructure.database.supabase import get_supabase_client

            self._client = get_supabase_client()
        return self._client

    async def initialize(self) -> None:
        """Initialize the database connection."""
        self._client = self.get_client()
        self._initialized = True
        logger.info("Database pool initialized")

    async def health_check(self) -> dict:
        """Check database health."""
        try:
            client = self.get_client()
            client.table("health_check").select("count", count="exact").limit(
                0
            ).execute()
            return {"status": "healthy"}
        except Exception as e:
            return {"status": "unhealthy", "error": str(e)}


_db_pool: Optional[DatabasePool] = None


def get_db_client() -> DatabasePool:
    """Get the global database pool instance."""
    global _db_pool
    if _db_pool is None:
        _db_pool = DatabasePool()
    return _db_pool


__all__ = [
    "DatabasePool",
    "get_db_client",
    "create_pool",
    "get_pool",
    "close_pool",
    "execute_query",
    "execute_one",
    "execute_write",
    "get_pool_stats",
    "get_supabase_client",
    "get_supabase_admin",
    "reset_supabase_clients",
    "QueryMonitor",
    "QueryStats",
    "query_monitor",
    "monitored_query",
]
