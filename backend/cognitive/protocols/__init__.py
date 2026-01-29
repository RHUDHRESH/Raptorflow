"""
Cognitive Protocols - Agent communication and coordination

Defines protocols for agent-to-agent communication, handoffs,
error handling, and standardized message formats.
"""

from discovery import AgentDescriptor, AgentDiscovery
from errors import ErrorCode, ErrorProtocol, ProtocolError
from handoff import HandoffProtocol
from messages import AgentMessage, MessageFormat, MessageType
from routing_rules import RoutingRule, RoutingRules
from schemas import ProtocolSchemas, validate_schema
from versioning import ProtocolVersion, negotiate_version

__all__ = [
    "AgentMessage",
    "MessageFormat",
    "MessageType",
    "HandoffProtocol",
    "ErrorProtocol",
    "ErrorCode",
    "ProtocolError",
    "ProtocolSchemas",
    "validate_schema",
    "ProtocolVersion",
    "negotiate_version",
    "AgentDiscovery",
    "AgentDescriptor",
    "RoutingRules",
    "RoutingRule",
]
