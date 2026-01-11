"""
Campaign service for business logic operations
Handles campaign-related business logic and validation
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from ..core.models import ValidationError
from ..core.supabase import get_supabase_client
from ..db.campaigns import CampaignRepository
from ..db.moves import MoveRepository


class CampaignService:
    """Service for campaign business logic"""

    def __init__(self):
        self.repository = CampaignRepository()
        self.move_repository = MoveRepository()
        self.supabase = get_supabase_client()

    async def create_campaign(
        self, workspace_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create new campaign with validation

        Args:
            workspace_id: Workspace ID
            data: Campaign data

        Returns:
            Created campaign data
        """
        # Validate required fields
        if not data.get("name"):
            raise ValidationError("Campaign name is required")

        # Validate target ICPs if provided
        if "target_icps" in data:
            target_icps = data["target_icps"]
            if not isinstance(target_icps, list):
                raise ValidationError("Target ICPs must be a list")

            # Verify all ICPs belong to workspace
            for icp_id in target_icps:
                icp = (
                    await self.supabase.table("icp_profiles")
                    .select("*")
                    .eq("id", icp_id)
                    .eq("workspace_id", workspace_id)
                    .single()
                    .execute()
                )
                if not icp.data:
                    raise ValidationError(f"Target ICP not found: {icp_id}")

        # Validate budget if provided
        if "budget_usd" in data:
            budget = data["budget_usd"]
            if not isinstance(budget, (int, float)) or budget < 0:
                raise ValidationError("Budget must be a positive number")

        return await self.repository.create(workspace_id, data)

    async def add_move(self, campaign_id: str, workspace_id: str, move_id: str) -> bool:
        """
        Add move to campaign

        Args:
            campaign_id: Campaign ID
            workspace_id: Workspace ID
            move_id: Move ID

        Returns:
            True if added successfully, False otherwise
        """
        # Verify campaign belongs to workspace
        campaign = await self.repository.get_by_id(campaign_id, workspace_id)
        if not campaign:
            raise ValidationError("Campaign not found")

        # Verify move belongs to workspace
        move = await self.move_repository.get_by_id(move_id, workspace_id)
        if not move:
            raise ValidationError("Move not found")

        # Update move to associate with campaign
        result = await self.move_repository.update(
            move_id, workspace_id, {"campaign_id": campaign_id}
        )
        return result is not None

    async def launch_campaign(
        self, campaign_id: str, workspace_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Launch a campaign (change status to active)

        Args:
            campaign_id: Campaign ID
            workspace_id: Workspace ID

        Returns:
            Updated campaign data or None if not found
        """
        campaign = await self.repository.get_by_id(campaign_id, workspace_id)
        if not campaign:
            raise ValidationError("Campaign not found")

        if campaign.get("status") == "active":
            raise ValidationError("Campaign is already active")

        # Update campaign status
        updated_campaign = await self.repository.update_status(campaign_id, "active")

        # Activate all associated moves
        if updated_campaign:
            moves = await self.move_repository.list_by_workspace(
                workspace_id, {"campaign_id": campaign_id}
            )
            for move in moves:
                await self.move_repository.start_move(move["id"], workspace_id)

        return updated_campaign

    async def calculate_roi(
        self, campaign_id: str, workspace_id: str
    ) -> Dict[str, Any]:
        """
        Calculate ROI for campaign

        Args:
            campaign_id: Campaign ID
            workspace_id: Workspace ID

        Returns:
            ROI calculation data
        """
        campaign = await self.repository.get_with_moves(campaign_id, workspace_id)
        if not campaign:
            raise ValidationError("Campaign not found")

        budget = campaign.get("budget_usd", 0)
        moves = campaign.get("moves", [])

        # Calculate total cost from moves
        total_cost = budget
        total_results = {}

        for move in moves:
            # Get execution results
            if move.get("results"):
                results = move["results"]
                # Aggregate results (simplified)
                if "leads" in results:
                    total_results["leads"] = (
                        total_results.get("leads", 0) + results["leads"]
                    )
                if "conversions" in results:
                    total_results["conversions"] = (
                        total_results.get("conversions", 0) + results["conversions"]
                    )
                if "revenue" in results:
                    total_results["revenue"] = (
                        total_results.get("revenue", 0) + results["revenue"]
                    )

        # Calculate ROI
        revenue = total_results.get("revenue", 0)
        roi = ((revenue - total_cost) / total_cost * 100) if total_cost > 0 else 0

        return {
            "campaign_id": campaign_id,
            "campaign_name": campaign.get("name"),
            "budget_usd": budget,
            "total_cost_usd": total_cost,
            "revenue_usd": revenue,
            "roi_percentage": round(roi, 2),
            "results": total_results,
            "move_count": len(moves),
            "completed_moves": len(
                [m for m in moves if m.get("status") == "completed"]
            ),
        }

    async def get_campaign_with_analytics(
        self, campaign_id: str, workspace_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get campaign with full analytics

        Args:
            campaign_id: Campaign ID
            workspace_id: Workspace ID

        Returns:
            Campaign data with analytics or None if not found
        """
        campaign = await self.repository.get_with_moves(campaign_id, workspace_id)
        if not campaign:
            return None

        # Add analytics
        analytics = await self.calculate_roi(campaign_id, workspace_id)
        campaign["analytics"] = analytics

        # Add performance metrics
        moves = campaign.get("moves", [])
        campaign["performance_metrics"] = {
            "total_moves": len(moves),
            "active_moves": len([m for m in moves if m.get("status") == "active"]),
            "completed_moves": len(
                [m for m in moves if m.get("status") == "completed"]
            ),
            "paused_moves": len([m for m in moves if m.get("status") == "paused"]),
        }

        return campaign

    async def list_campaigns(
        self, workspace_id: str, filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        List campaigns for workspace with optional filters

        Args:
            workspace_id: Workspace ID
            filters: Optional filters

        Returns:
            List of campaign data
        """
        return await self.repository.list_by_workspace(workspace_id, filters)

    async def update_campaign(
        self, campaign_id: str, workspace_id: str, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update campaign with validation

        Args:
            campaign_id: Campaign ID
            workspace_id: Workspace ID
            data: Update data

        Returns:
            Updated campaign data or None if not found
        """
        campaign = await self.repository.get_by_id(campaign_id, workspace_id)
        if not campaign:
            raise ValidationError("Campaign not found")

        # Validate status if provided
        if "status" in data:
            valid_statuses = ["planning", "active", "paused", "completed", "archived"]
            if data["status"] not in valid_statuses:
                raise ValidationError(f"Invalid status: {data['status']}")

        # Validate budget if provided
        if "budget_usd" in data:
            budget = data["budget_usd"]
            if not isinstance(budget, (int, float)) or budget < 0:
                raise ValidationError("Budget must be a positive number")

        return await self.repository.update(campaign_id, data)

    async def delete_campaign(self, campaign_id: str, workspace_id: str) -> bool:
        """
        Delete campaign

        Args:
            campaign_id: Campaign ID
            workspace_id: Workspace ID

        Returns:
            True if deleted, False otherwise
        """
        campaign = await self.repository.get_by_id(campaign_id, workspace_id)
        if not campaign:
            raise ValidationError("Campaign not found")

        # Check if campaign is active
        if campaign.get("status") == "active":
            raise ValidationError("Cannot delete active campaign. Pause it first.")

        # Disassociate moves from campaign
        moves = await self.move_repository.list_by_workspace(
            workspace_id, {"campaign_id": campaign_id}
        )
        for move in moves:
            await self.move_repository.update(
                move["id"], workspace_id, {"campaign_id": None}
            )

        return await self.repository.delete(campaign_id)

    async def get_campaign_dashboard(self, workspace_id: str) -> Dict[str, Any]:
        """
        Get campaign dashboard data for workspace

        Args:
            workspace_id: Workspace ID

        Returns:
            Dashboard data
        """
        campaigns = await self.list_campaigns(workspace_id)

        dashboard = {
            "total_campaigns": len(campaigns),
            "active_campaigns": [],
            "completed_campaigns": [],
            "total_budget": 0,
            "total_spent": 0,
            "total_revenue": 0,
            "average_roi": 0,
            "performance_by_status": {},
        }

        total_roi = 0
        roi_count = 0

        for campaign in campaigns:
            status = campaign.get("status", "planning")
            dashboard["performance_by_status"][status] = (
                dashboard["performance_by_status"].get(status, 0) + 1
            )

            if status == "active":
                dashboard["active_campaigns"].append(campaign)
            elif status == "completed":
                dashboard["completed_campaigns"].append(campaign)

            # Calculate financial metrics
            budget = campaign.get("budget_usd", 0)
            dashboard["total_budget"] += budget

            # Get campaign analytics
            try:
                analytics = await self.calculate_roi(campaign["id"], workspace_id)
                dashboard["total_spent"] += analytics["total_cost_usd"]
                dashboard["total_revenue"] += analytics["revenue_usd"]

                if analytics["roi_percentage"] is not None:
                    total_roi += analytics["roi_percentage"]
                    roi_count += 1
            except:
                pass

        # Calculate average ROI
        if roi_count > 0:
            dashboard["average_roi"] = round(total_roi / roi_count, 2)

        return dashboard

    async def validate_campaign_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate campaign data before saving

        Args:
            data: Campaign data to validate

        Returns:
            True if valid, raises ValidationError if invalid
        """
        # Required fields
        required_fields = ["name"]
        for field in required_fields:
            if not data.get(field):
                raise ValidationError(f"Required field missing: {field}")

        # Validate name length
        if len(data["name"]) > 100:
            raise ValidationError("Campaign name too long (max 100 characters)")

        # Validate description length if provided
        if "description" in data and len(data["description"]) > 500:
            raise ValidationError("Description too long (max 500 characters)")

        # Validate status
        if "status" in data:
            valid_statuses = ["planning", "active", "paused", "completed", "archived"]
            if data["status"] not in valid_statuses:
                raise ValidationError(f"Invalid status: {data['status']}")

        # Validate budget
        if "budget_usd" in data:
            budget = data["budget_usd"]
            if not isinstance(budget, (int, float)) or budget < 0:
                raise ValidationError("Budget must be a positive number")

        # Validate JSON fields
        json_fields = ["target_icps", "phases", "success_metrics", "results"]
        for field in json_fields:
            if field in data and not isinstance(data[field], list):
                raise ValidationError(f"{field} must be a list")

        return True
