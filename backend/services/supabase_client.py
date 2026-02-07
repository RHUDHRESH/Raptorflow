"""
Supabase Client Configuration
Handles Supabase database connections and operations
"""

import logging
import os
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel

from supabase import Client, create_client

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
        self._initialize_client()

    def _load_config(self) -> SupabaseConfig:
        """Load Supabase configuration from environment variables"""
        return SupabaseConfig(
            url=os.getenv("NEXT_PUBLIC_SUPABASE_URL", ""),
            anon_key=os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY", ""),
            service_role_key=os.getenv("SUPABASE_SERVICE_ROLE_KEY", ""),
            pool_min=int(os.getenv("DATABASE_POOL_MIN", "2")),
            pool_max=int(os.getenv("DATABASE_POOL_MAX", "10")),
            pool_idle_timeout=int(os.getenv("DATABASE_POOL_IDLE_TIMEOUT", "30000")),
        )

    def _initialize_client(self):
        """Initialize Supabase client"""
        try:
            self._client = create_client(self.config.url, self.config.anon_key)
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
            return create_client(self.config.url, self.config.service_role_key)
        except Exception as e:
            logger.error(f"Failed to create service client: {e}")
            raise

    async def execute_query(
        self, query: str, params: Optional[Union[Dict[str, Any], List[Any]]] = None
    ) -> Any:
        """Execute a SQL query with error handling."""
        try:
            client = self.get_client()
            result = client.rpc(
                "execute_sql",
                {"query": query, "params": params if params is not None else {}},
            ).execute()
            return result
        except Exception as e:
            logger.error(f"Query execution failed: {e}")
            raise

    async def execute(
        self, query: str, params: Optional[Union[List[Any], Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """Execute SQL and return row data list."""
        result = await self.execute_query(query, params=params)
        data = getattr(result, "data", None)
        if data is None and isinstance(result, dict):
            data = result.get("data")
        return data or []

    async def insert_data(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert data into a table"""
        try:
            client = self.get_client()
            result = client.table(table).insert(data).execute()
            return result
        except Exception as e:
            logger.error(f"Insert operation failed: {e}")
            raise

    async def update_data(
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

    async def delete_data(self, table: str, filters: Dict[str, Any]) -> Dict[str, Any]:
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

    async def select_data(
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
            # Simple health check - try to execute a basic query
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

    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID"""
        try:
            result = await self.select_data("users", {"id": user_id})
            if result.get("data") and len(result["data"]) > 0:
                return result["data"][0]
            return None
        except Exception as e:
            logger.error(f"Failed to get user by ID: {e}")
            return None

    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user"""
        try:
            result = await self.insert_data("users", user_data)
            return result
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise

    async def update_user(
        self, user_id: str, user_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update user data"""
        try:
            result = await self.update_data("users", user_data, {"id": user_id})
            return result
        except Exception as e:
            logger.error(f"Failed to update user: {e}")
            raise

    async def delete_user(self, user_id: str) -> Dict[str, Any]:
        """Delete user"""
        try:
            result = await self.delete_data("users", {"id": user_id})
            return result
        except Exception as e:
            logger.error(f"Failed to delete user: {e}")
            raise

    async def get_workspace_by_id(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        """Get workspace by ID"""
        try:
            result = await self.select_data("workspaces", {"id": workspace_id})
            if result.get("data") and len(result["data"]) > 0:
                return result["data"][0]
            return None
        except Exception as e:
            logger.error(f"Failed to get workspace by ID: {e}")
            return None

    async def create_workspace(self, workspace_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new workspace"""
        try:
            result = await self.insert_data("workspaces", workspace_data)
            return result
        except Exception as e:
            logger.error(f"Failed to create workspace: {e}")
            raise

    async def update_workspace(
        self, workspace_id: str, workspace_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Update workspace data"""
        try:
            result = await self.update_data(
                "workspaces", workspace_data, {"id": workspace_id}
            )
            return result
        except Exception as e:
            logger.error(f"Failed to update workspace: {e}")
            raise

    async def delete_workspace(self, workspace_id: str) -> Dict[str, Any]:
        """Delete workspace"""
        try:
            result = await self.delete_data("workspaces", {"id": workspace_id})
            return result
        except Exception as e:
            logger.error(f"Failed to delete workspace: {e}")
            raise

    async def get_user_workspaces(self, user_id: str) -> List[Dict[str, Any]]:
        """Get all workspaces for a user"""
        try:
            result = await self.select_data("workspaces", {"owner_id": user_id})
            return result.get("data", [])
        except Exception as e:
            logger.error(f"Failed to get user workspaces: {e}")
            return []

    async def get_workspace_users(self, workspace_id: str) -> List[Dict[str, Any]]:
        """Get all users in a workspace"""
        try:
            result = await self.select_data(
                "workspace_users", {"workspace_id": workspace_id}
            )
            return result.get("data", [])
        except Exception as e:
            logger.error(f"Failed to get workspace users: {e}")
            return []

    async def add_user_to_workspace(
        self, workspace_id: str, user_id: str, role: str = "member"
    ) -> Dict[str, Any]:
        """Add user to workspace"""
        try:
            data = {
                "workspace_id": workspace_id,
                "user_id": user_id,
                "role": role,
                "created_at": "2024-01-01T00:00:00Z",
            }
            result = await self.insert_data("workspace_users", data)
            return result
        except Exception as e:
            logger.error(f"Failed to add user to workspace: {e}")
            raise

    async def remove_user_from_workspace(
        self, workspace_id: str, user_id: str
    ) -> Dict[str, Any]:
        """Remove user from workspace"""
        try:
            result = await self.delete_data(
                "workspace_users", {"workspace_id": workspace_id, "user_id": user_id}
            )
            return result
        except Exception as e:
            logger.error(f"Failed to remove user from workspace: {e}")
            raise


# Global instance
supabase_client = SupabaseClient()


def get_supabase_client() -> SupabaseClient:
    """Get Supabase client instance"""
    return supabase_client


def get_service_supabase_client() -> Client:
    """Get Supabase client with service role key"""
    return supabase_client.get_service_client()


def get_supabase_admin() -> Client:
    """Backwards-compatible alias for a service-role Supabase client."""
    return get_service_supabase_client()
