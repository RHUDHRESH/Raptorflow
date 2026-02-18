# RaptorFlow AI Architecture Fix - Implementation Plan

## Problem Statement
The AI system is fragmented:
- **Moves** has NO AI backing - just CRUD operations
- **4 separate orchestrators** (Muse, Context, CampaignMoves, Optional) with no unification
- **Multiple patterns** (single/council/swarm) without coherent architecture
- **Scattered prompts** everywhere
- **No feature-agent linkage** - features exist independently of AI capabilities

## Solution: Unified Agent Architecture

Based on research (LangChain multi-agent patterns, Anthropic best practices, Google agent architecture):

### Core Pattern: Router + Domain Agents
- **Router**: Single entry point (`RaptorFlowAgentRouter`)
- **Domain Agents**: Specialized agents per feature domain
  - `CampaignAgent` - Gives Moves actual AI capabilities
  - `ContentAgent` - Unified content generation (replaces Muse)
  - `ContextAgent` - BCM operations (replaces Context orchestrator)
  - `ResearchAgent` - Search/scraper (replaces Optional orchestrator)

## Implementation Files to Create

### 1. Router (Entry Point)
**File**: `backend/agents/router.py`
- Routes intents to domain-specific agents
- Single `execute(intent, workspace_id, **kwargs)` interface
- Convenience methods: `generate_content()`, `plan_campaign()`, `suggest_moves()`, etc.

### 2. CampaignAgent (Moves + AI)
**File**: `backend/agents/domains/campaign_agent.py`

**Capabilities**:
- `plan_and_create(brief)` - AI plans campaign strategy, suggests moves, generates content
- `suggest_moves(campaign_id)` - AI analyzes campaign and recommends optimal moves
- `optimize_campaign(campaign_id)` - AI reviews performance and suggests improvements
- `generate_move_content(move_id, content_type)` - AI generates content for specific move
- `execute_move(move_id)` - AI executes move across channels

**Why this fixes Moves**: Currently Moves just stores JSON. CampaignAgent adds:
- Strategic planning
- Move sequencing optimization
- Content generation per move
- Performance analysis
- Recommendations

### 3. ContentAgent (Unified Generation)
**File**: `backend/agents/domains/content_agent.py`

**Replaces**: Muse orchestrator + swarm/council/single modes

**Pattern**: Skills (progressive disclosure)
- Load specialized prompts based on content_type
- Single unified generation flow
- Quality assessment determines if multi-draft needed

**Capabilities**:
- `generate(task, content_type)` - Primary generation
- `_assess_complexity()` - Determine if simple or multi-draft
- `_generate_single()` - Fast path for simple content
- `_generate_with_drafts()` - Quality path for complex content

### 4. ContextAgent (BCM Operations)
**File**: `backend/agents/domains/context_agent.py`

**Replaces**: Context orchestrator

**Capabilities**:
- `seed(raw_data)` - AI synthesizes raw inputs into structured BCM
- `reflect()` - AI reviews generation history, suggests BCM updates
- `update_from_feedback(feedback)` - AI learns from user feedback
- `synthesize_voice()` - AI extracts voice patterns from content

### 5. ResearchAgent (Search + Scraper)
**File**: `backend/agents/domains/research_agent.py`

**Replaces**: Optional orchestrator

**Capabilities**:
- `research(query)` - Plans and executes multi-source research
- `synthesize_findings(results)` - AI synthesizes research into actionable insights
- `monitor_topic(topic)` - Continuous monitoring with AI filtering

### 6. Prompt Registry (Unified Prompts)
**File**: `backend/agents/prompts/registry.py`

**Pattern**: Skills-based organization

```python
class PromptRegistry:
    _skills = {
        "content.email": EmailSkill(),
        "content.social": SocialSkill(),
        "content.blog": BlogSkill(),
        "campaign.planning": CampaignPlanningSkill(),
        "campaign.move_suggestion": MoveSuggestionSkill(),
        "context.synthesis": ContextSynthesisSkill(),
        "research.synthesis": ResearchSynthesisSkill(),
    }
```

**Skill Structure**:
- `system_prompt` - Base instructions
- `compile(context)` - Inject BCM data
- `examples` - Few-shot examples
- `guardrails` - Constraints and rules

### 7. Base Agent Class
**File**: `backend/agents/domains/base.py`

**Shared infrastructure**:
- LLM client management
- Memory/persistence hooks
- Observability integration
- Error handling patterns
- Retry logic
- Cost tracking

### 8. Refactored Campaign Moves API
**File**: `backend/api/v1/campaigns/router.py`

**Before**:
```python
@router.post("/")
async def create_campaign(workspace_id: str, payload: dict):
    return campaign_service.create_campaign(workspace_id, payload)  # Just stores JSON
```

