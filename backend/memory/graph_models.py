"""
Graph memory models and types.

This module defines the data structures for the knowledge graph
memory system, including entities, relationships, and subgraphs.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

import numpy as np


class EntityType(Enum):
    """Types of entities in the knowledge graph."""

    COMPANY = "company"
    ICP = "icp"
    COMPETITOR = "competitor"
    CHANNEL = "channel"
    PAIN_POINT = "pain_point"
    USP = "usp"
    FEATURE = "feature"
    MOVE = "move"
    CAMPAIGN = "campaign"
    CONTENT = "content"

    @classmethod
    def get_all_types(cls) -> List[str]:
        """Get all entity type values as strings."""
        return [t.value for t in cls]

    @classmethod
    def from_string(cls, value: str) -> "EntityType":
        """Create EntityType from string value."""
        for entity_type in cls:
            if entity_type.value == value:
                return entity_type
        raise ValueError(f"Invalid entity type: {value}")


class RelationType(Enum):
    """Types of relationships between entities."""

    HAS_ICP = "has_icp"
    COMPETES_WITH = "competes_with"
    USES_CHANNEL = "uses_channel"
    SOLVES_PAIN = "solves_pain"
    HAS_USP = "has_usp"
    HAS_FEATURE = "has_feature"
    TARGETS = "targets"
    PART_OF = "part_of"
    CREATED_BY = "created_by"
    MENTIONS = "mentions"
    RELATED_TO = "related_to"
    SIMILAR_TO = "similar_to"

    @classmethod
    def get_all_types(cls) -> List[str]:
        """Get all relationship type values as strings."""
        return [t.value for t in cls]

    @classmethod
    def from_string(cls, value: str) -> "RelationType":
        """Create RelationType from string value."""
        for relation_type in cls:
            if relation_type.value == value:
                return relation_type
        raise ValueError(f"Invalid relation type: {value}")


@dataclass
class GraphEntity:
    """An entity in the knowledge graph."""

    id: Optional[str] = None
    workspace_id: Optional[str] = None
    entity_type: Optional[EntityType] = None
    name: str = ""
    properties: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[np.ndarray] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Initialize default values."""
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "workspace_id": self.workspace_id,
            "entity_type": self.entity_type.value if self.entity_type else None,
            "name": self.name,
            "properties": self.properties,
            "embedding": self.get_embedding_list(),
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GraphEntity":
        """Create from dictionary."""
        # Handle datetime parsing
        if data.get("created_at"):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if data.get("updated_at"):
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])

        # Handle entity type
        if data.get("entity_type"):
            data["entity_type"] = EntityType.from_string(data["entity_type"])

        # Handle embedding
        entity = cls(**data)
        if data.get("embedding"):
            entity.set_embedding_from_list(data["embedding"])

        return entity

    def get_embedding_list(self) -> Optional[List[float]]:
        """Get embedding as list for JSON serialization."""
        if self.embedding is not None:
            return self.embedding.tolist()
        return None

    def set_embedding_from_list(self, embedding_list: List[float]):
        """Set embedding from list."""
        self.embedding = np.array(embedding_list)

    def add_property(self, key: str, value: Any):
        """Add or update a property."""
        self.properties[key] = value
        self.updated_at = datetime.now()

    def get_property(self, key: str, default: Any = None) -> Any:
        """Get a property value."""
        return self.properties.get(key, default)

    def has_property(self, key: str) -> bool:
        """Check if property exists."""
        return key in self.properties

    def remove_property(self, key: str):
        """Remove a property."""
        if key in self.properties:
            del self.properties[key]
            self.updated_at = datetime.now()

    def get_display_name(self) -> str:
        """Get display name, falling back to a truncated version."""
        if len(self.name) <= 50:
            return self.name
        return self.name[:47] + "..."

    def is_valid(self) -> bool:
        """Check if entity is valid."""
        return self.name and self.name.strip() and self.entity_type is not None

    def similarity_score(self, other: "GraphEntity") -> float:
        """Calculate similarity with another entity using embeddings."""
        if self.embedding is None or other.embedding is None:
            return 0.0

        # Normalize embeddings
        norm1 = np.linalg.norm(self.embedding)
        norm2 = np.linalg.norm(other.embedding)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        # Cosine similarity
        return float(np.dot(self.embedding / norm1, other.embedding / norm2))

    def __str__(self) -> str:
        """String representation."""
        type_str = self.entity_type.value if self.entity_type else "unknown"
        return f"GraphEntity({type_str}: {self.get_display_name()})"

    def __repr__(self) -> str:
        """Detailed representation."""
        return (
            f"GraphEntity(id={self.id}, type={self.entity_type}, "
            f"name='{self.name}', properties={len(self.properties)})"
        )


