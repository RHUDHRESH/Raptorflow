import logging
from typing import Any, Dict, List, Optional

from db import save_memory, vector_search
from memory.policy import DEFAULT_IMPORTANCE, get_memory_policy

logger = logging.getLogger("raptorflow.memory.episodic_l2")


class L2EpisodicMemory:
    """
    SOTA L2 Episodic Memory (L2).
    Uses Supabase pgvector for long-term historical recall of agent actions and outcomes.
    Ideal for retrieving similar past campaign results and learning from success/failure.
    """

    def __init__(self, table: str = "muse_assets"):
        self.table = table
        self.memory_type = "episodic"

    async def store_episode(
        self,
        workspace_id: str,
        content: str,
        embedding: List[float],
        metadata: Optional[Dict[str, Any]] = None,
        workspace_importance: str = DEFAULT_IMPORTANCE,
        agent_importance: str = DEFAULT_IMPORTANCE,
    ) -> str:
        """Saves a historical episode to pgvector."""
        if metadata is None:
            metadata = {}
        metadata["type"] = self.memory_type
        policy = get_memory_policy()
        metadata.update(
            policy.retention_metadata(workspace_importance, agent_importance)
        )

        try:
            episode_id = await save_memory(
                workspace_id=workspace_id,
                content=content,
                embedding=embedding,
                memory_type=self.memory_type,
                metadata=metadata,
            )
            logger.info(f"L2 Episode stored: {episode_id} for workspace {workspace_id}")
            return episode_id
        except Exception as e:
            logger.error(f"L2 Episode store failed: {e}")
            raise

    async def recall_similar(
        self,
        workspace_id: str,
        query_embedding: List[float],
        limit: Optional[int] = None,
        filters: Optional[Dict[str, Any]] = None,
        workspace_importance: str = DEFAULT_IMPORTANCE,
        agent_importance: str = DEFAULT_IMPORTANCE,
    ) -> List[Dict[str, Any]]:
        """Recalls similar past episodes using vector similarity search."""
        if filters is None:
            filters = {}
        filters["type"] = self.memory_type
        if limit is None:
            policy = get_memory_policy()
            limit = policy.resolve(workspace_importance, agent_importance).recall_limit

        try:
            raw_results = await vector_search(
                workspace_id=workspace_id,
                embedding=query_embedding,
                table=self.table,
                limit=limit,
                filters=filters,
            )

            formatted_results = [
                {"id": r[0], "content": r[1], "metadata": r[2], "similarity": r[3]}
                for r in raw_results
            ]

            logger.info(f"L2 Recall: found {len(formatted_results)} similar episodes")
            return formatted_results
        except Exception as e:
            logger.error(f"L2 Recall failed: {e}")
            return []

    async def recall_campaign_outcomes(
        self, workspace_id: str, query_embedding: List[float], limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Specialized recall for historical campaign outcomes."""
        return await self.recall_similar(
            workspace_id=workspace_id,
            query_embedding=query_embedding,
            limit=limit,
            filters={"subtype": "campaign_outcome"},
        )
