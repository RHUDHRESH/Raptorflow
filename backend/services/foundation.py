"""
Foundation service for business logic operations
Handles foundation-related business logic and validation
"""

from datetime import datetime
from typing import Any, Dict, Optional

from ..core.models import ValidationError
from ..core.supabase import get_supabase_client
from ..db.foundations import FoundationRepository


class FoundationService:
    """Service for foundation business logic"""

    def __init__(self):
        self.repository = FoundationRepository()
        self.supabase = get_supabase_client()

    async def get_foundation(self, workspace_id: str) -> Optional[Dict[str, Any]]:
        """
        Get foundation for workspace

        Args:
            workspace_id: Workspace ID

        Returns:
            Foundation data or None if not found
        """
        return await self.repository.get_by_workspace(workspace_id)

    async def update_foundation(
        self, workspace_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Update foundation with validation

        Args:
            workspace_id: Workspace ID
            data: Foundation data to update

        Returns:
            Updated foundation data
        """
        # Validate required fields
        if not data.get("company_name"):
            raise ValidationError("Company name is required")

        # Validate industry if provided
        valid_industries = [
            "technology",
            "healthcare",
            "finance",
            "retail",
            "manufacturing",
            "education",
            "government",
            "nonprofit",
            "consulting",
            "other",
        ]
        if "industry" in data and data["industry"] not in valid_industries:
            raise ValidationError(f"Invalid industry: {data['industry']}")

        # Validate company stage if provided
        valid_stages = ["startup", "growth", "mature", "enterprise"]
        if "company_stage" in data and data["company_stage"] not in valid_stages:
            raise ValidationError(f"Invalid company stage: {data['company_stage']}")

        return await self.repository.upsert(workspace_id, data)

    async def generate_summary(self, workspace_id: str) -> Optional[str]:
        """
        Generate AI-powered summary for foundation

        Args:
            workspace_id: Workspace ID

        Returns:
            Generated summary or None if failed
        """
        foundation = await self.get_foundation(workspace_id)
        if not foundation:
            return None

        # For now, create a simple summary
        # In a real implementation, this would call an AI service
        company_name = foundation.get("company_name", "Unknown Company")
        industry = foundation.get("industry", "Unknown Industry")
        mission = foundation.get("mission", "")

        summary = f"{company_name} is a {industry} company"
        if mission:
            summary += f" focused on {mission.lower()}"

        # Update foundation with summary
        await self.update_foundation(workspace_id, {"summary": summary})

        return summary

    async def get_foundation_with_metrics(
        self, workspace_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get foundation with additional metrics

        Args:
            workspace_id: Workspace ID

        Returns:
            Foundation data with metrics
        """
        foundation = await self.get_foundation(workspace_id)
        if not foundation:
            return None

        # Get related metrics
        icp_count = (
            await self.supabase.table("icp_profiles")
            .select("id", count="exact")
            .eq("workspace_id", workspace_id)
            .execute()
        )
        foundation["icp_count"] = icp_count.count if icp_count.count else 0

        move_count = (
            await self.supabase.table("moves")
            .select("id", count="exact")
            .eq("workspace_id", workspace_id)
            .execute()
        )
        foundation["move_count"] = move_count.count if move_count.count else 0

        campaign_count = (
            await self.supabase.table("campaigns")
            .select("id", count="exact")
            .eq("workspace_id", workspace_id)
            .execute()
        )
        foundation["campaign_count"] = (
            campaign_count.count if campaign_count.count else 0
        )

        return foundation

    async def validate_foundation_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate foundation data before saving

        Args:
            data: Foundation data to validate

        Returns:
            True if valid, raises ValidationError if invalid
        """
        # Required fields
        required_fields = ["company_name"]
        for field in required_fields:
            if not data.get(field):
                raise ValidationError(f"Required field missing: {field}")

        # Validate company name length
        if len(data["company_name"]) > 100:
            raise ValidationError("Company name too long (max 100 characters)")

        # Validate mission length if provided
        if "mission" in data and len(data["mission"]) > 500:
            raise ValidationError("Mission too long (max 500 characters)")

        # Validate vision length if provided
        if "vision" in data and len(data["vision"]) > 500:
            raise ValidationError("Vision too long (max 500 characters)")

        # Validate JSON fields
        json_fields = ["values", "messaging_guardrails"]
        for field in json_fields:
            if field in data and not isinstance(data[field], list):
                raise ValidationError(f"{field} must be a list")

        return True

    async def delete_foundation(self, workspace_id: str) -> bool:
        """
        Delete foundation for workspace

        Args:
            workspace_id: Workspace ID

        Returns:
            True if deleted, False otherwise
        """
        return await self.repository.delete(workspace_id)

    async def export_foundation(
        self, workspace_id: str, format: str = "json"
    ) -> Dict[str, Any]:
        """
        Export foundation data in specified format

        Args:
            workspace_id: Workspace ID
            format: Export format (json, csv, etc.)

        Returns:
            Exported data
        """
        foundation = await self.get_foundation_with_metrics(workspace_id)
        if not foundation:
            raise ValidationError("Foundation not found")

        if format == "json":
            return foundation
        elif format == "csv":
            # Convert to CSV format
            # For now, return JSON as placeholder
            return foundation
        else:
            raise ValidationError(f"Unsupported export format: {format}")

    async def import_foundation(
        self, workspace_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Import foundation data with validation

        Args:
            workspace_id: Workspace ID
            data: Foundation data to import

        Returns:
            Imported foundation data
        """
        # Validate data
        await self.validate_foundation_data(data)

        # Import data
        return await self.update_foundation(workspace_id, data)
