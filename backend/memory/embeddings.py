"""
Embedding model for vector memory.

This module provides a singleton embedding model using SentenceTransformer
for generating text embeddings with caching support.
"""

import hashlib
import logging
import os
from datetime import datetime, timedelta
from functools import lru_cache
from typing import Any, Dict, List, Optional

import numpy as np

logger = logging.getLogger(__name__)


class EmbeddingModel:
    """
    Singleton embedding model using SentenceTransformer.

    Provides text embedding generation with caching and normalization.
    """

    _instance: Optional["EmbeddingModel"] = None
    _model = None
    _cache: Dict[str, np.ndarray] = {}
    _cache_timestamps: Dict[str, datetime] = {}
    _cache_ttl = timedelta(hours=1)  # Cache for 1 hour
    _max_cache_size = 1000

    def __new__(cls) -> "EmbeddingModel":
        """Ensure singleton pattern."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """Initialize the embedding model."""
        if hasattr(self, "_initialized"):
            return

        self.model_name = os.getenv("MODEL_NAME")
        self.embedding_dim = 384
        self._initialized = True
        self._load_model()

    def _load_model(self):
        """Load the SentenceTransformer model."""
        try:
            from sentence_transformers import SentenceTransformer

            self._model = SentenceTransformer(self.model_name)
            logger.info(f"Loaded embedding model: {self.model_name}")
        except ImportError:
            logger.error(
                "sentence_transformers not installed. Install with: pip install sentence-transformers"
            )
            raise
        except Exception as e:
            logger.error(f"Failed to load embedding model: {e}")
            raise

    def _get_cache_key(self, text: str) -> str:
        """Generate cache key for text."""
        return hashlib.md5(text.encode("utf-8")).hexdigest()

    def _clean_cache(self):
        """Clean expired cache entries."""
        now = datetime.now()
        expired_keys = []

        for key, timestamp in self._cache_timestamps.items():
            if now - timestamp > self._cache_ttl:
                expired_keys.append(key)

        for key in expired_keys:
            self._cache.pop(key, None)
            self._cache_timestamps.pop(key, None)

        # If cache is too large, remove oldest entries
        if len(self._cache) > self._max_cache_size:
            # Sort by timestamp and remove oldest
            sorted_items = sorted(self._cache_timestamps.items(), key=lambda x: x[1])

            excess = len(self._cache) - self._max_cache_size
            for key, _ in sorted_items[:excess]:
                self._cache.pop(key, None)
                self._cache_timestamps.pop(key, None)

    def _get_from_cache(self, text: str) -> Optional[np.ndarray]:
        """Get embedding from cache."""
        key = self._get_cache_key(text)

        if key in self._cache:
            # Check if cache entry is still valid
            timestamp = self._cache_timestamps.get(key)
            if timestamp and datetime.now() - timestamp < self._cache_ttl:
                return self._cache[key].copy()
            else:
                # Remove expired entry
                self._cache.pop(key, None)
                self._cache_timestamps.pop(key, None)

        return None

    def _store_in_cache(self, text: str, embedding: np.ndarray):
        """Store embedding in cache."""
        key = self._get_cache_key(text)
        self._cache[key] = embedding.copy()
        self._cache_timestamps[key] = datetime.now()

        # Clean cache if needed
        if len(self._cache) > self._max_cache_size:
            self._clean_cache()

    def encode(self, texts: List[str]) -> np.ndarray:
        """
        Encode multiple texts to embeddings.

        Args:
            texts: List of text strings to encode

        Returns:
            numpy array of shape (len(texts), embedding_dim)
        """
        if not texts:
            return np.array([]).reshape(0, self.embedding_dim)

        # Check cache for each text
        cached_embeddings = []
        uncached_texts = []
        uncached_indices = []

        for i, text in enumerate(texts):
            cached = self._get_from_cache(text)
            if cached is not None:
                cached_embeddings.append((i, cached))
            else:
                uncached_texts.append(text)
                uncached_indices.append(i)

        # Encode uncached texts
        if uncached_texts:
            try:
                new_embeddings = self._model.encode(
                    uncached_texts, convert_to_numpy=True, normalize_embeddings=True
                )

                # Store in cache
                for text, embedding in zip(uncached_texts, new_embeddings):
                    self._store_in_cache(text, embedding)

                # Combine with cached results
                all_embeddings = np.zeros((len(texts), self.embedding_dim))

                # Fill cached embeddings
                for idx, embedding in cached_embeddings:
                    all_embeddings[idx] = embedding

                # Fill new embeddings
                for idx, embedding in zip(uncached_indices, new_embeddings):
                    all_embeddings[idx] = embedding

                return all_embeddings

            except Exception as e:
                logger.error(f"Failed to encode texts: {e}")
                raise
        else:
            # All texts were cached
            all_embeddings = np.zeros((len(texts), self.embedding_dim))
            for idx, embedding in cached_embeddings:
                all_embeddings[idx] = embedding
            return all_embeddings

    def encode_single(self, text: str) -> np.ndarray:
        """
        Encode a single text to embedding.

        Args:
            text: Text string to encode

        Returns:
            numpy array of shape (embedding_dim,)
        """
        # Check cache first
        cached = self._get_from_cache(text)
        if cached is not None:
            return cached

        try:
            embedding = self._model.encode(
                text, convert_to_numpy=True, normalize_embeddings=True
            )

            # Store in cache
            self._store_in_cache(text, embedding)

            return embedding

        except Exception as e:
            logger.error(f"Failed to encode text: {e}")
            raise

    @lru_cache(maxsize=1000)
    def encode_cached(self, text: str) -> np.ndarray:
        """
        Encode text with LRU cache (alternative caching method).

        Args:
            text: Text string to encode

        Returns:
            numpy array of shape (embedding_dim,)
        """
        return self.encode_single(text)

    def get_embedding_info(self) -> Dict[str, Any]:
        """Get information about the embedding model."""
        return {
            "model_name": self.model_name,
            "embedding_dim": self.embedding_dim,
            "cache_size": len(self._cache),
            "max_cache_size": self._max_cache_size,
            "cache_ttl_hours": self._cache_ttl.total_seconds() / 3600,
            "model_loaded": self._model is not None,
        }

    def clear_cache(self):
        """Clear all cached embeddings."""
        self._cache.clear()
        self._cache_timestamps.clear()
        logger.info("Embedding cache cleared")

    def warm_up(self, sample_texts: List[str] = None):
        """Warm up the model with sample texts."""
        if sample_texts is None:
            sample_texts = [
                "This is a sample text for warming up the embedding model.",
                "Another sample text to ensure the model is working properly.",
                "Foundation information about a company.",
                "ICP profile describing ideal customers.",
                "Marketing move strategy and execution plan.",
            ]

        logger.info(f"Warming up embedding model with {len(sample_texts)} texts...")
        try:
            self.encode(sample_texts)
            logger.info("Embedding model warmed up successfully")
        except Exception as e:
            logger.error(f"Failed to warm up embedding model: {e}")
            raise

    def validate_embedding(self, embedding: np.ndarray) -> bool:
        """
        Validate that an embedding has the correct shape and values.

        Args:
            embedding: numpy array to validate

        Returns:
            True if valid, False otherwise
        """
        if not isinstance(embedding, np.ndarray):
            return False

        if embedding.shape != (self.embedding_dim,):
            return False

        if not np.isfinite(embedding).all():
            return False

        # Check if normalized (should have L2 norm close to 1)
        norm = np.linalg.norm(embedding)
        if abs(norm - 1.0) > 0.1:  # Allow some tolerance
            return False

        return True

    def normalize_embedding(self, embedding: np.ndarray) -> np.ndarray:
        """
        Normalize an embedding to unit length.

        Args:
            embedding: numpy array to normalize

        Returns:
            normalized embedding
        """
        norm = np.linalg.norm(embedding)
        if norm == 0:
            return embedding
        return embedding / norm

    def compute_similarity(
        self, embedding1: np.ndarray, embedding2: np.ndarray
    ) -> float:
        """
        Compute cosine similarity between two embeddings.

        Args:
            embedding1: First embedding
            embedding2: Second embedding

        Returns:
            cosine similarity score
        """
        # Normalize embeddings
        norm1 = self.normalize_embedding(embedding1)
        norm2 = self.normalize_embedding(embedding2)

        # Compute cosine similarity
        return float(np.dot(norm1, norm2))


# Global instance
_embedding_model: Optional[EmbeddingModel] = None


def get_embedding_model() -> EmbeddingModel:
    """Get the singleton embedding model instance."""
    global _embedding_model
    if _embedding_model is None:
        _embedding_model = EmbeddingModel()
    return _embedding_model


def encode_texts(texts: List[str]) -> np.ndarray:
    """Convenience function to encode multiple texts."""
    return get_embedding_model().encode(texts)


def encode_text(text: str) -> np.ndarray:
    """Convenience function to encode a single text."""
    return get_embedding_model().encode_single(text)
