import asyncio
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Set
from uuid import UUID, uuid4

from memory.consolidated import MemoryFragment, SwarmMemoryConsolidator
from models.cognitive import AgentMessage, CognitiveIntelligenceState

logger = logging.getLogger("raptorflow.memory.swarm_coordinator")


class SwarmMemoryCoordinator:
    """
    Central coordinator for swarm-wide memory operations.
    Integrates with the SwarmOrchestrator to provide unified memory services.
    """

    def __init__(self, workspace_id: str):
        if not workspace_id or not isinstance(workspace_id, str):
            raise ValueError("workspace_id must be a non-empty string")

        self.workspace_id = workspace_id
        self.consolidator = SwarmMemoryConsolidator(workspace_id)

        # Active agent tracking
        self.active_agents: Set[str] = set()
        self.agent_memory_usage: Dict[str, Dict[str, int]] = {}

        # Performance metrics
        self.consolidation_count = 0
        self.search_count = 0
        self.cache_hits = 0
        self.cache_misses = 0

        logger.info(f"SwarmMemoryCoordinator initialized for workspace {workspace_id}")

    async def initialize_agent_memory(self, agent_id: str, agent_type: str) -> bool:
        """
        Initializes memory tracking for a new agent.
        Called when agents join the swarm.
        """
        try:
            self.active_agents.add(agent_id)
            self.agent_memory_usage[agent_id] = {
                "fragments": 0,
                "consolidations": 0,
                "searches": 0,
                "last_activity": datetime.now().isoformat(),
            }

            # Store agent profile in consolidated memory
            await self.consolidator.memory_manager.l1.store(
                f"agent_profile:{agent_id}",
                {
                    "agent_id": agent_id,
                    "agent_type": agent_type,
                    "workspace_id": self.workspace_id,
                    "initialized_at": datetime.now().isoformat(),
                },
                ttl=3600 * 24,  # 24 hours
            )

            logger.info(f"Initialized memory for agent {agent_id} ({agent_type})")
            return True

        except Exception as e:
            logger.error(f"Failed to initialize memory for agent {agent_id}: {e}")
            return False

    async def record_agent_memory(
        self,
        agent_id: str,
        content: Any,
        metadata: Optional[Dict[str, Any]] = None,
        importance: float = 0.5,
        thread_id: Optional[str] = None,
    ) -> bool:
        """
        Records a memory fragment from an agent.
        This is the primary interface for agents to store memories.
        """
        try:
            # Create memory fragment
            fragment = MemoryFragment(
                agent_id=agent_id,
                content=content,
                metadata=metadata or {},
                importance_score=importance,
                workspace_id=self.workspace_id,
                thread_id=thread_id or f"{agent_id}_{datetime.now().timestamp()}",
            )

            # Generate embedding
            embedder = self.consolidator.embedder
            content_str = str(content)
            fragment.embedding = await embedder.aembed_query(content_str)

            # Store in appropriate memory tier
            if importance > 0.8:
                # High importance - store in L2 episodic
                await self.consolidator.memory_manager.l2.store_episode(
                    workspace_id=self.workspace_id,
                    content=content_str,
                    embedding=fragment.embedding,
                    metadata={
                        **metadata,
                        "agent_id": agent_id,
                        "importance": importance,
                    },
                )
                fragment.memory_tier = "L2"
            else:
                # Standard importance - store in L1
                await self.consolidator.memory_manager.l1.store(
                    f"agent_memory:{agent_id}:{fragment.id}",
                    content,
                    ttl=3600 * 6,  # 6 hours
                )
                fragment.memory_tier = "L1"

            # Update agent usage tracking
            if agent_id in self.agent_memory_usage:
                self.agent_memory_usage[agent_id]["fragments"] += 1
                self.agent_memory_usage[agent_id][
                    "last_activity"
                ] = datetime.now().isoformat()

            # Cache for fast retrieval
            cache_key = f"fragment:{fragment.id}"
            await self.cache.set(cache_key, fragment, ttl=300)  # 5 minutes

            logger.debug(
                f"Recorded memory fragment {fragment.id} from agent {agent_id}"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to record memory for agent {agent_id}: {e}")
            return False

    async def search_swarm_memory(
        self,
        query: str,
        agent_filter: Optional[List[str]] = None,
        tier_filter: Optional[List[str]] = None,
        limit: int = 10,
        use_cache: bool = True,
    ) -> List[MemoryFragment]:
        """
        Searches across all swarm memory with intelligent caching.
        """
        self.search_count += 1

        # Check cache first
        cache_key = f"search:{hash(query)}_{agent_filter}_{tier_filter}_{limit}"
        if use_cache:
            cached_result = await self.cache.get(cache_key)
            if cached_result:
                self.cache_hits += 1
                logger.debug(f"Cache hit for search: {query[:50]}...")
                return cached_result

        self.cache_misses += 1

        try:
            # Perform search in consolidated memory
            results = await self.consolidator.search_consolidated_memory(
                query=query,
                agent_filter=agent_filter,
                tier_filter=tier_filter,
                limit=limit,
            )

            # Cache results
            if use_cache:
                await self.cache.set(cache_key, results, ttl=300)  # 5 minutes

            # Update search tracking
            for agent_id in set(fragment.agent_id for fragment in results):
                if agent_id in self.agent_memory_usage:
                    self.agent_memory_usage[agent_id]["searches"] += 1

            logger.info(f"Search returned {len(results)} results for: {query[:50]}...")
            return results

        except Exception as e:
            logger.error(f"Search failed for query '{query}': {e}")
            return []

    async def get_agent_context(
        self,
        agent_id: str,
        query: Optional[str] = None,
        include_cross_agent: bool = True,
    ) -> Dict[str, Any]:
        """
        Retrieves contextual memory for a specific agent.
        Optimized for agent decision-making.
        """
        try:
            context = {
                "agent_id": agent_id,
                "personal_memory": [],
                "relevant_swarm_memory": [],
                "cross_agent_insights": [],
                "recent_activity": [],
            }

            # Get agent's own recent memories
            agent_fragments = await self.search_swarm_memory(
                query=query or "recent activity", agent_filter=[agent_id], limit=20
            )
            context["personal_memory"] = agent_fragments

            # Get relevant swarm memory if requested
            if include_cross_agent and query:
                swarm_fragments = await self.search_swarm_memory(query=query, limit=15)
                # Filter out agent's own memories
                context["relevant_swarm_memory"] = [
                    f for f in swarm_fragments if f.agent_id != agent_id
                ]

            # Get cross-agent insights
            if include_cross_agent:
                # Get synthesized knowledge
                for (
                    synthesis
                ) in self.consolidator.consolidated_memory.synthesized_knowledge:
                    if not query or query.lower() in synthesis.get("theme", "").lower():
                        context["cross_agent_insights"].append(synthesis)

            # Get recent activity summary
            recent_fragments = await self.search_swarm_memory(
                query="recent activity outcome result", limit=10
            )
            context["recent_activity"] = recent_fragments[:5]

            return context

        except Exception as e:
            logger.error(f"Failed to get context for agent {agent_id}: {e}")
            return {"agent_id": agent_id, "error": str(e)}

    async def consolidate_swarm_memories(self, force: bool = False) -> Dict[str, Any]:
        """
        Triggers memory consolidation across the swarm.
        Can be called periodically or on-demand.
        """
        try:
            self.consolidation_count += 1

            # Get list of active agents
            agent_ids = list(self.active_agents) if self.active_agents else None

            # Perform consolidation
            start_time = datetime.now()
            consolidated = await self.consolidator.consolidate_agent_memories(
                agent_ids=agent_ids, force_consolidation=force
            )

            duration = (datetime.now() - start_time).total_seconds()

            # Update agent consolidation tracking
            for agent_id in set(
                fragment.agent_id for fragment in consolidated.fragments
            ):
                if agent_id in self.agent_memory_usage:
                    self.agent_memory_usage[agent_id]["consolidations"] += 1

            result = {
                "consolidation_id": str(uuid4()),
                "workspace_id": self.workspace_id,
                "duration_seconds": duration,
                "fragments_consolidated": len(consolidated.fragments),
                "agents_involved": len(set(f.agent_id for f in consolidated.fragments)),
                "synthesized_insights": len(consolidated.synthesized_knowledge),
                "cross_agent_links": len(consolidated.cross_agent_links),
                "timestamp": datetime.now().isoformat(),
            }

            logger.info(f"Consolidation completed in {duration:.2f}s: {result}")
            return result

        except Exception as e:
            logger.error(f"Consolidation failed: {e}")
            return {
                "consolidation_id": str(uuid4()),
                "workspace_id": self.workspace_id,
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }

    async def cleanup_agent_memory(self, agent_id: str) -> bool:
        """
        Cleans up memory for an agent that's leaving the swarm.
        Preserves important memories in L2/L3.
        """
        try:
            # Get agent's important memories
            important_fragments = await self.search_swarm_memory(
                query="important knowledge outcome learning",
                agent_filter=[agent_id],
                tier_filter=["L2", "L3"],
                limit=50,
            )

            # Ensure important memories are preserved in L2/L3
            for fragment in important_fragments:
                if fragment.memory_tier == "L1":
                    # Promote to L2
                    await self.consolidator.memory_manager.l2.store_episode(
                        workspace_id=self.workspace_id,
                        content=str(fragment.content),
                        embedding=fragment.embedding
                        or await self.consolidator.embedder.aembed_query(
                            str(fragment.content)
                        ),
                        metadata={**fragment.metadata, "promoted_from_L1": True},
                    )

            # Clear agent from active tracking
            self.active_agents.discard(agent_id)
            if agent_id in self.agent_memory_usage:
                del self.agent_memory_usage[agent_id]

            # Clear agent-specific cache entries
            # (Implementation depends on cache structure)

            logger.info(
                f"Cleaned up memory for agent {agent_id}, preserved {len(important_fragments)} important fragments"
            )
            return True

        except Exception as e:
            logger.error(f"Failed to cleanup memory for agent {agent_id}: {e}")
            return False

    async def get_swarm_memory_metrics(self) -> Dict[str, Any]:
        """
        Returns comprehensive metrics about swarm memory performance.
        """
        try:
            # Get base statistics from consolidator
            stats = await self.consolidator.get_memory_statistics()

            # Add coordinator-specific metrics
            stats.update(
                {
                    "active_agents": len(self.active_agents),
                    "total_consolidations": self.consolidation_count,
                    "total_searches": self.search_count,
                    "cache_hit_rate": self.cache_hits / max(self.search_count, 1),
                    "agent_memory_usage": self.agent_memory_usage.copy(),
                }
            )

            # Add performance metrics
            stats["performance"] = {
                "average_consolidation_time": "N/A",  # Would need tracking
                "average_search_latency": "N/A",  # Would need tracking
                "memory_efficiency": len(
                    self.consolidator.consolidated_memory.fragments
                )
                / max(len(self.active_agents), 1),
            }

            return stats

        except Exception as e:
            logger.error(f"Failed to get memory metrics: {e}")
            return {"error": str(e), "timestamp": datetime.now().isoformat()}


# Global coordinator registry for workspace isolation
_coordinator_registry: Dict[str, SwarmMemoryCoordinator] = {}


def get_swarm_memory_coordinator(workspace_id: str) -> SwarmMemoryCoordinator:
    """
    Gets or creates a swarm memory coordinator for a workspace.
    Provides workspace isolation and singleton behavior.
    """
    if workspace_id not in _coordinator_registry:
        _coordinator_registry[workspace_id] = SwarmMemoryCoordinator(workspace_id)
    return _coordinator_registry[workspace_id]


async def initialize_workspace_memory(workspace_id: str) -> SwarmMemoryCoordinator:
    """
    Initializes memory system for a new workspace.
    """
    coordinator = get_swarm_memory_coordinator(workspace_id)
    logger.info(f"Initialized workspace memory system for {workspace_id}")
    return coordinator


# Integration helpers for the SwarmOrchestrator
async def hydrate_state_with_swarm_memory(
    state: CognitiveIntelligenceState,
) -> CognitiveIntelligenceState:
    """
    Hydrates agent state with relevant swarm memory.
    Called by SwarmOrchestrator before agent execution.
    """
    workspace_id = state.get("workspace_id")
    if not workspace_id:
        return state

    try:
        coordinator = get_swarm_memory_coordinator(workspace_id)

        # Get context for the current agent
        last_agent = state.get("last_agent")
        if last_agent:
            context = await coordinator.get_agent_context(
                agent_id=last_agent,
                query=state.get("raw_prompt", ""),
                include_cross_agent=True,
            )

            # Add context to state
            state["swarm_memory_context"] = context

            # Add relevant memories to messages for context
            if context.get("personal_memory"):
                for fragment in context["personal_memory"][
                    :3
                ]:  # Limit to prevent context overflow
                    memory_message = AgentMessage(
                        role="system",
                        content=f"[Memory from {fragment.agent_id}]: {str(fragment.content)[:200]}...",
                        metadata={"source": "swarm_memory", "fragment_id": fragment.id},
                    )
                    state.setdefault("messages", []).append(memory_message)

        return state

    except Exception as e:
        logger.error(f"Failed to hydrate state with swarm memory: {e}")
        return state


async def record_agent_execution(
    state: CognitiveIntelligenceState, result: Dict[str, Any]
) -> bool:
    """
    Records agent execution results in swarm memory.
    Called by SwarmOrchestrator after agent execution.
    """
    workspace_id = state.get("workspace_id")
    last_agent = state.get("last_agent")

    if not workspace_id or not last_agent:
        return False

    try:
        coordinator = get_swarm_memory_coordinator(workspace_id)

        # Record the execution result
        content = {
            "agent": last_agent,
            "task": state.get("instructions", ""),
            "result": result.get("analysis_summary", ""),
            "tokens_used": result.get("token_usage", {}),
            "timestamp": datetime.now().isoformat(),
        }

        metadata = {
            "agent_type": state.get("agent_type", "unknown"),
            "execution_id": str(uuid4()),
            "workspace_id": workspace_id,
        }

        success = await coordinator.record_agent_memory(
            agent_id=last_agent,
            content=content,
            metadata=metadata,
            importance=0.6,  # Medium importance for execution results
        )

        if success:
            logger.debug(f"Recorded execution for agent {last_agent}")

        return success

    except Exception as e:
        logger.error(f"Failed to record agent execution: {e}")
        return False
