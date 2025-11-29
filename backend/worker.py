"""
Background Event Processing Worker for RaptorFlow

Consumes events from RaptorBus and handles them asynchronously.
Provides event-driven processing for agent coordination, system monitoring,
and operational tasks.

Features:
- Event handlers for workspace creation, agent management, etc.
- Graceful shutdown and error handling
- Multiple handler registration
- Event enrichment and logging
"""

import asyncio
import json
from typing import Callable, Dict, Any, Optional

from backend.bus.raptor_bus import get_bus, RaptorBus
from backend.utils.logging_config import get_logger, setup_logging, set_correlation_id
from backend.core.request_context import set_request_context, RequestContext
from backend.services.agent_registry import agent_registry

logger = get_logger("worker")

# Global registry of event handlers
EVENT_HANDLERS: Dict[str, Callable] = {}


def register_event_handler(event_type: str):
    """
    Decorator to register an event handler for specific event types.

    Usage:
        @register_event_handler("workspace.created")
        async def handle_workspace_created(event: dict):
            # Handle event
            pass
    """
    def decorator(handler: Callable):
        if event_type in EVENT_HANDLERS:
            logger.warning(f"Event handler for {event_type} already exists, replacing")
        EVENT_HANDLERS[event_type] = handler
        logger.info(f"Registered event handler for {event_type}: {handler.__name__}")
        return handler
    return decorator


@register_event_handler("workspace.created")
async def handle_workspace_created(event: Dict[str, Any]) -> None:
    """Handle workspace creation by seeding with core agents."""
    workspace_id = event.get("payload", {}).get("workspace_id")
    if not workspace_id:
        logger.warning("Workspace created event missing workspace_id", event=event)
        return

    try:
        logger.info("Seeding workspace with core agents", workspace_id=workspace_id)
        await agent_registry.ensure_core_agents_for_workspace(workspace_id)
        logger.info("Successfully seeded workspace", workspace_id=workspace_id)
    except Exception as e:
        logger.error("Failed to seed workspace with agents",
                    workspace_id=workspace_id, error=str(e))


@register_event_handler("test.event")
async def handle_test_event(event: Dict[str, Any]) -> None:
    """Handle test events for smoke testing."""
    logger.info("Received test event", payload=event.get("payload"))


async def run_event_loop(redis_client, logger) -> None:
    """
    Main event processing loop according to master skeleton.

    Subscribes to events and processes them as they arrive.
    """
    processor = EventProcessor(await get_bus(), logger)
    await processor.start()

    try:
        # Keep the processor running
        await asyncio.Future()  # Run forever
    except KeyboardInterrupt:
        logger.info("Received shutdown signal")
    finally:
        await processor.stop()


class EventProcessor:
    """Processes events from the RaptorBus."""

    def __init__(self, bus: RaptorBus, logger_instance):
        self.bus = bus
        self.logger = logger_instance
        self.handlers = EVENT_HANDLERS.copy()
        self.is_running = False

    async def start(self) -> None:
        """Start event processing."""
        self.is_running = True
        await self.bus.connect()

        # Subscribe to all registered event types
        for event_type in self.handlers:
            await self.bus.subscribe_to_channel(
                f"raptorflow.events.{event_type}",
                self._create_handler_wrapper(event_type)
            )

        logger.info("Event processor started")

    def _create_handler_wrapper(self, event_type: str) -> Callable:
        """Create a wrapper that calls the registered handler with event envelope."""
        async def wrapper(envelope_json: str) -> None:
            try:
                # Parse the envelope
                envelope = json.loads(envelope_json)

                # Set correlation ID for this processing context
                correlation_id = envelope.get("correlation_id")
                if correlation_id:
                    set_correlation_id(correlation_id)

                # Set request context if workspace_id available
                workspace_id = envelope.get("workspace_id")
                if workspace_id:
                    ctx = RequestContext(workspace_id=workspace_id, correlation_id=correlation_id)
                    set_request_context(ctx)

                logger.info(f"Processing event {event_type}",
                           correlation_id=correlation_id,
                           workspace_id=workspace_id)

                # Get the handler
                handler = self.handlers.get(event_type)
                if handler:
                    await handler(envelope)
                else:
                    logger.warning(f"No handler for event type {event_type}")

            except Exception as e:
                logger.error(f"Event processing error: {e}", event_type=event_type)

        return wrapper

    async def stop(self) -> None:
        """Stop event processing."""
        self.is_running = False
        await self.bus.disconnect()
        logger.info("Event processor stopped")


async def main():
    """Main entry point for the worker."""
    setup_logging()
    redis_client = None  # Will be handled by get_bus internally

    try:
        logger.info("Starting RaptorFlow worker")
        await run_event_loop(redis_client, logger)
    except Exception as e:
        logger.error(f"Worker failed: {e}")
        raise
    finally:
        logger.info("Worker shutting down")


if __name__ == "__main__":
    asyncio.run(main())
