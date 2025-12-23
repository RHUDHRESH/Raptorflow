from typing import List, Dict, Optional, Any
from backend.db import vector_search, save_memory
from backend.inference import InferenceProvider

class SemanticMemory:
    """
    SOTA Semantic Memory Manager.
    Handles long-term business context and preference storage using pgvector.
    """
    
    def __init__(self):
        self.table = "muse_assets" # Default SOTA table for embeddings

    async def search(self, tenant_id: str, query: str, limit: int = 5) -> List[Dict]:
        """Performs a semantic search for relevant context."""
        embedder = InferenceProvider.get_embeddings()
        query_embedding = await embedder.aembed_query(query)
        
        raw_results = await vector_search(
            workspace_id=tenant_id,
            embedding=query_embedding,
            table=self.table,
            limit=limit
        )
        
        # Format results for SOTA consumption
        return [
            {
                "id": r[0],
                "content": r[1],
                "metadata": r[2],
                "similarity": r[3]
            } for r in raw_results
        ]

    async def remember(self, tenant_id: str, content: str, embedding: List[float], metadata: Optional[Dict] = None):
        """Persists a new piece of semantic memory."""
        return await save_memory(
            workspace_id=tenant_id,
            content=content,
            embedding=embedding,
            memory_type="semantic",
            metadata=metadata
        )
