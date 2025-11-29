"""
Agent Registry Service

Canonical source of truth for core agents (Council of Lords).
Provides idempotent seeding of workspace agents.
"""

import json
from typing import List, Dict, Any, Optional
import uuid

from backend.services.supabase_client import supabase_client
from backend.utils.logging_config import get_logger

logger = get_logger("agent_registry")

# ============================================================================
# CORE AGENT DEFINITIONS
# ============================================================================

# The 7 Council of Lords - canonical manifests
COUNCIL_OF_LORDS = {
    "lord-architect": {
        "name": "Architect Lord",
        "guild": "lord",
        "kind": "lord",
        "description": "System architecture, design, evolution, and knowledge of the complete RaptorFlow system",
        "config": {
            "domain": "architecture",
            "capabilities": ["system_design", "architecture_analysis", "component_optimization", "guidance"],
            "priority": 100,
            "max_concurrent_tasks": 3,
            "memory_context": "complete_system_knowledge",
        },
    },
    "lord-cognition": {
        "name": "Cognition Lord",
        "guild": "lord",
        "kind": "lord",
        "description": "Research, understanding, knowledge acquisition, and learning from data",
        "config": {
            "domain": "cognition",
            "capabilities": ["research", "learning", "knowledge_synthesis", "decision_making"],
            "priority": 95,
            "max_concurrent_tasks": 5,
            "memory_context": "knowledge_base_access",
        },
    },
    "lord-strategos": {
        "name": "Strategos Lord",
        "guild": "lord",
        "kind": "lord",
        "description": "Campaign strategy, prioritization, planning, and tactical execution",
        "config": {
            "domain": "strategy",
            "capabilities": ["campaign_planning", "task_assignment", "resource_allocation", "performance_analysis"],
            "priority": 90,
            "max_concurrent_tasks": 4,
            "memory_context": "strategic_goals",
        },
    },
    "lord-aesthete": {
        "name": "Aesthete Lord",
        "guild": "lord",
        "kind": "lord",
        "description": "Brand, creative quality control, taste validation, and aesthetic oversight",
        "config": {
            "domain": "aesthetics",
            "capabilities": ["quality_review", "brand_enforcement", "creative_feedback", "tone_management"],
            "priority": 85,
            "max_concurrent_tasks": 3,
            "memory_context": "brand_guidelines",
        },
    },
    "lord-seer": {
        "name": "Seer Lord",
        "guild": "lord",
        "kind": "lord",
        "description": "Trend analysis, forecasting, pattern recognition, and intelligence gathering",
        "config": {
            "domain": "intelligence",
            "capabilities": ["trend_prediction", "intelligence_gathering", "performance_analysis", "anomaly_detection"],
            "priority": 88,
            "max_concurrent_tasks": 4,
            "memory_context": "trend_data",
        },
    },
    "lord-arbiter": {
        "name": "Arbiter Lord",
        "guild": "lord",
        "kind": "lord",
        "description": "Rules, guardrails, compliance, conflict resolution, and justice administration",
        "config": {
            "domain": "justice",
            "capabilities": ["conflict_registration", "conflict_analysis", "resolution_proposal", "decision_making", "appeal_handling"],
            "priority": 92,
            "max_concurrent_tasks": 2,
            "memory_context": "rules_and_precedents",
        },
    },
    "lord-herald": {
        "name": "Herald Lord",
        "guild": "lord",
        "kind": "lord",
        "description": "Communication, messaging, storytelling, and information dissemination",
        "config": {
            "domain": "communication",
            "capabilities": ["message_sending", "announcement_scheduling", "template_management", "delivery_tracking"],
            "priority": 80,
            "max_concurrent_tasks": 5,
            "memory_context": "communication_history",
        },
    },
}

# Future: Guild leaders and specialists can be added here
# GUILD_LEADERS = { ... }


