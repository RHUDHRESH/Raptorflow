"""
Campaign repository for database operations
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from filters import Filter, build_query
from pagination import PaginatedResult, Pagination

from .base import Repository
from .core.supabase_mgr import get_supabase_client


class CampaignRepository(Repository):
    """Repository for campaign operations"""

    def __init__(self):
        super().__init__("campaigns")

    def _map_to_model(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Map database record to dict."""
        return data

    async def get_by_workspace(
        self, workspace_id: str, pagination: Optional[Pagination] = None
    ) -> PaginatedResult:
        """Get all campaigns for a workspace"""
        query = (
            self.client.table("campaigns").select("*").eq("workspace_id", workspace_id)
        )

        if pagination:
            query = query.order("created_at", desc=True).range(
                pagination.page * pagination.page_size,
                (pagination.page + 1) * pagination.page_size - 1,
            )

        result = query.execute()

        if pagination:
            # Get total count
            count_result = (
                self.client.table("campaigns")
                .select("id", count="exact")
                .eq("workspace_id", workspace_id)
                .execute()
            )
            total = count_result.count or 0

            return PaginatedResult(
                items=result.data or [],
                total=total,
                page=pagination.page,
                page_size=pagination.page_size,
                total_pages=(total + pagination.page_size - 1) // pagination.page_size,
            )

        return PaginatedResult(
            items=result.data or [],
            total=len(result.data or []),
            page=0,
            page_size=len(result.data or []),
            total_pages=1,
        )

    async def get_with_moves(self, campaign_id: str) -> Optional[Dict[str, Any]]:
        """Get campaign with associated moves"""
        campaign_result = (
            self.client.table("campaigns")
            .select("*")
            .eq("id", campaign_id)
            .single()
            .execute()
        )

        if not campaign_result.data:
            return None

        campaign = campaign_result.data

        # Get associated moves
        moves_result = (
            self.client.table("moves")
            .select("*")
            .eq("campaign_id", campaign_id)
            .order("created_at", desc=True)
            .execute()
        )
        campaign["moves"] = moves_result.data or []

        return campaign

    async def update_status(
        self, campaign_id: str, status: str
    ) -> Optional[Dict[str, Any]]:
        """Update campaign status"""
        # Validate status
        valid_statuses = ["planning", "active", "paused", "completed", "archived"]
        if status not in valid_statuses:
            raise ValueError(
                f"Invalid status: {status}. Must be one of: {valid_statuses}"
            )

        update_data = {"status": status}

        # Set ended_at if completing
        if status == "completed":
            update_data["ended_at"] = datetime.utcnow().isoformat()

        result = (
            self.client.table("campaigns")
            .update(update_data)
            .eq("id", campaign_id)
            .execute()
        )

        if result.data:
            return result.data[0]
        return None

    async def add_move(self, campaign_id: str, move_id: str) -> bool:
        """Add a move to a campaign"""
        result = (
            self.client.table("moves")
            .update({"campaign_id": campaign_id})
            .eq("id", move_id)
            .execute()
        )
        return len(result.data or []) > 0

    async def remove_move(self, move_id: str) -> bool:
        """Remove a move from its campaign"""
        result = (
            self.client.table("moves")
            .update({"campaign_id": None})
            .eq("id", move_id)
            .execute()
        )
        return len(result.data or []) > 0

    async def get_campaign_stats(self, campaign_id: str) -> Dict[str, Any]:
        """Get campaign statistics"""
        campaign_result = (
            self.client.table("campaigns")
            .select("*")
            .eq("id", campaign_id)
            .single()
            .execute()
        )

        if not campaign_result.data:
            return {}

        campaign = campaign_result.data

        # Get move statistics
        moves_result = (
            self.client.table("moves")
            .select("status")
            .eq("campaign_id", campaign_id)
            .execute()
        )
        moves = moves_result.data or []

        total_moves = len(moves)
        completed_moves = len([m for m in moves if m.get("status") == "completed"])
        active_moves = len([m for m in moves if m.get("status") == "active"])

        # Get asset statistics
        assets_query = (
            self.client.table("moves").select("id").eq("campaign_id", campaign_id)
        )
        assets_result = (
            self.client.table("muse_assets")
            .select("id", count="exact")
            .in_("move_id", [m["id"] for m in moves])
            .execute()
        )

        total_assets = assets_result.count or 0

        # Calculate duration
        duration_days = None
        if campaign.get("started_at"):
            end_date = campaign.get("ended_at") or datetime.utcnow()
            start_date = datetime.fromisoformat(
                campaign["started_at"].replace("Z", "+00:00")
            )
            duration_days = (end_date - start_date).days

        return {
            "campaign_id": campaign_id,
            "total_moves": total_moves,
            "completed_moves": completed_moves,
            "active_moves": active_moves,
            "total_assets": total_assets,
            "completion_rate": (
                (completed_moves / total_moves * 100) if total_moves > 0 else 0
            ),
            "duration_days": duration_days,
            "status": campaign.get("status"),
            "budget_usd": campaign.get("budget_usd"),
            "started_at": campaign.get("started_at"),
            "ended_at": campaign.get("ended_at"),
        }

    async def calculate_roi(self, campaign_id: str) -> Dict[str, Any]:
        """Calculate campaign ROI"""
        campaign_result = (
            self.client.table("campaigns")
            .select("*")
            .eq("id", campaign_id)
            .single()
            .execute()
        )

        if not campaign_result.data:
            return {}

        campaign = campaign_result.data

        # Get total cost from agent executions
        moves_result = (
            self.client.table("moves")
            .select("id")
            .eq("campaign_id", campaign_id)
            .execute()
        )
        move_ids = [m["id"] for m in moves_result.data or []]

        total_cost = 0
        if move_ids:
            executions_result = (
                self.client.table("agent_executions")
                .select("cost_usd")
                .in_("move_id", move_ids)
                .execute()
            )
            total_cost = sum(e.get("cost_usd", 0) for e in executions_result.data or [])

        # Get results from campaign
        results = campaign.get("results", {})
        revenue = results.get("revenue", 0)
        leads = results.get("leads", 0)
        conversions = results.get("conversions", 0)

        # Calculate ROI metrics
        roi_percentage = (
            ((revenue - total_cost) / total_cost * 100) if total_cost > 0 else 0
        )
        cost_per_lead = total_cost / leads if leads > 0 else 0
        cost_per_conversion = total_cost / conversions if conversions > 0 else 0

        return {
            "campaign_id": campaign_id,
            "total_cost": total_cost,
            "revenue": revenue,
            "leads": leads,
            "conversions": conversions,
            "roi_percentage": roi_percentage,
            "cost_per_lead": cost_per_lead,
            "cost_per_conversion": cost_per_conversion,
            "profit": revenue - total_cost,
        }

    async def list_by_status(
        self, workspace_id: str, status: str, pagination: Optional[Pagination] = None
    ) -> PaginatedResult:
        """List campaigns by status"""
        query = (
            self.client.table("campaigns")
            .select("*")
            .eq("workspace_id", workspace_id)
            .eq("status", status)
        )

        if pagination:
            query = query.order("created_at", desc=True).range(
                pagination.page * pagination.page_size,
                (pagination.page + 1) * pagination.page_size - 1,
            )

        result = query.execute()

        if pagination:
            count_result = (
                self.client.table("campaigns")
                .select("id", count="exact")
                .eq("workspace_id", workspace_id)
                .eq("status", status)
                .execute()
            )
            total = count_result.count or 0

            return PaginatedResult(
                items=result.data or [],
                total=total,
                page=pagination.page,
                page_size=pagination.page_size,
                total_pages=(total + pagination.page_size - 1) // pagination.page_size,
            )

        return PaginatedResult(
            items=result.data or [],
            total=len(result.data or []),
            page=0,
            page_size=len(result.data or []),
            total_pages=1,
        )

    async def get_active_campaigns(self, workspace_id: str) -> List[Dict[str, Any]]:
        """Get all active campaigns for a workspace"""
        result = (
            self.client.table("campaigns")
            .select("*")
            .eq("workspace_id", workspace_id)
            .eq("status", "active")
            .order("created_at", desc=True)
            .execute()
        )
        return result.data or []

    async def archive_campaign(self, campaign_id: str) -> bool:
        """Archive a campaign"""
        return await self.update_status(campaign_id, "archived") is not None

    async def duplicate_campaign(
        self, campaign_id: str, new_name: str
    ) -> Optional[Dict[str, Any]]:
        """Duplicate a campaign"""
        # Get original campaign
        original = await self.get(campaign_id)
        if not original:
            return None

        # Remove fields that shouldn't be duplicated
        campaign_data = {
            k: v
            for k, v in original.items()
            if k not in ["id", "created_at", "updated_at", "ended_at"]
        }
        campaign_data["name"] = new_name
        campaign_data["status"] = "planning"
        campaign_data["started_at"] = None

        # Create new campaign
        result = self.client.table("campaigns").insert(campaign_data).execute()

        if result.data:
            return result.data[0]
        return None

    async def get_campaign_timeline(self, campaign_id: str) -> List[Dict[str, Any]]:
        """Get campaign timeline with key events"""
        campaign = await self.get(campaign_id)
        if not campaign:
            return []

        timeline = []

        # Add campaign creation
        if campaign.get("created_at"):
            timeline.append(
                {
                    "type": "campaign_created",
                    "date": campaign["created_at"],
                    "description": f"Campaign '{campaign.get('name')}' created",
                }
            )

        # Add campaign start
        if campaign.get("started_at"):
            timeline.append(
                {
                    "type": "campaign_started",
                    "date": campaign["started_at"],
                    "description": f"Campaign '{campaign.get('name')}' started",
                }
            )

        # Add moves
        moves = await self.get_with_moves(campaign_id)
        if moves and moves.get("moves"):
            for move in moves["moves"]:
                if move.get("created_at"):
                    timeline.append(
                        {
                            "type": "move_created",
                            "date": move["created_at"],
                            "description": f"Move '{move.get('name')}' created",
                        }
                    )

                if move.get("started_at"):
                    timeline.append(
                        {
                            "type": "move_started",
                            "date": move["started_at"],
                            "description": f"Move '{move.get('name')}' started",
                        }
                    )

                if move.get("completed_at"):
                    timeline.append(
                        {
                            "type": "move_completed",
                            "date": move["completed_at"],
                            "description": f"Move '{move.get('name')}' completed",
                        }
                    )

        # Add campaign end
        if campaign.get("ended_at"):
            timeline.append(
                {
                    "type": "campaign_completed",
                    "date": campaign["ended_at"],
                    "description": f"Campaign '{campaign.get('name')}' completed",
                }
            )

        # Sort by date
        timeline.sort(key=lambda x: x["date"], reverse=True)

        return timeline
