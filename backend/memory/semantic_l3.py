import logging
from typing import Any, Dict, List, Optional

from backend.db import save_memory, vector_search
from backend.inference import InferenceProvider

logger = logging.getLogger("raptorflow.memory.semantic_l3")


class L3SemanticMemory:
    """
    SOTA L3 Semantic Memory (L3).
    Specialized for Brand Foundation lookup and long-term business logic.
    Targets pgvector storage with 'foundation' metadata scoping.
    """

    def __init__(self, table: str = "muse_assets"):
        self.table = table
        self.memory_type = "semantic"

    async def search_foundation(
        self, workspace_id: str, query: str, limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Searches for relevant brand foundation context."""
        try:
            embedder = InferenceProvider.get_embeddings()
            query_embedding = await embedder.aembed_query(query)

            raw_results = await vector_search(
                workspace_id=workspace_id,
                embedding=query_embedding,
                table=self.table,
                limit=limit,
                filters={"type": "foundation"},
            )

            formatted_results = [
                {"id": r[0], "content": r[1], "metadata": r[2], "similarity": r[3]}
                for r in raw_results
            ]

            logger.info(
                f"L3 Foundation Search: found {len(formatted_results)} results for {workspace_id}"
            )
            return formatted_results
        except Exception as e:
            logger.error(f"L3 Foundation Search failed: {e}")
            return []

    async def remember_foundation(
        self,
        workspace_id: str,
        content: str,
        embedding: List[float],
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Saves a new brand foundation fact."""
        if metadata is None:
            metadata = {}
        metadata["type"] = "foundation"

        try:
            fact_id = await save_memory(
                workspace_id=workspace_id,
                content=content,
                embedding=embedding,
                memory_type=self.memory_type,
                metadata=metadata,
            )
            logger.info(
                f"L3 Foundation Fact stored: {fact_id} for workspace {workspace_id}"
            )
            return fact_id
        except Exception as e:
            logger.error(f"L3 Foundation Fact store failed: {e}")
            raise
