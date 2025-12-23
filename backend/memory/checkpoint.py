import logging
from typing import Optional
from backend.db import init_checkpointer

logger = logging.getLogger("raptorflow.memory.checkpoint")

class StateCheckpointManager:
    """
    SOTA State Checkpoint Manager.
    Orchestrates LangGraph persistence using Supabase/Postgres.
    Singleton pattern ensures unified checkpointer access across the engine.
    """
    _instance: Optional['StateCheckpointManager'] = None
    _checkpointer = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(StateCheckpointManager, cls).__new__(cls)
        return cls._instance

    async def get_checkpointer(self):
        """Initializes and returns the LangGraph checkpointer."""
        if self._checkpointer is None:
            logger.info("Initializing LangGraph State Checkpointer...")
            try:
                self._checkpointer = await init_checkpointer()
            except Exception as e:
                logger.error(f"Failed to initialize checkpointer: {e}")
                raise
        return self._checkpointer

    async def clear_checkpoint(self, thread_id: str):
        """Manually clears a checkpoint for a specific thread."""
        # Note: PostgresSaver doesn't always have a direct 'clear' but we can delete from the table
        # For now, we log the intent as LangGraph 0.2 manages lifecycle mostly automatically
        logger.warning(f"Checkpoint clearing requested for thread {thread_id} (Manual DB action required).")
