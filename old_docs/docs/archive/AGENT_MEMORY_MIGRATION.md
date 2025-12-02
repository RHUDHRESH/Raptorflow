# Agent Memory Integration Migration Guide

## Overview

This document provides a comprehensive guide for migrating all RaptorFlow agents to use the new memory-enhanced base classes (`BaseAgentEnhanced` and `BaseSupervisorEnhanced`).

**Status**: 1/35+ agents migrated
**Completed**: ICPBuilderAgent ✅
**In Progress**: Research, Content, Strategy, Analytics, Execution, Safety, Onboarding agents

---

## Architecture Changes

### New Components

1. **MemoryManager** (`backend/services/memory_manager.py`)
   - Vector-based memory storage using Supabase + pgvector
   - Semantic search for retrieving relevant past experiences
   - Workspace-isolated memory for multi-tenancy
   - Success scoring and feedback incorporation

2. **BaseAgentEnhanced** (`backend/agents/base_agent_enhanced.py`)
   - Extends `BaseAgent` with memory capabilities
   - Automatic memory context management
   - Convenience methods: `remember()`, `recall()`, `learn_from_feedback()`
   - Auto-remember feature for automatic memory storage

3. **BaseSupervisorEnhanced** (`backend/agents/base_agent_enhanced.py`)
   - Extends `BaseSupervisor` with memory capabilities
   - Tracks successful routing decisions and agent combinations
   - Learns from past supervisor executions

### Database Schema

**New Table**: `agent_memories`
```sql
CREATE TABLE agent_memories (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID NOT NULL REFERENCES workspaces(id),
    agent_name TEXT NOT NULL,
    memory_type TEXT NOT NULL, -- 'success', 'failure', 'preference', 'insight'
    context JSONB NOT NULL,
    result JSONB NOT NULL,
    embedding VECTOR(768), -- pgvector for semantic search
    success_score FLOAT NOT NULL DEFAULT 0.5,
    feedback JSONB,
    tags TEXT[],
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_agent_memories_workspace_agent ON agent_memories(workspace_id, agent_name);
CREATE INDEX idx_agent_memories_type ON agent_memories(memory_type);
CREATE INDEX idx_agent_memories_score ON agent_memories(success_score);
CREATE INDEX idx_agent_memories_embedding ON agent_memories USING ivfflat (embedding vector_cosine_ops);
```

**Required RPC Function**:
```sql
CREATE OR REPLACE FUNCTION search_agent_memories(
    query_embedding VECTOR(768),
    filter_workspace_id UUID,
    filter_agent_name TEXT,
    filter_memory_types TEXT[],
    filter_tags TEXT[],
    min_score FLOAT,
    match_count INT
)
RETURNS TABLE (
    id UUID,
    context JSONB,
    result JSONB,
    success_score FLOAT,
    feedback JSONB,
    tags TEXT[],
    created_at TIMESTAMP,
    similarity FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        m.id,
        m.context,
        m.result,
        m.success_score,
        m.feedback,
        m.tags,
        m.created_at,
        1 - (m.embedding <=> query_embedding) AS similarity
    FROM agent_memories m
    WHERE m.workspace_id = filter_workspace_id
        AND m.agent_name = filter_agent_name
        AND (filter_memory_types IS NULL OR m.memory_type = ANY(filter_memory_types))
        AND (filter_tags IS NULL OR m.tags && filter_tags)
        AND m.success_score >= min_score
    ORDER BY m.embedding <=> query_embedding
    LIMIT match_count;
END;
$$ LANGUAGE plpgsql;
```

---

## Migration Pattern

### Pattern A: Agents Currently Inheriting from BaseAgent

**Example**: ICPBuilderAgent (COMPLETED ✅)

**Before**:
```python
from backend.agents.base_agent import BaseAgent

class ICPBuilderAgent(BaseAgent):
    def __init__(self):
        super().__init__(name="ICPBuilderAgent")

    async def execute(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        # Agent logic
        return {"agent": self.name, "output": result}
```

