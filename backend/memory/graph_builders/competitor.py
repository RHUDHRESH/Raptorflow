"""
Competitor entity builder for knowledge graph construction.

This module provides the CompetitorEntityBuilder class for creating
and linking competitor entities in the knowledge graph.
"""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..embeddings import get_embedding_model
from ..graph_memory import GraphMemory
from ..graph_models import EntityType, GraphEntity, GraphRelationship, RelationType

logger = logging.getLogger(__name__)


class CompetitorEntityBuilder:
    """
    Builder for competitor entities and their relationships.

    Creates competitor entities and links them to the company,
    their features, market position, and competitive intelligence.
    """

    def __init__(self, graph_memory: Optional[GraphMemory] = None):
        """
        Initialize competitor entity builder.

        Args:
            graph_memory: Graph memory instance
        """
        self.graph_memory = graph_memory or GraphMemory()
        self.embedding_model = get_embedding_model()

    async def build_competitor_entity(
        self, workspace_id: str, competitor_data: Dict[str, Any]
    ) -> str:
        """
        Build competitor entity from competitor data.

        Args:
            workspace_id: Workspace identifier
            competitor_data: Competitor data dictionary

        Returns:
            Competitor entity ID
        """
        try:
            # Extract competitor information
            competitor_info = self._extract_competitor_info(competitor_data)

            # Create competitor entity
            competitor_id = await self.graph_memory.add_entity(
                workspace_id=workspace_id,
                entity_type=EntityType.COMPETITOR,
                name=competitor_info["name"],
                properties=competitor_info["properties"],
            )

            # Create relationships to related entities
            await self._create_competitor_relationships(
                workspace_id, competitor_id, competitor_data
            )

            logger.info(
                f"Built competitor entity {competitor_id} for workspace {workspace_id}"
            )
            return competitor_id

        except Exception as e:
            logger.error(f"Error building competitor entity: {e}")
            raise

    def _extract_competitor_info(
        self, competitor_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Extract competitor information from competitor data.

        Args:
            competitor_data: Competitor data dictionary

        Returns:
            Competitor information dictionary
        """
        competitor_info = {
            "name": competitor_data.get("name", "Unknown Competitor"),
            "properties": {},
        }

        # Extract basic competitor info
        for field in [
            "description",
            "industry",
            "size",
            "location",
            "website",
            "founded",
        ]:
            if field in competitor_data:
                competitor_info["properties"][field] = competitor_data[field]

        # Add market position
        if "market_position" in competitor_data:
            competitor_info["properties"]["market_position"] = competitor_data[
                "market_position"
            ]

        # Add strengths and weaknesses
        for field in ["strengths", "weaknesses"]:
            if field in competitor_data:
                competitor_info["properties"][field] = competitor_data[field]

        # Add competitive intelligence
        if "intelligence" in competitor_data:
            competitor_info["properties"]["intelligence"] = competitor_data[
                "intelligence"
            ]

        return competitor_info

    async def _create_competitor_relationships(
        self, workspace_id: str, competitor_id: str, competitor_data: Dict[str, Any]
    ):
        """
        Create relationships between competitor and other entities.

        Args:
            workspace_id: Workspace identifier
            competitor_id: Competitor entity ID
            competitor_data: Competitor data dictionary
        """
        try:
            # Create relationship to company
            await self._create_company_relationship(workspace_id, competitor_id)

            # Create feature entities and relationships
            await self._create_feature_relationships(
                workspace_id, competitor_id, competitor_data
            )

            # Create strength entities and relationships
            await self._create_strength_relationships(
                workspace_id, competitor_id, competitor_data
            )

            # Create weakness entities and relationships
            await self._create_weakness_relationships(
                workspace_id, competitor_id, competitor_data
            )

        except Exception as e:
            logger.error(f"Error creating competitor relationships: {e}")

    async def _create_company_relationship(self, workspace_id: str, competitor_id: str):
        """Create relationship between competitor and company."""
        try:
            # Find company entity
            company_entities = await self.graph_memory.find_entities(
                workspace_id=workspace_id, entity_type=EntityType.COMPANY
            )

            if company_entities:
                company_id = company_entities[0].id

                # Create competitive relationship
                await self.graph_memory.add_relationship(
                    source_id=competitor_id,
                    target_id=company_id,
                    relation_type=RelationType.COMPETES_WITH,
                    weight=1.0,
                )

        except Exception as e:
            logger.error(f"Error creating company relationship: {e}")

    async def _create_feature_relationships(
        self, workspace_id: str, competitor_id: str, competitor_data: Dict[str, Any]
    ):
        """Create feature entities and relationships."""
        features = competitor_data.get("features", [])
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
                    name=f"{feature_text[:100]} (Competitor)",
                    properties={
                        "full_text": feature_text,
                        "source": "competitor",
                        "competitor_feature": True,
                        **feature_props,
                    },
                )

                # Create relationship
                await self.graph_memory.add_relationship(
                    source_id=competitor_id,
                    target_id=feature_id,
                    relation_type=RelationType.HAS_FEATURE,
                    weight=0.8,
                )

    async def _create_strength_relationships(
        self, workspace_id: str, competitor_id: str, competitor_data: Dict[str, Any]
    ):
        """Create strength entities and relationships."""
        strengths = competitor_data.get("strengths", [])
        if isinstance(strengths, str):
            strengths = [strengths]

        for strength in strengths:
            if isinstance(strength, str):
                strength_text = strength
                strength_props = {}
            elif isinstance(strength, dict):
                strength_text = strength.get("description", strength.get("name", ""))
                strength_props = {
                    k: v
                    for k, v in strength.items()
                    if k not in ["description", "name"]
                }
            else:
                continue

            if strength_text:
                # Create strength entity
                strength_id = await self.graph_memory.add_entity(
                    workspace_id=workspace_id,
                    entity_type=EntityType.FEATURE,
                    name=f"Strength: {strength_text[:80]}",
                    properties={
                        "full_text": strength_text,
                        "entity_subtype": "strength",
                        "source": "competitor",
                        **strength_props,
                    },
                )

                # Create relationship
                await self.graph_memory.add_relationship(
                    source_id=competitor_id,
                    target_id=strength_id,
                    relation_type=RelationType.HAS_FEATURE,
                    weight=0.9,
                )

    async def _create_weakness_relationships(
        self, workspace_id: str, competitor_id: str, competitor_data: Dict[str, Any]
    ):
        """Create weakness entities and relationships."""
        weaknesses = competitor_data.get("weaknesses", [])
        if isinstance(weaknesses, str):
            weaknesses = [weaknesses]

        for weakness in weaknesses:
            if isinstance(weakness, str):
                weakness_text = weakness
                weakness_props = {}
            elif isinstance(weakness, dict):
                weakness_text = weakness.get("description", weakness.get("name", ""))
                weakness_props = {
                    k: v
                    for k, v in weakness.items()
                    if k not in ["description", "name"]
                }
            else:
                continue

            if weakness_text:
                # Create weakness entity
                weakness_id = await self.graph_memory.add_entity(
                    workspace_id=workspace_id,
                    entity_type=EntityType.FEATURE,
                    name=f"Weakness: {weakness_text[:80]}",
                    properties={
                        "full_text": weakness_text,
                        "entity_subtype": "weakness",
                        "source": "competitor",
                        **weakness_props,
                    },
                )

                # Create relationship
                await self.graph_memory.add_relationship(
                    source_id=competitor_id,
                    target_id=weakness_id,
                    relation_type=RelationType.HAS_FEATURE,
                    weight=0.7,
                )

    async def update_competitor_entity(
        self, workspace_id: str, competitor_data: Dict[str, Any]
    ) -> str:
        """
        Update competitor entity with new data.

        Args:
            workspace_id: Workspace identifier
            competitor_data: Updated competitor data

        Returns:
            Competitor entity ID
        """
        try:
            # Find existing competitor entity by name
            competitor_name = competitor_data.get("name", "Unknown Competitor")
            competitor_entities = await self.graph_memory.find_entities(
                workspace_id=workspace_id,
                entity_type=EntityType.COMPETITOR,
                name_pattern=competitor_name,
            )

            if competitor_entities:
                # Update existing entity
                competitor_id = competitor_entities[0].id
                competitor_info = self._extract_competitor_info(competitor_data)

                # Update entity properties
                await self.graph_memory.update_entity(
                    entity_id=competitor_id,
                    name=competitor_info["name"],
                    properties=competitor_info["properties"],
                )

                logger.info(
                    f"Updated competitor entity {competitor_id} for workspace {workspace_id}"
                )
                return competitor_id
            else:
                # Create new entity
                return await self.build_competitor_entity(workspace_id, competitor_data)

        except Exception as e:
            logger.error(f"Error updating competitor entity: {e}")
            raise

    async def get_competitor_entities(self, workspace_id: str) -> List[GraphEntity]:
        """
        Get all competitor entities for a workspace.

        Args:
            workspace_id: Workspace identifier

        Returns:
            List of competitor entities
        """
        try:
            return await self.graph_memory.find_entities(
                workspace_id=workspace_id, entity_type=EntityType.COMPETITOR
            )

        except Exception as e:
            logger.error(f"Error getting competitor entities: {e}")
            return []

    async def get_competitor_features(
        self, workspace_id: str, competitor_id: Optional[str] = None
    ) -> List[GraphEntity]:
        """
        Get features associated with competitor entities.

        Args:
            workspace_id: Workspace identifier
            competitor_id: Optional specific competitor entity ID

        Returns:
            List of feature entities
        """
        try:
            if competitor_id:
                # Get features for specific competitor
                relationships = await self.graph_memory.get_relationships(
                    entity_id=competitor_id, direction="outgoing"
                )

                feature_ids = [
                    rel.target_id
                    for rel in relationships
                    if rel.relation_type == RelationType.HAS_FEATURE
                ]

                features = []
                for feature_id in feature_ids:
                    entity = await self.graph_memory.get_entity(feature_id)
                    if entity:
                        features.append(entity)

                return features
            else:
                # Get all competitor features
                all_features = await self.graph_memory.find_entities(
                    workspace_id=workspace_id, entity_type=EntityType.FEATURE
                )

                # Filter for competitor features
                return [
                    feature
                    for feature in all_features
                    if feature.properties
                    and feature.properties.get("competitor_feature")
                ]

        except Exception as e:
            logger.error(f"Error getting competitor features: {e}")
            return []

    async def get_competitor_strengths(
        self, workspace_id: str, competitor_id: Optional[str] = None
    ) -> List[GraphEntity]:
        """
        Get strengths associated with competitor entities.

        Args:
            workspace_id: Workspace identifier
            competitor_id: Optional specific competitor entity ID

        Returns:
            List of strength entities
        """
        try:
            features = await self.get_competitor_features(workspace_id, competitor_id)

            return [
                feature
                for feature in features
                if feature.properties
                and feature.properties.get("entity_subtype") == "strength"
            ]

        except Exception as e:
            logger.error(f"Error getting competitor strengths: {e}")
            return []

    async def get_competitor_weaknesses(
        self, workspace_id: str, competitor_id: Optional[str] = None
    ) -> List[GraphEntity]:
        """
        Get weaknesses associated with competitor entities.

        Args:
            workspace_id: Workspace identifier
            competitor_id: Optional specific competitor entity ID

        Returns:
            List of weakness entities
        """
        try:
            features = await self.get_competitor_features(workspace_id, competitor_id)

            return [
                feature
                for feature in features
                if feature.properties
                and feature.properties.get("entity_subtype") == "weakness"
            ]

        except Exception as e:
            logger.error(f"Error getting competitor weaknesses: {e}")
            return []
