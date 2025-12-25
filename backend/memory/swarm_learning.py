import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from backend.db import save_memory, vector_search
from backend.inference import InferenceProvider

logger = logging.getLogger("raptorflow.memory.swarm_learning")


class SwarmLearningMemory:
    """
    Swarm feedback memory for tool selection and agent routing biases.
    """

    def __init__(self, table: str = "muse_assets"):
        self.table = table
        self.memory_type = "swarm_feedback"

    async def store_feedback(
        self,
        workspace_id: str,
        feedback: str,
        context: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> str:
        """Stores user feedback as swarm learning memory."""
        if metadata is None:
            metadata = {}

        metadata.setdefault("timestamp", datetime.now(timezone.utc).isoformat())
        metadata.setdefault("subtype", "feedback")
        metadata["type"] = self.memory_type

        content = self._build_content(feedback, context, metadata)

        try:
            embedder = InferenceProvider.get_embeddings()
            embedding = await embedder.aembed_query(content)
            feedback_id = await save_memory(
                workspace_id=workspace_id,
                content=content,
                embedding=embedding,
                memory_type=self.memory_type,
                metadata=metadata,
            )
            logger.info(
                "Swarm feedback stored for workspace %s with id %s",
                workspace_id,
                feedback_id,
            )
            return feedback_id
        except Exception as exc:
            logger.error("Failed to store swarm feedback: %s", exc)
            raise

    async def recall_feedback(
        self,
        workspace_id: str,
        query: str,
        limit: int = 3,
    ) -> List[Dict[str, Any]]:
        """Recalls feedback relevant to the current intent/query."""
        try:
            embedder = InferenceProvider.get_embeddings()
            query_embedding = await embedder.aembed_query(query)

            raw_results = await vector_search(
                workspace_id=workspace_id,
                embedding=query_embedding,
                table=self.table,
                limit=limit,
                filters={"type": self.memory_type, "subtype": "feedback"},
            )

            return [
                {"id": r[0], "content": r[1], "metadata": r[2], "similarity": r[3]}
                for r in raw_results
            ]
        except Exception as exc:
            logger.error("Swarm feedback recall failed: %s", exc)
            return []

    @staticmethod
    def _build_content(feedback: str, context: str, metadata: Dict[str, Any]) -> str:
        parts = [f"Feedback: {feedback}", f"Context: {context}"]
        signal = metadata.get("signal")
        tool_hint = metadata.get("tool_hint")
        agent_hint = metadata.get("agent_hint")

        if signal:
            parts.append(f"Signal: {signal}")
        if tool_hint:
            parts.append(f"Tool Hint: {tool_hint}")
        if agent_hint:
            parts.append(f"Agent Hint: {agent_hint}")

        return "\n".join(parts)
