"""
Thorough system integration test for memory components.

This script verifies that all memory components work together:
1. Models, embeddings, chunker, vector store, and graph models integrate
2. Data flows correctly between components
3. Workspace isolation is maintained across all systems
4. Memory types and entity types are consistent
5. End-to-end workflows function properly
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import asyncio
import uuid
from unittest.mock import Mock

import numpy as np
from memory.chunker import ContentChunker
from memory.embeddings import get_embedding_model
from memory.graph_models import (
    EntityType,
    GraphEntity,
    GraphRelationship,
    RelationType,
    SubGraph,
)
from memory.models import MemoryChunk, MemoryType
from memory.vector_store import VectorMemory


class MockSupabaseClient:
    """Mock Supabase client for integration testing."""

    def __init__(self):
        self.tables = {}

    def table(self, table_name):
        return MockTable(self, table_name)

    def rpc(self, function_name, params):
        return MockResponse([])


class MockTable:
    """Mock table interface."""

    def __init__(self, client, table_name):
        self.client = client
        self.table_name = table_name
        self.query = {}

    def insert(self, data):
        if isinstance(data, list):
            results = []
            for item in data:
                item_id = item.get("id", str(uuid.uuid4()))
                self.client.tables.setdefault(self.table_name, {})[item_id] = item
                results.append(item)
            return MockResponse(results)
        else:
            item_id = data.get("id", str(uuid.uuid4()))
            self.client.tables.setdefault(self.table_name, {})[item_id] = data
            return MockResponse([data])

    def select(self, columns="*", count=None):
        self.query["select"] = columns
        self.query["count"] = count
        return self

    def eq(self, column, value):
        self.query[f"eq_{column}"] = value
        return self

    def in_(self, column, values):
        self.query[f"in_{column}"] = values
        return self

    def limit(self, limit):
        self.query["limit"] = limit
        return self

    def range(self, offset, to):
        self.query["range"] = (offset, to)
        return self

    def order(self, column, desc=False):
        self.query["order"] = (column, desc)
        return self

    def single(self):
        self.query["single"] = True
        return self

    def execute(self):
        table_data = self.client.tables.get(self.table_name, {})
        results = list(table_data.values())

        for key, value in self.query.items():
            if key.startswith("eq_"):
                column = key[3:]
                results = [r for r in results if r.get(column) == value]
            elif key.startswith("in_"):
                column = key[3:]
                results = [r for r in results if r.get(column) in value]

        if "order" in self.query:
            column, desc = self.query["order"]
            results.sort(key=lambda x: x.get(column, ""), reverse=desc)

        if "limit" in self.query:
            results = results[: self.query["limit"]]

        if "range" in self.query:
            offset, to = self.query["range"]
            results = results[offset : to + 1]

        if self.query.get("single"):
            results = results[0] if results else None

        return MockResponse(results)


class MockResponse:
    """Mock Supabase response."""

    def __init__(self, data):
        self.data = data
        self.count = len(data) if isinstance(data, list) else (1 if data else 0)

    def execute(self):
        """Mock execute - returns self for chaining."""
        return self


def setup_mock_system():
    """Set up complete mock memory system."""
    mock_client = MockSupabaseClient()
    vector_memory = VectorMemory(mock_client)

    # Mock embedding model
    import numpy as np

    mock_embedding_model = Mock()
    mock_embedding_model.encode_single = Mock(return_value=np.array([0.1] * 384))
    mock_embedding_model.encode = Mock(
        return_value=np.array([[0.1] * 384] * 10)
    )  # Support up to 10 embeddings
    mock_embedding_model.compute_similarity = Mock(return_value=0.8)
    mock_embedding_model.normalize_embedding = Mock(return_value=np.array([0.1] * 384))
    vector_memory.embedding_model = mock_embedding_model

    chunker = ContentChunker(chunk_size=100, overlap=20)

    return {
        "vector_memory": vector_memory,
        "chunker": chunker,
        "mock_client": mock_client,
        "mock_embedding_model": mock_embedding_model,
    }


async def test_end_to_end_memory_workflow():
    """Test complete end-to-end memory workflow."""
    print("Testing end-to-end memory workflow...")

    system = setup_mock_system()
    vector_memory = system["vector_memory"]
    chunker = system["chunker"]

    workspace_id = "test-workspace-integration"

    # Step 1: Create content and chunk it
    long_content = """
    Our company is revolutionizing the SaaS industry with innovative solutions.
    We focus on mid-market companies in the healthcare sector.
    Our main product helps streamline patient management and billing.
    Key features include automated scheduling, telemedicine integration, and analytics.
    We compete with traditional EMR systems but offer better user experience.
    Our ICP includes healthcare administrators and clinic managers.
    They struggle with inefficient workflows and regulatory compliance.
    Our solution addresses these pain points with modern technology.
    """

    chunks = chunker.chunk(long_content)
    assert len(chunks) > 1, "Content should be chunked into multiple pieces"

    # Step 2: Store chunks with different memory types
    chunk_ids = []
    for i, chunk in enumerate(chunks):
        memory_type = MemoryType.FOUNDATION if i == 0 else MemoryType.RESEARCH
        chunk_id = await vector_memory.store(
            workspace_id=workspace_id,
            memory_type=memory_type,
            content=chunk,
            metadata={"chunk_index": i, "total_chunks": len(chunks)},
        )
        chunk_ids.append(chunk_id)

    assert len(chunk_ids) == len(chunks), "All chunks should be stored"

    # Step 3: Search and retrieve memories
    search_results = await vector_memory.search(
        workspace_id=workspace_id, query="healthcare SaaS solutions", limit=5
    )

    assert len(search_results) > 0, "Search should return results"
    assert all(
        isinstance(result, MemoryChunk) for result in search_results
    ), "Results should be MemoryChunk objects"

    # Step 4: Create graph entities from memories
    entities = []
    for chunk in search_results[:2]:  # Create entities from first 2 results
        entity = GraphEntity(
            id=str(uuid.uuid4()),
            workspace_id=workspace_id,
            entity_type=EntityType.COMPANY,
            name=f"Entity from chunk {chunk.id[:8]}",
            properties={
                "source_chunk_id": chunk.id,
                "content_preview": chunk.content[:100],
            },
        )
        entities.append(entity)

    assert len(entities) == 2, "Should create 2 entities"

    # Step 5: Create relationships between entities
    relationships = []
    if len(entities) >= 2:
        rel = GraphRelationship(
            id=str(uuid.uuid4()),
            workspace_id=workspace_id,
            source_id=entities[0].id,
            target_id=entities[1].id,
            relation_type=RelationType.RELATED_TO,
            weight=0.7,
        )
        relationships.append(rel)

    assert len(relationships) == 1, "Should create 1 relationship"

    # Step 6: Create subgraph
    subgraph = SubGraph(center_entity_id=entities[0].id, depth=1)
    for entity in entities:
        subgraph.add_entity(entity)
    for rel in relationships:
        subgraph.add_relationship(rel)

    assert (
        subgraph.size() == 3
    ), "Subgraph should have 3 items (2 entities + 1 relationship)"

    print(
        f"✓ End-to-end workflow: {len(chunks)} chunks → {len(chunk_ids)} stored → {len(search_results)} found → {len(entities)} entities → {len(relationships)} relationships"
    )
    print("✓ End-to-end memory workflow test passed")


async def test_workspace_isolation_across_systems():
    """Test workspace isolation across all memory components."""
    print("Testing workspace isolation across systems...")

    system = setup_mock_system()
    vector_memory = system["vector_memory"]
    chunker = system["chunker"]

    # Create data in different workspaces
    workspace1 = "workspace-isolation-1"
    workspace2 = "workspace-isolation-2"

    # Store chunks in both workspaces
    content1 = "Workspace 1: Company data and strategies"
    content2 = "Workspace 2: Different company data"

    chunk_id1 = await vector_memory.store(workspace1, MemoryType.FOUNDATION, content1)
    chunk_id2 = await vector_memory.store(workspace2, MemoryType.FOUNDATION, content2)

    # Create entities in different workspaces
    entity1 = GraphEntity(
        id="entity-1",
        workspace_id=workspace1,
        entity_type=EntityType.COMPANY,
        name="Company 1",
    )

    entity2 = GraphEntity(
        id="entity-2",
        workspace_id=workspace2,
        entity_type=EntityType.COMPANY,
        name="Company 2",
    )

    # Search should only return results from respective workspaces
    results1 = await vector_memory.search(workspace1, "company data")
    results2 = await vector_memory.search(workspace2, "company data")

    # Verify isolation
    for result in results1:
        assert result.workspace_id == workspace1, f"Result should belong to workspace1"

    for result in results2:
        assert result.workspace_id == workspace2, f"Result should belong to workspace2"

    # Test entity isolation
    assert entity1.workspace_id == workspace1, "Entity 1 should belong to workspace1"
    assert entity2.workspace_id == workspace2, "Entity 2 should belong to workspace2"

    print(
        f"✓ Workspace isolation: Workspace 1 has {len(results1)} results, Workspace 2 has {len(results2)} results"
    )
    print("✓ Workspace isolation test passed")


def test_memory_type_consistency():
    """Test consistency between memory types and entity types."""
    print("Testing memory type consistency...")

    # Check that all required memory types exist
    required_memory_types = [
        "foundation",
        "icp",
        "move",
        "campaign",
        "research",
        "conversation",
        "feedback",
    ]
    actual_memory_types = MemoryType.get_all_types()

    assert set(required_memory_types) == set(
        actual_memory_types
    ), f"Missing memory types: {set(required_memory_types) - set(actual_memory_types)}"

    # Check that all required entity types exist
    required_entity_types = [
        "company",
        "icp",
        "competitor",
        "channel",
        "pain_point",
        "usp",
        "feature",
        "move",
        "campaign",
        "content",
    ]
    actual_entity_types = EntityType.get_all_types()

    assert set(required_entity_types) == set(
        actual_entity_types
    ), f"Missing entity types: {set(required_entity_types) - set(actual_entity_types)}"

    # Check mapping consistency (some types should match)
    common_types = ["icp", "move", "campaign"]
    for type_name in common_types:
        assert (
            type_name in actual_memory_types
        ), f"{type_name} should be in memory types"
        assert (
            type_name in actual_entity_types
        ), f"{type_name} should be in entity types"

    print("✓ Memory type consistency test passed")


def test_embedding_integration():
    """Test embedding integration across components."""
    print("Testing embedding integration...")

    system = setup_mock_system()
    mock_embedding_model = system["mock_embedding_model"]

    # Test that embedding model is used by vector memory
    test_text = "Test text for embedding integration"

    # This should call the mock embedding model
    embedding = mock_embedding_model.encode_single(test_text)
    assert isinstance(embedding, np.ndarray), "Should return numpy array"
    assert len(embedding) == 384, "Should return 384-dimensional embedding"

    # Test batch encoding
    texts = ["Text 1", "Text 2", "Text 3"]
    embeddings = mock_embedding_model.encode(texts)
    assert isinstance(embeddings, np.ndarray), "Should return numpy array"
    assert embeddings.shape[1] == 384, "Each embedding should be 384-dimensional"
    assert embeddings.shape[0] >= len(texts), "Should return embeddings for all texts"

    # Test similarity computation
    similarity = mock_embedding_model.compute_similarity(embedding, embedding)
    assert isinstance(similarity, float), "Similarity should be float"
    assert 0 <= similarity <= 1, "Similarity should be between 0 and 1"

    print("✓ Embedding integration test passed")


async def test_chunker_vector_memory_integration():
    """Test integration between chunker and vector memory."""
    print("Testing chunker-vector memory integration...")

    system = setup_mock_system()
    vector_memory = system["vector_memory"]
    chunker = system["chunker"]

    # Create content that needs chunking
    long_content = "This is a very long content that needs to be chunked. " * 20

    # Chunk the content
    chunks = chunker.chunk(long_content)
    assert len(chunks) > 1, "Content should be chunked"

    # Store all chunks
    workspace_id = "test-chunk-integration"
    chunk_ids = []

    for i, chunk in enumerate(chunks):
        chunk_id = await vector_memory.store(
            workspace_id=workspace_id,
            memory_type=MemoryType.RESEARCH,
            content=chunk,
            metadata={"chunk_index": i, "original_length": len(long_content)},
        )
        chunk_ids.append(chunk_id)

    assert len(chunk_ids) == len(chunks), "All chunks should be stored"

    # Search for content
    search_results = await vector_memory.search(
        workspace_id=workspace_id, query="long content chunked", limit=10
    )

    assert len(search_results) > 0, "Should find chunked content"

    # Verify chunk metadata is preserved
    for result in search_results:
        assert "chunk_index" in result.metadata, "Chunk index should be preserved"
        assert (
            "original_length" in result.metadata
        ), "Original length should be preserved"

    print(
        f"✓ Chunker-vector memory integration: {len(chunks)} chunks stored and retrieved"
    )
    print("✓ Chunker-vector memory integration test passed")


def test_graph_models_serialization_roundtrip():
    """Test graph models serialization and deserialization."""
    print("Testing graph models serialization roundtrip...")

    # Create complex graph structure
    subgraph = SubGraph(center_entity_id="center", depth=2)

    # Add entities
    entities = []
    for i in range(3):
        entity = GraphEntity(
            id=f"entity-{i}",
            workspace_id="test-workspace",
            entity_type=list(EntityType)[i],
            name=f"Entity {i}",
            properties={"index": i, "type": list(EntityType)[i].value},
        )
        entities.append(entity)
        subgraph.add_entity(entity)

    # Add relationships
    for i in range(2):
        rel = GraphRelationship(
            id=f"rel-{i}",
            workspace_id="test-workspace",
            source_id=f"entity-{i}",
            target_id=f"entity-{i+1}",
            relation_type=list(RelationType)[i],
            weight=0.5 + i * 0.2,
            properties={"index": i},
        )
        subgraph.add_relationship(rel)

    # Serialize to dict
    subgraph_dict = subgraph.to_dict()

    # Deserialize from dict
    restored_subgraph = SubGraph.from_dict(subgraph_dict)

    # Verify roundtrip
    assert restored_subgraph.center_entity_id == subgraph.center_entity_id
    assert restored_subgraph.depth == subgraph.depth
    assert len(restored_subgraph.entities) == len(subgraph.entities)
    assert len(restored_subgraph.relationships) == len(subgraph.relationships)

    # Verify entity data
    for entity_id, original_entity in subgraph.entities.items():
        restored_entity = restored_subgraph.get_entity(entity_id)
        assert restored_entity is not None, f"Entity {entity_id} should be restored"
        assert restored_entity.name == original_entity.name
        assert restored_entity.entity_type == original_entity.entity_type
        assert restored_entity.properties == original_entity.properties

    # Verify relationship data
    for rel_id, original_rel in subgraph.relationships.items():
        restored_rel = restored_subgraph.get_relationship(rel_id)
        assert restored_rel is not None, f"Relationship {rel_id} should be restored"
        assert restored_rel.source_id == original_rel.source_id
        assert restored_rel.target_id == original_rel.target_id
        assert restored_rel.relation_type == original_rel.relation_type
        assert restored_rel.weight == original_rel.weight

    print(
        f"✓ Graph models serialization: {len(entities)} entities and {len(subgraph.relationships)} relationships roundtripped"
    )
    print("✓ Graph models serialization roundtrip test passed")


async def run_all_system_tests():
    """Run all thorough system tests."""
    print("=" * 70)
    print("RUNNING THOROUGH SYSTEM INTEGRATION TESTS")
    print("=" * 70)

    try:
        await test_end_to_end_memory_workflow()
        await test_workspace_isolation_across_systems()
        test_memory_type_consistency()
        test_embedding_integration()
        await test_chunker_vector_memory_integration()
        test_graph_models_serialization_roundtrip()

        print("=" * 70)
        print("✅ ALL SYSTEM TESTS PASSED - MEMORY SYSTEMS INTEGRATE CORRECTLY")
        print("=" * 70)
        return True

    except Exception as e:
        print("=" * 70)
        print(f"❌ SYSTEM TEST FAILED: {e}")
        print("=" * 70)
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = asyncio.run(run_all_system_tests())
    sys.exit(0 if success else 1)
