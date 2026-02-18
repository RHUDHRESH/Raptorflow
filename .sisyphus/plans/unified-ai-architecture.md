# RaptorFlow Unified AI Architecture

## The Problem
- 4 separate orchestrators with no unification
- Campaigns/Moves have NO AI - just CRUD
- Muse has 3 fragmented modes (single/council/swarm)
- No shared infrastructure
- No checkpointing, retries, or durable execution

## The Solution: Unified Agent Router

### Architecture Overview
```
User Request -> Agent Router -> Domain Agent -> AI Capabilities
```

### Domain Agents

#### 1. CampaignAgent (AI-Powered Campaigns)
**Replaces**: CampaignMovesOrchestrator (CRUD-only)

**Capabilities**:
- `plan_campaign(brief)` → AI creates strategy, suggests moves, generates timeline
- `optimize_campaign(campaign_id)` → AI analyzes performance, suggests improvements
- `suggest_moves(campaign_id)` → AI recommends optimal move sequence
- `predict_performance(campaign_id)` → AI forecasts campaign outcomes

**AI Integration**:
- Uses BCM context for brand voice
- Analyzes target ICPs
- Generates move strategy
- Creates content for each move
- Optimizes timing/channels

#### 2. MoveAgent (AI-Powered Moves)
**Replaces**: Move CRUD operations

**Capabilities**:
- `create_move_with_content(campaign_id, brief)` → AI generates complete move
- `generate_content(move_id, variants)` → A/B test variants
- `optimize_timing(move_id)` → AI suggests best send time
- `select_channels(move_id)` → AI recommends channels
- `execute_move(move_id)` → AI executes across channels

**AI Integration**:
- Content generation per move type
- Channel optimization
- Timing recommendations
- Performance prediction

#### 3. ContentAgent (Unified Generation)
**Replaces**: MuseOrchestrator (3 fragmented modes)

**Pattern**: Quality-based mode selection (not manual)

**Flow**:
1. Assess complexity → Simple or Complex
2. Simple → Single generation
3. Complex → Multi-draft with synthesis
4. No manual mode selection

**Capabilities**:
- `generate(task, content_type, context)` → Unified interface
- `_assess_complexity()` → AI determines generation strategy
- `_generate_single()` → Fast path
- `_generate_multi_draft()` → Quality path with synthesis

**Improvements**:
- Checkpointing after each step
- Retry logic with exponential backoff
- Timeout controls
- Unified prompt registry

#### 4. ContextAgent (Intelligent BCM)
**Replaces**: ContextOrchestrator

**Capabilities**:
- `synthesize_context(raw_data)` → AI converts inputs to structured BCM
- `extract_voice(content_samples)` → AI extracts brand voice
- `learn_from_feedback(feedback)` → AI improves from user feedback
- `reflect_and_suggest()` → AI reviews history, suggests updates
- `compact_context()` → AI compresses old context

**AI Integration**:
- Synthesizes raw business inputs
- Extracts voice from examples
- Learns from generation feedback
- Auto-updates based on performance

#### 5. ResearchAgent (AI Research)
**Replaces**: OptionalOrchestrator + Search/Scraper

**Capabilities**:
- `research(query)` → Plans, executes, synthesizes
- `plan_research_strategy(query)` → AI determines what to search
- `synthesize_findings(results)` → AI creates research report
- `monitor_topic(topic)` → Continuous research with AI filtering
- `extract_insights(content)` → AI extracts key insights

**AI Integration**:
- Query expansion
- Source quality assessment
- Fact extraction
- Report generation with citations

### Shared Infrastructure

#### BaseAgent
**File**: `backend/agents/domains/base.py`

All domain agents inherit from BaseAgent:
```python
class BaseAgent:
    def __init__(self):
        self.llm_client = get_llm_client()
        self.memory = get_memory_store()
        self.checkpointer = get_checkpointer()
        self.observer = get_observer()
    
    async def execute_with_retry(self, fn, max_retries=3):
        # Exponential backoff
        
    async def execute_with_timeout(self, fn, timeout=30):
        # Timeout wrapper
        
    def checkpoint(self, state):
        # Save state for resumption
```

#### Unified Router
**File**: `backend/agents/router.py`

```python
class RaptorFlowAgentRouter:
    def __init__(self):
        self.agents = {
            "campaign": CampaignAgent(),
            "move": MoveAgent(),
            "content": ContentAgent(),
            "context": ContextAgent(),
            "research": ResearchAgent(),
        }
    
    async def execute(self, intent, workspace_id, **kwargs):
        agent = self.agents[intent]
        return await agent.execute(workspace_id=workspace_id, **kwargs)
```

