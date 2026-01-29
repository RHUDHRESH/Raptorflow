"""
Memory services wrapper to handle import issues.
Provides a clean interface for memory system functionality.
"""

import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add backend to path for proper imports
backend_path = Path(__file__).parent
sys.path.insert(0, str(backend_path))

# Import exceptions with fallback
try:
    from ..exceptions import DatabaseError, ValidationError, WorkspaceError
except ImportError:
    # Fallback definitions
    class DatabaseError(Exception):
        pass

    class ValidationError(Exception):
        pass

    class WorkspaceError(Exception):
        pass


class MemoryController:
    """Simplified memory controller with proper imports"""

    def __init__(self):
        self.initialized = False
        self._init_memory_systems()

    def _init_memory_systems(self):
        """Initialize memory systems with error handling"""
        try:
            # Try to import and initialize memory components
            from memory.episodic_memory import EpisodicMemory
            from memory.graph_memory import GraphMemory
            from memory.vector_store import VectorMemory
            from memory.working_memory import WorkingMemory

            self.vector_memory = VectorMemory()
            self.graph_memory = GraphMemory()
            self.episodic_memory = EpisodicMemory()
            self.working_memory = WorkingMemory()

            self.initialized = True

        except ImportError as e:
            print(f"Memory system import error: {e}")
            self.initialized = False
        except Exception as e:
            print(f"Memory system initialization error: {e}")
            self.initialized = False

    async def store_episodic_memory(
        self, workspace_id: str, content: str, context: Dict[str, Any]
    ) -> str:
        """Store episodic memory with validation"""
        if not self.initialized:
            raise DatabaseError("Memory system not initialized")

        if not workspace_id:
            raise ValidationError("Workspace ID is required")

        if not content or len(content.strip()) == 0:
            raise ValidationError("Content cannot be empty")

        try:
            return await self.episodic_memory.add_episode(
                workspace_id=workspace_id, content=content, context=context
            )
        except Exception as e:
            raise DatabaseError(f"Failed to store episodic memory: {e}")

    async def search_memories(
        self, workspace_id: str, query: str, limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Search across all memory types"""
        if not self.initialized:
            return []

        try:
            results = []

            # Search vector memory
            vector_results = await self.vector_memory.search(
                workspace_id=workspace_id, query=query, limit=limit
            )
            results.extend(vector_results)

            return results

        except Exception as e:
            print(f"Memory search error: {e}")
            return []

    def is_available(self) -> bool:
        """Check if memory system is available"""
        return self.initialized


# Global memory controller instance
_memory_controller = None


def get_memory_controller() -> MemoryController:
    """Get global memory controller instance"""
    global _memory_controller
    if _memory_controller is None:
        _memory_controller = MemoryController()
    return _memory_controller
