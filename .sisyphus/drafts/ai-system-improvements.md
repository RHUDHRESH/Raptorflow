# Draft: AI System Analysis & Improvement Plan

## Current Architecture Overview

### Core Components

**1. LangGraph Orchestrators (4 main orchestrators)**

Located in `backend/agents/`:

#### LangGraphMuseOrchestrator (`backend/agents/muse/orchestrator.py`)
- **Purpose**: AI content generation (primary AI workload)
- **State**: `MuseGraphState` - TypedDict with workspace_id, task, content_type, tone, etc.
- **Nodes**:
  1. `resolve_profile` - Determines execution parameters from reasoning_depth/intensity
  2. `load_workspace_context` - Loads BCM manifest and memories
  3. `compile_prompt` - Builds system/user prompts
  4. `run_generation` - Calls Vertex AI (single/council/swarm modes)
  5. `log_generation` - Logs to BCM generation logger + auto-reflection
  6. `assemble_response` - Formats final response
- **Execution Modes**:
  - `single`: One generation call
  - `council`: Two agents (analyst + creative) + synthesis
  - `swarm`: Three specialists (strategist, copywriter, critic) + synthesis
- **Fallback**: Deterministic fallback on AI failure (rule-based templates)

#### LangGraphContextOrchestrator (`backend/agents/context/orchestrator.py`)
- **Purpose**: BCM context operations
- **Operations**: seed, rebuild, reflect
- **State**: `ContextGraphState`
- Uses conditional edges to route to appropriate operation

#### LangGraphCampaignMovesOrchestrator (`backend/agents/campaign_moves/orchestrator.py`)
- **Purpose**: Campaign and move CRUD operations
- **Operations**: list/create/get/update/delete for both campaigns and moves
- **State**: `CampaignMoveState`
- Simple router pattern with conditional edges

#### LangGraphOptionalOrchestrator (`backend/agents/optional/orchestrator.py`)
- **Purpose**: Optional modules (search, scraper)
- **Nodes**:
  1. `check_enabled` - Feature flag check
  2. `resolve_runtime_profile` - Intensity/execution_mode normalization
  3. `execute` - Calls provided executor function
  4. `finalize` - Adds metadata to result

**2. AI Backend Abstraction (`backend/ai/backends/`)**

#### BaseAIBackend (`backend/ai/backends/base.py`)
- Abstract base class with Protocol
- Handles: cost calculation, result creation, model failover
- Properties: backend_type, model_name, cost rates

#### VertexAIBackend (`backend/ai/backends/vertex_ai.py`)
- **Provider**: Google Vertex AI (Gemini models)
- **Features**:
  - Automatic credential resolution (searches multiple paths)
  - Rate limiting (requests_per_minute/hour)
  - Model failover (gemini-2.0-flash → gemini-2.0-flash-lite → gemini-1.5-flash)
  - Cost tracking (Gemini pricing)
- **Models**: gemini-2.0-flash (default), with fallback chain

#### Other Backends
- `genai_api_key.py` - Google GenAI with API key
- `deterministic.py` - Rule-based fallback (no AI)

**3. Runtime Profiles (`backend/agents/runtime/profiles.py`)**

```python
INTENSITY_PROFILES = {
    "low": {
        "muse": {"reasoning_depth": "low", "token_multiplier": 0.75, "ensemble_cap": 1},
        "search": {"default_engines": ["duckduckgo"], "max_results": 10},
        "scraper": {"default_strategy": "conservative", "timeout_seconds": 45},
    },
    "medium": {
        "muse": {"reasoning_depth": "medium", "token_multiplier": 1.0, "ensemble_cap": 2},
        "search": {"default_engines": ["duckduckgo", "brave"], "max_results": 20},
        "scraper": {"default_strategy": "balanced", "timeout_seconds": 30},
    },
    "high": {
        "muse": {"reasoning_depth": "high", "token_multiplier": 1.25, "ensemble_cap": 3},
        "search": {"default_engines": ["duckduckgo", "brave", "searx"], "max_results": 40},
        "scraper": {"default_strategy": "optimized", "timeout_seconds": 25},
    },
}
```

**4. Prompt System (`backend/ai/prompts/__init__.py`)**

- `compile_system_prompt()` - Builds prompts from BCM manifest
  - Supports synthesized BCM (identity + prompt_kit + guardrails_v2)
  - Falls back to legacy foundation-based prompts
- `build_user_prompt()` - Simple task formatting

**5. Business Context Memory (BCM)**

Located in `backend/bcm/` and `backend/services/bcm/`:
- **Core**: Types, reducers for BCM state management
- **Memory**: Memory storage and retrieval
- **Reflection**: Auto-reflection triggers after generation
- **Generation Logger**: Tracks all AI generations

