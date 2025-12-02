# backend/channels.py
# RaptorFlow Codex - Channel Topology & Routing
# Week 3 Tuesday - Message Channel Architecture

from typing import Dict, List, Set
from dataclasses import dataclass
from enum import Enum

# ============================================================================
# CHANNEL DEFINITIONS
# ============================================================================

@dataclass
class Channel:
    """Channel definition with metadata"""
    name: str
    redis_key: str
    description: str
    subscribers: List[str]
    message_types: List[str]
    retention_hours: int = 24
    max_queue_size: int = 10000

# ============================================================================
# CHANNEL TOPOLOGY
# ============================================================================

class ChannelTopology:
    """
    Defines the message routing topology for RaptorBus.

    Channels:
    1. Heartbeat - Agent health signals
    2. Guild Broadcast - Guild-wide announcements
    3. Guild-Specific - Intra-guild communication
    4. Alert - System alerts and notifications
    5. State Update - Workspace state propagation
    6. DLQ - Dead-letter queue for failures
    """

    # ========================================================================
    # CORE CHANNELS
    # ========================================================================

    HEARTBEAT = Channel(
        name="heartbeat",
        redis_key="raptor:heartbeat",
        description="Agent health and liveness signals",
        subscribers=[
            "health-monitor",
            "metrics-aggregator",
            "alert-service"
        ],
        message_types=[
            "agent:heartbeat",
            "service:ready",
            "service:degraded"
        ],
        retention_hours=1,
        max_queue_size=5000
    )

    GUILD_BROADCAST = Channel(
        name="guild_broadcast",
        redis_key="raptor:guild:broadcast",
        description="Multi-guild broadcast channel",
        subscribers=[
            "council-of-lords",
            "research-guild",
            "muse-guild",
            "matrix-guild",
            "guardian-guild"
        ],
        message_types=[
            "coordination:inter_guild",
            "coordination:council_directive",
            "metrics:performance",
            "resource:allocation"
        ],
        retention_hours=24,
        max_queue_size=10000
    )

    GUILD_RESEARCH = Channel(
        name="guild_research",
        redis_key="raptor:guild:research",
        description="Research Guild internal communication",
        subscribers=[
            "research-agents",
            "council-of-lords",
            "matrix-guild"
        ],
        message_types=[
            "agent:start",
            "agent:complete",
            "agent:error",
            "guild:research",
            "signal:detected"
        ],
        retention_hours=24,
        max_queue_size=8000
    )

    GUILD_MUSE = Channel(
        name="guild_muse",
        redis_key="raptor:guild:muse",
        description="Muse Guild creative output channel",
        subscribers=[
            "muse-agents",
            "council-of-lords",
            "guardian-guild"
        ],
        message_types=[
            "agent:start",
            "agent:complete",
            "agent:error",
            "guild:muse"
        ],
        retention_hours=48,
        max_queue_size=8000
    )

    GUILD_MATRIX = Channel(
        name="guild_matrix",
        redis_key="raptor:guild:matrix",
        description="Matrix Guild intelligence channel",
        subscribers=[
            "matrix-agents",
            "council-of-lords",
            "research-guild"
        ],
        message_types=[
            "agent:start",
            "agent:complete",
            "agent:error",
            "guild:matrix",
            "insight:generated"
        ],
        retention_hours=24,
        max_queue_size=8000
    )

    GUILD_GUARDIAN = Channel(
        name="guild_guardian",
        redis_key="raptor:guild:guardian",
        description="Guardian Guild compliance channel",
        subscribers=[
            "guardian-agents",
            "council-of-lords",
            "alert-service"
        ],
        message_types=[
            "agent:start",
            "agent:complete",
            "agent:error",
            "guild:guardian",
            "alert:created"
        ],
        retention_hours=72,
        max_queue_size=10000
    )

    # ========================================================================
    # SYSTEM CHANNELS
    # ========================================================================

    ALERT = Channel(
        name="alert",
        redis_key="raptor:alert",
        description="System alerts and critical notifications",
        subscribers=[
            "alert-service",
            "notification-service",
            "council-of-lords",
            "dashboard"
        ],
        message_types=[
            "alert:created",
            "alert:acknowledged",
            "alert:resolved"
        ],
        retention_hours=72,
        max_queue_size=5000
    )

    STATE_UPDATE = Channel(
        name="state_update",
        redis_key="raptor:state:update",
        description="Workspace state synchronization",
        subscribers=[
            "state-manager",
            "cache-invalidator",
            "audit-logger"
        ],
        message_types=[
            "workspace:update",
            "campaign:activate",
            "campaign:pause",
            "move:execute"
        ],
        retention_hours=24,
        max_queue_size=10000
    )

    DLQ = Channel(
        name="dlq",
        redis_key="raptor:dlq",
        description="Dead-letter queue for failed messages",
        subscribers=[
            "dlq-monitor",
            "alert-service",
            "error-logger"
        ],
        message_types=[
            "error:max_retries",
            "error:unroutable",
            "error:processing_failed"
        ],
        retention_hours=168,  # 7 days
        max_queue_size=50000
    )

    # ========================================================================
    # CHANNEL REGISTRY
    # ========================================================================

    ALL_CHANNELS = [
        HEARTBEAT,
        GUILD_BROADCAST,
        GUILD_RESEARCH,
        GUILD_MUSE,
        GUILD_MATRIX,
        GUILD_GUARDIAN,
        ALERT,
        STATE_UPDATE,
        DLQ
    ]

    CHANNEL_MAP = {
        channel.redis_key: channel
        for channel in ALL_CHANNELS
    }

