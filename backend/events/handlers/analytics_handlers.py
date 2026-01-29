"""
Analytics event handlers.
Handle events that record metrics, track performance, and update analytics.
"""

import logging
from types import AgentExecutionEvent, ContentGeneratedEvent, Event, EventType
from typing import Any, Dict, Optional

from ...infrastructure.bigquery import BigQueryClient
from ...redis.usage import UsageTracker

logger = logging.getLogger(__name__)


async def on_agent_execution_started(event: Event) -> None:
    """Handle agent execution started event - records start time and metrics."""
    try:
        workspace_id = event.workspace_id
        user_id = event.user_id
        agent_name = event.data.get("agent_name") if event.data else None
        execution_id = event.data.get("execution_id") if event.data else None
        input_data = event.data.get("input_data") if event.data else {}

        if not all([agent_name, execution_id]):
            logger.warning("Agent execution started event missing required data")
            return

        logger.info(f"Agent execution started: {agent_name} ({execution_id})")

        # Record execution start in analytics
        bigquery = BigQueryClient()
        if bigquery.is_enabled():
            await bigquery.insert_rows(
                "agent_executions",
                [
                    {
                        "execution_id": execution_id,
                        "workspace_id": workspace_id,
                        "user_id": user_id,
                        "agent_name": agent_name,
                        "status": "started",
                        "started_at": event.timestamp,
                        "input_data": input_data,
                        "created_at": event.timestamp,
                    }
                ],
            )

        # Record usage metrics
        usage_tracker = UsageTracker()
        await usage_tracker.record_agent_execution_start(
            workspace_id=workspace_id,
            user_id=user_id,
            agent_name=agent_name,
            execution_id=execution_id,
        )

        logger.debug(f"Agent execution start recorded: {execution_id}")

    except Exception as e:
        logger.error(f"Failed to handle agent execution started event: {e}")


async def on_agent_execution_completed(event: Event) -> None:
    """Handle agent execution completed event - records completion metrics."""
    try:
        workspace_id = event.workspace_id
        user_id = event.user_id
        agent_name = event.data.get("agent_name") if event.data else None
        execution_id = event.data.get("execution_id") if event.data else None
        output_data = event.data.get("output_data") if event.data else {}
        execution_time = event.data.get("execution_time") if event.data else None
        tokens_used = event.data.get("tokens_used", 0) if event.data else 0
        cost = event.data.get("cost", 0.0) if event.data else 0.0

        if not all([agent_name, execution_id]):
            logger.warning("Agent execution completed event missing required data")
            return

        logger.info(
            f"Agent execution completed: {agent_name} ({execution_id}) in {execution_time}s"
        )

        # Update execution record in analytics
        bigquery = BigQueryClient()
        if bigquery.is_enabled():
            await bigquery.insert_rows(
                "agent_executions",
                [
                    {
                        "execution_id": execution_id,
                        "workspace_id": workspace_id,
                        "user_id": user_id,
                        "agent_name": agent_name,
                        "status": "completed",
                        "completed_at": event.timestamp,
                        "execution_time": execution_time,
                        "tokens_used": tokens_used,
                        "cost": cost,
                        "output_data": output_data,
                        "updated_at": event.timestamp,
                    }
                ],
            )

        # Record usage metrics
        usage_tracker = UsageTracker()
        await usage_tracker.record_agent_execution_complete(
            workspace_id=workspace_id,
            user_id=user_id,
            agent_name=agent_name,
            execution_id=execution_id,
            tokens_used=tokens_used,
            cost=cost,
            execution_time=execution_time,
        )

        logger.debug(f"Agent execution completion recorded: {execution_id}")

    except Exception as e:
        logger.error(f"Failed to handle agent execution completed event: {e}")


async def on_agent_execution_failed(event: Event) -> None:
    """Handle agent execution failed event - records failure metrics."""
    try:
        workspace_id = event.workspace_id
        user_id = event.user_id
        agent_name = event.data.get("agent_name") if event.data else None
        execution_id = event.data.get("execution_id") if event.data else None
        error = event.data.get("error") if event.data else None
        execution_time = event.data.get("execution_time") if event.data else None

        if not all([agent_name, execution_id]):
            logger.warning("Agent execution failed event missing required data")
            return

        logger.warning(
            f"Agent execution failed: {agent_name} ({execution_id}) - {error}"
        )

        # Update execution record in analytics
        bigquery = BigQueryClient()
        if bigquery.is_enabled():
            await bigquery.insert_rows(
                "agent_executions",
                [
                    {
                        "execution_id": execution_id,
                        "workspace_id": workspace_id,
                        "user_id": user_id,
                        "agent_name": agent_name,
                        "status": "failed",
                        "failed_at": event.timestamp,
                        "execution_time": execution_time,
                        "error": error,
                        "updated_at": event.timestamp,
                    }
                ],
            )

        # Record failure metrics
        usage_tracker = UsageTracker()
        await usage_tracker.record_agent_execution_failure(
            workspace_id=workspace_id,
            user_id=user_id,
            agent_name=agent_name,
            execution_id=execution_id,
            error=error,
            execution_time=execution_time,
        )

        logger.debug(f"Agent execution failure recorded: {execution_id}")

    except Exception as e:
        logger.error(f"Failed to handle agent execution failed event: {e}")


