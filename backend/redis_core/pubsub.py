"""
PubSub Service - Redis Pub/Sub messaging

Provides publish/subscribe functionality for real-time messaging
and event distribution across the system.
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Any, Callable, Dict, List, Optional

from .client import RedisClient

logger = logging.getLogger(__name__)


class PubSubService:
    """Redis Pub/Sub service for real-time messaging."""

    def __init__(self, redis_client: Optional[RedisClient] = None):
        self.redis = redis_client or RedisClient()
        self.subscriptions: Dict[str, List[Callable]] = {}
        self.pubsub = None
        self._running = False

    async def publish(self, channel: str, message: Any) -> bool:
        """
        Publish message to channel.

        Args:
            channel: Channel name
            message: Message to publish (will be JSON serialized)

        Returns:
            Success status
        """
        try:
            # Serialize message
            if not isinstance(message, str):
                message = json.dumps(message, default=str)

            # Add timestamp
            message_data = {
                "message": message,
                "timestamp": datetime.now().isoformat(),
                "channel": channel,
            }

            # Publish to Redis
            result = await self.redis.publish(channel, json.dumps(message_data))

            logger.debug(
                f"Published message to channel {channel}, {result} subscribers"
            )
            return result > 0

        except Exception as e:
            logger.error(f"Failed to publish to channel {channel}: {e}")
            return False

    async def subscribe(self, channel: str, callback: Callable) -> bool:
        """
        Subscribe to channel with callback.

        Args:
            channel: Channel name
            callback: Callback function for messages

        Returns:
            Success status
        """
        try:
            if channel not in self.subscriptions:
                self.subscriptions[channel] = []

            self.subscriptions[channel].append(callback)

            # Start pubsub listener if not running
            if not self._running:
                await self._start_listener()

            logger.info(f"Subscribed to channel {channel}")
            return True

        except Exception as e:
            logger.error(f"Failed to subscribe to channel {channel}: {e}")
            return False

    async def unsubscribe(
        self, channel: str, callback: Optional[Callable] = None
    ) -> bool:
        """
        Unsubscribe from channel.

        Args:
            channel: Channel name
            callback: Specific callback to remove (None removes all)

        Returns:
            Success status
        """
        try:
            if channel not in self.subscriptions:
                return True

            if callback:
                # Remove specific callback
                if callback in self.subscriptions[channel]:
                    self.subscriptions[channel].remove(callback)
            else:
                # Remove all callbacks for channel
                self.subscriptions[channel] = []

            # Clean up empty channels
            if not self.subscriptions[channel]:
                del self.subscriptions[channel]

            logger.info(f"Unsubscribed from channel {channel}")
            return True

        except Exception as e:
            logger.error(f"Failed to unsubscribe from channel {channel}: {e}")
            return False

    async def _start_listener(self):
        """Start the pubsub listener."""
        try:
            if self._running:
                return

            self._running = True
            self.pubsub = self.redis.pubsub()

            # Subscribe to all channels
            if self.subscriptions:
                await self.pubsub.subscribe(*self.subscriptions.keys())

            # Start listening in background
            asyncio.create_task(self._listen_loop())

            logger.info("PubSub listener started")

        except Exception as e:
            logger.error(f"Failed to start pubsub listener: {e}")
            self._running = False

    async def _listen_loop(self):
        """Main pubsub listening loop."""
        try:
            while self._running:
                try:
                    message = await self.pubsub.get_message(timeout=1.0)

                    if message and message["type"] == "message":
                        await self._handle_message(message)

                except Exception as e:
                    logger.error(f"Error in pubsub message handling: {e}")
                    await asyncio.sleep(1)

        except Exception as e:
            logger.error(f"PubSub listener loop failed: {e}")
            self._running = False

    async def _handle_message(self, message):
        """Handle incoming pubsub message."""
        try:
            channel = message["channel"].decode("utf-8")
            data = message["data"].decode("utf-8")

            # Parse message
            try:
                message_data = json.loads(data)
                message_content = message_data.get("message", data)
            except json.JSONDecodeError:
                message_content = data

            # Call all callbacks for this channel
            if channel in self.subscriptions:
                for callback in self.subscriptions[channel]:
                    try:
                        if asyncio.iscoroutinefunction(callback):
                            await callback(channel, message_content)
                        else:
                            callback(channel, message_content)
                    except Exception as e:
                        logger.error(f"Callback error for channel {channel}: {e}")

        except Exception as e:
            logger.error(f"Failed to handle pubsub message: {e}")

    async def broadcast(self, channels: List[str], message: Any) -> int:
        """
        Broadcast message to multiple channels.

        Args:
            channels: List of channel names
            message: Message to broadcast

        Returns:
            Number of successful publishes
        """
        success_count = 0

        for channel in channels:
            if await self.publish(channel, message):
                success_count += 1

        return success_count

    async def get_channel_subscribers(self, channel: str) -> int:
        """
        Get number of subscribers for a channel.

        Args:
            channel: Channel name

        Returns:
            Number of subscribers
        """
        try:
            # This requires Redis PUBSUB command
            # Implementation depends on Redis client capabilities
            return 0  # Placeholder

        except Exception as e:
            logger.error(f"Failed to get subscriber count: {e}")
            return 0

    async def create_event_channel(self, event_type: str, workspace_id: str) -> str:
        """
        Create standardized event channel name.

        Args:
            event_type: Type of event
            workspace_id: Workspace identifier

        Returns:
            Channel name
        """
        return f"events:{workspace_id}:{event_type}"

    async def publish_event(
        self, event_type: str, workspace_id: str, event_data: Dict[str, Any]
    ) -> bool:
        """
        Publish workspace event.

        Args:
            event_type: Type of event
            workspace_id: Workspace identifier
            event_data: Event data

        Returns:
            Success status
        """
        channel = await self.create_event_channel(event_type, workspace_id)

        event = {
            "type": event_type,
            "workspace_id": workspace_id,
            "data": event_data,
            "timestamp": datetime.now().isoformat(),
        }

        return await self.publish(channel, event)

    async def stop(self):
        """Stop the pubsub service."""
        try:
            self._running = False

            if self.pubsub:
                await self.pubsub.unsubscribe()
                await self.pubsub.close()
                self.pubsub = None

            logger.info("PubSub service stopped")

        except Exception as e:
            logger.error(f"Failed to stop pubsub service: {e}")


# Standard channel names
class Channels:
    """Standard channel names for system events."""

    # Agent events
    AGENT_UPDATES = "agent_updates"
    AGENT_STATUS = "agent_status"

    # Approval events
    APPROVAL_REQUESTS = "approval_requests"
    APPROVAL_UPDATES = "approval_updates"

    # Session events
    SESSION_EVENTS = "session_events"
    SESSION_UPDATES = "session_updates"

    # System events
    SYSTEM_ALERTS = "system_alerts"
    SYSTEM_METRICS = "system_metrics"

    # Workspace events
    WORKSPACE_UPDATES = "workspace_updates"
    WORKSPACE_EVENTS = "workspace_events"
