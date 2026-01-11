#!/usr/bin/env python3
"""
Test script to verify memory system fixes.
Tests components from the backend directory.
"""

import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))


def test_memory_fixes():
    """Test memory system after import fixes."""
    print("=" * 60)
    print("MEMORY SYSTEM FIXES TEST")
    print("=" * 60)

    try:
        # Test basic imports from backend directory
        print("Testing imports from backend directory...")

        # Test models
        from memory.models import MemoryChunk, MemoryType

        print("✓ Models imported successfully")

        # Test chunker
        from memory.chunker import ContentChunker

        print("✓ ContentChunker imported successfully")

        # Test graph models
        from memory.graph_models import EntityType, GraphEntity

        print("✓ Graph models imported successfully")

        # Test episodic memory
        from memory.episodic_memory import Episode

        print("✓ Episodic memory imported successfully")

        # Test graph memory
        from memory.graph_memory import GraphMemory

        print("✓ Graph memory imported successfully")

        # Test working memory
        from memory.working_memory import WorkingMemory

        print("✓ Working memory imported successfully")

        # Test memory controller
        from memory.controller import MemoryController

        print("✓ Memory controller imported successfully")

        # Test basic functionality
        print("\nTesting basic functionality...")

        # Create memory chunk
        chunk = MemoryChunk(
            workspace_id="test-workspace",
            memory_type=MemoryType.FOUNDATION,
            content="Test content for memory system verification",
            metadata={"test": True, "source": "verification"},
        )
        print(f"✓ MemoryChunk created: {chunk}")

        # Test chunker
        chunker = ContentChunker(chunk_size=100, overlap=20)
        chunks = chunker.chunk(
            "This is a test content that should be chunked into smaller pieces for better processing and storage."
        )
        print(f"✓ Content chunked into {len(chunks)} pieces")

        # Test graph entity
        entity = GraphEntity(
            workspace_id="test-workspace",
            entity_type=EntityType.COMPANY,
            name="Test Company",
            properties={
                "description": "Test company for verification",
                "industry": "technology",
            },
        )
        print(f"✓ GraphEntity created: {entity}")

        # Test episode
        episode = Episode(
            workspace_id="test-workspace",
            user_id="test-user",
            session_id="test-session",
            episode_type="conversation",
            title="Test Episode",
            content="Test episode content for verification",
            importance=0.9,
            tags=["test", "verification"],
        )
        print(f"✓ Episode created: {episode}")

        print("\n" + "=" * 60)
        print("MEMORY SYSTEM FIXES TEST COMPLETE")
        print("✓ All imports working correctly")
        print("✓ Basic functionality verified")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_memory_fixes()
    sys.exit(0 if success else 1)
