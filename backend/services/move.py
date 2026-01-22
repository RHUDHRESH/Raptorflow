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
from backend.services.bcm_integration import bcm_evolution


class MoveService:
    """Service for move business logic with BCM integration"""

    def __init__(self):
        self.repository = MoveRepository()
        self.campaign_repository = CampaignRepository()
        self.supabase = get_supabase_client()

    async def create_move(
        self, workspace_id: str, data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Create new move with validation and BCM logging
        """
        # Validate required fields
        if not data.get("name"):
            raise ValidationError("Move name is required")

        # ... (validation logic kept same)
        valid_categories = ["ignite", "capture", "authority", "repair", "rally"]
        if "category" in data and data["category"] not in valid_categories:
            raise ValidationError(f"Invalid category: {data['category']}")

        created_move = await self.repository.create(workspace_id, data)

        # Record in BCM Ledger
        await bcm_evolution.record_interaction(
            workspace_id=workspace_id,
            agent_name="MoveService",
            interaction_type="MOVE_CREATED",
            payload={
                "move_id": created_move.get("id"),
                "name": created_move.get("name"),
                "category": created_move.get("category"),
            },
        )

        return created_move

    async def start_move(
        self, move_id: str, workspace_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Start a move (change status to active)
        """
        move = await self.repository.get_by_id(move_id, workspace_id)
        if not move:
            raise ValidationError("Move not found")

        if move.get("status") == "active":
            raise ValidationError("Move is already active")

        updated = await self.repository.start_move(move_id, workspace_id)

        await bcm_evolution.record_interaction(
            workspace_id=workspace_id,
            agent_name="MoveService",
            interaction_type="MOVE_STARTED",
            payload={"move_id": move_id, "name": move.get("name")},
        )

        return updated

    async def pause_move(
        self, move_id: str, workspace_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Pause a move (change status to paused)
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
        Complete a move and record milestone in BCM Ledger
        """
        move = await self.repository.get_by_id(move_id, workspace_id)
        if not move:
            raise ValidationError("Move not found")

        if move.get("status") == "completed":
            raise ValidationError("Move is already completed")

        completed_move = await self.repository.complete_move(
            move_id, workspace_id, results
        )

        # Record milestone via unified utility
        await bcm_evolution.record_interaction(
            workspace_id=workspace_id,
            agent_name="MoveService",
            interaction_type="MOVE_COMPLETED",
            payload={
                "move_id": move_id,
                "title": move.get("name", "Unknown Move"),
                "results": results or {},
            },
        )

        return completed_move

    async def generate_tasks(
        self, move_id: str, workspace_id: str
    ) -> List[Dict[str, Any]]:
        """
        Generate tasks for a move and log AI interaction
        """
        move = await self.repository.get_by_id(move_id, workspace_id)
        if not move:
            raise ValidationError("Move not found")

        tasks = await self.repository.generate_tasks(move_id, workspace_id)

        await bcm_evolution.record_interaction(
            workspace_id=workspace_id,
            agent_name="MoveService",
            interaction_type="TASK_GENERATION",
            payload={"move_id": move_id, "task_count": len(tasks)},
        )

        return tasks

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
        """
        move = await self.repository.get_with_tasks(move_id, workspace_id)
        if not move:
            return None

        # Parallel fetching for performance
        tasks = []

        # Get campaign details if associated
        if move.get("campaign_id"):
            tasks.append(
                self.campaign_repository.get_by_id(move["campaign_id"], workspace_id)
            )
        else:
            tasks.append(asyncio.sleep(0, result=None))

        # Get target ICP details if specified
        if move.get("target_icp_id"):
            tasks.append(
                self.supabase.table("icp_profiles")
                .select("*")
                .eq("id", move["target_icp_id"])
                .single()
                .execute()
            )
        else:
            tasks.append(asyncio.sleep(0, result=None))

        results = await asyncio.gather(*tasks)

        move["campaign"] = results[0]
        if results[1] and hasattr(results[1], "data"):
            move["target_icp"] = results[1].data
        else:
            move["target_icp"] = None

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
