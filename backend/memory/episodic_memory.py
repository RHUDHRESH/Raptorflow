"""
Episodic memory system for conversation and session tracking.

This module provides episodic memory storage and retrieval
for conversations, user interactions, and session history.
"""

import json
import logging
import os
import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Union

from embeddings import get_embedding_model

from .agents.exceptions import DatabaseError, ValidationError, WorkspaceError
from .models import MemoryChunk, MemoryType
from .redis_client import get_redis_client

logger = logging.getLogger(__name__)


@dataclass
class Episode:
    """Single episode in episodic memory."""

    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    workspace_id: str = ""
    user_id: str = ""
    session_id: str = ""
    episode_type: str = "conversation"  # conversation, interaction, feedback, decision
    title: str = ""
    content: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None
    timestamp: datetime = field(default_factory=datetime.now)
    importance: float = 1.0  # 0.0 to 1.0
    tags: List[str] = field(default_factory=list)

    def __post_init__(self):
        """Initialize default values."""
        if not self.id:
            self.id = str(uuid.uuid4())

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "workspace_id": self.workspace_id,
            "user_id": self.user_id,
            "session_id": self.session_id,
            "episode_type": self.episode_type,
            "title": self.title,
            "content": self.content,
            "metadata": self.metadata,
            "embedding": self.embedding,
            "timestamp": self.timestamp.isoformat(),
            "importance": self.importance,
            "tags": self.tags,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Episode":
        """Create from dictionary."""
        if data.get("timestamp"):
            data["timestamp"] = datetime.fromisoformat(data["timestamp"])

        return cls(**data)

    def get_token_count(self) -> int:
        """Estimate token count (rough approximation: 1 token ≈ 4 characters)."""
        return len(self.content) // 4

    def add_tag(self, tag: str):
        """Add a tag to the episode."""
        if tag not in self.tags:
            self.tags.append(tag)

    def has_tag(self, tag: str) -> bool:
        """Check if episode has a specific tag."""
        return tag in self.tags

    def is_expired(self, max_age_days: int = 365) -> bool:
        """Check if episode is older than max_age_days."""
        age = datetime.now() - self.timestamp
        return age.days > max_age_days

    def truncate_content(self, max_length: int = 1000) -> str:
        """Truncate content to max_length with ellipsis."""
        if len(self.content) <= max_length:
            return self.content
        return self.content[: max_length - 3] + "..."

    def __str__(self) -> str:
        """String representation."""
        return f"Episode(id={self.id}, type={self.episode_type}, title='{self.title[:50]}...')"


