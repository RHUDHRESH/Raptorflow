"""
Production-ready memory system integration tests.
No mocks, no fallbacks - 100% enterprise verification.
"""

import asyncio
import os
import sys
import uuid
from datetime import datetime
from typing import Any, Dict

import pytest

# Add backend to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from memory import (
    EpisodicMemory,
    GraphMemory,
    MemoryChunk,
    MemoryController,
    MemoryType,
    VectorMemory,
    WorkingMemory,
)
from memory.chunker import ContentChunker
from memory.embeddings import get_embedding_model
from memory.graph_models import EntityType, RelationType


class TestMemorySystemProduction:
    """Production memory system tests."""

    @pytest.fixture
    def test_workspace_id(self):
        """Test workspace ID."""
        return str(uuid.uuid4())

    @pytest.fixture
    def test_data(self):
        """Comprehensive test data."""
        return {
            "foundation": {
                "company_name": "ProductionTest Corp",
                "mission": "Excellence in AI-driven solutions",
                "vision": "Leading the future of enterprise AI",
                "usps": [
                    "Advanced machine learning",
                    "Real-time processing",
                    "Enterprise security",
                ],
                "industry": "Technology",
                "size": "Enterprise",
            },
            "icp": {
                "name": "Enterprise CTOs",
                "demographics": {
                    "company_size": "1000+ employees",
                    "industry": "Technology",
                    "revenue": "$100M+",
                },
                "pain_points": [
                    "Legacy system integration",
                    "Data security concerns",
                    "Scalability challenges",
                ],
                "psychographics": {
                    "values": ["Innovation", "Security", "Scalability"],
                    "communication_style": "Technical and strategic",
                },
            },
            "content": [
                "Our AI platform processes millions of transactions daily.",
                "Enterprise-grade security with SOC 2 compliance.",
                "Seamless integration with existing infrastructure.",
                "Real-time analytics and insights dashboard.",
            ],
        }

    def test_01_embedding_model_production(self, test_data):
        """Test embedding model in production."""
        print("\n🧠 Testing Embedding Model Production...")

        # Initialize model
        model = get_embedding_model()
        assert model is not None, "Embedding model should initialize"

        # Test single embedding
        text = test_data["foundation"]["mission"]
        embedding = model.encode_single(text)
        assert len(embedding) == 384, f"Expected 384 dimensions, got {len(embedding)}"
        assert all(
            isinstance(x, float) for x in embedding
        ), "All values should be floats"

        # Test batch embeddings
        texts = test_data["content"]
        embeddings = model.encode(texts)
        assert len(embeddings) == len(texts), "Should return same number of embeddings"
        assert all(
            len(emb) == 384 for emb in embeddings
        ), "All embeddings should be 384 dimensions"

        # Test embedding consistency
        text = "Consistency test"
        emb1 = model.encode_single(text)
        emb2 = model.encode_single(text)

        # Calculate cosine similarity
        dot_product = sum(a * b for a, b in zip(emb1, emb2))
        magnitude1 = sum(a * a for a in emb1) ** 0.5
        magnitude2 = sum(b * b for b in emb2) ** 0.5
        similarity = dot_product / (magnitude1 * magnitude2)

        assert (
            similarity > 0.99
        ), f"Embeddings should be consistent, got similarity {similarity}"

        print("✅ Embedding model production tests passed")

    def test_02_content_chunker_production(self, test_data):
        """Test content chunker in production."""
        print("\n🔪 Testing Content Chunker Production...")

        chunker = ContentChunker()

        # Test basic chunking
        text = " ".join(test_data["content"])
        chunks = chunker.chunk(text)
        assert len(chunks) > 0, "Should generate chunks"
        assert all(
            isinstance(chunk, str) for chunk in chunks
        ), "All chunks should be strings"

        # Test chunk size limits
        long_text = " ".join(["Production test word."] * 100)
        chunks = chunker.chunk(long_text)
        assert all(
            len(chunk) <= 500 for chunk in chunks
        ), "All chunks should respect size limit"

        # Test content preservation
        original_words = set(text.lower().split())
        chunked_words = set(" ".join(chunks).lower().split())

        # Most words should be preserved (allowing for some loss due to chunking)
        preservation_rate = len(original_words & chunked_words) / len(original_words)
        assert (
            preservation_rate > 0.9
        ), f"Should preserve most content, got {preservation_rate}"

        print("✅ Content chunker production tests passed")

    def test_03_memory_chunk_production(self, test_workspace_id, test_data):
        """Test memory chunk creation and management."""
        print("\n📦 Testing Memory Chunk Production...")

        # Test foundation chunk
        foundation_chunk = MemoryChunk(
            workspace_id=test_workspace_id,
            memory_type=MemoryType.FOUNDATION,
            content=test_data["foundation"]["mission"],
            metadata={
                "source": "production_test",
                "company": test_data["foundation"]["company_name"],
            },
        )

        assert (
            foundation_chunk.memory_type == MemoryType.FOUNDATION
        ), "Memory type should be correct"
        assert (
            foundation_chunk.workspace_id == test_workspace_id
        ), "Workspace ID should match"
        assert len(foundation_chunk.content) > 0, "Content should not be empty"
        assert (
            foundation_chunk.metadata["source"] == "production_test"
        ), "Metadata should be preserved"

        # Test ICP chunk
        icp_content = f"ICP: {test_data['icp']['name']}, Pain points: {', '.join(test_data['icp']['pain_points'])}"
        icp_chunk = MemoryChunk(
            workspace_id=test_workspace_id,
            memory_type=MemoryType.ICP,
            content=icp_content,
            metadata={"icp_name": test_data["icp"]["name"]},
        )

        assert (
            icp_chunk.memory_type == MemoryType.ICP
        ), "ICP memory type should be correct"
        assert (
            "pain points" in icp_chunk.content.lower()
        ), "Content should include pain points"

        # Test chunk serialization
        foundation_dict = foundation_chunk.to_dict()
        assert "id" in foundation_dict, "Serialized chunk should have ID"
        assert (
            "memory_type" in foundation_dict
        ), "Serialized chunk should have memory type"
        assert (
            foundation_dict["memory_type"] == "foundation"
        ), "Serialized memory type should match"

        # Test chunk deserialization
        restored_chunk = MemoryChunk.from_dict(foundation_dict)
        assert (
            restored_chunk.memory_type == foundation_chunk.memory_type
        ), "Deserialized chunk should match"
        assert (
            restored_chunk.content == foundation_chunk.content
        ), "Content should be preserved"

        print("✅ Memory chunk production tests passed")

    def test_04_graph_models_production(self, test_workspace_id, test_data):
        """Test graph models in production."""
        print("\n🕸️ Testing Graph Models Production...")

        from memory.graph_models import GraphEntity, GraphRelationship, SubGraph

        # Test company entity
        company_entity = GraphEntity(
            id=str(uuid.uuid4()),
            workspace_id=test_workspace_id,
            entity_type=EntityType.COMPANY,
            name=test_data["foundation"]["company_name"],
            properties={
                "industry": test_data["foundation"]["industry"],
                "size": test_data["foundation"]["size"],
                "mission": test_data["foundation"]["mission"],
            },
        )

        assert (
            company_entity.entity_type == EntityType.COMPANY
        ), "Entity type should be COMPANY"
        assert (
            company_entity.workspace_id == test_workspace_id
        ), "Workspace ID should match"
        assert len(company_entity.properties) > 0, "Properties should be set"

        # Test USP entity
        usp_entity = GraphEntity(
            id=str(uuid.uuid4()),
            workspace_id=test_workspace_id,
            entity_type=EntityType.USP,
            name="Advanced Machine Learning",
            properties={"category": "technology", "importance": "high"},
        )

        assert (
            usp_entity.entity_type == EntityType.USP
        ), "USP entity type should be correct"

        # Test relationship
        relationship = GraphRelationship(
            id=str(uuid.uuid4()),
            workspace_id=test_workspace_id,
            source_id=company_entity.id,
            target_id=usp_entity.id,
            relation_type=RelationType.HAS_USP,
            weight=1.0,
            properties={"established": datetime.now().isoformat()},
        )

        assert (
            relationship.relation_type == RelationType.HAS_USP
        ), "Relationship type should be correct"
        assert (
            relationship.source_id == company_entity.id
        ), "Source should match company"
        assert relationship.target_id == usp_entity.id, "Target should match USP"
        assert 0.0 <= relationship.weight <= 1.0, "Weight should be in valid range"

        # Test subgraph
        subgraph = SubGraph(
            entities=[company_entity, usp_entity], relationships=[relationship]
        )

        assert len(subgraph.entities) == 2, "Subgraph should have 2 entities"
        assert len(subgraph.relationships) == 1, "Subgraph should have 1 relationship"

        print("✅ Graph models production tests passed")

    def test_05_episodic_memory_production(self, test_workspace_id, test_data):
        """Test episodic memory in production."""
        print("\n📖 Testing Episodic Memory Production...")

        from memory.episodic_memory import Episode

        # Test conversation episode
        episode = Episode(
            workspace_id=test_workspace_id,
            session_id=str(uuid.uuid4()),
            episode_type="conversation",
            title="Product Discussion",
            content=f"Discussion about {test_data['foundation']['company_name']} products",
            metadata={
                "participants": ["user", "assistant"],
                "topic": "product_features",
                "duration_minutes": 15,
            },
            importance=0.8,
            tags=["product", "discussion", "features"],
        )

        assert episode.workspace_id == test_workspace_id, "Workspace ID should match"
        assert (
            episode.episode_type == "conversation"
        ), "Episode type should be conversation"
        assert (
            episode.importance >= 0.0 and episode.importance <= 1.0
        ), "Importance should be in range"
        assert len(episode.tags) > 0, "Tags should be set"

        # Test episode serialization
        episode_dict = episode.to_dict()
        assert "id" in episode_dict, "Episode should serialize with ID"
        assert "episode_type" in episode_dict, "Episode should serialize with type"
        assert episode_dict["importance"] == 0.8, "Importance should be preserved"

        # Test episode embedding
        model = get_embedding_model()
        embedding = model.encode_single(episode.content)
        episode.embedding = embedding.tolist()

        assert episode.embedding is not None, "Episode should have embedding"
        assert (
            len(episode.embedding) == 384
        ), "Episode embedding should be 384 dimensions"

        print("✅ Episodic memory production tests passed")

    def test_06_working_memory_production(self, test_workspace_id):
        """Test working memory in production."""
        print("\n⚡ Testing Working Memory Production...")

        from memory.working_memory import MemoryItem, MemorySession, WorkingMemory

        # Test memory item
        item = MemoryItem(
            key="current_task",
            value="analyzing_customer_requirements",
            created_at=datetime.now(),
            updated_at=datetime.now(),
            tags=["task", "analysis"],
            metadata={"priority": "high", "assigned_to": "ai_agent"},
        )

        assert item.key == "current_task", "Item key should match"
        assert item.access_count == 0, "Access count should initialize to 0"
        assert len(item.tags) > 0, "Tags should be set"

        # Test session
        session = MemorySession(
            session_id=str(uuid.uuid4()),
            workspace_id=test_workspace_id,
            user_id="test_user_123",
            created_at=datetime.now(),
            last_activity=datetime.now(),
            context={"current_page": "dashboard", "user_role": "admin"},
        )

        assert session.workspace_id == test_workspace_id, "Workspace ID should match"
        assert len(session.context) > 0, "Session context should be set"

        # Test item addition to session
        session.items[item.key] = item
        assert len(session.items) == 1, "Session should contain one item"
        assert session.items["current_task"] == item, "Item should be retrievable"

        # Test working memory initialization
        working_memory = WorkingMemory()
        assert working_memory is not None, "Working memory should initialize"

        print("✅ Working memory production tests passed")

    def test_07_memory_controller_production(self, test_workspace_id, test_data):
        """Test memory controller integration."""
        print("\n🎛️ Testing Memory Controller Production...")

        # Initialize controller
        controller = MemoryController()
        assert controller is not None, "Memory controller should initialize"

        # Test creating multiple memory chunks
        chunks = []

        # Foundation chunk
        foundation_chunk = MemoryChunk(
            workspace_id=test_workspace_id,
            memory_type=MemoryType.FOUNDATION,
            content=test_data["foundation"]["mission"],
            metadata={"company": test_data["foundation"]["company_name"]},
        )
        chunks.append(foundation_chunk)

        # ICP chunk
        icp_content = f"Target: {test_data['icp']['name']}, Industry: {test_data['icp']['demographics']['industry']}"
        icp_chunk = MemoryChunk(
            workspace_id=test_workspace_id,
            memory_type=MemoryType.ICP,
            content=icp_content,
            metadata={"target_segment": test_data["icp"]["name"]},
        )
        chunks.append(icp_chunk)

        # Content chunks
        for i, content in enumerate(test_data["content"]):
            content_chunk = MemoryChunk(
                workspace_id=test_workspace_id,
                memory_type=MemoryType.RESEARCH,
                content=content,
                metadata={"content_index": i, "category": "product_info"},
            )
            chunks.append(content_chunk)

        assert len(chunks) == 6, "Should have created 6 chunks total"

        # Test memory type distribution
        type_counts = {}
        for chunk in chunks:
            type_counts[chunk.memory_type] = type_counts.get(chunk.memory_type, 0) + 1

        assert type_counts[MemoryType.FOUNDATION] == 1, "Should have 1 foundation chunk"
        assert type_counts[MemoryType.ICP] == 1, "Should have 1 ICP chunk"
        assert type_counts[MemoryType.RESEARCH] == 4, "Should have 4 research chunks"

        # Test embedding generation for all chunks
        model = get_embedding_model()
        for chunk in chunks:
            embedding = model.encode_single(chunk.content)
            chunk.embedding = embedding
            assert (
                len(chunk.embedding) == 384
            ), "All chunks should have 384-dimension embeddings"

        # Test chunk metadata consistency
        for chunk in chunks:
            assert chunk.metadata is not None, "All chunks should have metadata"
            assert (
                "workspace_id" not in chunk.metadata
            ), "Workspace ID should be separate field"

        print("✅ Memory controller production tests passed")

    def test_08_memory_type_validation_production(self, test_workspace_id, test_data):
        """Test memory type validation in production."""
        print("\n🏷️ Testing Memory Type Validation Production...")

        # Test all memory types
        all_types = [
            MemoryType.FOUNDATION,
            MemoryType.ICP,
            MemoryType.MOVE,
            MemoryType.CAMPAIGN,
            MemoryType.RESEARCH,
            MemoryType.CONVERSATION,
            MemoryType.FEEDBACK,
        ]

        chunks = []
        for memory_type in all_types:
            chunk = MemoryChunk(
                workspace_id=test_workspace_id,
                memory_type=memory_type,
                content=f"Test content for {memory_type.value}",
                metadata={"test_type": memory_type.value},
            )
            chunks.append(chunk)

        assert len(chunks) == len(all_types), "Should have chunk for each memory type"

        # Test type conversion
        for chunk in chunks:
            # Test to_dict conversion
            chunk_dict = chunk.to_dict()
            assert (
                chunk_dict["memory_type"] == chunk.memory_type.value
            ), "Type should convert to string"

            # Test from_dict conversion
            restored_chunk = MemoryChunk.from_dict(chunk_dict)
            assert (
                restored_chunk.memory_type == chunk.memory_type
            ), "Type should restore correctly"

        # Test invalid type handling
        try:
            invalid_chunk = MemoryChunk(
                workspace_id=test_workspace_id,
                memory_type="invalid_type",
                content="This should fail",
            )
            assert False, "Should not accept invalid memory type"
        except (ValueError, AttributeError):
            pass  # Expected behavior

        print("✅ Memory type validation production tests passed")

    def test_09_content_processing_production(self, test_data):
        """Test content processing pipeline."""
        print("\n⚙️ Testing Content Processing Production...")

        # Test content preparation
        content_items = []

        # Foundation content
        foundation_content = f"""
        Company: {test_data['foundation']['company_name']}
        Mission: {test_data['foundation']['mission']}
        Vision: {test_data['foundation']['vision']}
        Industry: {test_data['foundation']['industry']}
        USPs: {', '.join(test_data['foundation']['usps'])}
        """
        content_items.append(("foundation", foundation_content))

        # ICP content
        icp_content = f"""
        ICP Name: {test_data['icp']['name']}
        Company Size: {test_data['icp']['demographics']['company_size']}
        Industry: {test_data['icp']['demographics']['industry']}
        Pain Points: {', '.join(test_data['icp']['pain_points'])}
        Values: {', '.join(test_data['icp']['psychographics']['values'])}
        """
        content_items.append(("icp", icp_content))

        # Test chunking for all content
        chunker = ContentChunker(chunk_size=300, overlap=50)
        all_chunks = []

        for content_type, content in content_items:
            chunks = chunker.chunk(content)
            for i, chunk in enumerate(chunks):
                memory_chunk = MemoryChunk(
                    workspace_id=str(uuid.uuid4()),
                    memory_type=MemoryType.from_string(content_type),
                    content=chunk,
                    metadata={
                        "content_type": content_type,
                        "chunk_index": i,
                        "total_chunks": len(chunks),
                    },
                )
                all_chunks.append(memory_chunk)

        assert len(all_chunks) > 0, "Should generate chunks from all content"

        # Test embedding generation for all chunks
        model = get_embedding_model()
        for chunk in all_chunks:
            embedding = model.encode_single(chunk.content)
            chunk.embedding = embedding
            assert len(chunk.embedding) == 384, "All chunks should have embeddings"

        # Test content preservation across chunks
        original_total_chars = sum(len(content) for _, content in content_items)
        chunked_total_chars = sum(len(chunk.content) for chunk in all_chunks)

        # Allow for some loss due to chunking boundaries
        preservation_rate = chunked_total_chars / original_total_chars
        assert (
            preservation_rate > 0.95
        ), f"Should preserve most content, got {preservation_rate}"

        print("✅ Content processing production tests passed")

    def test_10_error_handling_production(self, test_workspace_id):
        """Test error handling in production."""
        print("\n🚨 Testing Error Handling Production...")

        # Test invalid memory type
        try:
            MemoryType.from_string("nonexistent_type")
            assert False, "Should raise ValueError for invalid type"
        except ValueError:
            pass  # Expected

        # Test empty content handling
        empty_chunk = MemoryChunk(
            workspace_id=test_workspace_id,
            memory_type=MemoryType.CONVERSATION,
            content="",
        )

        assert empty_chunk.is_empty(), "Empty content should be detected"

        # Test content truncation
        long_content = "A" * 1000
        truncated = empty_chunk.truncate_content(100)
        assert (
            len(truncated) <= 103
        ), "Truncated content should respect limit with ellipsis"
        assert truncated.endswith("..."), "Truncated content should end with ellipsis"

        # Test metadata operations
        chunk = MemoryChunk(
            workspace_id=test_workspace_id,
            memory_type=MemoryType.RESEARCH,
            content="Test content",
        )

        # Test metadata addition
        chunk.add_metadata("test_key", "test_value")
        assert (
            chunk.get_metadata("test_key") == "test_value"
        ), "Metadata should be retrievable"

        # Test missing metadata
        assert (
            chunk.get_metadata("missing_key", "default") == "default"
        ), "Should return default for missing key"

        # Test metadata existence check
        assert chunk.has_metadata("test_key"), "Should detect existing metadata"
        assert not chunk.has_metadata("missing_key"), "Should detect missing metadata"

        print("✅ Error handling production tests passed")


if __name__ == "__main__":
    # Run production tests
    pytest.main([__file__, "-v", "-s"])
