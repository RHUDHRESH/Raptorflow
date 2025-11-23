RaptorFlow Memory System

This module provides a comprehensive memory architecture for the RaptorFlow
multi-agent marketing OS. It supports multiple memory types for different
use cases and timeframes.

Memory Types:
-------------
- ConversationMemory: Short-term session-based conversation history (TTL: 1 hour)
- AgentMemory: Agent-specific learning, patterns, and performance history
- WorkspaceMemory: Shared workspace context (ICPs, brand voice, preferences)
- SemanticMemory: Vector-based semantic search across all generated content
- WorkingMemory: Temporary execution state and intermediate results

Main Components:
----------------
- BaseMemory: Abstract base class defining the memory interface
- MemoryManager: Orchestrator for all memory types with unified API
- Individual memory implementations for each type

Usage:
------
from memory import MemoryManager, get_memory_manager

# Initialize the memory manager
memory_manager = MemoryManager()

# Or use the singleton
memory = get_memory_manager()

# Store conversation memory
await memory.remember(
    memory_type="conversation",
    key="session:123",
    value={"role": "user", "content": "Hello"},
    workspace_id=workspace_id
)

# Retrieve context for a task
context = await memory.get_context(
    workspace_id=workspace_id,
    task_type="campaign_planning"
)
"""

from memory.base import BaseMemory, MemoryError
from memory.conversation_memory import ConversationMemory
from memory.agent_memory import AgentMemory
from memory.workspace_memory import WorkspaceMemory
from memory.semantic_memory import SemanticMemory
from memory.embeddings import EmbeddingGenerator, get_embedder
from memory.memory_manager import MemoryManager, get_memory_manager

__all__ = [
    # Base classes
    "BaseMemory",
    "MemoryError",

    # Memory implementations
    "ConversationMemory",
    "AgentMemory",
    "WorkspaceMemory",
    "SemanticMemory",

    # Embeddings
    "EmbeddingGenerator",
    "get_embedder",

    # Manager
    "MemoryManager",
    "get_memory_manager",
]
