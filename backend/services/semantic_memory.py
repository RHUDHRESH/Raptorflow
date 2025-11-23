"""
Semantic Memory Service - Vector-based memory and context management.

Provides:
- Vector storage and retrieval for agent context
- Semantic search across past interactions
- Context persistence and retrieval
- ChromaDB integration with fallback to in-memory FAISS
"""

import structlog
from typing import List, Dict, Any, Optional
from datetime import datetime
import json
import numpy as np

logger = structlog.get_logger(__name__)


class SemanticMemoryService:
    """
    Semantic memory service using vector embeddings for context retrieval.

    Features:
    - Store and retrieve agent context with semantic search
    - Support for multiple workspace isolation
    - ChromaDB integration (optional)
    - In-memory FAISS fallback
    """

    def __init__(self, use_chromadb: bool = False):
        """
        Initialize semantic memory service.

        Args:
            use_chromadb: Whether to use ChromaDB (requires chromadb package)
        """
        self.use_chromadb = use_chromadb
        self.embeddings_cache: Dict[str, np.ndarray] = {}
        self.memory_store: Dict[str, List[Dict[str, Any]]] = {}

        if use_chromadb:
            try:
                import chromadb
                self.chroma_client = chromadb.Client()
                self.collection = self.chroma_client.get_or_create_collection(
                    name="agent_memory",
                    metadata={"description": "Agent context and memory"}
                )
                logger.info("ChromaDB initialized successfully")
            except ImportError:
                logger.warning("ChromaDB not installed, using in-memory fallback")
                self.use_chromadb = False

        logger.info(
            "Semantic memory service initialized",
            backend="chromadb" if self.use_chromadb else "in-memory"
        )

    async def store_context(
        self,
        workspace_id: str,
        context_type: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None
    ) -> str:
        """
        Store context with semantic embeddings.

        Args:
            workspace_id: Workspace identifier
            context_type: Type of context (icp, strategy, content, etc.)
            content: Content to store
            metadata: Additional metadata
            correlation_id: Correlation ID for tracking

        Returns:
            context_id: Unique identifier for stored context
        """
        try:
            context_id = f"{workspace_id}_{context_type}_{datetime.utcnow().timestamp()}"

            # Create embedding (mock for now - in production use sentence-transformers)
            embedding = await self._create_embedding(content)

            context_data = {
                "id": context_id,
                "workspace_id": workspace_id,
                "context_type": context_type,
                "content": content,
                "metadata": metadata or {},
                "timestamp": datetime.utcnow().isoformat(),
                "correlation_id": correlation_id
            }

            if self.use_chromadb:
                # Store in ChromaDB
                self.collection.add(
                    ids=[context_id],
                    embeddings=[embedding.tolist()],
                    documents=[content],
                    metadatas=[{
                        "workspace_id": workspace_id,
                        "context_type": context_type,
                        "timestamp": context_data["timestamp"],
                        "correlation_id": correlation_id or ""
                    }]
                )
            else:
                # Store in-memory
                if workspace_id not in self.memory_store:
                    self.memory_store[workspace_id] = []

                self.memory_store[workspace_id].append({
                    **context_data,
                    "embedding": embedding
                })

            logger.info(
                "Context stored",
                context_id=context_id,
                workspace_id=workspace_id,
                context_type=context_type,
                correlation_id=correlation_id
            )

            return context_id

        except Exception as e:
            logger.error(f"Failed to store context: {e}", correlation_id=correlation_id)
            raise

    async def retrieve_context(
        self,
        workspace_id: str,
        query: str,
        context_type: Optional[str] = None,
        limit: int = 5,
        correlation_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Retrieve relevant context using semantic search.

        Args:
            workspace_id: Workspace identifier
            query: Search query
            context_type: Filter by context type (optional)
            limit: Maximum number of results
            correlation_id: Correlation ID for tracking

        Returns:
            List of relevant context items with similarity scores
        """
        try:
            # Create query embedding
            query_embedding = await self._create_embedding(query)

            if self.use_chromadb:
                # Query ChromaDB
                results = self.collection.query(
                    query_embeddings=[query_embedding.tolist()],
                    n_results=limit,
                    where={
                        "workspace_id": workspace_id,
                        **({"context_type": context_type} if context_type else {})
                    }
                )

                contexts = []
                for i, doc_id in enumerate(results["ids"][0]):
                    contexts.append({
                        "id": doc_id,
                        "content": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i],
                        "similarity": 1 - results["distances"][0][i] if "distances" in results else 0.0
                    })

                return contexts
            else:
                # In-memory search
                workspace_contexts = self.memory_store.get(workspace_id, [])

                # Filter by context type if specified
                if context_type:
                    workspace_contexts = [
                        ctx for ctx in workspace_contexts
                        if ctx["context_type"] == context_type
                    ]

                # Calculate similarities
                results = []
                for ctx in workspace_contexts:
                    similarity = self._cosine_similarity(
                        query_embedding,
                        ctx["embedding"]
                    )
                    results.append({
                        "id": ctx["id"],
                        "content": ctx["content"],
                        "metadata": ctx["metadata"],
                        "context_type": ctx["context_type"],
                        "timestamp": ctx["timestamp"],
                        "similarity": similarity
                    })

                # Sort by similarity and limit
                results.sort(key=lambda x: x["similarity"], reverse=True)
                return results[:limit]

        except Exception as e:
            logger.error(
                f"Failed to retrieve context: {e}",
                workspace_id=workspace_id,
                correlation_id=correlation_id
            )
            return []

    async def get_workspace_context(
        self,
        workspace_id: str,
        context_type: Optional[str] = None,
        limit: int = 50,
        correlation_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get all context for a workspace (for debugging/admin purposes).

        Args:
            workspace_id: Workspace identifier
            context_type: Filter by context type (optional)
            limit: Maximum number of results
            correlation_id: Correlation ID for tracking

        Returns:
            List of context items
        """
        try:
            if self.use_chromadb:
                results = self.collection.get(
                    where={
                        "workspace_id": workspace_id,
                        **({"context_type": context_type} if context_type else {})
                    },
                    limit=limit
                )

                contexts = []
                for i, doc_id in enumerate(results["ids"]):
                    contexts.append({
                        "id": doc_id,
                        "content": results["documents"][i],
                        "metadata": results["metadatas"][i]
                    })

                return contexts
            else:
                workspace_contexts = self.memory_store.get(workspace_id, [])

                if context_type:
                    workspace_contexts = [
                        ctx for ctx in workspace_contexts
                        if ctx["context_type"] == context_type
                    ]

                # Remove embeddings from response
                return [
                    {k: v for k, v in ctx.items() if k != "embedding"}
                    for ctx in workspace_contexts[:limit]
                ]

        except Exception as e:
            logger.error(
                f"Failed to get workspace context: {e}",
                workspace_id=workspace_id,
                correlation_id=correlation_id
            )
            return []

    async def _create_embedding(self, text: str) -> np.ndarray:
        """
        Create embedding for text.

        In production, this should use sentence-transformers or OpenAI embeddings.
        For now, uses a simple hash-based mock embedding.

        Args:
            text: Text to embed

        Returns:
            Embedding vector (384 dimensions)
        """
        # Mock embedding - in production use:
        # from sentence_transformers import SentenceTransformer
        # model = SentenceTransformer('all-MiniLM-L6-v2')
        # return model.encode(text)

        # Simple deterministic mock based on text hash
        np.random.seed(hash(text) % (2**32))
        embedding = np.random.randn(384).astype(np.float32)
        embedding = embedding / np.linalg.norm(embedding)  # Normalize
        return embedding

    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors."""
        return float(np.dot(vec1, vec2) / (np.linalg.norm(vec1) * np.linalg.norm(vec2)))

    async def delete_workspace_context(
        self,
        workspace_id: str,
        correlation_id: Optional[str] = None
    ) -> int:
        """
        Delete all context for a workspace.

        Args:
            workspace_id: Workspace identifier
            correlation_id: Correlation ID for tracking

        Returns:
            Number of items deleted
        """
        try:
            if self.use_chromadb:
                # ChromaDB doesn't support bulk delete by metadata easily
                # Would need to get all IDs first, then delete
                logger.warning("ChromaDB bulk delete not implemented")
                return 0
            else:
                count = len(self.memory_store.get(workspace_id, []))
                if workspace_id in self.memory_store:
                    del self.memory_store[workspace_id]

                logger.info(
                    "Workspace context deleted",
                    workspace_id=workspace_id,
                    count=count,
                    correlation_id=correlation_id
                )
                return count

        except Exception as e:
            logger.error(
                f"Failed to delete workspace context: {e}",
                workspace_id=workspace_id,
                correlation_id=correlation_id
            )
            return 0


# Global semantic memory instance
semantic_memory = SemanticMemoryService(use_chromadb=False)
