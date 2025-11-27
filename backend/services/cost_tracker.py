"""
Cost Tracking Service

Service for logging and retrieving AI agent costs. Handles database operations
for cost tracking, including logging individual actions and retrieving
cost summaries for workspaces.
"""

import structlog
from typing import List, Optional
from uuid import UUID
from decimal import Decimal

from backend.models.cost import CostLog
from backend.services.supabase_client import supabase_client

logger = structlog.get_logger(__name__)


class CostTrackerService:
    """
    Service for tracking AI agent costs.

    This service provides methods to log costs for individual AI actions
    and retrieve cost summaries. It integrates with the cost_logs database
    table and provides a clean API for cost tracking operations.
    """

    def __init__(self):
        """Initialize the cost tracker service."""
        self.db = supabase_client

    async def log_cost(
        self,
        workspace_id: UUID,
        correlation_id: UUID,
        agent_name: str,
        action_name: str,
        input_tokens: int,
        output_tokens: int,
    ) -> CostLog:
        """
        Log the estimated cost of an AI agent action.

        This method creates a cost log entry for a specific AI operation,
        calculates the estimated cost using the predefined formula, and
        persists it to the database.

        Args:
            workspace_id: The workspace identifier for multi-tenancy
            correlation_id: Unique identifier for tracking across workflows
            agent_name: Name or identifier of the agent performing the action
            action_name: Description of the action being performed
            input_tokens: Number of input tokens processed
            output_tokens: Number of output tokens generated

        Returns:
            The created CostLog record

        Raises:
            Exception: If there's an error saving to the database
        """
        try:
            # Create cost log with automatic cost calculation
            cost_log = CostLog.create_log(
                workspace_id=workspace_id,
                correlation_id=correlation_id,
                agent_name=agent_name,
                action_name=action_name,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
            )

            # Prepare data for database insertion
            log_data = {
                "workspace_id": str(cost_log.workspace_id),
                "correlation_id": str(cost_log.correlation_id),
                "agent_name": cost_log.agent_name,
                "action_name": cost_log.action_name,
                "input_tokens": cost_log.input_tokens,
                "output_tokens": cost_log.output_tokens,
                "estimated_cost_usd": str(cost_log.estimated_cost_usd),  # Store as string to preserve precision
            }

            # Insert into database
            result = await self.db.insert("cost_logs", log_data)

            logger.info(
                "Cost logged successfully",
                workspace_id=str(workspace_id),
                correlation_id=str(correlation_id),
                agent_name=agent_name,
                action_name=action_name,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                estimated_cost_usd=float(cost_log.estimated_cost_usd),
            )

            return cost_log

        except Exception as e:
            logger.error(
                "Failed to log cost",
                workspace_id=str(workspace_id),
                correlation_id=str(correlation_id),
                agent_name=agent_name,
                action_name=action_name,
                error=str(e),
            )
            raise

    async def get_costs_for_workspace(
        self,
        workspace_id: UUID,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[CostLog]:
        """
        Retrieve all cost logs for a specific workspace.

        This method fetches historical cost data for a workspace, ordered
        by creation time (newest first). Results can be paginated using
        limit and offset parameters.

        Args:
            workspace_id: The workspace identifier
            limit: Maximum number of records to return (optional)
            offset: Number of records to skip (optional)

        Returns:
            List of CostLog records for the workspace

        Raises:
            Exception: If there's an error retrieving from the database
        """
        try:
            # Query cost logs for workspace
            query = self.db.client.table("cost_logs").select("*").eq("workspace_id", str(workspace_id))

            # Add ordering (newest first)
            query = query.order("created_at", desc=True)

            # Add pagination if specified
            if limit:
                query = query.limit(limit)
            if offset:
                query = query.range(offset, offset + (limit - 1) if limit else None)

            result = query.execute()
            records = result.data or []

            # Convert database records to CostLog objects
            cost_logs = []
            for record in records:
                try:
                    cost_log = CostLog(
                        id=UUID(record["id"]),
                        workspace_id=UUID(record["workspace_id"]),
                        correlation_id=UUID(record["correlation_id"]),
                        agent_name=record["agent_name"],
                        action_name=record["action_name"],
                        input_tokens=record["input_tokens"],
                        output_tokens=record["output_tokens"],
                        estimated_cost_usd=Decimal(str(record["estimated_cost_usd"])),  # Convert from string safely
                        created_at=record["created_at"],
                    )
                    cost_logs.append(cost_log)
                except (KeyError, ValueError) as e:
                    logger.warning(
                        "Skipping invalid cost log record",
                        record_id=record.get("id"),
                        error=str(e),
                    )

            logger.info(
                "Retrieved cost logs for workspace",
                workspace_id=str(workspace_id),
                count=len(cost_logs),
                limit=limit,
                offset=offset,
            )

            return cost_logs

        except Exception as e:
            logger.error(
                "Failed to retrieve cost logs for workspace",
                workspace_id=str(workspace_id),
                error=str(e),
            )
            raise

    async def get_total_cost_for_workspace(self, workspace_id: UUID) -> Decimal:
        """
        Calculate the total estimated cost for a workspace.

        This method aggregates all cost logs for a workspace to provide
        a total cost summary.

        Args:
            workspace_id: The workspace identifier

        Returns:
            Total estimated cost in USD as Decimal

        Raises:
            Exception: If there's an error calculating the total
        """
        try:
            cost_logs = await self.get_costs_for_workspace(workspace_id)
            total_cost = sum(log.estimated_cost_usd for log in cost_logs)

            logger.info(
                "Calculated total cost for workspace",
                workspace_id=str(workspace_id),
                total_cost=float(total_cost),
            )

            return total_cost

        except Exception as e:
            logger.error(
                "Failed to calculate total cost for workspace",
                workspace_id=str(workspace_id),
                error=str(e),
            )
            raise


# Global service instance
cost_tracker = CostTrackerService()
