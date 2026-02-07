"""
Distance Context Manager (DCM)
=============================

Refined context management for strategic moves.
Uses vector similarity sorting to find the most relevant business context
(Distance-based prioritization) and integrates with BCM snippets.
"""

import logging
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional

from memory.models import MemoryType
from memory.vector_store import VectorMemory

from .upstash_client import get_upstash_client

logger = logging.getLogger("raptorflow.services.dcm")


class DistanceContextManager:
    """
    DCM handles the semantic 'Distance' of business context.
    It filters and prioritizes context fragments based on their relevance to a specific goal.
    """

    def __init__(self, vector_memory: Optional[VectorMemory] = None):
        self.vector_memory = vector_memory or VectorMemory()
        self.upstash = get_upstash_client()
        self.similarity_threshold = 0.65  # Distance filter

    async def get_relevant_context(
        self,
        workspace_id: str,
        goal_prompt: str,
        limit: int = 5,
        context_types: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Retrieves semantically sorted context based on distance to the goal.
        """
        logger.info(
            f"DCM: Calculating context distance for goal: '{goal_prompt[:50]}...'"
        )

        # 1. Search Vector Memory for relevant fragments
        # Mapping string types to MemoryType enum
        search_types = []
        if context_types:
            for t in context_types:
                try:
                    search_types.append(MemoryType(t))
                except ValueError:
                    continue
        else:
            search_types = [MemoryType.BCM, MemoryType.MARKET_INTEL]

        memories = await self.vector_memory.search(
            workspace_id=workspace_id,
            query=goal_prompt,
            memory_types=search_types,
            limit=limit,
            similarity_threshold=self.similarity_threshold,
        )

        # 2. Sort and Filter by Distance (Similarity Score)
        # Note: VectorMemory.search already sorts by similarity

        high_signal_context = []
        for mem in memories:
            high_signal_context.append(
                {
                    "content": mem.content,
                    "distance_score": mem.score,
                    "type": mem.memory_type.value,
                    "metadata": mem.metadata,
                }
            )

        # 3. Snippet Bundle Check (Check Upstash for hot snippets)
        cache_key = f"dcm:hot_context:{workspace_id}"
        cached_snippets = await self.upstash.get(cache_key)

        return {
            "query": goal_prompt,
            "signal_count": len(high_signal_context),
            "fragments": high_signal_context,
            "cached_snippets": cached_snippets or {},
            "generated_at": datetime.now(UTC).isoformat(),
        }

    async def prioritize_and_prune(
        self, context_list: List[Dict[str, Any]], max_tokens: int = 2000
    ) -> List[Dict[str, Any]]:
        """
        Prunes context that is too 'Distant' or exceeds token budgets.
        """
        # Simple pruning by score and count for now
        sorted_context = sorted(
            context_list, key=lambda x: x.get("distance_score", 0), reverse=True
        )
        return sorted_context[:5]  # Return top 5 high-signal fragments


# Singleton pattern
_dcm_instance: Optional[DistanceContextManager] = None


def get_dcm() -> DistanceContextManager:
    global _dcm_instance
    if _dcm_instance is None:
        _dcm_instance = DistanceContextManager()
    return _dcm_instance
