"""
Empirical test for memory models.

This script verifies that:
1. MemoryType enum has all required types
2. MemoryChunk dataclass works correctly
3. All methods function as expected
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from datetime import datetime

import numpy as np
from memory.models import MemoryChunk, MemoryType


def test_memory_type_enum():
    """Test MemoryType enum functionality."""
    print("Testing MemoryType enum...")

    # Check all required types exist
    required_types = [
        "foundation",
        "icp",
        "move",
        "campaign",
        "research",
        "conversation",
        "feedback",
    ]
    actual_types = MemoryType.get_all_types()

    print(f"Required types: {required_types}")
    print(f"Actual types: {actual_types}")

    assert set(required_types) == set(
        actual_types
    ), f"Missing types: {set(required_types) - set(actual_types)}"

    # Test from_string conversion
    for type_str in required_types:
        memory_type = MemoryType.from_string(type_str)
        assert memory_type.value == type_str, f"Failed to convert {type_str}"

    # Test invalid type raises error
    try:
        MemoryType.from_string("invalid_type")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass  # Expected

    print("✓ MemoryType enum tests passed")


def test_memory_chunk_dataclass():
    """Test MemoryChunk dataclass functionality."""
    print("Testing MemoryChunk dataclass...")

    # Test basic creation
    chunk = MemoryChunk(
        id="test-123",
        workspace_id="ws-456",
        memory_type=MemoryType.FOUNDATION,
        content="This is test content",
        metadata={"key": "value"},
    )

    assert chunk.id == "test-123"
    assert chunk.workspace_id == "ws-456"
    assert chunk.memory_type == MemoryType.FOUNDATION
    assert chunk.content == "This is test content"
    assert chunk.metadata == {"key": "value"}
    assert chunk.embedding is None
    assert chunk.score is None

    # Test default values
    empty_chunk = MemoryChunk()
    assert empty_chunk.id is None
    assert empty_chunk.workspace_id is None
    assert empty_chunk.memory_type is None
    assert empty_chunk.content == ""
    assert empty_chunk.metadata == {}
    assert empty_chunk.created_at is not None
    assert empty_chunk.updated_at is not None

    print("✓ MemoryChunk creation tests passed")


def test_memory_chunk_methods():
    """Test MemoryChunk methods."""
    print("Testing MemoryChunk methods...")

    chunk = MemoryChunk(
        id="test-123",
        workspace_id="ws-456",
        memory_type=MemoryType.ICP,
        content="Test content for method testing",
        metadata={"existing_key": "existing_value"},
    )

    # Test to_dict/from_dict
    chunk_dict = chunk.to_dict()
    assert chunk_dict["id"] == "test-123"
    assert chunk_dict["memory_type"] == "icp"
    assert "created_at" in chunk_dict

    restored_chunk = MemoryChunk.from_dict(chunk_dict)
    assert restored_chunk.id == chunk.id
    assert restored_chunk.memory_type == chunk.memory_type
    assert restored_chunk.content == chunk.content

    # Test embedding methods
    test_embedding = np.random.rand(384)
    chunk.embedding = test_embedding

    embedding_list = chunk.get_embedding_list()
    assert len(embedding_list) == 384
    assert isinstance(embedding_list, list)

    new_chunk = MemoryChunk()
    new_chunk.set_embedding_from_list(embedding_list)
    assert np.array_equal(new_chunk.embedding, test_embedding)

    # Test metadata methods
    chunk.add_metadata("new_key", "new_value")
    assert chunk.get_metadata("new_key") == "new_value"
    assert chunk.get_metadata("missing_key", "default") == "default"
    assert chunk.has_metadata("new_key")
    assert not chunk.has_metadata("missing_key")

    # Test utility methods
    assert not chunk.is_empty()
    empty_chunk = MemoryChunk(content="")
    assert empty_chunk.is_empty()

    # Test truncation
    long_content = "a" * 100
    long_chunk = MemoryChunk(content=long_content)
    truncated = long_chunk.truncate_content(50)
    assert len(truncated) <= 50
    assert truncated.endswith("...")

    # Test token count estimation
    chunk.content = "This is a test content with about twelve words"
    token_count = chunk.get_token_count()
    assert token_count > 0
    assert isinstance(token_count, int)

    # Test age check
    assert not chunk.is_expired(90)  # Should not be expired

    print("✓ MemoryChunk method tests passed")


def test_memory_chunk_with_embedding():
    """Test MemoryChunk with actual embedding."""
    print("Testing MemoryChunk with embedding...")

    # Create chunk with embedding
    embedding = np.random.rand(384)  # Simulate SentenceTransformer output
    chunk = MemoryChunk(
        id="test-with-embedding",
        workspace_id="ws-789",
        memory_type=MemoryType.RESEARCH,
        content="Research content with embedding",
        embedding=embedding,
    )

    # Verify embedding properties
    assert chunk.embedding is not None
    assert chunk.embedding.shape == (384,)
    assert isinstance(chunk.embedding, np.ndarray)

    # Test serialization with embedding
    chunk_dict = chunk.to_dict()
    # Note: embedding not included in to_dict for storage efficiency
    assert "embedding" not in chunk_dict

    # Test round trip with embedding
    embedding_list = chunk.get_embedding_list()
    restored_chunk = MemoryChunk.from_dict(chunk_dict)
    restored_chunk.set_embedding_from_list(embedding_list)

    assert np.array_equal(restored_chunk.embedding, chunk.embedding)

    print("✓ MemoryChunk embedding tests passed")


def run_all_tests():
    """Run all empirical tests."""
    print("=" * 60)
    print("RUNNING EMPIRICAL TESTS FOR MEMORY MODELS")
    print("=" * 60)

    try:
        test_memory_type_enum()
        test_memory_chunk_dataclass()
        test_memory_chunk_methods()
        test_memory_chunk_with_embedding()

        print("=" * 60)
        print("✅ ALL TESTS PASSED - MODELS WORK CORRECTLY")
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