**6. Types (`backend/ai/types.py`)**

Key dataclasses:
- `GenerationRequest` - Input to backend
- `GenerationResult` - Output with tokens, cost, timing
- `BackendHealth` - Health check response
- `CostRecord` - Cost tracking entry

### Integration Patterns

**FastAPI → LangGraph Flow:**
```
API Route → Service → Orchestrator.invoke() → LangGraph.ainvoke() → Nodes → Vertex AI
```

**Key Integration Points:**
- `backend/api/v1/muse/routes.py` → `muse_service.generate()` → `langgraph_muse_orchestrator.invoke()`
- `backend/api/v1/context/routes.py` → `langgraph_context_orchestrator.seed/rebuild/reflect`
- `backend/api/v1/campaigns/routes.py` → `langgraph_campaign_moves_orchestrator.*`
- `backend/api/v1/search/routes.py` → `langgraph_optional_orchestrator.run()`

---

## Strengths of Current System

1. **Clean Architecture**
   - Clear separation: domain → application → adapters
   - Protocol-based backend abstraction allows swapping providers
   - TypedDict states provide type safety

2. **Multi-Mode Execution**
   - Single/Council/Swarm modes for different quality/cost tradeoffs
   - Intensity profiles (low/medium/high) for resource control
   - Deterministic fallback ensures reliability

3. **Cost Awareness**
   - Token counting on every request
   - Cost calculation per generation
   - Rate limiting in VertexAIBackend

4. **Business Context Integration**
   - BCM manifest feeds into prompts
   - Memory system for learned preferences
   - Auto-reflection after generations

5. **Testing Coverage**
   - Unit tests for orchestrators
   - Mock-based testing with monkeypatch
   - Characterization tests for API contracts

6. **Error Handling**
   - Try/catch in generation with fallback
   - Graceful degradation to deterministic output
   - Logging of warnings (not failures) for resilience

---

## Identified Gaps & Improvement Opportunities

### 1. **Observability & Monitoring**

**Current State:**
- Basic logging with Python logger
- Generation logging to BCM
- No distributed tracing
- No metrics collection

**Gap:**
- No visibility into graph execution flow
- No latency breakdown by node
- No error rate tracking
- No cost dashboards

**Improvement:**
- Add OpenTelemetry tracing for each LangGraph node
- Track per-node execution time
- Export metrics (Prometheus/OpenTelemetry)
- Create cost/performance dashboards

### 2. **Streaming Support**

**Current State:**
- All generation is synchronous/batch
- No streaming tokens to client
- Client waits for full completion

**Gap:**
- Poor UX for long generations
- No progress indication
- Cannot interrupt generation

**Improvement:**
- Implement token streaming via Server-Sent Events (SSE)
- Add `astream()` support to backends
- Frontend streaming consumption
- Progress callbacks in LangGraph nodes

### 3. **Advanced Memory Management**

**Current State:**
- Simple memory retrieval from BCM
- No conversation history tracking
- No context window management

**Gap:**
- No conversation threading
- Context window overflow risk
- No memory summarization for long contexts

**Improvement:**
- Conversation thread management
- Context window monitoring and truncation
- Sliding window memory for long conversations
- Memory summarization for historical context

### 4. **Caching Layer**

**Current State:**
- No caching of AI responses
- Every request hits the model
- No deduplication

**Gap:**
- Expensive redundant calls
- Latency not optimized
- No cache invalidation strategy

**Improvement:**
- Semantic caching (embeddings-based)
- Exact match caching for identical prompts
- Cache TTL based on content type
- Cache warming for common queries

### 5. **Tool Use & Function Calling**

**Current State:**
- No structured tool use
- No function calling patterns
- Deterministic fallback uses templates only

**Gap:**
- Cannot call external tools/APIs
- No tool-augmented generation
- Limited agent capabilities

**Improvement:**
- Add ToolNode to LangGraph workflows
- Implement function calling with Gemini
- Tool registry and validation
- Parallel tool execution

### 6. **Prompt Versioning & Management**

**Current State:**
- Prompts hardcoded in `backend/ai/prompts/`
- No versioning system
- No A/B testing capability

**Gap:**
- Cannot iterate on prompts safely
- No prompt performance tracking
- No systematic optimization

**Improvement:**
- Prompt registry with versions
- Database-stored prompts
- A/B testing framework
- Prompt performance analytics

### 7. **Rate Limiting & Quotas**

**Current State:**
- Per-backend rate limiting (requests/minute, requests/hour)
- No per-workspace or per-user limits
- No quota management

**Gap:**
- Cannot prevent abuse
- No tiered limits
- No cost controls

**Improvement:**
- Per-workspace rate limiting
- Per-user quotas
- Token budget management
- Alerting on approaching limits