# ============================================================================
# MESSAGE ROUTING
# ============================================================================

class MessageRouter:
    """Routes messages to appropriate channels"""

    # Route map: event_type -> channels
    ROUTING_TABLE: Dict[str, List[str]] = {
        # Agent events
        "agent:start": [
            ChannelTopology.GUILD_BROADCAST.redis_key,
            ChannelTopology.GUILD_RESEARCH.redis_key,
            ChannelTopology.GUILD_MUSE.redis_key,
            ChannelTopology.GUILD_MATRIX.redis_key,
            ChannelTopology.GUILD_GUARDIAN.redis_key
        ],
        "agent:complete": [
            ChannelTopology.GUILD_BROADCAST.redis_key,
            ChannelTopology.GUILD_RESEARCH.redis_key,
            ChannelTopology.GUILD_MUSE.redis_key,
            ChannelTopology.GUILD_MATRIX.redis_key,
            ChannelTopology.GUILD_GUARDIAN.redis_key
        ],
        "agent:error": [
            ChannelTopology.GUILD_BROADCAST.redis_key,
            ChannelTopology.ALERT.redis_key
        ],

        # Campaign events
        "campaign:activate": [
            ChannelTopology.GUILD_BROADCAST.redis_key,
            ChannelTopology.STATE_UPDATE.redis_key
        ],
        "campaign:pause": [
            ChannelTopology.GUILD_BROADCAST.redis_key,
            ChannelTopology.ALERT.redis_key
        ],

        # Move events
        "move:execute": [
            ChannelTopology.STATE_UPDATE.redis_key
        ],

        # Signal events
        "signal:detected": [
            ChannelTopology.GUILD_RESEARCH.redis_key,
            ChannelTopology.GUILD_BROADCAST.redis_key
        ],

        # Insight events
        "insight:generated": [
            ChannelTopology.GUILD_MATRIX.redis_key,
            ChannelTopology.GUILD_BROADCAST.redis_key
        ],

        # Alert events
        "alert:created": [
            ChannelTopology.ALERT.redis_key,
            ChannelTopology.GUILD_GUARDIAN.redis_key
        ],

        # Workspace events
        "workspace:update": [
            ChannelTopology.STATE_UPDATE.redis_key
        ],

        # Coordination events
        "coordination:inter_guild": [
            ChannelTopology.GUILD_BROADCAST.redis_key
        ],
        "coordination:council_directive": [
            ChannelTopology.GUILD_BROADCAST.redis_key
        ],

        # Metrics events
        "metrics:performance": [
            ChannelTopology.GUILD_BROADCAST.redis_key
        ],

        # Resource events
        "resource:allocation": [
            ChannelTopology.GUILD_BROADCAST.redis_key
        ]
    }

    @staticmethod
    def get_channels_for_event(event_type: str) -> List[str]:
        """Get channels for event type"""
        return MessageRouter.ROUTING_TABLE.get(event_type, [])

    @staticmethod
    def get_all_channels() -> List[str]:
        """Get all active channels"""
        return [channel.redis_key for channel in ChannelTopology.ALL_CHANNELS]

# ============================================================================
# CHANNEL SUBSCRIPTIONS (Who listens to what)
# ============================================================================

class ChannelSubscriptions:
    """Define which components subscribe to which channels"""

    SUBSCRIPTIONS: Dict[str, List[str]] = {
        # Council of Lords listens to everything
        "council_of_lords": [
            ChannelTopology.GUILD_BROADCAST.redis_key,
            ChannelTopology.GUILD_RESEARCH.redis_key,
            ChannelTopology.GUILD_MUSE.redis_key,
            ChannelTopology.GUILD_MATRIX.redis_key,
            ChannelTopology.GUILD_GUARDIAN.redis_key,
            ChannelTopology.ALERT.redis_key
        ],

        # Guild agents listen to their own channel + broadcast
        "research_guild": [
            ChannelTopology.GUILD_RESEARCH.redis_key,
            ChannelTopology.GUILD_BROADCAST.redis_key
        ],
        "muse_guild": [
            ChannelTopology.GUILD_MUSE.redis_key,
            ChannelTopology.GUILD_BROADCAST.redis_key
        ],
        "matrix_guild": [
            ChannelTopology.GUILD_MATRIX.redis_key,
            ChannelTopology.GUILD_BROADCAST.redis_key
        ],
        "guardian_guild": [
            ChannelTopology.GUILD_GUARDIAN.redis_key,
            ChannelTopology.GUILD_BROADCAST.redis_key
        ],

        # System services
        "alert_service": [
            ChannelTopology.ALERT.redis_key,
            ChannelTopology.GUILD_GUARDIAN.redis_key
        ],
        "metrics_aggregator": [
            ChannelTopology.HEARTBEAT.redis_key,
            ChannelTopology.GUILD_BROADCAST.redis_key
        ],
        "state_manager": [
            ChannelTopology.STATE_UPDATE.redis_key
        ],
        "dlq_monitor": [
            ChannelTopology.DLQ.redis_key
        ]
    }

    @staticmethod
    def get_subscriptions(component: str) -> List[str]:
        """Get channels subscribed by component"""
        return ChannelSubscriptions.SUBSCRIPTIONS.get(component, [])

    @staticmethod
    def get_subscribers_for_channel(channel: str) -> List[str]:
        """Get components subscribed to channel"""
        subscribers = []
        for component, channels in ChannelSubscriptions.SUBSCRIPTIONS.items():
            if channel in channels:
                subscribers.append(component)
        return subscribers

