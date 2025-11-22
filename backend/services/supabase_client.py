"""
Supabase client for database operations
"""

from typing import Any, Dict, List, Optional
from supabase import create_client, Client
from config.settings import settings
import structlog

logger = structlog.get_logger()


class SupabaseClient:
    """Async Supabase client for database operations"""
    
    def __init__(self):
        self.client: Optional[Client] = None
        
    def connect(self):
        """Initialize Supabase client"""
        try:
            self.client = create_client(
                settings.SUPABASE_URL,
                settings.SUPABASE_SERVICE_KEY  # Service role key for backend
            )
            logger.info("Supabase client connected")
        except Exception as e:
            logger.error("Failed to connect to Supabase", error=str(e))
            raise
    
    # === COHORTS (ICPs) === #
    
    async def create_cohort(self, cohort_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new ICP/cohort"""
        result = self.client.table("cohorts").insert(cohort_data).execute()
        return result.data[0] if result.data else {}
    
    async def get_cohort(self, cohort_id: str) -> Optional[Dict[str, Any]]:
        """Get cohort by ID"""
        result = self.client.table("cohorts").select("*").eq("id", cohort_id).execute()
        return result.data[0] if result.data else None
    
    async def list_cohorts(self, workspace_id: str) -> List[Dict[str, Any]]:
        """List all cohorts for a workspace"""
        result = self.client.table("cohorts").select("*").eq("workspace_id", workspace_id).execute()
        return result.data or []
    
    async def update_cohort(self, cohort_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update cohort"""
        result = self.client.table("cohorts").update(updates).eq("id", cohort_id).execute()
        return result.data[0] if result.data else {}
    
    async def delete_cohort(self, cohort_id: str) -> bool:
        """Delete cohort"""
        self.client.table("cohorts").delete().eq("id", cohort_id).execute()
        return True
    
    # === MOVES (CAMPAIGNS) === #
    
    async def create_move(self, move_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new move/campaign"""
        result = self.client.table("moves").insert(move_data).execute()
        return result.data[0] if result.data else {}
    
    async def get_move(self, move_id: str) -> Optional[Dict[str, Any]]:
        """Get move by ID"""
        result = self.client.table("moves").select("*").eq("id", move_id).execute()
        return result.data[0] if result.data else None
    
    async def list_moves(self, workspace_id: str) -> List[Dict[str, Any]]:
        """List all moves for a workspace"""
        result = self.client.table("moves").select("*").eq("workspace_id", workspace_id).execute()
        return result.data or []
    
    # === ASSETS === #
    
    async def create_asset(self, asset_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create content asset"""
        result = self.client.table("assets").insert(asset_data).execute()
        return result.data[0] if result.data else {}
    
    async def list_assets(self, workspace_id: str, asset_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """List assets, optionally filtered by type"""
        query = self.client.table("assets").select("*").eq("workspace_id", workspace_id)
        if asset_type:
            query = query.eq("asset_type", asset_type)
        result = query.execute()
        return result.data or []
    
    # === WORKSPACES === #
    
    async def get_workspace(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        """Get workspace by ID"""
        result = self.client.table("workspaces").select("*").eq("id", workspace_id).execute()
        return result.data[0] if result.data else None
    
    async def get_user_workspace(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get workspace for user"""
        result = self.client.table("user_workspaces").select("workspace_id").eq("user_id", user_id).limit(1).execute()
        if not result.data:
            return None
        workspace_id = result.data[0]["workspace_id"]
        return await self.get_workspace(workspace_id)
    
    # === QUICK WINS === #
    
    async def create_quick_win(self, quick_win_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create ambient search opportunity"""
        result = self.client.table("quick_wins").insert(quick_win_data).execute()
        return result.data[0] if result.data else {}
    
    async def list_quick_wins(self, workspace_id: str, status: str = "New") -> List[Dict[str, Any]]:
        """List quick wins by status"""
        result = self.client.table("quick_wins").select("*").eq("workspace_id", workspace_id).eq("status", status).execute()
        return result.data or []


# Global client instance
db = SupabaseClient()

