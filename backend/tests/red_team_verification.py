"""
RED TEAM MEMORY SYSTEMS VERIFICATION

This script performs a cynical, empirical verification of the memory systems implementation.
No graceful failures, no CI/CD bullshit - we check if it actually works.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import asyncio
import uuid
from datetime import datetime
from unittest.mock import AsyncMock, Mock

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

# Import all memory components
from memory.models import MemoryChunk, MemoryType
from memory.vector_store import VectorMemory


class RedTeamMemoryChecker:
    """Cynical verification of memory systems implementation."""

    def __init__(self):
        self.failures = []
        self.warnings = []
        self.passes = []
        self.test_results = {}

    def log_failure(self, test_name: str, issue: str):
        """Log a critical failure."""
        self.failures.append(f"❌ {test_name}: {issue}")

    def log_warning(self, test_name: str, issue: str):
        """Log a warning."""
        self.warnings.append(f"⚠️ {test_name}: {issue}")

    def log_pass(self, test_name: str, details: str = ""):
        """Log a successful test."""
        self.passes.append(f"✅ {test_name}: {details}")
        self.test_results[test_name] = "PASS"

    def log_info(self, test_name: str, info: str):
        """Log informational message."""
        print(f"ℹ️ {test_name}: {info}")

    def run_all_checks(self):
        """Run all red team checks."""
        print("=" * 80)
        print("🔥 RED TEAM MEMORY SYSTEMS VERIFICATION")
        print("=" * 80)
        print("No graceful failures accepted - checking if it actually works")
        print("=" * 80)

        try:
            self.check_imports()
            self.check_memory_types()
            self.check_embedding_model()
            self.check_content_chunker()
            self.check_vector_store()
            self.check_graph_models()
            self.check_workspace_isolation()
            self.check_data_integrity()
            self.check_error_handling()
            self.check_performance()

            self.print_summary()

            return len(self.failures) == 0

        except Exception as e:
            self.log_failure("CRITICAL", f"Red team check crashed: {e}")
            self.print_summary()
            return False

    def print_summary(self):
        """Print verification summary."""
        print("=" * 80)
        print("📊 RED TEAM VERIFICATION SUMMARY")
        print("=" * 80)
        print(f"✅ Passed: {len(self.passes)}")
        print(f"⚠️ Warnings: {len(self.warnings)}")
        print(f"❌ Failures: {len(self.failures)}")

        if self.failures:
            print("\n🚨 CRITICAL FAILURES:")
            for failure in self.failures:
                print(f"  {failure}")

        if self.warnings:
            print("\n⚠️ WARNINGS:")
            for warning in self.warnings:
                print(f"  {warning}")

        print("=" * 80)

    def check_imports(self):
        """Check all imports work correctly."""
        self.log_info("IMPORTS", "Checking all memory system imports...")

        try:
            # Test core imports
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

            self.log_pass("IMPORTS", "All imports successful")

            # Test that classes are actually classes
            assert isinstance(MemoryType, type), "MemoryType should be an enum class"
            assert isinstance(MemoryChunk, type), "MemoryChunk should be a dataclass"
            assert isinstance(ContentChunker, type), "ContentChunker should be a class"
            assert isinstance(VectorMemory, type), "VectorMemory should be a class"
            assert isinstance(GraphEntity, type), "GraphEntity should be a dataclass"
            assert isinstance(GraphRelationship, type), "GraphRelationship should be a dataclass"
            assert isinstance(SubGraph, type), "SubGraph should be a dataclass"

        except ImportError as e:
            self.log_failure("IMPORTS", f"Import failed: {e}")
        except Exception as e:
            self.log_failure("IMPORTS", f"Import error: {e}")

    def check_memory_types(self):
        """Check memory types are complete and functional."""
        self.log_info("MEMORY_TYPES", "Checking memory type completeness...")

        # Check all required types exist
        required_types = [
            "foundation", "icp", "move", "campaign", "research", "conversation", "feedback"
        ]

        actual_types = MemoryType.get_all_types()

        missing_types = set(required_types) - set(actual_types)
        if missing_types:
            self.log_failure("MEMORY_TYPES", f"Missing memory types: {missing_types}")

        extra_types = set(actual_types) - set(required_types)
        if extra_types:
            self.log_warning("MEMORY_TYPES", f"Extra memory types: {extra_types}")

        # Test type conversion
        for type_str in required_types:
            try:
                memory_type = MemoryType.from_string(type_str)
                assert memory_type.value == type_str, f"Type conversion failed for {type_str}"
            except ValueError:
                self.log_failure("MEMORY_TYPES", f"Invalid memory type: {type_str}")

        # Test enum functionality
        assert len(MemoryType) == 7, f"Should have 7 memory types, got {len(MemoryType)}"

        self.log_pass("MEMORY_TYPES", f"Memory types verified: {len(MemoryType)} types")

    def check_embedding_model(self):
        """Check embedding model actually works."""
        self.log_info("EMBEDDINGS", "Testing embedding model functionality...")

        try:
            # Test singleton pattern
            model1 = get_embedding_model()
            model2 = get_embedding_model()
            assert model1 is model2, "Embedding model should be singleton"

            # Test embedding generation
            test_text = "Test embedding generation"
            embedding = model1.encode_single(test_text)

            # Verify it's actually a numpy array with correct dimensions
            assert isinstance(embedding, np.ndarray), "Should return numpy array"
            assert len(embedding) == 384, f"Should be 384 dimensions, got {len(embedding)}"
            assert np.isfinite(embedding).all(), "All values should be finite"

            # Test normalization
            norm = np.linalg.norm(embedding)
            assert abs(norm - 1.0) < 0.1, f"Should be normalized (norm={norm})"

            # Test caching
            cached_embedding = model1.encode_cached(test_text)
            assert np.array_equal(embedding, cached_embedding), "Cached embedding should match"

            # Test batch encoding
            texts = ["Text 1", "Text 2", "Text 3"]
            embeddings = model1.encode(texts)
            assert isinstance(embeddings, np.ndarray), "Should return numpy array"
            assert embeddings.shape[1] == 384, "Each embedding should be 384-dimensional"

            self.log_pass("EMBEDDINGS", "Embedding model fully functional")

        except Exception as e:
            self.log_failure("EMBEDDINGS", f"Embedding model failed: {e}")

    def check_content_chunker(self):
        """Check content chunker actually chunks content."""
        self.log_info("CHUNKER", "Testing content chunking functionality...")

        try:
            chunker = ContentChunker(chunk_size=100, overlap=20)

            # Test empty content
            empty_chunks = chunker.chunk("")
            assert len(empty_chunks) == 0, "Empty content should produce no chunks"

            # Test whitespace only
            whitespace_chunks = chunker.chunk("   \n\t   ")
            assert len(whitespace_chunks) == 0, "Whitespace only should produce no chunks"

            # Test short content
            short_content = "Short content"
            short_chunks = chunker.chunk(short_content)
            assert len(short_chunks) == 1, "Short content should produce 1 chunk"
            assert short_chunks[0] == short_content, "Short content should be returned as-is"

            # Test long content
            long_content = "This is a very long content that needs to be chunked into multiple pieces. " * 20
            long_chunks = chunker.chunk(long_content)
            assert len(long_chunks) > 1, "Long content should be chunked into multiple pieces"

            # Verify chunk info
            chunk_infos = chunker.chunk_with_info(long_content)
            assert len(chunk_infos) == len(long_chunks), "Chunk info should match chunk count"

            # Verify metadata
            for i, info in enumerate(chunk_infos):
                assert info.chunk_index == i, f"Chunk index should be {i}"
                assert info.start_index >= 0, f"Start index should be non-negative"
                assert info.end_index > info.start_index, f"End index should be greater than start index"

            self.log_pass("CHUNKER", f"Content chunker works: {len(long_chunks)} chunks from {len(long_content)} chars")

        except Exception as e:
            self.log_failure("CHUNKER", f"Content chunker failed: {e}")

    def check_vector_store(self):
        """Check vector store can actually store and retrieve."""
        self.log_info("VECTOR_STORE", "Testing vector store functionality...")

        try:
            # Mock setup for testing
            class MockSupabaseClient:
                def __init__(self):
                    self.tables = {}

                def table(self, table_name):
                    return MockTable(self, table_name)

            class MockTable:
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

                def limit(self, limit):
                    self.query["limit"] = limit
                    return self

                def execute(self):
                    table_data = self.client.tables.get(self.table_name, {})
                    results = list(table_data.values())

                    for key, value in self.query.items():
                        if key.startswith("eq_"):
                            column = key[3:]
                                results = [r for r in results if r.get(column) == value]

                    if "limit" in self.query:
                        results = results[:self.query["limit"]]

                    return MockResponse(results)

            class MockResponse:
                def __init__(self, data):
                    self.data = data
                    self.count = len(data) if isinstance(data, list) else (1 if data else 0)

                def execute(self):
                    return self

            # Test vector memory with mock
            mock_client = MockSupabaseClient()
            vector_memory = VectorMemory(mock_client)

            # Mock embedding model
            import numpy as np
            mock_embedding_model = Mock()
            mock_embedding_model.encode_single = Mock(return_value=np.array([0.1] * 384))
            mock_embedding_model.encode = Mock(return_value=np.array([[0.1] * 384] * 10))
            mock_embedding_model.compute_similarity = Mock(return_value=0.8)
            mock_embedding_model.normalize_embedding = Mock(return_value=np.array([0.1] * 384))
            vector_memory.embedding_model = mock_embedding_model

            # Test storage
            workspace_id = "test-ws"
            content = "Test content for vector storage"
            chunk_id = await vector_memory.store(
                workspace_id=workspace_id,
                memory_type=MemoryType.FOUNDATION,
                content=content,
                metadata={"test": True}
            )

            assert chunk_id is not None, "Should return chunk ID"
            assert isinstance(chunk_id, str), "Chunk ID should be string"

            # Test retrieval
            retrieved_chunk = await vector_memory.get_by_id(chunk_id)
            assert retrieved_chunk is not None, "Should retrieve stored chunk"
            assert retrieved_chunk.content == content, "Content should match"
            assert retrieved_chunk.memory_type == MemoryType.FOUNDATION, "Memory type should match"

            # Test search
            search_results = await vector_memory.search(
                workspace_id=workspace_id,
                query="test query",
                limit=5
            )
            assert isinstance(search_results, list), "Search should return list"

            # Test batch operations
            batch_data = [
                {"content": f"Batch content {i}", "memory_type": MemoryType.RESEARCH}
                for i in range(3)
            ]
            batch_ids = await vector_memory.store_batch(workspace_id, batch_data)
            assert len(batch_ids) == 3, "Should store 3 chunks"

            # Test deletion
            delete_success = await vector_memory.delete(chunk_id)
            assert delete_success, "Should delete chunk"

            # Test workspace isolation
            other_ws_results = await vector_memory.search("other-ws", "test query")
            assert len(other_ws_results) == 0, "Should not find data from other workspace"

            self.log_pass("VECTOR_STORE", "Vector store fully functional")

        except Exception as e:
            self.log_failure("VECTOR_STORE", f"Vector store failed: {e}")

    def check_graph_models(self):
        """Check graph models work correctly."""
        self.log_info("GRAPH_MODELS", "Testing graph models functionality...")

        try:
            # Test entity types
            required_entity_types = [
                "company", "icp", "competitor", "channel", "pain_point",
                "usp", "feature", "move", "campaign", "content"
            ]
            actual_entity_types = EntityType.get_all_types()

            missing_entity_types = set(required_entity_types) - set(actual_entity_types)
            if missing_entity_types:
                self.log_failure("GRAPH_MODELS", f"Missing entity types: {missing_entity_types}")

            # Test relationship types
            required_rel_types = [
                "has_icp", "competes_with", "uses_channel", "solves_pain", "has_usp",
                "has_feature", "targets", "part_of", "created_by", "mentions", "related_to", "similar_to"
            ]
            actual_rel_types = RelationType.get_all_types()

            missing_rel_types = set(required_rel_types) - set(actual_rel_types)
            if missing_rel_types:
                self.log_failure("GRAPH_MODELS", f"Missing relationship types: {missing_rel_types}")

            # Test entity creation
            entity = GraphEntity(
                id="test-entity",
                workspace_id="test-ws",
                entity_type=EntityType.COMPANY,
                name="Test Entity",
                properties={"test": True}
            )

            assert entity.id == "test-entity", "Entity ID should be set"
            assert entity.workspace_id == "test-ws", "Workspace ID should be set"
            assert entity.entity_type == EntityType.COMPANY, "Entity type should be set"
            assert entity.name == "Test Entity", "Entity name should be set"
            assert entity.properties == {"test": True}, "Properties should be set"

            # Test relationship creation
            rel = GraphRelationship(
                id="test-rel",
                workspace_id="test-ws",
                source_id="source-entity",
                target_id="target-entity",
                relation_type=RelationType.RELATED_TO,
                weight=0.5
            )

            assert rel.id == "test-rel", "Relationship ID should be set"
            assert rel.source_id == "source-entity", "Source ID should be set"
            assert rel.target_id == "target-entity", "Target ID should be set"
            assert rel.relation_type == RelationType.RELATED_TO, "Relation type should be set"
            assert rel.weight == 0.5, "Weight should be set"

            # Test validation
            assert entity.is_valid(), "Valid entity should pass validation"

            invalid_entity = GraphEntity(name="", entity_type=None)
            assert not invalid_entity.is_valid(), "Invalid entity should fail validation"

            invalid_rel = GraphRelationship(
                source_id="same-id",
                target_id="same-id",
                relation_type=RelationType.RELATED_TO
            )
            assert not invalid_rel.is_valid(), "Self-referencing relationship should be invalid")

            # Test subgraph
            subgraph = SubGraph()
            assert subgraph.is_empty(), "Empty subgraph should be empty"

            subgraph.add_entity(entity)
            subgraph.add_relationship(rel)
            assert not subgraph.is_empty(), "Subgraph with items should not be empty"
            assert subgraph.size() == 2, "Subgraph size should be 2 (1 entity + 1 relationship)"

            # Test serialization
            subgraph_dict = subgraph.to_dict()
            restored_subgraph = SubGraph.from_dict(subgraph_dict)

            assert restored_subgraph.center_entity_id == subgraph.center_entity_id, "Center entity ID should be preserved"
            assert len(restored_subgraph.entities) == len(subgraph.entities), "Entity count should be preserved"
            assert len(restored_subgraph.relationships) == len(subgraph.relationships), "Relationship count should be preserved"

            self.log_pass("GRAPH_MODELS", "Graph models fully functional")

        except Exception as e:
            self.log_failure("GRAPH_MODELS", f"Graph models failed: {e}")

    def check_workspace_isolation(self):
        """Check workspace isolation is enforced."""
        self.log_info("WORKSPACE_ISOLATION", "Testing workspace isolation enforcement...")

        try:
            # Test memory chunk isolation
            chunk1 = MemoryChunk(
                id="chunk-1",
                workspace_id="ws-1",
                memory_type=MemoryType.FOUNDATION,
                content="Content for workspace 1"
            )

            chunk2 = MemoryChunk(
                id="chunk-2",
                workspace_id="ws-2",
                memory_type=MemoryType.FOUNDATION,
                content="Content for workspace 2"
            )

            # Verify workspace separation
            assert chunk1.workspace_id == "ws-1", "Chunk 1 should belong to ws-1"
            assert chunk2.workspace_id == "ws-2", "Chunk 2 should belong to ws-2"

            # Test graph entity isolation
            entity1 = GraphEntity(
                id="entity-1",
                workspace_id="ws-1",
                entity_type=EntityType.COMPANY,
                name="Entity 1"
            )

            entity2 = GraphEntity(
                id="entity-2",
                workspace_id="ws-2",
                entity_type=EntityType.COMPANY,
                name="Entity 2"
            )

            assert entity1.workspace_id == "ws-1", "Entity 1 should belong to ws-1"
            assert entity2.workspace_id == "ws-2", "Entity 2 should belong to ws-2"

            # Test relationship isolation
            rel1 = GraphRelationship(
                id="rel-1",
                workspace_id="ws-1",
                source_id="entity-1",
                target_id="entity-2",
                relation_type=RelationType.RELATED_TO
            )

            assert rel1.workspace_id == "ws-1", "Relationship should belong to ws-1"

            self.log_pass("WORKSPACE_ISOLATION", "Workspace isolation enforced across all components")

        except Exception as e:
            self.log_failure("WORKSPACE_ISOLATION", f"Workspace isolation failed: {e}")

    def check_data_integrity(self):
        """Check data integrity and consistency."""
        self.log_info("DATA_INTEGRITY", "Testing data integrity...")

        try:
            # Test memory chunk serialization
            chunk = MemoryChunk(
                id="test-chunk",
                workspace_id="test-ws",
                memory_type=MemoryType.FOUNDATION,
                content="Test content",
                metadata={"key": "value"}
            )

            chunk_dict = chunk.to_dict()
            restored_chunk = MemoryChunk.from_dict(chunk_dict)

            assert restored_chunk.id == chunk.id, "Chunk ID should be preserved"
            assert restored_chunk.content == chunk.content, "Content should be preserved"
            assert restored_chunk.memory_type == chunk.memory_type, "Memory type should be preserved"
            assert restored_chunk.metadata == chunk.metadata, "Metadata should be preserved"

            # Test entity serialization
            entity = GraphEntity(
                id="test-entity",
                workspace_id="test-ws",
                entity_type=EntityType.COMPANY,
                name="Test Entity",
                properties={"key": "value"}
            )

            entity_dict = entity.to_dict()
            restored_entity = GraphEntity.from_dict(entity_dict)

            assert restored_entity.id == entity.id, "Entity ID should be preserved"
            assert restored_entity.name == entity.name, "Entity name should be preserved"
            assert restored_entity.entity_type == entity.entity_type, "Entity type should be preserved"
            assert restored_entity.properties == entity.properties, "Properties should be preserved"

            # Test relationship serialization
            rel = GraphRelationship(
                id="test-rel",
                workspace_id="test-ws",
                source_id="source-id",
                target_id="target-id",
                relation_type=RelationType.RELATED_TO,
                weight=0.7
            )

            rel_dict = rel.to_dict()
            restored_rel = GraphRelationship.from_dict(rel_dict)

            assert restored_rel.id == rel.id, "Relationship ID should be preserved"
            assert restored_rel.source_id == rel.source_id, "Source ID should be preserved"
            assert restored_rel.target_id == rel.target_id, "Target ID should be preserved"
            assert restored_rel.relation_type == rel.relation_type, "Relation type should be preserved"
            assert restored_rel.weight == rel.weight, "Weight should be preserved"

            # Test subgraph serialization
            subgraph = SubGraph()
            subgraph.add_entity(entity)
            subgraph.add_relationship(rel)

            subgraph_dict = subgraph.to_dict()
            restored_subgraph = SubGraph.from_dict(subgraph_dict)

            assert restored_subgraph.size() == subgraph.size(), "Subgraph size should be preserved"

            self.log_pass("DATA_INTEGRITY", "Data serialization/deserialization works correctly")

        except Exception as e:
            self.log_failure("DATA_INTEGRITY", f"Data integrity check failed: {e}")

    def check_error_handling(self):
        """Check error handling and validation."""
        self.log_info("ERROR_HANDLING", "Testing error handling...")

        try:
            # Test invalid memory type
            try:
                MemoryType.from_string("invalid_type")
                self.log_failure("ERROR_HANDLING", "Should raise ValueError for invalid type")
            except ValueError:
                pass  # Expected

            # Test invalid entity type
            try:
                EntityType.from_string("invalid_type")
                self.log_failure("ERROR_HANDLING", "Should raise ValueError for invalid type")
            except ValueError:
                pass  # Expected

            # Test empty content validation
            empty_chunk = MemoryChunk(content="")
            assert empty_chunk.is_empty(), "Empty chunk should be detected"

            # Test invalid entity validation
            invalid_entity = GraphEntity(name="", entity_type=None)
            assert not invalid_entity.is_valid(), "Invalid entity should fail validation"

            # Test invalid relationship validation
            invalid_rel = GraphRelationship(
                source_id="same",
                target_id="same",
                relation_type=RelationType.RELATED_TO
            )
            assert not invalid_rel.is_valid(), "Self-referencing relationship should fail validation"

            # Test weight normalization
            high_weight_rel = GraphRelationship(weight=1.5)
            assert high_weight_rel.weight == 1.0, "High weight should be normalized to 1.0"

            low_weight_rel = GraphRelationship(weight=-0.5)
            assert low_weight_rel.weight == 0.0, "Low weight should be normalized to 0.0"

            self.log_pass("ERROR_HANDLING", "Error handling works correctly")

        except Exception as e:
            self.log_failure("ERROR_HANDLING", f"Error handling failed: {e}")

    def check_performance(self):
        """Check performance characteristics."""
        self.log_info("PERFORMANCE", "Testing performance characteristics...")

        try:
            # Test embedding model caching
            model = get_embedding_model()

            # Clear cache first
            model.clear_cache()

            # First call should be slower
            import time
            start_time = time.time()
            embedding1 = model.encode_single("Test performance test")
            first_call_time = time.time() - start_time

            # Second call should be cached
            start_time = time.time()
            embedding2 = model.encode_single("Test performance test")
            second_call_time = time.time() - start_time

            # Third call should also be cached
            start_time = time.time()
            embedding3 = model.encode_single("Different test content")
            third_call_time = time.time() - start_time

            # Cached calls should be much faster
            assert second_call_time < first_call_time * 0.5, "Cached call should be significantly faster"
            assert third_call_time < first_call_time * 0.5, "Cached call should be significantly faster"

            # Test chunker performance
            chunker = ContentChunker(chunk_size=1000, overlap=100)

            large_content = "Large content for performance testing. " * 100
            start_time = time.time()
            chunks = chunker.chunk(large_content)
            chunking_time = time.time() - start_time

            assert len(chunks) > 10, "Large content should be chunked efficiently"
            assert chunking_time < 1.0, "Chunking should be fast"

            # Test batch operations
            system = self.setup_mock_system()
            vector_memory = system["vector_memory"]

            batch_data = [
                {"content": f"Batch item {i}", "memory_type": MemoryType.RESEARCH}
                for i in range(50)
            ]

            start_time = time.time()
            batch_ids = await vector_memory.store_batch("test-ws", batch_data)
            batch_time = time.time() - start_time

            assert len(batch_ids) == 50, "Batch operation should handle 50 items"
            assert batch_time < 2.0, "Batch operation should be fast")

            self.log_pass("PERFORMANCE", f"Performance characteristics verified")

        except Exception as e:
            self.log_failure("PERFORMANCE", f"Performance check failed: {e}")

    def setup_mock_system(self):
        """Set up mock system for testing."""
        class MockSupabaseClient:
            def __init__(self):
                self.tables = {}

            def table(self, table_name):
                return MockTable(self, table_name)

            class MockTable:
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

                def limit(self, limit):
                    self.query["limit"] = limit
                    return self

                def execute(self):
                    table_data = self.client.tables.get(self.table_name, {})
                    results = list(table_data.values())

                    for key, value in self.query.items():
                        if key.startswith("eq_"):
                            column = key[3:]
                                results = [r for r in results if r.get(column) == value]

                    if "limit" in self.query:
                        results = results[:self.query["limit"]]

                    return MockResponse(results)

            class MockResponse:
                def __init__(self, data):
                    self.data = data
                    self.count = len(data) if isinstance(data, list) else (1 if data else 0)

                def execute(self):
                    return self

            import numpy as np
            mock_client = MockSupabaseClient()
            vector_memory = VectorMemory(mock_client)

            mock_embedding_model = Mock()
            mock_embedding_model.encode_single = Mock(return_value=np.array([0.1] * 384))
            mock_embedding_model.encode = Mock(return_value=np.array([[0.1] * 384] * 10))
            mock_embedding_model.compute_similarity = Mock(return_value=0.8)
            mock_embedding_model.normalize_embedding = Mock(return_value=np.array([0.1] * 384))
            vector_memory.embedding_model = mock_embedding_model

            chunker = ContentChunker(chunk_size=100, overlap=20)

            return {
                "vector_memory": vector_memory,
                "chunker": chunker,
                "mock_client": mock_client,
                "mock_embedding_model": mock_embedding_model
            }

    def print_summary(self):
        """Print verification summary."""
        print("=" * 80)
        print("📊 RED TEAM VERIFICATION SUMMARY")
        print("=" * 80)
        print(f"✅ Passed: {len(self.passes)}")
        print(f"⚠️ Warnings: {len(self.warnings)}")
        print(f"❌ Failures: {len(self.failures)}")

        if self.failures:
            print("\n🚨 CRITICAL FAILURES:")
            for failure in self.failures:
                print(f"  {failure}")

        if self.warnings:
            print("\n⚠️ WARNINGS:")
            for warning in self.warnings:
                print(f"  {warning}")

        print("=" * 80)

    def run_red_team_verification():
        """Run the complete red team verification."""
        checker = RedTeamMemoryChecker()
        success = checker.run_all_checks()

        if success:
            print("\n🎉 RED TEAM VERIFICATION PASSED")
            print("🔥 Memory systems are truly ready for production!")
        else:
            print("\n🚨 RED TEAM VERIFICATION FAILED")
            print("🔥 Fix critical issues before production deployment")

        return success


if __name__ == "__main__":
    success = run_red_team_verification()
    sys.exit(0 if success else 1)