### 8. **Retry & Circuit Breaker Patterns**

**Current State:**
- Model failover in VertexAIBackend
- Single retry attempt (implicit in failover)
- No circuit breaker

**Gap:**
- No exponential backoff
- No circuit breaker for failing backends
- Cascade failure risk

**Improvement:**
- Exponential backoff with jitter
- Circuit breaker pattern for backends
- Dead letter queue for failed generations
- Automatic recovery detection

### 9. **Async Task Queue Integration**

**Current State:**
- Reflection runs via `asyncio.create_task()`
- No persistent task queue
- Risk of losing tasks on restart

**Gap:**
- No guaranteed execution
- No task prioritization
- No retry for reflection

**Improvement:**
- Integrate with task queue (Celery/RQ)
- Persistent job storage
- Priority queues for different operation types
- Scheduled/reflection jobs

### 10. **Evaluation & Testing**

**Current State:**
- Unit tests with mocks
- No evaluation framework
- No regression testing for AI outputs

**Gap:**
- Cannot measure quality improvements
- No systematic testing of prompts
- Risk of regressions

**Improvement:**
- LLM-as-judge evaluation framework
- Regression test suite with expected outputs
- A/B testing for prompt changes
- Quality metrics tracking

### 11. **Security & Safety**

**Current State:**
- Basic input validation through Pydantic
- No prompt injection detection
- No content filtering

**Gap:**
- Prompt injection vulnerability
- No output moderation
- Potential data leakage

**Improvement:**
- Prompt injection detection
- Input sanitization
- Output content moderation
- PII detection and redaction

### 12. **Configuration Management**

**Current State:**
- Global settings in `backend/config/settings.py`
- Runtime profiles for intensity
- No per-workspace configuration

**Gap:**
- One-size-fits-all settings
- No customization per workspace
- No feature flags

**Improvement:**
- Per-workspace AI configuration
- Feature flag system
- Dynamic configuration updates
- Configuration validation

### 13. **Multi-Model Support**

**Current State:**
- Primarily Gemini (Vertex AI)
- Backend abstraction exists but limited usage
- Model failover only for Gemini variants

**Gap:**
- Vendor lock-in
- Cannot use specialized models
- No model routing

**Improvement:**
- OpenAI GPT support
- Anthropic Claude support
- Model routing based on task type
- Cost/quality tradeoff selection

### 14. **Checkpoint & Recovery**

**Current State:**
- No checkpointing in LangGraph
- State not persisted between calls
- Cannot resume interrupted workflows

**Gap:**
- Lost state on restart
- Cannot debug long workflows
- No recovery mechanism

**Improvement:**
- LangGraph checkpointing with Postgres
- State persistence between nodes
- Recovery from interrupted workflows
- Workflow replay for debugging

### 15. **Batch Processing**

**Current State:**
- Single generation per request
- No batch endpoint
- Sequential processing only

**Gap:**
- Inefficient for bulk operations
- Higher costs due to per-request overhead
- Slower for batch content generation

**Improvement:**
- Batch generation endpoint
- Parallel processing within requests
- Bulk import/export for content
- Queue-based batch jobs

---

## Priority Matrix

### Critical (High Impact, Low Effort)
1. **Observability & Monitoring** - Add tracing and metrics
2. **Caching Layer** - Implement semantic and exact-match caching
3. **Rate Limiting & Quotas** - Per-workspace limits
4. **Retry & Circuit Breaker** - Improve reliability

### High (High Impact, Medium Effort)
5. **Streaming Support** - Better UX for generations
6. **Tool Use & Function Calling** - Enhanced agent capabilities
7. **Advanced Memory Management** - Conversation threading
8. **Prompt Versioning** - Safer iteration

### Medium (Medium Impact, Medium Effort)
9. **Async Task Queue** - Guaranteed execution
10. **Multi-Model Support** - Vendor flexibility
11. **Evaluation Framework** - Quality measurement
12. **Configuration Management** - Per-workspace settings

### Lower Priority (High Effort or Lower Impact)
13. **Security & Safety** - Important but requires careful design
14. **Checkpoint & Recovery** - Nice to have for complex workflows
15. **Batch Processing** - Optimization for scale

---

## Architecture Recommendations

### Recommended Architecture Changes

1. **Add Observability Layer**
   - Instrument all LangGraph nodes with OpenTelemetry
   - Export to Prometheus/Grafana
   - Create execution dashboards

2. **Implement Caching Strategy**
   - Redis-based semantic cache (using embeddings)
   - In-memory exact-match cache for hot queries
   - Cache invalidation based on workspace updates

3. **Add Streaming Infrastructure**
   - SSE endpoints in FastAPI
   - Async generators in backends
   - Frontend streaming support

