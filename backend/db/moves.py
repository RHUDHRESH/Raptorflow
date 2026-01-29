"""
Moves repository for database operations
Handles CRUD operations for marketing moves
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from .base import Repository
from .core.models import ValidationError
from .core.supabase_mgr import get_supabase_client


class MoveRepository(Repository):
    """Repository for moves operations"""

    def __init__(self):
        super().__init__("moves")

    def _map_to_model(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Map database record to dict."""
        return data

    async def list_by_campaign(
        self, campaign_id: str, workspace_id: str
    ) -> List[Dict[str, Any]]:
        """
        List all moves for a campaign

        Args:
            campaign_id: Campaign ID
            workspace_id: Workspace ID (for security)

        Returns:
            List of move data
        """
        try:
            result = (
                await self.client.table(self.table_name)
                .select("*")
                .eq("campaign_id", campaign_id)
                .eq("workspace_id", workspace_id)
                .execute()
            )
            return result.data if result.data else []

        except Exception as e:
            raise ValidationError(f"Failed to list moves by campaign: {e}")

    async def list_active(self, workspace_id: str) -> List[Dict[str, Any]]:
        """
        List all active moves for workspace

        Args:
            workspace_id: Workspace ID

        Returns:
            List of active move data
        """
        try:
            result = (
                await self.client.table(self.table_name)
                .select("*")
                .eq("workspace_id", workspace_id)
                .eq("status", "active")
                .execute()
            )
            return result.data if result.data else []

        except Exception as e:
            raise ValidationError(f"Failed to list active moves: {e}")

    async def update_status(
        self, move_id: str, workspace_id: str, status: str
    ) -> Optional[Dict[str, Any]]:
        """
        Update move status

        Args:
            move_id: Move ID
            workspace_id: Workspace ID (for security)
            status: New status

        Returns:
            Updated move data or None if not found
        """
        try:
            # Validate status
            valid_statuses = ["draft", "active", "paused", "completed", "archived"]
            if status not in valid_statuses:
                raise ValidationError(f"Invalid status: {status}")

            update_data = {
                "status": status,
                "updated_at": datetime.utcnow().isoformat(),
            }

            # Add timestamp for status changes
            if status == "active":
                update_data["started_at"] = datetime.utcnow().isoformat()
            elif status == "completed":
                update_data["completed_at"] = datetime.utcnow().isoformat()

            result = (
                await self.client.table(self.table_name)
                .update(update_data)
                .eq("id", move_id)
                .eq("workspace_id", workspace_id)
                .execute()
            )

            if not result.data:
                return None

            return result.data[0]

        except Exception as e:
            raise ValidationError(f"Failed to update move status: {e}")

    async def get_with_tasks(
        self, move_id: str, workspace_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get move with associated tasks

        Args:
            move_id: Move ID
            workspace_id: Workspace ID (for security)

        Returns:
            Move data with tasks or None if not found
        """
        try:
            # Get move
            move_result = (
                await self.client.table(self.table_name)
                .select("*")
                .eq("id", move_id)
                .eq("workspace_id", workspace_id)
                .single()
                .execute()
            )

            if not move_result.data:
                return None

            move = move_result.data

            # Get associated tasks
            tasks_result = (
                await self.client.table("move_tasks")
                .select("*")
                .eq("move_id", move_id)
                .execute()
            )
            move["tasks"] = tasks_result.data if tasks_result.data else []

            return move

        except Exception as e:
            raise ValidationError(f"Failed to get move with tasks: {e}")

    async def create(self, workspace_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create new move

        Args:
            workspace_id: Workspace ID
            data: Move data

        Returns:
            Created move data
        """
        try:
            move_data = {
                "workspace_id": workspace_id,
                **data,
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat(),
            }

            # Map calendar fields if present
            if "start_date" in data:
                move_data["start_date"] = data["start_date"]
            if "end_date" in data:
                move_data["end_date"] = data["end_date"]

            # Validate required fields
            if not move_data.get("name"):
                raise ValidationError("Move name is required")

            if not move_data.get("category"):
                move_data["category"] = "ignite"  # Default category

            # Validate category
            valid_categories = ["ignite", "capture", "authority", "repair", "rally"]
            if move_data["category"] not in valid_categories:
                raise ValidationError(f"Invalid category: {move_data['category']}")

            if not move_data.get("status"):
                move_data["status"] = "draft"  # Default status

            result = (
                await self.client.table(self.table_name).insert(move_data).execute()
            )
            return result.data[0] if result.data else move_data

        except Exception as e:
            raise ValidationError(f"Failed to create move: {e}")

    async def update(
        self, move_id: str, workspace_id: str, data: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Update move

        Args:
            move_id: Move ID
            workspace_id: Workspace ID (for security)
            data: Update data

        Returns:
            Updated move data or None if not found
        """
        try:
            update_data = {**data, "updated_at": datetime.utcnow().isoformat()}

            result = (
                await self.client.table(self.table_name)
                .update(update_data)
                .eq("id", move_id)
                .eq("workspace_id", workspace_id)
                .execute()
            )

            if not result.data:
                return None

            return result.data[0]

        except Exception as e:
            raise ValidationError(f"Failed to update move: {e}")

    async def delete(self, move_id: str, workspace_id: str) -> bool:
        """
        Delete move

        Args:
            move_id: Move ID
            workspace_id: Workspace ID (for security)

        Returns:
            True if deleted, False otherwise
        """
        try:
            result = (
                await self.client.table(self.table_name)
                .delete()
                .eq("id", move_id)
                .eq("workspace_id", workspace_id)
                .execute()
            )
            return len(result.data) > 0

        except Exception as e:
            raise ValidationError(f"Failed to delete move: {e}")

    async def get_by_id(
        self, move_id: str, workspace_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get move by ID

        Args:
            move_id: Move ID
            workspace_id: Workspace ID (for security)

        Returns:
            Move data or None if not found
        """
        try:
            result = (
                await self.client.table(self.table_name)
                .select("*")
                .eq("id", move_id)
                .eq("workspace_id", workspace_id)
                .single()
                .execute()
            )

            if not result.data:
                return None

            return result.data

        except Exception as e:
            raise ValidationError(f"Failed to get move: {e}")

    async def list_by_workspace(
        self, workspace_id: str, filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        List all moves for workspace with optional filters

        Args:
            workspace_id: Workspace ID
            filters: Optional filters to apply

        Returns:
            List of move data
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
                    if field == "status":
                        query = query.eq(field, value)
                    elif field == "category":
                        query = query.eq(field, value)
                    elif field == "target_icp_id":
                        query = query.eq(field, value)

            result = await query.execute()
            return result.data if result.data else []

        except Exception as e:
            raise ValidationError(f"Failed to list moves: {e}")

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
        return await self.update_status(move_id, workspace_id, "active")

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
        return await self.update_status(move_id, workspace_id, "paused")

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
        update_data = {"status": "completed"}
        if results:
            update_data["results"] = results

        return await self.update(move_id, workspace_id, update_data)

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
        try:
            # Get move details
            move = await self.get_by_id(move_id, workspace_id)
            if not move:
                return []

            # Generate sample tasks based on move category
            # In a real implementation, this would use AI to generate tasks
            tasks = []
            category = move.get("category", "ignite")

            if category == "ignite":
                task_templates = [
                    {
                        "title": "Research target audience",
                        "description": "Analyze ICP demographics and psychographics",
                    },
                    {
                        "title": "Create content outline",
                        "description": "Structure the content based on research",
                    },
                    {
                        "title": "Develop content assets",
                        "description": "Create actual content pieces",
                    },
                ]
            elif category == "capture":
                task_templates = [
                    {
                        "title": "Set up lead capture",
                        "description": "Implement lead generation mechanisms",
                    },
                    {
                        "title": "Create landing pages",
                        "description": "Build conversion-focused pages",
                    },
                    {
                        "title": "Configure email sequences",
                        "description": "Set up automated email flows",
                    },
                ]
            elif category == "authority":
                task_templates = [
                    {
                        "title": "Identify thought leadership topics",
                        "description": "Research industry trends and insights",
                    },
                    {
                        "title": "Create expert content",
                        "description": "Develop authoritative content pieces",
                    },
                    {
                        "title": "Distribute to channels",
                        "description": "Publish across relevant platforms",
                    },
                ]
            else:
                task_templates = [
                    {
                        "title": "Research and planning",
                        "description": "Initial research and strategy development",
                    },
                    {
                        "title": "Content creation",
                        "description": "Create core content assets",
                    },
                    {
                        "title": "Distribution and promotion",
                        "description": "Promote content to target audience",
                    },
                ]

            # Create tasks
            for i, template in enumerate(task_templates):
                task_data = {
                    "move_id": move_id,
                    "workspace_id": workspace_id,
                    "title": template["title"],
                    "description": template["description"],
                    "status": "pending",
                    "priority": "medium",
                    "order": i + 1,
                    "created_at": datetime.utcnow().isoformat(),
                    "updated_at": datetime.utcnow().isoformat(),
                }

                result = (
                    await self.client.table("move_tasks").insert(task_data).execute()
                )
                if result.data:
                    tasks.append(result.data[0])

            return tasks

        except Exception as e:
            raise ValidationError(f"Failed to generate tasks for move: {e}")
