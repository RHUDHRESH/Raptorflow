"""
RaptorBus: Redis-based Pub/Sub message bus for RaptorFlow Codex.

Provides:
- Topic-based publish/subscribe with schema validation
- Message routing based on event type and destination
- Automatic retry logic with exponential backoff
- Dead-letter queue (DLQ) for failed messages
- Message persistence and replay
- Metrics tracking (messages per channel, latency, failures)
"""

import json
import asyncio
import logging
from typing import Callable, Dict, List, Optional, Any, Union
from datetime import datetime, timedelta
from uuid import uuid4

import redis.asyncio as redis
from redis.asyncio.connection import ConnectionPool

from backend.bus.events import BusEvent, EventPriority
from backend.bus.channels import (
    Channel, ChannelType, GUILD_CHANNELS, ALERT_CHANNELS, DLQ_PREFIX,
    HEARTBEAT_CHANNEL, STATE_UPDATE_CHANNEL, is_alert_channel, is_dlq_channel
)
from backend.core.config import settings
from backend.utils.logging_config import get_logger, get_correlation_id, get_workspace_id

logger = get_logger("bus")


class RaptorBusException(Exception):
    """Base exception for RaptorBus errors."""
    pass


class SchemaValidationError(RaptorBusException):
    """Raised when event fails schema validation."""
    pass


class RoutingError(RaptorBusException):
    """Raised when event cannot be routed."""
    pass


class PublishError(RaptorBusException):
    """Raised when publish operation fails."""
    pass


class SubscriptionError(RaptorBusException):
    """Raised when subscription fails."""
    pass


