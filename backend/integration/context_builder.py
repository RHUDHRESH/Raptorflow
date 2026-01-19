"""
Unified context builder for agents.
Gathers context from memory, database, and session data.
"""

import logging
from typing import Any, Dict, List, Optional
import datetime
import hashlib
import json

from backend.agents.state import AgentState
from backend.memory.controller import MemoryController

from supabase import Client

logger = logging.getLogger(__name__)


async def build_full_context(
    workspace_id: str,
    query: str,
    db_client: Client,
    memory_controller: MemoryController,
    session_data: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """
    Build comprehensive context from all sources.

    Args:
        workspace_id: Workspace ID
        query: Query string
        db_client: Database client
        memory_controller: Memory controller
        session_data: Optional session data

    Returns:
        Complete context dictionary
    """
    try:
        logger.info(f"Building full context for workspace {workspace_id}")

        context = {
            "workspace_id": workspace_id,
            "query": query,
            "timestamp": datetime.datetime.now().timestamp(),
        }

        # Gather database context
        context["database"] = await _build_database_context(workspace_id, db_client)

        # Gather memory context
        context["memory"] = await _build_memory_context(
            workspace_id, query, memory_controller
        )

        # Gather session context
        if session_data:
            context["session"] = session_data

        # Build unified context
        unified_context = _unify_context(context)

        logger.info(
            f"Built context with {len(unified_context.get('relevant_items', []))} items"
        )

        return unified_context

    except Exception as e:
        logger.error(f"Error building full context: {e}")
        return {
            "workspace_id": workspace_id,
            "query": query,
            "error": str(e),
            "relevant_items": [],
        }


async def _build_database_context(
    workspace_id: str, db_client: Client
) -> Dict[str, Any]:
    """Build context from database."""
    try:
        context = {"foundation": None, "icps": [], "moves": [], "campaigns": []}

        # Get foundation data
        foundation_result = (
            db_client.table("foundations")
            .select("*")
            .eq("workspace_id", workspace_id)
            .execute()
        )
        if foundation_result.data:
            context["foundation"] = foundation_result.data[0]

        # Get ICP data
        icp_result = (
            db_client.table("icp_profiles")
            .select("*")
            .eq("workspace_id", workspace_id)
            .execute()
        )
        if icp_result.data:
            context["icps"] = icp_result.data

        # Get recent moves
        moves_result = (
            db_client.table("moves")
            .select("*")
            .eq("workspace_id", workspace_id)
            .order("created_at", desc=True)
            .limit(10)
            .execute()
        )
        if moves_result.data:
            context["moves"] = moves_result.data

        # Get active campaigns
        campaigns_result = (
            db_client.table("campaigns")
            .select("*")
            .eq("workspace_id", workspace_id)
            .eq("status", "active")
            .execute()
        )
        if campaigns_result.data:
            context["campaigns"] = campaigns_result.data

        return context

    except Exception as e:
        logger.error(f"Error building database context: {e}")
        return {"error": str(e)}


async def _build_memory_context(
    workspace_id: str, query: str, memory_controller: MemoryController
) -> Dict[str, Any]:
    """Build context from memory system."""
    try:
        context = {
            "vector_results": [],
            "graph_entities": [],
            "episodic_memories": [],
            "working_memory": [],
        }

        # Vector search
        vector_results = await memory_controller.search(
            workspace_id=workspace_id,
            query=query,
            memory_types=["foundation", "icp", "conversation", "move", "campaign"],
            limit=20,
        )
        context["vector_results"] = vector_results

        # Graph entities
        try:
            graph_entities = await memory_controller.graph_memory.get_entities(
                workspace_id=workspace_id, entity_type=None, limit=15
            )
            context["graph_entities"] = graph_entities
        except Exception as e:
            logger.warning(f"Error getting graph entities: {e}")

        # Episodic memories
        try:
            episodic_memories = await memory_controller.episodic_memory.get_recent(
                workspace_id=workspace_id, limit=10
            )
            context["episodic_memories"] = episodic_memories
        except Exception as e:
            logger.warning(f"Error getting episodic memories: {e}")

        # Working memory
        try:
            working_memory = await memory_controller.working_memory.get_active_context(
                workspace_id=workspace_id
            )
            context["working_memory"] = working_memory
        except Exception as e:
            logger.warning(f"Error getting working memory: {e}")

        return context

    except Exception as e:
        logger.error(f"Error building memory context: {e}")
        return {"error": str(e)}


def _unify_context(context: Dict[str, Any]) -> Dict[str, Any]:
    """Unify context from different sources."""
    try:
        unified = {
            "workspace_id": context["workspace_id"],
            "query": context["query"],
            "timestamp": context["timestamp"],
            "relevant_items": [],
            "summary": {},
            "metadata": {},
        }

        # Process database context
        db_context = context.get("database", {})
        if "foundation" in db_context and db_context["foundation"]:
            foundation = db_context["foundation"]
            unified["relevant_items"].append(
                {
                    "type": "foundation",
                    "content": f"Business: {foundation.get('business_name', '')}",
                    "industry": foundation.get("industry", ""),
                    "description": foundation.get("business_description", ""),
                    "source": "database",
                    "relevance": 1.0,
                }
            )

        # Process ICPs
        for icp in db_context.get("icps", []):
            unified["relevant_items"].append(
                {
                    "type": "icp",
                    "content": f"ICP: {icp.get('name', '')}",
                    "description": icp.get("description", ""),
                    "source": "database",
                    "relevance": 0.9,
                }
            )

        # Process recent moves
        for move in db_context.get("moves", []):
            unified["relevant_items"].append(
                {
                    "type": "move",
                    "content": f"Move: {move.get('title', '')}",
                    "status": move.get("status", ""),
                    "source": "database",
                    "relevance": 0.7,
                }
            )

        # Process memory context
        memory_context = context.get("memory", {})

        # Vector results
        for item in memory_context.get("vector_results", []):
            unified["relevant_items"].append(
                {
                    "type": item.memory_type,
                    "content": item.content[:500],  # Truncate
                    "score": item.score,
                    "source": "memory_vector",
                    "relevance": item.score,
                }
            )

        # Graph entities
        for entity in memory_context.get("graph_entities", []):
            unified["relevant_items"].append(
                {
                    "type": "graph_entity",
                    "content": f"{entity.type}: {entity.name}",
                    "properties": entity.properties,
                    "source": "memory_graph",
                    "relevance": 0.8,
                }
            )

        # Episodic memories
        for memory in memory_context.get("episodic_memories", []):
            unified["relevant_items"].append(
                {
                    "type": "episodic",
                    "content": memory.get("content", "")[:300],
                    "timestamp": memory.get("timestamp"),
                    "source": "memory_episodic",
                    "relevance": 0.6,
                }
            )

        # Sort by relevance
        unified["relevant_items"].sort(key=lambda x: x["relevance"], reverse=True)

        # Limit to top items
        unified["relevant_items"] = unified["relevant_items"][:15]

        # Build summary
        unified["summary"] = {
            "total_items": len(unified["relevant_items"]),
            "foundation_exists": bool(db_context.get("foundation")),
            "icp_count": len(db_context.get("icps", [])),
            "move_count": len(db_context.get("moves", [])),
            "memory_items": len(memory_context.get("vector_results", [])),
            "graph_entities": len(memory_context.get("graph_entities", [])),
        }

        # Add metadata
        unified["metadata"] = {
            "sources_used": [
                "database",
                "memory_vector",
                "memory_graph",
                "memory_episodic",
            ],
            "query_processed": context["query"],
            "workspace_id": context["workspace_id"],
        }

        return unified

    except Exception as e:
        logger.error(f"Error unifying context: {e}")
        return {
            "workspace_id": context.get("workspace_id"),
            "query": context.get("query"),
            "relevant_items": [],
            "error": str(e),
        }


async def build_business_context_manifest(
    workspace_id: str,
    db_client: Client,
    memory_controller: MemoryController,
    version_major: int = 1,
    version_minor: int = 0,
    version_patch: int = 0
) -> Dict[str, Any]:
    """
    Build Business Context Manifest (BCM) JSON from workspace data.
    
    Args:
        workspace_id: Workspace ID
        db_client: Supabase client
        memory_controller: Memory controller
        version_major: Major version
        version_minor: Minor version
        version_patch: Patch version
        
    Returns:
        Dictionary with manifest data ready for Supabase storage
    """
    try:
        # Build comprehensive context
        context = await build_full_context(
            workspace_id=workspace_id,
            query="build_business_context_manifest",
            db_client=db_client,
            memory_controller=memory_controller
        )
        
        # Extract and compress key components
        foundation = context.get("database", {}).get("foundation", {})
        icps = context.get("database", {}).get("icps", [])
        moves = context.get("database", {}).get("moves", [])
        campaigns = context.get("database", {}).get("campaigns", [])
        
        # Build manifest structure
        manifest = {
            "version": {
                "major": version_major,
                "minor": version_minor,
                "patch": version_patch
            },
            "workspace_id": workspace_id,
            "foundation": {
                "business_name": foundation.get("business_name"),
                "industry": foundation.get("industry"),
                "description": foundation.get("business_description"),
                "key_attributes": foundation.get("key_attributes", [])
            },
            "icps": [
                {
                    "id": icp.get("id"),
                    "name": icp.get("name"),
                    "key_attributes": icp.get("key_attributes", []),
                    "pain_points": icp.get("pain_points", [])
                }
                for icp in icps[:3]  # Max 3 ICPs as per business rules
            ],
            "current_moves": [
                {
                    "id": move.get("id"),
                    "title": move.get("title"),
                    "status": move.get("status"),
                    "key_actions": move.get("key_actions", [])
                }
                for move in moves[:5]  # Last 5 moves
            ],
            "active_campaigns": [
                {
                    "id": campaign.get("id"),
                    "name": campaign.get("name"),
                    "status": campaign.get("status"),
                    "key_metrics": campaign.get("key_metrics", {})
                }
                for campaign in campaigns
            ],
            "metadata": {
                "created_at": datetime.datetime.now().isoformat(),
                "source": "context_builder",
                "context_hash": context.get("metadata", {}).get("query_processed")
            }
        }
        
        # Calculate checksum
        manifest_str = json.dumps(manifest, sort_keys=True)
        checksum = hashlib.sha256(manifest_str.encode()).hexdigest()
        
        return {
            "version_major": version_major,
            "version_minor": version_minor,
            "version_patch": version_patch,
            "checksum": checksum,
            "content": manifest
        }
        
    except Exception as e:
        logger.error(f"Error building business context manifest: {e}")
        raise


class ContextBuilder:
    """
    Advanced context builder with caching and optimization.
    """

    def __init__(self, db_client: Client, memory_controller: MemoryController):
        self.db_client = db_client
        self.memory_controller = memory_controller
        self.context_cache = {}

    async def build_context(
        self,
        workspace_id: str,
        query: str,
        session_data: Dict[str, Any] = None,
        use_cache: bool = True,
    ) -> Dict[str, Any]:
        """
        Build context with caching.

        Args:
            workspace_id: Workspace ID
            query: Query string
            session_data: Session data
            use_cache: Whether to use cache

        Returns:
            Built context
        """
        # Generate cache key
        cache_key = f"{workspace_id}:{hash(query)}"

        # Check cache
        if use_cache and cache_key in self.context_cache:
            cache_entry = self.context_cache[cache_key]
            if datetime.datetime.now().timestamp() - cache_entry["timestamp"] < 600:  # 10 minute cache
                cached_context = cache_entry["context"]
                # Update with current session data
                if session_data:
                    cached_context["session"] = session_data
                return cached_context

        # Build new context
        context = await build_full_context(
            workspace_id, query, self.db_client, self.memory_controller, session_data
        )

        # Cache result
        if use_cache:
            self.context_cache[cache_key] = {
                "context": context,
                "timestamp": datetime.datetime.now().timestamp(),
            }

        return context

    async def build_agent_context(
        self,
        workspace_id: str,
        agent_name: str,
        query: str,
        session_data: Dict[str, Any] = None,
    ) -> Dict[str, Any]:
        """
        Build context specific to an agent.

        Args:
            workspace_id: Workspace ID
            agent_name: Agent name
            query: Query string
            session_data: Session data

        Returns:
            Agent-specific context
        """
        # Build general context
        general_context = await self.build_context(workspace_id, query, session_data)

        # Filter for agent relevance
        agent_context = self._filter_for_agent(general_context, agent_name)

        # Add agent-specific data
        agent_context["agent"] = {
            "name": agent_name,
            "context_type": "agent_specific",
            "filtered_items": len(agent_context["relevant_items"]),
        }

        return agent_context

    def _filter_for_agent(
        self, context: Dict[str, Any], agent_name: str
    ) -> Dict[str, Any]:
        """Filter context for specific agent."""
        # Define agent preferences (would come from agent configuration)
        agent_preferences = {
            "market_research": ["foundation", "icp", "industry"],
            "content_creator": ["icp", "campaign", "move"],
            "campaign_planner": ["icp", "campaign", "move"],
            "move_strategist": ["move", "foundation", "icp"],
            "blackbox_strategist": ["foundation", "icp", "move"],
            "daily_wins": ["move", "campaign", "content"],
            "analytics_agent": ["move", "campaign", "usage"],
        }

        preferred_types = agent_preferences.get(agent_name, [])

        if not preferred_types:
            return context

        # Filter relevant items
        filtered_items = []
        for item in context.get("relevant_items", []):
            if item["type"] in preferred_types:
                filtered_items.append(item)

        # Update context
        filtered_context = context.copy()
        filtered_context["relevant_items"] = filtered_items
        filtered_context["summary"]["filtered_for_agent"] = len(filtered_items)

        return filtered_context

    async def clear_cache(self, workspace_id: str = None):
        """Clear context cache."""
        if workspace_id:
            # Clear specific workspace cache
            keys_to_remove = [
                k for k in self.context_cache.keys() if k.startswith(f"{workspace_id}:")
            ]
            for key in keys_to_remove:
                del self.context_cache[key]
        else:
            # Clear all cache
            self.context_cache.clear()

        logger.info(f"Cleared context cache for {workspace_id or 'all workspaces'}")

    async def build_and_store_manifest(
        self,
        workspace_id: str,
        version_major: int = 1,
        version_minor: int = 0,
        version_patch: int = 0
    ) -> Dict[str, Any]:
        """
        Build and store business context manifest in Supabase.
        
        Args:
            workspace_id: Workspace ID
            version_major: Major version
            version_minor: Minor version
            version_patch: Patch version
            
        Returns:
            Dictionary with manifest data and storage result
        """
        try:
            # Build manifest
            manifest_data = await build_business_context_manifest(
                workspace_id=workspace_id,
                db_client=self.db_client,
                memory_controller=self.memory_controller,
                version_major=version_major,
                version_minor=version_minor,
                version_patch=version_patch
            )
            
            # Store in Supabase
            result = self.db_client.table("business_context_manifests").insert(
                {
                    "workspace_id": workspace_id,
                    "version_major": manifest_data["version_major"],
                    "version_minor": manifest_data["version_minor"],
                    "version_patch": manifest_data["version_patch"],
                    "checksum": manifest_data["checksum"],
                    "content": manifest_data["content"]
                }
            ).execute()
            
            return {
                "manifest": manifest_data,
                "storage_result": result.data[0] if result.data else None
            }
            
        except Exception as e:
            logger.error(f"Error building/storing manifest: {e}")
            raise
