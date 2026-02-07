"""
Database Infrastructure Layer
Handles Supabase connections and operations
"""

import logging
import os
from typing import Any, Dict, List, Optional

from core.supabase_mgr import get_supabase_admin, get_supabase_client
from pydantic import BaseModel

from supabase import Client

logger = logging.getLogger(__name__)


class SupabaseConfig(BaseModel):
    """Supabase configuration settings"""

    url: str
    anon_key: str
    service_role_key: str
    pool_min: int = 2
    pool_max: int = 10
    pool_idle_timeout: int = 30000


class SupabaseClient:
    """Supabase client wrapper with connection pooling and error handling"""

    def __init__(self, config: Optional[SupabaseConfig] = None):
        self.config = config or self._load_config()
        self._client: Optional[Client] = None
        # Lazy init: do not connect at import time

    def _load_config(self) -> SupabaseConfig:
        """Load Supabase configuration from environment variables"""
        return SupabaseConfig(
            url=(
                os.getenv("SUPABASE_URL")
                or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
                or os.getenv("DATABASE_URL")
                or ""
            ),
            anon_key=(
                os.getenv("SUPABASE_ANON_KEY")
                or os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")
                or ""
            ),
            service_role_key=(
                os.getenv("SUPABASE_SERVICE_ROLE_KEY")
                or os.getenv("SUPABASE_SERVICE_KEY")
                or ""
            ),
            pool_min=int(os.getenv("DATABASE_POOL_MIN", "2")),
            pool_max=int(os.getenv("DATABASE_POOL_MAX", "10")),
            pool_idle_timeout=int(os.getenv("DATABASE_POOL_IDLE_TIMEOUT", "30000")),
        )

    def _initialize_client(self):
        """Initialize Supabase client"""
        try:
            # Delegate to canonical supabase manager
            self._client = get_supabase_client()
            logger.info("Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            raise

    def get_client(self) -> Client:
        """Get Supabase client instance"""
        if not self._client:
            self._initialize_client()
        return self._client

    def get_service_client(self) -> Client:
        """Get Supabase client with service role key"""
        try:
            return get_supabase_admin()
        except Exception as e:
            logger.error(f"Failed to create service client: {e}")
            raise

    async def execute_query(
        self, query: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Execute a SQL query with error handling"""
        try:
            client = self.get_client()
            result = client.rpc("execute_sql", {"query": query, "params": params or {}})
            return result
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise

    async def insert(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert data into a table"""
        try:
            client = self.get_client()
            result = client.table(table).insert(data).execute()
            return result
        except Exception as e:
            logger.error(f"Insert operation failed: {e}")
            raise

    async def update(
        self, table: str, data: Dict[str, Any], filters: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update data in a table"""
        try:
            client = self.get_client()
            query = client.table(table).update(data)

            for key, value in filters.items():
                query = query.eq(key, value)

            result = query.execute()
            return result
        except Exception as e:
            logger.error(f"Update operation failed: {e}")
            raise

    async def delete(self, table: str, filters: Dict[str, Any]) -> Dict[str, Any]:
        """Delete data from a table"""
        try:
            client = self.get_client()
            query = client.table(table).delete()

            for key, value in filters.items():
                query = query.eq(key, value)

            result = query.execute()
            return result
        except Exception as e:
            logger.error(f"Delete operation failed: {e}")
            raise

    async def select(
        self,
        table: str,
        filters: Optional[Dict[str, Any]] = None,
        columns: Optional[List[str]] = None,
        limit: Optional[int] = None,
    ) -> Dict[str, Any]:
        """Select data from a table"""
        try:
            client = self.get_client()
            query = client.table(table)

            if columns:
                query = query.select(*columns)

            if filters:
                for key, value in filters.items():
                    query = query.eq(key, value)

            if limit:
                query = query.limit(limit)

            result = query.execute()
            return result
        except Exception as e:
            logger.error(f"Select operation failed: {e}")
            raise

    async def health_check(self) -> Dict[str, Any]:
        """Check Supabase connection health"""
        try:
            client = self.get_client()
            result = client.table("users").select("id").limit(1).execute()
            return {
                "status": "healthy",
                "message": "Supabase connection is working",
                "timestamp": "2024-01-01T00:00:00Z",
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "message": f"Supabase connection failed: {str(e)}",
                "timestamp": "2024-01-01T00:00:00Z",
            }


_supabase_client: Optional[SupabaseClient] = None


def get_supabase() -> SupabaseClient:
    """Get Supabase client instance"""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = SupabaseClient()
    return _supabase_client


def get_service_supabase() -> Client:
    """Get Supabase client with service role key"""
    return get_supabase().get_service_client()
