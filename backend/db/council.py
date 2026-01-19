"""
Expert Council Repository
Handles database persistence for council sessions and reports.
"""

from typing import Any, Dict, List, Optional
from backend.db.base import Repository
from backend.core.supabase_mgr import get_supabase_client

class CouncilRepository(Repository):
    """Repository for Expert Council operations"""

    def __init__(self):
        super().__init__("council_sessions")

    def _map_to_model(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Map database record to dict."""
        return data

    async def create_session(self, workspace_id: str, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new session record."""
        session_data["workspace_id"] = workspace_id
        result = (
            self._get_supabase_client()
            .table(self.table_name)
            .insert(session_data)
            .execute()
        )
        return result.data[0] if result.data else {}

    async def list_by_workspace(self, workspace_id: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve recent sessions for a workspace."""
        result = (
            self._get_supabase_client()
            .table(self.table_name)
            .select("*")
            .eq("workspace_id", workspace_id)
            .order("created_at", descending=True)
            .limit(limit)
            .execute()
        )
        return result.data or []

    async def get_by_id(self, session_id: str, workspace_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific session."""
        try:
            result = (
                self._get_supabase_client()
                .table(self.table_name)
                .select("*")
                .eq("id", session_id)
                .eq("workspace_id", workspace_id)
                .single()
                .execute()
            )
            return result.data
        except Exception:
            return None
