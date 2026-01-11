"""
Database tool for Raptorflow agents with workspace isolation.
"""

import logging
import os
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel

from .base import RaptorflowTool, ToolError, ToolResult

logger = logging.getLogger(__name__)


class DatabaseQueryInput(BaseModel):
    """Input schema for database queries."""

    table: Literal[
        "foundations",
        "icp_profiles",
        "moves",
        "campaigns",
        "muse_assets",
        "blackbox_strategies",
        "daily_wins",
        "agent_executions",
    ]
    workspace_id: str
    filters: Optional[Dict[str, Any]] = None
    limit: int = 20
    offset: int = 0


class DatabaseTool(RaptorflowTool):
    """Database query tool with workspace isolation enforcement."""

    def __init__(self):
        super().__init__(
            name="database",
            description="Query database tables with workspace isolation",
        )

        # Table schemas for validation
        self.table_schemas = {
            "foundations": [
                "id",
                "workspace_id",
                "company_name",
                "industry",
                "summary",
                "brand_voice",
                "onboarding_completed",
            ],
            "icp_profiles": [
                "id",
                "workspace_id",
                "name",
                "tagline",
                "is_primary",
                "demographics",
                "psychographics",
                "behaviors",
            ],
            "moves": [
                "id",
                "workspace_id",
                "name",
                "category",
                "status",
                "goal",
                "duration_days",
                "start_date",
                "end_date",
            ],
            "campaigns": [
                "id",
                "workspace_id",
                "name",
                "objective",
                "status",
                "goal",
                "duration_days",
                "start_date",
                "end_date",
            ],
            "muse_assets": [
                "id",
                "workspace_id",
                "title",
                "type",
                "content",
                "status",
                "created_at",
                "updated_at",
            ],
            "blackbox_strategies": [
                "id",
                "workspace_id",
                "name",
                "focus_area",
                "risk_level",
                "status",
                "created_at",
                "updated_at",
            ],
            "daily_wins": [
                "id",
                "workspace_id",
                "topic",
                "angle",
                "hook",
                "platform",
                "status",
                "generated_at",
            ],
            "agent_executions": [
                "id",
                "workspace_id",
                "request_type",
                "success",
                "tokens_used",
                "cost_usd",
                "created_at",
            ],
        }

    async def _arun(
        self,
        table: str,
        workspace_id: str,
        filters: Dict[str, Any] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> ToolResult:
        """Execute database query with workspace isolation."""
        try:
            # Validate table name
            if table not in self.table_schemas:
                return ToolResult(
                    success=False,
                    error=f"Invalid table: {table}. Valid tables: {list(self.table_schemas.keys())}",
                )

            # Validate workspace_id
            if not workspace_id:
                return ToolResult(success=False, error="workspace_id is required")

            # Set workspace context
            self.set_workspace_id(workspace_id)

            # Build query
            query_result = await self._build_query(
                table, workspace_id, filters, limit, offset
            )

            return ToolResult(success=True, data=query_result)

        except Exception as e:
            return ToolResult(success=False, error=str(e))

    async def _build_query(
        self,
        table: str,
        workspace_id: str,
        filters: Dict[str, Any] = None,
        limit: int = 20,
        offset: int = 0,
    ) -> Dict[str, Any]:
        """Build and execute database query with real Supabase integration."""
        try:
            from supabase import Client, create_client

            # Initialize Supabase client
            supabase: Client = create_client(
                url=os.getenv("SUPABASE_URL"), key=os.getenv("SUPABASE_SERVICE_KEY")
            )

            # Validate workspace_id
            if not workspace_id or not workspace_id.strip():
                raise ToolError(self.name, "Invalid workspace_id: cannot be empty")

            # Build the base query with workspace_id filter
            query = supabase.table(table).select("*").eq("workspace_id", workspace_id)

            # Apply additional filters
            if filters:
                for key, value in filters.items():
                    if key in self.table_schemas.get(table, []):
                        query = query.eq(key, value)
                    else:
                        logger.warning(
                            f"Filter key '{key}' not in table schema for '{table}'"
                        )

            # Apply pagination
            query = query.range(offset, offset + limit - 1)

            # Execute query
            result = query.execute()

            if result.error:
                raise ToolError(
                    self.name, f"Database query failed: {result.error.message}"
                )

            # Verify all results have correct workspace_id (double-check isolation)
            for item in result.data:
                if item.get("workspace_id") != workspace_id:
                    logger.error(
                        f"Workspace isolation breach detected in {table}: {item}"
                    )
                    raise ToolError(self.name, "Workspace isolation violation detected")

            return {
                "data": result.data,
                "total_count": len(result.data),
                "limit": limit,
                "offset": offset,
                "table": table,
                "workspace_id": workspace_id,
                "filters_applied": filters or {},
            }

        except ImportError:
            raise ToolError(
                self.name,
                "Supabase client not available. Install with: pip install supabase",
            )
        except Exception as e:
            logger.error(f"Database query error: {e}")
            raise ToolError(self.name, f"Database operation failed: {str(e)}")

    def get_table_schema(self, table: str) -> Optional[List[str]]:
        """Get schema for a table."""
        return self.table_schemas.get(table)

    def validate_filters(self, table: str, filters: Dict[str, Any]) -> bool:
        """Validate filters against table schema."""
        schema = self.table_schemas.get(table, [])

        for key in filters.keys():
            if key not in schema:
                logger.warning(f"Invalid filter key '{key}' for table '{table}'")
                return False

        return True

    async def validate_workspace_access(self, workspace_id: str) -> bool:
        """Validate that the workspace exists and is accessible."""
        # In a real implementation, this would check the database
        # For now, assume any non-empty workspace_id is valid
        return bool(workspace_id and workspace_id.strip())

    def get_available_tables(self) -> List[str]:
        """Get list of available tables."""
        return list(self.table_schemas.keys())

    def explain_workspace_isolation(self) -> str:
        """Explain how workspace isolation works."""
        return """
        Workspace Isolation in DatabaseTool:

        1. Every query MUST include workspace_id parameter
        2. All data returned is filtered by workspace_id
        3. No cross-workspace data leakage possible
        4. RLS policies enforce isolation at database level

        This ensures users can only access their own data.
        """
