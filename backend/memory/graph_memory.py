"""
Graph memory system for knowledge graph storage and retrieval.

This module provides the GraphMemory class for storing and retrieving
knowledge graph entities and relationships.
"""

import json
import logging
import os
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from .graph_models import (
    EntityType,
    GraphEntity,
    GraphRelationship,
    RelationType,
    SubGraph,
)
from .redis_client import get_redis_client

logger = logging.getLogger(__name__)


class GraphMemory:
    """
    Graph memory system for knowledge graph storage and retrieval.

    Provides storage and retrieval of graph entities and relationships
    with workspace isolation and semantic search capabilities.
    """

    def __init__(self, supabase_client=None, redis_client=None):
        """
        Initialize graph memory system.

        Args:
            supabase_client: Supabase client instance
            redis_client: Redis client instance
        """
        self.supabase_client = supabase_client
        self.redis_client = redis_client or get_redis_client()

        # Initialize Supabase client if not provided
        if self.supabase_client is None:
            self._init_supabase_client()

        # Table names for graph storage
        self._entities_table = "graph_entities"
        self._relationships_table = "graph_relationships"

    def _init_supabase_client(self):
        """Initialize Supabase client from environment variables."""
        try:
            from supabase import create_client

            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

            if supabase_url and supabase_key:
                self.supabase_client = create_client(supabase_url, supabase_key)
                logger.info("Initialized Supabase client for graph memory")
            else:
                logger.warning(
                    "Supabase credentials not found, graph memory will be limited"
                )
                self.supabase_client = None
        except Exception as e:
            logger.error(f"Failed to initialize Supabase client: {e}")
            self.supabase_client = None

    async def store_entity(self, entity: GraphEntity) -> str:
        """
        Store an entity in graph memory.

        Args:
            entity: GraphEntity to store

        Returns:
            Entity ID
        """
        if not self.supabase_client:
            raise DatabaseError(
                "Supabase client required for entity storage - no fallbacks allowed"
            )

        try:
            # Generate ID if not provided
            if not entity.id:
                entity.id = str(uuid.uuid4())

            # Store in Supabase
            data = entity.to_dict()

            result = (
                self.supabase_client.table(self._entities_table).insert(data).execute()
            )

            if result.data:
                return result.data[0]["id"]
            else:
                raise DatabaseError("Failed to store entity in Supabase")

        except Exception as e:
            logger.error(f"Failed to store entity in Supabase: {e}")
            raise DatabaseError(
                f"Supabase required for entity storage - no fallbacks: {e}"
            )

    async def _store_entity_redis(self, entity: GraphEntity) -> str:
        """Store entity in Redis."""
        try:
            if not entity.id:
                entity.id = str(uuid.uuid4())

            key = f"graph:entity:{entity.workspace_id}:{entity.id}"

            data = {"entity": entity.to_dict(), "stored_at": datetime.now().isoformat()}

            await self.redis_client.setex(
                key=key, value=json.dumps(data), ex=86400  # 24 hours
            )

            return entity.id

        except Exception as e:
            logger.error(f"Failed to store entity in Redis: {e}")
            raise DatabaseError(f"Failed to store entity: {e}")

    async def store_relationship(self, relationship: GraphRelationship) -> str:
        """
        Store a relationship in graph memory.

        Args:
            relationship: GraphRelationship to store

        Returns:
            Relationship ID
        """
        if not self.supabase_client:
            raise DatabaseError(
                "Supabase client required for relationship storage - no fallbacks allowed"
            )

        try:
            # Generate ID if not provided
            if not relationship.id:
                relationship.id = str(uuid.uuid4())

            # Store in Supabase
            data = relationship.to_dict()

            result = (
                self.supabase_client.table(self._relationships_table)
                .insert(data)
                .execute()
            )

            if result.data:
                return result.data[0]["id"]
            else:
                raise DatabaseError("Failed to store relationship in Supabase")

        except Exception as e:
            logger.error(f"Failed to store relationship in Supabase: {e}")
            raise DatabaseError(
                f"Supabase required for relationship storage - no fallbacks: {e}"
            )

    async def _store_relationship_redis(self, relationship: GraphRelationship) -> str:
        """Store relationship in Redis."""
        try:
            if not relationship.id:
                relationship.id = str(uuid.uuid4())

            key = f"graph:relationship:{relationship.workspace_id}:{relationship.id}"

            data = {
                "relationship": relationship.to_dict(),
                "stored_at": datetime.now().isoformat(),
            }

            await self.redis_client.setex(
                key=key, value=json.dumps(data), ex=86400  # 24 hours
            )

            return relationship.id

        except Exception as e:
            logger.error(f"Failed to store relationship in Redis: {e}")
            raise DatabaseError(f"Failed to store relationship: {e}")

    async def get_entity(
        self, entity_id: str, workspace_id: str
    ) -> Optional[GraphEntity]:
        """
        Retrieve an entity by ID.

        Args:
            entity_id: Entity ID
            workspace_id: Workspace ID for security

        Returns:
            GraphEntity object or None if not found
        """
        if not self.supabase_client:
            raise DatabaseError(
                "Supabase client required for entity retrieval - no fallbacks allowed"
            )

        try:
            result = (
                self.supabase_client.table(self._entities_table)
                .select("*")
                .eq("id", entity_id)
                .eq("workspace_id", workspace_id)
                .execute()
            )

            if result.data:
                entity_data = result.data[0]
                return GraphEntity.from_dict(entity_data)
            else:
                return None

        except Exception as e:
            logger.error(f"Failed to retrieve entity from Supabase: {e}")
            raise DatabaseError(
                f"Supabase required for entity retrieval - no fallbacks: {e}"
            )

    async def _get_entity_redis(
        self, entity_id: str, workspace_id: str
    ) -> Optional[GraphEntity]:
        """Retrieve entity from Redis."""
        try:
            key = f"graph:entity:{workspace_id}:{entity_id}"

            data = await self.redis_client.get(key)

            if data:
                entity_data = json.loads(data)
                entity_data = entity_data.get("entity")
                return GraphEntity.from_dict(entity_data)
            else:
                return None

        except Exception as e:
            logger.error(f"Failed to retrieve entity from Redis: {e}")
            return None

    async def get_relationship(
        self, relationship_id: str, workspace_id: str
    ) -> Optional[GraphRelationship]:
        """
        Retrieve a relationship by ID.

        Args:
            relationship_id: Relationship ID
            workspace_id: Workspace ID for security

        Returns:
            GraphRelationship object or None if not found
        """
        if not self.supabase_client:
            raise DatabaseError(
                "Supabase client required for relationship retrieval - no fallbacks allowed"
            )

        try:
            result = (
                self.supabase_client.table(self._relationships_table)
                .select("*")
                .eq("id", relationship_id)
                .eq("workspace_id", workspace_id)
                .execute()
            )

            if result.data:
                relationship_data = result.data[0]
                return GraphRelationship.from_dict(relationship_data)
            else:
                return None

        except Exception as e:
            logger.error(f"Failed to retrieve relationship from Supabase: {e}")
            raise DatabaseError(
                f"Supabase required for relationship retrieval - no fallbacks: {e}"
            )

    async def _get_relationship_redis(
        self, relationship_id: str, workspace_id: str
    ) -> Optional[GraphRelationship]:
        """Retrieve relationship from Redis."""
        try:
            key = f"graph:relationship:{workspace_id}:{relationship_id}"

            data = await self.redis_client.get(key)

            if data:
                relationship_data = json.loads(data)
                relationship_data = relationship_data.get("relationship")
                return GraphRelationship.from_dict(relationship_data)
            else:
                return None

        except Exception as e:
            logger.error(f"Failed to retrieve relationship from Redis: {e}")
            return None

    async def search_entities(
        self,
        workspace_id: str,
        query: str,
        entity_types: Optional[List[str]] = None,
        limit: int = 10,
    ) -> List[GraphEntity]:
        """
        Search entities by text query.

        Args:
            workspace_id: Workspace ID for security
            query: Search query text
            entity_types: Optional list of entity types to filter by
            limit: Maximum number of results

        Returns:
            List of matching entities
        """
        if self.supabase_client:
            try:
                # For now, we'll use a simple text-based search
                result = (
                    self.supabase.table(self._entities_table)
                    .select("*")
                    .eq("workspace_id", workspace_id)
                )

                # Add type filtering if specified
                if entity_types:
                    for entity_type in entity_types:
                        result = result.or_("entity_type", "eq", entity_type)

                # Add text search
                if query:
                    result = result.or_("name", "ilike", f"%{query}%")
                    result = result.or_("description", "ilike", f"%{query}%")

                # Order by created_at desc
                result = result.order("created_at", desc=True).limit(limit)

                entities_data = result.execute()

                entities = []
                for entity_data in entities_data:
                    entity = GraphEntity.from_dict(entity_data)

                    # Simple relevance scoring based on text matching
                    if query:
                        if (
                            query.lower() in entity.name.lower()
                            or query.lower() in entity.description.lower()
                        ):
                            entities.append(entity)

                return entities[:limit]

            except Exception as e:
                logger.error(f"Failed to search entities in Supabase: {e}")

        # Fallback to Redis search
        return await self._search_entities_redis(
            workspace_id, query, entity_types, limit
        )

    async def _search_entities_redis(
        self,
        workspace_id: str,
        query: str,
        entity_types: Optional[List[str]] = None,
        limit: int = 10,
    ) -> List[GraphEntity]:
        """Search entities in Redis."""
        try:
            # Get all entity keys for workspace
            pattern = f"graph:entity:{workspace_id}:*"
            keys = await self.redis_client.keys(pattern)

            entities = []

            for key in keys:
                try:
                    data = await self.redis_client.get(key)
                    if data:
                        entity_data = json.loads(data)
                        entity_data = entity_data.get("entity")
                        entity = GraphEntity.from_dict(entity_data)

                        # Filter by type if specified
                        if (
                            entity_types
                            and entity.entity_type.value not in entity_types
                        ):
                            continue

                        # Simple text matching
                        if (
                            query
                            and query.lower() not in entity.name.lower()
                            and query.lower() not in entity.description.lower()
                        ):
                            continue

                        entities.append(entity)

                except Exception as e:
                    logger.error(f"Error parsing entity data: {e}")
                    continue

            # Sort by created_at
            entities.sort(key=lambda x: x.created_at, reverse=True)
            return entities[:limit]

        except Exception as e:
            logger.error(f"Failed to search entities in Redis: {e}")
            return []

    async def get_entity_relationships(
        self,
        entity_id: str,
        workspace_id: str,
        relationship_types: Optional[List[str]] = None,
        limit: int = 50,
    ) -> List[GraphRelationship]:
        """
        Get all relationships for an entity.

        Args:
            entity_id: Entity ID
            workspace_id: Workspace ID for security
            relationship_types: Optional list of relationship types to filter by
            limit: Maximum number of relationships

        Returns:
            List of relationships
        """
        if self.supabase_client:
            try:
                result = (
                    self.supabase.table(self._relationships_table)
                    .select("*")
                    .eq("workspace_id", workspace_id)
                )

                # Filter by source or target entity
                result = result.or_("source_entity_id", "eq", entity_id)
                result = result.or_("target_entity_id", "eq", entity_id)

                # Add type filtering if specified
                if relationship_types:
                    for rel_type in relationship_types:
                        result = result.or_("relationship_type", "eq", rel_type)

                # Order by created_at desc
                result = result.order("created_at", desc=True).limit(limit)

                relationships_data = result.execute()

                relationships = []
                for rel_data in relationships_data:
                    relationship = GraphRelationship.from_dict(rel_data)
                    relationships.append(relationship)

                return relationships

            except Exception as e:
                logger.error(f"Failed to get relationships from Supabase: {e}")

        # Fallback to Redis
        return await self._get_entity_relationships_redis(
            entity_id, workspace_id, relationship_types, limit
        )

    async def _get_entity_relationships_redis(
        self,
        entity_id: str,
        workspace_id: str,
        relationship_types: Optional[List[str]] = None,
        limit: int = 50,
    ) -> List[GraphRelationship]:
        """Get entity relationships from Redis."""
        try:
            # Get all relationship keys for workspace
            pattern = f"graph:relationship:{workspace_id}:*"
            keys = await self.redis_client.keys(pattern)

            relationships = []

            for key in keys:
                try:
                    data = await self.redis_client.get(key)
                    if data:
                        relationship_data = json.loads(data)
                        relationship_data = relationship_data.get("relationship")
                        relationship = GraphRelationship.from_dict(relationship_data)

                        # Filter by source or target entity
                        if (
                            relationship.source_entity_id != entity_id
                            and relationship.target_entity_id != entity_id
                        ):
                            continue

                        # Filter by type if specified
                        if (
                            relationship_types
                            and relationship.relationship_type.value
                            not in relationship_types
                        ):
                            continue

                        relationships.append(relationship)

                except Exception as e:
                    logger.error(f"Error parsing relationship data: {e}")
                    continue

            # Sort by created_at
            relationships.sort(key=lambda x: x.created_at, reverse=True)
            return relationships[:limit]

        except Exception as e:
            logger.error(f"Failed to get relationships from Redis: {e}")
            return []

    async def get_subgraph(
        self,
        workspace_id: str,
        entity_ids: List[str],
        max_depth: int = 2,
        limit: int = 100,
    ) -> SubGraph:
        """
        Get a subgraph containing entities and their relationships.

        Args:
            workspace_id: Workspace ID for security
            entity_ids: List of entity IDs to include
            max_depth: Maximum depth of relationships to include
            limit: Maximum number of entities

        Returns:
            SubGraph object
        """
        try:
            subgraph = SubGraph()
            visited_entities = set()
            queue = entity_ids.copy()

            while queue and len(subgraph.entities) < limit:
                current_entity_id = queue.pop(0)

                if current_entity_id in visited_entities:
                    continue

                visited_entities.add(current_entity_id)

                # Get entity
                entity = await self.get_entity(current_entity_id, workspace_id)
                if entity:
                    subgraph.entities[current_entity_id] = entity

                    # Get relationships
                    if max_depth > 0:
                        relationships = await self.get_entity_relationships(
                            current_entity_id, workspace_id, limit=limit
                        )

                        for relationship in relationships:
                            subgraph.relationships[relationship.id] = relationship

                            # Add connected entities to queue
                            if relationship.source_entity_id not in visited_entities:
                                queue.append(relationship.source_entity_id)
                            if relationship.target_entity_id not in visited_entities:
                                queue.append(relationship.target_entity_id)

            return subgraph

        except Exception as e:
            logger.error(f"Failed to get subgraph: {e}")
            return SubGraph()

    async def delete_entity(self, entity_id: str, workspace_id: str) -> bool:
        """
        Delete an entity and its relationships.

        Args:
            entity_id: Entity ID
            workspace_id: Workspace ID for security

        Returns:
            True if deleted, False otherwise
        """
        try:
            # Delete relationships first
            relationships = await self.get_entity_relationships(entity_id, workspace_id)
            for relationship in relationships:
                await self.delete_relationship(relationship.id, workspace_id)

            # Delete entity
            if self.supabase_client:
                result = (
                    self.supabase.table(self._entities_table)
                    .delete()
                    .eq("id", entity_id)
                    .eq("workspace_id", workspace_id)
                    .execute()
                )
                entity_deleted = result.count > 0
            else:
                # Redis fallback
                key = f"graph:entity:{workspace_id}:{entity_id}"
                entity_deleted = await self.redis_client.delete(key)

            return entity_deleted

        except Exception as e:
            logger.error(f"Failed to delete entity: {e}")
            return False

    async def delete_relationship(
        self, relationship_id: str, workspace_id: str
    ) -> bool:
        """
        Delete a relationship.

        Args:
            relationship_id: Relationship ID
            workspace_id: Workspace ID for security

        Returns:
            True if deleted, False otherwise
        """
        if self.supabase_client:
            try:
                result = (
                    self.supabase.table(self._relationships_table)
                    .delete()
                    .eq("id", relationship_id)
                    .eq("workspace_id", workspace_id)
                    .execute()
                )
                return result.count > 0
            except Exception as e:
                logger.error(f"Failed to delete relationship from Supabase: {e}")

        # Fallback to Redis
        try:
            key = f"graph:relationship:{workspace_id}:{relationship_id}"
            result = await self.redis_client.delete(key)
            return result
        except Exception as e:
            logger.error(f"Failed to delete relationship from Redis: {e}")
            return False

    async def get_memory_stats(self, workspace_id: str) -> Dict[str, Any]:
        """
        Get statistics about graph memory usage.

        Args:
            workspace_id: Workspace ID

        Returns:
            Dictionary with memory statistics
        """
        try:
            # Get all entity keys for workspace
            entity_pattern = f"graph:entity:{workspace_id}:*"
            entity_keys = await self.redis_client.keys(entity_pattern)

            # Get all relationship keys for workspace
            relationship_pattern = f"graph:relationship:{workspace_id}:*"
            relationship_keys = await self.redis_client.keys(relationship_pattern)

            # Count entity types
            entity_types = {}
            for key in entity_keys:
                try:
                    data = await self.redis_client.get(key)
                    if data:
                        entity_data = json.loads(data)
                        entity_data = entity_data.get("entity")

                        if entity_data:
                            entity_type = entity_data.get("entity_type", "unknown")
                            entity_types[entity_type] = (
                                entity_types.get(entity_type, 0) + 1
                            )

                except Exception as e:
                    logger.error(f"Error checking entity type: {e}")
                    continue

            # Count relationship types
            relationship_types = {}
            for key in relationship_keys:
                try:
                    data = await self.redis_client.get(key)
                    if data:
                        relationship_data = json.loads(data)
                        relationship_data = relationship_data.get("relationship")

                        if relationship_data:
                            rel_type = relationship_data.get(
                                "relationship_type", "unknown"
                            )
                            relationship_types[rel_type] = (
                                relationship_types.get(rel_type, 0) + 1
                            )

                except Exception as e:
                    logger.error(f"Error checking relationship type: {e}")
                    continue

            return {
                "total_entities": len(entity_keys),
                "total_relationships": len(relationship_keys),
                "entity_types": entity_types,
                "relationship_types": relationship_types,
                "storage_type": "redis" if not self.supabase_client else "supabase",
            }

        except Exception as e:
            logger.error(f"Failed to get memory stats: {e}")
            return {
                "total_entities": 0,
                "total_relationships": 0,
                "entity_types": {},
                "relationship_types": {},
                "storage_type": "unknown",
            }

    def __str__(self) -> str:
        """String representation."""
        storage_type = "Supabase" if self.supabase_client else "Redis"
        return f"GraphMemory(storage={storage_type})"


# Convenience functions
def get_graph_memory(supabase_client=None, redis_client=None) -> GraphMemory:
    """Get graph memory instance."""
    return GraphMemory(supabase_client, redis_client)


def create_entity(
    workspace_id: str,
    entity_type: EntityType,
    name: str,
    description: str = "",
    properties: Optional[Dict[str, Any]] = None,
    confidence: float = 1.0,
) -> GraphEntity:
    """Create a new graph entity."""
    entity = GraphEntity(
        workspace_id=workspace_id,
        entity_type=entity_type,
        name=name,
        description=description,
        properties=properties or {},
        confidence=confidence,
    )
    return entity


def create_relationship(
    workspace_id: str,
    source_entity_id: str,
    target_entity_id: str,
    relationship_type: RelationType,
    properties: Optional[Dict[str, Any]] = None,
    confidence: float = 1.0,
) -> GraphRelationship:
    """Create a new graph relationship."""
    relationship = GraphRelationship(
        workspace_id=workspace_id,
        source_entity_id=source_entity_id,
        target_entity_id=target_entity_id,
        relationship_type=relationship_type,
        properties=properties or {},
        confidence=confidence,
    )
    return relationship
