"""
Event bus implementation using Redis pub/sub for distributed event handling.
"""

import asyncio
import json
import logging
import weakref
from datetime import datetime
from typing import Callable, Dict, List, Optional, Set

from ..redis.client import RedisClient
from ..redis.pubsub import PubSubService
from .types import Event, EventType

logger = logging.getLogger(__name__)


class EventBus:
    """Singleton event bus for internal system events."""

    _instance: Optional["EventBus"] = None
    _initialized: bool = False

    def __new__(cls) -> "EventBus":
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the event bus."""
        if EventBus._initialized:
            return

        self.redis_client = RedisClient()
        self.pubsub = PubSubService()
        self.handlers: Dict[EventType, List[Callable]] = {}
        self.subscribed_channels: Set[str] = set()
        self.running = False
        self._subscriber_task: Optional[asyncio.Task] = None

        EventBus._initialized = True

    async def start(self) -> None:
        """Start the event bus subscriber."""
        if self.running:
            return

        self.running = True
        self._subscriber_task = asyncio.create_task(self._subscriber_loop())
        logger.info("Event bus started")

    async def stop(self) -> None:
        """Stop the event bus subscriber."""
        if not self.running:
            return

        self.running = False

        if self._subscriber_task:
            self._subscriber_task.cancel()
            try:
                await self._subscriber_task
            except asyncio.CancelledError:
                pass

        # Unsubscribe from all channels
        for channel in self.subscribed_channels:
            await self.pubsub.unsubscribe(channel)

        self.subscribed_channels.clear()
        logger.info("Event bus stopped")

    async def emit(self, event: Event) -> None:
        """Emit an event to the bus."""
        try:
            # Publish to Redis pub/sub
            channel = f"events:{event.event_type.value}"
            message = event.to_dict()

            await self.pubsub.publish(channel, json.dumps(message))

            # Also call local handlers synchronously for immediate processing
            if event.event_type in self.handlers:
                for handler in self.handlers[event.event_type]:
                    try:
                        if asyncio.iscoroutinefunction(handler):
                            await handler(event)
                        else:
                            handler(event)
                    except Exception as e:
                        logger.error(f"Error in event handler: {e}")

            logger.debug(f"Emitted event: {event.event_type.value} ({event.event_id})")

        except Exception as e:
            logger.error(f"Failed to emit event {event.event_type.value}: {e}")
            raise

    def subscribe(self, event_type: EventType, handler: Callable) -> None:
        """Subscribe a handler to an event type."""
        if event_type not in self.handlers:
            self.handlers[event_type] = []

        # Use weak reference to avoid memory leaks
        if asyncio.iscoroutinefunction(handler):
            self.handlers[event_type].append(handler)
        else:
            # For sync handlers, we need to be careful about references
            self.handlers[event_type].append(handler)

        # Subscribe to Redis channel if not already subscribed
        channel = f"events:{event_type.value}"
        if channel not in self.subscribed_channels:
            asyncio.create_task(self._subscribe_to_channel(channel))
            self.subscribed_channels.add(channel)

        logger.debug(f"Subscribed handler for {event_type.value}")

    def unsubscribe(self, event_type: EventType, handler: Callable) -> None:
        """Unsubscribe a handler from an event type."""
        if event_type in self.handlers:
            try:
                self.handlers[event_type].remove(handler)
                if not self.handlers[event_type]:
                    del self.handlers[event_type]

                    # Unsubscribe from Redis channel if no more handlers
                    channel = f"events:{event_type.value}"
                    if channel in self.subscribed_channels:
                        asyncio.create_task(self.pubsub.unsubscribe(channel))
                        self.subscribed_channels.remove(channel)

                logger.debug(f"Unsubscribed handler for {event_type.value}")
            except ValueError:
                pass  # Handler not found

    async def _subscribe_to_channel(self, channel: str) -> None:
        """Subscribe to a Redis channel."""
        try:
            await self.pubsub.subscribe(channel, self._handle_redis_message)
            logger.debug(f"Subscribed to Redis channel: {channel}")
        except Exception as e:
            logger.error(f"Failed to subscribe to Redis channel {channel}: {e}")

    async def _handle_redis_message(self, channel: str, message: str) -> None:
        """Handle incoming Redis message."""
        try:
            data = json.loads(message)
            event = Event.from_dict(data)

            # Call local handlers
            if event.event_type in self.handlers:
                for handler in self.handlers[event.event_type]:
                    try:
                        if asyncio.iscoroutinefunction(handler):
                            await handler(event)
                        else:
                            handler(event)
                    except Exception as e:
                        logger.error(
                            f"Error in event handler for {event.event_type.value}: {e}"
                        )

        except Exception as e:
            logger.error(f"Failed to handle Redis message from {channel}: {e}")

    async def _subscriber_loop(self) -> None:
        """Main subscriber loop (keeps the connection alive)."""
        while self.running:
            try:
                await asyncio.sleep(1)  # Keep alive
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in subscriber loop: {e}")
                await asyncio.sleep(5)  # Back off on error

    async def get_handler_count(self, event_type: EventType) -> int:
        """Get the number of handlers for an event type."""
        return len(self.handlers.get(event_type, []))

    async def get_all_handler_counts(self) -> Dict[EventType, int]:
        """Get handler counts for all event types."""
        return {
            event_type: len(handlers) for event_type, handlers in self.handlers.items()
        }


# Global event bus instance
_event_bus: Optional[EventBus] = None


def get_event_bus() -> EventBus:
    """Get the global event bus instance."""
    global _event_bus
    if _event_bus is None:
        _event_bus = EventBus()
    return _event_bus


async def emit_event(event: Event) -> None:
    """Convenience function to emit an event."""
    bus = get_event_bus()
    await bus.emit(event)


def subscribe_event(event_type: EventType, handler: Callable) -> None:
    """Convenience function to subscribe to an event type."""
    bus = get_event_bus()
    bus.subscribe(event_type, handler)


async def start_event_bus() -> None:
    """Start the global event bus."""
    bus = get_event_bus()
    await bus.start()


async def stop_event_bus() -> None:
    """Stop the global event bus."""
    bus = get_event_bus()
    await bus.stop()
