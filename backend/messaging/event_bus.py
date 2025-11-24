"""
Event Bus Layer for Agent Swarm Communication

This module implements Redis-based event bus for agent-to-agent communication.
Each agent can publish and subscribe to typed messages.
"""

import json
import uuid
from typing import Callable, List, Dict, Any, Literal, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel
import redis
import asyncio
from enum import Enum


class EventType(str, Enum):
    """All event types in the swarm"""

    # Goal & Strategy
    GOAL_REQUEST = "goal.request"
    MOVE_PLAN = "move.plan"
    MOVE_REVISED = "move.revised"

    # Content Creation
    CONTENT_BRIEF = "content.brief"
    SKELETON_DESIGN = "skeleton.design"
    DRAFT_ASSET = "content.draft"
    ASSET_VARIANT = "asset.variant"

    # Performance & Metrics
    PERFORMANCE_UPDATE = "metrics.update"
    ASSET_PERFORMANCE = "asset.performance"
    MOVE_METRICS = "move.metrics"

    # Intelligence
    TREND_ALERT = "trend.alert"
    COMPETITOR_INTEL = "competitor.intel"
    COHORT_DRIFT = "cohort.drift"
    PATTERN_IDENTIFIED = "pattern.identified"

    # Risk & Quality
    RISK_ALERT = "risk.alert"
    CONTENT_REVIEW = "content.review"
    REVIEW_COMPLETE = "review.complete"

    # Experiments
    EXPERIMENT_DESIGN = "experiment.design"
    EXPERIMENT_RESULT = "experiment.result"

    # Execution
    PUBLISH_REQUEST = "publish.request"
    PUBLISH_COMPLETE = "publish.complete"

    # Policy & Consensus
    CONFLICT_ALERT = "conflict.alert"
    POLICY_DECISION = "policy.decision"
    DEBATE_REQUEST = "debate.request"
    DEBATE_ROUND = "debate.round"
    DEBATE_RESULT = "debate.result"

    # System
    AGENT_HEARTBEAT = "agent.heartbeat"
    WORKFLOW_START = "workflow.start"
    WORKFLOW_COMPLETE = "workflow.complete"
    AGENT_ERROR = "agent.error"


class AgentMessage(BaseModel):
    """Typed message for agent communication"""

    id: str = None
    type: EventType
    origin: str  # agent_id
    targets: List[str] = []  # agent_ids to notify
    broadcast: bool = False  # If True, broadcast to all subscribers
    payload: Dict[str, Any]
    priority: Literal["CRITICAL", "HIGH", "MEDIUM", "LOW"] = "MEDIUM"
    correlation_id: str  # move_id, campaign_id, workflow_id, etc.
    timestamp: datetime = None
    ttl: int = 3600  # seconds

    def __init__(self, **data):
        super().__init__(**data)
        if not self.id:
            self.id = str(uuid.uuid4())
        if not self.timestamp:
            self.timestamp = datetime.utcnow()

    def to_json(self) -> str:
        return json.dumps(self.model_dump(mode='json', exclude_none=True))

    @classmethod
    def from_json(cls, data: str) -> 'AgentMessage':
        return cls(**json.loads(data))


class EventBus:
    """Redis-based event bus for agent communication"""

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.pubsub = None
        self.listening = False

    def publish(self, message: AgentMessage) -> bool:
        """
        Publish message to targets

        If broadcast=True, publishes to 'agent.*' (all agents)
        Otherwise, publishes to individual agent channels
        """

        message_json = message.to_json()

        if message.broadcast:
            # Broadcast to all agents
            channel = "agent.*"
            self.redis.publish(channel, message_json)
        else:
            # Send to specific agents
            for target in message.targets:
                channel = f"agent.{target}"
                self.redis.publish(channel, message_json)

        # Log message for audit trail
        self._log_message(message)

        return True

    def _log_message(self, message: AgentMessage):
        """Store message in audit log"""

        log_key = f"events:{message.correlation_id}"
        log_entry = {
            "id": message.id,
            "type": message.type.value,
            "origin": message.origin,
            "targets": message.targets,
            "timestamp": message.timestamp.isoformat(),
            "priority": message.priority
        }

        # Store in sorted set (score = timestamp)
        self.redis.zadd(
            log_key,
            {json.dumps(log_entry): message.timestamp.timestamp()}
        )

        # Set expiry
        self.redis.expire(log_key, message.ttl)

    async def subscribe(self, agent_id: str, callback: Callable):
        """
        Subscribe agent to messages

        Blocks and listens for messages. Run in background task.
        """

        pubsub = self.redis.pubsub()
        pubsub.subscribe(f"agent.{agent_id}")
        pubsub.subscribe("agent.*")  # Also listen to broadcasts

        print(f"[EventBus] {agent_id} listening...")

        try:
            for raw_message in pubsub.listen():
                if raw_message['type'] == 'message':
                    try:
                        data = raw_message['data']
                        if isinstance(data, bytes):
                            data = data.decode('utf-8')

                        message = AgentMessage.from_json(data)

                        # Call handler
                        if asyncio.iscoroutinefunction(callback):
                            await callback(message)
                        else:
                            callback(message)

                    except Exception as e:
                        print(f"[EventBus] Error processing message: {e}")

        finally:
            pubsub.unsubscribe()
            pubsub.close()

    def get_event_history(
        self,
        correlation_id: str,
        event_type: Optional[EventType] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Retrieve event history for a workflow"""

        log_key = f"events:{correlation_id}"

        # Get all events (sorted by timestamp)
        raw_events = self.redis.zrange(log_key, 0, -1)

        events = []
        for raw_event in raw_events[-limit:]:
            event = json.loads(raw_event)

            if event_type is None or event['type'] == event_type.value:
                events.append(event)

        return events

    def clear_history(self, correlation_id: str):
        """Clear event history for a workflow"""

        log_key = f"events:{correlation_id}"
        self.redis.delete(log_key)


class MessageRouter:
    """Route messages based on type and priority"""

    def __init__(self, event_bus: EventBus):
        self.event_bus = event_bus
        self.handlers: Dict[EventType, List[Callable]] = {}

    def register_handler(self, event_type: EventType, handler: Callable):
        """Register a handler for an event type"""

        if event_type not in self.handlers:
            self.handlers[event_type] = []

        self.handlers[event_type].append(handler)

    async def route(self, message: AgentMessage):
        """Route message to registered handlers"""

        handlers = self.handlers.get(message.type, [])

        for handler in handlers:
            try:
                if asyncio.iscoroutinefunction(handler):
                    await handler(message)
                else:
                    handler(message)
            except Exception as e:
                print(f"[MessageRouter] Error in handler: {e}")


# Example usage in agent:
"""
from backend.messaging.event_bus import EventBus, AgentMessage, EventType

event_bus = EventBus(redis_client)

# Publish
message = AgentMessage(
    type=EventType.MOVE_PLAN,
    origin="STRAT-01",
    targets=["COPY-01", "VIS-01"],
    payload={"move_id": "123", "channels": ["linkedin", "email"]},
    correlation_id="move-456"
)
event_bus.publish(message)

# Subscribe (run in background)
async def handle_message(msg: AgentMessage):
    if msg.type == EventType.CONTENT_BRIEF:
        # Generate content
        pass

asyncio.create_task(event_bus.subscribe("COPY-01", handle_message))
"""
