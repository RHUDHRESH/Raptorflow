import json
import logging
from typing import Any, Dict, List, Optional

from backend.inference import InferenceProvider
from backend.memory.manager import MemoryManager

logger = logging.getLogger("raptorflow.memory.swarm_learning")


class SwarmLearning:
    """
    SOTA Swarm Learning Manager.
    Aggregates shared knowledge across L1/L2/L3 memory tiers for swarm agents.
    """

    def __init__(self):
        self.memory = MemoryManager()

    def _serialize_learning(self, learning: Any) -> str:
        if isinstance(learning, str):
            return learning
        return json.dumps(learning)

    async def record_learning(
        self,
        workspace_id: str,
        thread_id: str,
        learning: Any,
        metadata: Optional[Dict[str, Any]] = None,
        ttl: int = 3600 * 24,
    ) -> bool:
        """Stores a swarm learning in L1 and L2 for fast recall and episodic trace."""
        if metadata is None:
            metadata = {}

        try:
            serialized = self._serialize_learning(learning)
            entry = {"content": serialized, "metadata": metadata}

            # L1 aggregation
            l1_key = f"swarm:learning:{thread_id}"
            existing = await self.memory.l1.retrieve(l1_key) or []
            if not isinstance(existing, list):
                existing = [existing]
            existing.append(entry)
            await self.memory.l1.store(l1_key, existing, ttl=ttl)

            # L2 episodic memory
            embedder = InferenceProvider.get_embeddings()
            embedding = await embedder.aembed_query(serialized)
            await self.memory.l2.store_episode(
                workspace_id=workspace_id,
                content=serialized,
                embedding=embedding,
                metadata={**metadata, "subtype": "swarm_learning"},
            )

            return True
        except Exception as e:
            logger.error(f"SwarmLearning record_learning failed: {e}")
            return False

    async def retrieve_swarm_knowledge(
        self,
        workspace_id: str,
        query: str,
        thread_id: Optional[str] = None,
        limit: int = 5,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Aggregates L1/L2/L3 knowledge for swarm-aware recall."""
        context = {"short_term": [], "episodic": [], "semantic": []}

        try:
            if thread_id:
                l1_key = f"swarm:learning:{thread_id}"
                l1_data = await self.memory.l1.retrieve(l1_key) or []
                if isinstance(l1_data, list):
                    context["short_term"] = l1_data[-limit:]
                else:
                    context["short_term"] = [l1_data]

            embedder = InferenceProvider.get_embeddings()
            query_embedding = await embedder.aembed_query(query)

            context["episodic"] = await self.memory.l2.recall_similar(
                workspace_id,
                query_embedding,
                limit=limit,
                filters={"subtype": "swarm_learning"},
            )

            semantic_results = await self.memory.l3.search_foundation(
                workspace_id, query, limit=limit
            )
            context["semantic"] = [
                item
                for item in semantic_results
                if item.get("metadata", {}).get("subtype") == "swarm_learning"
            ]

            return context
        except Exception as e:
            logger.error(f"SwarmLearning retrieve_swarm_knowledge failed: {e}")
            return context

    async def promote_learning(
        self,
        workspace_id: str,
        learning: Any,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """Promotes a learning to L3 semantic memory for long-term retention."""
        if metadata is None:
            metadata = {}

        try:
            serialized = self._serialize_learning(learning)
            embedder = InferenceProvider.get_embeddings()
            embedding = await embedder.aembed_query(serialized)

            await self.memory.l3.remember_foundation(
                workspace_id=workspace_id,
                content=serialized,
                embedding=embedding,
                metadata={**metadata, "subtype": "swarm_learning"},
            )
            return True
        except Exception as e:
            logger.error(f"SwarmLearning promote_learning failed: {e}")
            return False


async def record_learning(
    *,
    workspace_id: Optional[str],
    content: Any,
    evaluation: Optional[Dict[str, Any]] = None,
    metadata: Optional[Dict[str, Any]] = None,
    ttl: int = 3600 * 24,
) -> bool:
    """Convenience helper for recording blackbox learnings via SwarmLearning."""
    if not workspace_id:
        logger.warning("SwarmLearning record_learning skipped: missing workspace_id")
        return False

    metadata = metadata or {}
    thread_id = metadata.get("move_id") or "blackbox_learning"
    learning_payload = {"content": content, "evaluation": evaluation}
    return await SwarmLearning().record_learning(
        workspace_id=workspace_id,
        thread_id=str(thread_id),
        learning=learning_payload,
        metadata=metadata,
        ttl=ttl,
    )
