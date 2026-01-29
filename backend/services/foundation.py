"""
Foundation service for business logic operations
Handles foundation-related business logic and validation
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from .core.models import User
from .core.supabase_mgr import get_supabase_client
from db.campaigns import CampaignRepository
from db.foundations import FoundationRepository
from db.icps import ICPRepository
from db.messaging import MessagingRepository
from db.moves import MoveRepository
from .redis_core.cache import cached
from schemas import RICP, MessagingStrategy
from .services.business_context_generator import get_business_context_generator


class FoundationService:
    """Service for foundation business logic"""

    def __init__(self):
        self.repository = FoundationRepository()
        self.icp_repository = ICPRepository()
        self.messaging_repository = MessagingRepository()
        self.supabase = get_supabase_client()

    @cached(ttl=3600, cache_type="foundation")
    async def get_foundation(
        self, workspace_id: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get foundation for workspace

        Args:
            workspace_id: Workspace ID

        Returns:
            Foundation data or None if not found
        """
        return await self.repository.get_by_workspace(workspace_id)

    @cached(ttl=3600, cache_type="foundation")
    async def get_foundation_with_metrics(
        self, workspace_id: str = None
    ) -> Optional[Dict[str, Any]]:
        """
        Get foundation with additional metrics and RICPs

        Args:
            workspace_id: Workspace ID

        Returns:
            Foundation data with metrics and RICPs
        """
        foundation = await self.get_foundation(workspace_id)
        if not foundation:
            return None

        # Get RICPs/ICPs
        icp_data = await self.icp_repository.list_by_workspace(workspace_id)
        ricps = []
        for item in icp_data:
            # Map database item back to RICP schema
            market_soph = item.get("market_sophistication", {})
            if isinstance(market_soph, dict):
                stage = market_soph.get("stage", 3)
            else:
                stage = 3

            ricps.append(
                RICP(
                    id=str(item.get("id")),
                    name=item.get("name", "Unknown"),
                    persona_name=item.get("persona_name"),
                    avatar=item.get("avatar", "=ƒæñ"),
                    demographics=item.get("demographics", {}),
                    psychographics=item.get("psychographics", {}),
                    market_sophistication=stage,
                    confidence=item.get("confidence", 0),
                    created_at=item.get("created_at"),
                    updated_at=item.get("updated_at"),
                )
            )

        foundation["ricps"] = ricps
        foundation["icp_count"] = len(ricps)

        # Get Messaging Strategy
        msg_data = await self.messaging_repository.get_by_workspace(workspace_id)
        if msg_data:
            foundation["messaging"] = MessagingStrategy(**msg_data)
        else:
            foundation["messaging"] = None

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

    async def update_foundation(
        self, workspace_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Updates foundation data for a workspace.

        Args:
            workspace_id: Workspace ID
            data: Foundation data to update

        Returns:
            Updated foundation data
        """
        # Validate data
        await self.validate_foundation_data(data)

        # Update in repository
        result = await self.repository.upsert(workspace_id, data)

        # Invalidate Cache
        from redis_core.cache import CacheService

        cache = CacheService()

        # 1. Clear Foundation Cache
        await cache.delete(workspace_id, "get_foundation")
        await cache.delete(workspace_id, "get_foundation_with_metrics")

        # 2. Clear Dependent Caches (ICPs, Moves, Campaigns, AI results)
        # We clear the whole workspace cache because Foundation is the root source of truth
        await cache.clear_workspace(workspace_id)

        return result

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
