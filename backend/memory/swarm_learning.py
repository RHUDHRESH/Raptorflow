<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
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


class SwarmLearningMemory:
    """
    Swarm memory manager for user feedback and swarm context recall.
    """

    def __init__(self, memory_manager: Optional[MemoryManager] = None):
        self.memory = memory_manager or MemoryManager()

    @staticmethod
    def _normalize_feedback_metadata(
        context: str, metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        normalized = dict(metadata or {})
        normalized.setdefault("context", context)
        normalized.setdefault("signal", normalized.get("signal") or "neutral")
        normalized.setdefault("tool_hint", normalized.get("tool_hint"))
        normalized.setdefault("agent_hint", normalized.get("agent_hint"))
        return normalized

    @staticmethod
    def _matches_scope(metadata: Dict[str, Any], swarm_scope: Optional[str]) -> bool:
        if not swarm_scope:
            return True
        return any(
            hint == swarm_scope
            for hint in (
                metadata.get("swarm_scope"),
                metadata.get("agent_hint"),
                metadata.get("tool_hint"),
            )
        )

    async def store_feedback(
        self,
        workspace_id: str,
        feedback: str,
        context: str,
        metadata: Optional[Dict[str, Any]] = None,
        ttl: int = 3600 * 24,
    ) -> str:
        """Stores user feedback in L1/L2 and promotes to L3 for swarm recall."""
        normalized_metadata = self._normalize_feedback_metadata(context, metadata)
        entry = {"content": feedback, "metadata": normalized_metadata}

        l1_key = f"swarm:feedback:{workspace_id}"
        existing = await self.memory.l1.retrieve(l1_key) or []
        if not isinstance(existing, list):
            existing = [existing]
        existing.append(entry)
        await self.memory.l1.store(l1_key, existing, ttl=ttl)

        embedder = InferenceProvider.get_embeddings()
        embedding_text = f"{feedback}\nContext: {context}"
        embedding = await embedder.aembed_query(embedding_text)
        feedback_id = await self.memory.l2.store_episode(
            workspace_id=workspace_id,
            content=feedback,
            embedding=embedding,
            metadata={**normalized_metadata, "subtype": "swarm_feedback"},
        )

        await self.memory.l3.remember_foundation(
            workspace_id=workspace_id,
            content=feedback,
            embedding=embedding,
            metadata={**normalized_metadata, "subtype": "swarm_feedback"},
        )

        return feedback_id

    async def recall_feedback(
        self,
        workspace_id: str,
        query: str,
        limit: int = 5,
        swarm_scope: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Recalls similar feedback from L2, optionally filtered by swarm scope."""
        embedder = InferenceProvider.get_embeddings()
        query_embedding = await embedder.aembed_query(query)

        results = await self.memory.l2.recall_similar(
            workspace_id,
            query_embedding,
            limit=limit,
            filters={"subtype": "swarm_feedback"},
        )

        return [
            entry
            for entry in results
            if self._matches_scope(entry.get("metadata", {}), swarm_scope)
        ]

    async def retrieve_swarm_context(
        self,
        workspace_id: str,
        query: str,
        swarm_scope: Optional[str] = None,
        limit: int = 5,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Aggregates L1/L2/L3 feedback for swarm-aware recall."""
        context: Dict[str, List[Dict[str, Any]]] = {
            "short_term": [],
            "episodic": [],
            "semantic": [],
        }

        l1_key = f"swarm:feedback:{workspace_id}"
        l1_data = await self.memory.l1.retrieve(l1_key) or []
        if not isinstance(l1_data, list):
            l1_data = [l1_data]
        scoped_l1 = [
            entry
            for entry in l1_data
            if self._matches_scope(entry.get("metadata", {}), swarm_scope)
        ]
        context["short_term"] = scoped_l1[-limit:]

        embedder = InferenceProvider.get_embeddings()
        query_embedding = await embedder.aembed_query(query)
        episodic_results = await self.memory.l2.recall_similar(
            workspace_id,
            query_embedding,
            limit=limit,
            filters={"subtype": "swarm_feedback"},
        )
        context["episodic"] = [
            entry
            for entry in episodic_results
            if self._matches_scope(entry.get("metadata", {}), swarm_scope)
        ]

        semantic_results = await self.memory.l3.search_foundation(
            workspace_id, query, limit=limit
        )
        context["semantic"] = [
            entry
            for entry in semantic_results
            if entry.get("metadata", {}).get("subtype") == "swarm_feedback"
            and self._matches_scope(entry.get("metadata", {}), swarm_scope)
        ]

        return context
=======
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
import json
import logging
from typing import TYPE_CHECKING, Any, Dict, List, Optional

from inference import InferenceProvider

if TYPE_CHECKING:
    from memory.manager import MemoryManager

logger = logging.getLogger("raptorflow.memory.swarm_learning")


class SwarmLearning:
    """
    SOTA Swarm Learning Manager.
    Aggregates shared knowledge across L1/L2/L3 memory tiers for swarm agents.
    """

    def __init__(self):
        from memory.manager import MemoryManager
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


class SwarmLearningMemory:
    """
    Swarm memory manager for user feedback and swarm context recall.
    """

    def __init__(self, memory_manager: Optional[MemoryManager] = None):
        self.memory = memory_manager or MemoryManager()

    @staticmethod
    def _normalize_feedback_metadata(
        context: str, metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        normalized = dict(metadata or {})
        normalized.setdefault("context", context)
        normalized.setdefault("signal", normalized.get("signal") or "neutral")
        normalized.setdefault("tool_hint", normalized.get("tool_hint"))
        normalized.setdefault("agent_hint", normalized.get("agent_hint"))
        return normalized

    @staticmethod
    def _matches_scope(metadata: Dict[str, Any], swarm_scope: Optional[str]) -> bool:
        if not swarm_scope:
            return True
        return any(
            hint == swarm_scope
            for hint in (
                metadata.get("swarm_scope"),
                metadata.get("agent_hint"),
                metadata.get("tool_hint"),
            )
        )

    async def store_feedback(
        self,
        workspace_id: str,
        feedback: str,
        context: str,
        metadata: Optional[Dict[str, Any]] = None,
        ttl: int = 3600 * 24,
    ) -> str:
        """Stores user feedback in L1/L2 and promotes to L3 for swarm recall."""
        normalized_metadata = self._normalize_feedback_metadata(context, metadata)
        entry = {"content": feedback, "metadata": normalized_metadata}

        l1_key = f"swarm:feedback:{workspace_id}"
        existing = await self.memory.l1.retrieve(l1_key) or []
        if not isinstance(existing, list):
            existing = [existing]
        existing.append(entry)
        await self.memory.l1.store(l1_key, existing, ttl=ttl)

        embedder = InferenceProvider.get_embeddings()
        embedding_text = f"{feedback}\nContext: {context}"
        embedding = await embedder.aembed_query(embedding_text)
        feedback_id = await self.memory.l2.store_episode(
            workspace_id=workspace_id,
            content=feedback,
            embedding=embedding,
            metadata={**normalized_metadata, "subtype": "swarm_feedback"},
        )

        await self.memory.l3.remember_foundation(
            workspace_id=workspace_id,
            content=feedback,
            embedding=embedding,
            metadata={**normalized_metadata, "subtype": "swarm_feedback"},
        )

        return feedback_id

    async def recall_feedback(
        self,
        workspace_id: str,
        query: str,
        limit: int = 5,
        swarm_scope: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Recalls similar feedback from L2, optionally filtered by swarm scope."""
        embedder = InferenceProvider.get_embeddings()
        query_embedding = await embedder.aembed_query(query)

        results = await self.memory.l2.recall_similar(
            workspace_id,
            query_embedding,
            limit=limit,
            filters={"subtype": "swarm_feedback"},
        )

        return [
            entry
            for entry in results
            if self._matches_scope(entry.get("metadata", {}), swarm_scope)
        ]

    async def retrieve_swarm_context(
        self,
        workspace_id: str,
        query: str,
        swarm_scope: Optional[str] = None,
        limit: int = 5,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Aggregates L1/L2/L3 feedback for swarm-aware recall."""
        context: Dict[str, List[Dict[str, Any]]] = {
            "short_term": [],
            "episodic": [],
            "semantic": [],
        }

        l1_key = f"swarm:feedback:{workspace_id}"
        l1_data = await self.memory.l1.retrieve(l1_key) or []
        if not isinstance(l1_data, list):
            l1_data = [l1_data]
        scoped_l1 = [
            entry
            for entry in l1_data
            if self._matches_scope(entry.get("metadata", {}), swarm_scope)
        ]
        context["short_term"] = scoped_l1[-limit:]

        embedder = InferenceProvider.get_embeddings()
        query_embedding = await embedder.aembed_query(query)
        episodic_results = await self.memory.l2.recall_similar(
            workspace_id,
            query_embedding,
            limit=limit,
            filters={"subtype": "swarm_feedback"},
        )
        context["episodic"] = [
            entry
            for entry in episodic_results
            if self._matches_scope(entry.get("metadata", {}), swarm_scope)
        ]

        semantic_results = await self.memory.l3.search_foundation(
            workspace_id, query, limit=limit
        )
        context["semantic"] = [
            entry
            for entry in semantic_results
            if entry.get("metadata", {}).get("subtype") == "swarm_feedback"
            and self._matches_scope(entry.get("metadata", {}), swarm_scope)
        ]

        return context
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
<<<<<<< Updated upstream
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
=======
>>>>>>> Stashed changes
