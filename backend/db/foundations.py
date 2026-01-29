"""
Foundation repository for database operations
Handles CRUD operations for foundation data
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from db.base import Repository

from .core.models import ValidationError
from .core.supabase_mgr import get_supabase_client


class FoundationRepository(Repository):
    """Repository for foundation operations"""

    def __init__(self):
        super().__init__("foundations")

    def _map_to_model(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Map database record to dict."""
        return data

    async def get_by_workspace(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        """
        Get foundation by workspace ID

        Args:
            workspace_id: Workspace ID

        Returns:
            Foundation data or None if not found
        """
        try:
            result = (
                await self.client.table(self.table_name)
                .select("*")
                .eq("workspace_id", workspace_id)
                .single()
                .execute()
            )

            if not result.data:
                return None

            return result.data

        except Exception as e:
            raise ValidationError(f"Failed to get foundation: {e}")

    async def upsert(self, workspace_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create or update foundation for workspace

        Args:
            workspace_id: Workspace ID
            data: Foundation data

        Returns:
            Created/updated foundation data
        """
        try:
            # Check if foundation exists
            existing = await self.get_by_workspace(workspace_id)

            foundation_data = {
                "workspace_id": workspace_id,
                **data,
                "updated_at": datetime.utcnow().isoformat(),
            }

            if existing:
                # Update existing foundation
                result = (
                    await self.client.table(self.table_name)
                    .update(foundation_data)
                    .eq("workspace_id", workspace_id)
                    .execute()
                )
                return result.data[0] if result.data else foundation_data
            else:
                # Create new foundation
                foundation_data["created_at"] = datetime.utcnow().isoformat()
                result = (
                    await self.client.table(self.table_name)
                    .insert(foundation_data)
                    .execute()
                )
                return result.data[0] if result.data else foundation_data

        except Exception as e:
            raise ValidationError(f"Failed to upsert foundation: {e}")

    async def delete(self, workspace_id: str) -> bool:
        """
        Delete foundation for workspace

        Args:
            workspace_id: Workspace ID

        Returns:
            True if deleted, False otherwise
        """
        try:
            result = (
                await self.client.table(self.table_name)
                .delete()
                .eq("workspace_id", workspace_id)
                .execute()
            )
            return len(result.data) > 0
        except Exception as e:
            raise ValidationError(f"Failed to delete foundation: {e}")

    async def list_all(
        self, workspace_id: str, filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        List all foundations for workspace with optional filters

        Args:
            workspace_id: Workspace ID
            filters: Optional filters to apply

        Returns:
            List of foundation data
        """
        try:
            query = (
                self.client.table(self.table_name)
                .select("*")
                .eq("workspace_id", workspace_id)
            )

            # Apply filters if provided
            if filters:
                for field, value in filters.items():
                    if field == "industry":
                        query = query.eq(field, value)
                    elif field == "company_stage":
                        query = query.eq(field, value)
                    # Add more filter types as needed

            result = await query.execute()
            return result.data

        except Exception as e:
            raise ValidationError(f"Failed to list foundations: {e}")

    async def generate_summary(self, workspace_id: str) -> Optional[str]:
        """
        Generate AI-powered summary for foundation

        Args:
            workspace_id: Workspace ID

        Returns:
            Generated summary or None if failed
        """
        try:
            foundation = await self.get_by_workspace(workspace_id)
            if not foundation:
                return None

            # For now, return a simple summary
            # In a real implementation, this would call an AI service
            summary = f"Foundation for {foundation.get('company_name', 'Unknown Company')} in {foundation.get('industry', 'Unknown Industry')}."

            # Update foundation with summary
            await self.upsert(workspace_id, {"summary": summary})

            return summary

        except Exception as e:
            raise ValidationError(f"Failed to generate summary: {e}")

    async def get_with_related_data(
        self, workspace_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get foundation with related ICPs and recent moves

        Args:
            workspace_id: Workspace ID

        Returns:
            Foundation data with related information
        """
        try:
            foundation = await self.get_by_workspace(workspace_id)
            if not foundation:
                return None

            # Get related ICPs
            icps_result = (
                await self.client.table("icp_profiles")
                .select("*")
                .eq("workspace_id", workspace_id)
                .execute()
            )
            icps = icps_result.data if icps_result.data else []

            # Get recent moves
            moves_result = (
                await self.client.table("moves")
                .select("*")
                .eq("workspace_id", workspace_id)
                .order("created_at", desc=True)
                .limit(5)
                .execute()
            )
            moves = moves_result.data if moves_result.data else []

            foundation["icps"] = icps
            foundation["recent_moves"] = moves

            return foundation

        except Exception as e:
            raise ValidationError(f"Failed to get foundation with related data: {e}")