**After**:
```python
from backend.agents.base_agent_enhanced import BaseAgentEnhanced

class ICPBuilderAgent(BaseAgentEnhanced):
    def __init__(self):
        super().__init__(name="ICPBuilderAgent", auto_remember=True)

    async def _execute_with_memory(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        # 1. Recall similar past successes
        past_successes = await self.recall(
            query=f"successful ICP for {payload['industry']}",
            memory_types=["success"],
            min_success_score=0.7,
            top_k=3
        )

        # 2. Extract patterns from past successes
        patterns = self._extract_patterns(past_successes)

        # 3. Use patterns in execution
        result = await self._do_work(payload, patterns)

        # 4. Calculate success score
        success_score = self._calculate_success(result)

        # 5. Return result (auto-stored by auto_remember=True)
        return {
            "status": "success",
            "agent": self.name,
            "output": result,
            "success_score": success_score
        }
```

**Key Changes**:
1. Import `BaseAgentEnhanced` instead of `BaseAgent`
2. Add `auto_remember=True` to constructor
3. Rename `execute()` → `_execute_with_memory()`
4. Add memory recall at start
5. Include `success_score` in return value
6. Add pattern extraction and success calculation helpers

---

### Pattern B: Agents NOT Inheriting from BaseAgent

**Example**: HookGeneratorAgent, BlogWriterAgent (35+ agents)

**Before**:
```python
import structlog
from backend.services.vertex_ai_client import vertex_ai_client

class HookGeneratorAgent:
    def __init__(self):
        self.llm = vertex_ai_client

    async def generate_hooks(self, topic, icp_profile, count=5):
        # Agent logic
        return hooks
```

**After**:
```python
import structlog
from backend.agents.base_agent_enhanced import BaseAgentEnhanced
from backend.services.vertex_ai_client import vertex_ai_client

class HookGeneratorAgent(BaseAgentEnhanced):
    def __init__(self):
        super().__init__(name="HookGeneratorAgent", auto_remember=True)
        self.llm = vertex_ai_client

    async def _execute_with_memory(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Execute with standard interface."""
        # Extract parameters
        topic = payload.get("topic")
        icp_profile = payload.get("icp_profile")
        count = payload.get("count", 5)

        # Call existing method
        hooks = await self.generate_hooks(topic, icp_profile, count)

        return {
            "status": "success",
            "agent": self.name,
            "output": {"hooks": hooks},
            "success_score": sum(h.score for h in hooks) / len(hooks)
        }

    async def generate_hooks(self, topic, icp_profile, count=5):
        # 1. Recall high-performing hooks for similar topics
        past_hooks = await self.recall(
            query=f"successful hooks for {topic} targeting {icp_profile.name}",
            memory_types=["success"],
            min_success_score=0.7,
            top_k=3
        )

        # 2. Extract successful patterns
        successful_styles = self._extract_hook_styles(past_hooks)

        # 3. Generate with learned patterns
        prompt = self._build_prompt(topic, icp_profile, successful_styles)
        hooks = await self.llm.chat_completion(...)

        return hooks
```

**Key Changes**:
1. Inherit from `BaseAgentEnhanced`
2. Call `super().__init__()` with agent name
3. Implement `_execute_with_memory()` for standard interface
4. Add memory recall to existing methods
5. Extract and use patterns from past successes

---

### Pattern C: Supervisors

**Example**: ContentSupervisor, StrategySupervisor

**Before**:
```python
from backend.agents.base_agent import BaseSupervisor

class ContentSupervisor(BaseSupervisor):
    def __init__(self):
        super().__init__(name="ContentSupervisor")
        self.register_agent("hook_generator", HookGeneratorAgent())

    async def execute(self, goal: str, context: Dict[str, Any]) -> Dict[str, Any]:
        # Routing logic
        return result
```

