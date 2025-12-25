from datetime import datetime
from typing import Any, Dict


class HandoffProtocol:
    """
    Standardized protocol for agent-to-agent communication and context transfer.
    """

    @staticmethod
    def create_packet(
        source: str, target: str, context: Dict[str, Any], priority: str = "normal"
    ) -> Dict[str, Any]:
        """
        Creates a standardized handoff packet.
        """
        return {
            "source": source,
            "target": target,
            "context": context,
            "priority": priority,
            "timestamp": datetime.now().isoformat(),
        }

    @staticmethod
    def validate(packet: Dict[str, Any]) -> bool:
        """
        Validates the structure of a handoff packet.
        """
        required_keys = ["source", "target", "context", "priority"]
        return all(key in packet for key in required_keys)