4. **Enhance Memory System**
   - Redis-backed conversation store
   - Context window management service
   - Memory compression for long contexts

5. **Build Tool Framework**
   - ToolNode integration in LangGraph
   - Tool registry with JSON Schema validation
   - Parallel tool execution

6. **Add Guardrails**
   - Prompt injection detection (using heuristics + LLM)
   - Output moderation (Perspective API or similar)
   - PII detection and redaction

7. **Implement Checkpointing**
   - Postgres checkpointer for LangGraph
   - State recovery on restart
   - Workflow debugging capabilities

---

## Implementation Phases

### Phase 1: Foundation (Weeks 1-2)
- Observability & monitoring
- Caching layer
- Enhanced rate limiting

### Phase 2: UX & Reliability (Weeks 3-4)
- Streaming support
- Retry & circuit breaker
- Async task queue

### Phase 3: Capabilities (Weeks 5-6)
- Tool use & function calling
- Advanced memory management
- Prompt versioning

### Phase 4: Scale & Quality (Weeks 7-8)
- Multi-model support
- Evaluation framework
- Batch processing

### Phase 5: Polish (Weeks 9-10)
- Security & safety
- Configuration management
- Checkpoint & recovery

---

## Key Files for Implementation

**Core AI System:**
- `backend/agents/muse/orchestrator.py` - Main orchestrator
- `backend/agents/runtime/profiles.py` - Execution profiles
- `backend/ai/backends/vertex_ai.py` - Primary backend
- `backend/ai/prompts/__init__.py` - Prompt compilation
- `backend/services/bcm/` - Business Context Memory

**Integration Points:**
- `backend/api/v1/muse/routes.py` - Muse API
- `backend/api/v1/context/routes.py` - Context API
- `backend/api/v1/campaigns/routes.py` - Campaigns API
- `backend/services/muse_service.py` - Service layer

**Configuration:**
- `backend/config/settings.py` - Global settings
- `backend/requirements.txt` - Dependencies

**Tests:**
- `backend/tests/unit/test_langgraph_*.py` - Orchestrator tests
- `backend/tests/characterization/` - API contract tests

---

## Research Notes

### LangGraph Production Best Practices (from research)

1. **State Management**
   - Use TypedDict for state (✅ Already doing this)
   - Keep state serializable for checkpointing
   - Minimize state size for performance

2. **Error Handling**
   - Use try/except in node functions
   - Return error states, don't raise (for graph continuity)
   - Implement fallback nodes

3. **Async Patterns**
   - Use `ainvoke()` for async execution (✅ Already doing this)
   - Avoid blocking I/O in nodes
   - Use asyncio.gather for parallel operations (✅ Already doing this in council/swarm)

4. **Testing**
   - Mock external dependencies (✅ Already doing this)
   - Test graph structure separately from node logic
   - Use snapshot testing for state transitions

5. **Observability**
   - Instrument each node with timing
   - Log state transitions
   - Track token usage per node

6. **Deployment**
   - Use Postgres checkpointer for state persistence
   - Implement health checks
   - Graceful shutdown handling

### Production AI System Patterns (from research)

1. **Multi-Agent Patterns**
   - Router pattern (✅ Already using this)
   - Ensemble/council pattern (✅ Already using this)
   - Hierarchical teams
   - Parallel specialist pattern (✅ Already using this in swarm)

2. **Memory Patterns**
   - Vector store for semantic memory
   - Key-value for episodic memory
   - Summary memory for long contexts
   - Working memory for current task

3. **Tool Use**
   - ToolNode in LangGraph
   - JSON Schema validation
   - Parallel tool execution
   - Tool result caching

4. **Reliability**
   - Circuit breakers for external services
   - Exponential backoff with jitter
   - Dead letter queues
   - Graceful degradation

---

## Summary

The current RaptorFlow AI system has a **solid foundation** with:
- Clean architecture and separation of concerns
- Multi-mode execution (single/council/swarm)
- Good abstraction layers
- Business context integration
- Basic error handling and fallbacks

**Key improvement areas** are:
1. **Observability** - Need tracing, metrics, dashboards
2. **Caching** - No current caching, high opportunity for cost savings
3. **Streaming** - Synchronous only, poor UX for long generations
4. **Tool Use** - No external tool integration
5. **Memory** - Basic memory, no conversation threading
6. **Rate Limiting** - Global only, no per-workspace limits

The architecture is well-positioned for these enhancements, with clear integration points and modular design.

---

## Next Steps

1. Create detailed work plan with specific TODOs
2. Prioritize Phase 1 improvements (observability, caching, rate limiting)
3. Get approval on approach and priorities
4. Begin implementation with Sisyphus

---

*Draft created: 2026-02-15*
*Status: Ready for review and plan generation*