**After**:
```python
from backend.agents.base_agent_enhanced import BaseSupervisorEnhanced

class ContentSupervisor(BaseSupervisorEnhanced):
    def __init__(self):
        super().__init__(name="ContentSupervisor", auto_remember=True)
        self.register_agent("hook_generator", HookGeneratorAgent())

    async def _execute_with_memory(self, goal: str, context: Dict[str, Any]) -> Dict[str, Any]:
        # 1. Recall similar past goals
        similar_goals = await self.recall(
            query=f"content generation: {goal}",
            memory_types=["success"],
            top_k=3
        )

        # 2. Learn from past routing decisions
        best_agent_sequence = self._extract_routing_pattern(similar_goals)

        # 3. Execute with learned patterns
        result = await self._route_to_agents(goal, context, best_agent_sequence)

        return {
            "status": "success",
            "result": result,
            "success_score": self._calculate_quality(result)
        }
```

---

## Agent-Specific Integration Examples

### Research Agents

#### ICPBuilderAgent ✅ (COMPLETED)
- **Recalls**: Past ICPs for similar industries
- **Learns**: Common pain points, triggers, decision structures
- **Stores**: Generated ICP with confidence and completeness scores

#### PersonaNarrativeAgent
- **Recalls**: Effective narrative styles for similar personas
- **Learns**: Storytelling patterns that resonate
- **Stores**: Narratives with engagement predictions

#### PainPointMinerAgent
- **Recalls**: Previously discovered pain points for similar products
- **Learns**: Which sources yield high-quality insights
- **Stores**: Pain points with source quality scores

---

### Content Agents

#### HookGeneratorAgent
- **Recalls**: High-performing hooks for same ICP/topic
- **Learns**: Which hook styles work best (curiosity, pain-agitate-solve, etc.)
- **Stores**: Hooks with predicted engagement scores

#### BlogWriterAgent
- **Recalls**: Successful blog structures for similar topics
- **Learns**: Effective section flows, CTAs, and conclusions
- **Stores**: Blogs with readability and engagement metrics

#### EmailWriterAgent
- **Recalls**: High open-rate subject lines and email structures
- **Learns**: Optimal email length and CTA placement
- **Stores**: Emails with open/click predictions

---

### Strategy Agents

#### CampaignPlannerAgent
- **Recalls**: Successful campaign plans for similar budgets/timeframes
- **Learns**: Which "chess moves" work for different contexts
- **Stores**: Campaign plans with projected ROI

#### MarketResearchAgent
- **Recalls**: Past market insights for similar industries
- **Learns**: Which data sources are most reliable
- **Stores**: Market research with confidence scores

---

### Analytics Agents

#### MetricsCollectorAgent
- **Recalls**: Baseline metrics for similar campaigns
- **Learns**: Which metrics are most predictive of success
- **Stores**: Collected metrics with data quality scores

#### InsightAgent
- **Recalls**: Similar patterns in past campaign performance
- **Learns**: Which insights lead to successful pivots
- **Stores**: Insights with actionability scores

---

## Graph State Updates

All state classes now include memory-related fields:

```python
class ResearchState(BaseAgentState):
    # ... existing fields ...
    past_successes: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Memory references to similar successful ICPs"
    )
    preferences: Dict[str, Any] = Field(
        default_factory=dict,
        description="User/workspace preferences for ICP generation"
    )

class ContentState(BaseAgentState):
    # ... existing fields ...
    past_successes: List[Dict[str, Any]] = Field(
        default_factory=list,
        description="Memory of high-performing content for same ICP/topic"
    )
    preferences: Dict[str, Any] = Field(
        default_factory=dict,
        description="Content generation preferences (tone, style, length)"
    )
```

---

## Testing Strategy

### Unit Tests
```python
# backend/tests/test_memory_integration.py

async def test_icp_builder_recalls_similar_icps():
    """Test that ICP builder recalls and uses past successful ICPs."""
    agent = ICPBuilderAgent()

    # Create test workspace and store a successful ICP
    workspace_id = "test-workspace-123"
    await agent.set_workspace(workspace_id)

    # Store a past success
    await agent.remember(
        context={"industry": "SaaS", "product": "Marketing automation"},
        result={"icp": {...}, "confidence": 0.9},
        success_score=0.9,
        tags=["b2b", "saas"]
    )

    # Execute for similar context
    result = await agent.execute({
        "workspace_id": workspace_id,
        "industry": "SaaS",
        "product": "Sales automation"
    })

    # Verify it used past patterns
    assert result["used_past_patterns"] == True
    assert result["success_score"] >= 0.7
```

