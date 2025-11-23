"""
Semantic Memory - Vector-Based Semantic Search

This module implements semantic memory using ChromaDB for vector storage and
similarity search. Semantic memory enables finding content based on meaning
rather than exact keyword matches.

Purpose:
--------
- Store vector embeddings of all generated content
- Enable semantic search across campaigns, content, personas
- Find similar or related content automatically
- Support RAG (Retrieval Augmented Generation) patterns
- Cluster content by semantic similarity

Schema:
-------
Collection Structure (ChromaDB):
- collection_name: "{workspace_id}_semantic"
- documents: Original text content
- embeddings: Vector representations (384 or 768 dimensions)
- metadata: Dict containing:
  - content_type: str (campaign, content, icp, message, etc.)
  - created_at: str (ISO 8601 timestamp)
  - workspace_id: str (UUID)
  - source_id: str (reference to original record)
  - tags: List[str] (optional tags)
  - custom fields: Any additional metadata

Storage Backend: ChromaDB
- Local vector database for fast similarity search
- Built-in persistence to disk
- Cosine similarity by default
- Support for metadata filtering
- No external dependencies or API keys required

Alternative: Supabase pgvector
- If VECTOR_STORE=supabase in settings, use PostgreSQL pgvector
- Integrated with existing Supabase database
- Better for production/cloud deployments

Dependencies:
-------------
- chromadb: For vector database operations
- memory.embeddings: For generating embeddings
- uuid: For workspace and document IDs

Usage Example:
--------------
from memory.semantic_memory import SemanticMemory
from uuid import UUID

# Initialize semantic memory
semantic = SemanticMemory()

# Store content with automatic embedding
await semantic.remember(
    key="campaign_123",
    value="Launch campaign targeting tech-savvy millennials with AI focus",
    workspace_id=UUID("..."),
    metadata={
        "content_type": "campaign",
        "campaign_id": "campaign_123",
        "tags": ["AI", "millennials"]
    }
)

# Semantic search
results = await semantic.search(
    query="artificial intelligence marketing for young professionals",
    workspace_id=UUID("..."),
    top_k=5
)
# Returns similar campaigns/content based on meaning

# Search with filters
results = await semantic.search(
    query="social media strategy",
    workspace_id=UUID("..."),
    filters={"content_type": "campaign"},
    top_k=10
)
"""

import json
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4
from datetime import datetime
import structlog

try:
    import chromadb
    from chromadb.config import Settings
    CHROMADB_AVAILABLE = True
except ImportError:
    chromadb = None
    Settings = None
    CHROMADB_AVAILABLE = False

from memory.base import BaseMemory, MemoryError
from memory.embeddings import get_embedder

logger = structlog.get_logger()


