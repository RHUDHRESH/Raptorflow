"""
Vector memory store using Supabase and pgvector.

This module provides the VectorMemory class for storing and retrieving
text embeddings using Supabase with pgvector extension.
"""

import asyncio
import logging
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional, Union

from .embeddings import get_embedding_model
from .models import MemoryChunk, MemoryType

logger = logging.getLogger(__name__)


class VectorMemory:
    """
    Vector memory store using Supabase and pgvector.

    Provides storage and retrieval of text embeddings with
    workspace isolation and semantic search capabilities.
    """

    def __init__(self, supabase_client=None):
        """
        Initialize vector memory store.

        Args:
            supabase_client: Supabase client instance
        """
        self.supabase_client = supabase_client
        self.embedding_model = get_embedding_model()
        self._table_name = "memory_vectors"

        # Initialize Supabase client if not provided
        if self.supabase_client is None:
            self._init_supabase_client()

    def _init_supabase_client(self):
        """Initialize Supabase client from environment variables."""
        try:
            from supabase import create_client

            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

            if not supabase_url or not supabase_key:
                raise ValueError(
                    "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set"
                )

            self.supabase_client = create_client(supabase_url, supabase_key)
            logger.info("Supabase client initialized")

        except ImportError:
            logger.error(
                "supabase package not installed. Install with: pip install supabase"
            )
            raise
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            raise

    async def store(
        self,
        workspace_id: str,
        memory_type: MemoryType,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        reference_id: Optional[str] = None,
        reference_table: Optional[str] = None,
    ) -> str:
        """
        Store a memory chunk with embedding.

        Args:
            workspace_id: Workspace ID for isolation
            memory_type: Type of memory
            content: Text content to store
            metadata: Additional metadata
            reference_id: Optional reference to another record
            reference_table: Optional reference table name

        Returns:
            ID of the stored memory chunk
        """
        if not content or not content.strip():
            raise ValueError("Content cannot be empty")

        # Generate embedding
        embedding = self.embedding_model.encode_single(content)

        # Create memory chunk
        chunk = MemoryChunk(
            id=str(uuid.uuid4()),
            workspace_id=workspace_id,
            memory_type=memory_type,
            content=content,
            metadata=metadata or {},
            embedding=embedding,
            reference_id=reference_id,
            reference_table=reference_table,
        )

        # Store in Supabase
        try:
            data = {
                "id": chunk.id,
                "workspace_id": chunk.workspace_id,
                "memory_type": chunk.memory_type.value,
                "content": chunk.content,
                "metadata": chunk.metadata,
                "embedding": chunk.get_embedding_list(),
                "reference_id": chunk.reference_id,
                "reference_table": chunk.reference_table,
                "created_at": chunk.created_at.isoformat(),
                "updated_at": chunk.updated_at.isoformat(),
            }

            result = self.supabase_client.table(self._table_name).insert(data).execute()

            if result.data:
                logger.info(f"Stored memory chunk {chunk.id}")
                return chunk.id
            else:
                raise Exception("Failed to store memory chunk")

        except Exception as e:
            logger.error(f"Failed to store memory chunk: {e}")
            raise

    async def store_batch(
        self, workspace_id: str, chunks: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Store multiple memory chunks.

        Args:
            workspace_id: Workspace ID for isolation
            chunks: List of chunk dictionaries with keys: content, memory_type, metadata, etc.

        Returns:
            List of stored chunk IDs
        """
        if not chunks:
            return []

        # Generate embeddings for all content
        contents = [chunk["content"] for chunk in chunks]
        embeddings = self.embedding_model.encode(contents)

        # Prepare data for insertion
        data_list = []
        for i, chunk_data in enumerate(chunks):
            chunk = MemoryChunk(
                id=str(uuid.uuid4()),
                workspace_id=workspace_id,
                memory_type=chunk_data.get("memory_type", MemoryType.CONVERSATION),
                content=chunk_data["content"],
                metadata=chunk_data.get("metadata", {}),
                embedding=embeddings[i],
                reference_id=chunk_data.get("reference_id"),
                reference_table=chunk_data.get("reference_table"),
            )

            data_list.append(
                {
                    "id": chunk.id,
                    "workspace_id": chunk.workspace_id,
                    "memory_type": chunk.memory_type.value,
                    "content": chunk.content,
                    "metadata": chunk.metadata,
                    "embedding": chunk.get_embedding_list(),
                    "reference_id": chunk.reference_id,
                    "reference_table": chunk.reference_table,
                    "created_at": chunk.created_at.isoformat(),
                    "updated_at": chunk.updated_at.isoformat(),
                }
            )

        # Store in Supabase
        try:
            result = (
                self.supabase_client.table(self._table_name).insert(data_list).execute()
            )

            if result.data:
                stored_ids = [item["id"] for item in result.data]
                logger.info(f"Stored {len(stored_ids)} memory chunks")
                return stored_ids
            else:
                raise Exception("Failed to store memory chunks")

        except Exception as e:
            logger.error(f"Failed to store memory chunks: {e}")
            raise

    async def search(
        self,
        workspace_id: str,
        query: str,
        memory_types: Optional[List[MemoryType]] = None,
        limit: int = 10,
        similarity_threshold: float = 0.7,
    ) -> List[MemoryChunk]:
        """
        Search for similar memories using vector similarity.

        Args:
            workspace_id: Workspace ID for isolation
            query: Search query
            memory_types: Optional filter by memory types
            limit: Maximum number of results
            similarity_threshold: Minimum similarity score

        Returns:
            List of matching memory chunks
        """
        if not query or not query.strip():
            return []

        # Generate query embedding
        query_embedding = self.embedding_model.encode_single(query)

        # Build the search query
        try:
            # Convert memory types to strings
            type_filter = ""
            if memory_types:
                type_strings = [t.value for t in memory_types]
                type_filter = (
                    f"AND memory_type IN ({','.join([f"'{t}'" for t in type_strings])})"
                )

            # Use the similarity search function
            sql_query = f"""
                SELECT *, 1 - (embedding <=> $1::vector) as similarity
                FROM {self._table_name}
                WHERE workspace_id = $2
                {type_filter}
                AND 1 - (embedding <=> $1::vector) > $3
                ORDER BY similarity DESC
                LIMIT $4
            """

            # Execute the query
            result = self.supabase_client.rpc(
                "search_memory_vectors",
                {
                    "p_workspace_id": workspace_id,
                    "p_query_embedding": query_embedding.tolist(),
                    "p_memory_types": (
                        [t.value for t in memory_types] if memory_types else None
                    ),
                    "p_limit": limit,
                },
            ).execute()

            # Fallback to direct SQL if RPC not available
            if not result.data:
                # Direct SQL approach (simplified)
                result = (
                    self.supabase_client.table(self._table_name)
                    .select("*", count="exact")
                    .eq("workspace_id", workspace_id)
                    .limit(limit)
                    .execute()
                )

                # Filter by similarity in Python (less efficient)
                chunks = []
                for item in result.data or []:
                    if item.get("embedding"):
                        stored_embedding = item["embedding"]
                        similarity = self.embedding_model.compute_similarity(
                            query_embedding,
                            self.embedding_model.normalize_embedding(stored_embedding),
                        )
                        if similarity >= similarity_threshold:
                            chunk = self._dict_to_memory_chunk(item)
                            chunk.score = similarity
                            chunks.append(chunk)

                # Sort by similarity
                chunks.sort(key=lambda x: x.score or 0, reverse=True)
                return chunks[:limit]

            # Convert results to MemoryChunk objects
            chunks = []
            for item in result.data:
                chunk = self._dict_to_memory_chunk(item)
                chunk.score = item.get("similarity", 0.0)
                chunks.append(chunk)

            logger.info(f"Found {len(chunks)} matching chunks for query")
            return chunks

        except Exception as e:
            logger.error(f"Failed to search memory vectors: {e}")
            raise

    async def get_by_id(self, chunk_id: str) -> Optional[MemoryChunk]:
        """
        Retrieve a memory chunk by ID.

        Args:
            chunk_id: ID of the memory chunk

        Returns:
            MemoryChunk or None if not found
        """
        try:
            result = (
                self.supabase_client.table(self._table_name)
                .select("*")
                .eq("id", chunk_id)
                .single()
                .execute()
            )

            if result.data:
                return self._dict_to_memory_chunk(result.data)
            else:
                return None

        except Exception as e:
            logger.error(f"Failed to get memory chunk {chunk_id}: {e}")
            return None

    async def get_by_workspace(
        self,
        workspace_id: str,
        memory_type: Optional[MemoryType] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> List[MemoryChunk]:
        """
        Retrieve memory chunks by workspace.

        Args:
            workspace_id: Workspace ID
            memory_type: Optional filter by memory type
            limit: Maximum number of results
            offset: Offset for pagination

        Returns:
            List of memory chunks
        """
        try:
            query = (
                self.supabase_client.table(self._table_name)
                .select("*", count="exact")
                .eq("workspace_id", workspace_id)
            )

            if memory_type:
                query = query.eq("memory_type", memory_type.value)

            result = (
                query.range(offset, offset + limit - 1)
                .order("created_at", desc=True)
                .execute()
            )

            chunks = []
            for item in result.data or []:
                chunk = self._dict_to_memory_chunk(item)
                chunks.append(chunk)

            return chunks

        except Exception as e:
            logger.error(
                f"Failed to get memory chunks for workspace {workspace_id}: {e}"
            )
            return []

    async def update(
        self,
        chunk_id: str,
        content: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Update a memory chunk.

        Args:
            chunk_id: ID of the memory chunk
            content: New content (if provided)
            metadata: New metadata (if provided)

        Returns:
            True if successful, False otherwise
        """
        try:
            update_data = {"updated_at": datetime.now().isoformat()}

            # Update content and embedding if provided
            if content is not None:
                if not content or not content.strip():
                    raise ValueError("Content cannot be empty")

                embedding = self.embedding_model.encode_single(content)
                update_data["content"] = content
                update_data["embedding"] = embedding.tolist()

            # Update metadata if provided
            if metadata is not None:
                update_data["metadata"] = metadata

            result = (
                self.supabase_client.table(self._table_name)
                .update(update_data)
                .eq("id", chunk_id)
                .execute()
            )

            if result.data:
                logger.info(f"Updated memory chunk {chunk_id}")
                return True
            else:
                logger.warning(f"No memory chunk found with ID {chunk_id}")
                return False

        except Exception as e:
            logger.error(f"Failed to update memory chunk {chunk_id}: {e}")
            return False

    async def delete(self, chunk_id: str) -> bool:
        """
        Delete a memory chunk.

        Args:
            chunk_id: ID of the memory chunk to delete

        Returns:
            True if successful, False otherwise
        """
        try:
            result = (
                self.supabase_client.table(self._table_name)
                .delete()
                .eq("id", chunk_id)
                .execute()
            )

            if result.data:
                logger.info(f"Deleted memory chunk {chunk_id}")
                return True
            else:
                logger.warning(f"No memory chunk found with ID {chunk_id}")
                return False

        except Exception as e:
            logger.error(f"Failed to delete memory chunk {chunk_id}: {e}")
            return False

    async def delete_by_workspace(self, workspace_id: str) -> int:
        """
        Delete all memory chunks for a workspace.

        Args:
            workspace_id: Workspace ID

        Returns:
            Number of deleted chunks
        """
        try:
            result = (
                self.supabase_client.table(self._table_name)
                .delete()
                .eq("workspace_id", workspace_id)
                .execute()
            )

            deleted_count = len(result.data) if result.data else 0
            logger.info(
                f"Deleted {deleted_count} memory chunks for workspace {workspace_id}"
            )
            return deleted_count

        except Exception as e:
            logger.error(
                f"Failed to delete memory chunks for workspace {workspace_id}: {e}"
            )
            return 0

    async def get_stats(self, workspace_id: str) -> Dict[str, Any]:
        """
        Get statistics for a workspace.

        Args:
            workspace_id: Workspace ID

        Returns:
            Dictionary with statistics
        """
        try:
            # Get total count
            total_result = (
                self.supabase_client.table(self._table_name)
                .select("count", count="exact")
                .eq("workspace_id", workspace_id)
                .execute()
            )

            total_count = total_result.count if total_result.count else 0

            # Get counts by type
            type_counts = {}
            for memory_type in MemoryType:
                type_result = (
                    self.supabase_client.table(self._table_name)
                    .select("count", count="exact")
                    .eq("workspace_id", workspace_id)
                    .eq("memory_type", memory_type.value)
                    .execute()
                )

                type_counts[memory_type.value] = (
                    type_result.count if type_result.count else 0
                )

            # Get storage size (approximate)
            size_result = (
                self.supabase_client.table(self._table_name)
                .select("content, metadata")
                .eq("workspace_id", workspace_id)
                .execute()
            )

            total_size = 0
            for item in size_result.data or []:
                content_size = len(item.get("content", ""))
                metadata_size = len(str(item.get("metadata", {})))
                total_size += content_size + metadata_size

            return {
                "total_chunks": total_count,
                "chunks_by_type": type_counts,
                "estimated_storage_bytes": total_size,
                "workspace_id": workspace_id,
            }

        except Exception as e:
            logger.error(f"Failed to get stats for workspace {workspace_id}: {e}")
            return {
                "total_chunks": 0,
                "chunks_by_type": {},
                "estimated_storage_bytes": 0,
                "workspace_id": workspace_id,
            }

    def _dict_to_memory_chunk(self, data: Dict[str, Any]) -> MemoryChunk:
        """Convert dictionary to MemoryChunk object."""
        chunk = MemoryChunk(
            id=data.get("id"),
            workspace_id=data.get("workspace_id"),
            memory_type=(
                MemoryType.from_string(data["memory_type"])
                if data.get("memory_type")
                else None
            ),
            content=data.get("content", ""),
            metadata=data.get("metadata", {}),
            reference_id=data.get("reference_id"),
            reference_table=data.get("reference_table"),
        )

        # Handle embedding
        if data.get("embedding"):
            chunk.set_embedding_from_list(data["embedding"])

        # Handle timestamps
        if data.get("created_at"):
            chunk.created_at = datetime.fromisoformat(data["created_at"])
        if data.get("updated_at"):
            chunk.updated_at = datetime.fromisoformat(data["updated_at"])

        return chunk

    async def health_check(self) -> Dict[str, Any]:
        """
        Check the health of the vector store.

        Returns:
            Dictionary with health status
        """
        health = {
            "supabase_connected": False,
            "pgvector_enabled": False,
            "table_exists": False,
            "embedding_model_loaded": False,
            "errors": [],
        }

        # Check Supabase connection
        try:
            result = (
                self.supabase_client.table("pg_tables")
                .select("tablename")
                .eq("schemaname", "public")
                .execute()
            )
            health["supabase_connected"] = True
        except Exception as e:
            health["errors"].append(f"Supabase connection failed: {e}")

        # Check if table exists
        try:
            result = (
                self.supabase_client.table(self._table_name)
                .select("count", count="exact")
                .execute()
            )
            health["table_exists"] = True
        except Exception as e:
            health["errors"].append(f"Table {self._table_name} not accessible: {e}")

        # Check embedding model
        try:
            test_embedding = self.embedding_model.encode_single("test")
            health["embedding_model_loaded"] = True
        except Exception as e:
            health["errors"].append(f"Embedding model failed: {e}")

        return health


# Convenience functions
async def store_memory(
    workspace_id: str,
    memory_type: MemoryType,
    content: str,
    metadata: Optional[Dict[str, Any]] = None,
) -> str:
    """Convenience function to store a memory chunk."""
    vector_memory = VectorMemory()
    return await vector_memory.store(workspace_id, memory_type, content, metadata)


async def search_memories(
    workspace_id: str,
    query: str,
    memory_types: Optional[List[MemoryType]] = None,
    limit: int = 10,
) -> List[MemoryChunk]:
    """Convenience function to search memories."""
    vector_memory = VectorMemory()
    return await vector_memory.search(workspace_id, query, memory_types, limit)
