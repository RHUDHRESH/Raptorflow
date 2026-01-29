"""
Messaging Strategy repository for database operations
"""

from typing import Any, Dict, Optional
from db.base import Repository
from .core.supabase_mgr import get_supabase_client


class MessagingRepository(Repository):
    """Repository for messaging strategy operations"""

    def __init__(self):
        super().__init__("messaging_strategies")

    def _map_to_model(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Map database record to dict."""
        return data

    async def get_by_workspace(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        """Get strategy by workspace ID"""
        try:
            result = (
                self._get_supabase_client()
                .table(self.table_name)
                .select("*")
                .eq("workspace_id", workspace_id)
                .single()
                .execute()
            )
            return result.data
        except Exception:
            return None

    async def upsert(self, workspace_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create or update strategy"""
        existing = await self.get_by_workspace(workspace_id)

        if existing:
            result = (
                self._get_supabase_client()
                .table(self.table_name)
                .update(data)
                .eq("workspace_id", workspace_id)
                .execute()
            )
        else:
            data["workspace_id"] = workspace_id
            result = (
                self._get_supabase_client()
                .table(self.table_name)
                .insert(data)
                .execute()
            )

        return result.data[0] if result.data else data
