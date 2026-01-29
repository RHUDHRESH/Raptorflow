"""
Company entity builder for knowledge graph construction.

This module provides the CompanyEntityBuilder class for creating
and linking company entities in the knowledge graph.
"""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from embeddings import get_embedding_model
from graph_memory import GraphMemory
from graph_models import EntityType, GraphEntity, GraphRelationship, RelationType

logger = logging.getLogger(__name__)


class CompanyEntityBuilder:
    """
    Builder for company entities and their relationships.

    Creates company entities and links them to USPs, features,
    channels, and other related entities in the knowledge graph.
    """

    def __init__(self, graph_memory: Optional[GraphMemory] = None):
        """
        Initialize company entity builder.

        Args:
            graph_memory: Graph memory instance
        """
        self.graph_memory = graph_memory or GraphMemory()
        self.embedding_model = get_embedding_model()

    async def build_company_entity(
        self, workspace_id: str, foundation: Dict[str, Any]
    ) -> str:
        """
        Build company entity from foundation data.

        Args:
            workspace_id: Workspace identifier
            foundation: Foundation data dictionary

        Returns:
            Company entity ID
        """
        try:
            # Extract company information
            company_info = self._extract_company_info(foundation)

            # Create company entity
            company_id = await self.graph_memory.add_entity(
                workspace_id=workspace_id,
                entity_type=EntityType.COMPANY,
                name=company_info["name"],
                properties=company_info["properties"],
            )

            # Create relationships to related entities
            await self._create_company_relationships(
                workspace_id, company_id, foundation
            )

            logger.info(
                f"Built company entity {company_id} for workspace {workspace_id}"
            )
            return company_id

        except Exception as e:
            logger.error(f"Error building company entity: {e}")
            raise

    def _extract_company_info(self, foundation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract company information from foundation data.

        Args:
            foundation: Foundation data dictionary

        Returns:
            Company information dictionary
        """
        company_info = {"name": "Unknown Company", "properties": {}}

        # Extract basic company info
        if "company_info" in foundation:
            company_data = foundation["company_info"]
            company_info["name"] = company_data.get("name", "Unknown Company")
            company_info["properties"].update(
                {
                    "description": company_data.get("description", ""),
                    "industry": company_data.get("industry", ""),
                    "size": company_data.get("size", ""),
                    "location": company_data.get("location", ""),
                    "founded": company_data.get("founded", ""),
                    "website": company_data.get("website", ""),
                }
            )

        # Add core foundation elements
        for field in ["mission", "vision", "values"]:
            if field in foundation:
                company_info["properties"][field] = foundation[field]

        return company_info

    async def _create_company_relationships(
        self, workspace_id: str, company_id: str, foundation: Dict[str, Any]
    ):
        """
        Create relationships between company and other entities.

        Args:
            workspace_id: Workspace identifier
            company_id: Company entity ID
            foundation: Foundation data dictionary
        """
        try:
            # Create USP entities and relationships
            await self._create_usp_relationships(workspace_id, company_id, foundation)

            # Create feature entities and relationships
            await self._create_feature_relationships(
                workspace_id, company_id, foundation
            )

            # Create channel entities and relationships
            await self._create_channel_relationships(
                workspace_id, company_id, foundation
            )

            # Create pain point entities and relationships
            await self._create_pain_point_relationships(
                workspace_id, company_id, foundation
            )

        except Exception as e:
            logger.error(f"Error creating company relationships: {e}")

    async def _create_usp_relationships(
        self, workspace_id: str, company_id: str, foundation: Dict[str, Any]
    ):
        """Create USP entities and relationships."""
        usps = foundation.get("usps", [])
        if isinstance(usps, str):
            usps = [usps]

        for usp in usps:
            if isinstance(usp, str):
                usp_text = usp
                usp_props = {}
            elif isinstance(usp, dict):
                usp_text = usp.get("text", usp.get("description", ""))
                usp_props = {
                    k: v for k, v in usp.items() if k not in ["text", "description"]
                }
            else:
                continue

            if usp_text:
                # Create USP entity
                usp_id = await self.graph_memory.add_entity(
                    workspace_id=workspace_id,
                    entity_type=EntityType.USP,
                    name=usp_text[:100],  # Limit name length
                    properties={"full_text": usp_text, **usp_props},
                )

                # Create relationship
                await self.graph_memory.add_relationship(
                    source_id=company_id,
                    target_id=usp_id,
                    relation_type=RelationType.HAS_USP,
                    weight=1.0,
                )

    async def _create_feature_relationships(
        self, workspace_id: str, company_id: str, foundation: Dict[str, Any]
    ):
        """Create feature entities and relationships."""
        features = foundation.get("features", [])
        if isinstance(features, str):
            features = [features]

        for feature in features:
            if isinstance(feature, str):
                feature_text = feature
                feature_props = {}
            elif isinstance(feature, dict):
                feature_text = feature.get("name", feature.get("description", ""))
                feature_props = {
                    k: v for k, v in feature.items() if k not in ["name", "description"]
                }
            else:
                continue

            if feature_text:
                # Create feature entity
                feature_id = await self.graph_memory.add_entity(
                    workspace_id=workspace_id,
                    entity_type=EntityType.FEATURE,
                    name=feature_text[:100],
                    properties={"full_text": feature_text, **feature_props},
                )

                # Create relationship
                await self.graph_memory.add_relationship(
                    source_id=company_id,
                    target_id=feature_id,
                    relation_type=RelationType.HAS_FEATURE,
                    weight=0.8,
                )

    async def _create_channel_relationships(
        self, workspace_id: str, company_id: str, foundation: Dict[str, Any]
    ):
        """Create channel entities and relationships."""
        channels = foundation.get("channels", [])
        if isinstance(channels, str):
            channels = [channels]

        for channel in channels:
            if isinstance(channel, str):
                channel_text = channel
                channel_props = {}
            elif isinstance(channel, dict):
                channel_text = channel.get("name", channel.get("type", ""))
                channel_props = {
                    k: v for k, v in channel.items() if k not in ["name", "type"]
                }
            else:
                continue

            if channel_text:
                # Create channel entity
                channel_id = await self.graph_memory.add_entity(
                    workspace_id=workspace_id,
                    entity_type=EntityType.CHANNEL,
                    name=channel_text[:100],
                    properties={"full_text": channel_text, **channel_props},
                )

                # Create relationship
                await self.graph_memory.add_relationship(
                    source_id=company_id,
                    target_id=channel_id,
                    relation_type=RelationType.USES_CHANNEL,
                    weight=0.7,
                )

    async def _create_pain_point_relationships(
        self, workspace_id: str, company_id: str, foundation: Dict[str, Any]
    ):
        """Create pain point entities and relationships."""
        pain_points = foundation.get("pain_points_solved", [])
        if isinstance(pain_points, str):
            pain_points = [pain_points]

        for pain_point in pain_points:
            if isinstance(pain_point, str):
                pain_text = pain_point
                pain_props = {}
            elif isinstance(pain_point, dict):
                pain_text = pain_point.get("description", pain_point.get("name", ""))
                pain_props = {
                    k: v
                    for k, v in pain_point.items()
                    if k not in ["description", "name"]
                }
            else:
                continue

            if pain_text:
                # Create pain point entity
                pain_id = await self.graph_memory.add_entity(
                    workspace_id=workspace_id,
                    entity_type=EntityType.PAIN_POINT,
                    name=pain_text[:100],
                    properties={"full_text": pain_text, **pain_props},
                )

                # Create relationship
                await self.graph_memory.add_relationship(
                    source_id=company_id,
                    target_id=pain_id,
                    relation_type=RelationType.SOLVES_PAIN,
                    weight=0.9,
                )

    async def update_company_entity(
        self, workspace_id: str, foundation: Dict[str, Any]
    ) -> str:
        """
        Update company entity with new foundation data.

        Args:
            workspace_id: Workspace identifier
            foundation: Updated foundation data

        Returns:
            Company entity ID
        """
        try:
            # Find existing company entity
            company_entities = await self.graph_memory.find_entities(
                workspace_id=workspace_id, entity_type=EntityType.COMPANY
            )

            if company_entities:
                # Update existing entity
                company_id = company_entities[0].id
                company_info = self._extract_company_info(foundation)

                # Update entity properties
                await self.graph_memory.update_entity(
                    entity_id=company_id,
                    name=company_info["name"],
                    properties=company_info["properties"],
                )

                # Note: In a full implementation, we would also update relationships
                # For now, we'll just update the entity itself

                logger.info(
                    f"Updated company entity {company_id} for workspace {workspace_id}"
                )
                return company_id
            else:
                # Create new entity
                return await self.build_company_entity(workspace_id, foundation)

        except Exception as e:
            logger.error(f"Error updating company entity: {e}")
            raise

    async def get_company_entity(self, workspace_id: str) -> Optional[GraphEntity]:
        """
        Get the company entity for a workspace.

        Args:
            workspace_id: Workspace identifier

        Returns:
            Company entity or None if not found
        """
        try:
            company_entities = await self.graph_memory.find_entities(
                workspace_id=workspace_id, entity_type=EntityType.COMPANY
            )

            return company_entities[0] if company_entities else None

        except Exception as e:
            logger.error(f"Error getting company entity: {e}")
            return None

    async def get_company_relationships(
        self, workspace_id: str, relation_types: Optional[List[RelationType]] = None
    ) -> List[GraphRelationship]:
        """
        Get relationships for the company entity.

        Args:
            workspace_id: Workspace identifier
            relation_types: Optional filter for relation types

        Returns:
            List of relationships
        """
        try:
            company_entity = await self.get_company_entity(workspace_id)
            if not company_entity:
                return []

            return await self.graph_memory.get_relationships(
                entity_id=company_entity.id, direction="both"
            )

        except Exception as e:
            logger.error(f"Error getting company relationships: {e}")
            return []
