"""
Empirical test for graph models.

This script verifies that:
1. GraphEntity dataclass works correctly
2. GraphRelationship dataclass works correctly
3. SubGraph dataclass works correctly
4. Enums have all required values
5. Serialization/deserialization works
"""

import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))

import uuid
from datetime import datetime

import numpy as np
from memory.graph_models import (
    EntityType,
    GraphEntity,
    GraphRelationship,
    RelationType,
    SubGraph,
)


def test_entity_type_enum():
    """Test EntityType enum functionality."""
    print("Testing EntityType enum...")

    # Check all required types exist
    required_types = [
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
    actual_types = EntityType.get_all_types()

    print(f"Required types: {required_types}")
    print(f"Actual types: {actual_types}")

    assert set(required_types) == set(
        actual_types
    ), f"Missing types: {set(required_types) - set(actual_types)}"

    # Test from_string conversion
    for type_str in required_types:
        entity_type = EntityType.from_string(type_str)
        assert entity_type.value == type_str, f"Failed to convert {type_str}"

    # Test invalid type raises error
    try:
        EntityType.from_string("invalid_type")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass  # Expected

    print("✓ EntityType enum tests passed")


def test_relation_type_enum():
    """Test RelationType enum functionality."""
    print("Testing RelationType enum...")

    # Check all required types exist
    required_types = [
        "has_icp",
        "competes_with",
        "uses_channel",
        "solves_pain",
        "has_usp",
        "has_feature",
        "targets",
        "part_of",
        "created_by",
        "mentions",
        "related_to",
        "similar_to",
    ]
    actual_types = RelationType.get_all_types()

    print(f"Required types: {required_types}")
    print(f"Actual types: {actual_types}")

    assert set(required_types) == set(
        actual_types
    ), f"Missing types: {set(required_types) - set(actual_types)}"

    # Test from_string conversion
    for type_str in required_types:
        relation_type = RelationType.from_string(type_str)
        assert relation_type.value == type_str, f"Failed to convert {type_str}"

    # Test invalid type raises error
    try:
        RelationType.from_string("invalid_type")
        assert False, "Should have raised ValueError"
    except ValueError:
        pass  # Expected

    print("✓ RelationType enum tests passed")


def test_graph_entity_dataclass():
    """Test GraphEntity dataclass functionality."""
    print("Testing GraphEntity dataclass...")

    # Test basic creation
    entity = GraphEntity(
        id="entity-123",
        workspace_id="ws-456",
        entity_type=EntityType.COMPANY,
        name="Test Company",
        properties={"industry": "SaaS", "size": "mid-market"},
    )

    assert entity.id == "entity-123"
    assert entity.workspace_id == "ws-456"
    assert entity.entity_type == EntityType.COMPANY
    assert entity.name == "Test Company"
    assert entity.properties == {"industry": "SaaS", "size": "mid-market"}
    assert entity.embedding is None

    # Test default values
    empty_entity = GraphEntity()
    assert empty_entity.id is None
    assert empty_entity.workspace_id is None
    assert empty_entity.entity_type is None
    assert empty_entity.name == ""
    assert empty_entity.properties == {}
    assert empty_entity.created_at is not None
    assert empty_entity.updated_at is not None

    print("✓ GraphEntity creation tests passed")


def test_graph_entity_methods():
    """Test GraphEntity methods."""
    print("Testing GraphEntity methods...")

    entity = GraphEntity(
        id="test-entity",
        workspace_id="ws-test",
        entity_type=EntityType.ICP,
        name="Test ICP Profile",
        properties={"industry": "healthcare", "size": "enterprise"},
    )

    # Test to_dict/from_dict
    entity_dict = entity.to_dict()
    assert entity_dict["id"] == "test-entity"
    assert entity_dict["entity_type"] == "icp"
    assert entity_dict["name"] == "Test ICP Profile"
    assert "created_at" in entity_dict

    restored_entity = GraphEntity.from_dict(entity_dict)
    assert restored_entity.id == entity.id
    assert restored_entity.entity_type == entity.entity_type
    assert restored_entity.name == entity.name

    # Test embedding methods
    test_embedding = np.random.rand(384)
    entity.embedding = test_embedding

    embedding_list = entity.get_embedding_list()
    assert len(embedding_list) == 384
    assert isinstance(embedding_list, list)

    new_entity = GraphEntity()
    new_entity.set_embedding_from_list(embedding_list)
    assert np.array_equal(new_entity.embedding, test_embedding)

    # Test property methods
    entity.add_property("new_key", "new_value")
    assert entity.get_property("new_key") == "new_value"
    assert entity.get_property("missing_key", "default") == "default"
    assert entity.has_property("new_key")
    assert not entity.has_property("missing_key")

    entity.remove_property("new_key")
    assert not entity.has_property("new_key")

    # Test utility methods
    assert entity.is_valid(), "Entity should be valid"
    assert entity.get_display_name() == "Test ICP Profile"

    # Test long name truncation
    long_name_entity = GraphEntity(name="A" * 100)
    assert len(long_name_entity.get_display_name()) <= 50
    assert long_name_entity.get_display_name().endswith("...")

    # Test similarity calculation
    entity1 = GraphEntity(name="Entity 1")
    entity2 = GraphEntity(name="Entity 2")

    # Without embeddings, similarity should be 0
    assert entity1.similarity_score(entity2) == 0.0

    # With embeddings
    entity1.embedding = np.array([1.0, 0.0])
    entity2.embedding = np.array([1.0, 0.0])
    assert entity1.similarity_score(entity2) == 1.0

    entity2.embedding = np.array([0.0, 1.0])
    assert entity1.similarity_score(entity2) == 0.0

    print("✓ GraphEntity method tests passed")


def test_graph_relationship_dataclass():
    """Test GraphRelationship dataclass functionality."""
    print("Testing GraphRelationship dataclass...")

    # Test basic creation
    rel = GraphRelationship(
        id="rel-123",
        workspace_id="ws-456",
        source_id="entity-1",
        target_id="entity-2",
        relation_type=RelationType.HAS_ICP,
        properties={"strength": "strong"},
        weight=0.8,
    )

    assert rel.id == "rel-123"
    assert rel.workspace_id == "ws-456"
    assert rel.source_id == "entity-1"
    assert rel.target_id == "entity-2"
    assert rel.relation_type == RelationType.HAS_ICP
    assert rel.properties == {"strength": "strong"}
    assert rel.weight == 0.8

    # Test default values
    empty_rel = GraphRelationship()
    assert empty_rel.id is None
    assert empty_rel.workspace_id is None
    assert empty_rel.source_id is None
    assert empty_rel.target_id is None
    assert empty_rel.relation_type is None
    assert empty_rel.properties == {}
    assert empty_rel.weight == 1.0
    assert empty_rel.created_at is not None
    assert empty_rel.updated_at is not None

    print("✓ GraphRelationship creation tests passed")


def test_graph_relationship_methods():
    """Test GraphRelationship methods."""
    print("Testing GraphRelationship methods...")

    rel = GraphRelationship(
        id="test-rel",
        workspace_id="ws-test",
        source_id="source-entity",
        target_id="target-entity",
        relation_type=RelationType.USES_CHANNEL,
        properties={"channel_type": "email"},
        weight=0.7,
    )

    # Test to_dict/from_dict
    rel_dict = rel.to_dict()
    assert rel_dict["id"] == "test-rel"
    assert rel_dict["relation_type"] == "uses_channel"
    assert rel_dict["source_id"] == "source-entity"
    assert rel_dict["target_id"] == "target-entity"
    assert "created_at" in rel_dict

    restored_rel = GraphRelationship.from_dict(rel_dict)
    assert restored_rel.id == rel.id
    assert restored_rel.relation_type == rel.relation_type
    assert restored_rel.source_id == rel.source_id
    assert restored_rel.target_id == rel.target_id

    # Test property methods
    rel.add_property("new_key", "new_value")
    assert rel.get_property("new_key") == "new_value"
    assert rel.get_property("missing_key", "default") == "default"
    assert rel.has_property("new_key")

    rel.remove_property("new_key")
    assert not rel.has_property("new_key")

    # Test validation
    assert rel.is_valid(), "Relationship should be valid"

    # Test invalid relationship (same source and target)
    invalid_rel = GraphRelationship(
        source_id="same-id", target_id="same-id", relation_type=RelationType.RELATED_TO
    )
    assert (
        not invalid_rel.is_valid()
    ), "Relationship with same source and target should be invalid"

    # Test weight normalization
    high_weight_rel = GraphRelationship(weight=1.5)
    assert high_weight_rel.weight == 1.0, "Weight should be normalized to 1.0"

    low_weight_rel = GraphRelationship(weight=-0.5)
    assert low_weight_rel.weight == 0.0, "Weight should be normalized to 0.0"

    # Test reverse relationship
    reversed_rel = rel.reverse()
    assert reversed_rel.source_id == rel.target_id
    assert reversed_rel.target_id == rel.source_id
    assert reversed_rel.relation_type == rel.get_reverse_type()

    print("✓ GraphRelationship method tests passed")


def test_subgraph_dataclass():
    """Test SubGraph dataclass functionality."""
    print("Testing SubGraph dataclass...")

    # Test basic creation
    subgraph = SubGraph()
    assert subgraph.entities == {}
    assert subgraph.relationships == {}
    assert subgraph.center_entity_id is None
    assert subgraph.depth == 0
    assert subgraph.created_at is not None

    # Test adding entities and relationships
    entity1 = GraphEntity(id="e1", name="Entity 1", entity_type=EntityType.COMPANY)
    entity2 = GraphEntity(id="e2", name="Entity 2", entity_type=EntityType.ICP)
    rel = GraphRelationship(
        id="r1", source_id="e1", target_id="e2", relation_type=RelationType.HAS_ICP
    )

    subgraph.add_entity(entity1)
    subgraph.add_entity(entity2)
    subgraph.add_relationship(rel)

    assert len(subgraph.entities) == 2
    assert len(subgraph.relationships) == 1
    assert subgraph.get_entity("e1") == entity1
    assert subgraph.get_entity("e2") == entity2
    assert subgraph.get_relationship("r1") == rel

    # Test connected entities
    connected = subgraph.get_connected_entities("e1")
    assert len(connected) == 1
    assert connected[0].id == "e2"

    # Test entity relationships
    entity_rels = subgraph.get_entity_relationships("e1")
    assert len(entity_rels) == 1
    assert entity_rels[0].id == "r1"

    # Test type counts
    entity_types = subgraph.get_entity_types()
    assert EntityType.COMPANY in entity_types
    assert EntityType.ICP in entity_types
    assert entity_types[EntityType.COMPANY] == 1
    assert entity_types[EntityType.ICP] == 1

    rel_types = subgraph.get_relationship_types()
    assert RelationType.HAS_ICP in rel_types
    assert rel_types[RelationType.HAS_ICP] == 1

    # Test utility methods
    assert not subgraph.is_empty(), "Subgraph should not be empty"
    assert (
        subgraph.size() == 3
    ), "Subgraph size should be 3 (2 entities + 1 relationship)"

    print("✓ SubGraph tests passed")


def test_subgraph_serialization():
    """Test SubGraph serialization."""
    print("Testing SubGraph serialization...")

    # Create subgraph with data
    subgraph = SubGraph(center_entity_id="center", depth=2)

    entity = GraphEntity(
        id="center",
        name="Center Entity",
        entity_type=EntityType.COMPANY,
        properties={"key": "value"},
    )
    rel = GraphRelationship(
        id="rel-1",
        source_id="center",
        target_id="other",
        relation_type=RelationType.COMPETES_WITH,
        weight=0.8,
    )

    subgraph.add_entity(entity)
    subgraph.add_relationship(rel)

    # Test to_dict
    subgraph_dict = subgraph.to_dict()
    assert "entities" in subgraph_dict
    assert "relationships" in subgraph_dict
    assert subgraph_dict["center_entity_id"] == "center"
    assert subgraph_dict["depth"] == 2

    # Test from_dict
    restored_subgraph = SubGraph.from_dict(subgraph_dict)
    assert restored_subgraph.center_entity_id == "center"
    assert restored_subgraph.depth == 2
    assert len(restored_subgraph.entities) == 1
    assert len(restored_subgraph.relationships) == 1

    restored_entity = restored_subgraph.get_entity("center")
    assert restored_entity.name == "Center Entity"
    assert restored_entity.entity_type == EntityType.COMPANY

    print("✓ SubGraph serialization tests passed")


def test_reverse_relationship_types():
    """Test reverse relationship type mapping."""
    print("Testing reverse relationship types...")

    # Test specific reverse mappings
    test_cases = [
        (RelationType.HAS_ICP, RelationType.PART_OF),
        (RelationType.PART_OF, RelationType.HAS_ICP),
        (RelationType.USES_CHANNEL, RelationType.TARGETS),
        (RelationType.TARGETS, RelationType.USES_CHANNEL),
        (RelationType.COMPETES_WITH, RelationType.COMPETES_WITH),
        (RelationType.SIMILAR_TO, RelationType.SIMILAR_TO),
    ]

    for original, expected_reverse in test_cases:
        rel = GraphRelationship(source_id="a", target_id="b", relation_type=original)
        reverse_rel = rel.reverse()
        assert (
            reverse_rel.relation_type == expected_reverse
        ), f"{original} should reverse to {expected_reverse}"

    print("✓ Reverse relationship type tests passed")


def run_all_tests():
    """Run all empirical tests."""
    print("=" * 60)
    print("RUNNING EMPIRICAL TESTS FOR GRAPH MODELS")
    print("=" * 60)

    try:
        test_entity_type_enum()
        test_relation_type_enum()
        test_graph_entity_dataclass()
        test_graph_entity_methods()
        test_graph_relationship_dataclass()
        test_graph_relationship_methods()
        test_subgraph_dataclass()
        test_subgraph_serialization()
        test_reverse_relationship_types()

        print("=" * 60)
        print("✅ ALL TESTS PASSED - GRAPH MODELS WORK CORRECTLY")
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
