import logging
from typing import Any, Dict, Optional

from backend.inference import InferenceProvider
from backend.memory.episodic_l2 import L2EpisodicMemory
from backend.memory.semantic_l3 import L3SemanticMemory

logger = logging.getLogger("raptorflow.memory.swarm_learning")


async def record_learning(
    workspace_id: Optional[str],
    content: str,
    evaluation: Dict[str, Any],
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """
    Records evaluator outcomes and schedules promotion to L2/L3 based on confidence.
    """
    if metadata is None:
        metadata = {}

    metadata.update(
        {
            "evaluation_score": evaluation.get("score"),
            "evaluation_confidence": evaluation.get("confidence"),
            "promotion_targets": evaluation.get("promotion_targets", []),
        }
    )

    result = {
        "workspace_id": workspace_id,
        "content": content,
        "evaluation": evaluation,
        "metadata": metadata,
    }

    if not workspace_id:
        logger.warning("No workspace_id provided; skipping L2/L3 promotion.")
        return result

    promote_to_l2 = evaluation.get("promote_to_l2", False)
    promote_to_l3 = evaluation.get("promote_to_l3", False)

    if not (promote_to_l2 or promote_to_l3):
        logger.info("Learning does not meet promotion thresholds.")
        return result

    embedder = InferenceProvider.get_embeddings()
    embedding = await embedder.aembed_query(content)

    if promote_to_l2:
        l2_memory = L2EpisodicMemory()
        await l2_memory.store_episode(
            workspace_id=workspace_id,
            content=content,
            embedding=embedding,
            metadata={**metadata, "promotion_level": "L2"},
        )
        logger.info("Learning promoted to L2 episodic memory.")

    if promote_to_l3:
        l3_memory = L3SemanticMemory()
        await l3_memory.remember_foundation(
            workspace_id=workspace_id,
            content=content,
            embedding=embedding,
            metadata={**metadata, "promotion_level": "L3"},
        )
        logger.info("Learning promoted to L3 semantic memory.")

    return result
