#!/usr/bin/env python3
"""
Test script for memory components with direct imports.
Tests components directly without using package imports.
"""

import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))


def test_memory_direct():
    """Test memory components with direct imports."""
    print("=" * 60)
    print("MEMORY DIRECT IMPORT TEST")
    print("=" * 60)

    try:
        # Test models directly
        print("Testing models directly...")
        sys.path.insert(0, str(backend_path / "memory"))
        from models import MemoryChunk, MemoryType

        print("✓ Models imported directly")

        # Test MemoryType
        all_types = MemoryType.get_all_types()
        print(f"✓ Memory types: {all_types}")

        # Test MemoryChunk
        chunk = MemoryChunk(
            workspace_id="test-workspace",
            memory_type=MemoryType.FOUNDATION,
            content="Test content",
            metadata={"test": True},
        )
        print(f"✓ MemoryChunk created: {chunk}")

        # Test chunker directly
        print("\nTesting chunker directly...")
        from chunker import ContentChunker

        chunker = ContentChunker(chunk_size=100, overlap=20)
        chunks = chunker.chunk(
            "This is a test content that should be chunked into smaller pieces for better processing and storage."
        )
        print(f"✓ Content chunked into {len(chunks)} pieces")

        # Test graph models directly
        print("\nTesting graph models directly...")
        from graph_models import EntityType, GraphEntity, RelationType

        entity = GraphEntity(
            workspace_id="test-workspace",
            entity_type=EntityType.COMPANY,
            name="Test Company",
            properties={"description": "Test description", "industry": "technology"},
        )
        print(f"✓ GraphEntity created: {entity}")

        # Test episodic memory directly
        print("\nTesting episodic memory directly...")
        from episodic_memory import Episode

        episode = Episode(
            workspace_id="test-workspace",
            user_id="test-user",
            session_id="test-session",
            episode_type="conversation",
            title="Test Episode",
            content="Test episode content",
        )
        print(f"✓ Episode created: {episode}")

        print("\n" + "=" * 60)
        print("MEMORY DIRECT IMPORT TEST COMPLETE")
        print("✓ All components working")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_memory_direct()
    sys.exit(0 if success else 1)