class EpisodicMemory:
    """Episodic memory system for conversation and session tracking."""

    def __init__(self, supabase_client=None, redis_client=None):
        """
        Initialize episodic memory system.

        Args:
            supabase_client: Supabase client instance
            redis_client: Redis client instance
        """
        self.supabase_client = supabase_client
        self.redis_client = redis_client or get_redis_client()
        self.embedding_model = get_embedding_model()

        # Initialize Supabase client if not provided
        if self.supabase_client is None:
            self._init_supabase_client()

        # Table name for episodic storage
        self._table_name = "episodic_memory"

    def _init_supabase_client(self):
        """Initialize Supabase client from environment variables."""
        try:
            from supabase import create_client

            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

            if supabase_url and supabase_key:
                self.supabase_client = create_client(supabase_url, supabase_key)
                logger.info("Initialized Supabase client for episodic memory")
            else:
                logger.warning(
                    "Supabase credentials not found, episodic memory will be limited"
                )
                self.supabase_client = None
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            self.supabase_client = None

    async def store_episode(self, episode: Episode) -> str:
        """
        Store an episode in episodic memory.

        Args:
            episode: Episode to store

        Returns:
            Episode ID
        """
        if not self.supabase_client:
            # Fallback to Redis storage
            return await self._store_episode_redis(episode)

        try:
            # Generate embedding if not provided
            if episode.embedding is None:
                embedding = self.embedding_model.encode_single(episode.content)
                episode.embedding = embedding.tolist()

            # Store in Supabase
            data = episode.to_dict()

            result = self.supabase_client.table(self._table_name).insert(data).execute()

            if result.data:
                return result.data[0]["id"]
            else:
                raise DatabaseError("Failed to store episode in Supabase")

        except Exception as e:
            logger.error(f"Failed to store episode in Supabase: {e}")
            # Fallback to Redis
            return await self._store_episode_redis(episode)

    async def _store_episode_redis(self, episode: Episode) -> str:
        """Store episode in Redis."""
        try:
            key = f"episodic:{episode.workspace_id}:{episode.id}"

            data = {
                "episode": episode.to_dict(),
                "stored_at": datetime.now().isoformat(),
            }

            await self.redis_client.setex(
                key=key, value=json.dumps(data), ex=86400  # 24 hours
            )

            return episode.id

        except Exception as e:
            logger.error(f"Failed to store episode in Redis: {e}")
            raise DatabaseError(f"Failed to store episode: {e}")

    async def retrieve_episode(
        self, episode_id: str, workspace_id: str
    ) -> Optional[Episode]:
        """
        Retrieve an episode by ID.

        Args:
            episode_id: Episode ID
            workspace_id: Workspace ID for security

        Returns:
            Episode object or None if not found
        """
        if not self.supabase_client:
            # Fallback to Redis
            return await self._retrieve_episode_redis(episode_id, workspace_id)

        try:
            result = (
                self.supabase_client.table(self._table_name)
                .select("*")
                .eq("id", episode_id)
                .eq("workspace_id", workspace_id)
                .execute()
            )

            if result.data:
                episode_data = result.data[0]
                return Episode.from_dict(episode_data)
            else:
                return None

        except Exception as e:
            logger.error(f"Failed to retrieve episode from Supabase: {e}")
            # Fallback to Redis
            return await self._retrieve_episode_redis(episode_id, workspace_id)

    async def _retrieve_episode_redis(
        self, episode_id: str, workspace_id: str
    ) -> Optional[Episode]:
        """Retrieve episode from Redis."""
        try:
            key = f"episodic:{workspace_id}:{episode_id}"

            data = await self.redis_client.get(key)

            if data:
                episode_data = json.loads(data)
                episode_data = episode_data.get("episode")
                return Episode.from_dict(episode_data)
            else:
                return None

        except Exception as e:
            logger.error(f"Failed to retrieve episode from Redis: {e}")
            return None

    async def search_episodes(
        self,
        workspace_id: str,
        query: str,
        memory_types: Optional[List[str]] = None,
        limit: int = 10,
        min_similarity: float = 0.5,
    ) -> List[Episode]:
        """
        Search episodes by semantic similarity.

        Args:
            workspace_id: Workspace ID for security
            query: Search query text
            memory_types: Optional list of episode types to filter by
            limit: Maximum number of results
            min_similarity: Minimum similarity score

        Returns:
            List of matching episodes
        """
        # Generate query embedding
        query_embedding = self.embedding_model.encode_single(query)

        # Search in Supabase if available
        if self.supabase_client:
            try:
                # For now, we'll use a simple text-based search
                # In a real implementation, this would use vector similarity
                result = (
                    self.supabase.table(self._table_name)
                    .select("*")
                    .eq("workspace_id", workspace_id)
                )

                # Add type filtering if specified
                if memory_types:
                    for memory_type in memory_types:
                        result = result.or_("episode_type", "eq", memory_type)

                # Add text search
                if query:
                    result = result.or_("content", "ilike", f"%{query}%")

                # Order by timestamp desc
                result = result.order("timestamp", desc=desc).limit(limit)

                episodes_data = result.execute()

                episodes = []
                for episode_data in episodes_data:
                    episode = Episode.from_dict(episode_data)

                    # Simple relevance scoring based on text matching
                    if query:
                        if query.lower() in episode.content.lower():
                            episodes.append(episode)

                return episodes[:limit]

            except Exception as e:
                logger.error(f"Failed to search episodes in Supabase: {e}")

        # Fallback to Redis search
        return await self._search_episodes_redis(
            workspace_id, query, memory_types, limit
        )

    async def _search_episodes_redis(
        self,
        workspace_id: str,
        query: str,
        memory_types: Optional[List[str]] = None,
        limit: int = 10,
    ) -> List[Episode]:
        """Search episodes in Redis."""
        try:
            # Get all episode keys for workspace
            pattern = f"episodic:{workspace_id}:*"
            keys = await self.redis_client.keys(pattern)

            episodes = []

            for key in keys:
                try:
                    data = await self.redis_client.get(key)
                    if data:
                        episode_data = json.loads(data)
                        episode_data = episode_data.get("episode")
                        episode = Episode.from_dict(episode_data)

                        # Filter by type if specified
                        if memory_types and episode.episode_type not in memory_types:
                            continue

                        # Simple text matching
                        if query and query.lower() not in episode.content.lower():
                            continue

                        episodes.append(episode)

                except Exception as e:
                    logger.error(f"Error parsing episode data: {e}")
                    continue

            # Sort by timestamp
            episodes.sort(key=lambda x: x.timestamp, reverse=True)
            return episodes[:limit]

        except Exception as e:
            logger.error(f"Failed to search episodes in Redis: {e}")
            return []

    async def get_session_episodes(
        self, workspace_id: str, session_id: str, limit: int = 50
    ) -> List[Episode]:
        """
        Get all episodes for a session.

        Args:
            workspace_id: Workspace ID for security
            session_id: Session ID
            limit: Maximum number of episodes

        Returns:
            List of episodes in the session
        """
        return await self.search_episodes(
            workspace_id=workspace_id,
            query=session_id,
            memory_types=["conversation"],
            limit=limit,
        )

    async def get_user_episodes(
        self, workspace_id: str, user_id: str, limit: int = 50
    ) -> List[Episode]:
        """
        Get all episodes for a user.

        Args:
            workspace_id: Workspace ID for security
            user_id: User ID
            limit: Maximum number of episodes

        Returns:
            List of episodes for the user
        """
        return await self.search_episodes(
            workspace_id=workspace_id, query=user_id, limit=limit
        )

    async def delete_episode(self, episode_id: str, workspace_id: str) -> bool:
        """
        Delete an episode.

        Args:
            episode_id: Episode ID
            workspace_id: Workspace ID for security

        Returns:
            True if deleted, False otherwise
        """
        if self.supabase_client:
            try:
                result = (
                    self.supabase.table(self._table_name)
                    .delete()
                    .eq("id", episode_id)
                    .eq("workspace_id", workspace_id)
                    .execute()
                )
                return result.count > 0
            except Exception as e:
                logger.error(f"Failed to delete episode from Supabase: {e}")

        # Fallback to Redis
        try:
            key = f"episodic:{workspace_id}:{episode_id}"
            result = await self.redis_client.delete(key)
            return result
        except Exception as e:
            logger.error(f"Failed to delete episode from Redis: {e}")
            return False

    async def cleanup_expired_episodes(
        self, workspace_id: str, max_age_days: int = 365
    ) -> int:
        """
        Clean up expired episodes.

        Args:
            workspace_id: Workspace ID
            max_age_days: Maximum age in days

        Returns:
            Number of episodes cleaned up
        """
        try:
            # Get all episode keys for workspace
            pattern = f"episodic:{workspace_id}:*"
            keys = await self.redis_client.keys(pattern)

            deleted_count = 0
            now = datetime.now()

            for key in keys:
                try:
                    data = await self.redis_client.get(key)
                    if data:
                        episode_data = json.loads(data)
                        episode_data = episode_data.get("episode")

                        if episode_data:
                            timestamp = datetime.fromisoformat(
                                episode_data.get("timestamp", "")
                            )
                            age = now - timestamp

                            if age.days > max_age_days:
                                key = (
                                    f"episodic:{workspace_id}:{episode_data.get('id')}"
                                )
                                await self.redis_client.delete(key)
                                deleted_count += 1

                except Exception as e:
                    logger.error(f"Error checking episode expiration: {e}")
                    continue

            return deleted_count

        except Exception as e:
            logger.error(f"Failed to cleanup expired episodes: {e}")
            return 0

    async def get_memory_stats(self, workspace_id: str) -> Dict[str, Any]:
        """
        Get statistics about episodic memory usage.

        Args:
            workspace_id: Workspace ID

        Returns:
            Dictionary with memory statistics
        """
        try:
            # Get all episode keys for workspace
            pattern = f"episodic:{workspace_id}:*"
            keys = await self.redis_client.keys(pattern)

            total_episodes = len(keys)
            recent_episodes = 0
            old_episodes = 0

            now = datetime.now()
            for key in keys:
                try:
                    data = await self.redis_client.get(key)
                    if data:
                        episode_data = json.loads(data)
                        episode_data = episode_data.get("episode")

                        if episode_data:
                            timestamp = datetime.fromisoformat(
                                episode_data.get("timestamp", "")
                            )
                            age = now - timestamp

                            if age.days < 7:
                                recent_episodes += 1
                            elif age.days > 30:
                                old_episodes += 1

                except Exception as e:
                    logger.error(f"Error checking episode age: {e}")
                    continue

            return {
                "total_episodes": total_episodes,
                "recent_episodes": recent_episodes,
                "old_episodes": old_episodes,
                "storage_type": "redis" if not self.supabase_client else "supabase",
            }

        except Exception as e:
            logger.error(f"Failed to get memory stats: {e}")
            return {
                "total_episodes": 0,
                "recent_episodes": 0,
                "old_episodes": 0,
                "storage_type": "unknown",
            }

    def __str__(self) -> str:
        """String representation."""
        storage_type = "Supabase" if self.supabase_client else "Redis"
        return f"EpisodicMemory(storage={storage_type})"


# Convenience functions
def get_episodic_memory(supabase_client=None, redis_client=None) -> EpisodicMemory:
    """Get episodic memory instance."""
    return EpisodicMemory(supabase_client, redis_client)


def create_episode(
    workspace_id: str,
    user_id: str,
    session_id: str,
    episode_type: str = "conversation",
    title: str = "",
    content: str = "",
    metadata: Optional[Dict[str, Any]] = None,
    importance: float = 1.0,
    tags: Optional[List[str]] = None,
) -> Episode:
    """Create a new episode."""
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
    return episode
