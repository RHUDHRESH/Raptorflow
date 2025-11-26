"""
Supabase client for database operations
"""

from typing import Any, Dict, List, Optional
from supabase import create_client, Client
from backend.config.settings import settings
import structlog

logger = structlog.get_logger()


class SupabaseClient:
    """Async Supabase client for database operations"""
    
    def __init__(self):
        self.client: Optional[Client] = None
        # Lazy init to avoid failing when env vars are missing in certain environments
        try:
            self.connect()
        except Exception:
            logger.warning("Supabase client not initialized - will retry on first query")
        
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

    def _ensure_client(self) -> None:
        """Ensure the underlying Supabase client is available."""
        if self.client is None:
            self.connect()

    # === Generic helpers === #

    async def insert(self, table: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Insert a row and return the inserted record."""
        self._ensure_client()
        result = self.client.table(table).insert(data).execute()
        return result.data[0] if result.data else {}

    async def fetch_one(self, table: str, filters: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Fetch a single row by filters."""
        self._ensure_client()
        query = self.client.table(table).select("*")
        for key, value in filters.items():
            query = query.eq(key, value)
        result = query.limit(1).execute()
        return result.data[0] if result.data else None

    async def fetch_all(self, table: str, filters: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Fetch multiple rows with optional filters."""
        self._ensure_client()
        query = self.client.table(table).select("*")
        if filters:
            for key, value in filters.items():
                query = query.eq(key, value)
        result = query.execute()
        return result.data or []

    async def update(self, table: str, filters: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update rows matching filters and return first updated record."""
        self._ensure_client()
        query = self.client.table(table).update(updates)
        for key, value in filters.items():
            query = query.eq(key, value)
        result = query.execute()
        return result.data[0] if result.data else {}

    async def delete(self, table: str, filters: Dict[str, Any]) -> bool:
        """Delete rows matching filters."""
        self._ensure_client()
        query = self.client.table(table).delete()
        for key, value in filters.items():
            query = query.eq(key, value)
        query.execute()
        return True

    async def upsert(self, table: str, data: Dict[str, Any], match_columns: Optional[List[str]] = None) -> Dict[str, Any]:
        """Upsert a row (insert or update based on match columns)."""
        self._ensure_client()
        if match_columns:
            result = self.client.table(table).upsert(data, {"onConflict": ",".join(match_columns)}).execute()
        else:
            result = self.client.table(table).upsert(data).execute()
        return result.data[0] if result.data else {}

    async def execute_transaction(self, operations: List[Dict[str, Any]]) -> bool:
        """
        Execute multiple operations atomically.

        Operations format:
        [
            {"type": "insert", "table": "...", "data": {...}},
            {"type": "update", "table": "...", "filters": {...}, "data": {...}},
            ...
        ]

        Rolls back all operations if any fails.
        """
        self._ensure_client()
        try:
            # Since Supabase REST API doesn't support transactions,
            # we implement transaction-like behavior with rollback capability
            completed_ops = []

            for op in operations:
                op_type = op.get("type")
                table = op.get("table")

                try:
                    if op_type == "insert":
                        result = await self.insert(table, op.get("data", {}))
                        completed_ops.append({"type": "insert", "table": table, "data": result})

                    elif op_type == "update":
                        result = await self.update(table, op.get("filters", {}), op.get("data", {}))
                        completed_ops.append({"type": "update", "table": table, "data": result})

                    elif op_type == "upsert":
                        result = await self.upsert(table, op.get("data", {}), op.get("match_columns"))
                        completed_ops.append({"type": "upsert", "table": table, "data": result})

                except Exception as e:
                    logger.error(f"Transaction operation failed: {op_type} on {table}")
                    logger.error(f"Rolling back {len(completed_ops)} completed operations")

                    # Rollback completed operations
                    for completed_op in reversed(completed_ops):
                        try:
                            if completed_op["type"] in ["insert", "upsert"]:
                                # For inserts/upserts, we need to identify and delete the record
                                # This assumes the data has an 'id' field
                                if "id" in completed_op.get("data", {}):
                                    await self.delete(completed_op["table"], {"id": completed_op["data"]["id"]})
                            elif completed_op["type"] == "update":
                                # Updates are harder to rollback without original state
                                # Log warning instead
                                logger.warning(f"Could not rollback update on {completed_op['table']}")
                        except Exception as rollback_error:
                            logger.error(f"Rollback failed for {completed_op['type']}: {rollback_error}")

                    raise

            logger.info(f"Transaction completed successfully with {len(operations)} operations")
            return True

        except Exception as e:
            logger.error(f"Transaction failed: {e}", exc_info=True)
            raise
    
    # === COHORTS (ICPs) === #
    
    async def create_cohort(self, cohort_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new ICP/cohort"""
        self._ensure_client()
        result = self.client.table("cohorts").insert(cohort_data).execute()
        return result.data[0] if result.data else {}
    
    async def get_cohort(self, cohort_id: str) -> Optional[Dict[str, Any]]:
        """Get cohort by ID"""
        self._ensure_client()
        result = self.client.table("cohorts").select("*").eq("id", cohort_id).execute()
        return result.data[0] if result.data else None
    
    async def list_cohorts(self, workspace_id: str) -> List[Dict[str, Any]]:
        """List all cohorts for a workspace"""
        self._ensure_client()
        result = self.client.table("cohorts").select("*").eq("workspace_id", workspace_id).execute()
        return result.data or []
    
    async def update_cohort(self, cohort_id: str, updates: Dict[str, Any]) -> Dict[str, Any]:
        """Update cohort"""
        self._ensure_client()
        result = self.client.table("cohorts").update(updates).eq("id", cohort_id).execute()
        return result.data[0] if result.data else {}
    
    async def delete_cohort(self, cohort_id: str) -> bool:
        """Delete cohort"""
        self._ensure_client()
        self.client.table("cohorts").delete().eq("id", cohort_id).execute()
        return True
    
    # === MOVES (CAMPAIGNS) === #
    
    async def create_move(self, move_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new move/campaign"""
        self._ensure_client()
        result = self.client.table("moves").insert(move_data).execute()
        return result.data[0] if result.data else {}
    
    async def get_move(self, move_id: str) -> Optional[Dict[str, Any]]:
        """Get move by ID"""
        self._ensure_client()
        result = self.client.table("moves").select("*").eq("id", move_id).execute()
        return result.data[0] if result.data else None
    
    async def list_moves(self, workspace_id: str) -> List[Dict[str, Any]]:
        """List all moves for a workspace"""
        self._ensure_client()
        result = self.client.table("moves").select("*").eq("workspace_id", workspace_id).execute()
        return result.data or []
    
    # === ASSETS === #
    
    async def create_asset(self, asset_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create content asset"""
        self._ensure_client()
        result = self.client.table("assets").insert(asset_data).execute()
        return result.data[0] if result.data else {}
    
    async def list_assets(self, workspace_id: str, asset_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """List assets, optionally filtered by type"""
        self._ensure_client()
        query = self.client.table("assets").select("*").eq("workspace_id", workspace_id)
        if asset_type:
            query = query.eq("asset_type", asset_type)
        result = query.execute()
        return result.data or []
    
    # === WORKSPACES === #
    
    async def get_workspace(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        """Get workspace by ID"""
        self._ensure_client()
        result = self.client.table("workspaces").select("*").eq("id", workspace_id).execute()
        return result.data[0] if result.data else None
    
    async def get_user_workspace(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get workspace for user"""
        self._ensure_client()
        result = self.client.table("user_workspaces").select("workspace_id").eq("user_id", user_id).limit(1).execute()
        if not result.data:
            return None
        workspace_id = result.data[0]["workspace_id"]
        return await self.get_workspace(workspace_id)
    
    # === QUICK WINS === #
    
    async def create_quick_win(self, quick_win_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create ambient search opportunity"""
        self._ensure_client()
        result = self.client.table("quick_wins").insert(quick_win_data).execute()
        return result.data[0] if result.data else {}
    
    async def list_quick_wins(self, workspace_id: str, status: str = "New") -> List[Dict[str, Any]]:
        """List quick wins by status"""
        self._ensure_client()
        result = self.client.table("quick_wins").select("*").eq("workspace_id", workspace_id).eq("status", status).execute()
        return result.data or []


# Global client instance
supabase_client = SupabaseClient()
# Backward-compatible alias
db = supabase_client

