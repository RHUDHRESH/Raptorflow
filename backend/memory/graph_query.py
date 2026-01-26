"""
Advanced graph querying and visualization system for knowledge graphs.

This module provides sophisticated graph traversal, pattern matching,
and visualization capabilities for the knowledge graph system.
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional, Set, Tuple

from backend.memory.embeddings import get_embedding_model

from .graph_memory import GraphMemory
from .graph_models import (
    EntityType,
    GraphEntity,
    GraphRelationship,
    RelationType,
    SubGraph,
)
from .vector_store import VectorMemory

logger = logging.getLogger(__name__)


@dataclass
class GraphPattern:
    """Graph pattern for pattern matching queries."""

    entity_types: List[EntityType]
    relationship_types: List[RelationType]
    min_depth: int = 1
    max_depth: int = 3
    constraints: Dict[str, Any] = None

    def __post_init__(self):
        if self.constraints is None:
            self.constraints = {}


@dataclass
class PatternMatch:
    """Result of a pattern matching query."""

    matched_entities: List[GraphEntity]
    matched_relationships: List[GraphRelationship]
    confidence_score: float
    match_details: Dict[str, Any]


@dataclass
class PathResult:
    """Result of a path finding query."""

    path_entities: List[GraphEntity]
    path_relationships: List[GraphRelationship]
    total_weight: float
    path_length: int


@dataclass
class GraphAnalytics:
    """Analytics about the knowledge graph."""

    entity_counts: Dict[EntityType, int]
    relationship_counts: Dict[RelationType, int]
    connectivity_metrics: Dict[str, float]
    central_entities: List[Tuple[str, float]]  # (entity_id, centrality_score)
    clusters: List[List[str]]  # List of entity clusters


class GraphQueryEngine:
    """
    Advanced graph querying engine with pattern matching and analytics.

    Provides sophisticated graph traversal, pattern matching,
    path finding, and visualization capabilities.
    """

    def __init__(self, graph_memory: GraphMemory, vector_memory: VectorMemory):
        """
        Initialize graph query engine.

        Args:
            graph_memory: Graph memory instance
            vector_memory: Vector memory instance for semantic search
        """
        self.graph_memory = graph_memory
        self.vector_memory = vector_memory
        self.embedding_model = get_embedding_model()

        # Cache for frequently accessed data
        self._entity_cache = {}
        self._relationship_cache = {}
        self._cache_expiry = 300  # 5 minutes

    async def find_path(
        self,
        workspace_id: str,
        from_entity_id: str,
        to_entity_id: str,
        max_depth: int = 5,
        weight_function: str = "shortest",
    ) -> Optional[PathResult]:
        """
        Find path between two entities using BFS or weighted algorithms.

        Args:
            workspace_id: Workspace identifier
            from_entity_id: Starting entity ID
            to_entity_id: Target entity ID
            max_depth: Maximum search depth
            weight_function: Weight function ('shortest', 'weighted', 'semantic')

        Returns:
            PathResult if path found, None otherwise
        """
        try:
            # Get entities
            from_entity = await self.graph_memory.get_entity(
                from_entity_id, workspace_id
            )
            to_entity = await self.graph_memory.get_entity(to_entity_id, workspace_id)

            if not from_entity or not to_entity:
                return None

            # BFS for shortest path
            if weight_function == "shortest":
                return await self._find_shortest_path(
                    workspace_id, from_entity, to_entity, max_depth
                )
            elif weight_function == "weighted":
                return await self._find_weighted_path(
                    workspace_id, from_entity, to_entity, max_depth
                )
            elif weight_function == "semantic":
                return await self._find_semantic_path(
                    workspace_id, from_entity, to_entity, max_depth
                )
            else:
                return await self._find_shortest_path(
                    workspace_id, from_entity, to_entity, max_depth
                )

        except Exception as e:
            logger.error(f"Error finding path: {e}")
            return None

    async def _find_shortest_path(
        self,
        workspace_id: str,
        from_entity: GraphEntity,
        to_entity: GraphEntity,
        max_depth: int,
    ) -> Optional[PathResult]:
        """Find shortest path using BFS algorithm."""
        from collections import deque

        queue = deque([(from_entity, [from_entity], [])])
        visited = {from_entity.id}

        while queue and len(queue[0][1]) <= max_depth:
            current_entity, path, relationships = queue.popleft()

            if current_entity.id == to_entity.id:
                return PathResult(
                    path_entities=path,
                    path_relationships=relationships,
                    total_weight=len(relationships),
                    path_length=len(path) - 1,
                )

            # Get neighbors
            neighbors = await self.graph_memory.get_relationships(
                current_entity.id, workspace_id
            )

            for rel in neighbors:
                next_entity_id = (
                    rel.target_id
                    if rel.source_id == current_entity.id
                    else rel.source_id
                )

                if next_entity_id not in visited:
                    visited.add(next_entity_id)
                    next_entity = await self.graph_memory.get_entity(
                        next_entity_id, workspace_id
                    )

                    if next_entity:
                        new_path = path + [next_entity]
                        new_relationships = relationships + [rel]
                        queue.append((next_entity, new_path, new_relationships))

        return None

    async def _find_weighted_path(
        self,
        workspace_id: str,
        from_entity: GraphEntity,
        to_entity: GraphEntity,
        max_depth: int,
    ) -> Optional[PathResult]:
        """Find weighted path using Dijkstra's algorithm."""
        import heapq

        # Priority queue: (total_cost, entity, path, relationships)
        heap = [(0, from_entity, [from_entity], [])]
        visited = {from_entity.id: 0}

        while heap and len(heap[0][2]) <= max_depth:
            total_cost, current_entity, path, relationships = heapq.heappop(heap)

            if current_entity.id == to_entity.id:
                return PathResult(
                    path_entities=path,
                    path_relationships=relationships,
                    total_weight=total_cost,
                    path_length=len(path) - 1,
                )

            # Get neighbors with weights
            neighbors = await self.graph_memory.get_relationships(
                current_entity.id, workspace_id
            )

            for rel in neighbors:
                next_entity_id = (
                    rel.target_id
                    if rel.source_id == current_entity.id
                    else rel.source_id
                )
                weight = rel.weight or 1.0
                new_cost = total_cost + weight

                if next_entity_id not in visited or new_cost < visited[next_entity_id]:
                    visited[next_entity_id] = new_cost
                    next_entity = await self.graph_memory.get_entity(
                        next_entity_id, workspace_id
                    )

                    if next_entity:
                        new_path = path + [next_entity]
                        new_relationships = relationships + [rel]
                        heapq.heappush(
                            heap, (new_cost, next_entity, new_path, new_relationships)
                        )

        return None

    async def _find_semantic_path(
        self,
        workspace_id: str,
        from_entity: GraphEntity,
        to_entity: GraphEntity,
        max_depth: int,
    ) -> Optional[PathResult]:
        """Find path using semantic similarity."""
        # Get entity embeddings
        from_embedding = await self._get_entity_embedding(from_entity)
        to_embedding = await self._get_entity_embedding(to_entity)

        if not from_embedding or not to_embedding:
            return await self._find_shortest_path(
                workspace_id, from_entity, to_entity, max_depth
            )

        # Use BFS with semantic scoring
        from collections import deque

        queue = deque([(from_entity, [from_entity], [], 0.0)])
        visited = {from_entity.id}

        while queue and len(queue[0][1]) <= max_depth:
            current_entity, path, relationships, semantic_score = queue.popleft()

            if current_entity.id == to_entity.id:
                return PathResult(
                    path_entities=path,
                    path_relationships=relationships,
                    total_weight=semantic_score,
                    path_length=len(path) - 1,
                )

            # Get neighbors and calculate semantic similarity
            neighbors = await self.graph_memory.get_relationships(
                current_entity.id, workspace_id
            )

            for rel in neighbors:
                next_entity_id = (
                    rel.target_id
                    if rel.source_id == current_entity.id
                    else rel.source_id
                )

                if next_entity_id not in visited:
                    visited.add(next_entity_id)
                    next_entity = await self.graph_memory.get_entity(
                        next_entity_id, workspace_id
                    )

                    if next_entity:
                        next_embedding = await self._get_entity_embedding(next_entity)
                        if next_embedding:
                            # Calculate semantic similarity
                            similarity = self._cosine_similarity(
                                from_embedding, next_embedding
                            )
                            new_score = semantic_score + (1.0 - similarity)

                            new_path = path + [next_entity]
                            new_relationships = relationships + [rel]
                            queue.append(
                                (next_entity, new_path, new_relationships, new_score)
                            )

        return None

    async def get_subgraph(
        self,
        workspace_id: str,
        center_entity_id: str,
        depth: int = 2,
        max_entities: int = 100,
    ) -> Optional[SubGraph]:
        """
        Get subgraph centered around an entity.

        Args:
            workspace_id: Workspace identifier
            center_entity_id: Center entity ID
            depth: Maximum depth from center
            max_entities: Maximum number of entities

        Returns:
            SubGraph if found, None otherwise
        """
        try:
            center_entity = await self.graph_memory.get_entity(
                center_entity_id, workspace_id
            )
            if not center_entity:
                return None

            # BFS to collect entities and relationships
            from collections import deque

            queue = deque([(center_entity, 0)])
            visited_entities = {center_entity_id: center_entity}
            visited_relationships = []

            while queue and len(visited_entities) < max_entities:
                current_entity, current_depth = queue.popleft()

                if current_depth >= depth:
                    continue

                # Get relationships
                relationships = await self.graph_memory.get_relationships(
                    current_entity.id, workspace_id
                )

                for rel in relationships:
                    if rel.id not in [r.id for r in visited_relationships]:
                        visited_relationships.append(rel)

                    # Get connected entities
                    neighbor_id = (
                        rel.target_id
                        if rel.source_id == current_entity.id
                        else rel.source_id
                    )

                    if neighbor_id not in visited_entities and current_depth < depth:
                        neighbor_entity = await self.graph_memory.get_entity(
                            neighbor_id, workspace_id
                        )
                        if neighbor_entity:
                            visited_entities[neighbor_id] = neighbor_entity
                            queue.append((neighbor_entity, current_depth + 1))

            return SubGraph(
                entities=list(visited_entities.values()),
                relationships=visited_relationships,
            )

        except Exception as e:
            logger.error(f"Error getting subgraph: {e}")
            return None

    async def find_pattern(
        self, workspace_id: str, pattern: GraphPattern, limit: int = 10
    ) -> List[PatternMatch]:
        """
        Find patterns in the knowledge graph.

        Args:
            workspace_id: Workspace identifier
            pattern: Graph pattern to match
            limit: Maximum number of results

        Returns:
            List of pattern matches
        """
        matches = []

        try:
            # Get candidate entities
            candidate_entities = []
            for entity_type in pattern.entity_types:
                entities = await self.graph_memory.find_entities(
                    workspace_id, entity_type
                )
                candidate_entities.extend(entities)

            # Apply constraints
            if pattern.constraints:
                candidate_entities = [
                    entity
                    for entity in candidate_entities
                    if self._matches_constraints(entity, pattern.constraints)
                ]

            # Find pattern matches
            for entity in candidate_entities[:limit]:
                match = await self._match_pattern(workspace_id, entity, pattern)
                if match:
                    matches.append(match)

            return matches

        except Exception as e:
            logger.error(f"Error finding pattern: {e}")
            return []

    async def _match_pattern(
        self, workspace_id: str, start_entity: GraphEntity, pattern: GraphPattern
    ) -> Optional[PatternMatch]:
        """Match a pattern starting from an entity."""
        matched_entities = [start_entity]
        matched_relationships = []

        # Recursive pattern matching
        await self._recursive_pattern_match(
            workspace_id,
            start_entity,
            pattern,
            0,
            matched_entities,
            matched_relationships,
        )

        if len(matched_entities) >= pattern.min_depth:
            # Calculate confidence score
            confidence = self._calculate_pattern_confidence(
                matched_entities, matched_relationships, pattern
            )

            return PatternMatch(
                matched_entities=matched_entities,
                matched_relationships=matched_relationships,
                confidence_score=confidence,
                match_details={
                    "pattern_type": str(pattern.entity_types),
                    "depth": len(matched_entities),
                    "entity_count": len(matched_entities),
                    "relationship_count": len(matched_relationships),
                },
            )

        return None

    async def _recursive_pattern_match(
        self,
        workspace_id: str,
        current_entity: GraphEntity,
        pattern: GraphPattern,
        current_depth: int,
        matched_entities: List[GraphEntity],
        matched_relationships: List[GraphRelationship],
    ):
        """Recursive pattern matching."""
        if current_depth >= pattern.max_depth:
            return

        # Get relationships
        relationships = await self.graph_memory.get_relationships(
            current_entity.id, workspace_id
        )

        for rel in relationships:
            # Check if relationship type matches
            if (
                pattern.relationship_types
                and rel.relation_type not in pattern.relationship_types
            ):
                continue

            # Get connected entity
            neighbor_id = (
                rel.target_id if rel.source_id == current_entity.id else rel.source_id
            )
            neighbor_entity = await self.graph_memory.get_entity(
                neighbor_id, workspace_id
            )

            if neighbor_entity and neighbor_entity.entity_type in pattern.entity_types:
                # Check constraints
                if pattern.constraints and not self._matches_constraints(
                    neighbor_entity, pattern.constraints
                ):
                    continue

                matched_entities.append(neighbor_entity)
                matched_relationships.append(rel)

                # Continue recursion
                await self._recursive_pattern_match(
                    workspace_id,
                    neighbor_entity,
                    pattern,
                    current_depth + 1,
                    matched_entities,
                    matched_relationships,
                )

    def _matches_constraints(
        self, entity: GraphEntity, constraints: Dict[str, Any]
    ) -> bool:
        """Check if entity matches constraints."""
        for key, value in constraints.items():
            if key in entity.properties:
                if entity.properties[key] != value:
                    return False
            elif hasattr(entity, key):
                if getattr(entity, key) != value:
                    return False
        return True

    def _calculate_pattern_confidence(
        self,
        entities: List[GraphEntity],
        relationships: List[GraphRelationship],
        pattern: GraphPattern,
    ) -> float:
        """Calculate confidence score for pattern match."""
        base_score = 0.5

        # Bonus for exact type matches
        type_matches = sum(1 for e in entities if e.entity_type in pattern.entity_types)
        type_score = type_matches / len(entities) if entities else 0

        # Bonus for relationship matches
        rel_matches = sum(
            1 for r in relationships if r.relation_type in pattern.relationship_types
        )
        rel_score = rel_matches / len(relationships) if relationships else 0

        # Depth bonus
        depth_bonus = min(len(entities) / pattern.max_depth, 1.0)

        return base_score + (type_score * 0.3) + (rel_score * 0.2) + (depth_bonus * 0.2)

    async def get_analytics(self, workspace_id: str) -> GraphAnalytics:
        """
        Get analytics about the knowledge graph.

        Args:
            workspace_id: Workspace identifier

        Returns:
            GraphAnalytics object
        """
        try:
            # Get all entities and relationships
            entities = await self.graph_memory.get_all_entities(workspace_id)
            relationships = await self.graph_memory.get_all_relationships(workspace_id)

            # Count entity types
            entity_counts = {}
            for entity in entities:
                entity_counts[entity.entity_type] = (
                    entity_counts.get(entity.entity_type, 0) + 1
                )

            # Count relationship types
            relationship_counts = {}
            for rel in relationships:
                relationship_counts[rel.relation_type] = (
                    relationship_counts.get(rel.relation_type, 0) + 1
                )

            # Calculate connectivity metrics
            connectivity_metrics = self._calculate_connectivity_metrics(
                entities, relationships
            )

            # Calculate central entities (betweenness centrality)
            central_entities = self._calculate_centrality(entities, relationships)

            # Find clusters (simple community detection)
            clusters = self._find_clusters(entities, relationships)

            return GraphAnalytics(
                entity_counts=entity_counts,
                relationship_counts=relationship_counts,
                connectivity_metrics=connectivity_metrics,
                central_entities=central_entities,
                clusters=clusters,
            )

        except Exception as e:
            logger.error(f"Error getting analytics: {e}")
            return GraphAnalytics({}, {}, {}, [], [])

    def _calculate_connectivity_metrics(
        self, entities: List[GraphEntity], relationships: List[GraphRelationship]
    ) -> Dict[str, float]:
        """Calculate graph connectivity metrics."""
        if not entities:
            return {}

        node_count = len(entities)
        edge_count = len(relationships)

        # Density
        max_edges = node_count * (node_count - 1) / 2
        density = edge_count / max_edges if max_edges > 0 else 0

        # Average degree
        avg_degree = (2 * edge_count) / node_count if node_count > 0 else 0

        return {
            "node_count": node_count,
            "edge_count": edge_count,
            "density": density,
            "avg_degree": avg_degree,
        }

    def _calculate_centrality(
        self, entities: List[GraphEntity], relationships: List[GraphRelationship]
    ) -> List[Tuple[str, float]]:
        """Calculate betweenness centrality for entities."""
        centrality = {entity.id: 0.0 for entity in entities}

        # Simple betweenness calculation
        for entity in entities:
            # Count shortest paths that go through this entity
            for other_entity in entities:
                if other_entity.id != entity.id:
                    # Check if entity is on path between other pairs
                    for third_entity in entities:
                        if (
                            third_entity.id != entity.id
                            and third_entity.id != other_entity.id
                        ):
                            # Simplified centrality calculation
                            if self._is_between(
                                entity, other_entity, third_entity, relationships
                            ):
                                centrality[entity.id] += 1

        # Normalize
        max_centrality = max(centrality.values()) if centrality else 1
        if max_centrality > 0:
            centrality = {k: v / max_centrality for k, v in centrality.items()}

        return sorted(centrality.items(), key=lambda x: x[1], reverse=True)[:10]

    def _is_between(
        self,
        entity: GraphEntity,
        source: GraphEntity,
        target: GraphEntity,
        relationships: List[GraphRelationship],
    ) -> bool:
        """Check if entity is between source and target."""
        # Simplified check - in practice, this would use proper path finding
        connected_to_source = any(
            (rel.source_id == source.id and rel.target_id == entity.id)
            or (rel.source_id == entity.id and rel.target_id == source.id)
            for rel in relationships
        )

        connected_to_target = any(
            (rel.source_id == target.id and rel.target_id == entity.id)
            or (rel.source_id == entity.id and rel.target_id == target.id)
            for rel in relationships
        )

        return connected_to_source and connected_to_target

    def _find_clusters(
        self, entities: List[GraphEntity], relationships: List[GraphRelationship]
    ) -> List[List[str]]:
        """Find clusters using simple connected components."""
        visited = set()
        clusters = []

        for entity in entities:
            if entity.id not in visited:
                cluster = []
                self._dfs_cluster(entity.id, entities, relationships, visited, cluster)
                if cluster:
                    clusters.append(cluster)

        return clusters

    def _dfs_cluster(
        self,
        entity_id: str,
        entities: List[GraphEntity],
        relationships: List[GraphRelationship],
        visited: Set[str],
        cluster: List[str],
    ):
        """DFS to find connected component."""
        visited.add(entity_id)
        cluster.append(entity_id)

        # Find connected entities
        for rel in relationships:
            neighbor_id = rel.target_id if rel.source_id == entity_id else rel.source_id
            if neighbor_id not in visited:
                self._dfs_cluster(
                    neighbor_id, entities, relationships, visited, cluster
                )

    async def _get_entity_embedding(self, entity: GraphEntity) -> Optional[List[float]]:
        """Get embedding for entity using vector memory."""
        try:
            # Create searchable text from entity
            text = f"{entity.name} {entity.entity_type}"
            if entity.properties:
                text += " " + " ".join(str(v) for v in entity.properties.values())

            # Get embedding
            embedding = self.embedding_model.encode(text)
            return embedding

        except Exception as e:
            logger.error(f"Error getting entity embedding: {e}")
            return None

    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors."""
        if not vec1 or not vec2:
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        magnitude1 = sum(a * a for a in vec1) ** 0.5
        magnitude2 = sum(a * a for a in vec2) ** 0.5

        if magnitude1 == 0 or magnitude2 == 0:
            return 0.0

        return dot_product / (magnitude1 * magnitude2)

    async def to_d3_format(self, subgraph: SubGraph) -> Dict[str, Any]:
        """
        Convert subgraph to D3.js format for visualization.

        Args:
            subgraph: SubGraph to convert

        Returns:
            D3.js formatted data
        """
        nodes = []
        links = []

        # Convert entities to nodes
        for entity in subgraph.entities:
            nodes.append(
                {
                    "id": entity.id,
                    "name": entity.name,
                    "type": entity.entity_type.value,
                    "properties": entity.properties,
                    "group": entity.entity_type.value,
                }
            )

        # Convert relationships to links
        for rel in subgraph.relationships:
            links.append(
                {
                    "source": rel.source_id,
                    "target": rel.target_id,
                    "type": rel.relation_type.value,
                    "weight": rel.weight or 1.0,
                    "properties": rel.properties,
                }
            )

        return {
            "nodes": nodes,
            "links": links,
            "metadata": {
                "entity_count": len(nodes),
                "relationship_count": len(links),
                "generated_at": datetime.utcnow().isoformat(),
            },
        }

    async def to_cytoscape_format(self, subgraph: SubGraph) -> Dict[str, Any]:
        """
        Convert subgraph to Cytoscape.js format for visualization.

        Args:
            subgraph: SubGraph to convert

        Returns:
            Cytoscape.js formatted data
        """
        elements = []

        # Add nodes
        for entity in subgraph.entities:
            elements.append(
                {
                    "data": {
                        "id": entity.id,
                        "label": entity.name,
                        "type": entity.entity_type.value,
                        "properties": entity.properties,
                    }
                }
            )

        # Add edges
        for rel in subgraph.relationships:
            elements.append(
                {
                    "data": {
                        "id": rel.id,
                        "source": rel.source_id,
                        "target": rel.target_id,
                        "label": rel.relation_type.value,
                        "weight": rel.weight or 1.0,
                        "properties": rel.properties,
                    }
                }
            )

        return {
            "elements": elements,
            "metadata": {
                "node_count": len([e for e in elements if "source" not in e["data"]]),
                "edge_count": len([e for e in elements if "source" in e["data"]]),
                "generated_at": datetime.utcnow().isoformat(),
            },
        }