async def on_content_generated(event: Event) -> None:
    """Handle content generated event - records content metrics."""
    try:
        workspace_id = event.workspace_id
        user_id = event.user_id
        content_type = event.data.get("content_type") if event.data else None
        content_id = event.data.get("content_id") if event.data else None
        tokens_used = event.data.get("tokens_used", 0) if event.data else 0
        cost = event.data.get("cost", 0.0) if event.data else 0.0
        agent_name = event.data.get("agent_name") if event.data else None

        if not all([content_type, content_id]):
            logger.warning("Content generated event missing required data")
            return

        logger.info(f"Content generated: {content_type} ({content_id})")

        # Record content generation in analytics
        bigquery = BigQueryClient()
        if bigquery.is_enabled():
            await bigquery.insert_rows(
                "content_generations",
                [
                    {
                        "content_id": content_id,
                        "workspace_id": workspace_id,
                        "user_id": user_id,
                        "content_type": content_type,
                        "agent_name": agent_name,
                        "tokens_used": tokens_used,
                        "cost": cost,
                        "generated_at": event.timestamp,
                        "created_at": event.timestamp,
                    }
                ],
            )

        # Record usage
        usage_tracker = UsageTracker()
        await usage_tracker.record_usage(
            workspace_id=workspace_id,
            tokens=tokens_used,
            cost=cost,
            agent=agent_name or content_type,
        )

        logger.debug(f"Content generation recorded: {content_id}")

    except Exception as e:
        logger.error(f"Failed to handle content generated event: {e}")


async def on_move_started(event: Event) -> None:
    """Handle move started event - records move initiation."""
    try:
        workspace_id = event.workspace_id
        user_id = event.user_id
        move_id = event.data.get("move_id") if event.data else None
        move_type = event.data.get("move_type") if event.data else None
        agent = event.data.get("agent") if event.data else None

        if not all([move_id, move_type]):
            logger.warning("Move started event missing required data")
            return

        logger.info(f"Move started: {move_type} ({move_id})")

        # Record move start in analytics
        bigquery = BigQueryClient()
        if bigquery.is_enabled():
            await bigquery.insert_rows(
                "moves",
                [
                    {
                        "move_id": move_id,
                        "workspace_id": workspace_id,
                        "user_id": user_id,
                        "move_type": move_type,
                        "agent": agent,
                        "status": "started",
                        "started_at": event.timestamp,
                        "created_at": event.timestamp,
                    }
                ],
            )

        logger.debug(f"Move start recorded: {move_id}")

    except Exception as e:
        logger.error(f"Failed to handle move started event: {e}")


async def on_move_completed(event: Event) -> None:
    """Handle move completed event - records successful completion."""
    try:
        workspace_id = event.workspace_id
        user_id = event.user_id
        move_id = event.data.get("move_id") if event.data else None
        result = event.data.get("result") if event.data else {}
        execution_time = event.data.get("execution_time") if event.data else None

        if not move_id:
            logger.warning("Move completed event missing move_id")
            return

        logger.info(f"Move completed: {move_id}")

        # Update move record in analytics
        bigquery = BigQueryClient()
        if bigquery.is_enabled():
            await bigquery.insert_rows(
                "moves",
                [
                    {
                        "move_id": move_id,
                        "workspace_id": workspace_id,
                        "user_id": user_id,
                        "status": "completed",
                        "completed_at": event.timestamp,
                        "execution_time": execution_time,
                        "result": result,
                        "updated_at": event.timestamp,
                    }
                ],
            )

        logger.debug(f"Move completion recorded: {move_id}")

    except Exception as e:
        logger.error(f"Failed to handle move completed event: {e}")


async def on_move_failed(event: Event) -> None:
    """Handle move failed event - records failure details."""
    try:
        workspace_id = event.workspace_id
        user_id = event.user_id
        move_id = event.data.get("move_id") if event.data else None
        error = event.data.get("error") if event.data else None
        execution_time = event.data.get("execution_time") if event.data else None

        if not move_id:
            logger.warning("Move failed event missing move_id")
            return

        logger.warning(f"Move failed: {move_id} - {error}")

        # Update move record in analytics
        bigquery = BigQueryClient()
        if bigquery.is_enabled():
            await bigquery.insert_rows(
                "moves",
                [
                    {
                        "move_id": move_id,
                        "workspace_id": workspace_id,
                        "user_id": user_id,
                        "status": "failed",
                        "failed_at": event.timestamp,
                        "execution_time": execution_time,
                        "error": error,
                        "updated_at": event.timestamp,
                    }
                ],
            )

        logger.debug(f"Move failure recorded: {move_id}")

    except Exception as e:
        logger.error(f"Failed to handle move failed event: {e}")


# Register all handlers
def register_analytics_handlers():
    """Register all analytics event handlers."""
    from bus import subscribe_event

    handlers = [
        (EventType.AGENT_EXECUTION_STARTED, on_agent_execution_started),
        (EventType.AGENT_EXECUTION_COMPLETED, on_agent_execution_completed),
        (EventType.AGENT_EXECUTION_FAILED, on_agent_execution_failed),
        (EventType.CONTENT_GENERATED, on_content_generated),
        (EventType.MOVE_STARTED, on_move_started),
        (EventType.MOVE_COMPLETED, on_move_completed),
        (EventType.MOVE_FAILED, on_move_failed),
    ]

    for event_type, handler in handlers:
        subscribe_event(event_type, handler)
        logger.debug(f"Registered analytics handler for {event_type.value}")