### Integration Tests
```python
async def test_two_workspaces_different_memories():
    """Verify workspace isolation - memories don't leak."""
    agent = ICPBuilderAgent()

    # Workspace A: SaaS focus
    await agent.set_workspace("workspace-a")
    await agent.remember(...)

    # Workspace B: Healthcare focus
    await agent.set_workspace("workspace-b")
    memories = await agent.recall(query="SaaS product")

    # Should return empty - workspace A memories not visible
    assert len(memories) == 0
```

---

## Migration Checklist

### Phase 1: Infrastructure ✅
- [x] Create MemoryManager service
- [x] Create BaseAgentEnhanced class
- [x] Create BaseSupervisorEnhanced class
- [x] Update graph state classes

### Phase 2: Research Agents (3 agents)
- [x] ICPBuilderAgent
- [ ] PersonaNarrativeAgent
- [ ] PainPointMinerAgent

### Phase 3: Content Agents (7 agents)
- [ ] HookGeneratorAgent
- [ ] BlogWriterAgent
- [ ] EmailWriterAgent
- [ ] SocialCopyAgent
- [ ] BrandVoiceAgent
- [ ] CarouselAgent
- [ ] MemeAgent

### Phase 4: Strategy Agents (4 agents)
- [ ] CampaignPlannerAgent
- [ ] MarketResearchAgent
- [ ] AmbientSearchAgent
- [ ] SynthesisAgent

### Phase 5: Analytics Agents (5 agents)
- [ ] MetricsCollectorAgent
- [ ] InsightAgent
- [ ] CampaignReviewAgent
- [ ] AnalyticsAgent (wrapper)
- [ ] AnalyticsSupervisor

### Phase 6: Execution Agents (7 agents)
- [ ] TwitterAgent
- [ ] LinkedInAgent
- [ ] InstagramAgent
- [ ] EmailAgent (publisher)
- [ ] SchedulerAgent
- [ ] CanvaAgent
- [ ] ImageGenAgent

### Phase 7: Safety Agents (3 agents)
- [ ] CriticAgent
- [ ] GuardianAgent
- [ ] AssetQualityAgent

### Phase 8: Onboarding Agents (2 agents)
- [ ] QuestionAgent
- [ ] ProfileBuilderAgent

### Phase 9: Supervisors (5 supervisors)
- [ ] ContentSupervisor
- [ ] StrategySupervisor
- [ ] ExecutionSupervisor
- [ ] CustomerIntelligenceSupervisor
- [ ] MasterOrchestrator

### Phase 10: Testing & Validation
- [ ] Write integration tests for workspace isolation
- [ ] Test memory-driven behavior improvements
- [ ] Validate success score calculations
- [ ] Test feedback incorporation
- [ ] Performance testing with large memory datasets

---

## Common Pitfalls

1. **Forgetting to set workspace**: Always call `set_workspace()` before using memory
2. **Not including success_score**: Return value must include `success_score` for auto-remember
3. **Workspace ID not in payload**: Ensure all execute() calls include workspace_id
4. **Memory initialization timing**: Memory is initialized lazily - check that workspace is set
5. **Pattern extraction errors**: Handle empty past_successes gracefully

---

## Performance Considerations

1. **Vector Search Cost**: Limit `top_k` to 3-5 results to balance relevance vs. latency
2. **Embedding Generation**: Embeddings are generated asynchronously; cache when possible
3. **Memory Growth**: Implement periodic cleanup of low-success memories
4. **Query Optimization**: Use specific queries with relevant tags for faster retrieval

---

## Next Steps

1. Complete Research agent migrations
2. Update Content agents systematically
3. Add integration tests for each domain
4. Monitor memory usage and performance
5. Gather feedback on memory-driven improvements
6. Iterate on success score calculations
