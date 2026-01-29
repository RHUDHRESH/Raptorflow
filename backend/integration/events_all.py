"""
Event bus integration for all modules.
Wires all event handlers and manages cross-module communication.
"""

import json
import logging
from typing import Any, Callable, Dict, List, Optional

from .redis.client import Redis

logger = logging.getLogger(__name__)


class EventBus:
    """
    Central event bus for system-wide event handling.
    """

    def __init__(self, redis_client: Redis):
        self.redis_client = redis_client
        self.handlers = {}  # event_type -> list of handlers
        self.event_history = []  # Store recent events

    async def emit(
        self, event_type: str, data: Dict[str, Any], target_workspace: str = None
    ):
        """
        Emit event to all subscribers.

        Args:
            event_type: Type of event
            data: Event data
            target_workspace: Optional workspace filter
        """
        try:
            event = {
                "type": event_type,
                "data": data,
                "timestamp": time.time(),
                "target_workspace": target_workspace,
            }

            # Store in Redis for persistence
            await self._store_event(event)

            # Notify subscribers
            await self._notify_subscribers(event)

            # Add to history
            self.event_history.append(event)
            if len(self.event_history) > 1000:
                self.event_history = self.event_history[-1000:]

            logger.info(f"Emitted event: {event_type}")

        except Exception as e:
            logger.error(f"Error emitting event {event_type}: {e}")

    async def subscribe(
        self, event_type: str, handler: Callable, workspace_id: str = None
    ):
        """
        Subscribe to event type.

        Args:
            event_type: Event type to subscribe to
            handler: Handler function
            workspace_id: Optional workspace filter
        """
        if event_type not in self.handlers:
            self.handlers[event_type] = []

        self.handlers[event_type].append(
            {
                "handler": handler,
                "workspace_id": workspace_id,
                "subscribed_at": time.time(),
            }
        )

        logger.info(f"Subscribed to {event_type} events")

    async def unsubscribe(self, event_type: str, handler: Callable):
        """
        Unsubscribe from event type.

        Args:
            event_type: Event type
            handler: Handler function
        """
        if event_type in self.handlers:
            self.handlers[event_type] = [
                h for h in self.handlers[event_type] if h["handler"] != handler
            ]

        logger.info(f"Unsubscribed from {event_type} events")

    async def _store_event(self, event: Dict[str, Any]):
        """Store event in Redis."""
        key = f"event:{event['type']}:{event['timestamp']}"
        await self.redis_client.setex(key, 3600, json.dumps(event))

    async def _notify_subscribers(self, event: Dict[str, Any]):
        """Notify all subscribers of the event."""
        event_type = event["type"]
        target_workspace = event.get("target_workspace")

        if event_type not in self.handlers:
            return

        for handler_info in self.handlers[event_type]:
            # Check workspace filter
            if target_workspace and handler_info.get("workspace_id"):
                if handler_info["workspace_id"] != target_workspace:
                    continue

            try:
                await handler_info["handler"](event)
            except Exception as e:
                logger.error(f"Error in event handler: {e}")


# Global event bus instance
_event_bus: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    """Get the global event bus instance."""
    return _event_bus


def set_event_bus(event_bus: EventBus):
    """Set the global event bus instance."""
    global _event_bus
    _event_bus = event_bus


async def wire_all_event_handlers(
    redis_client: Redis, memory_controller, cognitive_engine, billing_service
):
    """
    Wire all event handlers for system integration.

    Args:
        redis_client: Redis client
        memory_controller: Memory controller
        cognitive_engine: Cognitive engine
        billing_service: Billing service
    """
    try:
        # Create event bus
        event_bus = EventBus(redis_client)
        set_event_bus(event_bus)

        # Wire foundation events
        await _wire_foundation_events(event_bus, memory_controller)

        # Wire ICP events
        await _wire_icp_events(event_bus, memory_controller)

        # Wire content events
        await _wire_content_events(event_bus, memory_controller, cognitive_engine)

        # Wire billing events
        await _wire_billing_events(event_bus, billing_service)

        # Wire approval events
        await _wire_approval_events(event_bus, cognitive_engine)

        # Wire usage events
        await _wire_usage_events(event_bus, billing_service)

        logger.info("All event handlers wired successfully")

    except Exception as e:
        logger.error(f"Error wiring event handlers: {e}")


async def _wire_foundation_events(event_bus: EventBus, memory_controller):
    """Wire foundation-related events."""

    async def on_foundation_updated(event):
        """Handle foundation update event."""
        data = event["data"]
        workspace_id = data.get("workspace_id")

        if workspace_id:
            # Re-index foundation in memory
            from memory.vectorizers.foundation import FoundationVectorizer

            vectorizer = FoundationVectorizer(memory_controller)
            await vectorizer.update_foundation_vectors(workspace_id)

            logger.info(f"Re-indexed foundation for workspace {workspace_id}")

    await event_bus.subscribe("foundation.updated", on_foundation_updated)
    await event_bus.subscribe("foundation.created", on_foundation_updated)


