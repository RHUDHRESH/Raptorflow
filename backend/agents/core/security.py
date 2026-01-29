"""
Security validation utilities for Raptorflow agents.
"""

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


def get_security_validator():
    """Get security validator instance."""
    return SecurityValidator()


class SecurityValidator:
    """Security validator for agent operations."""

    def __init__(self):
        self.trusted_agents = set()

    def validate_request(self, request: Dict[str, Any]) -> bool:
        """Validate a request for security."""
        # Simple implementation - can be extended
        return True

    def validate_agent(self, agent_id: str) -> bool:
        """Validate an agent for security."""
        return agent_id in self.trusted_agents

    def add_trusted_agent(self, agent_id: str):
        """Add a trusted agent."""
        self.trusted_agents.add(agent_id)
