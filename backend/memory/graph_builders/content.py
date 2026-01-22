"""
Content entity linker for knowledge graph construction.

This module provides the ContentEntityLinker class for linking
content entities to existing entities in the knowledge graph.
"""

import logging
import re
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..embeddings import get_embedding_model
from ..graph_memory import GraphMemory
from ..graph_models import EntityType, GraphEntity, GraphRelationship, RelationType

logger = logging.getLogger(__name__)


class ContentEntityLinker:
    """
    Linker for content entities to existing knowledge graph entities.

    Extracts entity mentions from content and creates MENTIONS
    relationships between content and the mentioned entities.
    """

    def __init__(self, graph_memory: Optional[GraphMemory] = None):
        """
        Initialize content entity linker.

        Args:
            graph_memory: Graph memory instance
        """
        self.graph_memory = graph_memory or GraphMemory()
        self.embedding_model = get_embedding_model()

        # Common entity mention patterns
        self.mention_patterns = {
            "company": r"\b(inc|corp|corporation|llc|ltd|limited|company|co)\b",
            "competitor": r"\b(competitor|rival|opponent|alternative)\b",
            "feature": r"\b(feature|capability|functionality|attribute|characteristic)\b",
            "usp": r"\b(usp|unique selling proposition|value proposition|differentiator)\b",
            "pain_point": r"\b(pain point|problem|issue|challenge|struggle|difficulty)\b",
            "channel": r"\b(channel|platform|medium|avenue|outlet|distribution)\b",
            "icp": r"\b(icp|ideal customer|target audience|persona|profile)\b",
            "move": r"\b(move|strategy|initiative|campaign|action)\b",
        }

    async def link_content_to_graph(
        self,
        workspace_id: str,
        content_id: str,
        content: str,
        content_type: str = "content",
    ) -> List[str]:
        """
        Link content to graph entities based on entity mentions.

        Args:
            workspace_id: Workspace identifier
            content_id: Content identifier
            content: Content text
            content_type: Type of content (campaign, move, etc.)

        Returns:
            List of created relationship IDs
        """
        try:
            relationship_ids = []

            # Create content entity
            content_entity_id = await self._create_content_entity(
                workspace_id, content_id, content, content_type
            )

            # Extract entity mentions
            entity_mentions = await self._extract_entity_mentions(content)

            # Create relationships for each mention
            for mention in entity_mentions:
                rel_id = await self._create_mention_relationship(
                    workspace_id, content_entity_id, mention
                )
                if rel_id:
                    relationship_ids.append(rel_id)

            logger.info(
                f"Linked content {content_id} to {len(relationship_ids)} entities"
            )
            return relationship_ids

        except Exception as e:
            logger.error(f"Error linking content to graph: {e}")
            return []

    async def _create_content_entity(
        self, workspace_id: str, content_id: str, content: str, content_type: str
    ) -> str:
        """
        Create content entity in the graph.

        Args:
            workspace_id: Workspace identifier
            content_id: Content identifier
            content: Content text
            content_type: Type of content

        Returns:
            Content entity ID
        """
        # Truncate content for entity name
        content_name = content[:100] + "..." if len(content) > 100 else content

        # Determine entity type based on content type
        entity_type = self._map_content_type_to_entity_type(content_type)

        return await self.graph_memory.add_entity(
            workspace_id=workspace_id,
            entity_type=entity_type,
            name=content_name,
            properties={
                "content_id": content_id,
                "full_content": content,
                "content_type": content_type,
                "content_length": len(content),
            },
        )

    def _map_content_type_to_entity_type(self, content_type: str) -> EntityType:
        """
        Map content type to graph entity type.

        Args:
            content_type: Content type string

        Returns:
            Corresponding entity type
        """
        mapping = {
            "campaign": EntityType.CAMPAIGN,
            "move": EntityType.MOVE,
            "research": EntityType.FEATURE,  # Use feature as general type
            "conversation": EntityType.FEATURE,
            "content": EntityType.CONTENT,
        }

        return mapping.get(content_type.lower(), EntityType.CONTENT)

    async def _extract_entity_mentions(self, content: str) -> List[Dict[str, Any]]:
        """
        Extract entity mentions from content.

        Args:
            content: Content text

        Returns:
            List of entity mentions
        """
        mentions = []

        # Extract pattern-based mentions
        for entity_type, pattern in self.mention_patterns.items():
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                mentions.append(
                    {
                        "type": entity_type,
                        "text": match.group(),
                        "position": match.span(),
                        "confidence": 0.7,  # Base confidence for pattern matching
                    }
                )

        # Extract named entities (basic implementation)
        # In a full implementation, this would use NER models
        mentions.extend(self._extract_named_entities(content))

        return mentions

    def _extract_named_entities(self, content: str) -> List[Dict[str, Any]]:
        """
        Extract named entities from content (basic implementation).

        Args:
            content: Content text

        Returns:
            List of named entity mentions
        """
        mentions = []

        # Extract capitalized phrases (potential company/product names)
        capitalized_pattern = r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b"
        matches = re.finditer(capitalized_pattern, content)

        for match in matches:
            text = match.group()
            # Filter out common words
            if text not in [
                "The",
                "This",
                "That",
                "These",
                "Those",
                "And",
                "But",
                "For",
                "With",
            ]:
                mentions.append(
                    {
                        "type": "named_entity",
                        "text": text,
                        "position": match.span(),
                        "confidence": 0.5,
                    }
                )

        return mentions

    async def _create_mention_relationship(
        self, workspace_id: str, content_entity_id: str, mention: Dict[str, Any]
    ) -> Optional[str]:
        """
        Create mention relationship between content and entity.

        Args:
            workspace_id: Workspace identifier
            content_entity_id: Content entity ID
            mention: Entity mention data

        Returns:
            Relationship ID or None if not found
        """
        try:
            # Find existing entities that match the mention
            entity_type = self._map_mention_type_to_entity_type(mention["type"])

            if entity_type:
                # Search for entities by name pattern
                entities = await self.graph_memory.find_entities(
                    workspace_id=workspace_id,
                    entity_type=entity_type,
                    name_pattern=mention["text"],
                )

                if entities:
                    # Create relationship to the first matching entity
                    target_entity = entities[0]

                    return await self.graph_memory.add_relationship(
                        source_id=content_entity_id,
                        target_id=target_entity.id,
                        relation_type=RelationType.MENTIONS,
                        weight=mention["confidence"],
                    )

            return None

        except Exception as e:
            logger.error(f"Error creating mention relationship: {e}")
            return None

    def _map_mention_type_to_entity_type(
        self, mention_type: str
    ) -> Optional[EntityType]:
        """
        Map mention type to graph entity type.

        Args:
            mention_type: Mention type string

        Returns:
            Corresponding entity type or None
        """
        mapping = {
            "company": EntityType.COMPANY,
            "competitor": EntityType.COMPETITOR,
            "feature": EntityType.FEATURE,
            "usp": EntityType.USP,
            "pain_point": EntityType.PAIN_POINT,
            "channel": EntityType.CHANNEL,
            "icp": EntityType.ICP,
            "move": EntityType.MOVE,
            "campaign": EntityType.CAMPAIGN,
        }

        return mapping.get(mention_type)

    async def unlink_content(self, workspace_id: str, content_id: str) -> int:
        """
        Remove all relationships for a content entity.

        Args:
            workspace_id: Workspace identifier
            content_id: Content identifier

        Returns:
            Number of deleted relationships
        """
        try:
            # Find content entity
            entities = await self.graph_memory.find_entities(
                workspace_id=workspace_id, entity_type=EntityType.CONTENT
            )

            content_entities = [
                entity
                for entity in entities
                if entity.properties
                and entity.properties.get("content_id") == content_id
            ]

            deleted_count = 0
            for content_entity in content_entities:
                # Get all relationships
                relationships = await self.graph_memory.get_relationships(
                    entity_id=content_entity.id, direction="both"
                )

                # Delete relationships
                for rel in relationships:
                    await self.graph_memory.delete_relationship(rel.id)
                    deleted_count += 1

                # Delete the content entity itself
                await self.graph_memory.delete_entity(content_entity.id)

            logger.info(
                f"Unlinked content {content_id}, deleted {deleted_count} relationships"
            )
            return deleted_count

        except Exception as e:
            logger.error(f"Error unlinking content: {e}")
            return 0

    async def get_content_relationships(
        self, workspace_id: str, content_id: str
    ) -> List[GraphRelationship]:
        """
        Get all relationships for a content entity.

        Args:
            workspace_id: Workspace identifier
            content_id: Content identifier

        Returns:
            List of relationships
        """
        try:
            # Find content entity
            entities = await self.graph_memory.find_entities(
                workspace_id=workspace_id, entity_type=EntityType.CONTENT
            )

            content_entities = [
                entity
                for entity in entities
                if entity.properties
                and entity.properties.get("content_id") == content_id
            ]

            if not content_entities:
                return []

            content_entity = content_entities[0]

            # Get all relationships
            return await self.graph_memory.get_relationships(
                entity_id=content_entity.id, direction="both"
            )

        except Exception as e:
            logger.error(f"Error getting content relationships: {e}")
            return []

    async def find_related_content(
        self, workspace_id: str, entity_id: str, content_type: Optional[str] = None
    ) -> List[GraphEntity]:
        """
        Find content that mentions a specific entity.

        Args:
            workspace_id: Workspace identifier
            entity_id: Entity ID
            content_type: Optional content type filter

        Returns:
            List of content entities
        """
        try:
            # Get incoming relationships (mentions)
            relationships = await self.graph_memory.get_relationships(
                entity_id=entity_id, direction="incoming"
            )

            # Filter for mention relationships
            mention_relationships = [
                rel
                for rel in relationships
                if rel.relation_type == RelationType.MENTIONS
            ]

            # Get content entities
            content_entities = []
            for rel in mention_relationships:
                content_entity = await self.graph_memory.get_entity(rel.source_id)
                if content_entity:
                    # Apply content type filter if provided
                    if not content_type or (
                        content_entity.properties
                        and content_entity.properties.get("content_type")
                        == content_type
                    ):
                        content_entities.append(content_entity)

            return content_entities

        except Exception as e:
            logger.error(f"Error finding related content: {e}")
            return []
