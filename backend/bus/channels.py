"""
RaptorBus channel topology and constants.

Defines all channel names, message retention policies, and routing rules.
"""

from dataclasses import dataclass
from enum import Enum
from typing import List


class ChannelType(str, Enum):
    """Channel categories."""
    HEARTBEAT = "heartbeat"
    GUILD_BROADCAST = "guild_broadcast"
    ALERT = "alert"
    STATE_UPDATE = "state_update"
    DLQ = "dlq"


@dataclass
class Channel:
    """Channel configuration."""
    name: str
    type: ChannelType
    retention_seconds: int  # TTL for messages
    is_pattern: bool = False  # True if name uses * pattern


# ============================================================================
# HEARTBEAT CHANNEL
# ============================================================================
# Health monitoring - all agents publish heartbeat every 30s
# Subscribed by: LORD-001 (Architect), monitoring dashboard

HEARTBEAT_CHANNEL = Channel(
    name="sys.global.heartbeat",
    type=ChannelType.HEARTBEAT,
    retention_seconds=60,  # Keep for 1 minute (covers 3 missed beats)
)


# ============================================================================
# GUILD BROADCAST CHANNELS
# ============================================================================
# Intra-guild coordination and Lord → Guild commands
# Each guild has its own broadcast channel for isolation

GUILD_CHANNELS = {
    "research": Channel(
        name="sys.guild.research.broadcast",
        type=ChannelType.GUILD_BROADCAST,
        retention_seconds=3600,  # 1 hour
    ),
    "muse": Channel(
        name="sys.guild.muse.broadcast",
        type=ChannelType.GUILD_BROADCAST,
        retention_seconds=86400,  # 24 hours (creative assets often referenced later)
    ),
    "matrix": Channel(
        name="sys.guild.matrix.broadcast",
        type=ChannelType.GUILD_BROADCAST,
        retention_seconds=604800,  # 7 days (intelligence has long value)
    ),
    "guardians": Channel(
        name="sys.guild.guardians.broadcast",
        type=ChannelType.GUILD_BROADCAST,
        retention_seconds=604800,  # 7 days (approval records important for audit)
    ),
}


# ============================================================================
# ALERT CHANNELS
# ============================================================================
# Critical and warning alerts - high priority routing
# Route-based on severity and alert type

ALERT_CHANNELS = {
    "critical": Channel(
        name="sys.alert.critical",
        type=ChannelType.ALERT,
        retention_seconds=86400,  # 24 hours (crisis management needs history)
    ),
    "warning": Channel(
        name="sys.alert.warning",
        type=ChannelType.ALERT,
        retention_seconds=86400,  # 24 hours
    ),
}

# Alert pattern channel for subscribing to all alerts
ALERT_PATTERN = Channel(
    name="sys.alert.*",
    type=ChannelType.ALERT,
    retention_seconds=86400,
    is_pattern=True,
)


# ============================================================================
# STATE UPDATE CHANNEL
# ============================================================================
# Real-time updates for frontend via WebSocket
# Includes: Campaign creation, move completion, achievement unlocks, agent status

STATE_UPDATE_CHANNEL = Channel(
    name="sys.state.update",
    type=ChannelType.STATE_UPDATE,
    retention_seconds=3600,  # 1 hour
)


# ============================================================================
# DEAD LETTER QUEUE CHANNELS
# ============================================================================
# Messages that failed delivery after max_retries attempts
# Format: sys.dlq.{original_channel}.{failure_reason}

DLQ_PREFIX = "sys.dlq"

DLQ_CHANNELS = {
    "max_retries": Channel(
        name="sys.dlq.max_retries_exceeded",
        type=ChannelType.DLQ,
        retention_seconds=2592000,  # 30 days (for post-mortem analysis)
    ),
    "schema_violation": Channel(
        name="sys.dlq.schema_violation",
        type=ChannelType.DLQ,
        retention_seconds=2592000,
    ),
    "routing_error": Channel(
        name="sys.dlq.routing_error",
        type=ChannelType.DLQ,
        retention_seconds=2592000,
    ),
    "processing_timeout": Channel(
        name="sys.dlq.processing_timeout",
        type=ChannelType.DLQ,
        retention_seconds=2592000,
    ),
}


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_guild_channel(guild_name: str) -> Channel:
    """Get channel for specific guild."""
    guild_lower = guild_name.lower()
    if guild_lower not in GUILD_CHANNELS:
        raise ValueError(
            f"Unknown guild: {guild_name}. "
            f"Valid guilds: {list(GUILD_CHANNELS.keys())}"
        )
    return GUILD_CHANNELS[guild_lower]


def get_all_channels() -> List[Channel]:
    """Get all defined channels."""
    channels = [HEARTBEAT_CHANNEL, STATE_UPDATE_CHANNEL, ALERT_PATTERN]
    channels.extend(GUILD_CHANNELS.values())
    channels.extend(ALERT_CHANNELS.values())
    channels.extend(DLQ_CHANNELS.values())
    return channels


def is_alert_channel(channel_name: str) -> bool:
    """Check if channel is an alert channel."""
    return channel_name.startswith("sys.alert.")


def is_dlq_channel(channel_name: str) -> bool:
    """Check if channel is a DLQ channel."""
    return channel_name.startswith(DLQ_PREFIX)


def is_guild_channel(channel_name: str) -> bool:
    """Check if channel is a guild broadcast channel."""
    return channel_name.startswith("sys.guild.") and ".broadcast" in channel_name


# ============================================================================
# CHANNEL ROUTING RULES
# ============================================================================

ROUTING_RULES = {
    # Event type -> target channel(s)
    "heartbeat": [HEARTBEAT_CHANNEL.name],
    "lord_command": lambda destination_guild: [get_guild_channel(destination_guild).name],
    "research_complete": [GUILD_CHANNELS["research"].name],
    "asset_generated": [GUILD_CHANNELS["muse"].name],
    "intelligence_update": [GUILD_CHANNELS["matrix"].name],
    "approval_required": [GUILD_CHANNELS["guardians"].name],
    "newsjack_opportunity": [ALERT_CHANNELS["critical"].name],
    "crisis": [ALERT_CHANNELS["critical"].name],
    "sentiment_shift": [ALERT_CHANNELS["warning"].name],
    "campaign_created": [STATE_UPDATE_CHANNEL.name],
    "achievement_unlocked": [STATE_UPDATE_CHANNEL.name],
    "agent_status_changed": [HEARTBEAT_CHANNEL.name],
}


# ============================================================================
# MESSAGE METADATA EXTRACTION
# ============================================================================

def extract_metadata_from_event_type(event_type: str) -> dict:
    """Extract routing hints from event type string."""
    # Example: event_type = "asset_generated:email_subject"
    # Returns: {"base_type": "asset_generated", "subtype": "email_subject"}

    parts = event_type.split(":")
    return {
        "base_type": parts[0],
        "subtype": parts[1] if len(parts) > 1 else None,
    }
