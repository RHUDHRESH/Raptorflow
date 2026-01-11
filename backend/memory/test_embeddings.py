"""
Empirical test for embedding model.

This script verifies that:
1. Embedding model generates 384-dim vectors
2. Caching works correctly
3. Singleton pattern works
4. Embeddings are normalized
5. Similarity computation works
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import time

import numpy as np
from memory.embeddings import (
    EmbeddingModel,
    encode_text,
    encode_texts,
    get_embedding_model,
)


def test_singleton_pattern():
    """Test that EmbeddingModel follows singleton pattern."""
    print("Testing singleton pattern...")

    # Create two instances
    model1 = EmbeddingModel()
    model2 = EmbeddingModel()

    # They should be the same instance
    assert model1 is model2, "EmbeddingModel should be singleton"

    # Global function should return same instance
    model3 = get_embedding_model()
    assert model1 is model3, "get_embedding_model() should return same instance"

    print("✓ Singleton pattern test passed")


def test_embedding_dimensions():
    """Test that embeddings have correct dimensions."""
    print("Testing embedding dimensions...")

    model = get_embedding_model()

    # Test single text embedding
    text = "This is a test text for embedding generation."
    embedding = model.encode_single(text)

    assert isinstance(embedding, np.ndarray), "Embedding should be numpy array"
    assert embedding.shape == (384,), f"Expected shape (384,), got {embedding.shape}"
    assert np.isfinite(embedding).all(), "Embedding should contain finite values"

    # Test multiple text embeddings
    texts = ["First test text", "Second test text", "Third test text"]
    embeddings = model.encode(texts)

    assert isinstance(embeddings, np.ndarray), "Embeddings should be numpy array"
    assert embeddings.shape == (
        3,
        384,
    ), f"Expected shape (3, 384), got {embeddings.shape}"
    assert np.isfinite(embeddings).all(), "All embeddings should contain finite values"

    print("✓ Embedding dimensions test passed")


def test_embedding_normalization():
    """Test that embeddings are properly normalized."""
    print("Testing embedding normalization...")

    model = get_embedding_model()

    text = "Test text for normalization check"
    embedding = model.encode_single(text)

    # Check L2 norm is close to 1
    norm = np.linalg.norm(embedding)
    assert abs(norm - 1.0) < 0.1, f"Embedding should be normalized, norm={norm}"

    # Test validation function
    assert model.validate_embedding(embedding), "Valid embedding should pass validation"

    # Test invalid embedding
    invalid_embedding = np.array([1, 2, 3])  # Wrong dimensions
    assert not model.validate_embedding(
        invalid_embedding
    ), "Invalid embedding should fail validation"

    # Test embedding with NaN
    nan_embedding = embedding.copy()
    nan_embedding[0] = np.nan
    assert not model.validate_embedding(
        nan_embedding
    ), "Embedding with NaN should fail validation"

    print("✓ Embedding normalization test passed")


def test_caching_functionality():
    """Test that caching works correctly."""
    print("Testing caching functionality...")

    model = get_embedding_model()

    # Clear cache to start fresh
    model.clear_cache()
    assert len(model._cache) == 0, "Cache should be empty after clear"

    # Encode a text
    text = "Test text for caching"

    # First call should not be cached
    start_time = time.time()
    embedding1 = model.encode_single(text)
    first_call_time = time.time() - start_time

    # Second call should be cached (faster)
    start_time = time.time()
    embedding2 = model.encode_single(text)
    second_call_time = time.time() - start_time

    # Results should be identical
    assert np.array_equal(
        embedding1, embedding2
    ), "Cached embedding should be identical"

    # Second call should be faster (though this might be flaky in CI)
    print(f"First call: {first_call_time:.4f}s, Second call: {second_call_time:.4f}s")

    # Check cache contains the text
    assert len(model._cache) > 0, "Cache should contain the embedding"

    # Test LRU cache function
    embedding3 = model.encode_cached(text)
    assert np.array_equal(
        embedding1, embedding3
    ), "LRU cached embedding should be identical"

    print("✓ Caching functionality test passed")


def test_similarity_computation():
    """Test similarity computation between embeddings."""
    print("Testing similarity computation...")

    model = get_embedding_model()

    # Create embeddings for similar texts
    text1 = "Marketing strategy for SaaS companies"
    text2 = "SaaS marketing approaches and tactics"
    text3 = "Cooking pasta with tomato sauce"

    emb1 = model.encode_single(text1)
    emb2 = model.encode_single(text2)
    emb3 = model.encode_single(text3)

    # Similarity between similar texts should be high
    sim_12 = model.compute_similarity(emb1, emb2)

    # Similarity between different texts should be lower
    sim_13 = model.compute_similarity(emb1, emb3)

    print(f"Similarity (marketing texts): {sim_12:.4f}")
    print(f"Similarity (marketing vs cooking): {sim_13:.4f}")

    # Similarities should be between -1 and 1
    assert -1.0 <= sim_12 <= 1.0, "Similarity should be between -1 and 1"
    assert -1.0 <= sim_13 <= 1.0, "Similarity should be between -1 and 1"

    # Similar texts should have higher similarity
    assert sim_12 > sim_13, "Similar texts should have higher similarity"

    # Self-similarity should be 1
    sim_11 = model.compute_similarity(emb1, emb1)
    assert abs(sim_11 - 1.0) < 0.001, "Self-similarity should be 1"

    print("✓ Similarity computation test passed")


def test_convenience_functions():
    """Test convenience functions."""
    print("Testing convenience functions...")

    # Test encode_text function
    text = "Test convenience function"
    embedding1 = encode_text(text)

    assert isinstance(embedding1, np.ndarray), "encode_text should return numpy array"
    assert embedding1.shape == (
        384,
    ), f"encode_text should return 384-dim vector, got {embedding1.shape}"

    # Test encode_texts function
    texts = ["Text 1", "Text 2", "Text 3"]
    embeddings2 = encode_texts(texts)

    assert isinstance(embeddings2, np.ndarray), "encode_texts should return numpy array"
    assert embeddings2.shape == (
        3,
        384,
    ), f"encode_texts should return (3, 384), got {embeddings2.shape}"

    print("✓ Convenience functions test passed")


def test_model_info():
    """Test model information methods."""
    print("Testing model info...")

    model = get_embedding_model()
    info = model.get_embedding_info()

    required_keys = [
        "model_name",
        "embedding_dim",
        "cache_size",
        "max_cache_size",
        "cache_ttl_hours",
        "model_loaded",
    ]
    for key in required_keys:
        assert key in info, f"Model info should contain {key}"

    assert (
        info["model_name"] == "all-MiniLM-L6-v2"
    ), f"Expected model name 'all-MiniLM-L6-v2', got {info['model_name']}"
    assert (
        info["embedding_dim"] == 384
    ), f"Expected embedding dim 384, got {info['embedding_dim']}"
    assert info["model_loaded"] == True, "Model should be loaded"

    print(f"Model info: {info}")
    print("✓ Model info test passed")


def test_warm_up():
    """Test model warm up functionality."""
    print("Testing model warm up...")

    model = get_embedding_model()

    # Clear cache first
    model.clear_cache()

    # Warm up with default texts
    model.warm_up()

    # Cache should have some entries after warm up
    assert len(model._cache) > 0, "Cache should have entries after warm up"

    # Test with custom texts
    model.clear_cache()
    custom_texts = ["Custom warm up text 1", "Custom warm up text 2"]
    model.warm_up(custom_texts)

    assert len(model._cache) >= len(
        custom_texts
    ), "Cache should have custom warm up texts"

    print("✓ Model warm up test passed")


def run_all_tests():
    """Run all empirical tests."""
    print("=" * 60)
    print("RUNNING EMPIRICAL TESTS FOR EMBEDDING MODEL")
    print("=" * 60)

    try:
        test_singleton_pattern()
        test_embedding_dimensions()
        test_embedding_normalization()
        test_caching_functionality()
        test_similarity_computation()
        test_convenience_functions()
        test_model_info()
        test_warm_up()

        print("=" * 60)
        print("✅ ALL TESTS PASSED - EMBEDDING MODEL WORKS CORRECTLY")
        print("=" * 60)
        return True

    except Exception as e:
        print("=" * 60)
        print(f"❌ TEST FAILED: {e}")
        print("=" * 60)
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