class SemanticMemory(BaseMemory):
    """
    ChromaDB-based semantic memory for vector search.

    This class provides semantic search capabilities using embeddings
    and vector similarity. It stores all content with embeddings and
    enables finding semantically similar items.

    Attributes:
        chroma_client: ChromaDB client instance
        embedder: Embedding generator instance
        persist_directory: Directory for ChromaDB persistence
    """

    def __init__(
        self,
        persist_directory: str = "./data/chroma",
        embedding_model: str = "all-MiniLM-L6-v2"
    ):
        """
        Initialize semantic memory with ChromaDB.

        Args:
            persist_directory: Directory to persist ChromaDB data
            embedding_model: Model to use for generating embeddings

        Raises:
            ImportError: If ChromaDB is not installed
        """
        if not CHROMADB_AVAILABLE:
            raise ImportError(
                "chromadb not installed. "
                "Install with: pip install chromadb"
            )

        super().__init__(memory_type="semantic")
        self.persist_directory = persist_directory
        self.embedding_model = embedding_model
        self.chroma_client: Optional[chromadb.Client] = None
        self.embedder = get_embedder(model_name=embedding_model)

    def _get_client(self) -> chromadb.Client:
        """
        Get or create ChromaDB client.

        Returns:
            ChromaDB client instance

        Raises:
            MemoryError: If client creation fails
        """
        if self.chroma_client is None:
            try:
                self.chroma_client = chromadb.PersistentClient(
                    path=self.persist_directory,
                    settings=Settings(
                        anonymized_telemetry=False,
                        allow_reset=False
                    )
                )
                self.logger.info(
                    "ChromaDB client initialized",
                    persist_dir=self.persist_directory
                )
            except Exception as e:
                self.logger.error(
                    "Failed to initialize ChromaDB client",
                    error=str(e)
                )
                raise MemoryError(
                    f"Failed to initialize ChromaDB: {str(e)}",
                    memory_type=self.memory_type,
                    operation="connect"
                )

        return self.chroma_client

    def _get_collection_name(self, workspace_id: UUID) -> str:
        """
        Generate collection name for workspace.

        Args:
            workspace_id: Workspace UUID

        Returns:
            Collection name string
        """
        # ChromaDB collection names must start with letter/number, no hyphens
        workspace_str = str(workspace_id).replace("-", "")
        return f"ws_{workspace_str}_semantic"

    def _get_or_create_collection(self, workspace_id: UUID):
        """
        Get or create a ChromaDB collection for workspace.

        Args:
            workspace_id: Workspace UUID

        Returns:
            ChromaDB collection instance
        """
        client = self._get_client()
        collection_name = self._get_collection_name(workspace_id)

        try:
            collection = client.get_or_create_collection(
                name=collection_name,
                metadata={"workspace_id": str(workspace_id)}
            )
            return collection
        except Exception as e:
            self.logger.error(
                "Failed to get/create collection",
                collection_name=collection_name,
                error=str(e)
            )
            raise MemoryError(
                f"Failed to get/create collection: {str(e)}",
                memory_type=self.memory_type,
                operation="get_collection"
            )

    async def remember(
        self,
        key: str,
        value: Any,
        workspace_id: UUID,
        metadata: Optional[Dict[str, Any]] = None,
        ttl: Optional[int] = None
    ) -> None:
        """
        Store content with semantic embedding.

        Generates embedding for the content and stores it in the vector database.

        Args:
            key: Unique identifier for the content (e.g., campaign_id, content_id)
            value: Content to store (string or dict with 'text' field)
            workspace_id: Workspace UUID
            metadata: Optional metadata (content_type, tags, etc.)
            ttl: Not used for semantic memory (persistent storage)

        Raises:
            MemoryError: If storage operation fails
        """
        self._validate_workspace_id(workspace_id)

        try:
            collection = self._get_or_create_collection(workspace_id)

            # Extract text content
            if isinstance(value, str):
                text = value
            elif isinstance(value, dict) and "text" in value:
                text = value["text"]
            elif isinstance(value, dict) and "content" in value:
                text = value["content"]
            else:
                text = str(value)

            if not text or not text.strip():
                raise ValueError("Cannot store empty text in semantic memory")

            # Generate embedding
            embedding = await self.embedder.embed(text)

            # Prepare metadata
            meta = metadata.copy() if metadata else {}
            meta["workspace_id"] = str(workspace_id)
            meta["created_at"] = datetime.utcnow().isoformat()
            meta["key"] = key

            # Store in ChromaDB
            collection.add(
                ids=[key],
                embeddings=[embedding],
                documents=[text],
                metadatas=[meta]
            )

            self.logger.debug(
                "Stored semantic memory",
                key=key,
                workspace_id=str(workspace_id),
                text_length=len(text)
            )

        except Exception as e:
            self.logger.error(
                "Failed to store semantic memory",
                key=key,
                workspace_id=str(workspace_id),
                error=str(e)
            )
            raise MemoryError(
                f"Failed to store semantic memory: {str(e)}",
                memory_type=self.memory_type,
                operation="remember"
            )

    async def recall(
        self,
        key: str,
        workspace_id: UUID,
        default: Any = None
    ) -> Optional[Dict[str, Any]]:
        """
        Retrieve specific content by key.

        Args:
            key: Content identifier
            workspace_id: Workspace UUID
            default: Default value if not found

        Returns:
            Dictionary with 'text' and 'metadata' fields, or default

        Raises:
            MemoryError: If retrieval fails
        """
        self._validate_workspace_id(workspace_id)

        try:
            collection = self._get_or_create_collection(workspace_id)

            # Get by ID
            result = collection.get(
                ids=[key],
                include=["documents", "metadatas", "embeddings"]
            )

            if not result["ids"]:
                self.logger.debug(
                    "No semantic memory found, returning default",
                    key=key,
                    workspace_id=str(workspace_id)
                )
                return default

            # Return document with metadata
            return {
                "text": result["documents"][0],
                "metadata": result["metadatas"][0],
                "embedding": result["embeddings"][0] if result["embeddings"] else None
            }

        except Exception as e:
            self.logger.error(
                "Failed to recall semantic memory",
                key=key,
                workspace_id=str(workspace_id),
                error=str(e)
            )
            raise MemoryError(
                f"Failed to recall semantic memory: {str(e)}",
                memory_type=self.memory_type,
                operation="recall"
            )

    async def search(
        self,
        query: str,
        workspace_id: UUID,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search based on query meaning.

        Generates embedding for query and finds most similar content.

        Args:
            query: Search query text
            workspace_id: Workspace UUID
            top_k: Maximum results to return
            filters: Optional metadata filters (e.g., {"content_type": "campaign"})

        Returns:
            List of matching documents with scores and metadata

        Raises:
            MemoryError: If search fails
        """
        self._validate_workspace_id(workspace_id)

        try:
            collection = self._get_or_create_collection(workspace_id)

            # Generate query embedding
            query_embedding = await self.embedder.embed(query)

            # Build where clause for filters
            where = None
            if filters:
                # Convert filters to ChromaDB where clause
                where = {}
                for key, value in filters.items():
                    if isinstance(value, list):
                        where[key] = {"$in": value}
                    else:
                        where[key] = value

            # Perform similarity search
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=top_k,
                where=where,
                include=["documents", "metadatas", "distances"]
            )

            # Format results
            formatted_results = []
            if results["ids"] and results["ids"][0]:
                for i in range(len(results["ids"][0])):
                    formatted_results.append({
                        "id": results["ids"][0][i],
                        "text": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "similarity": 1 - results["distances"][0][i],  # Convert distance to similarity
                        "distance": results["distances"][0][i]
                    })

            self.logger.debug(
                "Semantic search completed",
                query=query,
                workspace_id=str(workspace_id),
                results_count=len(formatted_results)
            )

            return formatted_results

        except Exception as e:
            self.logger.error(
                "Failed to perform semantic search",
                query=query,
                workspace_id=str(workspace_id),
                error=str(e)
            )
            raise MemoryError(
                f"Failed to perform semantic search: {str(e)}",
                memory_type=self.memory_type,
                operation="search"
            )

    async def forget(
        self,
        key: str,
        workspace_id: UUID
    ) -> bool:
        """
        Delete content from semantic memory.

        Args:
            key: Content identifier to delete
            workspace_id: Workspace UUID

        Returns:
            True if deletion was successful

        Raises:
            MemoryError: If deletion fails
        """
        self._validate_workspace_id(workspace_id)

        try:
            collection = self._get_or_create_collection(workspace_id)

            # Delete by ID
            collection.delete(ids=[key])

            self.logger.debug(
                "Semantic memory deleted",
                key=key,
                workspace_id=str(workspace_id)
            )

            return True

        except Exception as e:
            self.logger.error(
                "Failed to delete semantic memory",
                key=key,
                workspace_id=str(workspace_id),
                error=str(e)
            )
            raise MemoryError(
                f"Failed to delete semantic memory: {str(e)}",
                memory_type=self.memory_type,
                operation="forget"
            )

    async def learn_from_feedback(
        self,
        key: str,
        feedback: Dict[str, Any],
        workspace_id: UUID
    ) -> None:
        """
        Update semantic memory based on feedback.

        For semantic memory, this can be used to boost or demote
        specific content based on user feedback.

        Args:
            key: Content identifier
            feedback: Feedback data (rating, relevance, etc.)
            workspace_id: Workspace UUID

        Raises:
            MemoryError: If update fails
        """
        self._validate_workspace_id(workspace_id)

        try:
            # Get existing item
            existing = await self.recall(key, workspace_id)

            if not existing:
                self.logger.warning(
                    "Cannot learn from feedback: item not found",
                    key=key,
                    workspace_id=str(workspace_id)
                )
                return

            # Update metadata with feedback
            metadata = existing.get("metadata", {})
            if "feedback_history" not in metadata:
                metadata["feedback_history"] = []

            feedback_item = feedback.copy()
            feedback_item["timestamp"] = datetime.utcnow().isoformat()
            metadata["feedback_history"].append(feedback_item)

            # Keep only recent feedback (last 10 items)
            if len(metadata["feedback_history"]) > 10:
                metadata["feedback_history"] = metadata["feedback_history"][-10:]

            # Calculate average rating if provided
            if "rating" in feedback:
                ratings = [f.get("rating", 0) for f in metadata["feedback_history"] if "rating" in f]
                if ratings:
                    metadata["avg_rating"] = sum(ratings) / len(ratings)

            # Update in ChromaDB (delete and re-add with new metadata)
            collection = self._get_or_create_collection(workspace_id)
            collection.update(
                ids=[key],
                metadatas=[metadata]
            )

            self.logger.info(
                "Semantic memory learned from feedback",
                key=key,
                workspace_id=str(workspace_id)
            )

        except Exception as e:
            self.logger.error(
                "Failed to learn from feedback",
                key=key,
                workspace_id=str(workspace_id),
                error=str(e)
            )
            raise MemoryError(
                f"Failed to learn from feedback: {str(e)}",
                memory_type=self.memory_type,
                operation="learn_from_feedback"
            )

    async def clear(self, workspace_id: UUID) -> bool:
        """
        Clear all semantic memory for a workspace.

        Args:
            workspace_id: Workspace UUID

        Returns:
            True if successful

        Raises:
            MemoryError: If clear operation fails
        """
        self._validate_workspace_id(workspace_id)

        try:
            client = self._get_client()
            collection_name = self._get_collection_name(workspace_id)

            # Delete the entire collection
            try:
                client.delete_collection(name=collection_name)
                self.logger.info(
                    "Cleared semantic memory collection",
                    workspace_id=str(workspace_id),
                    collection_name=collection_name
                )
            except Exception:
                # Collection might not exist, which is fine
                pass

            return True

        except Exception as e:
            self.logger.error(
                "Failed to clear semantic memory",
                workspace_id=str(workspace_id),
                error=str(e)
            )
            raise MemoryError(
                f"Failed to clear semantic memory: {str(e)}",
                memory_type=self.memory_type,
                operation="clear"
            )

    async def get_similar(
        self,
        key: str,
        workspace_id: UUID,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """
        Find content similar to a specific item.

        Args:
            key: Content identifier to find similar items for
            workspace_id: Workspace UUID
            top_k: Maximum results to return
            filters: Optional metadata filters

        Returns:
            List of similar items (excluding the query item itself)

        Raises:
            MemoryError: If operation fails
        """
        self._validate_workspace_id(workspace_id)

        try:
            # Get the item
            item = await self.recall(key, workspace_id)

            if not item:
                self.logger.warning(
                    "Cannot find similar items: source item not found",
                    key=key,
                    workspace_id=str(workspace_id)
                )
                return []

            # Use the item's text as search query
            results = await self.search(
                query=item["text"],
                workspace_id=workspace_id,
                top_k=top_k + 1,  # +1 to account for the source item itself
                filters=filters
            )

            # Filter out the source item
            similar_items = [r for r in results if r["id"] != key]

            return similar_items[:top_k]

        except Exception as e:
            self.logger.error(
                "Failed to find similar items",
                key=key,
                workspace_id=str(workspace_id),
                error=str(e)
            )
            raise MemoryError(
                f"Failed to find similar items: {str(e)}",
                memory_type=self.memory_type,
                operation="get_similar"
            )
