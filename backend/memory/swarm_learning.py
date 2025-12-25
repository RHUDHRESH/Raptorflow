import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

from backend.db import save_memory, vector_search
from backend.inference import InferenceProvider
from backend.memory.episodic_l2 import L2EpisodicMemory
from backend.memory.short_term import L1ShortTermMemory

logger = logging.getLogger("raptorflow.memory.swarm_learning")


class SwarmLearningMemory:
    """
    Swarm Learning Memory layer.
    Sits above MemoryManager and standardizes how agents write/read shared learnings.
    Aggregates L1/L2/L3 tiers alongside a shared learning ledger.
    """

    L2_CONFIDENCE_THRESHOLD = 0.7
    L3_CONFIDENCE_THRESHOLD = 0.85

    L2_SOURCES = {"high_confidence_outcome", "user_feedback", "verified_research"}
    L3_SOURCES = {"verified_research"}

    def __init__(self, table: str = "muse_assets"):
        self.l1 = L1ShortTermMemory()
        self.l2 = L2EpisodicMemory(table=table)
        self.table = table
        self.ledger_ttl = 3600 * 24 * 7
        self.max_ledger_entries = 200

    def _normalize_scope(self, swarm_scope: Optional[str]) -> str:
        return swarm_scope or "workspace"

    def _ledger_key(self, workspace_id: str, swarm_scope: Optional[str]) -> str:
        scope = self._normalize_scope(swarm_scope)
        return f"swarm_learning:{scope}:{workspace_id}:ledger"

    def _promotion_policy(
        self, source: str, confidence: float, metadata: Dict[str, Any]
    ) -> Tuple[bool, bool]:
        """Determines whether a learning should be promoted to L2 or L3."""
        promote_l2 = (
            source in self.L2_SOURCES and confidence >= self.L2_CONFIDENCE_THRESHOLD
        ) or metadata.get("user_feedback", False)
        promote_l3 = (
            source in self.L3_SOURCES and confidence >= self.L3_CONFIDENCE_THRESHOLD
        ) or metadata.get("verified", False)
        return promote_l2, promote_l3

    async def record_learning(
        self,
        workspace_id: str,
        content: str,
        source: str,
        confidence: float,
        agent_id: Optional[str] = None,
        swarm_scope: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """Writes a learning artifact to the shared ledger and promotes it as needed."""
        if metadata is None:
            metadata = {}

        entry = {
            "id": str(uuid4()),
            "content": content,
            "source": source,
            "confidence": confidence,
            "agent_id": agent_id,
            "metadata": metadata,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "swarm_scope": self._normalize_scope(swarm_scope),
        }

        await self._append_ledger_entry(workspace_id, entry, swarm_scope)

        promote_l2, promote_l3 = self._promotion_policy(source, confidence, metadata)

        try:
            embedder = InferenceProvider.get_embeddings()
            if promote_l2:
                embedding = await embedder.aembed_query(content)
                await self.l2.store_episode(
                    workspace_id=workspace_id,
                    content=content,
                    embedding=embedding,
                    metadata={
                        "subtype": "learning",
                        "source": source,
                        "confidence": confidence,
                        "agent_id": agent_id,
                        "ledger_id": entry["id"],
                        "swarm_scope": entry["swarm_scope"],
                    },
                )

            if promote_l3:
                embedding = await embedder.aembed_query(content)
                await save_memory(
                    workspace_id=workspace_id,
                    content=content,
                    embedding=embedding,
                    memory_type="semantic",
                    metadata={
                        "type": "learning",
                        "source": source,
                        "confidence": confidence,
                        "agent_id": agent_id,
                        "ledger_id": entry["id"],
                        "swarm_scope": entry["swarm_scope"],
                    },
                )
        except Exception as exc:
            logger.error(f"Swarm learning promotion failed: {exc}")

        return entry

    async def _append_ledger_entry(
        self, workspace_id: str, entry: Dict[str, Any], swarm_scope: Optional[str]
    ) -> None:
        key = self._ledger_key(workspace_id, swarm_scope)
        ledger_entries = await self.l1.retrieve(key) or []
        ledger_entries.append(entry)
        ledger_entries = ledger_entries[-self.max_ledger_entries :]
        await self.l1.store(key, ledger_entries, ttl=self.ledger_ttl)

    async def retrieve_swarm_context(
        self,
        workspace_id: str,
        query: str,
        swarm_scope: Optional[str] = None,
        limit: int = 3,
    ) -> Dict[str, List[Dict[str, Any]]]:
        """Returns cross-agent learnings from ledger, L2, and L3."""
        scope = self._normalize_scope(swarm_scope)
        results = {"ledger": [], "episodic": [], "semantic": []}

        try:
            ledger_entries = await self.l1.retrieve(
                self._ledger_key(workspace_id, scope)
            )
            if ledger_entries:
                results["ledger"] = self._filter_ledger(ledger_entries, query, limit)

            embedder = InferenceProvider.get_embeddings()
            query_embedding = await embedder.aembed_query(query)

            results["episodic"] = await self.l2.recall_similar(
                workspace_id,
                query_embedding,
                limit=limit,
                filters={"subtype": "learning", "swarm_scope": scope},
            )

            raw_results = await vector_search(
                workspace_id=workspace_id,
                embedding=query_embedding,
                table=self.table,
                limit=limit,
                filters={"type": "learning", "swarm_scope": scope},
            )
            results["semantic"] = [
                {"id": r[0], "content": r[1], "metadata": r[2], "similarity": r[3]}
                for r in raw_results
            ]
        except Exception as exc:
            logger.error(f"Swarm learning retrieval failed: {exc}")

        return results

    def _filter_ledger(
        self, entries: List[Dict[str, Any]], query: str, limit: int
    ) -> List[Dict[str, Any]]:
        query_lower = query.lower()
        filtered = [
            entry
            for entry in entries
            if query_lower in str(entry.get("content", "")).lower()
        ]
        if not filtered:
            filtered = entries
        return filtered[-limit:]
