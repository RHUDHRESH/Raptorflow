"""
MacM (Memory Augmented Context) Hub
==================================

Hub for short-term and session-based context management.
Integrates SimpleMemoryController to provide a "Working Memory" for agents.
"""

import logging
from datetime import UTC, datetime
from typing import Any, Dict, List, Optional

from memory.controller import SimpleMemoryController

from .core.supabase_mgr import get_supabase_client
from .services.dcm import get_dcm

logger = logging.getLogger("raptorflow.services.macm")


class MacMHub:
    """
    MacM Hub manages the 'Hot Path' of context.
    It tracks recent interactions, session state, and reset-button logic.
    """

    def __init__(self, memory_controller: Optional[SimpleMemoryController] = None):
        self.memory = memory_controller or SimpleMemoryController()
        self.client = get_supabase_client()

    async def get_session_context(
        self, session_id: str, workspace_id: str
    ) -> Dict[str, Any]:
        """
        Retrieves recent context for a specific session.
        """
        logger.info(f"MacM: Fetching hot context for session {session_id}")

        # 1. Get working memory from SimpleMemoryController
        working_context = await self.memory.retrieve_memory(
            f"session:{session_id}", memory_type="working"
        )

        # 2. Get recent move interactions from Supabase
        recent_moves = (
            self.client.table("moves")
            .select("name, goal, status")
            .eq("workspace_id", workspace_id)
            .order("updated_at", desc=True)
            .limit(3)
            .execute()
        )

        return {
            "session_id": session_id,
            "working_memory": working_context or {},
            "recent_moves": recent_moves.data or [],
            "timestamp": datetime.now(UTC).isoformat(),
        }


class ContextAssembler:
    """
    The Master Synthesizer.
    Merges [User Input + DCM + MacM + BCM] into a surgical prompt.
    """

    def __init__(self):
        self.dcm = get_dcm()
        self.macm = MacMHub()

    async def assemble_strategic_context(
        self, workspace_id: str, user_prompt: str, session_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Highest-fidelity context assembly for specialists.
        """
        logger.info("ContextAssembler: Synthesizing multi-vector strategic context.")

        # 1. DCM Semantic Sort (BCM & Market Intel)
        dcm_data = await self.dcm.get_relevant_context(workspace_id, user_prompt)

        # 2. MacM Session Context
        session_data = {}
        if session_id:
            session_data = await self.macm.get_session_context(session_id, workspace_id)

        # 3. Assemble Ground Truth
        context_payload = {
            "origin_prompt": user_prompt,
            "ground_truth": {
                "semantic_context": dcm_data.get("fragments", []),
                "session_context": session_data,
                "bcm_snippets": dcm_data.get("cached_snippets", {}),
            },
            "meta": {
                "workspace_id": workspace_id,
                "synthesized_at": datetime.now(UTC).isoformat(),
            },
        }

        return context_payload


# Singleton instance
_assembler_instance: Optional[ContextAssembler] = None


def get_context_assembler() -> ContextAssembler:
    global _assembler_instance
    if _assembler_instance is None:
        _assembler_instance = ContextAssembler()
    return _assembler_instance