class AgentRegistry:
    """
    Canonical agent registry service.

    Responsible for:
    - Defining core agent manifests
    - Idempotent seeding of agents per workspace
    - Agent lookup by slug
    """

    def __init__(self):
        self.supabase = supabase_client

    def _get_core_agent_specs(self) -> List[Dict[str, Any]]:
        """Get all canonical core agent specifications."""
        specs = []
        for slug, config in COUNCIL_OF_LORDS.items():
            spec = dict(config)  # Copy
            spec["slug"] = slug
            specs.append(spec)
        return specs

    async def ensure_core_agents_for_workspace(self, workspace_id: str) -> None:
        """
        Idempotently ensure all core agents exist for a workspace.

        Creates agents if they don't exist. Does not modify existing agents.
        This is the canonical initialization point for workspaces.

        Args:
            workspace_id: Target workspace UUID
        """
        try:
            logger.info("Ensuring core agents for workspace", workspace_id=workspace_id)

            # Get canonical specifications
            core_specs = self._get_core_agent_specs()

            # For each core spec, ensure it exists
            created_count = 0
            for spec in core_specs:
                agent_id = await self._ensure_agent_exists(workspace_id, spec)
                if agent_id:
                    created_count += 1

            logger.info(
                "Core agents seeding complete",
                workspace_id=workspace_id,
                agents_created=created_count,
                lords_available=len(core_specs)
            )

        except Exception as e:
            logger.error(
                "Failed to ensure core agents for workspace",
                workspace_id=workspace_id,
                error=str(e)
            )
            # Continue - agent seeding failure shouldn't break workspace creation

    async def _ensure_agent_exists(self, workspace_id: str, agent_spec: Dict[str, Any]) -> Optional[str]:
        """
        Ensure a specific agent exists for the workspace.

        Returns the agent_id if created, None if already exists or failed.
        """
        slug = agent_spec["slug"]
        name = agent_spec["name"]

        try:
            # Check if agent already exists by workspace_id + slug
            result = self.supabase.client.table("agents").select("id").eq("workspace_id", workspace_id).eq("slug", slug)
            existing = result.execute()

            if existing.data and len(existing.data) > 0:
                # Agent already exists
                logger.debug("Agent already exists", workspace_id=workspace_id, agent_slug=slug)
                return None

            # Create the agent
            agent_data = {
                "id": str(uuid.uuid4()),  # Explicit UUID for consistency
                "workspace_id": workspace_id,
                "name": name,
                "slug": slug,
                "guild": agent_spec["guild"],
                "kind": agent_spec["kind"],
                "config": json.dumps(agent_spec["config"]),
                "status": "active",
            }

            result = await self.supabase.insert("agents", agent_data)
            agent_id = agent_data["id"]

            logger.info(
                "Created core agent",
                workspace_id=workspace_id,
                agent_name=name,
                agent_slug=slug,
                agent_id=agent_id
            )

            return agent_id

        except Exception as e:
            logger.error(
                "Failed to ensure agent exists",
                workspace_id=workspace_id,
                agent_name=name,
                agent_slug=slug,
                error=str(e)
            )
            return None

    async def get_agent_by_slug(self, workspace_id: str, slug: str) -> Optional[Dict[str, Any]]:
        """
        Get agent record by workspace + slug.

        Returns None if not found.

        Args:
            workspace_id: Target workspace
            slug: Agent slug (e.g., "lord-architect")

        Returns:
            Agent record dict or None
        """
        try:
            result = self.supabase.client.table("agents").select("*").eq("workspace_id", workspace_id).eq("slug", slug)
            data = result.execute()

            if data.data and len(data.data) > 0:
                agent = data.data[0]
                # Parse config JSON
                agent["config"] = json.loads(agent["config"]) if agent["config"] else {}
                return agent

            return None

        except Exception as e:
            logger.error("Failed to get agent by slug", workspace_id=workspace_id, slug=slug, error=str(e))
            return None

    def get_canonical_lords(self) -> List[str]:
        """
        Get list of canonical lord slugs.

        Useful for validation or UI display.
        """
        return list(COUNCIL_OF_LORDS.keys())

    def get_lord_spec(self, slug: str) -> Optional[Dict[str, Any]]:
        """
        Get canonical specification for a lord.

        Returns None if not a canonical lord.
        """
        if slug in COUNCIL_OF_LORDS:
            spec = dict(COUNCIL_OF_LORDS[slug])
            spec["slug"] = slug
            return spec
        return None

    async def list_workspace_agents(self, workspace_id: str) -> List[Dict[str, Any]]:
        """
        List all agents for a workspace.

        Returns list of agent records with parsed configs.
        """
        try:
            result = self.supabase.client.table("agents").select("*").eq("workspace_id", workspace_id)
            data = result.execute()

            agents = []
            for agent in data.data:
                agent["config"] = json.loads(agent["config"]) if agent["config"] else {}
                agents.append(agent)

            return agents

        except Exception as e:
            logger.error("Failed to list workspace agents", workspace_id=workspace_id, error=str(e))
            return []


# Global service instance
agent_registry = AgentRegistry()
