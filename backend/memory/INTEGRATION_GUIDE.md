"""
Swarm Memory System Integration Guide

This document explains how to integrate the consolidated memory system
with the existing RaptorFlow AI agent swarm network.

## Architecture Overview

The consolidated memory system consists of 4 main components:

1. **SwarmMemoryConsolidator** (`backend/memory/consolidated.py`)
   - Core consolidation engine that aggregates memories from all agents
   - Performs deduplication, scoring, and synthesis
   - Manages L1/L2/L3 memory tier integration

2. **SwarmMemoryCoordinator** (`backend/memory/swarm_coordinator.py`)
   - High-level coordinator for swarm-wide memory operations
   - Provides agent registration, memory recording, and search
   - Integrates with SwarmOrchestrator for state hydration

3. **SwarmMemoryCache** (`backend/memory/cache.py`)
   - Multi-tier caching system (L0 hot, L1 warm, L2 cold)
   - Intelligent eviction and promotion based on access patterns
   - Performance optimization for high-frequency operations

4. **Integration Layer** (helper functions)
   - State hydration for agent execution
   - Memory recording for agent results
   - Workspace isolation and singleton management

## Integration Steps

### 1. Update SwarmOrchestrator

Modify `backend/graphs/swarm_orchestrator.py` to integrate memory:

```python
# Add imports
from backend.memory.swarm_coordinator import (
    get_swarm_memory_coordinator,
    hydrate_state_with_swarm_memory,
    record_agent_execution
)

# In __call__ method, before agent execution:
async def __call__(self, state: Dict[str, Any]) -> Dict[str, Any]:
    # ... existing code ...

    # Hydrate state with swarm memory
    state = await hydrate_state_with_swarm_memory(state)

    # ... existing agent execution logic ...

    # Record agent execution results
    await record_agent_execution(state, result)

    return state
```

### 2. Update Base Agent

Modify `backend/agents/base.py` to use consolidated memory:

```python
# Add import
from backend.memory.swarm_coordinator import get_swarm_memory_coordinator

# In BaseCognitiveAgent.__init__:
def __init__(self, ...):
    # ... existing initialization ...
    self.memory_coordinator = None  # Will be set during execution

# In __call__ method:
async def __call__(self, state: CognitiveIntelligenceState) -> Dict[str, Any]:
    # Initialize memory coordinator if needed
    workspace_id = state.get("workspace_id")
    if workspace_id and not self.memory_coordinator:
        self.memory_coordinator = get_swarm_memory_coordinator(workspace_id)

        # Register agent with memory system
        await self.memory_coordinator.initialize_agent_memory(
            agent_id=self.name,
            agent_type=self.role
        )

    # ... existing agent logic ...

    # Record important memories
    if self.memory_coordinator and result:
        await self.memory_coordinator.record_agent_memory(
            agent_id=self.name,
            content=result.get("messages", []),
            importance=0.7,  # Medium importance for agent outputs
            metadata={"agent_type": self.role, "model_tier": self.model_tier}
        )

    return result
```

### 3. Update Agent Specialization

For specialized agents, add memory-specific logic:

```python
# Example for ResearcherAgent in backend/agents/specialists/researcher.py
async def __call__(self, state: CognitiveIntelligenceState) -> Dict[str, Any]:
    # Get research context from memory
    if self.memory_coordinator:
        context = await self.memory_coordinator.get_agent_context(
            agent_id=self.name,
            query="market research trends competitor analysis",
            include_cross_agent=True
        )

        # Use context to enhance research
        # ... context integration logic ...

    # ... existing research logic ...

    # Record research findings with high importance
    if self.memory_coordinator and result:
        await self.memory_coordinator.record_agent_memory(
            agent_id=self.name,
            content=result.get("trends", []),
            importance=0.9,  # High importance for research findings
            metadata={
                "type": "research_findings",
                "trends_count": len(result.get("trends", [])),
                "market_gaps": result.get("market_gaps", [])
            }
        )

    return result
```

### 4. Add Memory Consolidation Schedule

Create a scheduled task for periodic consolidation:

```python
# In backend/tasks/memory_tasks.py
import asyncio
from datetime import datetime, timedelta
from backend.memory.swarm_coordinator import _coordinator_registry

async def scheduled_memory_consolidation():
    """Scheduled task for periodic memory consolidation."""
    while True:
        try:
            # Consolidate memory for all active workspaces
            for workspace_id, coordinator in _coordinator_registry.items():
                if coordinator.active_agents:  # Only consolidate active workspaces
                    result = await coordinator.consolidate_swarm_memories()
                    logger.info(f"Consolidated memory for workspace {workspace_id}: {result}")

            # Wait before next consolidation (every 5 minutes)
            await asyncio.sleep(300)

        except Exception as e:
            logger.error(f"Scheduled memory consolidation failed: {e}")
            await asyncio.sleep(60)  # Wait 1 minute before retry

# Start the scheduled task in your application startup
async def start_memory_tasks():
    asyncio.create_task(scheduled_memory_consolidation())
```

### 5. API Integration

Add API endpoints for memory management:

```python
# In backend/api/v1/memory.py
from fastapi import APIRouter, Depends
from backend.memory.swarm_coordinator import get_swarm_memory_coordinator

router = APIRouter(prefix="/api/v1/memory", tags=["memory"])

@router.get("/workspace/{workspace_id}/stats")
async def get_memory_stats(workspace_id: str):
    coordinator = get_swarm_memory_coordinator(workspace_id)
    return await coordinator.get_swarm_memory_metrics()

@router.post("/workspace/{workspace_id}/consolidate")
async def trigger_consolidation(workspace_id: str, force: bool = False):
    coordinator = get_swarm_memory_coordinator(workspace_id)
    return await coordinator.consolidate_swarm_memories(force=force)

@router.get("/workspace/{workspace_id}/search")
async def search_memory(
    workspace_id: str,
    query: str,
    agent_filter: Optional[List[str]] = None,
    limit: int = 10
):
    coordinator = get_swarm_memory_coordinator(workspace_id)
    return await coordinator.search_swarm_memory(
        query=query,
        agent_filter=agent_filter,
        limit=limit
    )
```

## Performance Optimization

### 1. Cache Configuration

```python
# Configure cache size based on available memory
from backend.memory.cache import create_cached_coordinator

# For high-performance workspaces
high_perf_coordinator = create_cached_coordinator(
    coordinator,
    cache_size_mb=100  # 100MB cache
)

# For standard workspaces
standard_coordinator = create_cached_coordinator(
    coordinator,
    cache_size_mb=50   # 50MB cache
)
```

### 2. Memory Tier Optimization

```python
# Configure importance thresholds for memory tier placement
IMPORTANCE_THRESHOLDS = {
    "L3_STORAGE": 0.9,  # Semantic memory for very important content
    "L2_STORAGE": 0.7,  # Episodic memory for important content
    "L1_STORAGE": 0.0   # Short-term for everything else
}
```

### 3. Consolidation Frequency

```python
# Configure consolidation intervals based on workspace activity
CONSOLIDATION_INTERVALS = {
    "high_activity": timedelta(minutes=2),   # Active workspaces
    "medium_activity": timedelta(minutes=5), # Normal workspaces
    "low_activity": timedelta(minutes=15)    # Inactive workspaces
}
```

## Monitoring and Observability

### 1. Memory Metrics

Monitor these key metrics:

- **Cache Hit Rate**: Should be > 70% for optimal performance
- **Consolidation Duration**: Should complete in < 5 seconds
- **Memory Usage**: Monitor L1/L2/L3 distribution
- **Agent Memory Footprint**: Track per-agent memory usage

### 2. Health Checks

```python
async def memory_health_check(workspace_id: str) -> Dict[str, Any]:
    coordinator = get_swarm_memory_coordinator(workspace_id)
    stats = await coordinator.get_swarm_memory_metrics()

    health_status = {
        "status": "healthy",
        "issues": [],
        "recommendations": []
    }

    # Check cache performance
    if stats["cache_hit_rate"] < 0.7:
        health_status["issues"].append("Low cache hit rate")
        health_status["recommendations"].append("Increase cache size")

    # Check consolidation lag
    last_consolidation = datetime.fromisoformat(stats["last_consolidation"])
    if datetime.now() - last_consolidation > timedelta(minutes=10):
        health_status["issues"].append("Consolidation lag")
        health_status["recommendations"].append("Check consolidation task")

    return health_status
```

## Migration Strategy

### 1. Gradual Rollout

1. **Phase 1**: Deploy memory system alongside existing implementation
2. **Phase 2**: Enable memory recording for new agents only
3. **Phase 3**: Enable memory consolidation for test workspaces
4. **Phase 4**: Full rollout with migration of existing memories

### 2. Data Migration

```python
async def migrate_existing_memories(workspace_id: str):
    """Migrate existing memories to consolidated system."""
    coordinator = get_swarm_memory_coordinator(workspace_id)

    # Migrate L1 memories
    # Migrate L2 episodic memories
    # Migrate L3 semantic memories
    # Migrate swarm learning memories

    # Trigger consolidation
    await coordinator.consolidate_swarm_memories(force=True)
```

## Best Practices

### 1. Memory Importance Scoring

- **Research findings**: 0.8-0.9 (high importance)
- **Strategic decisions**: 0.9-1.0 (very high importance)
- **Creative outputs**: 0.6-0.8 (medium-high importance)
- **Execution results**: 0.5-0.7 (medium importance)
- **Debug logs**: 0.1-0.3 (low importance)

### 2. Search Optimization

- Use specific, relevant queries for better search results
- Apply agent filters when searching for agent-specific knowledge
- Use tier filters to target specific memory types
- Limit search results to prevent context overflow

### 3. Cache Management

- Monitor cache hit rates and adjust cache sizes
- Use appropriate TTL values based on content volatility
- Implement cache warming for frequently accessed content
- Clean up expired cache entries regularly

## Troubleshooting

### Common Issues

1. **Low Cache Hit Rate**
   - Increase cache size
   - Adjust TTL values
   - Check access patterns

2. **Slow Consolidation**
   - Reduce consolidation frequency
   - Optimize fragment scoring
   - Check database performance

3. **Memory Leaks**
   - Monitor memory usage trends
   - Implement proper cleanup
   - Check for circular references

4. **Search Inconsistency**
   - Verify embedding generation
   - Check vector indexing
   - Validate search filters

### Debug Tools

```python
# Enable debug logging
import logging
logging.getLogger("raptorflow.memory").setLevel(logging.DEBUG)

# Memory system diagnostics
async def memory_diagnostics(workspace_id: str):
    coordinator = get_swarm_memory_coordinator(workspace_id)

    return {
        "consolidator_stats": await coordinator.consolidator.get_memory_statistics(),
        "cache_stats": await coordinator.cache.get_cache_stats(),
        "agent_usage": coordinator.agent_memory_usage,
        "active_agents": list(coordinator.active_agents)
    }
```

## Conclusion

The consolidated memory system provides a unified, high-performance solution for managing memories across the RaptorFlow AI agent swarm. By following this integration guide, you can successfully implement the system and achieve significant improvements in memory efficiency, search performance, and cross-agent knowledge sharing.

For additional support or questions, refer to the test suite in `backend/tests/test_consolidated_memory.py` for comprehensive usage examples.
"""
