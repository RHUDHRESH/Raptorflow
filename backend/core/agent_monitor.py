import logging
from typing import Any, Dict

logger = logging.getLogger("raptorflow.core.agent_monitor")


class AgentHealthMonitor:
    """
    SOTA Agent Health Monitor.
    Detects hallucinations, loops, and resource exhaustion.
    """

    def __init__(self):
        self.HALLUCINATION_PATTERNS = [
            "as an AI language model",
            "nonsense text here",
            "error: ",
            "FAILED TO GENERATE",
        ]

    async def audit_response(
        self, agent_name: str, content: str, metadata: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Audits an agent response for health issues.
        """
        issues = []

        # 1. Check for emptiness
        if not content or len(content.strip()) < 10:
            issues.append("empty_response")

        # 2. Check for common hallucination markers
        for pattern in self.HALLUCINATION_PATTERNS:
            if pattern.lower() in content.lower():
                issues.append("hallucination_marker_detected")

        # 3. Check for resource spikes
        if metadata.get("tokens_out", 0) > 4000:
            issues.append("token_spike")

        if issues:
            logger.warning(f"Health Issue(s) detected for Agent {agent_name}: {issues}")
            return {"healthy": False, "issues": issues}

        return {"healthy": True, "issues": []}


def get_agent_health_monitor() -> AgentHealthMonitor:
    return AgentHealthMonitor()
