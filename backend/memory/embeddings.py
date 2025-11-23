"""
Embeddings Module - Text Embedding Generation

This module provides utilities for generating text embeddings using sentence-transformers.
Embeddings are vector representations of text that enable semantic search and similarity
matching across documents, messages, and generated content.

Purpose:
--------
- Generate high-quality text embeddings for semantic search
- Support multiple embedding models (sentence-transformers, OpenAI, etc.)
- Enable batch embedding generation for efficiency
- Provide embedding similarity/distance calculations
- Cache embeddings for frequently used texts

Supported Models:
-----------------
- sentence-transformers/all-MiniLM-L6-v2 (default, 384 dimensions, fast)
- sentence-transformers/all-mpnet-base-v2 (768 dimensions, high quality)
- OpenAI text-embedding-ada-002 (1536 dimensions, requires API key)

Use Cases:
----------
- Semantic search across conversation history
- Finding similar content pieces
- Clustering campaigns or personas by similarity
- Recommendation systems for content templates
- Context retrieval for agent prompts

Dependencies:
-------------
- sentence-transformers: For local embedding generation
- numpy: For vector operations
- torch: For model inference (optional GPU support)
- functools: For caching

Usage Example:
--------------
from memory.embeddings import EmbeddingGenerator

# Initialize generator
embedder = EmbeddingGenerator(model_name="all-MiniLM-L6-v2")

# Generate single embedding
text = "Our target audience is tech-savvy millennials"
embedding = await embedder.embed(text)
# Returns: List[float] of length 384

# Generate batch embeddings
texts = ["Campaign A description", "Campaign B description"]
embeddings = await embedder.embed_batch(texts)
# Returns: List[List[float]]

# Calculate similarity
similarity = embedder.cosine_similarity(embedding1, embedding2)
# Returns: float between -1 and 1 (1 = identical)
"""

import asyncio
from typing import List, Optional, Union
from functools import lru_cache
import structlog

try:
    from sentence_transformers import SentenceTransformer
    import numpy as np
    SENTENCE_TRANSFORMERS_AVAILABLE = True
except ImportError:
    SENTENCE_TRANSFORMERS_AVAILABLE = False
    SentenceTransformer = None
    np = None

logger = structlog.get_logger()


