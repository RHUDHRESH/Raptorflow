"""
Plan Checkpointer for Cognitive Engine

Handles saving and loading execution plan checkpoints.
Implements PROMPT 23 from STREAM_3_COGNITIVE_ENGINE.
"""

import asyncio
import json
import pickle
import uuid
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from ..models import ExecutionPlan, PlanStep


@dataclass
class CheckpointMetadata:
    """Metadata for a plan checkpoint."""

    checkpoint_id: str
    plan_id: str
    workspace_id: str
    user_id: str
    created_at: datetime
    completed_steps: List[str]
    failed_steps: List[str]
    total_steps: int
    progress_percentage: float
    total_cost_usd: float
    total_tokens_used: int
    execution_time_seconds: int
    metadata: Dict[str, Any]


@dataclass
class CheckpointData:
    """Complete checkpoint data."""

    metadata: CheckpointMetadata
    original_plan: ExecutionPlan
    current_state: Dict[str, Any]
    step_results: Dict[str, Any]
    context_data: Dict[str, Any]


class PlanCheckpointer:
    """
    Handles saving and loading execution plan checkpoints.

    Supports both file-based and database-based checkpoint storage.
    """

    def __init__(
        self, storage_type: str = "file", storage_path: str = None, db_client=None
    ):
        """
        Initialize the checkpointer.

        Args:
            storage_type: "file" or "database"
            storage_path: Path for file-based storage
            db_client: Database client for database storage
        """
        self.storage_type = storage_type
        self.storage_path = storage_path or Path.cwd() / "checkpoints"
        self.db_client = db_client

        if storage_type == "file":
            self.storage_path = Path(self.storage_path)
            self.storage_path.mkdir(parents=True, exist_ok=True)

    async def checkpoint(
        self,
        plan: ExecutionPlan,
        completed_steps: List[str],
        failed_steps: List[str] = None,
        current_state: Dict[str, Any] = None,
        step_results: Dict[str, Any] = None,
        context_data: Dict[str, Any] = None,
        workspace_id: str = None,
        user_id: str = None,
    ) -> str:
        """
        Create a checkpoint for the current execution state.

        Args:
            plan: Current execution plan
            completed_steps: List of completed step IDs
            failed_steps: List of failed step IDs
            current_state: Current execution state
            step_results: Results from completed steps
            context_data: Additional context data
            workspace_id: Workspace ID
            user_id: User ID

        Returns:
            Checkpoint ID
        """
        if failed_steps is None:
            failed_steps = []
        if current_state is None:
            current_state = {}
        if step_results is None:
            step_results = {}
        if context_data is None:
            context_data = {}

        # Generate checkpoint ID
        checkpoint_id = str(uuid.uuid4())

        # Calculate progress
        total_steps = len(plan.steps)
        progress_percentage = (
            len(completed_steps) / total_steps * 100 if total_steps > 0 else 0
        )

        # Calculate totals
        total_cost = sum(
            step.estimated_cost for step in plan.steps if step.id in completed_steps
        )
        total_tokens = sum(
            step.estimated_tokens for step in plan.steps if step.id in completed_steps
        )

        # Create metadata
        metadata = CheckpointMetadata(
            checkpoint_id=checkpoint_id,
            plan_id=plan.metadata.get("plan_id", str(uuid.uuid4())),
            workspace_id=workspace_id or "default",
            user_id=user_id or "default",
            created_at=datetime.now(),
            completed_steps=completed_steps,
            failed_steps=failed_steps,
            total_steps=total_steps,
            progress_percentage=progress_percentage,
            total_cost_usd=total_cost,
            total_tokens_used=total_tokens,
            execution_time_seconds=plan.total_time_seconds,
            metadata=plan.metadata,
        )

        # Create checkpoint data
        checkpoint_data = CheckpointData(
            metadata=metadata,
            original_plan=plan,
            current_state=current_state,
            step_results=step_results,
            context_data=context_data,
        )

        # Save checkpoint
        if self.storage_type == "file":
            await self._save_to_file(checkpoint_data)
        elif self.storage_type == "database":
            await self._save_to_database(checkpoint_data)

        return checkpoint_id

    async def resume(self, checkpoint_id: str) -> Optional[CheckpointData]:
        """
        Resume execution from a checkpoint.

        Args:
            checkpoint_id: ID of the checkpoint to resume from

        Returns:
            CheckpointData if found, None otherwise
        """
        if self.storage_type == "file":
            return await self._load_from_file(checkpoint_id)
        elif self.storage_type == "database":
            return await self._load_from_database(checkpoint_id)

        return None

    async def list_checkpoints(
        self,
        workspace_id: str = None,
        user_id: str = None,
        plan_id: str = None,
        limit: int = 50,
    ) -> List[CheckpointMetadata]:
        """
        List available checkpoints.

        Args:
            workspace_id: Filter by workspace ID
            user_id: Filter by user ID
            plan_id: Filter by plan ID
            limit: Maximum number of checkpoints to return

        Returns:
            List of checkpoint metadata
        """
        if self.storage_type == "file":
            return await self._list_files(workspace_id, user_id, plan_id, limit)
        elif self.storage_type == "database":
            return await self._list_database(workspace_id, user_id, plan_id, limit)

        return []

    async def delete_checkpoint(self, checkpoint_id: str) -> bool:
        """
        Delete a checkpoint.

        Args:
            checkpoint_id: ID of the checkpoint to delete

        Returns:
            True if deleted, False otherwise
        """
        if self.storage_type == "file":
            return await self._delete_file(checkpoint_id)
        elif self.storage_type == "database":
            return await self._delete_database(checkpoint_id)

        return False

    async def cleanup_old_checkpoints(
        self, max_age_days: int = 30, workspace_id: str = None
    ) -> int:
        """
        Clean up old checkpoints.

        Args:
            max_age_days: Maximum age in days
            workspace_id: Filter by workspace ID

        Returns:
            Number of checkpoints deleted
        """
        cutoff_date = datetime.now() - timedelta(days=max_age_days)

        if self.storage_type == "file":
            return await self._cleanup_files(cutoff_date, workspace_id)
        elif self.storage_type == "database":
            return await self._cleanup_database(cutoff_date, workspace_id)

        return 0

    async def _save_to_file(self, checkpoint_data: CheckpointData) -> None:
        """Save checkpoint to file."""
        file_path = self.storage_path / f"{checkpoint_data.metadata.checkpoint_id}.json"

        # Convert dataclasses to dicts for JSON serialization
        data = {
            "metadata": asdict(checkpoint_data.metadata),
            "original_plan": asdict(checkpoint_data.original_plan),
            "current_state": checkpoint_data.current_state,
            "step_results": checkpoint_data.step_results,
            "context_data": checkpoint_data.context_data,
        }

        # Convert datetime to string
        data["metadata"]["created_at"] = checkpoint_data.metadata.created_at.isoformat()

        with open(file_path, "w") as f:
            json.dump(data, f, indent=2, default=str)

    async def _save_to_database(self, checkpoint_data: CheckpointData) -> None:
        """Save checkpoint to database."""
        if not self.db_client:
            raise ValueError("Database client not provided")

        # Convert to dict and handle datetime serialization
        data = asdict(checkpoint_data)
        data["metadata"]["created_at"] = checkpoint_data.metadata.created_at.isoformat()

        # Insert into database
        await self.db_client.insert("plan_checkpoints", data)

    async def _load_from_file(self, checkpoint_id: str) -> Optional[CheckpointData]:
        """Load checkpoint from file."""
        file_path = self.storage_path / f"{checkpoint_id}.json"

        if not file_path.exists():
            return None

        try:
            with open(file_path, "r") as f:
                data = json.load(f)

            # Reconstruct objects
            metadata = CheckpointMetadata(**data["metadata"])
            metadata.created_at = datetime.fromisoformat(data["metadata"]["created_at"])

            original_plan = ExecutionPlan(**data["original_plan"])

            return CheckpointData(
                metadata=metadata,
                original_plan=original_plan,
                current_state=data["current_state"],
                step_results=data["step_results"],
                context_data=data["context_data"],
            )

        except Exception as e:
            print(f"Error loading checkpoint {checkpoint_id}: {e}")
            return None

    async def _load_from_database(self, checkpoint_id: str) -> Optional[CheckpointData]:
        """Load checkpoint from database."""
        if not self.db_client:
            raise ValueError("Database client not provided")

        try:
            data = await self.db_client.get("plan_checkpoints", checkpoint_id)

            if not data:
                return None

            # Reconstruct objects
            metadata = CheckpointMetadata(**data["metadata"])
            metadata.created_at = datetime.fromisoformat(data["metadata"]["created_at"])

            original_plan = ExecutionPlan(**data["original_plan"])

            return CheckpointData(
                metadata=metadata,
                original_plan=original_plan,
                current_state=data["current_state"],
                step_results=data["step_results"],
                context_data=data["context_data"],
            )

        except Exception as e:
            print(f"Error loading checkpoint {checkpoint_id}: {e}")
            return None

    async def _list_files(
        self,
        workspace_id: str = None,
        user_id: str = None,
        plan_id: str = None,
        limit: int = 50,
    ) -> List[CheckpointMetadata]:
        """List checkpoints from files."""
        checkpoints = []

        for file_path in self.storage_path.glob("*.json"):
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)

                metadata = CheckpointMetadata(**data["metadata"])
                metadata.created_at = datetime.fromisoformat(
                    data["metadata"]["created_at"]
                )

                # Apply filters
                if workspace_id and metadata.workspace_id != workspace_id:
                    continue
                if user_id and metadata.user_id != user_id:
                    continue
                if plan_id and metadata.plan_id != plan_id:
                    continue

                checkpoints.append(metadata)

            except Exception as e:
                print(f"Error reading checkpoint file {file_path}: {e}")

        # Sort by creation date (newest first) and limit
        checkpoints.sort(key=lambda x: x.created_at, reverse=True)
        return checkpoints[:limit]

    async def _list_database(
        self,
        workspace_id: str = None,
        user_id: str = None,
        plan_id: str = None,
        limit: int = 50,
    ) -> List[CheckpointMetadata]:
        """List checkpoints from database."""
        if not self.db_client:
            raise ValueError("Database client not provided")

        # Build query
        filters = {}
        if workspace_id:
            filters["workspace_id"] = workspace_id
        if user_id:
            filters["user_id"] = user_id
        if plan_id:
            filters["plan_id"] = plan_id

        results = await self.db_client.list("plan_checkpoints", filters, limit=limit)

        checkpoints = []
        for result in results:
            metadata = CheckpointMetadata(**result["metadata"])
            metadata.created_at = datetime.fromisoformat(
                result["metadata"]["created_at"]
            )
            checkpoints.append(metadata)

        return checkpoints

    async def _delete_file(self, checkpoint_id: str) -> bool:
        """Delete checkpoint file."""
        file_path = self.storage_path / f"{checkpoint_id}.json"

        try:
            if file_path.exists():
                file_path.unlink()
                return True
        except Exception as e:
            print(f"Error deleting checkpoint file {checkpoint_id}: {e}")

        return False

    async def _delete_database(self, checkpoint_id: str) -> bool:
        """Delete checkpoint from database."""
        if not self.db_client:
            raise ValueError("Database client not provided")

        try:
            await self.db_client.delete("plan_checkpoints", checkpoint_id)
            return True
        except Exception as e:
            print(f"Error deleting checkpoint {checkpoint_id}: {e}")

        return False

    async def _cleanup_files(
        self, cutoff_date: datetime, workspace_id: str = None
    ) -> int:
        """Clean up old checkpoint files."""
        deleted_count = 0

        for file_path in self.storage_path.glob("*.json"):
            try:
                with open(file_path, "r") as f:
                    data = json.load(f)

                created_at = datetime.fromisoformat(data["metadata"]["created_at"])

                # Check if file is old enough
                if created_at < cutoff_date:
                    # Apply workspace filter if provided
                    if (
                        workspace_id
                        and data["metadata"]["workspace_id"] != workspace_id
                    ):
                        continue

                    file_path.unlink()
                    deleted_count += 1

            except Exception as e:
                print(f"Error processing checkpoint file {file_path}: {e}")

        return deleted_count

    async def _cleanup_database(
        self, cutoff_date: datetime, workspace_id: str = None
    ) -> int:
        """Clean up old database checkpoints."""
        if not self.db_client:
            raise ValueError("Database client not provided")

        filters = {"created_at": {"lt": cutoff_date.isoformat()}}
        if workspace_id:
            filters["workspace_id"] = workspace_id

        try:
            return await self.db_client.delete_many("plan_checkpoints", filters)
        except Exception as e:
            print(f"Error cleaning up database checkpoints: {e}")
            return 0

    async def get_checkpoint_summary(
        self, checkpoint_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get a summary of checkpoint information.

        Args:
            checkpoint_id: ID of the checkpoint

        Returns:
            Summary dictionary or None if not found
        """
        checkpoint = await self.resume(checkpoint_id)

        if not checkpoint:
            return None

        return {
            "checkpoint_id": checkpoint.metadata.checkpoint_id,
            "plan_id": checkpoint.metadata.plan_id,
            "workspace_id": checkpoint.metadata.workspace_id,
            "user_id": checkpoint.metadata.user_id,
            "created_at": checkpoint.metadata.created_at.isoformat(),
            "progress_percentage": checkpoint.metadata.progress_percentage,
            "completed_steps": len(checkpoint.metadata.completed_steps),
            "failed_steps": len(checkpoint.metadata.failed_steps),
            "total_steps": checkpoint.metadata.total_steps,
            "total_cost_usd": checkpoint.metadata.total_cost_usd,
            "total_tokens_used": checkpoint.metadata.total_tokens_used,
            "execution_time_seconds": checkpoint.metadata.execution_time_seconds,
            "remaining_steps": checkpoint.metadata.total_steps
            - len(checkpoint.metadata.completed_steps)
            - len(checkpoint.metadata.failed_steps),
        }

    async def get_workspace_stats(self, workspace_id: str) -> Dict[str, Any]:
        """
        Get checkpoint statistics for a workspace.

        Args:
            workspace_id: Workspace ID

        Returns:
            Statistics dictionary
        """
        checkpoints = await self.list_checkpoints(workspace_id=workspace_id, limit=1000)

        if not checkpoints:
            return {
                "total_checkpoints": 0,
                "average_progress": 0.0,
                "total_cost": 0.0,
                "total_tokens": 0,
            }

        total_checkpoints = len(checkpoints)
        total_progress = sum(c.progress_percentage for c in checkpoints)
        total_cost = sum(c.total_cost_usd for c in checkpoints)
        total_tokens = sum(c.total_tokens_used for c in checkpoints)

        return {
            "total_checkpoints": total_checkpoints,
            "average_progress": total_progress / total_checkpoints,
            "total_cost": total_cost,
            "total_tokens": total_tokens,
            "oldest_checkpoint": min(c.created_at for c in checkpoints).isoformat(),
            "newest_checkpoint": max(c.created_at for c in checkpoints).isoformat(),
        }
