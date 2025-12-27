import hashlib
import json
import logging
from typing import Any, Dict, Optional

from memory.short_term import L1ShortTermMemory

logger = logging.getLogger("raptorflow.core.cache")


class ThoughtCache:
    """
    SOTA Response Caching for Agentic Thoughts.
    Reduces latency and cost for repeated strategic scenarios.
    """

    def __init__(self, memory: Optional[L1ShortTermMemory] = None):
        self.memory = memory or L1ShortTermMemory()

    def _generate_key(self, agent_role: str, messages: list) -> str:
        """Generates a unique deterministic key for a set of messages."""
        msg_str = json.dumps(
            [{"role": m["role"], "content": m["content"]} for m in messages],
            sort_keys=True,
        )
        h = hashlib.sha256(f"{agent_role}:{msg_str}".encode()).hexdigest()
        return f"thought_cache:{h}"

    async def get(self, agent_role: str, messages: list) -> Optional[Dict[str, Any]]:
        """Retrieves cached thought if available."""
        key = self._generate_key(agent_role, messages)
        cached = await self.memory.retrieve(key)
        if cached:
            logger.info(f"Cache HIT for {agent_role}")
            return json.loads(cached) if isinstance(cached, str) else cached
        return None

    async def set(
        self, agent_role: str, messages: list, response: Dict[str, Any], ttl: int = 3600
    ):
        """Caches a thought."""
        key = self._generate_key(agent_role, messages)
        await self.memory.store(key, response, ttl=ttl)
        logger.info(f"Cached thought for {agent_role}")


def get_thought_cache() -> ThoughtCache:
    return ThoughtCache()
