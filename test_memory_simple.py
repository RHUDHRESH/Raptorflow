#!/usr/bin/env python3
"""
Simple test for memory components without package imports.
"""

import os
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))


def test_memory_simple():
    """Test memory components with simple imports."""
    print("=" * 60)
    print("SIMPLE MEMORY TEST")
    print("=" * 60)

    try:
        # Test models directly
        print("Testing models...")
        from memory.models import MemoryChunk, MemoryType

        print("✓ Models imported")

        # Test chunker
        print("Testing chunker...")
        from memory.chunker import ContentChunker

        chunker = ContentChunker()
        print("✓ ContentChunker imported")

        # Test graph models
        print("Testing graph models...")
        from memory.graph_models import EntityType, GraphEntity

        entity = GraphEntity(
            workspace_id="test", entity_type=EntityType.COMPANY, name="Test Entity"
        )
        print(f"✓ GraphEntity created: {entity}")

        # Test basic functionality
        print("\nTesting basic functionality...")

        # Test MemoryType
        types = MemoryType.get_all_types()
        print(f"✓ Memory types: {types}")

        # Test MemoryChunk
        chunk = MemoryChunk(
            workspace_id="test-workspace",
            memory_type=MemoryType.FOUNDATION,
            content="Test content",
        )
        print(f"✓ MemoryChunk created: {chunk}")

        # Test chunking
        chunks = chunker.chunk("This is a test content that should be chunked.")
        print(f"✓ Content chunked into {len(chunks)} pieces")

        print("\n" + "=" * 60)
        print("SIMPLE MEMORY TEST COMPLETE")
        print("✓ Basic components working")
        print("=" * 60)
        return True

    except Exception as e:
        print(f"\n✗ Test failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_memory_simple()
    sys.exit(0 if success else 1)
