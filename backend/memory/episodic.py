import json
from typing import Any, Dict, List, Optional

from core.cache import get_cache_manager
from db import get_memory, save_memory
from inference import InferenceProvider


class EpisodicMemory:
    """
    SOTA Episodic Memory Manager.
    Handles short-term session state (Redis) and long-term vector recall (pgvector).
    """

    def __init__(self, client: Any = None):
        manager = get_cache_manager()
        self.client = client or (manager.client if manager else None)
        self.prefix = "episodic:"

    def _get_key(self, session_id: str) -> str:
        return f"{self.prefix}{session_id}"

    async def add_message(
        self, session_id: str, message: str, tenant_id: Optional[str] = None
    ):
        """Adds a message to the session's episodic history and optionally persists it."""
        key = self._get_key(session_id)
        current_history_raw = await self.client.get(key)

        if current_history_raw:
            history = json.loads(current_history_raw)
        else:
            history = []

        history.append(message)
        # Limit history size to 20 messages for SOTA performance
        history = history[-20:]

        await self.client.set(key, json.dumps(history), ex=3600 * 24)  # 24h TTL

        # If tenant_id is provided, also persist to long-term memory
        if tenant_id:
            await self.persist_to_long_term(tenant_id, session_id, message)

    async def get_history(self, session_id: str) -> List[str]:
        """Retrieves the full episodic history for a session."""
        key = self._get_key(session_id)
        raw = await self.client.get(key)
        if raw:
            return json.loads(raw)
        return []

    async def clear(self, session_id: str):
        """Wipes episodic memory for a session."""
        key = self._get_key(session_id)
        await self.client.delete(key)

    async def persist_to_long_term(self, tenant_id: str, session_id: str, message: str):
        """Archives a message to permanent pgvector storage."""
        embedder = InferenceProvider.get_embeddings()
        embedding = await embedder.aembed_query(message)

        await save_memory(
            workspace_id=tenant_id,
            content=message,
            embedding=embedding,
            memory_type="episodic",
            metadata={"session_id": session_id, "archived_at": "now"},
        )

    async def search_long_term(
        self, tenant_id: str, query: str, limit: int = 5
    ) -> List[Dict]:
        """Retrieves similar past interactions from pgvector."""
        embedder = InferenceProvider.get_embeddings()
        query_embedding = await embedder.aembed_query(query)

        raw_results = await get_memory(
            workspace_id=tenant_id,
            query_embedding=query_embedding,
            memory_type="episodic",
            limit=limit,
        )

        return [
            {"id": r[0], "content": r[1], "metadata": r[2], "similarity": r[3]}
            for r in raw_results
        ]
