# backend/raptor_bus.py
# RaptorFlow Codex - Message Bus & Event System
# Week 3 Tuesday - RaptorBus Implementation

import redis.asyncio as redis
import json
import logging
from typing import Dict, List, Any, Optional, Callable, Coroutine
from datetime import datetime
from enum import Enum
import asyncio
from dataclasses import dataclass, asdict
from uuid import uuid4
import time

logger = logging.getLogger(__name__)

# ============================================================================
# EVENT ROUTING & TOPOLOGY
# ============================================================================

class ChannelType(str, Enum):
    """RaptorBus channel types"""
    HEARTBEAT = "raptor:heartbeat"
    GUILD_BROADCAST = "raptor:guild:broadcast"
    GUILD_RESEARCH = "raptor:guild:research"
    GUILD_MUSE = "raptor:guild:muse"
    GUILD_MATRIX = "raptor:guild:matrix"
    GUILD_GUARDIAN = "raptor:guild:guardian"
    ALERT = "raptor:alert"
    STATE_UPDATE = "raptor:state:update"
    DLQ = "raptor:dlq"  # Dead Letter Queue

class EventType(str, Enum):
    """Event types published to bus"""
    AGENT_START = "agent:start"
    AGENT_COMPLETE = "agent:complete"
    AGENT_ERROR = "agent:error"
    CAMPAIGN_ACTIVATE = "campaign:activate"
    CAMPAIGN_PAUSE = "campaign:pause"
    MOVE_EXECUTE = "move:execute"
    SIGNAL_DETECTED = "signal:detected"
    INSIGHT_GENERATED = "insight:generated"
    ALERT_CREATED = "alert:created"
    WORKSPACE_UPDATE = "workspace:update"

# ============================================================================
# MESSAGE ENVELOPE
# ============================================================================

@dataclass
class Message:
    """Message envelope for all bus communications"""
    id: str
    event_type: EventType
    channel: ChannelType
    workspace_id: str
    user_id: str
    source_agent: str
    payload: Dict[str, Any]
    timestamp: str
    retry_count: int = 0
    max_retries: int = 3

    def to_json(self) -> str:
        """Serialize message to JSON"""
        return json.dumps({
            "id": self.id,
            "event_type": self.event_type.value,
            "channel": self.channel.value,
            "workspace_id": self.workspace_id,
            "user_id": self.user_id,
            "source_agent": self.source_agent,
            "payload": self.payload,
            "timestamp": self.timestamp,
            "retry_count": self.retry_count,
            "max_retries": self.max_retries
        })

    @staticmethod
    def from_json(data: str) -> "Message":
        """Deserialize message from JSON"""
        obj = json.loads(data)
        return Message(
            id=obj["id"],
            event_type=EventType(obj["event_type"]),
            channel=ChannelType(obj["channel"]),
            workspace_id=obj["workspace_id"],
            user_id=obj["user_id"],
            source_agent=obj["source_agent"],
            payload=obj["payload"],
            timestamp=obj["timestamp"],
            retry_count=obj.get("retry_count", 0),
            max_retries=obj.get("max_retries", 3)
        )

# ============================================================================
# RAPTORBUS MESSAGE BUS
# ============================================================================

