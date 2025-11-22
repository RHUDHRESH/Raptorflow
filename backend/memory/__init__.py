"""
Memory management system for RaptorFlow agents.

This module provides persistent memory capabilities for agents to:
- Store execution results, user preferences, and feedback
- Recall relevant context from past interactions
- Learn from user feedback to improve performance
- Track performance metrics over time

Components:
- MemoryManager: Core interface for agent memory operations
- MemoryStore: Backend storage implementation (vector + structured)
- MemorySearch: Semantic search over historical memories
"""

from backend.memory.manager import MemoryManager

__all__ = ["MemoryManager"]
