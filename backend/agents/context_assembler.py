import logging
from typing import Dict, List, TypedDict

from db import vector_search

logger = logging.getLogger("raptorflow.context_assembler")


class SemanticRAGNode:
    """
    SOTA Retrieval Node.
    Surgically retrieves evergreen brand knowledge from the fact_store (pgvector).
    """

    async def __call__(self, state: TypedDict):
        """Node execution logic."""
        workspace_id = state.get("workspace_id")
        logger.info(f"Retrieving semantic facts for workspace {workspace_id}...")

        # 1. Embed raw_prompt (simulated)
        dummy_embedding = [0.1] * 768

        # 2. Search muse_assets (foundation + approved assets)
        facts = await vector_search(
            workspace_id=workspace_id,
            embedding=dummy_embedding,
            table="muse_assets",
            limit=5,
            filters={"type": "foundation"},
        )

        logger.info(f"Retrieved {len(facts)} surgical facts.")

        return {"context_brief": {"retrieved_facts": [f[1] for f in facts]}}


def create_rag_node():
    return SemanticRAGNode()


class ContextAssemblerAgent:
    """
    Assembles the 'Knowledge Pack' for the generation agents.
    Pulls from Supabase pgvector and standard tables.
    """

    async def assemble(self, entities: List[str], goal: str) -> Dict:
        # 1. Search for Brand Voice / Foundation context
        # In a real impl, we'd embed the goal and search pgvector
        # For now, we simulate the 'Surgical' context retrieval

        context_pack = {
            "brand_voice": "ChatGPT simplicity + MasterClass polish + Editorial restraint.",
            "taboo_words": ["unlock", "game-changer", "delighted"],
            "retrieved_docs": [],
        }

        # If user mentioned a specific entity (@mention)
        if entities:
            # logic to fetch specific ICP or Campaign from DB
            pass

        return context_pack