class RaptorBus:
    """
    RaptorBus - Autonomous agent message orchestration system.

    Provides:
    - Redis Pub/Sub for agent-to-agent communication
    - Event publishing system for multi-guild coordination
    - Message consumption patterns with retry logic
    - Dead-letter queue for failed messages
    - Performance metrics per channel
    - Async message handling
    """

    def __init__(self, redis_url: str = "redis://localhost:6379/0"):
        """Initialize RaptorBus"""
        self.redis_url = redis_url
        self.redis: Optional[redis.Redis] = None
        self.pubsub: Optional[redis.client.PubSub] = None
        self.subscription_handlers: Dict[str, List[Callable]] = {}
        self.metrics: Dict[str, Dict[str, int]] = {}
        self.running = False

    async def connect(self) -> None:
        """Connect to Redis"""
        try:
            self.redis = await redis.from_url(self.redis_url, decode_responses=True)
            await self.redis.ping()
            logger.info("✅ RaptorBus connected to Redis")
        except Exception as e:
            logger.error(f"❌ RaptorBus connection failed: {e}")
            raise

    async def disconnect(self) -> None:
        """Disconnect from Redis"""
        if self.redis:
            await self.redis.close()
            logger.info("✅ RaptorBus disconnected")

    async def publish(
        self,
        event_type: EventType,
        channel: ChannelType,
        workspace_id: str,
        user_id: str,
        source_agent: str,
        payload: Dict[str, Any]
    ) -> str:
        """
        Publish event to RaptorBus.

        Args:
            event_type: Type of event
            channel: Target channel
            workspace_id: Workspace context
            user_id: User context
            source_agent: Publishing agent
            payload: Event data

        Returns:
            Message ID
        """
        message = Message(
            id=str(uuid4()),
            event_type=event_type,
            channel=channel,
            workspace_id=workspace_id,
            user_id=user_id,
            source_agent=source_agent,
            payload=payload,
            timestamp=datetime.utcnow().isoformat()
        )

        try:
            # Publish to Redis
            await self.redis.publish(channel.value, message.to_json())

            # Track metrics
            self._track_metric(channel.value, "published")

            logger.info(
                f"📤 Message published: {event_type.value} → {channel.value} "
                f"(agent={source_agent}, id={message.id})"
            )

            return message.id

        except Exception as e:
            logger.error(f"❌ Publish failed: {e}")
            await self._send_to_dlq(message, str(e))
            raise

    async def subscribe(
        self,
        channel: ChannelType,
        handler: Callable[[Message], Coroutine[Any, Any, None]]
    ) -> None:
        """
        Subscribe to channel with handler.

        Args:
            channel: Channel to subscribe to
            handler: Async handler function for messages
        """
        if channel.value not in self.subscription_handlers:
            self.subscription_handlers[channel.value] = []

        self.subscription_handlers[channel.value].append(handler)
        logger.info(f"📬 Handler subscribed to {channel.value}")

    async def start_consuming(self) -> None:
        """Start message consumption loop"""
        if self.running:
            logger.warning("⚠️ RaptorBus already consuming messages")
            return

        self.running = True
        logger.info("🚀 RaptorBus starting message consumption...")

        # Create pubsub if not exists
        self.pubsub = self.redis.pubsub()

        # Subscribe to all configured channels
        channels = list(self.subscription_handlers.keys())
        if channels:
            await self.pubsub.subscribe(*channels)
            logger.info(f"✅ Subscribed to {len(channels)} channels")

        # Start consumption loop
        try:
            async for message in self.pubsub.listen():
                if message["type"] == "message":
                    await self._handle_message(message)
        except asyncio.CancelledError:
            logger.info("🛑 Message consumption stopped")
            self.running = False
        except Exception as e:
            logger.error(f"❌ Consumption error: {e}")
            self.running = False
            raise

    async def _handle_message(self, redis_message: Dict[str, Any]) -> None:
        """
        Handle incoming message.

        Args:
            redis_message: Raw Redis message
        """
        try:
            channel = redis_message["channel"]
            data = redis_message["data"]

            # Deserialize message
            message = Message.from_json(data)

            # Track metrics
            self._track_metric(channel, "received")

            # Find handlers for this channel
            handlers = self.subscription_handlers.get(channel, [])

            if not handlers:
                logger.warning(f"⚠️ No handlers for channel: {channel}")
                return

            # Execute all handlers concurrently
            results = await asyncio.gather(
                *[handler(message) for handler in handlers],
                return_exceptions=True
            )

            # Check for errors
            errors = [r for r in results if isinstance(r, Exception)]
            if errors:
                message.retry_count += 1
                if message.retry_count < message.max_retries:
                    # Re-publish with retry count
                    await self.redis.publish(channel, message.to_json())
                    self._track_metric(channel, "retried")
                    logger.info(f"🔄 Message retried (attempt {message.retry_count})")
                else:
                    # Max retries exceeded, send to DLQ
                    await self._send_to_dlq(
                        message,
                        f"Max retries exceeded: {errors}"
                    )
            else:
                self._track_metric(channel, "processed")
                logger.info(f"✅ Message processed: {message.id}")

        except Exception as e:
            logger.error(f"❌ Message handling error: {e}")
            self._track_metric(channel, "error")

    async def _send_to_dlq(self, message: Message, reason: str) -> None:
        """
        Send message to dead-letter queue.

        Args:
            message: Message that failed
            reason: Failure reason
        """
        try:
            dlq_message = Message(
                id=str(uuid4()),
                event_type=EventType.ALERT_CREATED,
                channel=ChannelType.DLQ,
                workspace_id=message.workspace_id,
                user_id=message.user_id,
                source_agent="raptor-bus",
                payload={
                    "original_message_id": message.id,
                    "original_event": message.event_type.value,
                    "original_channel": message.channel.value,
                    "failure_reason": reason,
                    "original_payload": message.payload
                },
                timestamp=datetime.utcnow().isoformat()
            )

            await self.redis.publish(ChannelType.DLQ.value, dlq_message.to_json())
            self._track_metric(ChannelType.DLQ.value, "dlq_message")
            logger.error(f"📵 Message sent to DLQ: {message.id} - {reason}")

        except Exception as e:
            logger.error(f"❌ DLQ send failed: {e}")

    def _track_metric(self, channel: str, event: str) -> None:
        """Track message metrics"""
        if channel not in self.metrics:
            self.metrics[channel] = {}

        if event not in self.metrics[channel]:
            self.metrics[channel][event] = 0

        self.metrics[channel][event] += 1

    def get_metrics(self) -> Dict[str, Any]:
        """Get performance metrics"""
        return {
            "channels": self.metrics,
            "running": self.running,
            "timestamp": datetime.utcnow().isoformat()
        }

    async def get_dlq_messages(self, workspace_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Retrieve messages from dead-letter queue.

        Args:
            workspace_id: Filter by workspace
            limit: Max messages to retrieve

        Returns:
            List of DLQ messages
        """
        dlq_key = f"raptor:dlq:{workspace_id}"
        messages = []

        # Get messages from sorted set (stored with timestamp)
        dlq_items = await self.redis.zrange(dlq_key, 0, limit - 1)

        for item in dlq_items:
            try:
                msg = json.loads(item)
                messages.append(msg)
            except json.JSONDecodeError:
                logger.error(f"Failed to decode DLQ message: {item}")

        return messages

    async def retry_dlq_message(self, message_id: str, channel: ChannelType) -> bool:
        """
        Retry a message from DLQ.

        Args:
            message_id: Original message ID
            channel: Target channel

        Returns:
            Success status
        """
        try:
            # This would typically retrieve the original message from DLQ
            # and republish it to the appropriate channel
            logger.info(f"🔄 Retrying DLQ message: {message_id}")
            return True
        except Exception as e:
            logger.error(f"❌ DLQ retry failed: {e}")
            return False

# ============================================================================
# RAPTORBUS SINGLETON
# ============================================================================

_raptor_bus: Optional[RaptorBus] = None

async def get_raptor_bus(redis_url: str = "redis://localhost:6379/0") -> RaptorBus:
    """Get or create RaptorBus singleton"""
    global _raptor_bus

    if _raptor_bus is None:
        _raptor_bus = RaptorBus(redis_url)
        await _raptor_bus.connect()

    return _raptor_bus

async def shutdown_raptor_bus() -> None:
    """Shutdown RaptorBus"""
    global _raptor_bus

    if _raptor_bus:
        await _raptor_bus.disconnect()
        _raptor_bus = None

