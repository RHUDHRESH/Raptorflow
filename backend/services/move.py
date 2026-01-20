"""
Move service for business logic operations
Handles move-related business logic and validation
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from backend.core.models import ValidationError
from backend.core.supabase_mgr import get_supabase_client
from backend.db.campaigns import CampaignRepository
from backend.db.moves import MoveRepository
from backend.services.bcm_recorder import BCMEventRecorder
from backend.schemas.bcm_evolution import EventType


class MoveService:
    """Service for move business logic"""

    def __init__(self):
        self.repository = MoveRepository()
        self.campaign_repository = CampaignRepository()
        self.supabase = get_supabase_client()
        self.bcm_recorder = BCMEventRecorder(db_client=self.supabase)

    async def create_move(
        self, workspace_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create new move with validation

        Args:
            workspace_id: Workspace ID
            data: Move data

        Returns:
            Created move data
        """
        # Validate required fields
        if not data.get("name"):
            raise ValidationError("Move name is required")

        # Validate category
        valid_categories = ["ignite", "capture", "authority", "repair", "rally"]
        if "category" in data and data["category"] not in valid_categories:
            raise ValidationError(f"Invalid category: {data['category']}")

        # Validate campaign if provided
        if "campaign_id" in data and data["campaign_id"]:
            campaign = await self.campaign_repository.get_by_id(
                data["campaign_id"], workspace_id
            )
            if not campaign:
                raise ValidationError("Campaign not found")

        # Validate target ICP if provided
        if "target_icp_id" in data and data["target_icp_id"]:
            icp = (
                await self.supabase.table("icp_profiles")
                .select("*")
                .eq("id", data["target_icp_id"])
                .eq("workspace_id", workspace_id)
                .single()
                .execute()
            )
            if not icp.data:
                raise ValidationError("Target ICP not found")

        return await self.repository.create(workspace_id, data)

    async def start_move(
        self, move_id: str, workspace_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Start a move (change status to active)

        Args:
            move_id: Move ID
            workspace_id: Workspace ID

        Returns:
            Updated move data or None if not found
        """
        move = await self.repository.get_by_id(move_id, workspace_id)
        if not move:
            raise ValidationError("Move not found")

        if move.get("status") == "active":
            raise ValidationError("Move is already active")

        return await self.repository.start_move(move_id, workspace_id)

    async def pause_move(
        self, move_id: str, workspace_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Pause a move (change status to paused)

        Args:
            move_id: Move ID
            workspace_id: Workspace ID

        Returns:
            Updated move data or None if not found
        """
        move = await self.repository.get_by_id(move_id, workspace_id)
        if not move:
            raise ValidationError("Move not found")

        if move.get("status") != "active":
            raise ValidationError("Only active moves can be paused")

        return await self.repository.pause_move(move_id, workspace_id)

    async def complete_move(
        self, move_id: str, workspace_id: str, results: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Complete a move (change status to completed)

        Args:
            move_id: Move ID
            workspace_id: Workspace ID
            results: Optional results data

        Returns:
            Updated move data or None if not found
        """
        move = await self.repository.get_by_id(move_id, workspace_id)
        if not move:
            raise ValidationError("Move not found")

        if move.get("status") == "completed":
            raise ValidationError("Move is already completed")

        completed_move = await self.repository.complete_move(move_id, workspace_id, results)
        
        # Record event in BCM Ledger
        try:
            await self.bcm_recorder.record_event(
                workspace_id=workspace_id,
                event_type=EventType.MOVE_COMPLETED,
                payload={
                    "move_id": move_id,
                    "title": move.get("name", "Unknown Move"),
                    "results": results or {}
                }
            )
        except Exception as e:
            # We don't want to fail the move completion if the ledger fails, but we should log it
            import logging
            logging.getLogger(__name__).error(f"Failed to record BCM event for completed move {move_id}: {e}")

        return completed_move

    async def generate_tasks(
        self, move_id: str, workspace_id: str
    ) -> List[Dict[str, Any]]:
        """
        Generate tasks for a move

        Args:
            move_id: Move ID
            workspace_id: Workspace ID

        Returns:
            List of generated tasks
        """
        move = await self.repository.get_by_id(move_id, workspace_id)
        if not move:
            raise ValidationError("Move not found")

        return await self.repository.generate_tasks(move_id, workspace_id)

    async def list_moves(
        self, workspace_id: str, filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        List moves for workspace with optional filters

        Args:
            workspace_id: Workspace ID
            filters: Optional filters

        Returns:
            List of move data
        """
        return await self.repository.list_by_workspace(workspace_id, filters)

    async def get_move_with_details(
        self, move_id: str, workspace_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get move with full details including tasks and related data

        Args:
            move_id: Move ID
            workspace_id: Workspace ID

        Returns:
            Move data with details or None if not found
        """
        move = await self.repository.get_with_tasks(move_id, workspace_id)
        if not move:
            return None

        # Get campaign details if associated
        if move.get("campaign_id"):
            campaign = await self.campaign_repository.get_by_id(
                move["campaign_id"], workspace_id
            )
            move["campaign"] = campaign

        # Get target ICP details if specified
        if move.get("target_icp_id"):
            icp = (
                await self.supabase.table("icp_profiles")
                .select("*")
                .eq("id", move["target_icp_id"])
                .single()
                .execute()
            )
            move["target_icp"] = icp.data if icp.data else None

        return move

    async def update_move(
        self, move_id: str, workspace_id: str, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update move with validation

        Args:
            move_id: Move ID
            workspace_id: Workspace ID
            data: Update data

        Returns:
            Updated move data or None if not found
        """
        move = await self.repository.get_by_id(move_id, workspace_id)
        if not move:
            raise ValidationError("Move not found")

        # Validate category if provided
        if "category" in data:
            valid_categories = ["ignite", "capture", "authority", "repair", "rally"]
            if data["category"] not in valid_categories:
                raise ValidationError(f"Invalid category: {data['category']}")

        # Validate status if provided
        if "status" in data:
            valid_statuses = ["draft", "active", "paused", "completed", "archived"]
            if data["status"] not in valid_statuses:
                raise ValidationError(f"Invalid status: {data['status']}")

        return await self.repository.update(move_id, workspace_id, data)

    async def delete_move(self, move_id: str, workspace_id: str) -> bool:
        """
        Delete move

        Args:
            move_id: Move ID
            workspace_id: Workspace ID

        Returns:
            True if deleted, False otherwise
        """
        move = await self.repository.get_by_id(move_id, workspace_id)
        if not move:
            raise ValidationError("Move not found")

        # Check if move is active
        if move.get("status") == "active":
            raise ValidationError("Cannot delete active move. Pause it first.")

        return await self.repository.delete(move_id, workspace_id)

    async def get_move_analytics(self, workspace_id: str) -> Dict[str, Any]:
        """
        Get analytics for moves in workspace

        Args:
            workspace_id: Workspace ID

        Returns:
            Analytics data
        """
        moves = await self.list_moves(workspace_id)

        analytics = {
            "total_moves": len(moves),
            "by_status": {},
            "by_category": {},
            "active_moves": [],
            "completed_moves": [],
            "performance_metrics": {},
        }

        # Count by status
        for move in moves:
            status = move.get("status", "draft")
            analytics["by_status"][status] = analytics["by_status"].get(status, 0) + 1

            category = move.get("category", "ignite")
            analytics["by_category"][category] = (
                analytics["by_category"].get(category, 0) + 1
            )

            if status == "active":
                analytics["active_moves"].append(move)
            elif status == "completed":
                analytics["completed_moves"].append(move)

        # Calculate performance metrics
        if analytics["completed_moves"]:
            total_completed = len(analytics["completed_moves"])
            total_duration = 0

            for move in analytics["completed_moves"]:
                if move.get("started_at") and move.get("completed_at"):
                    start = datetime.fromisoformat(move["started_at"])
                    end = datetime.fromisoformat(move["completed_at"])
                    duration = (end - start).days
                    total_duration += duration

            if total_completed > 0:
                analytics["performance_metrics"]["average_duration_days"] = (
                    total_duration / total_completed
                )

        return analytics

    async def validate_move_data(self, data: Dict[str, Any]) -> bool:
        """
        Validate move data before saving

        Args:
            data: Move data to validate

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
            raise ValidationError("Move name too long (max 100 characters)")

        # Validate category
        if "category" in data:
            valid_categories = ["ignite", "capture", "authority", "repair", "rally"]
            if data["category"] not in valid_categories:
                raise ValidationError(f"Invalid category: {data['category']}")

        # Validate status
        if "status" in data:
            valid_statuses = ["draft", "active", "paused", "completed", "archived"]
            if data["status"] not in valid_statuses:
                raise ValidationError(f"Invalid status: {data['status']}")

        # Validate duration
        if "duration_days" in data:
            duration = data["duration_days"]
            if not isinstance(duration, int) or duration < 1 or duration > 365:
                raise ValidationError(
                    "Duration must be an integer between 1 and 365 days"
                )

        # Validate JSON fields
        json_fields = ["strategy", "execution_plan", "success_metrics", "results"]
        for field in json_fields:
            if field in data and not isinstance(data[field], list):
                raise ValidationError(f"{field} must be a list")

        return True