#### Prompt Registry
**File**: `backend/agents/prompts/registry.py`

```python
class PromptRegistry:
    _skills = {
        "campaign.planning": CampaignPlanningSkill(),
        "campaign.optimization": CampaignOptimizationSkill(),
        "move.content_generation": MoveContentSkill(),
        "move.channel_selection": ChannelSelectionSkill(),
        "content.email": EmailContentSkill(),
        "content.social": SocialContentSkill(),
        "context.synthesis": ContextSynthesisSkill(),
        "research.synthesis": ResearchSynthesisSkill(),
    }
```

### Feature-Agent Mapping

| Feature | Old | New | AI Capabilities |
|---------|-----|-----|-----------------|
| Campaigns | CRUD | CampaignAgent | Strategy, planning, optimization, prediction |
| Moves | CRUD | MoveAgent | Content generation, timing, channels, execution |
| Content | 3 fragmented modes | ContentAgent | Unified flow, automatic complexity detection |
| BCM | Basic ops | ContextAgent | Synthesis, voice extraction, learning, reflection |
| Search | Raw results | ResearchAgent | Query planning, synthesis, insights |
| Scraper | Raw scraping | ResearchAgent | Content extraction, summarization |

### Backend Integration

#### API Layer Changes

**Campaigns API**:
```python
@router.post("/")
async def create_campaign(
    brief: CampaignBrief,
    ai_assist: bool = True
):
    if ai_assist:
        return await agent_router.execute(
            intent="campaign",
            operation="plan_and_create",
            brief=brief
        )
```

**Moves API**:
```python
@router.post("/")
async def create_move(
    campaign_id: str,
    brief: MoveBrief,
    ai_content: bool = True
):
    if ai_content:
        return await agent_router.execute(
            intent="move",
            operation="create_with_content",
            campaign_id=campaign_id,
            brief=brief
        )
```

**Content API** (replaces Muse):
```python
@router.post("/generate")
async def generate_content(request: ContentRequest):
    return await agent_router.execute(
        intent="content",
        task=request.task,
        content_type=request.content_type,
        context=request.context
    )
```

### Migration Strategy

#### Phase 1: Foundation (Week 1)
- Create `BaseAgent` class
- Create `RaptorFlowAgentRouter`
- Create `PromptRegistry`
- Set up checkpointing infrastructure

#### Phase 2: Campaign/Move AI (Week 2-3)
- Build `CampaignAgent` with full AI capabilities
- Build `MoveAgent` with content generation
- Refactor Campaigns API
- Refactor Moves API

#### Phase 3: Content Unification (Week 3-4)
- Build `ContentAgent` (replaces Muse)
- Migrate all content generation
- Add checkpointing and retries
- Remove single/council/swarm fragmentation

#### Phase 4: Context/Research (Week 4-5)
- Build `ContextAgent` (replaces Context orchestrator)
- Build `ResearchAgent` (replaces Optional orchestrator)
- Add AI synthesis capabilities

#### Phase 5: Cleanup (Week 6)
- Remove old orchestrators
- Update tests
- Performance optimization

### Key Improvements

1. **Campaigns now have AI**: Strategy, planning, optimization
2. **Moves now have AI**: Content generation, timing, channels
3. **Content is unified**: No more fragmented modes
4. **All agents share infrastructure**: Retries, checkpointing, observability
5. **Single entry point**: Router pattern for all AI operations
6. **Durable execution**: Checkpointing for long-running operations
7. **Prompt registry**: Centralized, versioned prompts

### Files to Create

New Architecture:
```
backend/agents/
├── router.py                    # Unified router
├── domains/
│   ├── base.py                  # Base agent class
│   ├── campaign_agent.py        # AI-powered campaigns
│   ├── move_agent.py            # AI-powered moves
│   ├── content_agent.py         # Unified content generation
│   ├── context_agent.py         # Intelligent BCM
│   └── research_agent.py        # AI research
└── prompts/
    ├── registry.py              # Centralized prompts
    └── skills/                  # Skill-specific prompts
        ├── campaign_skills.py
        ├── move_skills.py
        ├── content_skills.py
        ├── context_skills.py
        └── research_skills.py
```

### Files to Remove (After Migration)

Old Architecture:
```
backend/agents/muse/orchestrator.py
backend/agents/context/orchestrator.py
backend/agents/campaign_moves/orchestrator.py
backend/agents/optional/orchestrator.py
backend/ai/prompts/__init__.py
```

This architecture transforms RaptorFlow from a fragmented CRUD app with some AI into a unified AI-powered platform where every feature has intelligent assistance.
