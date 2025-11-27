"""
RaptorBus - Redis-based Pub/Sub message backbone for RaptorFlow Codex.

Provides topic-based message routing for inter-agent communication across
Council of Lords, Research/Muse/Matrix/Guardian Guilds, and system alerts.
"""

from backend.bus.raptor_bus import RaptorBus
from backend.bus.events import BusEvent, EventPriority
from backend.bus.channels import (
    Channel,
    HEARTBEAT_CHANNEL,
    GUILD_CHANNELS,
    ALERT_CHANNELS,
    STATE_UPDATE_CHANNEL,
    DLQ_PREFIX,
)

__all__ = [
    "RaptorBus",
    "BusEvent",
    "EventPriority",
    "Channel",
    "HEARTBEAT_CHANNEL",
    "GUILD_CHANNELS",
    "ALERT_CHANNELS",
    "STATE_UPDATE_CHANNEL",
    "DLQ_PREFIX",
]
