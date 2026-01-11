#!/usr/bin/env python3
"""
Test script for basic memory system components.
Tests only the core models without external dependencies.
"""

import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))


def test_memory_basic():
    """Test basic memory components."""
    print("=" * 60)
    print("BASIC MEMORY TEST")
    print("=" * 60)

    try:
        # Test basic imports
        print("Testing basic imports...")
        from memory.models import MemoryChunk, MemoryType

        print("✓ Basic imports successful")

        # Test memory types
        print("\nTesting MemoryType enum...")
        all_types = MemoryType.get_all_types()
        print(f"✓ Available memory types: {all_types}")

        # Test memory chunk creation
        print("\nTesting MemoryChunk creation...")
        chunk = MemoryChunk(
            workspace_id="test-workspace",
            memory_type=MemoryType.FOUNDATION,
            content="This is a test memory chunk for foundation information.",
            metadata={"source": "test", "importance": 0.8},
        )

        print(f"✓ Created memory chunk: {chunk}")
        print(f"  - Type: {chunk.memory_type}")
        print(f"  - Token count: {chunk.get_token_count()}")
        print(f"  - Is empty: {chunk.is_empty()}")

        # Test content chunker
        print("\nTesting ContentChunker...")
        from memory.chunker import ContentChunker

        chunker = ContentChunker(chunk_size=200, overlap=50)

        long_content = """
        This is a long piece of content that should be split into multiple chunks.
        It contains several paragraphs and sentences that will be used to test
        the chunking functionality. The chunker should break this content
        into smaller pieces while maintaining context and overlap between
        chunks. This ensures that no important information is lost at the
        boundaries between chunks.
        """

        chunks = chunker.chunk(long_content)
        print(f"✓ Chunked content into {len(chunks)} chunks")

        chunk_infos = chunker.chunk_with_info(long_content)
        print(f"✓ Generated {len(chunk_infos)} chunk info objects")

        stats = chunker.get_chunk_stats(long_content)
        print(f"✓ Chunk stats: {stats}")

        # Test memory chunk serialization
        print("\nTesting MemoryChunk serialization...")
        chunk_dict = chunk.to_dict()
        print(f"✓ Serialized to dict with keys: {list(chunk_dict.keys())}")

        restored_chunk = MemoryChunk.from_dict(chunk_dict)
        print(f"✓ Restored from dict: {restored_chunk}")

        # Test graph models
        print("\nTesting Graph Models...")
        from memory.graph_models import EntityType, GraphEntity, RelationType

        entity = GraphEntity(
            workspace_id="test-workspace",
            entity_type=EntityType.COMPANY,
            name="Test Company",
            description="A test company for demonstration",
            properties={"industry": "technology", "size": "medium"},
        )

        print(f"✓ Created graph entity: {entity}")
        print(f"  - Type: {entity.entity_type}")
        print(f"  - Properties: {entity.properties}")

        # Test episodic memory models
        print("\nTesting Episodic Memory Models...")
        from memory.episodic_memory import Episode

        episode = Episode(
            workspace_id="test-workspace",
            user_id="test-user",
            session_id="test-session",
            episode_type="conversation",
            title="Test Conversation",
            content="This is a test conversation episode.",
            importance=0.9,
            tags=["test", "conversation"],
        )

        print(f"✓ Created episode: {episode}")
        print(f"  - Token count: {episode.get_token_count()}")
        print(f"  - Has tag 'test': {episode.has_tag('test')}")
        print(f"  - Is expired: {episode.is_expired()}")

        print("\n" + "=" * 60)
        print("BASIC MEMORY TEST COMPLETE")
        print("✓ All basic components working")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_memory_basic()
    sys.exit(0 if success else 1)