async def _wire_icp_events(event_bus: EventBus, memory_controller):
    """Wire ICP-related events."""

    async def on_icp_created(event):
        """Handle ICP creation event."""
        data = event["data"]
        workspace_id = data.get("workspace_id")

        if workspace_id:
            # Add ICP to graph memory
            from memory.graph_builders.icp import ICPEntityBuilder

            builder = ICPEntityBuilder()
            await builder.build_icp_entity(workspace_id, data)

            logger.info(f"Added ICP to graph for workspace {workspace_id}")

    await event_bus.subscribe("icp.created", on_icp_created)
    await event_bus.subscribe("icp.updated", on_icp_created)


async def _wire_content_events(
    event_bus: EventBus, memory_controller, cognitive_engine
):
    """Wire content-related events."""

    async def on_content_generated(event):
        """Handle content generation event."""
        data = event["data"]
        workspace_id = data.get("workspace_id")
        content = data.get("content")

        if workspace_id and content:
            # Store in memory
            await memory_controller.store(
                workspace_id=workspace_id,
                memory_type="conversation",
                content=content[:1000],  # Truncate for memory
                metadata={
                    "type": "generated_content",
                    "agent": data.get("agent"),
                    "content_type": data.get("content_type"),
                    "quality_score": data.get("quality_score"),
                },
            )

            # Trigger analytics
            await event_bus.emit(
                "analytics.content_generated",
                {
                    "workspace_id": workspace_id,
                    "content_length": len(content),
                    "agent": data.get("agent"),
                },
            )

    await event_bus.subscribe("content.generated", on_content_generated)


async def _wire_billing_events(event_bus: EventBus, billing_service):
    """Wire billing-related events."""

    async def on_usage_recorded(event):
        """Handle usage recording event."""
        data = event["data"]
        workspace_id = data.get("workspace_id")
        tokens = data.get("tokens_used", 0)
        cost = data.get("cost_usd", 0.0)

        if workspace_id and (tokens > 0 or cost > 0):
            # Record usage
            await billing_service.record_usage(workspace_id, tokens, cost)

            # Check limits
            await billing_service.check_usage_limits(workspace_id)

    await event_bus.subscribe("usage.recorded", on_usage_recorded)


async def _wire_approval_events(event_bus: EventBus, cognitive_engine):
    """Wire approval-related events."""

    async def on_approval_requested(event):
        """Handle approval request event."""
        data = event["data"]

        # Send notification
        await event_bus.emit(
            "notification.approval_required",
            {
                "workspace_id": data.get("workspace_id"),
                "user_id": data.get("user_id"),
                "gate_id": data.get("gate_id"),
                "risk_level": data.get("risk_level"),
            },
        )

    async def on_approval_timeout(event):
        """Handle approval timeout event."""
        data = event["data"]

        # Send timeout notification
        await event_bus.emit(
            "notification.approval_timeout",
            {
                "workspace_id": data.get("workspace_id"),
                "user_id": data.get("user_id"),
                "gate_id": data.get("gate_id"),
            },
        )

    await event_bus.subscribe("approval.requested", on_approval_requested)
    await event_bus.subscribe("approval.timeout", on_approval_timeout)


async def _wire_usage_events(event_bus: EventBus, billing_service):
    """Wire usage-related events."""

    async def on_limit_reached(event):
        """Handle usage limit reached event."""
        data = event["data"]
        workspace_id = data.get("workspace_id")

        # Send notification
        await event_bus.emit(
            "notification.usage_limit_reached",
            {
                "workspace_id": workspace_id,
                "limit_type": data.get("limit_type"),
                "current_usage": data.get("current_usage"),
                "limit": data.get("limit"),
            },
        )

        # Suspend operations if needed
        if data.get("suspend_operations"):
            await event_bus.emit(
                "system.suspend_operations",
                {"workspace_id": workspace_id, "reason": "usage_limit_reached"},
            )

    await event_bus.subscribe("usage.limit_reached", on_limit_reached)


# Event emitter convenience functions
async def emit_foundation_updated(workspace_id: str, foundation_data: Dict[str, Any]):
    """Emit foundation updated event."""
    event_bus = get_event_bus()
    if event_bus:
        await event_bus.emit(
            "foundation.updated",
            {"workspace_id": workspace_id, "foundation_data": foundation_data},
        )


async def emit_icp_created(workspace_id: str, icp_data: Dict[str, Any]):
    """Emit ICP created event."""
    event_bus = get_event_bus()
    if event_bus:
        await event_bus.emit(
            "icp.created", {"workspace_id": workspace_id, "icp_data": icp_data}
        )


async def emit_content_generated(
    workspace_id: str,
    content: str,
    agent: str,
    content_type: str,
    quality_score: float = None,
):
    """Emit content generated event."""
    event_bus = get_event_bus()
    if event_bus:
        await event_bus.emit(
            "content.generated",
            {
                "workspace_id": workspace_id,
                "content": content,
                "agent": agent,
                "content_type": content_type,
                "quality_score": quality_score,
            },
        )
