"""
Memory controller for coordinating all memory systems.

This module provides the MemoryController class that coordinates
vector, graph, episodic, and working memory systems.
"""

import logging
import os
import uuid
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from ..agents.exceptions import DatabaseError, ValidationError, WorkspaceError
from .chunker import ContentChunker
from .embeddings import get_embedding_model
from .episodic_memory import EpisodicMemory
from .graph_memory import GraphMemory
from .models import MemoryChunk, MemoryType
from .vector_store import VectorMemory
from .working_memory import WorkingMemory

logger = logging.getLogger(__name__)


@dataclass
class MemoryQuery:
    """Memory query with parameters."""

    query: str
    workspace_id: str
    memory_types: Optional[List[str]] = None
    limit: int = 10
    min_similarity: float = 0.5
    include_episodic: bool = True
    include_vector: bool = True
    include_graph: bool = True
    session_id: Optional[str] = None
    user_id: Optional[str] = None


@dataclass
class MemoryResult:
    """Memory search result."""

    chunks: List[MemoryChunk]
    episodes: List[Episode]
    graph_entities: List[Dict[str, Any]]
    total_results: int
    query_time_ms: int
    sources_used: List[str]


class MemoryController:
    """
    Memory controller for coordinating all memory systems.

    Provides a unified interface for storing and retrieving memories
    across vector, graph, episodic, and working memory systems.
    """

    def __init__(self, supabase_client=None, redis_client=None):
        """
        Initialize memory controller.

        Args:
            supabase_client: Supabase client instance
            redis_client: Redis client instance
        """
        self.supabase_client = supabase_client
        self.redis_client = redis_client

        # Initialize memory systems
        self.vector_memory = VectorMemory(supabase_client)
        self.graph_memory = GraphMemory(supabase_client)
        self.episodic_memory = EpisodicMemory(supabase_client, redis_client)
        self.working_memory = WorkingMemory()

        # Initialize tools
        self.embedding_model = get_embedding_model()
        self.chunker = ContentChunker()

        logger.info("Memory controller initialized")

    async def store_memory(
        self,
        workspace_id: str,
        content: str,
        memory_type: MemoryType,
        metadata: Optional[Dict[str, Any]] = None,
        reference_id: Optional[str] = None,
        reference_table: Optional[str] = None,
        score: Optional[float] = None,
    ) -> str:
        """
        Store content in vector memory.

        Args:
            workspace_id: Workspace ID
            content: Content to store
            memory_type: Type of memory
            metadata: Additional metadata
            reference_id: Reference to source entity
            reference_table: Reference table name
            score: Quality score

        Returns:
            Memory chunk ID
        """
        try:
            # Create memory chunk
            chunk = MemoryChunk(
                workspace_id=workspace_id,
                memory_type=memory_type,
                content=content,
                metadata=metadata or {},
                reference_id=reference_id,
                reference_table=reference_table,
                score=score,
            )

            # Store in vector memory
            chunk_id = await self.vector_memory.store_chunk(chunk)

            # Store in working memory for quick access
            await self.working_memory.set_item(
                workspace_id=workspace_id,
                user_id=metadata.get("user_id", "system"),
                session_id=metadata.get("session_id", "default"),
                key=f"vector_memory:{chunk_id}",
                value=chunk.to_dict(),
                ttl=3600,  # 1 hour
            )

            logger.info(f"Stored memory chunk: {chunk_id}")
            return chunk_id

        except Exception as e:
            logger.error(f"Failed to store memory: {e}")
            raise DatabaseError(f"Failed to store memory: {e}")

    async def store_episode(
        self,
        workspace_id: str,
        user_id: str,
        session_id: str,
        content: str,
        episode_type: str = "conversation",
        title: str = "",
        metadata: Optional[Dict[str, Any]] = None,
        importance: float = 1.0,
        tags: Optional[List[str]] = None,
    ) -> str:
        """
        Store an episode in episodic memory.

        Args:
            workspace_id: Workspace ID
            user_id: User ID
            session_id: Session ID
            content: Episode content
            episode_type: Type of episode
            title: Episode title
            metadata: Additional metadata
            importance: Importance score
            tags: Episode tags

        Returns:
            Episode ID
        """
        try:
            # Create episode
            episode = Episode(
                workspace_id=workspace_id,
                user_id=user_id,
                session_id=session_id,
                episode_type=episode_type,
                title=title,
                content=content,
                metadata=metadata or {},
                importance=importance,
                tags=tags or [],
            )

            # Store in episodic memory
            episode_id = await self.episodic_memory.store_episode(episode)

            # Also store in vector memory for semantic search
            await self.store_memory(
                workspace_id=workspace_id,
                content=content,
                memory_type=MemoryType.CONVERSATION,
                metadata={
                    "episode_id": episode_id,
                    "episode_type": episode_type,
                    "user_id": user_id,
                    "session_id": session_id,
                    "title": title,
                },
                reference_id=episode_id,
                reference_table="episodes",
            )

            logger.info(f"Stored episode: {episode_id}")
            return episode_id

        except Exception as e:
            logger.error(f"Failed to store episode: {e}")
            raise DatabaseError(f"Failed to store episode: {e}")

    async def search_memory(self, query: MemoryQuery) -> MemoryResult:
        """
        Search across all memory systems.

        Args:
            query: Memory query parameters

        Returns:
            Memory search results
        """
        start_time = datetime.now()
        sources_used = []

        try:
            chunks = []
            episodes = []
            graph_entities = []

            # Search vector memory
            if query.include_vector and query.memory_types:
                try:
                    vector_chunks = await self.vector_memory.search_chunks(
                        workspace_id=query.workspace_id,
                        query_text=query.query,
                        memory_types=query.memory_types,
                        limit=query.limit,
                        min_similarity=query.min_similarity,
                    )
                    chunks.extend(vector_chunks)
                    sources_used.append("vector_memory")
                except Exception as e:
                    logger.error(f"Vector memory search failed: {e}")

            # Search episodic memory
            if query.include_episodic:
                try:
                    episode_results = await self.episodic_memory.search_episodes(
                        workspace_id=query.workspace_id,
                        query=query.query,
                        memory_types=query.memory_types,
                        limit=query.limit,
                        min_similarity=query.min_similarity,
                    )
                    episodes.extend(episode_results)
                    sources_used.append("episodic_memory")
                except Exception as e:
                    logger.error(f"Episodic memory search failed: {e}")

            # Search graph memory
            if query.include_graph:
                try:
                    graph_results = await self.graph_memory.search_entities(
                        workspace_id=query.workspace_id,
                        query=query.query,
                        limit=query.limit,
                    )
                    graph_entities.extend(graph_results)
                    sources_used.append("graph_memory")
                except Exception as e:
                    logger.error(f"Graph memory search failed: {e}")

            # Calculate query time
            query_time = (datetime.now() - start_time).total_seconds() * 1000

            # Combine and rank results
            total_results = len(chunks) + len(episodes) + len(graph_entities)

            result = MemoryResult(
                chunks=chunks[: query.limit],
                episodes=episodes[: query.limit],
                graph_entities=graph_entities[: query.limit],
                total_results=total_results,
                query_time_ms=int(query_time),
                sources_used=sources_used,
            )

            logger.info(
                f"Memory search completed: {total_results} results in {query_time:.2f}ms"
            )
            return result

        except Exception as e:
            logger.error(f"Memory search failed: {e}")
            raise DatabaseError(f"Memory search failed: {e}")

    async def get_session_context(
        self, workspace_id: str, session_id: str, limit: int = 20
    ) -> Dict[str, Any]:
        """
        Get context for a session including recent memories and episodes.

        Args:
            workspace_id: Workspace ID
            session_id: Session ID
            limit: Maximum number of items to retrieve

        Returns:
            Session context dictionary
        """
        try:
            # Get recent episodes from session
            episodes = await self.episodic_memory.get_session_episodes(
                workspace_id=workspace_id, session_id=session_id, limit=limit
            )

            # Get recent vector memories for session
            query = MemoryQuery(
                query=session_id,
                workspace_id=workspace_id,
                memory_types=MemoryType.get_all_types(),
                limit=limit,
                include_episodic=False,
                include_graph=False,
            )

            vector_results = await self.search_memory(query)

            # Get working memory context
            working_context = await self.working_memory.get_session_context(
                workspace_id=workspace_id, session_id=session_id
            )

            context = {
                "session_id": session_id,
                "workspace_id": workspace_id,
                "episodes": [episode.to_dict() for episode in episodes],
                "vector_memories": [chunk.to_dict() for chunk in vector_results.chunks],
                "working_context": working_context,
                "total_items": len(episodes) + len(vector_results.chunks),
            }

            return context

        except Exception as e:
            logger.error(f"Failed to get session context: {e}")
            raise DatabaseError(f"Failed to get session context: {e}")

    async def get_workspace_summary(
        self, workspace_id: str, limit: int = 50
    ) -> Dict[str, Any]:
        """
        Get summary of all memories in a workspace.

        Args:
            workspace_id: Workspace ID
            limit: Maximum items per type

        Returns:
            Workspace summary dictionary
        """
        try:
            # Get vector memory stats
            vector_stats = await self.vector_memory.get_memory_stats(workspace_id)

            # Get episodic memory stats
            episodic_stats = await self.episodic_memory.get_memory_stats(workspace_id)

            # Get graph memory stats
            graph_stats = await self.graph_memory.get_memory_stats(workspace_id)

            # Get working memory stats
            working_stats = await self.working_memory.get_workspace_stats(workspace_id)

            # Get recent items from each system
            recent_chunks = await self.vector_memory.get_recent_chunks(
                workspace_id=workspace_id, limit=limit
            )

            recent_episodes = await self.episodic_memory.search_episodes(
                workspace_id=workspace_id, query="", limit=limit
            )

            recent_entities = await self.graph_memory.get_recent_entities(
                workspace_id=workspace_id, limit=limit
            )

            summary = {
                "workspace_id": workspace_id,
                "vector_memory": vector_stats,
                "episodic_memory": episodic_stats,
                "graph_memory": graph_stats,
                "working_memory": working_stats,
                "recent_items": {
                    "vector_chunks": [chunk.to_dict() for chunk in recent_chunks],
                    "episodes": [episode.to_dict() for episode in recent_episodes],
                    "graph_entities": recent_entities,
                },
                "total_memories": (
                    vector_stats.get("total_chunks", 0)
                    + episodic_stats.get("total_episodes", 0)
                    + graph_stats.get("total_entities", 0)
                ),
            }

            return summary

        except Exception as e:
            logger.error(f"Failed to get workspace summary: {e}")
            raise DatabaseError(f"Failed to get workspace summary: {e}")

    async def cleanup_expired_memories(
        self, workspace_id: str, max_age_days: int = 365
    ) -> Dict[str, int]:
        """
        Clean up expired memories across all systems.

        Args:
            workspace_id: Workspace ID
            max_age_days: Maximum age in days

        Returns:
            Dictionary with cleanup counts per system
        """
        try:
            cleanup_counts = {}

            # Clean up vector memory
            vector_count = await self.vector_memory.cleanup_expired_chunks(
                workspace_id=workspace_id, max_age_days=max_age_days
            )
            cleanup_counts["vector_memory"] = vector_count

            # Clean up episodic memory
            episodic_count = await self.episodic_memory.cleanup_expired_episodes(
                workspace_id=workspace_id, max_age_days=max_age_days
            )
            cleanup_counts["episodic_memory"] = episodic_count

            # Clean up graph memory
            graph_count = await self.graph_memory.cleanup_expired_entities(
                workspace_id=workspace_id, max_age_days=max_age_days
            )
            cleanup_counts["graph_memory"] = graph_count

            # Clean up working memory (shorter TTL)
            working_count = await self.working_memory.cleanup_expired_items(
                workspace_id=workspace_id, max_age_days=7  # 1 week for working memory
            )
            cleanup_counts["working_memory"] = working_count

            total_cleaned = sum(cleanup_counts.values())
            logger.info(
                f"Cleaned up {total_cleaned} expired memories in workspace {workspace_id}"
            )

            return cleanup_counts

        except Exception as e:
            logger.error(f"Failed to cleanup expired memories: {e}")
            raise DatabaseError(f"Failed to cleanup expired memories: {e}")

    async def export_workspace_memories(
        self, workspace_id: str, format: str = "json"
    ) -> Dict[str, Any]:
        """
        Export all memories from a workspace.

        Args:
            workspace_id: Workspace ID
            format: Export format (json, csv, etc.)

        Returns:
            Exported data dictionary
        """
        try:
            # Get all memories from each system
            vector_chunks = await self.vector_memory.get_all_chunks(workspace_id)
            episodes = await self.episodic_memory.get_all_episodes(workspace_id)
            graph_entities = await self.graph_memory.get_all_entities(workspace_id)

            export_data = {
                "workspace_id": workspace_id,
                "export_timestamp": datetime.now().isoformat(),
                "format": format,
                "vector_memory": [chunk.to_dict() for chunk in vector_chunks],
                "episodic_memory": [episode.to_dict() for episode in episodes],
                "graph_memory": graph_entities,
                "statistics": {
                    "total_chunks": len(vector_chunks),
                    "total_episodes": len(episodes),
                    "total_entities": len(graph_entities),
                },
            }

            logger.info(f"Exported workspace memories: {workspace_id}")
            return export_data

        except Exception as e:
            logger.error(f"Failed to export workspace memories: {e}")
            raise DatabaseError(f"Failed to export workspace memories: {e}")

    async def import_workspace_memories(
        self, workspace_id: str, import_data: Dict[str, Any]
    ) -> Dict[str, int]:
        """
        Import memories into a workspace.

        Args:
            workspace_id: Workspace ID
            import_data: Imported data dictionary

        Returns:
            Dictionary with import counts per system
        """
        try:
            import_counts = {}

            # Import vector memories
            vector_data = import_data.get("vector_memory", [])
            vector_count = 0
            for chunk_data in vector_data:
                try:
                    chunk = MemoryChunk.from_dict(chunk_data)
                    chunk.workspace_id = workspace_id  # Override workspace_id
                    await self.vector_memory.store_chunk(chunk)
                    vector_count += 1
                except Exception as e:
                    logger.error(f"Failed to import vector chunk: {e}")

            import_counts["vector_memory"] = vector_count

            # Import episodic memories
            episode_data = import_data.get("episodic_memory", [])
            episode_count = 0
            for ep_data in episode_data:
                try:
                    episode = Episode.from_dict(ep_data)
                    episode.workspace_id = workspace_id  # Override workspace_id
                    await self.episodic_memory.store_episode(episode)
                    episode_count += 1
                except Exception as e:
                    logger.error(f"Failed to import episode: {e}")

            import_counts["episodic_memory"] = episode_count

            # Import graph memories
            graph_data = import_data.get("graph_memory", [])
            graph_count = await self.graph_memory.import_entities(
                workspace_id, graph_data
            )
            import_counts["graph_memory"] = graph_count

            total_imported = sum(import_counts.values())
            logger.info(
                f"Imported {total_imported} memories into workspace {workspace_id}"
            )

            return import_counts

        except Exception as e:
            logger.error(f"Failed to import workspace memories: {e}")
            raise DatabaseError(f"Failed to import workspace memories: {e}")

    def __str__(self) -> str:
        """String representation."""
        return "MemoryController(vector+graph+episodic+working)"


# Convenience functions
def get_memory_controller(supabase_client=None, redis_client=None) -> MemoryController:
    """Get memory controller instance."""
    return MemoryController(supabase_client, redis_client)


def create_memory_query(
    workspace_id: str,
    query: str,
    memory_types: Optional[List[str]] = None,
    limit: int = 10,
    min_similarity: float = 0.5,
    session_id: Optional[str] = None,
    user_id: Optional[str] = None,
) -> MemoryQuery:
    """Create a memory query."""
    return MemoryQuery(
        query=query,
        workspace_id=workspace_id,
        memory_types=memory_types,
        limit=limit,
        min_similarity=min_similarity,
        session_id=session_id,
        user_id=user_id,
    )
