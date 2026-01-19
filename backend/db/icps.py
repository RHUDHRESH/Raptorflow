"""
ICP (Ideal Customer Profile) repository for database operations
Handles CRUD operations for ICP data
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from backend.core.models import ValidationError
from backend.core.supabase_mgr import get_supabase_client
from .base import Repository


class ICPRepository(Repository):
    """Repository for ICP operations"""

    def __init__(self):
        super().__init__("icp_profiles")

    def _map_to_model(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Map database record to dict (matching legacy expectations for now)."""
        return data

    async def list_by_workspace(
        self, workspace_id: str, filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        List all ICPs for workspace with optional filters

        Args:
            workspace_id: Workspace ID
            filters: Optional filters to apply

        Returns:
            List of ICP data
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
                    if field == "is_primary":
                        query = query.eq(field, value)
                    elif field == "market_sophistication":
                        query = query.eq(field, value)
                    elif field == "fit_score_min":
                        query = query.gte("fit_score", value)
                    elif field == "fit_score_max":
                        query = query.lte("fit_score", value)

            result = await query.execute()
            return result.data

        except Exception as e:
            raise ValidationError(f"Failed to list ICPs: {e}")

    async def get_primary(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        """
        Get primary ICP for workspace

        Args:
            workspace_id: Workspace ID

        Returns:
            Primary ICP data or None if not found
        """
        try:
            result = (
                await self.client.table(self.table_name)
                .select("*")
                .eq("workspace_id", workspace_id)
                .eq("is_primary", True)
                .single()
                .execute()
            )

            if not result.data:
                return None

            return result.data

        except Exception as e:
            raise ValidationError(f"Failed to get primary ICP: {e}")

    async def set_primary(self, workspace_id: str, icp_id: str) -> bool:
        """
        Set ICP as primary for workspace

        Args:
            workspace_id: Workspace ID
            icp_id: ICP ID

        Returns:
            True if successful, False otherwise
        """
        try:
            # First, unset all primary ICPs for this workspace
            await self.client.table(self.table_name).update({"is_primary": False}).eq(
                "workspace_id", workspace_id
            ).execute()

            # Then set the new primary
            result = (
                await self.client.table(self.table_name)
                .update({"is_primary": True})
                .eq("id", icp_id)
                .eq("workspace_id", workspace_id)
                .execute()
            )

            return len(result.data) > 0

        except Exception as e:
            raise ValidationError(f"Failed to set primary ICP: {e}")

    async def count_by_workspace(self, workspace_id: str) -> int:
        """
        Count ICPs for workspace

        Args:
            workspace_id: Workspace ID

        Returns:
            Number of ICPs
        """
        try:
            result = (
                await self.client.table(self.table_name)
                .select("id", count="exact")
                .eq("workspace_id", workspace_id)
                .execute()
            )
            return result.count if result.count else 0

        except Exception as e:
            raise ValidationError(f"Failed to count ICPs: {e}")

    async def create(self, workspace_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create new ICP for workspace

        Args:
            workspace_id: Workspace ID
            data: ICP data

        Returns:
            Created ICP data
        """
        try:
            icp_data = {
                "workspace_id": workspace_id,
                **data,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }

            # If this is the first ICP, make it primary
            count = await self.count_by_workspace(workspace_id)
            if count == 0:
                icp_data["is_primary"] = True
            else:
                icp_data["is_primary"] = data.get("is_primary", False)

            result = await self.client.table(self.table_name).insert(icp_data).execute()
            return result.data[0] if result.data else icp_data

        except Exception as e:
            raise ValidationError(f"Failed to create ICP: {e}")

    async def update(
        self, icp_id: str, workspace_id: str, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update ICP

        Args:
            icp_id: ICP ID
            workspace_id: Workspace ID (for security)
            data: Update data

        Returns:
            Updated ICP data or None if not found
        """
        try:
            update_data = {**data, "updated_at": datetime.utcnow().isoformat()}

            result = (
                await self.client.table(self.table_name)
                .update(update_data)
                .eq("id", icp_id)
                .eq("workspace_id", workspace_id)
                .execute()
            )

            if not result.data:
                return None

            return result.data[0]

        except Exception as e:
            raise ValidationError(f"Failed to update ICP: {e}")

    async def delete(self, icp_id: str, workspace_id: str) -> bool:
        """
        Delete ICP

        Args:
            icp_id: ICP ID
            workspace_id: Workspace ID (for security)

        Returns:
            True if deleted, False otherwise
        """
        try:
            result = (
                await self.client.table(self.table_name)
                .delete()
                .eq("id", icp_id)
                .eq("workspace_id", workspace_id)
                .execute()
            )
            return len(result.data) > 0

        except Exception as e:
            raise ValidationError(f"Failed to delete ICP: {e}")

    async def get_by_id(
        self, icp_id: str, workspace_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get ICP by ID

        Args:
            icp_id: ICP ID
            workspace_id: Workspace ID (for security)

        Returns:
            ICP data or None if not found
        """
        try:
            result = (
                await self.client.table(self.table_name)
                .select("*")
                .eq("id", icp_id)
                .eq("workspace_id", workspace_id)
                .single()
                .execute()
            )

            if not result.data:
                return None

            return result.data

        except Exception as e:
            raise ValidationError(f"Failed to get ICP: {e}")

    async def generate_from_foundation(self, workspace_id: str) -> List[Dict[str, Any]]:
        """
        Generate ICPs from foundation data

        Args:
            workspace_id: Workspace ID

        Returns:
            List of generated ICPs
        """
        try:
            # Get foundation data
            foundation_result = (
                await self.client.table("foundations")
                .select("*")
                .eq("workspace_id", workspace_id)
                .single()
                .execute()
            )

            if not foundation_result.data:
                return []

            foundation = foundation_result.data

            # Generate sample ICPs based on foundation
            # In a real implementation, this would use AI to generate ICPs
            generated_icps = []

            # Sample ICP 1
            icp1 = {
                "name": f"{foundation.get('company_name', 'Company')} - Primary Market",
                "tagline": "Primary target customer segment",
                "market_sophistication": 3,
                "demographics": {
                    "company_size": "50-200 employees",
                    "industry": foundation.get("industry", "Unknown"),
                    "revenue": "$10M-$50M",
                },
                "psychographics": {
                    "values": ["efficiency", "growth", "innovation"],
                    "pain_points": ["manual processes", "scalability issues"],
                    "goals": ["streamline operations", "increase revenue"],
                },
                "behaviors": {
                    "decision_process": "data-driven",
                    "tech_adoption": "early adopter",
                    "budget_cycle": "quarterly",
                },
                "pain_points": ["operational inefficiency", "limited resources"],
                "goals": ["business growth", "competitive advantage"],
                "fit_score": 85,
                "summary": f"Primary ICP for {foundation.get('company_name', 'Company')}",
            }

            # Sample ICP 2
            icp2 = {
                "name": f"{foundation.get('company_name', 'Company')} - Secondary Market",
                "tagline": "Secondary target customer segment",
                "market_sophistication": 2,
                "demographics": {
                    "company_size": "10-50 employees",
                    "industry": foundation.get("industry", "Unknown"),
                    "revenue": "$1M-$10M",
                },
                "psychographics": {
                    "values": ["cost-effectiveness", "simplicity", "reliability"],
                    "pain_points": ["budget constraints", "technical complexity"],
                    "goals": ["reduce costs", "simplify operations"],
                },
                "behaviors": {
                    "decision_process": "relationship-driven",
                    "tech_adoption": "mainstream",
                    "budget_cycle": "annual",
                },
                "pain_points": ["limited budget", "technical expertise"],
                "goals": ["affordable solutions", "easy implementation"],
                "fit_score": 75,
                "summary": f"Secondary ICP for {foundation.get('company_name', 'Company')}",
            }

            # Create generated ICPs
            for icp_data in [icp1, icp2]:
                created_icp = await self.create(workspace_id, icp_data)
                if created_icp:
                    generated_icps.append(created_icp)

            return generated_icps

        except Exception as e:
            raise ValidationError(f"Failed to generate ICPs from foundation: {e}")
