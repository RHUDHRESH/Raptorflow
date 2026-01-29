"""
Memory system package for Raptorflow.
Handles vector, graph, episodic, and working memory.
"""

from .controller import SimpleMemoryController as MemoryController
from .models import MemoryChunk, MemoryType


# Create AgentMemoryManager for backward compatibility
class AgentMemoryManager:
    """Agent memory manager (backward compatibility)."""

    def __init__(self):
        self.controller = MemoryController()

    def add_memory(self, agent_id: str, memory_type: str, content: str):
        """Add memory for agent."""
        return self.controller.add_memory(agent_id, memory_type, content)

    def get_memory(self, agent_id: str, memory_type: str = None):
        """Get memory for agent."""
        return self.controller.get_memory(agent_id, memory_type)


__all__ = [
    "MemoryType",
    "MemoryChunk",
    "MemoryController",
    "AgentMemoryManager",
]
