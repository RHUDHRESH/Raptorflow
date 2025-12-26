import logging
from typing import Any, Dict, List, Optional

from db import save_memory, vector_search
from inference import InferenceProvider

logger = logging.getLogger("raptorflow.memory.procedural")


class ProceduralMemory:
    """
    SOTA Procedural Memory.
    Stores and retrieves 'how-to' patterns for agent tool usage.
    Learns successful execution sequences (Task -> Tools -> Outcome).
    """

    def __init__(self, table: str = "agent_memory_procedural"):
        self.table = table

    async def store_procedure(
        self,
        tenant_id: str,
        intent: str,
        procedure: str,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        """Persists a successful tool-use pattern."""
        embedder = InferenceProvider.get_embeddings()
        embedding = await embedder.aembed_query(intent)

        if metadata is None:
            metadata = {}
        metadata["intent"] = intent

        return await save_memory(
            workspace_id=tenant_id,
            content=procedure,
            embedding=embedding,
            memory_type="procedural",
            metadata=metadata,
        )

    async def get_procedure(
        self, tenant_id: str, intent: str, limit: int = 1
    ) -> List[Dict[str, Any]]:
        """Retrieves the most relevant procedure for a given intent."""
        embedder = InferenceProvider.get_embeddings()
        query_embedding = await embedder.aembed_query(intent)

        raw_results = await vector_search(
            workspace_id=tenant_id,
            embedding=query_embedding,
            table=self.table,
            limit=limit,
        )

        return [
            {"id": r[0], "content": r[1], "metadata": r[2], "similarity": r[3]}
            for r in raw_results
        ]
