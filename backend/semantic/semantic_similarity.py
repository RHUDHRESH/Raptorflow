"""
Semantic Similarity - Computes similarity between content using embeddings

This module provides semantic similarity capabilities including:
- Text embedding generation
- Cosine similarity computation
- Content deduplication detection
- Similar content retrieval
- Semantic search functionality
"""

import json
import numpy as np
from typing import Any, Dict, List, Optional, Tuple
import structlog

from backend.services.openai_client import openai_client
from backend.utils.cache import redis_cache
from backend.utils.correlation import get_correlation_id

logger = structlog.get_logger(__name__)


class SemanticSimilarity:
    """
    Computes semantic similarity between texts using embeddings.

    Capabilities:
    - Generate embeddings for text content
    - Calculate cosine similarity between texts
    - Find similar content from workspace history
    - Detect duplicate or near-duplicate content
    - Enable semantic search across content
    """

    def __init__(self):
        self.embedding_model = "text-embedding-3-small"  # OpenAI's latest embedding model
        self.embedding_dimensions = 1536  # Default dimensions
        self.cache_ttl = 86400 * 7  # 7 days for embeddings
        self.similarity_threshold = 0.85  # Threshold for considering content similar

    async def get_embedding(
        self,
        text: str,
        correlation_id: Optional[str] = None
    ) -> List[float]:
        """
        Generate embedding vector for text.

        Args:
            text: Text to embed
            correlation_id: Request correlation ID

        Returns:
            List of floats representing the embedding vector
        """
        correlation_id = correlation_id or get_correlation_id()

        # Check cache first
        cache_key = self._generate_embedding_cache_key(text)
        cached_embedding = await redis_cache.get(cache_key)

        if cached_embedding:
            logger.debug(
                "Returning cached embedding",
                text_length=len(text),
                correlation_id=correlation_id
            )
            return cached_embedding

        try:
            logger.info(
                "Generating embedding",
                text_length=len(text),
                correlation_id=correlation_id
            )

            # Generate embedding using OpenAI
            response = await openai_client.client.embeddings.create(
                model=self.embedding_model,
                input=text[:8000]  # Limit to 8000 characters for embedding
            )

            embedding = response.data[0].embedding

            # Cache the embedding
            await redis_cache.set(cache_key, embedding, ttl=self.cache_ttl)

            logger.debug(
                "Embedding generated",
                dimensions=len(embedding),
                correlation_id=correlation_id
            )

            return embedding

        except Exception as e:
            logger.error(
                "Embedding generation failed",
                error=str(e),
                correlation_id=correlation_id,
                exc_info=True
            )
            raise

    async def compute_similarity(
        self,
        text1: str,
        text2: str,
        correlation_id: Optional[str] = None
    ) -> float:
        """
        Compute cosine similarity between two texts.

        Args:
            text1: First text
            text2: Second text
            correlation_id: Request correlation ID

        Returns:
            Similarity score between 0.0 and 1.0
        """
        correlation_id = correlation_id or get_correlation_id()

        logger.info(
            "Computing similarity",
            text1_length=len(text1),
            text2_length=len(text2),
            correlation_id=correlation_id
        )

        # Get embeddings for both texts
        import asyncio
        embedding1, embedding2 = await asyncio.gather(
            self.get_embedding(text1, correlation_id),
            self.get_embedding(text2, correlation_id)
        )

        # Compute cosine similarity
        similarity = self._cosine_similarity(embedding1, embedding2)

        logger.info(
            "Similarity computed",
            similarity=similarity,
            correlation_id=correlation_id
        )

        return similarity

    async def find_similar_content(
        self,
        query_text: str,
        workspace_id: str,
        top_k: int = 5,
        min_similarity: Optional[float] = None,
        correlation_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Find similar content from workspace history.

        Args:
            query_text: Text to find similar content for
            workspace_id: Workspace to search in
            top_k: Number of similar items to return
            min_similarity: Minimum similarity threshold (defaults to class threshold)
            correlation_id: Request correlation ID

        Returns:
            List of similar content with similarity scores
        """
        correlation_id = correlation_id or get_correlation_id()
        min_similarity = min_similarity or self.similarity_threshold

        logger.info(
            "Finding similar content",
            query_length=len(query_text),
            workspace_id=workspace_id,
            top_k=top_k,
            correlation_id=correlation_id
        )

        # Get query embedding
        query_embedding = await self.get_embedding(query_text, correlation_id)

        # Get all content embeddings from workspace
        workspace_content = await self._get_workspace_content_embeddings(workspace_id)

        if not workspace_content:
            logger.warning(
                "No content found in workspace",
                workspace_id=workspace_id
            )
            return []

        # Compute similarities
        similarities = []

        for content_item in workspace_content:
            content_embedding = content_item.get("embedding")
            if not content_embedding:
                continue

            similarity = self._cosine_similarity(query_embedding, content_embedding)

            if similarity >= min_similarity:
                similarities.append({
                    "content_id": content_item.get("content_id"),
                    "content_preview": content_item.get("content", "")[:200],
                    "metadata": content_item.get("metadata", {}),
                    "similarity_score": similarity
                })

        # Sort by similarity and return top_k
        similarities.sort(key=lambda x: x["similarity_score"], reverse=True)
        results = similarities[:top_k]

        logger.info(
            "Found similar content",
            count=len(results),
            correlation_id=correlation_id
        )

        return results

    async def detect_duplicates(
        self,
        texts: List[str],
        threshold: Optional[float] = None,
        correlation_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Detect duplicate or near-duplicate texts.

        Args:
            texts: List of texts to check for duplicates
            threshold: Similarity threshold for duplicates (default: 0.95)
            correlation_id: Request correlation ID

        Returns:
            List of duplicate pairs with similarity scores
        """
        correlation_id = correlation_id or get_correlation_id()
        threshold = threshold or 0.95

        logger.info(
            "Detecting duplicates",
            text_count=len(texts),
            threshold=threshold,
            correlation_id=correlation_id
        )

        # Generate embeddings for all texts
        import asyncio
        embeddings = await asyncio.gather(*[
            self.get_embedding(text, correlation_id)
            for text in texts
        ])

        # Find duplicate pairs
        duplicates = []

        for i in range(len(embeddings)):
            for j in range(i + 1, len(embeddings)):
                similarity = self._cosine_similarity(embeddings[i], embeddings[j])

                if similarity >= threshold:
                    duplicates.append({
                        "index1": i,
                        "index2": j,
                        "text1_preview": texts[i][:100],
                        "text2_preview": texts[j][:100],
                        "similarity": similarity,
                        "is_exact_duplicate": similarity > 0.99
                    })

        logger.info(
            "Duplicate detection completed",
            duplicate_pairs=len(duplicates),
            correlation_id=correlation_id
        )

        return duplicates

    async def semantic_search(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: int = 10,
        correlation_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Perform semantic search across documents.

        Args:
            query: Search query
            documents: List of documents with 'id' and 'content'
            top_k: Number of results to return
            correlation_id: Request correlation ID

        Returns:
            List of most relevant documents with scores
        """
        correlation_id = correlation_id or get_correlation_id()

        logger.info(
            "Performing semantic search",
            query_length=len(query),
            document_count=len(documents),
            correlation_id=correlation_id
        )

        # Get query embedding
        query_embedding = await self.get_embedding(query, correlation_id)

        # Get embeddings for all documents
        import asyncio
        doc_embeddings = await asyncio.gather(*[
            self.get_embedding(doc.get("content", ""), correlation_id)
            for doc in documents
        ])

        # Compute relevance scores
        results = []

        for i, doc in enumerate(documents):
            similarity = self._cosine_similarity(query_embedding, doc_embeddings[i])

            results.append({
                "document_id": doc.get("id"),
                "content": doc.get("content"),
                "metadata": doc.get("metadata", {}),
                "relevance_score": similarity
            })

        # Sort by relevance and return top_k
        results.sort(key=lambda x: x["relevance_score"], reverse=True)

        logger.info(
            "Semantic search completed",
            results_count=len(results[:top_k]),
            top_score=results[0]["relevance_score"] if results else 0,
            correlation_id=correlation_id
        )

        return results[:top_k]

    async def cluster_by_similarity(
        self,
        texts: List[str],
        num_clusters: Optional[int] = None,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Cluster texts by semantic similarity.

        Args:
            texts: List of texts to cluster
            num_clusters: Number of clusters (auto-detected if not specified)
            correlation_id: Request correlation ID

        Returns:
            Dict containing clusters and their members
        """
        correlation_id = correlation_id or get_correlation_id()

        logger.info(
            "Clustering texts",
            text_count=len(texts),
            num_clusters=num_clusters,
            correlation_id=correlation_id
        )

        # Generate embeddings
        import asyncio
        embeddings = await asyncio.gather(*[
            self.get_embedding(text, correlation_id)
            for text in texts
        ])

        # Simple clustering using similarity threshold
        # In production, you'd use more sophisticated clustering (k-means, DBSCAN)
        clusters = []
        assigned = set()

        for i, embedding1 in enumerate(embeddings):
            if i in assigned:
                continue

            cluster = {
                "cluster_id": len(clusters),
                "members": [{"index": i, "text_preview": texts[i][:100]}],
                "centroid_index": i
            }

            for j, embedding2 in enumerate(embeddings):
                if i == j or j in assigned:
                    continue

                similarity = self._cosine_similarity(embedding1, embedding2)

                if similarity >= 0.75:  # Clustering threshold
                    cluster["members"].append({
                        "index": j,
                        "text_preview": texts[j][:100]
                    })
                    assigned.add(j)

            assigned.add(i)
            clusters.append(cluster)

        result = {
            "num_clusters": len(clusters),
            "clusters": clusters,
            "metadata": {
                "total_texts": len(texts),
                "clustered_at": self._get_timestamp(),
                "correlation_id": correlation_id
            }
        }

        logger.info(
            "Clustering completed",
            num_clusters=len(clusters),
            correlation_id=correlation_id
        )

        return result

    async def store_content_with_embedding(
        self,
        workspace_id: str,
        content_id: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
        correlation_id: Optional[str] = None
    ) -> None:
        """
        Store content along with its embedding for future similarity searches.

        Args:
            workspace_id: Workspace to store in
            content_id: Unique identifier for content
            content: Content text
            metadata: Optional metadata about the content
            correlation_id: Request correlation ID
        """
        correlation_id = correlation_id or get_correlation_id()

        logger.info(
            "Storing content with embedding",
            workspace_id=workspace_id,
            content_id=content_id,
            correlation_id=correlation_id
        )

        # Generate embedding
        embedding = await self.get_embedding(content, correlation_id)

        # Store content with embedding
        storage_key = f"workspace:{workspace_id}:semantic:{content_id}"

        content_data = {
            "content_id": content_id,
            "content": content,
            "embedding": embedding,
            "metadata": metadata or {},
            "stored_at": self._get_timestamp()
        }

        try:
            await redis_cache.set(storage_key, content_data, ttl=86400 * 90)  # 90 days

            logger.debug(
                "Content stored with embedding",
                workspace_id=workspace_id,
                content_id=content_id
            )

        except Exception as e:
            logger.warning(
                "Failed to store content with embedding",
                error=str(e),
                workspace_id=workspace_id
            )

    def _cosine_similarity(
        self,
        embedding1: List[float],
        embedding2: List[float]
    ) -> float:
        """
        Compute cosine similarity between two embedding vectors.

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Cosine similarity score between 0.0 and 1.0
        """
        # Convert to numpy arrays
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)

        # Compute cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        similarity = dot_product / (norm1 * norm2)

        # Ensure result is between 0 and 1
        return max(0.0, min(1.0, float(similarity)))

    def _generate_embedding_cache_key(self, text: str) -> str:
        """Generate cache key for embedding."""
        import hashlib
        text_hash = hashlib.md5(text.encode()).hexdigest()
        return f"embedding:{text_hash}"

    async def _get_workspace_content_embeddings(
        self,
        workspace_id: str
    ) -> List[Dict[str, Any]]:
        """
        Retrieve all content with embeddings from workspace.

        Args:
            workspace_id: Workspace to retrieve from

        Returns:
            List of content items with embeddings
        """
        # This is a simplified implementation
        # In production, you'd query a vector database (Pinecone, Weaviate, etc.)
        logger.debug(
            "Getting workspace content embeddings",
            workspace_id=workspace_id
        )

        # Placeholder - in production this would query stored embeddings
        return []

    def _get_timestamp(self) -> str:
        """Get current ISO timestamp."""
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()


# Global instance
semantic_similarity = SemanticSimilarity()
