"""
Memory System API Endpoints

REST API endpoints for managing and accessing the consolidated swarm memory system.
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

from backend.memory.swarm_coordinator import (
    get_swarm_memory_coordinator,
    SwarmMemoryCoordinator
)
from backend.memory.cache import create_cached_coordinator

logger = logging.getLogger("raptorflow.memory.api")

router = APIRouter(prefix="/api/v1/memory", tags=["memory"])


class MemoryStatsResponse(BaseModel):
    """Response model for memory statistics."""
    workspace_id: str
    total_fragments: int
    unique_agents: int
    memory_tiers: Dict[str, int]
    average_importance: float
    cross_agent_links: int
    synthesized_insights: int
    cache_performance: Dict[str, Any]
    last_consolidation: str


class MemorySearchRequest(BaseModel):
    """Request model for memory search."""
    query: str = Field(..., description="Search query")
    agent_filter: Optional[List[str]] = Field(None, description="Filter by agent IDs")
    tier_filter: Optional[List[str]] = Field(None, description="Filter by memory tiers")
    limit: int = Field(10, ge=1, le=100, description="Maximum results to return")
    use_cache: bool = Field(True, description="Use cached results")


class MemorySearchResponse(BaseModel):
    """Response model for memory search."""
    query: str
    results_count: int
    fragments: List[Dict[str, Any]]
    search_time_ms: float


class ConsolidationRequest(BaseModel):
    """Request model for memory consolidation."""
    force: bool = Field(False, description="Force consolidation even if not due")
    agent_ids: Optional[List[str]] = Field(None, description="Specific agents to consolidate")


class ConsolidationResponse(BaseModel):
    """Response model for memory consolidation."""
    consolidation_id: str
    workspace_id: str
    duration_seconds: float
    fragments_consolidated: int
    agents_involved: int
    synthesized_insights: int
    cross_agent_links: int
    timestamp: str


class AgentContextRequest(BaseModel):
    """Request model for agent context."""
    agent_id: str = Field(..., description="Agent ID")
    query: Optional[str] = Field(None, description="Context query")
    include_cross_agent: bool = Field(True, description="Include cross-agent insights")
    use_cache: bool = Field(True, description="Use cached results")


class AgentContextResponse(BaseModel):
    """Response model for agent context."""
    agent_id: str
    personal_memory: List[Dict[str, Any]]
    relevant_swarm_memory: List[Dict[str, Any]]
    cross_agent_insights: List[Dict[str, Any]]
    recent_activity: List[Dict[str, Any]]


def get_coordinator(workspace_id: str) -> SwarmMemoryCoordinator:
    """Dependency function to get memory coordinator for workspace."""
    try:
        return get_swarm_memory_coordinator(workspace_id)
    except Exception as e:
        logger.error(f"Failed to get coordinator for workspace {workspace_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to initialize memory coordinator")


@router.get("/workspace/{workspace_id}/stats", response_model=MemoryStatsResponse)
async def get_memory_stats(
    workspace_id: str,
    coordinator: SwarmMemoryCoordinator = Depends(get_coordinator)
):
    """
    Get comprehensive memory statistics for a workspace.
    
    - **workspace_id**: Workspace identifier
    - **Returns**: Memory usage statistics, cache performance, and consolidation info
    """
    try:
        stats = await coordinator.get_swarm_memory_metrics()
        
        return MemoryStatsResponse(
            workspace_id=stats["workspace_id"],
            total_fragments=stats["total_fragments"],
            unique_agents=stats["active_agents"],
            memory_tiers=stats["memory_tiers"],
            average_importance=stats.get("average_importance", 0.0),
            cross_agent_links=stats.get("cross_agent_links", 0),
            synthesized_insights=stats.get("synthesized_insights", 0),
            cache_performance=stats.get("cache_performance", {}),
            last_consolidation=stats.get("last_consolidation", "")
        )
        
    except Exception as e:
        logger.error(f"Failed to get memory stats for workspace {workspace_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve memory statistics")


@router.post("/workspace/{workspace_id}/search", response_model=MemorySearchResponse)
async def search_memory(
    workspace_id: str,
    request: MemorySearchRequest,
    coordinator: SwarmMemoryCoordinator = Depends(get_coordinator)
):
    """
    Search across consolidated swarm memory.
    
    - **workspace_id**: Workspace identifier
    - **request**: Search parameters including query and filters
    - **Returns**: Relevant memory fragments matching the search criteria
    """
    try:
        start_time = datetime.now()
        
        # Create cached coordinator for better performance
        cached_coordinator = create_cached_coordinator(coordinator, cache_size_mb=50)
        
        results = await cached_coordinator.search_swarm_memory(
            query=request.query,
            agent_filter=request.agent_filter,
            tier_filter=request.tier_filter,
            limit=request.limit,
            use_cache=request.use_cache
        )
        
        search_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Convert fragments to serializable format
        fragments_data = []
        for fragment in results:
            fragments_data.append({
                "id": fragment.id,
                "agent_id": fragment.agent_id,
                "agent_type": fragment.agent_type,
                "content": fragment.content,
                "importance_score": fragment.importance_score,
                "memory_tier": fragment.memory_tier,
                "timestamp": fragment.timestamp.isoformat(),
                "access_count": fragment.access_count,
                "tags": list(fragment.tags),
                "metadata": fragment.metadata
            })
        
        return MemorySearchResponse(
            query=request.query,
            results_count=len(results),
            fragments=fragments_data,
            search_time_ms=search_time
        )
        
    except Exception as e:
        logger.error(f"Memory search failed for workspace {workspace_id}: {e}")
        raise HTTPException(status_code=500, detail="Memory search failed")


@router.post("/workspace/{workspace_id}/consolidate", response_model=ConsolidationResponse)
async def trigger_consolidation(
    workspace_id: str,
    request: ConsolidationRequest,
    coordinator: SwarmMemoryCoordinator = Depends(get_coordinator)
):
    """
    Trigger memory consolidation for a workspace.
    
    - **workspace_id**: Workspace identifier
    - **request**: Consolidation parameters
    - **Returns**: Consolidation results and statistics
    """
    try:
        result = await coordinator.consolidate_swarm_memories(
            force=request.force,
            agent_ids=request.agent_ids
        )
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return ConsolidationResponse(
            consolidation_id=result["consolidation_id"],
            workspace_id=result["workspace_id"],
            duration_seconds=result["duration_seconds"],
            fragments_consolidated=result["fragments_consolidated"],
            agents_involved=result["agents_involved"],
            synthesized_insights=result["synthesized_insights"],
            cross_agent_links=result["cross_agent_links"],
            timestamp=result["timestamp"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Consolidation failed for workspace {workspace_id}: {e}")
        raise HTTPException(status_code=500, detail="Memory consolidation failed")


@router.post("/workspace/{workspace_id}/agent/context", response_model=AgentContextResponse)
async def get_agent_context(
    workspace_id: str,
    request: AgentContextRequest,
    coordinator: SwarmMemoryCoordinator = Depends(get_coordinator)
):
    """
    Get contextual memory for a specific agent.
    
    - **workspace_id**: Workspace identifier
    - **request**: Agent context parameters
    - **Returns**: Agent's personal memory, relevant swarm memory, and insights
    """
    try:
        # Create cached coordinator for better performance
        cached_coordinator = create_cached_coordinator(coordinator, cache_size_mb=50)
        
        context = await cached_coordinator.get_agent_context(
            agent_id=request.agent_id,
            query=request.query,
            include_cross_agent=request.include_cross_agent,
            use_cache=request.use_cache
        )
        
        # Convert to serializable format
        def serialize_fragments(fragments):
            return [
                {
                    "id": f.id,
                    "agent_id": f.agent_id,
                    "content": f.content,
                    "importance_score": f.importance_score,
                    "timestamp": f.timestamp.isoformat(),
                    "memory_tier": f.memory_tier
                }
                for f in fragments
            ]
        
        return AgentContextResponse(
            agent_id=context["agent_id"],
            personal_memory=serialize_fragments(context.get("personal_memory", [])),
            relevant_swarm_memory=serialize_fragments(context.get("relevant_swarm_memory", [])),
            cross_agent_insights=context.get("cross_agent_insights", []),
            recent_activity=serialize_fragments(context.get("recent_activity", []))
        )
        
    except Exception as e:
        logger.error(f"Failed to get agent context for workspace {workspace_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve agent context")


@router.get("/workspace/{workspace_id}/agents")
async def list_active_agents(
    workspace_id: str,
    coordinator: SwarmMemoryCoordinator = Depends(get_coordinator)
):
    """
    List all active agents in the workspace.
    
    - **workspace_id**: Workspace identifier
    - **Returns**: List of active agent IDs and their memory usage
    """
    try:
        agents = []
        for agent_id in coordinator.active_agents:
            usage = coordinator.agent_memory_usage.get(agent_id, {})
            agents.append({
                "agent_id": agent_id,
                "fragments_count": usage.get("fragments", 0),
                "searches_count": usage.get("searches", 0),
                "consolidations_count": usage.get("consolidations", 0),
                "last_activity": usage.get("last_activity", "")
            })
        
        return {"workspace_id": workspace_id, "active_agents": agents}
        
    except Exception as e:
        logger.error(f"Failed to list agents for workspace {workspace_id}: {e}")
        raise HTTPException(status_code=500, detail="Failed to list active agents")


@router.delete("/workspace/{workspace_id}/agent/{agent_id}")
async def cleanup_agent_memory(
    workspace_id: str,
    agent_id: str,
    coordinator: SwarmMemoryCoordinator = Depends(get_coordinator)
):
    """
    Clean up memory for a specific agent (when agent leaves swarm).
    
    - **workspace_id**: Workspace identifier
    - **agent_id**: Agent identifier to cleanup
    - **Returns**: Cleanup confirmation
    """
    try:
        success = await coordinator.cleanup_agent_memory(agent_id)
        
        if not success:
            raise HTTPException(status_code=500, detail="Agent memory cleanup failed")
        
        return {
            "workspace_id": workspace_id,
            "agent_id": agent_id,
            "message": "Agent memory cleaned up successfully",
            "timestamp": datetime.now().isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Agent cleanup failed for workspace {workspace_id}: {e}")
        raise HTTPException(status_code=500, detail="Agent memory cleanup failed")


@router.get("/workspace/{workspace_id}/health")
async def memory_health_check(
    workspace_id: str,
    coordinator: SwarmMemoryCoordinator = Depends(get_coordinator)
):
    """
    Perform health check on memory system.
    
    - **workspace_id**: Workspace identifier
    - **Returns**: Health status and recommendations
    """
    try:
        stats = await coordinator.get_swarm_memory_metrics()
        
        health_status = {
            "status": "healthy",
            "issues": [],
            "recommendations": [],
            "metrics": stats
        }
        
        # Check cache performance
        cache_hit_rate = stats.get("cache_performance", {}).get("hit_rate", 0)
        if cache_hit_rate < 0.7:
            health_status["issues"].append("Low cache hit rate")
            health_status["recommendations"].append("Consider increasing cache size")
        
        # Check consolidation lag
        if stats.get("last_consolidation"):
            last_consolidation = datetime.fromisoformat(stats["last_consolidation"])
            if datetime.now() - last_consolidation > timedelta(minutes=10):
                health_status["issues"].append("Consolidation lag")
                health_status["recommendations"].append("Check consolidation task")
        
        # Check memory distribution
        memory_tiers = stats.get("memory_tiers", {})
        total_memory = sum(memory_tiers.values())
        if total_memory > 10000:  # Arbitrary threshold
            health_status["issues"].append("High memory usage")
            health_status["recommendations"].append("Consider memory cleanup")
        
        # Determine overall status
        if health_status["issues"]:
            health_status["status"] = "degraded" if len(health_status["issues"]) <= 2 else "unhealthy"
        
        return health_status
        
    except Exception as e:
        logger.error(f"Health check failed for workspace {workspace_id}: {e}")
        raise HTTPException(status_code=500, detail="Memory health check failed")


# Register router with FastAPI app
def register_memory_api(app):
    """Register memory API endpoints with FastAPI app."""
    app.include_router(router)
    logger.info("Memory API endpoints registered")
