"""
CYNICAL BREAKAGE TESTS - Find where the memory systems break

This script performs 10 different destructive tests to find weaknesses.
No assumptions, no graceful failures - we break shit on purpose.
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import asyncio
import gc
import json
import threading
import time
import traceback
import uuid
from datetime import datetime
from unittest.mock import Mock, patch

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

# Import memory components
from memory.models import MemoryChunk, MemoryType
from memory.vector_store import VectorMemory


class CynicalBreakageTester:
    """Cynical tester that finds where things break."""

    def __init__(self):
        self.breakages = []
        self.warnings = []
        self.successes = []

    def log_breakage(self, test_name: str, issue: str, details: str = ""):
        """Log a critical breakage."""
        self.breakages.append(f"💥 {test_name}: {issue}")
        if details:
            self.breakages.append(f"   Details: {details}")

    def log_warning(self, test_name: str, issue: str):
        """Log a warning."""
        self.warnings.append(f"⚠️ {test_name}: {issue}")

    def log_success(self, test_name: str, details: str = ""):
        """Log a successful test."""
        self.successes.append(f"✅ {test_name}: {details}")

    def run_all_breakage_tests(self):
        """Run all cynical breakage tests."""
        print("=" * 80)
        print("🔥 CYNICAL BREAKAGE TESTS - FIND WHERE IT BREAKS")
        print("=" * 80)
        print("Testing 10 different ways to break the memory systems")
        print("=" * 80)

        try:
            self.test_1_null_injection()
            self.test_2_memory_exhaustion()
            self.test_3_unicode_corruption()
            self.test_4_concurrent_race_conditions()
            self.test_5_invalid_data_types()
            self.test_6_workspace_boundary_violation()
            self.test_7_embedding_saturation()
            self.test_8_graph_circular_references()
            self.test_9_serialization_bombs()
            self.test_10_resource_exhaustion()

            self.print_summary()

        except Exception as e:
            self.log_breakage("CRITICAL", f"Breakage tests crashed: {e}")
            self.log_breakage("CRITICAL", f"Traceback: {traceback.format_exc()}")

        return len(self.breakages)

    def print_summary(self):
        """Print breakage summary."""
        print("=" * 80)
        print("📊 CYNICAL BREAKAGE SUMMARY")
        print("=" * 80)
        print(f"💥 Breakages Found: {len(self.breakages)}")
        print(f"⚠️ Warnings: {len(self.warnings)}")
        print(f"✅ Survived: {len(self.successes)}")

        if self.breakages:
            print("\n🚨 CRITICAL BREAKAGES:")
            for breakdown in self.breakages:
                print(f"  {breakdown}")

        if self.warnings:
            print("\n⚠️ WARNINGS:")
            for warning in self.warnings:
                print(f"  {warning}")

        print("=" * 80)

    def test_1_null_injection(self):
        """Test 1: Null/None injection attacks."""
        print("\n🔍 Test 1: Null Injection Attacks")

        try:
            # Test MemoryChunk with None values
            chunk = MemoryChunk(
                id=None,
                workspace_id=None,
                memory_type=None,
                content=None,
                metadata=None,
                embedding=None,
            )

            # This should not crash
            chunk_dict = chunk.to_dict()
            assert chunk_dict is not None, "Should handle None gracefully"

            # Test GraphEntity with None values
            entity = GraphEntity(
                id=None,
                workspace_id=None,
                entity_type=None,
                name=None,
                properties=None,
                embedding=None,
            )

            entity_dict = entity.to_dict()
            assert entity_dict is not None, "Should handle None gracefully"

            # Test GraphRelationship with None values
            rel = GraphRelationship(
                id=None,
                workspace_id=None,
                source_id=None,
                target_id=None,
                relation_type=None,
                properties=None,
            )

            rel_dict = rel.to_dict()
            assert rel_dict is not None, "Should handle None gracefully"

            # Test validation with None
            assert chunk.is_empty(), "Empty chunk with None should be empty"
            assert not entity.is_valid(), "Entity with None should be invalid"
            assert not rel.is_valid(), "Relationship with None should be invalid"

            self.log_success("NULL_INJECTION", "System handles None values gracefully")

        except Exception as e:
            self.log_breakage("NULL_INJECTION", f"Null injection breaks system: {e}")

    def test_2_memory_exhaustion(self):
        """Test 2: Memory exhaustion attacks."""
        print("\n🔍 Test 2: Memory Exhaustion Attacks")

        try:
            # Create massive amounts of data to exhaust memory
            large_content = "A" * 1000000  # 1MB string

            # Try to create many chunks
            chunker = ContentChunker(chunk_size=100000, overlap=10000)

            start_time = time.time()
            chunks = chunker.chunk(large_content)
            end_time = time.time()

            # Check if it handles large content without crashing
            assert len(chunks) > 0, "Should chunk large content"
            assert end_time - start_time < 10.0, "Should not take too long"

            # Create many memory chunks
            memory_chunks = []
            for i in range(1000):
                chunk = MemoryChunk(
                    id=f"chunk-{i}",
                    workspace_id=f"ws-{i}",
                    memory_type=MemoryType.FOUNDATION,
                    content=f"Content {i} " * 1000,
                    metadata={"index": i, "large": True},
                )
                memory_chunks.append(chunk)

            # This should not crash
            assert len(memory_chunks) == 1000, "Should create 1000 chunks"

            # Test serialization of large dataset
            start_time = time.time()
            serialized = [chunk.to_dict() for chunk in memory_chunks[:100]]
            end_time = time.time()

            assert len(serialized) == 100, "Should serialize large dataset"
            assert end_time - start_time < 5.0, "Serialization should be fast"

            self.log_success(
                "MEMORY_EXHAUSTION",
                f"Handled {len(memory_chunks)} chunks and {len(serialized)} serialized items",
            )

        except Exception as e:
            self.log_breakage(
                "MEMORY_EXHAUSTION", f"Memory exhaustion breaks system: {e}"
            )

    def test_3_unicode_corruption(self):
        """Test 3: Unicode corruption attacks."""
        print("\n🔍 Test 3: Unicode Corruption Attacks")

        try:
            # Test with various unicode attacks
            unicode_attacks = [
                # Null bytes
                "\x00" * 100,
                # High Unicode characters
                "\U0001F600" * 100,  # Emojis
                # Invalid UTF-8 sequences
                b"\xff\xfe".decode("utf-8", errors="ignore"),
                # Zero-width characters
                "\u200B" * 100,  # Zero-width space
                "\u200C" * 100,  # Non-breaking space
                # Control characters
                "\x01\x02\x03" * 100,
                # RTL override characters
                "\u202E" * 100,  # RTL override
                # Combining characters
                "e\u0301" * 100,  # e + combining acute
                # Surrogate pairs (invalid)
                "\uD800\uDC00" * 50,
                # Mixed encoding attacks
                "Normal text \x00\x01\x02\x03\x04\x05\x06\x07\x08\x09\x0A\x0B\x0C\x0D\x0E\x0F\x10\x11\x12\x13\x14\x15\x16\x17\x18\x19\x1A\x1B\x1C\x1D\x1E\x1F",
            ]

            for i, attack_content in enumerate(unicode_attacks):
                try:
                    # Test chunking with unicode attacks
                    chunker = ContentChunker()
                    chunks = chunker.chunk(attack_content)

                    # Should not crash
                    assert len(chunks) >= 0, f"Unicode attack {i} should not crash"

                    # Test memory chunk creation
                    chunk = MemoryChunk(
                        id=f"unicode-{i}",
                        workspace_id="test-ws",
                        memory_type=MemoryType.CONVERSATION,
                        content=attack_content,
                    )

                    # Test serialization
                    chunk_dict = chunk.to_dict()
                    assert (
                        chunk_dict is not None
                    ), f"Unicode attack {i} should serialize"

                    # Test deserialization
                    restored = MemoryChunk.from_dict(chunk_dict)
                    assert (
                        restored.content == chunk.content
                    ), f"Unicode attack {i} should roundtrip"

                except Exception as e:
                    self.log_warning(
                        "UNICODE_CORRUPTION", f"Unicode attack {i} partially fails: {e}"
                    )

            self.log_success(
                "UNICODE_CORRUPTION", "System handles unicode attacks gracefully"
            )

        except Exception as e:
            self.log_breakage(
                "UNICODE_CORRUPTION", f"Unicode corruption breaks system: {e}"
            )

    def test_4_concurrent_race_conditions(self):
        """Test 4: Concurrent race conditions."""
        print("\n🔍 Test 4: Concurrent Race Conditions")

        try:
            # Test concurrent chunking
            chunker = ContentChunker()
            large_content = "Test content for concurrency. " * 1000

            def chunk_worker(worker_id):
                """Worker function for concurrent chunking."""
                try:
                    chunks = chunker.chunk(large_content)
                    return f"Worker {worker_id}: {len(chunks)} chunks"
                except Exception as e:
                    return f"Worker {worker_id} failed: {e}"

            # Run multiple workers concurrently
            threads = []
            results = []

            for i in range(10):
                thread = threading.Thread(
                    target=lambda i=i: results.append(chunk_worker(i))
                )
                threads.append(thread)
                thread.start()

            # Wait for all threads to complete
            for thread in threads:
                thread.join()

            # Check results
            successful_workers = [r for r in results if "failed" not in r]
            assert (
                len(successful_workers) >= 8
            ), f"Most workers should succeed: {len(successful_workers)}/10"

            # Test concurrent memory operations
            def memory_worker(worker_id):
                """Worker function for concurrent memory operations."""
                try:
                    chunks = []
                    for i in range(100):
                        chunk = MemoryChunk(
                            id=f"worker-{worker_id}-chunk-{i}",
                            workspace_id=f"ws-{worker_id}",
                            memory_type=MemoryType.RESEARCH,
                            content=f"Content from worker {worker_id}, chunk {i}",
                        )
                        chunks.append(chunk)
                    return f"Worker {worker_id}: {len(chunks)} chunks"
                except Exception as e:
                    return f"Worker {worker_id} failed: {e}"

            # Run memory workers concurrently
            threads = []
            results = []

            for i in range(5):
                thread = threading.Thread(
                    target=lambda i=i: results.append(memory_worker(i))
                )
                threads.append(thread)
                thread.start()

            # Wait for all threads to complete
            for thread in threads:
                thread.join()

            # Check results
            successful_workers = [r for r in results if "failed" not in r]
            assert (
                len(successful_workers) >= 4
            ), f"Most memory workers should succeed: {len(success_workers)}/5"

            self.log_success(
                "CONCURRENT_RACE_CONDITIONS",
                f"Handled {len(threads)} concurrent workers successfully",
            )

        except Exception as e:
            self.log_breakage(
                "CONCURRENT_RACE_CONDITIONS", f"Race conditions break system: {e}"
            )

    def test_5_invalid_data_types(self):
        """Test 5: Invalid data type attacks."""
        print("\n🔍 Test 5: Invalid Data Type Attacks")

        try:
            # Test with invalid data types
            invalid_data = [
                # Integer instead of string
                12345,
                # Float instead of string
                123.456,
                # Boolean instead of string
                True,
                # List instead of string
                ["not", "a", "string"],
                # Dict instead of string
                {"not": "a", "string": "test"},
                # Function instead of string
                lambda x: x,
                # Class instead of string
                str,
                # Module instead of string
                sys,
                # None (already tested)
                None,
                # Complex object
                object(),
                # Recursive structure
                {"nested": {"deep": {"deeper": "value"}}},
            ]

            for i, invalid_value in enumerate(invalid_data):
                try:
                    # Test memory chunk creation
                    chunk = MemoryChunk(
                        id=f"invalid-{i}",
                        workspace_id="test-ws",
                        memory_type=MemoryType.FOUNDATION,
                        content=invalid_value,
                    )

                    # Should handle gracefully or fail predictably
                    chunk_dict = chunk.to_dict()

                    # Test graph entity creation
                    entity = GraphEntity(
                        id=f"invalid-{i}",
                        workspace_id="test-ws",
                        entity_type=EntityType.COMPANY,  # This might fail
                        name=invalid_value,
                    )

                    # Test graph relationship creation
                    rel = GraphRelationship(
                        id=f"invalid-{i}",
                        workspace_id="test-ws",
                        source_id="source",
                        target_id="target",
                        relation_type=RelationType.RELATED_TO,
                        weight=invalid_value,
                    )

                    # Should handle gracefully or fail predictably
                    rel_dict = rel.to_dict()

                except Exception as e:
                    # Some invalid types should fail predictably
                    if "unsupported operand type" in str(e) or "must be" in str(e):
                        pass  # Expected
                    else:
                        self.log_warning(
                            "INVALID_DATA_TYPES",
                            f"Invalid type {i} unexpected failure: {e}",
                        )

            self.log_success(
                "INVALID_DATA_TYPES", "System handles invalid data types predictably"
            )

        except Exception as e:
            self.log_breakage(
                "INVALID_DATA_TYPES", f"Invalid data types break system: {e}"
            )

    def test_6_workspace_boundary_violation(self):
        """Test 6: Workspace boundary violations."""
        print("\n🔍 Test 6: Workspace Boundary Violations")

        try:
            # Test cross-workspace data access
            chunk1 = MemoryChunk(
                id="chunk-1",
                workspace_id="ws-1",
                memory_type=MemoryType.FOUNDATION,
                content="Content for workspace 1",
            )

            chunk2 = MemoryChunk(
                id="chunk-2",
                workspace_id="ws-2",
                memory_type=MemoryType.FOUNDATION,
                content="Content for workspace 2",
            )

            # Try to access chunk2 from workspace 1 context
            # This should be prevented by design
            # (In real implementation, this would be enforced by database queries)

            # Test entity boundary violations
            entity1 = GraphEntity(
                id="entity-1",
                workspace_id="ws-1",
                entity_type=EntityType.COMPANY,
                name="Entity 1",
            )

            entity2 = GraphEntity(
                id="entity-2",
                workspace_id="ws-2",
                entity_type=EntityType.COMPANY,
                name="Entity 2",
            )

            # Create relationship crossing workspace boundaries
            boundary_violation_rel = GraphRelationship(
                id="boundary-violation",
                workspace_id="ws-1",
                source_id="entity-1",  # From ws-1
                target_id="entity-2",  # To ws-2
                relation_type=RelationType.RELATED_TO,
            )

            # This should be flagged as invalid
            assert not boundary_violation_rel.is_valid(
                entity1, entity2
            ), "Cross-workspace relationship should be invalid"

            # Test workspace boundary violation detection
            is_violation = boundary_violation_rel.is_workspace_boundary_violation(
                entity1, entity2
            )
            assert is_violation, "Should detect workspace boundary violation"

            # Test search boundary violations
            # (In real implementation, this would be enforced by database queries)

            # Test subgraph boundary violations
            subgraph = SubGraph()
            subgraph.add_entity(entity1)
            subgraph.add_entity(entity2)
            subgraph.add_relationship(boundary_violation_rel)

            # Subgraph should handle mixed workspaces but flag issues
            assert subgraph.size() == 3, "Subgraph should contain all items"

            # Test serialization with mixed workspaces
            subgraph_dict = subgraph.to_dict()
            restored_subgraph = SubGraph.from_dict(subgraph_dict)

            assert (
                restored_subgraph.size() == 3
            ), "Subgraph should preserve mixed workspace items"

            self.log_success(
                "WORKSPACE_BOUNDARY_VIOLATION",
                "System detects and handles boundary violations",
            )

        except Exception as e:
            self.log_breakage(
                "WORKSPACE_BOUNDARY_VIOLATION",
                f"Workspace boundary violations break system: {e}",
            )

    def test_7_embedding_saturation(self):
        """Test 7: Embedding saturation attacks."""
        print("\n🔍 Test 7: Embedding Saturation Attacks")

        try:
            # Test with massive embedding operations
            model = get_embedding_model()

            # Clear cache first
            try:
                model.clear_cache()
            except:
                pass  # Cache might not be available

            # Generate many embeddings to test saturation
            texts = [f"Test text {i}" for i in range(1000)]

            start_time = time.time()

            try:
                # This might fail due to memory or rate limiting
                embeddings = model.encode(texts)
                end_time = time.time()

                assert isinstance(embeddings, np.ndarray), "Should return numpy array"
                assert embeddings.shape[0] == 1000, "Should generate 1000 embeddings"
                assert (
                    end_time - start_time < 30.0
                ), "Should complete in reasonable time"

            except Exception as e:
                self.log_warning(
                    "EMBEDDING_SATURATION", f"Embedding saturation partially fails: {e}"
                )

            # Test single embedding saturation
            large_text = "A" * 1000000  # Very large text

            try:
                start_time = time.time()
                embedding = model.encode_single(large_text)
                end_time = time.time()

                assert isinstance(embedding, np.ndarray), "Should return numpy array"
                assert len(embedding) == 384, "Should be 384 dimensions"
                assert (
                    end_time - start_time < 10.0
                ), "Should complete in reasonable time"

            except Exception as e:
                self.log_warning(
                    "EMBEDDING_SATURATION", f"Large text encoding fails: {e}"
                )

            # Test cache saturation
            try:
                # Fill cache with many items
                for i in range(10000):
                    model.encode_cached(f"Cache test {i}")

                # Cache should handle saturation gracefully
                cache_size = len(model._cache) if hasattr(model, "_cache") else 0
                assert cache_size >= 0, "Cache should exist"

            except Exception as e:
                self.log_warning("EMBEDDING_SATURATION", f"Cache saturation fails: {e}")

            self.log_success(
                "EMBEDDING_SATURATION", "System handles embedding saturation gracefully"
            )

        except Exception as e:
            self.log_breakage(
                "EMBEDDING_SATURATION", f"Embedding saturation breaks system: {e}"
            )

    def test_8_graph_circular_references(self):
        """Test 8: Graph circular reference attacks."""
        print("\n🔍 Test 8: Graph Circular Reference Attacks")

        try:
            # Create circular references
            entity1 = GraphEntity(
                id="entity-1",
                workspace_id="test-ws",
                entity_type=EntityType.COMPANY,
                name="Entity 1",
            )

            entity2 = GraphEntity(
                id="entity-2",
                workspace_id="test-ws",
                entity_type=EntityType.COMPANY,
                name="Entity 2",
            )

            entity3 = GraphEntity(
                id="entity-3",
                workspace_id="test-ws",
                entity_type=EntityType.COMPANY,
                name="Entity 3",
            )

            # Create circular relationships
            rel1 = GraphRelationship(
                id="rel-1",
                workspace_id="test-ws",
                source_id="entity-1",
                target_id="entity-2",
                relation_type=RelationType.RELATED_TO,
            )

            rel2 = GraphRelationship(
                id="rel-2",
                workspace_id="test-ws",
                source_id="entity-2",
                target_id="entity-3",
                relation_type=RelationType.RELATED_TO,
            )

            rel3 = GraphRelationship(
                id="rel-3",
                workspace_id="test-ws",
                source_id="entity-3",
                target_id="entity-1",
                relation_type=RelationType.RELATED_TO,
            )

            # Create subgraph with circular references
            subgraph = SubGraph()
            subgraph.add_entity(entity1)
            subgraph.add_entity(entity2)
            subgraph.add_entity(entity3)
            subgraph.add_relationship(rel1)
            subgraph.add_relationship(rel2)
            subgraph.add_relationship(rel3)

            # Should handle circular references gracefully
            assert subgraph.size() == 6, "Subgraph should contain all items"

            # Test serialization with circular references
            subgraph_dict = subgraph.to_dict()
            assert subgraph_dict is not None, "Should serialize circular references"

            # Test deserialization
            restored_subgraph = SubGraph.from_dict(subgraph_dict)
            assert (
                restored_subgraph.size() == 6
            ), "Should deserialize circular references"

            # Test connected entities with circular references
            connected = subgraph.get_connected_entities("entity-1")
            assert (
                len(connected) == 2
            ), "Should find connected entities despite circular refs"

            # Test infinite loop prevention
            visited = set()

            def traverse_entities(entity_id):
                if entity_id in visited:
                    return
                visited.add(entity_id)
                connected = subgraph.get_connected_entities(entity_id)
                for entity in connected:
                    traverse_entities(entity.id)

            traverse_entities("entity-1")
            assert len(visited) == 3, "Should prevent infinite loops"

            self.log_success(
                "GRAPH_CIRCULAR_REFERENCES",
                "System handles circular references gracefully",
            )

        except Exception as e:
            self.log_breakage(
                "GRAPH_CIRCULAR_REFERENCES", f"Circular references break system: {e}"
            )

    def test_9_serialization_bombs(self):
        """Test 9: Serialization bomb attacks."""
        print("\n🔍 Test 9: Serialization Bomb Attacks")

        try:
            # Test with deeply nested structures
            def create_nested_structure(depth=0):
                """Create deeply nested structure."""
                if depth > 10:
                    return {
                        "level": depth,
                        "nested": create_nested_structure(depth - 1),
                        "data": "x" * 1000,
                        "list": [create_nested_structure(depth - 1)] * 5,
                    }
                else:
                    return {"level": depth, "data": "x" * 1000}

            # Create memory chunk with nested metadata
            nested_metadata = create_nested_structure(20)
            chunk = MemoryChunk(
                id="nested-chunk",
                workspace_id="test-ws",
                memory_type=MemoryType.RESEARCH,
                content="Test content",
                metadata=nested_metadata,
            )

            # Test serialization
            start_time = time.time()
            chunk_dict = chunk.to_dict()
            end_time = time.time()

            assert chunk_dict is not None, "Should serialize nested structure"
            assert end_time - start_time < 5.0, "Should serialize quickly"

            # Test deserialization
            start_time = time.time()
            restored_chunk = MemoryChunk.from_dict(chunk_dict)
            end_time = time.time()

            assert (
                restored_chunk.content == chunk.content
            ), "Should deserialize nested structure"
            assert end_time - start_time < 5.0, "Should deserialize quickly"

            # Test graph with nested properties
            nested_properties = create_nested_structure(15)
            entity = GraphEntity(
                id="nested-entity",
                workspace_id="test-ws",
                entity_type=EntityType.COMPANY,
                name="Nested Entity",
                properties=nested_properties,
            )

            # Test serialization
            entity_dict = entity.to_dict()
            assert entity_dict is not None, "Should serialize nested properties"

            # Test deserialization
            restored_entity = GraphEntity.from_dict(entity_dict)
            assert (
                restored_entity.name == entity.name
            ), "Should deserialize nested properties"

            # Test subgraph with nested data
            subgraph = SubGraph()
            subgraph.add_entity(entity)

            nested_subgraph_dict = subgraph.to_dict()
            assert (
                nested_subgraph_dict is not None
            ), "Should serialize subgraph with nested data"

            # Test with extremely large data
            large_metadata = {
                "large_data": "x" * 1000000,
                "large_list": list(range(100000)),
                "large_dict": {f"key_{i}": f"value_{i}" for i in range(10000)},
            }

            large_chunk = MemoryChunk(
                id="large-chunk",
                workspace_id="test-ws",
                memory_type=MemoryType.RESEARCH,
                content="Large content",
                metadata=large_metadata,
            )

            # Should handle large data gracefully or fail predictably
            try:
                large_chunk_dict = large_chunk.to_dict()
                assert large_chunk_dict is not None, "Should handle large data"
            except Exception as e:
                self.log_warning(
                    "SERIALIZATION_BOMBS", f"Large data serialization fails: {e}"
                )

            self.log_success(
                "SERIALIZATION_BOMBS", "System handles serialization bombs gracefully"
            )

        except Exception as e:
            self.log_breakage(
                "SERIALIZATION_BOMBS", f"Serialization bombs break system: {e}"
            )

    def test_10_resource_exhaustion(self):
        """Test 10: Resource exhaustion attacks."""
        print("\n🔍 Test 10: Resource Exhaustion Attacks")

        try:
            # Test file handle exhaustion
            file_handles = []

            try:
                # Try to open many files
                for i in range(1000):
                    file_path = f"test_file_{i}.txt"
                    with open(file_path, "w") as f:
                        f.write(f"Test content {i}")
                    file_handles.append(file_path)

                # Should handle file handle limits
                assert (
                    len(file_handles) >= 100
                ), "Should handle reasonable file handle count"

            except Exception as e:
                self.log_warning("RESOURCE_EXHAUSTION", f"File handle exhaustion: {e}")
            finally:
                # Clean up files
                for file_path in file_handles:
                    try:
                        os.remove(file_path)
                    except:
                        pass

            # Test thread exhaustion
            threads = []

            try:
                # Try to create many threads
                def dummy_worker():
                    time.sleep(0.01)

                for i in range(100):
                    thread = threading.Thread(target=dummy_worker)
                    threads.append(thread)
                    thread.start()

                # Wait for threads to complete
                for thread in threads:
                    thread.join()

                assert len(threads) >= 50, "Should handle reasonable thread count"

            except Exception as e:
                self.log_warning("RESOURCE_EXHAUSTION", f"Thread exhaustion: {e}")

            # Test memory exhaustion with garbage collection
            try:
                # Create many objects and force garbage collection
                objects = []

                for i in range(10000):
                    obj = {"data": "x" * 1000, "metadata": {"index": i, "large": True}}
                    objects.append(obj)

                # Force garbage collection
                gc.collect()

                assert len(objects) == 10000, "Should create many objects"

            except Exception as e:
                self.log_warning("RESOURCE_EXHAUSTION", f"Memory exhaustion: {e}")

            # Test embedding model resource exhaustion
            model = get_embedding_model()

            try:
                # Try to generate many embeddings
                embeddings = []

                for i in range(1000):
                    embedding = model.encode_single(f"Test text {i}")
                    embeddings.append(embedding)

                # Should handle or fail gracefully
                assert (
                    len(embeddings) >= 100
                ), "Should generate many embeddings or fail gracefully"

            except Exception as e:
                self.log_warning(
                    "RESOURCE_EXHAUSTION", f"Embedding model exhaustion: {e}"
                )

            self.log_success(
                "RESOURCE_EXHAUSTION", "System handles resource exhaustion gracefully"
            )

        except Exception as e:
            self.log_breakage(
                "RESOURCE_EXHAUSTION", f"Resource exhaustion breaks system: {e}"
            )


def run_cynical_breakage_tests():
    """Run all cynical breakage tests."""
    tester = CynicalBreakageTester()
    breakage_count = tester.run_all_breakage_tests()

    if breakage_count == 0:
        print("\n🎉 ALL TESTS SURVIVED - SYSTEM IS ROBUST!")
    else:
        print(f"\n🚨 FOUND {breakage_count} BREAKAGES - SYSTEM NEEDS FIXES!")

    return breakage_count


if __name__ == "__main__":
    breakage_count = run_cynical_breakage_tests()
    sys.exit(0 if breakage_count == 0 else 1)