**After**:
```python
@router.post("/")
async def create_campaign(
    workspace_id: str, 
    brief: CampaignBrief,
    ai_assist: bool = True
):
    if ai_assist:
        # Use CampaignAgent for AI-powered creation
        return await agent_router.plan_campaign(workspace_id, brief)
    else:
        # Fallback to basic CRUD
        return campaign_service.create_campaign(workspace_id, brief)
```

## Migration Path

### Phase 1: Create Router + ContentAgent (Week 1)
1. Create `backend/agents/router.py`
2. Create `backend/agents/domains/base.py`
3. Create `backend/agents/domains/content_agent.py`
4. Port Muse orchestrator logic
5. Add backward compatibility layer

### Phase 2: CampaignAgent - Give Moves AI (Week 2)
1. Create `backend/agents/domains/campaign_agent.py`
2. Design AI capabilities for campaign planning
3. Create campaign planning skill prompts
4. Refactor Campaign Moves API to use agent
5. Add `suggest_moves` endpoint
6. Add `optimize_campaign` endpoint

### Phase 3: ContextAgent + ResearchAgent (Week 2)
1. Migrate Context orchestrator → ContextAgent
2. Migrate Optional orchestrator → ResearchAgent
3. Update all API endpoints

### Phase 4: Prompt Registry + Skills (Week 1)
1. Create `backend/agents/prompts/registry.py`
2. Migrate all prompts to skills
3. Update agents to use registry

### Phase 5: Cleanup (Week 1)
1. Remove old orchestrators
2. Update tests
3. Documentation

## Key Design Decisions

### 1. Single Router vs Multiple Entry Points
**Decision**: Single router with intent routing
**Rationale**: Consistent interface, centralized observability, easier to reason about

### 2. Domain Agents vs Tool-Heavy Single Agent
**Decision**: Domain-specific agents
**Rationale**: Better context isolation, parallel development, domain-specific optimization

### 3. Skills vs Inline Prompts
**Decision**: Skills-based prompt organization
**Rationale**: Progressive disclosure, team ownership, easier maintenance

### 4. When to Use Multi-Draft
**Decision**: AI assesses complexity, decides single vs multi-draft
**Rationale**: Cost optimization for simple tasks, quality for complex tasks

## Success Metrics

- **Campaign Creation**: 90%+ of campaigns use AI assistance
- **Move Suggestions**: AI suggests moves for 80%+ of campaigns
- **Content Quality**: User acceptance rate >85%
- **System Coherence**: Single router handles 100% of AI operations
- **Prompt Organization**: 100% of prompts in registry

## Files to Delete (After Migration)
- `backend/agents/muse/orchestrator.py`
- `backend/agents/context/orchestrator.py`
- `backend/agents/campaign_moves/orchestrator.py`
- `backend/agents/optional/orchestrator.py`
- `backend/ai/prompts/__init__.py` (migrate to skills)

## Files to Create (New Architecture)
- `backend/agents/router.py`
- `backend/agents/domains/base.py`
- `backend/agents/domains/campaign_agent.py`
- `backend/agents/domains/content_agent.py`
- `backend/agents/domains/context_agent.py`
- `backend/agents/domains/research_agent.py`
- `backend/agents/prompts/registry.py`
- `backend/agents/prompts/skills/*.py` (skill-specific prompts)

## Backward Compatibility

During migration, maintain compatibility:
```python
# Old API continues to work
campaign_service.create_campaign(...)  # Basic CRUD

# New AI-powered API
agent_router.plan_campaign(...)  # Full AI assistance
```

After full migration, deprecate old paths.

## Testing Strategy

1. **Unit Tests**: Each agent in isolation
2. **Integration Tests**: Router + agents
3. **End-to-End**: Full user workflows
4. **A/B Tests**: AI-assisted vs manual creation

## Cost Considerations

- **Campaign Planning**: ~2K tokens per campaign (Gemini Flash: $0.00015)
- **Content Generation**: Variable based on complexity
- **Research**: Parallel search + synthesis (~5K tokens)

**Optimization**: Cache planning results, reuse research across campaigns

## Rollout Plan

1. **Week 1**: Deploy Router + ContentAgent (behind feature flag)
2. **Week 2**: Enable CampaignAgent for beta users
3. **Week 3**: Full rollout of all agents
4. **Week 4**: Remove old orchestrators

## Documentation Updates

- API documentation for new endpoints
- Agent capabilities guide
- Prompt engineering guidelines
- Migration guide for developers

## Immediate Next Steps

1. Create `backend/agents/router.py`
2. Create `backend/agents/domains/base.py`
3. Begin `backend/agents/domains/campaign_agent.py`
4. Design first skill: `CampaignPlanningSkill`

This plan transforms RaptorFlow from fragmented orchestrators to a unified, feature-specific AI architecture.
