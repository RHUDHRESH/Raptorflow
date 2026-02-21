"""
Infrastructure - Supabase Async Adapter.

Async adapter for Supabase database operations.
This replaces the synchronous client to avoid blocking the event loop.
"""

from typing import Optional, Dict, Any, List
from supabase import AsyncClient, create_client as create_async_client
import os


class SupabaseAsyncAdapter:
    """
    Async Supabase client adapter.

    This adapter provides async access to Supabase, avoiding
    the event loop blocking issues with the synchronous client.
    """

    def __init__(
        self,
        url: Optional[str] = None,
        key: Optional[str] = None,
    ):
        self._url = (
            url
            or os.getenv("SUPABASE_URL")
            or os.getenv("NEXT_PUBLIC_SUPABASE_URL")
            or ""
        )
        self._key = (
            key
            or os.getenv("SUPABASE_SERVICE_ROLE_KEY")
            or os.getenv("SUPABASE_ANON_KEY")
            or ""
        )
        self._client: Optional[AsyncClient] = None

    async def get_client(self) -> AsyncClient:
        """Get or create the async client."""
        if self._client is None:
            if not self._url or not self._key:
                raise ValueError(
                    "Supabase credentials not configured. "
                    "Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY."
                )
            self._client = create_async_client(self._url, self._key)
        return self._client

    async def table(self, table_name: str):
        """Get a table reference."""
        client = await self.get_client()
        return client.table(table_name)

    async def execute(self, query: Any) -> Dict[str, Any]:
        """Execute a query."""
        client = await self.get_client()
        return await query.execute()

    async def insert(
        self,
        table: str,
        data: Dict[str, Any],
        returning: str = "representation",
    ) -> Dict[str, Any]:
        """Insert data into a table."""
        client = await self.get_client()
        return await client.table(table).insert(data).execute()

    async def select(
        self,
        table: str,
        columns: str = "*",
        filters: Optional[Dict[str, Any]] = None,
        order: Optional[Dict[str, Any]] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[Dict[str, Any]]:
        """Select data from a table."""
        client = await self.get_client()
        query = client.table(table).select(columns)

        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)

        if order:
            query = query.order(order["column"], desc=order.get("desc", False))

        if limit:
            query = query.limit(limit)

        if offset:
            query = query.offset(offset)

        result = await query.execute()
        return result.data

    async def update(
        self,
        table: str,
        data: Dict[str, Any],
        filters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Update data in a table."""
        client = await self.get_client()
        query = client.table(table).update(data)

        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)

        return await query.execute()

    async def delete(
        self,
        table: str,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Delete data from a table."""
        client = await self.get_client()
        query = client.table(table).delete()

        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)

        return await query.execute()

    async def rpc(
        self,
        function_name: str,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Call a Supabase RPC function."""
        client = await self.get_client()
        return await client.rpc(function_name, params or {})


# Global instance
_supabase_async: Optional[SupabaseAsyncAdapter] = None


async def get_supabase_async() -> SupabaseAsyncAdapter:
    """Get the global Supabase async adapter."""
    global _supabase_async
    if _supabase_async is None:
        _supabase_async = SupabaseAsyncAdapter()
    return _supabase_async