@dataclass
class GraphRelationship:
    """A relationship between two entities."""

    id: Optional[str] = None
    workspace_id: Optional[str] = None
    source_id: Optional[str] = None
    target_id: Optional[str] = None
    relation_type: Optional[RelationType] = None
    properties: Dict[str, Any] = field(default_factory=dict)
    weight: float = 1.0
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def __post_init__(self):
        """Initialize default values."""
        if self.created_at is None:
            self.created_at = datetime.now()
        if self.updated_at is None:
            self.updated_at = datetime.now()

        # Validate and normalize weight
        try:
            if not isinstance(self.weight, (int, float)):
                # Convert to float if possible, otherwise default to 1.0
                try:
                    self.weight = float(self.weight)
                except (ValueError, TypeError):
                    self.weight = 1.0

            # Normalize weight to [0, 1] range
            self.weight = max(0.0, min(1.0, float(self.weight)))
        except Exception:
            # Fallback to default weight if anything goes wrong
            self.weight = 1.0

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "workspace_id": self.workspace_id,
            "source_id": self.source_id,
            "target_id": self.target_id,
            "relation_type": self.relation_type.value if self.relation_type else None,
            "properties": self.properties,
            "weight": self.weight,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GraphRelationship":
        """Create from dictionary."""
        # Handle datetime parsing
        if data.get("created_at"):
            data["created_at"] = datetime.fromisoformat(data["created_at"])
        if data.get("updated_at"):
            data["updated_at"] = datetime.fromisoformat(data["updated_at"])

        # Handle relation type
        if data.get("relation_type"):
            data["relation_type"] = RelationType.from_string(data["relation_type"])

        return cls(**data)

    def add_property(self, key: str, value: Any):
        """Add or update a property."""
        self.properties[key] = value
        self.updated_at = datetime.now()

    def get_property(self, key: str, default: Any = None) -> Any:
        """Get a property value."""
        return self.properties.get(key, default)

    def has_property(self, key: str) -> bool:
        """Check if property exists."""
        return key in self.properties

    def remove_property(self, key: str):
        """Remove a property."""
        if key in self.properties:
            del self.properties[key]
            self.updated_at = datetime.now()

    def is_valid(
        self,
        source_entity: Optional[GraphEntity] = None,
        target_entity: Optional[GraphEntity] = None,
    ) -> bool:
        """Check if relationship is valid."""
        if not self.id:
            return False

        if not self.workspace_id:
            return False

        if not self.source_id:
            return False

        if not self.target_id:
            return False

        if not self.relation_type:
            return False

        # Prevent self-referencing relationships
        if self.source_id == self.target_id:
            return False

        # Validate weight is numeric
        if not isinstance(self.weight, (int, float)):
            return False

        # Check workspace boundary violations if entities provided
        if source_entity and target_entity:
            if self.is_workspace_boundary_violation(source_entity, target_entity):
                return False

        return True

    def is_workspace_boundary_violation(
        self, source_entity: GraphEntity, target_entity: GraphEntity
    ) -> bool:
        """Check if this relationship violates workspace boundaries."""
        if not source_entity or not target_entity:
            return True  # Can't validate without entities

        # Check if entities are in different workspaces
        if source_entity.workspace_id != target_entity.workspace_id:
            return True

        # Check if relationship workspace matches entities
        if (
            self.workspace_id != source_entity.workspace_id
            or self.workspace_id != target_entity.workspace_id
        ):
            return True

        return False

    def reverse(self) -> "GraphRelationship":
        """Create a reversed relationship."""
        reverse_type = self.get_reverse_type()
        return GraphRelationship(
            id=None,  # New ID will be generated
            workspace_id=self.workspace_id,
            source_id=self.target_id,
            target_id=self.source_id,
            relation_type=reverse_type,
            properties=self.properties.copy(),
            weight=self.weight,
        )

    def get_reverse_type(self) -> RelationType:
        """Get the reverse relationship type."""
        reverse_mapping = {
            RelationType.HAS_ICP: RelationType.PART_OF,
            RelationType.COMPETES_WITH: RelationType.COMPETES_WITH,
            RelationType.USES_CHANNEL: RelationType.TARGETS,
            RelationType.SOLVES_PAIN: RelationType.RELATED_TO,
            RelationType.HAS_USP: RelationType.RELATED_TO,
            RelationType.HAS_FEATURE: RelationType.RELATED_TO,
            RelationType.TARGETS: RelationType.USES_CHANNEL,
            RelationType.PART_OF: RelationType.HAS_ICP,
            RelationType.CREATED_BY: RelationType.RELATED_TO,
            RelationType.MENTIONS: RelationType.RELATED_TO,
            RelationType.RELATED_TO: RelationType.RELATED_TO,
            RelationType.SIMILAR_TO: RelationType.SIMILAR_TO,
        }
        return reverse_mapping.get(self.relation_type, RelationType.RELATED_TO)

    def __str__(self) -> str:
        """String representation."""
        type_str = self.relation_type.value if self.relation_type else "unknown"
        return f"GraphRelationship({type_str}: {self.source_id} -> {self.target_id})"

    def __repr__(self) -> str:
        """Detailed representation."""
        return (
            f"GraphRelationship(id={self.id}, type={self.relation_type}, "
            f"source={self.source_id}, target={self.target_id}, weight={self.weight})"
        )