class EmbeddingGenerator:
    """
    Text embedding generator using sentence-transformers.

    This class provides methods for generating embeddings from text using
    pre-trained models. It supports both single and batch generation with
    automatic GPU detection and model caching.

    Attributes:
        model_name: Name of the sentence-transformers model
        model: Loaded SentenceTransformer model instance
        dimensions: Dimensionality of the embedding vectors
        device: Device used for inference (cuda/cpu)
    """

    # Model configurations
    MODEL_CONFIGS = {
        "all-MiniLM-L6-v2": {
            "full_name": "sentence-transformers/all-MiniLM-L6-v2",
            "dimensions": 384,
            "description": "Fast and efficient, good for most use cases"
        },
        "all-mpnet-base-v2": {
            "full_name": "sentence-transformers/all-mpnet-base-v2",
            "dimensions": 768,
            "description": "Higher quality, slower than MiniLM"
        },
        "paraphrase-MiniLM-L6-v2": {
            "full_name": "sentence-transformers/paraphrase-MiniLM-L6-v2",
            "dimensions": 384,
            "description": "Optimized for paraphrase detection"
        }
    }

    def __init__(
        self,
        model_name: str = "all-MiniLM-L6-v2",
        device: Optional[str] = None
    ):
        """
        Initialize embedding generator with specified model.

        Args:
            model_name: Name of the model to use (see MODEL_CONFIGS)
            device: Device to use ('cuda', 'cpu', or None for auto-detect)

        Raises:
            ImportError: If sentence-transformers is not installed
            ValueError: If model_name is not recognized
        """
        if not SENTENCE_TRANSFORMERS_AVAILABLE:
            raise ImportError(
                "sentence-transformers not installed. "
                "Install with: pip install sentence-transformers"
            )

        self.model_name = model_name
        self.model: Optional[SentenceTransformer] = None
        self.device = device
        self.dimensions = 0

        # Validate model name
        if model_name not in self.MODEL_CONFIGS:
            raise ValueError(
                f"Unknown model: {model_name}. "
                f"Available models: {list(self.MODEL_CONFIGS.keys())}"
            )

        self.logger = structlog.get_logger().bind(
            model_name=model_name,
            device=device
        )

    def _load_model(self) -> SentenceTransformer:
        """
        Load the sentence-transformers model.

        Returns:
            Loaded SentenceTransformer model

        Raises:
            Exception: If model loading fails
        """
        if self.model is None:
            try:
                config = self.MODEL_CONFIGS[self.model_name]
                full_model_name = config["full_name"]

                self.logger.info(
                    "Loading embedding model",
                    model=full_model_name
                )

                self.model = SentenceTransformer(
                    full_model_name,
                    device=self.device
                )
                self.dimensions = config["dimensions"]

                self.logger.info(
                    "Embedding model loaded successfully",
                    dimensions=self.dimensions,
                    device=self.model.device
                )

            except Exception as e:
                self.logger.error(
                    "Failed to load embedding model",
                    error=str(e)
                )
                raise

        return self.model

    async def embed(self, text: str) -> List[float]:
        """
        Generate embedding for a single text.

        Args:
            text: Input text to embed

        Returns:
            List of floats representing the embedding vector

        Raises:
            ValueError: If text is empty
            Exception: If embedding generation fails
        """
        if not text or not text.strip():
            raise ValueError("Cannot embed empty text")

        try:
            model = self._load_model()

            # Run embedding in thread pool to avoid blocking
            loop = asyncio.get_running_loop()
            embedding = await loop.run_in_executor(
                None,
                lambda: model.encode(text, convert_to_numpy=True)
            )

            # Convert to list for JSON serialization
            embedding_list = embedding.tolist()

            self.logger.debug(
                "Generated embedding",
                text_length=len(text),
                dimensions=len(embedding_list)
            )

            return embedding_list

        except Exception as e:
            self.logger.error(
                "Failed to generate embedding",
                text_preview=text[:100],
                error=str(e)
            )
            raise

    async def embed_batch(
        self,
        texts: List[str],
        batch_size: int = 32,
        show_progress: bool = False
    ) -> List[List[float]]:
        """
        Generate embeddings for multiple texts efficiently.

        Args:
            texts: List of input texts to embed
            batch_size: Batch size for processing (default: 32)
            show_progress: Whether to show progress bar (default: False)

        Returns:
            List of embedding vectors, one per input text

        Raises:
            ValueError: If texts list is empty
            Exception: If batch embedding fails
        """
        if not texts:
            raise ValueError("Cannot embed empty text list")

        # Filter out empty texts
        valid_texts = [t for t in texts if t and t.strip()]
        if not valid_texts:
            raise ValueError("All texts are empty")

        try:
            model = self._load_model()

            # Run batch embedding in thread pool
            loop = asyncio.get_running_loop()
            embeddings = await loop.run_in_executor(
                None,
                lambda: model.encode(
                    valid_texts,
                    batch_size=batch_size,
                    show_progress_bar=show_progress,
                    convert_to_numpy=True
                )
            )

            # Convert to list of lists
            embeddings_list = [emb.tolist() for emb in embeddings]

            self.logger.debug(
                "Generated batch embeddings",
                count=len(embeddings_list),
                dimensions=len(embeddings_list[0]) if embeddings_list else 0
            )

            return embeddings_list

        except Exception as e:
            self.logger.error(
                "Failed to generate batch embeddings",
                text_count=len(texts),
                error=str(e)
            )
            raise

    def cosine_similarity(
        self,
        embedding1: List[float],
        embedding2: List[float]
    ) -> float:
        """
        Calculate cosine similarity between two embeddings.

        Cosine similarity ranges from -1 (opposite) to 1 (identical).
        Values closer to 1 indicate higher similarity.

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Cosine similarity score (float between -1 and 1)

        Raises:
            ValueError: If embeddings have different dimensions
        """
        if len(embedding1) != len(embedding2):
            raise ValueError(
                f"Embedding dimensions mismatch: {len(embedding1)} vs {len(embedding2)}"
            )

        # Convert to numpy arrays
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)

        # Calculate cosine similarity
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        similarity = dot_product / (norm1 * norm2)

        return float(similarity)

    def euclidean_distance(
        self,
        embedding1: List[float],
        embedding2: List[float]
    ) -> float:
        """
        Calculate Euclidean distance between two embeddings.

        Lower distance indicates higher similarity.

        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector

        Returns:
            Euclidean distance (float >= 0)

        Raises:
            ValueError: If embeddings have different dimensions
        """
        if len(embedding1) != len(embedding2):
            raise ValueError(
                f"Embedding dimensions mismatch: {len(embedding1)} vs {len(embedding2)}"
            )

        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)

        distance = np.linalg.norm(vec1 - vec2)

        return float(distance)

    def find_most_similar(
        self,
        query_embedding: List[float],
        candidate_embeddings: List[List[float]],
        top_k: int = 5
    ) -> List[tuple]:
        """
        Find the most similar embeddings to a query embedding.

        Args:
            query_embedding: Query embedding vector
            candidate_embeddings: List of candidate embedding vectors
            top_k: Number of top results to return

        Returns:
            List of tuples (index, similarity_score) sorted by similarity (descending)

        Example:
            results = embedder.find_most_similar(query_emb, candidate_embs, top_k=3)
            # Returns: [(5, 0.92), (12, 0.87), (3, 0.84)]
        """
        if not candidate_embeddings:
            return []

        # Calculate similarities
        similarities = []
        for idx, candidate in enumerate(candidate_embeddings):
            similarity = self.cosine_similarity(query_embedding, candidate)
            similarities.append((idx, similarity))

        # Sort by similarity (descending)
        similarities.sort(key=lambda x: x[1], reverse=True)

        # Return top_k results
        return similarities[:top_k]

    @staticmethod
    def get_available_models() -> dict:
        """
        Get information about available embedding models.

        Returns:
            Dictionary of model configurations
        """
        return EmbeddingGenerator.MODEL_CONFIGS.copy()


# Singleton instance for shared use
_default_embedder: Optional[EmbeddingGenerator] = None


def get_embedder(
    model_name: str = "all-MiniLM-L6-v2",
    device: Optional[str] = None
) -> EmbeddingGenerator:
    """
    Get or create a singleton embedding generator.

    This function provides a shared embedding generator instance to avoid
    loading the model multiple times.

    Args:
        model_name: Name of the model to use
        device: Device to use for inference

    Returns:
        EmbeddingGenerator instance
    """
    global _default_embedder

    if _default_embedder is None:
        _default_embedder = EmbeddingGenerator(
            model_name=model_name,
            device=device
        )

    return _default_embedder


# Convenience functions
async def embed_text(text: str) -> List[float]:
    """
    Convenience function to embed a single text using default embedder.

    Args:
        text: Text to embed

    Returns:
        Embedding vector
    """
    embedder = get_embedder()
    return await embedder.embed(text)


async def embed_texts(texts: List[str]) -> List[List[float]]:
    """
    Convenience function to embed multiple texts using default embedder.

    Args:
        texts: List of texts to embed

    Returns:
        List of embedding vectors
    """
    embedder = get_embedder()
    return await embedder.embed_batch(texts)
