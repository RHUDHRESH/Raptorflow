"""
Agent Runs Service

Tracks agent execution runs and their lifecycle.
Provides helpers for starting, completing, and querying agent runs.
"""

from datetime import datetime
from typing import Optional, Dict, Any, List
from uuid import uuid4
import json

from backend.utils.logging_config import get_logger
from backend.core.request_context import get_current_workspace_id
from backend.services.supabase_client import supabase_client

logger = get_logger("agent_runs")


class AgentRunsService:
    """
    Service for managing agent run lifecycles.

    Provides helpers for:
    - Starting runs (with metadata)
    - Completing runs (success/failure)
    - Querying run history
    - Integration with audit logging and cost tracking
    """

    def __init__(self):
        self.supabase = supabase_client

    async def start_agent_run(
        self,
        *,
        workspace_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        actor_user_id: Optional[str] = None,
        run_type: str = "task",
        input_payload: Optional[Dict[str, Any]] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Start a new agent run and return the run ID.

        Args:
            workspace_id: Target workspace (uses context if not provided)
            agent_id: Agent executing the run
            actor_user_id: User initiating the run
            run_type: Type of run (task, workflow, agent, etc.)
            input_payload: Input data for the run
            metadata: Additional metadata

        Returns:
            run_id for tracking
        """
        run_id = str(uuid4())
        resolved_workspace_id = workspace_id or get_current_workspace_id()

        run_data = {
            "id": run_id,
            "workspace_id": resolved_workspace_id,
            "agent_id": agent_id,
            "actor_user_id": actor_user_id,
            "run_type": run_type,
            "status": "running",
            "started_at": datetime.utcnow().isoformat(),
            "input_payload": json.dumps(input_payload) if input_payload else None,
            "metadata": json.dumps(metadata) if metadata else None,
        }

        try:
            await self.supabase.insert("agent_runs", run_data)

            logger.info(
                "Agent run started",
                run_id=run_id,
                workspace_id=resolved_workspace_id,
                agent_id=agent_id,
                actor_user_id=actor_user_id,
                run_type=run_type
            )

        except Exception as e:
            logger.error(
                "Failed to start agent run",
                run_id=run_id,
                workspace_id=resolved_workspace_id,
                error=str(e)
            )
            raise

        return run_id

    async def complete_agent_run(
        self,
        run_id: str,
        *,
        status: str = "completed",
        result_summary: Optional[str] = None,
        output_payload: Optional[Dict[str, Any]] = None,
        error_message: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Complete an agent run with final status and results.

        Args:
            run_id: Run ID to update
            status: Final status (completed, failed, cancelled)
            result_summary: Brief summary of results
            output_payload: Output data from the run
            error_message: Error details if failed
            metadata: Additional metadata to merge
        """
        update_data = {
            "status": status,
            "completed_at": datetime.utcnow().isoformat(),
        }

        if result_summary:
            update_data["result_summary"] = result_summary

        if output_payload:
            update_data["output_payload"] = json.dumps(output_payload)

        if error_message:
            update_data["error_message"] = error_message

        if metadata:
            # Note: In real implementation, you'd merge with existing metadata
            update_data["metadata"] = json.dumps(metadata)

        try:
            # Update the run record
            await self.supabase.update(
                "agent_runs",
                update_data,
                filters={"id": run_id}
            )

            logger.info(
                f"Agent run {status}",
                run_id=run_id,
                status=status,
                error_message=error_message[:200] if error_message else None
            )

        except Exception as e:
            logger.error(
                f"Failed to complete agent run {run_id}",
                run_id=run_id,
                status=status,
                error=str(e)
            )

    async def get_agent_run(self, run_id: str, workspace_id: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """
        Get details of a specific agent run.

        Args:
            run_id: Run ID to retrieve
            workspace_id: Workspace context for security (will use context var if not provided)

        Returns:
            Run data dict or None if not found
        """
        resolved_workspace_id = workspace_id or get_current_workspace_id()

        try:
            result = self.supabase.client.table("agent_runs").select("*").eq("id", run_id).eq("workspace_id", resolved_workspace_id).execute()

            if result.data and len(result.data) > 0:
                run_data = result.data[0]
                # Parse JSON fields
                if run_data.get("input_payload"):
                    run_data["input_payload"] = json.loads(run_data["input_payload"])
                if run_data.get("output_payload"):
                    run_data["output_payload"] = json.loads(run_data["output_payload"])
                if run_data.get("metadata"):
                    run_data["metadata"] = json.loads(run_data["metadata"])

                return run_data

            return None

        except Exception as e:
            logger.error(f"Failed to get agent run {run_id}", run_id=run_id, error=str(e))
            return None

    async def list_agent_runs(
        self,
        workspace_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        actor_user_id: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        List agent runs with optional filtering.

        Args:
            workspace_id: Filter by workspace
            agent_id: Filter by agent
            actor_user_id: Filter by user who started runs
            status: Filter by status (running, completed, failed)
            limit: Max results to return
            offset: Pagination offset

        Returns:
            List of run records
        """
        resolved_workspace_id = workspace_id or get_current_workspace_id()

        try:
            query = self.supabase.client.table("agent_runs").select("*").eq("workspace_id", resolved_workspace_id)

            if agent_id:
                query = query.eq("agent_id", agent_id)
            if actor_user_id:
                query = query.eq("actor_user_id", actor_user_id)
            if status:
                query = query.eq("status", status)

            query = query.order("started_at", desc=True).range(offset, offset + limit - 1)
            result = query.execute()

            runs = []
            for run in result.data:
                # Parse JSON fields
                if run.get("input_payload"):
                    run["input_payload"] = json.loads(run["input_payload"])
                if run.get("output_payload"):
                    run["output_payload"] = json.loads(run["output_payload"])
                if run.get("metadata"):
                    run["metadata"] = json.loads(run["metadata"])
                runs.append(run)

            return runs

        except Exception as e:
            logger.error(
                "Failed to list agent runs",
                workspace_id=resolved_workspace_id,
                error=str(e)
            )
            return []

    async def get_run_stats(
        self,
        workspace_id: Optional[str] = None,
        agent_id: Optional[str] = None,
        days: int = 7
    ) -> Dict[str, Any]:
        """
        Get statistics about agent runs.

        Args:
            workspace_id: Target workspace
            agent_id: Specific agent to get stats for
            days: Number of days to look back

        Returns:
            Stats dict with run counts, success rates, etc.
        """
        resolved_workspace_id = workspace_id or get_current_workspace_id()

        try:
            # Calculate date threshold
            since_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            since_date = since_date.replace(day=since_date.day - days)

            query = self.supabase.client.table("agent_runs").select("status, run_type").eq("workspace_id", resolved_workspace_id).gte("started_at", since_date.isoformat())

            if agent_id:
                query = query.eq("agent_id", agent_id)

            result = query.execute()

            # Aggregate stats
            stats = {
                "total_runs": len(result.data),
                "completed_runs": 0,
                "failed_runs": 0,
                "running_runs": 0,
                "cancelled_runs": 0,
                "runs_by_type": {},
                "period_days": days,
                "workspace_id": resolved_workspace_id,
            }

            for run in result.data:
                status = run["status"]
                run_type = run["run_type"]

                stats["runs_by_type"][run_type] = stats["runs_by_type"].get(run_type, 0) + 1

                if status == "completed":
                    stats["completed_runs"] += 1
                elif status == "failed":
                    stats["failed_runs"] += 1
                elif status == "running":
                    stats["running_runs"] += 1
                elif status == "cancelled":
                    stats["cancelled_runs"] += 1

            return stats

        except Exception as e:
            logger.error(
                "Failed to get run stats",
                workspace_id=resolved_workspace_id,
                error=str(e)
            )
            return {}


# Global service instance
agent_runs = AgentRunsService()