class RaptorBus:
    """
    Redis-based Pub/Sub message bus for inter-agent communication.

    Features:
    - Schema-validated messages (Pydantic BusEvent)
    - Topic-based routing with pattern subscriptions
    - Automatic retry with exponential backoff
    - Dead-letter queues for failed messages
    - Message persistence for replay
    - Metrics collection

    Usage:
        bus = RaptorBus()
        await bus.connect()

        # Publish event
        event_id = await bus.publish_event(
            channel="sys.guild.research.broadcast",
            event_type="research_complete",
            payload={"results": {...}},
            priority="normal"
        )

        # Subscribe to guild broadcasts
        async def handler(event: BusEvent):
            print(f"Received: {event.type}")

        await bus.subscribe_to_guild("research", handler)
    """

    def __init__(self, redis_url: Optional[str] = None):
        """
        Initialize RaptorBus.

        Args:
            redis_url: Redis connection URL. Defaults to settings.REDIS_URL
        """
        self.redis_url = redis_url or settings.REDIS_URL
        self.connection_pool: Optional[ConnectionPool] = None
        self.redis_client: Optional[redis.Redis] = None
        self.is_connected = False

        # Subscription management
        self._subscriptions: Dict[str, asyncio.Task] = {}
        self._handlers: Dict[str, Callable] = {}

        # Metrics
        self._metrics = {
            "published": 0,
            "published_by_priority": {},
            "received": 0,
            "failed": 0,
            "retried": 0,
            "dlq_sent": 0,
        }

    async def connect(self):
        """Establish Redis connection."""
        try:
            # Parse SSL requirement from URL
            ssl_required = "rediss://" in self.redis_url
            ssl_cert_reqs = "required" if ssl_required else None

            self.connection_pool = ConnectionPool.from_url(
                self.redis_url,
                decode_responses=True,
                max_connections=50,
                socket_connect_timeout=5,
                socket_keepalive=True,
                socket_keepalive_options={
                    1: 1,  # TCP_KEEPIDLE
                    2: 1,  # TCP_KEEPINTVL
                    3: 3,  # TCP_KEEPCNT
                } if hasattr(redis, "socket") else None,
                ssl_cert_reqs=ssl_cert_reqs,
            )

            self.redis_client = redis.Redis(
                connection_pool=self.connection_pool,
                decode_responses=True
            )

            # Test connection
            await self.redis_client.ping()
            self.is_connected = True
            logger.info("RaptorBus connected to Redis")

        except Exception as e:
            logger.error(f"Failed to connect to Redis: {e}")
            raise RaptorBusException(f"Redis connection failed: {e}")

    async def disconnect(self):
        """Close Redis connection."""
        if self.redis_client:
            await self.redis_client.close()
            self.is_connected = False
            logger.info("RaptorBus disconnected")

    async def publish(self, event_type: str, payload: dict, *, workspace_id: Optional[str] = None, correlation_id: Optional[str] = None) -> None:
        """
        Simple publish method for agent communication according to master skeleton spec.

        Args:
            event_type: Type of event (e.g., "agent.task_started", "model_inference_complete")
            payload: Event-specific data
            workspace_id: Workspace context (uses context var if not provided)
            correlation_id: Correlation ID (uses context var if not provided)
        """
        import json
        from datetime import datetime

        resolved_correlation_id = correlation_id or get_correlation_id()
        resolved_workspace_id = workspace_id or get_workspace_id()

        # Build envelope as per master skeleton spec
        envelope = {
            "event_type": event_type,
            "workspace_id": resolved_workspace_id,
            "correlation_id": resolved_correlation_id,
            "payload": payload,
            "timestamp": datetime.utcnow().isoformat()
        }

        channel = f"raptorflow.events.{event_type}"

        try:
            await self.redis_client.publish(channel, json.dumps(envelope))
            logger.info(f"Published event {event_type} to {channel}",
                       workspace_id=resolved_workspace_id,
                       correlation_id=resolved_correlation_id)
        except Exception as e:
            logger.error(f"Failed to publish event {event_type}: {e}")
            raise

        # Also keep the existing complex publish method available

    def subscribe(self, event_type: str, handler: Callable[[dict], None]) -> None:
        """
        Register a handler for a specific event type.

        Args:
            event_type: Event type to subscribe to
            handler: Function that receives the event payload dict
        """
        # Create an async wrapper that extracts payload and calls the handler
        async def async_handler(event: BusEvent):
            handler(event.payload)

        channel = f"raptorflow.events.{event_type}"
        # Use the full subscription method but with a converted handler
        self._handlers[channel] = handler  # Store the original handler for simple dispatching

        # Register the async wrapper
        async def event_wrapper(event: BusEvent):
            handler(event.payload)

        self._registry_handlers[channel] = event_wrapper

        logger.info(f"Registered handler for {event_type} on {channel}")

    # ========================================================================
    # PUBLISH OPERATIONS
    # ========================================================================

    async def publish_event(
        self,
        channel: str,
        event_type: str,
        payload: Dict[str, Any],
        priority: Union[str, EventPriority] = EventPriority.NORMAL,
        source_agent_id: Optional[str] = None,
        destination_guild: Optional[str] = None,
        request_id: Optional[str] = None,
    ) -> str:
        """
        Publish a validated event to a channel.

        Args:
            channel: Target channel name
            event_type: Type of event
            payload: Event-specific data
            priority: Message priority (low, normal, high, critical)
            source_agent_id: ID of publishing agent (e.g., RES-001)
            destination_guild: Target guild (if applicable)
            request_id: Correlation ID for tracking

        Returns:
            Event ID for tracking

        Raises:
            SchemaValidationError: If event fails validation
            PublishError: If publish fails
        """

        if not self.is_connected:
            raise PublishError("RaptorBus not connected")

        try:
            # Create event object
            event = BusEvent(
                type=event_type,
                priority=priority if isinstance(priority, EventPriority) else EventPriority(priority),
                source_agent_id=source_agent_id,
                destination_guild=destination_guild,
                request_id=request_id or str(uuid4()),
                payload=payload,
            )

            # Validate schema
            event_json = event.to_json_str()

            # Publish to channel
            num_subscribers = await self.redis_client.publish(channel, event_json)

            # Persist for replay (configurable TTL)
            msg_ttl = self._get_message_ttl(channel)
            cache_key = f"msg:{channel}:{event.id}"
            await self.redis_client.setex(cache_key, msg_ttl, event_json)

            # Update metrics
            self._metrics["published"] += 1
            priority_str = event.priority.value
            self._metrics["published_by_priority"][priority_str] = \
                self._metrics["published_by_priority"].get(priority_str, 0) + 1

            # Track channel statistics
            await self._increment_channel_metric(channel, "published")

            logger.debug(
                f"Published event {event.id} to {channel} "
                f"({num_subscribers} subscribers)"
            )

            return event.id

        except Exception as e:
            logger.error(f"Publish failed: {e}")
            await self._send_to_dlq(
                channel=channel,
                event_json=event_json if "event_json" in locals() else None,
                reason="publish_error",
                error_details=str(e)
            )
            raise PublishError(f"Failed to publish event: {e}")

    # ========================================================================
    # SUBSCRIBE OPERATIONS
    # ========================================================================

    async def subscribe_to_channel(
        self,
        channel: str,
        handler: Callable[[BusEvent], Any],
        handler_name: Optional[str] = None,
    ):
        """
        Subscribe to a specific channel.

        Args:
            channel: Channel name to subscribe to
            handler: Async function to handle received events
            handler_name: Name for logging (defaults to function name)
        """

        if not self.is_connected:
            raise SubscriptionError("RaptorBus not connected")

        handler_name = handler_name or handler.__name__

        try:
            # Start subscription task
            task = asyncio.create_task(
                self._subscription_loop(channel, handler, handler_name)
            )

            self._subscriptions[f"{channel}:{handler_name}"] = task
            logger.info(f"Subscribed {handler_name} to {channel}")

        except Exception as e:
            logger.error(f"Subscription failed: {e}")
            raise SubscriptionError(f"Failed to subscribe: {e}")

    async def subscribe_to_guild(
        self,
        guild_name: str,
        handler: Callable[[BusEvent], Any],
        handler_name: Optional[str] = None,
    ):
        """
        Subscribe to a guild's broadcast channel.

        Args:
            guild_name: Guild name (research, muse, matrix, guardians)
            handler: Async function to handle events
            handler_name: Optional name for logging
        """

        if guild_name.lower() not in GUILD_CHANNELS:
            raise SubscriptionError(f"Unknown guild: {guild_name}")

        channel = GUILD_CHANNELS[guild_name.lower()].name
        await self.subscribe_to_channel(channel, handler, handler_name)

    async def subscribe_to_alerts(
        self,
        handler: Callable[[BusEvent, str], Any],
        handler_name: Optional[str] = None,
    ):
        """
        Subscribe to all alert channels (pattern subscription).

        Args:
            handler: Async function to handle alerts. Receives (event, channel)
            handler_name: Optional name for logging
        """

        if not self.is_connected:
            raise SubscriptionError("RaptorBus not connected")

        handler_name = handler_name or handler.__name__

        try:
            task = asyncio.create_task(
                self._pattern_subscription_loop("sys.alert.*", handler, handler_name)
            )

            self._subscriptions[f"sys.alert.*:{handler_name}"] = task
            logger.info(f"Subscribed {handler_name} to alert pattern")

        except Exception as e:
            logger.error(f"Alert subscription failed: {e}")
            raise SubscriptionError(f"Failed to subscribe to alerts: {e}")

    async def subscribe_to_state_updates(
        self,
        handler: Callable[[BusEvent], Any],
        handler_name: Optional[str] = None,
    ):
        """Subscribe to real-time state updates."""
        await self.subscribe_to_channel(
            STATE_UPDATE_CHANNEL.name,
            handler,
            handler_name
        )

    # ========================================================================
    # SUBSCRIPTION LOOPS (INTERNAL)
    # ========================================================================

    async def _subscription_loop(
        self,
        channel: str,
        handler: Callable,
        handler_name: str,
    ):
        """Main subscription loop for a channel."""

        pubsub = self.redis_client.pubsub()
        await pubsub.subscribe(channel)

        logger.info(f"Subscription loop started: {handler_name} on {channel}")

        try:
            async for message in pubsub.listen():
                if message["type"] == "message":
                    await self._handle_message(
                        message["data"],
                        handler,
                        handler_name,
                    )
        except asyncio.CancelledError:
            logger.info(f"Subscription loop cancelled: {handler_name}")
            await pubsub.unsubscribe(channel)
        except Exception as e:
            logger.error(f"Subscription loop error ({handler_name}): {e}")
            await pubsub.unsubscribe(channel)
        finally:
            await pubsub.close()

    async def _pattern_subscription_loop(
        self,
        pattern: str,
        handler: Callable,
        handler_name: str,
    ):
        """Subscription loop for pattern-based channels."""

        pubsub = self.redis_client.pubsub()
        await pubsub.psubscribe(pattern)

        logger.info(f"Pattern subscription loop started: {handler_name} on {pattern}")

        try:
            async for message in pubsub.listen():
                if message["type"] == "pmessage":
                    await self._handle_message(
                        message["data"],
                        handler,
                        handler_name,
                        channel=message["channel"],  # For pattern handlers
                    )
        except asyncio.CancelledError:
            logger.info(f"Pattern subscription loop cancelled: {handler_name}")
            await pubsub.punsubscribe(pattern)
        except Exception as e:
            logger.error(f"Pattern subscription loop error ({handler_name}): {e}")
            await pubsub.punsubscribe(pattern)
        finally:
            await pubsub.close()

    # ========================================================================
    # MESSAGE HANDLING
    # ========================================================================

    async def _handle_message(
        self,
        message_data: str,
        handler: Callable,
        handler_name: str,
        channel: Optional[str] = None,
    ):
        """Process a received message."""

        try:
            # Parse and validate
            event = BusEvent.model_validate_json(message_data)
            self._metrics["received"] += 1

            # Call handler
            if asyncio.iscoroutinefunction(handler):
                if channel:
                    # Pattern handler gets (event, channel)
                    await handler(event, channel)
                else:
                    # Regular handler gets (event)
                    await handler(event)
            else:
                if channel:
                    handler(event, channel)
                else:
                    handler(event)

            # Update metrics
            await self._increment_channel_metric(channel or "unknown", "received")

        except Exception as e:
            logger.error(f"Message handling error ({handler_name}): {e}")
            self._metrics["failed"] += 1

    # ========================================================================
    # MESSAGE PERSISTENCE & REPLAY
    # ========================================================================

    async def get_message(self, message_id: str) -> Optional[BusEvent]:
        """Retrieve a message by ID from cache."""
        try:
            # Search across all message caches
            pattern = f"msg:*:{message_id}"
            keys = await self.redis_client.keys(pattern)

            if keys:
                msg_json = await self.redis_client.get(keys[0])
                if msg_json:
                    return BusEvent.model_validate_json(msg_json)

            return None

        except Exception as e:
            logger.error(f"Failed to retrieve message {message_id}: {e}")
            return None

    async def replay_channel(
        self,
        channel: str,
        handler: Callable,
        max_age_seconds: Optional[int] = None,
    ) -> int:
        """
        Replay persisted messages from a channel.

        Args:
            channel: Channel to replay
            handler: Handler function
            max_age_seconds: Only replay messages newer than this

        Returns:
            Number of messages replayed
        """

        try:
            pattern = f"msg:{channel}:*"
            keys = await self.redis_client.keys(pattern)

            replayed = 0
            for key in keys:
                msg_json = await self.redis_client.get(key)
                if msg_json:
                    event = BusEvent.model_validate_json(msg_json)

                    if max_age_seconds:
                        msg_age = (
                            datetime.utcnow() - datetime.fromisoformat(event.timestamp)
                        ).total_seconds()
                        if msg_age > max_age_seconds:
                            continue

                    await self._handle_message(msg_json, handler, "replay")
                    replayed += 1

            logger.info(f"Replayed {replayed} messages from {channel}")
            return replayed

        except Exception as e:
            logger.error(f"Replay failed: {e}")
            return 0

    # ========================================================================
    # DEAD LETTER QUEUE
    # ========================================================================

    async def _send_to_dlq(
        self,
        channel: str,
        event_json: Optional[str],
        reason: str,
        error_details: str,
    ):
        """Send failed message to Dead Letter Queue."""

        try:
            dlq_channel = f"{DLQ_PREFIX}.{reason}"

            dlq_message = {
                "original_channel": channel,
                "reason": reason,
                "error_details": error_details,
                "timestamp": datetime.utcnow().isoformat(),
                "event": event_json,
            }

            await self.redis_client.publish(
                dlq_channel,
                json.dumps(dlq_message)
            )

            # Store in DLQ persistence
            dlq_key = f"dlq:{dlq_channel}:{uuid4()}"
            await self.redis_client.setex(
                dlq_key,
                30 * 24 * 3600,  # 30 days
                json.dumps(dlq_message)
            )

            self._metrics["dlq_sent"] += 1
            logger.warning(f"Sent message to DLQ: {reason}")

        except Exception as e:
            logger.error(f"Failed to send to DLQ: {e}")

    async def get_dlq_messages(
        self,
        reason: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict]:
        """Retrieve messages from Dead Letter Queue."""

        try:
            if reason:
                pattern = f"dlq:sys.dlq.{reason}:*"
            else:
                pattern = "dlq:*"

            keys = await self.redis_client.keys(pattern)
            messages = []

            for key in keys[:limit]:
                msg_json = await self.redis_client.get(key)
                if msg_json:
                    messages.append(json.loads(msg_json))

            return messages

        except Exception as e:
            logger.error(f"Failed to retrieve DLQ messages: {e}")
            return []

    # ========================================================================
    # METRICS & MONITORING
    # ========================================================================

    async def _increment_channel_metric(
        self,
        channel: str,
        metric_type: str,
    ):
        """Track metrics for a channel."""

        try:
            key = f"metrics:channel:{channel}:{metric_type}"
            await self.redis_client.incr(key)

        except Exception as e:
            logger.warning(f"Failed to update metrics: {e}")

    async def get_metrics(self) -> Dict[str, Any]:
        """Get RaptorBus metrics."""

        return {
            **self._metrics,
            "is_connected": self.is_connected,
            "active_subscriptions": len(self._subscriptions),
        }

    async def get_channel_metrics(self, channel: str) -> Dict[str, int]:
        """Get metrics for a specific channel."""

        try:
            published = await self.redis_client.get(
                f"metrics:channel:{channel}:published"
            ) or 0
            received = await self.redis_client.get(
                f"metrics:channel:{channel}:received"
            ) or 0

            return {
                "published": int(published),
                "received": int(received),
            }

        except Exception as e:
            logger.error(f"Failed to get channel metrics: {e}")
            return {}

    # ========================================================================
    # UTILITY METHODS
    # ========================================================================

    def _get_message_ttl(self, channel: str) -> int:
        """Determine TTL for message based on channel."""

        if channel == HEARTBEAT_CHANNEL.name:
            return 60
        elif "guild" in channel:
            if "muse" in channel:
                return 86400  # 24 hours
            elif "matrix" in channel:
                return 604800  # 7 days
            else:
                return 3600  # 1 hour
        elif "alert" in channel:
            return 86400  # 24 hours
        else:
            return 3600  # Default 1 hour

    async def health_check(self) -> Dict[str, Any]:
        """
        Perform health check of RaptorBus.

        Returns:
            Health status dict
        """

        try:
            if not self.is_connected:
                return {
                    "status": "disconnected",
                    "message": "RaptorBus not connected"
                }

            # Test ping
            ping_result = await self.redis_client.ping()

            # Get info
            info = await self.redis_client.info()

            return {
                "status": "healthy",
                "redis_ping": ping_result,
                "redis_version": info.get("redis_version"),
                "connected_clients": info.get("connected_clients"),
                "used_memory_mb": info.get("used_memory") / 1024 / 1024 if info.get("used_memory") else 0,
                "metrics": await self.get_metrics(),
            }

        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
            }

    async def unsubscribe_all(self):
        """Cancel all subscriptions."""

        for sub_key, task in self._subscriptions.items():
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass

        self._subscriptions.clear()
        logger.info("All subscriptions cancelled")


# ============================================================================
# SINGLETON INSTANCE
# ============================================================================

_bus_instance: Optional[RaptorBus] = None


async def get_bus() -> RaptorBus:
    """Get or create RaptorBus singleton instance."""

    global _bus_instance

    if _bus_instance is None:
        _bus_instance = RaptorBus()
        await _bus_instance.connect()

    return _bus_instance


async def shutdown_bus():
    """Shutdown RaptorBus gracefully."""

    global _bus_instance

    if _bus_instance:
        await _bus_instance.unsubscribe_all()
        await _bus_instance.disconnect()
        _bus_instance = None