@dataclass
class SubGraph:
    """A subgraph containing entities and relationships."""

    entities: Dict[str, GraphEntity] = field(default_factory=dict)
    relationships: Dict[str, GraphRelationship] = field(default_factory=dict)
    center_entity_id: Optional[str] = None
    depth: int = 0
    created_at: Optional[datetime] = None

    def __post_init__(self):
        """Initialize default values."""
        if self.created_at is None:
            self.created_at = datetime.now()

    def add_entity(self, entity: GraphEntity):
        """Add an entity to the subgraph."""
        if entity.id:
            self.entities[entity.id] = entity

    def add_relationship(self, relationship: GraphRelationship):
        """Add a relationship to the subgraph."""
        if relationship.id:
            self.relationships[relationship.id] = relationship

    def get_entity(self, entity_id: str) -> Optional[GraphEntity]:
        """Get an entity by ID."""
        return self.entities.get(entity_id)

    def get_relationship(self, relationship_id: str) -> Optional[GraphRelationship]:
        """Get a relationship by ID."""
        return self.relationships.get(relationship_id)

    def get_entity_relationships(self, entity_id: str) -> List[GraphRelationship]:
        """Get all relationships for an entity."""
        relationships = []
        for rel in self.relationships.values():
            if rel.source_id == entity_id or rel.target_id == entity_id:
                relationships.append(rel)
        return relationships

    def get_connected_entities(self, entity_id: str) -> List[GraphEntity]:
        """Get all entities connected to the given entity."""
        connected_ids = set()
        for rel in self.relationships.values():
            if rel.source_id == entity_id:
                connected_ids.add(rel.target_id)
            elif rel.target_id == entity_id:
                connected_ids.add(rel.source_id)

        return [self.entities[eid] for eid in connected_ids if eid in self.entities]

    def get_entity_types(self) -> Dict[EntityType, int]:
        """Get count of entities by type."""
        type_counts = {}
        for entity in self.entities.values():
            if entity.entity_type:
                type_counts[entity.entity_type] = (
                    type_counts.get(entity.entity_type, 0) + 1
                )
        return type_counts

    def get_relationship_types(self) -> Dict[RelationType, int]:
        """Get count of relationships by type."""
        type_counts = {}
        for rel in self.relationships.values():
            if rel.relation_type:
                type_counts[rel.relation_type] = (
                    type_counts.get(rel.relation_type, 0) + 1
                )
        return type_counts

    def is_empty(self) -> bool:
        """Check if subgraph is empty."""
        return len(self.entities) == 0 and len(self.relationships) == 0

    def size(self) -> int:
        """Get total size (entities + relationships)."""
        return len(self.entities) + len(self.relationships)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "entities": {
                eid: entity.to_dict() for eid, entity in self.entities.items()
            },
            "relationships": {
                rid: rel.to_dict() for rid, rel in self.relationships.items()
            },
            "center_entity_id": self.center_entity_id,
            "depth": self.depth,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SubGraph":
        """Create from dictionary."""
        subgraph = cls()

        # Parse entities
        for eid, entity_data in data.get("entities", {}).items():
            entity = GraphEntity.from_dict(entity_data)
            subgraph.entities[eid] = entity

        # Parse relationships
        for rid, rel_data in data.get("relationships", {}).items():
            rel = GraphRelationship.from_dict(rel_data)
            subgraph.relationships[rid] = rel

        subgraph.center_entity_id = data.get("center_entity_id")
        subgraph.depth = data.get("depth", 0)

        if data.get("created_at"):
            subgraph.created_at = datetime.fromisoformat(data["created_at"])

        return subgraph

    def __str__(self) -> str:
        """String representation."""
        return f"SubGraph({len(self.entities)} entities, {len(self.relationships)} relationships)"

    def __repr__(self) -> str:
        """Detailed representation."""
        return (
            f"SubGraph(center={self.center_entity_id}, depth={self.depth}, "
            f"entities={len(self.entities)}, relationships={len(self.relationships)})"
        )


# Type aliases
GraphEntities = Dict[str, GraphEntity]
GraphRelationships = Dict[str, GraphRelationship]
