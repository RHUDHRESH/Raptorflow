import logging
from typing import List, Dict, Any, Optional
from backend.db import save_memory, get_memory

logger = logging.getLogger("raptorflow.memory.episodic_l2")

class L2EpisodicMemory:
    """
    SOTA L2 Episodic Memory (L2).
    Uses Supabase pgvector for long-term historical recall of agent actions and outcomes.
    Ideal for retrieving similar past campaign results and learning from success/failure.
    """

    def __init__(self):
        self.memory_type = "episodic"

    async def store_episode(
        self, 
        workspace_id: str, 
        content: str, 
        embedding: List[float], 
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Saves a historical episode to pgvector."""
        try:
            episode_id = await save_memory(
                workspace_id=workspace_id,
                content=content,
                embedding=embedding,
                memory_type=self.memory_type,
                metadata=metadata
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
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """Recalls similar past episodes using vector similarity search."""
        try:
            raw_results = await get_memory(
                workspace_id=workspace_id,
                query_embedding=query_embedding,
                memory_type=self.memory_type,
                limit=limit
            )
            
            formatted_results = []
            for row in raw_results:
                # row: (id, content, metadata, similarity)
                formatted_results.append({
                    "id": row[0],
                    "content": row[1],
                    "metadata": row[2],
                    "similarity": row[3]
                })
            
            logger.info(f"L2 Recall: found {len(formatted_results)} similar episodes")
            return formatted_results
        except Exception as e:
            logger.error(f"L2 Recall failed: {e}")
            return []
