"""
ICP entity builder for knowledge graph construction.

This module provides the ICPEntityBuilder class for creating
and linking ICP entities in the knowledge graph.
"""

import logging
import uuid
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..embeddings import get_embedding_model
from ..graph_memory import GraphMemory
from ..graph_models import EntityType, GraphEntity, GraphRelationship, RelationType

logger = logging.getLogger(__name__)


class ICPEntityBuilder:
    """
    Builder for ICP (Ideal Customer Profile) entities and their relationships.

    Creates ICP entities and links them to pain points, channels,
    behaviors, and other related entities in the knowledge graph.
    """

    def __init__(self, graph_memory: Optional[GraphMemory] = None):
        """
        Initialize ICP entity builder.

        Args:
            graph_memory: Graph memory instance
        """
        self.graph_memory = graph_memory or GraphMemory()
        self.embedding_model = get_embedding_model()

    async def build_icp_entity(
        self, workspace_id: str, icp_profile: Dict[str, Any]
    ) -> str:
        """
        Build ICP entity from ICP profile data.

        Args:
            workspace_id: Workspace identifier
            icp_profile: ICP profile data dictionary

        Returns:
            ICP entity ID
        """
        try:
            # Extract ICP information
            icp_info = self._extract_icp_info(icp_profile)

            # Create ICP entity
            icp_id = await self.graph_memory.add_entity(
                workspace_id=workspace_id,
                entity_type=EntityType.ICP,
                name=icp_info["name"],
                properties=icp_info["properties"],
            )

            # Create relationships to related entities
            await self._create_icp_relationships(workspace_id, icp_id, icp_profile)

            logger.info(f"Built ICP entity {icp_id} for workspace {workspace_id}")
            return icp_id

        except Exception as e:
            logger.error(f"Error building ICP entity: {e}")
            raise

    def _extract_icp_info(self, icp_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract ICP information from ICP profile data.

        Args:
            icp_profile: ICP profile data dictionary

        Returns:
            ICP information dictionary
        """
        icp_info = {"name": "Unnamed ICP", "properties": {}}

        # Extract basic ICP info
        if "basic_info" in icp_profile:
            basic_data = icp_profile["basic_info"]
            icp_info["name"] = basic_data.get("name", "Unnamed ICP")
            icp_info["properties"].update(
                {
                    "description": basic_data.get("description", ""),
                    "industry": basic_data.get("industry", ""),
                    "size": basic_data.get("size", ""),
                    "location": basic_data.get("location", ""),
                }
            )

        # Add demographic information
        for field in ["demographics", "psychographics", "behaviors"]:
            if field in icp_profile:
                icp_info["properties"][field] = icp_profile[field]

        # Add firmographics if present
        if "firmographics" in icp_profile:
            icp_info["properties"]["firmographics"] = icp_profile["firmographics"]

        return icp_info

    async def _create_icp_relationships(
        self, workspace_id: str, icp_id: str, icp_profile: Dict[str, Any]
    ):
        """
        Create relationships between ICP and other entities.

        Args:
            workspace_id: Workspace identifier
            icp_id: ICP entity ID
            icp_profile: ICP profile data dictionary
        """
        try:
            # Create pain point entities and relationships
            await self._create_pain_point_relationships(
                workspace_id, icp_id, icp_profile
            )

            # Create channel entities and relationships
            await self._create_channel_relationships(workspace_id, icp_id, icp_profile)

            # Create goal entities and relationships
            await self._create_goal_relationships(workspace_id, icp_id, icp_profile)

            # Create behavior entities and relationships
            await self._create_behavior_relationships(workspace_id, icp_id, icp_profile)

        except Exception as e:
            logger.error(f"Error creating ICP relationships: {e}")

    async def _create_pain_point_relationships(
        self, workspace_id: str, icp_id: str, icp_profile: Dict[str, Any]
    ):
        """Create pain point entities and relationships."""
        pain_points = icp_profile.get("pain_points", [])
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
                    properties={
                        "full_text": pain_text,
                        "source": "icp_profile",
                        **pain_props,
                    },
                )

                # Create relationship
                await self.graph_memory.add_relationship(
                    source_id=icp_id,
                    target_id=pain_id,
                    relation_type=RelationType.HAS_PAIN_POINT,
                    weight=1.0,
                )

    async def _create_channel_relationships(
        self, workspace_id: str, icp_id: str, icp_profile: Dict[str, Any]
    ):
        """Create channel entities and relationships."""
        channels = icp_profile.get("channels", [])
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
                    properties={
                        "full_text": channel_text,
                        "source": "icp_profile",
                        **channel_props,
                    },
                )

                # Create relationship
                await self.graph_memory.add_relationship(
                    source_id=icp_id,
                    target_id=channel_id,
                    relation_type=RelationType.USES_CHANNEL,
                    weight=0.8,
                )

    async def _create_goal_relationships(
        self, workspace_id: str, icp_id: str, icp_profile: Dict[str, Any]
    ):
        """Create goal entities and relationships."""
        goals = icp_profile.get("goals", [])
        if isinstance(goals, str):
            goals = [goals]

        for goal in goals:
            if isinstance(goal, str):
                goal_text = goal
                goal_props = {}
            elif isinstance(goal, dict):
                goal_text = goal.get("description", goal.get("name", ""))
                goal_props = {
                    k: v for k, v in goal.items() if k not in ["description", "name"]
                }
            else:
                continue

            if goal_text:
                # Create goal entity (use feature as general entity type for goals)
                goal_id = await self.graph_memory.add_entity(
                    workspace_id=workspace_id,
                    entity_type=EntityType.FEATURE,
                    name=goal_text[:100],
                    properties={
                        "full_text": goal_text,
                        "entity_subtype": "goal",
                        "source": "icp_profile",
                        **goal_props,
                    },
                )

                # Create relationship
                await self.graph_memory.add_relationship(
                    source_id=icp_id,
                    target_id=goal_id,
                    relation_type=RelationType.TARGETS,
                    weight=0.9,
                )

    async def _create_behavior_relationships(
        self, workspace_id: str, icp_id: str, icp_profile: Dict[str, Any]
    ):
        """Create behavior entities and relationships."""
        behaviors = icp_profile.get("behaviors", [])
        if isinstance(behaviors, str):
            behaviors = [behaviors]

        for behavior in behaviors:
            if isinstance(behavior, str):
                behavior_text = behavior
                behavior_props = {}
            elif isinstance(behavior, dict):
                behavior_text = behavior.get("description", behavior.get("name", ""))
                behavior_props = {
                    k: v
                    for k, v in behavior.items()
                    if k not in ["description", "name"]
                }
            else:
                continue

            if behavior_text:
                # Create behavior entity
                behavior_id = await self.graph_memory.add_entity(
                    workspace_id=workspace_id,
                    entity_type=EntityType.FEATURE,
                    name=behavior_text[:100],
                    properties={
                        "full_text": behavior_text,
                        "entity_subtype": "behavior",
                        "source": "icp_profile",
                        **behavior_props,
                    },
                )

                # Create relationship
                await self.graph_memory.add_relationship(
                    source_id=icp_id,
                    target_id=behavior_id,
                    relation_type=RelationType.RELATES_TO,
                    weight=0.7,
                )

    async def update_icp_entity(
        self, workspace_id: str, icp_profile: Dict[str, Any]
    ) -> str:
        """
        Update ICP entity with new profile data.

        Args:
            workspace_id: Workspace identifier
            icp_profile: Updated ICP profile data

        Returns:
            ICP entity ID
        """
        try:
            # Find existing ICP entity by name
            icp_info = self._extract_icp_info(icp_profile)
            icp_entities = await self.graph_memory.find_entities(
                workspace_id=workspace_id,
                entity_type=EntityType.ICP,
                name_pattern=icp_info["name"],
            )

            if icp_entities:
                # Update existing entity
                icp_id = icp_entities[0].id

                # Update entity properties
                await self.graph_memory.update_entity(
                    entity_id=icp_id,
                    name=icp_info["name"],
                    properties=icp_info["properties"],
                )

                logger.info(f"Updated ICP entity {icp_id} for workspace {workspace_id}")
                return icp_id
            else:
                # Create new entity
                return await self.build_icp_entity(workspace_id, icp_profile)

        except Exception as e:
            logger.error(f"Error updating ICP entity: {e}")
            raise

    async def get_icp_entities(self, workspace_id: str) -> List[GraphEntity]:
        """
        Get all ICP entities for a workspace.

        Args:
            workspace_id: Workspace identifier

        Returns:
            List of ICP entities
        """
        try:
            return await self.graph_memory.find_entities(
                workspace_id=workspace_id, entity_type=EntityType.ICP
            )

        except Exception as e:
            logger.error(f"Error getting ICP entities: {e}")
            return []

    async def get_icp_pain_points(
        self, workspace_id: str, icp_id: Optional[str] = None
    ) -> List[GraphEntity]:
        """
        Get pain points associated with ICP entities.

        Args:
            workspace_id: Workspace identifier
            icp_id: Optional specific ICP entity ID

        Returns:
            List of pain point entities
        """
        try:
            if icp_id:
                # Get pain points for specific ICP
                relationships = await self.graph_memory.get_relationships(
                    entity_id=icp_id, direction="outgoing"
                )

                pain_point_ids = [
                    rel.target_id
                    for rel in relationships
                    if rel.relation_type == RelationType.HAS_PAIN_POINT
                ]

                pain_points = []
                for pain_id in pain_point_ids:
                    entity = await self.graph_memory.get_entity(pain_id)
                    if entity:
                        pain_points.append(entity)

                return pain_points
            else:
                # Get all pain points for all ICPs
                return await self.graph_memory.find_entities(
                    workspace_id=workspace_id, entity_type=EntityType.PAIN_POINT
                )

        except Exception as e:
            logger.error(f"Error getting ICP pain points: {e}")
            return []

    async def get_icp_channels(
        self, workspace_id: str, icp_id: Optional[str] = None
    ) -> List[GraphEntity]:
        """
        Get channels associated with ICP entities.

        Args:
            workspace_id: Workspace identifier
            icp_id: Optional specific ICP entity ID

        Returns:
            List of channel entities
        """
        try:
            if icp_id:
                # Get channels for specific ICP
                relationships = await self.graph_memory.get_relationships(
                    entity_id=icp_id, direction="outgoing"
                )

                channel_ids = [
                    rel.target_id
                    for rel in relationships
                    if rel.relation_type == RelationType.USES_CHANNEL
                ]

                channels = []
                for channel_id in channel_ids:
                    entity = await self.graph_memory.get_entity(channel_id)
                    if entity:
                        channels.append(entity)

                return channels
            else:
                # Get all channels for all ICPs
                return await self.graph_memory.find_entities(
                    workspace_id=workspace_id, entity_type=EntityType.CHANNEL
                )

        except Exception as e:
            logger.error(f"Error getting ICP channels: {e}")
            return []
