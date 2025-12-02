"""
Phase 2B - RaptorBus Event System
Redis-based Pub/Sub implementation for event broadcasting across 70+ agents
"""

import asyncio
import json
from typing import Dict, List, Callable, Optional, Set
from datetime import datetime, timedelta
import aioredis
from dataclasses import asdict

from phase2b_base_agent import (
    RaptorBusInterface,
    RaptorBusEvent,
    EventType,
    Channel
)


# ============================================================================
# REDIS RAPTOR BUS
# ============================================================================

class RedisRaptorBus(RaptorBusInterface):
    """
    Redis-based RaptorBus for event broadcasting
    Manages 9 channels with 21 event types
    Provides pub/sub, event history, and routing
    """

    def __init__(
        self,
        redis_url: str = "redis://localhost:6379",
        db: int = 0,
        event_retention_days: int = 7
    ):
        self.redis_url = redis_url
        self.db = db
        self.event_retention_days = event_retention_days

        # Connection pool
        self.redis = None
        self.pubsub_clients: Dict[Channel, aioredis.Redis] = {}

        # Local tracking
        self.subscribers: Dict[Channel, List[Callable]] = {
            ch: [] for ch in Channel
        }
        self.events_local: List[RaptorBusEvent] = []  # In-memory for testing
        self.max_local_events = 10000

    async def connect(self) -> None:
        """Connect to Redis"""
        try:
            self.redis = await aioredis.create_redis_pool(self.redis_url)
            await self._initialize_channels()
            print("[OK] RaptorBus connected to Redis")
        except Exception as e:
            print(f"[ERROR] RaptorBus Redis connection failed: {e}")
            print("[FALLBACK] Using in-memory event storage")
            self.redis = None

    async def disconnect(self) -> None:
        """Disconnect from Redis"""
        if self.redis:
            self.redis.close()
            await self.redis.wait_closed()

    async def _initialize_channels(self) -> None:
        """Initialize all 9 pub/sub channels"""
        if not self.redis:
            return

        for channel in Channel:
            try:
                # Subscribe to channel for monitoring
                pubsub = await self.redis.subscribe(channel.value)
                self.pubsub_clients[channel] = pubsub
            except Exception as e:
                print(f"[WARN] Failed to initialize channel {channel.value}: {e}")

    # ========================================================================
    # EVENT PUBLISHING
    # ========================================================================

    async def publish(self, channel: Channel, event: RaptorBusEvent) -> bool:
        """
        Publish event to Redis channel and store in history
        """
        event.timestamp = datetime.utcnow().isoformat()

        try:
            # Store locally
            self._store_event_locally(event)

            # Publish to Redis
            if self.redis:
                event_json = event.to_json()
                await self.redis.publish(channel.value, event_json)

            # Call local subscribers
            await self._notify_subscribers(channel, event)

            return True

        except Exception as e:
            print(f"[ERROR] Failed to publish event: {e}")
            return False

    async def _notify_subscribers(self, channel: Channel, event: RaptorBusEvent) -> None:
        """Notify local subscribers"""
        for callback in self.subscribers.get(channel, []):
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(event)
                else:
                    callback(event)
            except Exception as e:
                print(f"[ERROR] Subscriber notification failed: {e}")

    # ========================================================================
    # EVENT SUBSCRIPTION
    # ========================================================================

    async def subscribe(self, channel: Channel, callback: Callable) -> None:
        """
        Subscribe to channel events
        """
        if channel not in self.subscribers:
            self.subscribers[channel] = []
        self.subscribers[channel].append(callback)

    async def unsubscribe(self, channel: Channel, callback: Callable) -> None:
        """Unsubscribe from channel"""
        if channel in self.subscribers:
            if callback in self.subscribers[channel]:
                self.subscribers[channel].remove(callback)

    # ========================================================================
    # BROADCASTING
    # ========================================================================

    async def broadcast(
        self,
        event: RaptorBusEvent,
        lord: Optional[str] = None,
        agent: Optional[str] = None
    ) -> int:
        """
        Broadcast event to multiple channels
        Optionally filter by lord or agent
        """
        broadcast_channels = []

        # Determine which channels to broadcast to
        if lord and agent:
            # Specific agent on specific lord
            broadcast_channels = self._get_channels_for_agent(lord, agent)
        elif lord:
            # All agents on specific lord
            broadcast_channels = self._get_channels_for_lord(lord)
        else:
            # All channels
            broadcast_channels = list(Channel)

        # Publish to all target channels
        count = 0
        for channel in broadcast_channels:
            if await self.publish(channel, event):
                count += 1

        return count

    def _get_channels_for_lord(self, lord: str) -> List[Channel]:
        """Get channels relevant to a lord domain"""
        # Map lord domain to channels
        lord_channel_map = {
            "architect": [
                Channel.AGENT_EXECUTION,
                Channel.SYSTEM_EVENTS,
                Channel.METRICS,
                Channel.WORKFLOWS
            ],
            "cognition": [
                Channel.AGENT_EXECUTION,
                Channel.AGENT_COMMUNICATION,
                Channel.ANALYTICS,
                Channel.METRICS
            ],
            "strategos": [
                Channel.AGENT_EXECUTION,
                Channel.WORKFLOWS,
                Channel.METRICS,
                Channel.NOTIFICATIONS
            ],
            "aesthete": [
                Channel.AGENT_EXECUTION,
                Channel.DATA_OPERATIONS,
                Channel.NOTIFICATIONS,
                Channel.METRICS
            ],
            "seer": [
                Channel.AGENT_EXECUTION,
                Channel.ANALYTICS,
                Channel.METRICS,
                Channel.SYSTEM_EVENTS
            ],
            "arbiter": [
                Channel.AGENT_EXECUTION,
                Channel.SYSTEM_EVENTS,
                Channel.ERROR_HANDLING,
                Channel.METRICS
            ],
            "herald": [
                Channel.AGENT_EXECUTION,
                Channel.AGENT_COMMUNICATION,
                Channel.NOTIFICATIONS,
                Channel.METRICS
            ]
        }
        return lord_channel_map.get(lord, list(Channel))

    def _get_channels_for_agent(self, lord: str, agent: str) -> List[Channel]:
        """Get primary channel for an agent"""
        # All agents primarily use AGENT_EXECUTION
        channels = [Channel.AGENT_EXECUTION]

        # Add lord-specific channels
        channels.extend(self._get_channels_for_lord(lord))

        return list(set(channels))  # Remove duplicates

    # ========================================================================
    # EVENT HISTORY & RETRIEVAL
    # ========================================================================

    def _store_event_locally(self, event: RaptorBusEvent) -> None:
        """Store event in local list for retrieval"""
        self.events_local.append(event)

        # Trim to max size
        if len(self.events_local) > self.max_local_events:
            self.events_local = self.events_local[-self.max_local_events:]

    async def get_event_history(
        self,
        agent_id: str,
        limit: int = 100,
        event_type: Optional[EventType] = None,
        channel: Optional[Channel] = None
    ) -> List[RaptorBusEvent]:
        """
        Get event history for an agent
        """
        history = [
            e for e in self.events_local
            if e.agent == agent_id
        ]

        # Filter by event type
        if event_type:
            history = [e for e in history if e.event_type == event_type]

        # Filter by channel
        if channel:
            history = [e for e in history if e.channel == channel]

        # Return most recent, limited
        return history[-limit:]

    async def get_events_by_lord(
        self,
        lord: str,
        limit: int = 100,
        event_type: Optional[EventType] = None
    ) -> List[RaptorBusEvent]:
        """Get events for all agents in a lord domain"""
        history = [
            e for e in self.events_local
            if e.lord == lord
        ]

        if event_type:
            history = [e for e in history if e.event_type == event_type]

        return history[-limit:]

    async def get_events_by_type(
        self,
        event_type: EventType,
        limit: int = 100
    ) -> List[RaptorBusEvent]:
        """Get all events of a specific type"""
        history = [
            e for e in self.events_local
            if e.event_type == event_type
        ]
        return history[-limit:]

    async def get_channel_events(
        self,
        channel: Channel,
        limit: int = 100
    ) -> List[RaptorBusEvent]:
        """Get all events published to a channel"""
        history = [
            e for e in self.events_local
            if e.channel == channel
        ]
        return history[-limit:]

    # ========================================================================
    # EVENT ROUTING & FILTERING
    # ========================================================================

    async def get_workflow_events(
        self,
        workflow_id: str,
        limit: int = 100
    ) -> List[RaptorBusEvent]:
        """Get all events for a specific workflow"""
        history = [
            e for e in self.events_local
            if e.data.get("workflow_id") == workflow_id or
               e.metadata.get("workflow_id") == workflow_id
        ]
        return history[-limit:]

    async def get_errors(
        self,
        limit: int = 100,
        lord: Optional[str] = None
    ) -> List[RaptorBusEvent]:
        """Get all error events"""
        history = [
            e for e in self.events_local
            if e.status == "error" and
               (lord is None or e.lord == lord)
        ]
        return history[-limit:]

    async def get_warnings(
        self,
        limit: int = 100,
        lord: Optional[str] = None
    ) -> List[RaptorBusEvent]:
        """Get all warning events"""
        history = [
            e for e in self.events_local
            if e.status == "warning" and
               (lord is None or e.lord == lord)
        ]
        return history[-limit:]

    # ========================================================================
    # STATISTICS & ANALYTICS
    # ========================================================================

    async def get_event_stats(self) -> Dict[str, any]:
        """Get event statistics"""
        if not self.events_local:
            return {
                "total_events": 0,
                "by_channel": {},
                "by_event_type": {},
                "by_lord": {},
                "by_status": {}
            }

        stats = {
            "total_events": len(self.events_local),
            "by_channel": {},
            "by_event_type": {},
            "by_lord": {},
            "by_status": {},
            "oldest_event": self.events_local[0].timestamp if self.events_local else None,
            "newest_event": self.events_local[-1].timestamp if self.events_local else None
        }

        for event in self.events_local:
            # By channel
            ch = event.channel.value
            stats["by_channel"][ch] = stats["by_channel"].get(ch, 0) + 1

            # By event type
            et = event.event_type.value
            stats["by_event_type"][et] = stats["by_event_type"].get(et, 0) + 1

            # By lord
            stats["by_lord"][event.lord] = stats["by_lord"].get(event.lord, 0) + 1

            # By status
            stats["by_status"][event.status] = stats["by_status"].get(event.status, 0) + 1

        return stats

    async def get_agent_stats(self, agent_id: str) -> Dict[str, any]:
        """Get statistics for a specific agent"""
        agent_events = [e for e in self.events_local if e.agent == agent_id]

        if not agent_events:
            return {"total_events": 0, "agent_id": agent_id}

        execution_times = [
            e.execution_time_ms
            for e in agent_events
            if e.execution_time_ms > 0
        ]

        return {
            "agent_id": agent_id,
            "total_events": len(agent_events),
            "event_types": len(set(e.event_type for e in agent_events)),
            "success_count": len([e for e in agent_events if e.status == "success"]),
            "error_count": len([e for e in agent_events if e.status == "error"]),
            "warning_count": len([e for e in agent_events if e.status == "warning"]),
            "avg_execution_ms": sum(execution_times) / len(execution_times) if execution_times else 0,
            "min_execution_ms": min(execution_times) if execution_times else 0,
            "max_execution_ms": max(execution_times) if execution_times else 0
        }

    # ========================================================================
    # CLEANUP & MAINTENANCE
    # ========================================================================

    async def cleanup_old_events(self) -> int:
        """Remove events older than retention period"""
        cutoff_date = datetime.utcnow() - timedelta(days=self.event_retention_days)
        cutoff_iso = cutoff_date.isoformat()

        original_count = len(self.events_local)
        self.events_local = [
            e for e in self.events_local
            if e.timestamp > cutoff_iso
        ]

        return original_count - len(self.events_local)

    def clear_events(self) -> int:
        """Clear all local event history"""
        count = len(self.events_local)
        self.events_local = []
        return count


# ============================================================================
# RAPTOR BUS SINGLETON
# ============================================================================

_raptor_bus_instance: Optional[RedisRaptorBus] = None


def initialize_raptor_bus(
    redis_url: str = "redis://localhost:6379",
    db: int = 0
) -> RedisRaptorBus:
    """Initialize global RaptorBus instance"""
    global _raptor_bus_instance
    _raptor_bus_instance = RedisRaptorBus(redis_url=redis_url, db=db)
    return _raptor_bus_instance


def get_raptor_bus() -> RedisRaptorBus:
    """Get global RaptorBus instance"""
    global _raptor_bus_instance
    if _raptor_bus_instance is None:
        _raptor_bus_instance = RedisRaptorBus()
    return _raptor_bus_instance


if __name__ == "__main__":
    print("Phase 2B RaptorBus Event System")
    print("Redis-based event broadcasting for 70+ agents")
