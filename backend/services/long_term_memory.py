"""
Long-Term Memory Service (Experience Vault)
===========================================

Vectorizes strategic outcomes into the DCM learning pool.
"""

import logging
from typing import Any, Dict, List, Optional
from backend.core.supabase_mgr import get_supabase_client
from backend.memory.bcm_vector_manager import BCMVectorManager

logger = logging.getLogger(__name__)

class LongTermMemoryService:
    """Service for preserving high-value strategic experiences."""

    def __init__(self):
        self.vector_manager = BCMVectorManager()
        self.supabase = get_supabase_client()

    async def vectorize_move_outcome(self, workspace_id: str, move_id: str, outcome: Dict[str, Any]) -> bool:
        """
        Stores a move's post-mortem into long-term vector memory.
        This enables 'Distance Context' matching for future similar goals.
        """
        try:
            content = f"Move: {outcome.get('move_name')}. Result: {outcome.get('summary')}. Success Score: {outcome.get('success_score')}"
            
            # Store in vector DB
            await self.vector_manager.add_context(
                workspace_id=workspace_id,
                content=content,
                metadata={
                    "move_id": move_id,
                    "type": "experience_vault",
                    "success_score": outcome.get("success_score")
                }
            )
            
            logger.info(f"Vectorized move {move_id} into Experience Vault.")
            return True
        except Exception as e:
            logger.error(f"Failed to vectorize move outcome: {e}")
            return False

    async def get_relevant_experiences(self, workspace_id: str, query: str) -> List[Dict[str, Any]]:
        """
        Retrieves similar past experiences to inform current strategy.
        """
        return await self.vector_manager.search_context(workspace_id, query, limit=3)
