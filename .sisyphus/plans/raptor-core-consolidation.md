# RaptorCore Consolidation Plan

## TL;DR

> **Objective**: Consolidate all fragmented AI components in RaptorFlow into a single, self-improving hierarchical meta-brain called RaptorCore (internal) / Raptor Prime (UI branding).
> 
> **Current State**: 9+ distinct AI surfaces scattered across backend/ai/, backend/agents/, and backend/bcm/ - each with different memory slices, tool access, prompt sets, and entry points.
> 
> **Target State**: ONE unified entry point (`RaptorCore.execute()`) with BCM as root context, shared memory, hierarchical LangGraph supervisor, and pluggable specialists.
> 
> **Estimated Effort**: XL (significant architectural change)
> **Parallel Execution**: YES - multiple phases can run in parallel
> **Critical Path**: Phase 0 Analysis → Phase 1 Core → Phase 2 Migration → Phase 3 Integration

---

## Context

### Current Repository Analysis (as of Feb 20, 2026)

**AI Entry Points Identified**:
| Component | Location | Purpose | Entry Point |
|-----------|----------|---------|-------------|
| AIClient | `backend/ai/client.py` | Primary AI interface | `get_client().generate()` |
| generate_with_manifest | `backend/ai/client.py:189` | BCM-aware generation | `client.generate_with_manifest()` |
| LangGraph Muse | `backend/agents/muse/orchestrator.py` | Creative generation | `langgraph_muse_orchestrator.invoke()` |
| Campaign Moves | `backend/agents/campaign_moves/` | Strategic execution | TBD |
| SingleStrategy | `backend/ai/orchestration/strategies/__init__.py` | Single model | `get_strategy(ExecutionMode.SINGLE)` |
| CouncilStrategy | `backend/ai/orchestration/strategies/__init__.py` | Multi-agent debate | `get_strategy(ExecutionMode.COUNCIL)` |
| SwarmStrategy | `backend/ai/orchestration/strategies/__init__.py` | Parallel specialists | `get_strategy(ExecutionMode.SWARM)` |
| BCM System | `backend/bcm/core/types.py` | Business Context | `BCMManifest` class |
| Backends | `backend/ai/backends/` | LLM providers | VertexAI, GenAI, Deterministic |

**Fragmentation Issues Identified**:
1. **Memory Isolation**: AIClient has loose `memories: list`, BCM has `memories_delta`, Muse has separate memory access
2. **No Central Supervisor**: No unified brain that coordinates all agents
3. **Duplicate Orchestration**: Muse has its own LangGraph, strategies have separate execution
4. **BCM Scattered**: `generate_with_manifest` is optional - most calls use plain `generate()`
5. **Missing Research Agent**: User mentioned `research_agent` but not found in current codebase

---

## Work Objectives

### Core Objective
Create RaptorCore - a unified AI meta-brain that:
1. Replaces ALL fragmented AI entry points with ONE entry point
2. Uses BCM as the immutable root context for EVERY decision
3. Provides hierarchical LangGraph supervision with pluggable specialists
4. Implements shared memory across all agents
5. Maintains full backward compatibility for 60 days

### Concrete Deliverables
- `backend/ai/core/` - New consolidated AI core directory
- `backend/ai/core/raptor_core.py` - Singleton with `execute()` entry point
- `backend/ai/core/supervisor_graph.py` - Hierarchical LangGraph supervisor
- `backend/ai/core/shared_memory.py` - Unified memory layer
- `backend/ai/core/bcm_keeper.py` - BCM load/validate/version/inject
- `backend/ai/core/tool_registry.py` - Unified tool registry
- `backend/ai/core/reflection_loop.py` - Self-improvement mechanism
- `backend/ai/core/guardrails.py` - Budget, safety, workspace isolation
- `backend/ai/core/specialists/` - Specialist sub-agents

### Definition of Done
- [ ] All AI calls route through `RaptorCore.execute()` - verified via code search
- [ ] BCM is loaded once per workspace, injected into every prompt
- [ ] Shared memory accessible by all specialists
- [ ] Backward compatible API returns identical GenerationResult shape
- [ ] All existing tests pass without modification (60-day shim)
- [ ] Production HA works with 3-replica Docker + Redis sentinel

### Must Have
- Zero breaking changes to frontend, middleware, Supabase
- Full test coverage with 12+ test cases
- Self-improvement via reflection loop

### Must NOT Have
- No new external runtime dependencies (except LangGraph)
- No deletion of existing files (deprecate with comments)
- No PII in logs

---

## Verification Strategy

### Test Decision
- **Infrastructure exists**: YES (pytest in backend/)
- **Automated tests**: Recommend TDD for core components
- **Framework**: pytest (existing)

### Agent-Executed QA Scenarios

**Scenario: Verify all AI routes through RaptorCore**
  Tool: Bash
  Preconditions: Code changes applied
  Steps:
    1. Search for all `generate(` calls in codebase
    2. Verify each calls RaptorCore or goes through proxy
    3. List any remaining direct backend calls
  Expected Result: Zero direct AI calls outside RaptorCore
  Evidence: Code search results

**Scenario: BCM injected in every prompt**
  Tool: Code inspection
  Preconditions: RaptorCore implemented
  Steps:
    1. Read supervisor_graph.py system prompt construction
    2. Verify BCM is first token in every prompt
    3. Check specialist calls include BCM context
  Expected Result: BCM appears in all prompt construction paths
  Evidence: Code inspection report

**Scenario: Shared memory accessible**
  Tool: Integration test
  Preconditions: shared_memory.py implemented
  Steps:
    1. Create memory chunk from one specialist
    2. Query from another specialist
    3. Verify cross-specialist memory sharing
  Expected Result: Memory accessible across specialists
  Evidence: Test output

---

## Execution Strategy

### Phase 0: Analysis & Mapping (Week 1)

**Tasks**:
- [ ] 0.1 Map every AI call site across the codebase
- [ ] 0.2 Identify all duplicated concepts (memory, tools, budgets, prompts)
- [ ] 0.3 Document current BCM usage patterns
- [ ] 0.4 Identify research_agent location or confirm separate repo

**Parallelization**: All tasks in this phase are independent - run in parallel

### Phase 1: Core Implementation (Weeks 2-4)

**Wave 1 (Week 2)**:
- [ ] 1.1 Create `backend/ai/core/` directory structure
- [ ] 1.2 Implement `bcm_keeper.py` - BCM load/validate/version
- [ ] 1.3 Implement `shared_memory.py` - Redis + vector + BCM wrapper

**Wave 2 (Week 3)**:
- [ ] 1.4 Implement `raptor_core.py` - Singleton with execute()
- [ ] 1.5 Implement `guardrails.py` - Budget enforcement, workspace isolation
- [ ] 1.6 Implement `tool_registry.py` - Unified tool registry

**Wave 3 (Week 4)**:
- [ ] 1.7 Implement `supervisor_graph.py` - Hierarchical LangGraph
- [ ] 1.8 Implement `reflection_loop.py` - Self-improvement
- [ ] 1.9 Create specialists directory and base specialists

### Phase 2: Migration (Weeks 5-6)

**Wave 1 (Week 5)**:
- [ ] 2.1 Modify `backend/ai/client.py` → thin proxy to RaptorCore
- [ ] 2.2 Add RAPTORCORE_* settings to `backend/config/settings.py`
- [ ] 2.3 Add RaptorCore initialization to `backend/app_factory.py`

**Wave 2 (Week 6)**:
- [ ] 2.4 Migrate Muse orchestrator to specialist
- [ ] 2.5 Migrate Campaign Moves to specialist
- [ ] 2.6 Implement 60-day backward compatibility shim
- [ ] 2.7 Update all routers to delegate to core

### Phase 3: Testing & HA (Weeks 7-8)

**Wave 1 (Week 7)**:
- [ ] 3.1 Write test_brain.py with 12+ test cases
- [ ] 3.2 Implement production healthchecks
- [ ] 3.3 Update docker-compose.prod.yml

**Wave 2 (Week 8)**:
- [ ] 3.4 Create verification script
- [ ] 3.5 Run full integration tests
- [ ] 3.6 Deploy to staging for validation

---

## TODOs

### Phase 0: Analysis

- [ ] 0.1 Map every AI call site

  **What to do**:
  - Search codebase for all `generate(`, `generate_with_manifest(`, `invoke(` calls
  - Categorize by entry point type
  - Document each call's context requirements

  **Must NOT do**:
  - Modify any existing code during mapping

  **Recommended Agent Profile**:
  - **Category**: unspecified-low
    - Reason: Straightforward code search task
  - **Skills**: []
  - **Skills Evaluated but Omitted**:
    - N/A - simple search task

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Phase 0 (with 0.2, 0.3, 0.4)
  - **Blocks**: 1.1 (must know all call sites before creating core)
  - **Blocked By**: None

  **References**:
  - `backend/ai/client.py` - Primary AI entry point
  - `backend/agents/muse/orchestrator.py` - Muse invocation
  - `backend/agents/campaign_moves/` - Campaign moves entry

  **Acceptance Criteria**:
  - [ ] Complete list of all AI call sites with file:line references
  - [ ] Each call site categorized by type
  - [ ] Dependencies between call sites mapped

- [ ] 0.2 Identify duplicated concepts

  **What to do**:
  - Find all memory-related code (LongTermMemory, memories list, memories_delta)
  - Find all tool-related code (search, scraping, visual)
  - Find all budget-related code (DAILY_AI_BUDGET, MONTHLY_AI_BUDGET)
  - Find all profile-related code (AIProfile, intensity, execution_mode)

  **Must NOT do**:
  - Make assumptions about functionality

  **Parallelization**:
  - **Can Run In Parallel**: YES
  - **Parallel Group**: Phase 0

  **Acceptance Criteria**:
  - [ ] List of duplicated concepts with locations
  - [ ] Recommendation for each consolidation

- [ ] 0.3 Document BCM usage patterns

  **What to do**:
  - Find all compile_system_prompt calls
  - Find all manifest usage
  - Find all BCM enforcement (ENFORCE_BCM_READY_GATE)

  **References**:
  - `backend/bcm/core/types.py:83-130` - BCMManifest class
  - `backend/ai/client.py:189-237` - generate_with_manifest
  - `backend/ai/prompts/` - prompt compilation

  **Acceptance Criteria**:
  - [ ] Complete BCM flow diagram
  - [ ] All injection points identified

- [ ] 0.4 Identify research_agent location

  **What to do**:
  - Search for ResearchAgent, research_agent, LongTermMemory
  - Check if in separate repo or not yet implemented

  **Acceptance Criteria**:
  - [ ] Research agent location confirmed (or create plan to implement)

### Phase 1: Core Implementation

- [ ] 1.1 Create backend/ai/core/ directory

  **What to do**:
  - Create directory structure
  - Create __init__.py files

  **Acceptance Criteria**:
  - [ ] Directory exists with proper Python package structure

- [ ] 1.2 Implement bcm_keeper.py

  **What to do**:
  - Load BCM from Supabase per workspace
  - Cache in Redis with 1-hour TTL
  - Version management for deltas
  - Inject BCM into prompts

  **References**:
  - `backend/bcm/core/types.py:83` - BCMManifest
  - `backend/config/settings.py:149` - ENFORCE_BCM_READY_GATE

  **Acceptance Criteria**:
  - [ ] BCM loads once per workspace
  - [ ] Redis caching works
  - [ ] Version tracking implemented

- [ ] 1.3 Implement shared_memory.py

  **What to do**:
  - Wrap existing LongTermMemory (from BCM if exists, or create new)
  - Redis episodic memory layer
  - Vector memory layer (PGVector or Chroma)
  - Cross-specialist memory sharing

  **References**:
  - `backend/bcm/memory/` - Existing memory system
  - `backend/ai/client.py:194` - memories parameter

  **Acceptance Criteria**:
  - [ ] Long-term memory preserved
  - [ ] Episodic memory works
  - [ ] Cross-specialist sharing verified

- [ ] 1.4 Implement raptor_core.py

  **What to do**:
  - Singleton pattern get_raptor_core()
  - execute(request: BrainRequest) → BrainResponse
  - initialize() method

  **References**:
  - `backend/ai/client.py:30` - AIClient pattern
  - `backend/ai/types.py:42-83` - GenerationRequest/Result

  **Acceptance Criteria**:
  - [ ] Singleton works correctly
  - [ ] execute() returns BrainResponse
  - [ ] initialize() sets up all components

- [ ] 1.5 Implement guardrails.py

  **What to do**:
  - Budget enforcement (DAILY_AI_BUDGET, MONTHLY_AI_BUDGET)
  - PII filter
  - Workspace isolation
  - Onboarding gate (ENFORCE_BCM_READY_GATE)

  **References**:
  - `backend/config/settings.py:107-109` - Budget settings
  - `backend/config/settings.py:149` - ENFORCE_BCM_READY_GATE

  **Acceptance Criteria**:
  - [ ] Budget checked before every call
  - [ ] Workspace isolation enforced
  - [ ] Onboarding gate works

- [ ] 1.6 Implement tool_registry.py

  **What to do**:
  - Unified registry for all tools
  - Wrap existing tools (search, scraping, visual)
  - Research agent as tool (when available)
  - Budget/guardrails integration

  **References**:
  - `backend/ai/backends/` - Existing backends

  **Acceptance Criteria**:
  - [ ] All existing tools registered
  - [ ] New tools can be added easily

- [ ] 1.7 Implement supervisor_graph.py

  **What to do**:
  - Hierarchical LangGraph supervisor
  - Sub-team spawning
  - Reflection capability
  - BCM + memory as system prompt root

  **References**:
  - `backend/agents/muse/orchestrator.py:138` - LangGraph pattern

  **Acceptance Criteria**:
  - [ ] Supervisor creates sub-teams
  - [ ] BCM is first in system prompt
  - [ ] Reflection triggers correctly

- [ ] 1.8 Implement reflection_loop.py

  **What to do**:
  - Runs every 10 tasks or confidence<70
  - Outputs git-diff style improvements
  - Human approval via UI

  **References**:
  - `backend/bcm/reflection/` - Existing reflection

  **Acceptance Criteria**:
  - [ ] Loop triggers at correct intervals
  - [ ] Outputs valid git diff format
  - [ ] Approval workflow defined

- [ ] 1.9 Create specialists

  **What to do**:
  - research.py - Research specialist (or wrapper)
  - muse.py - Creative specialist (from existing)
  - foundation.py - Foundation locking
  - campaign.py - Campaign execution
  - visual.py - Visual/dnd-kit outputs

  **References**:
  - `backend/agents/muse/orchestrator.py` - Existing Muse
  - `backend/agents/campaign_moves/` - Campaign moves

  **Acceptance Criteria**:
  - [ ] Each specialist is a sub-graph or ReAct agent
  - [ ] All existing functionality preserved
  - [ ] Output structured properly

### Phase 2: Migration

- [ ] 2.1 Modify client.py to proxy

  **What to do**:
  - Make AIClient a thin proxy to RaptorCore
  - Maintain backward compatibility
  - Add deprecation warnings

  **References**:
  - `backend/ai/client.py` - Current implementation

  **Acceptance Criteria**:
  - [ ] Existing code still works
  - [ ] Calls route through RaptorCore
  - [ ] Deprecation warnings appear

- [ ] 2.2 Add RaptorCore settings

  **What to do**:
  - Add RAPTORCORE_* keys to settings
  - FEATURE_FLAG_RAPTORCORE = True

  **References**:
  - `backend/config/settings.py` - Current settings

  **Acceptance Criteria**:
  - [ ] New settings available
  - [ ] Feature flag works

- [ ] 2.3 Update app_factory.py

  **What to do**:
  - Add RaptorCore.initialize() to lifespan
  - Ensure proper startup order

  **References**:
  - `backend/app_factory.py` - Current factory

  **Acceptance Criteria**:
  - [ ] RaptorCore initializes on startup
  - [ ] Proper error handling

- [ ] 2.4-2.7 Migration tasks

  **What to do**:
  - Migrate each existing component to specialist
  - Implement backward compatibility shim
  - Update all routers

  **Acceptance Criteria**:
  - [ ] All components work as specialists
  - [ ] 60-day backward compat maintained

### Phase 3: Testing & HA

- [ ] 3.1 Write test_brain.py

  **What to do**:
  - 12+ test cases covering:
    - Basic execution
    - BCM injection
    - Memory sharing
    - Budget enforcement
    - Error handling
    - Specialist coordination

  **Acceptance Criteria**:
  - [ ] 12 tests minimum
  - [ ] All pass

- [ ] 3.2-3.6 HA and deployment tasks

  **What to do**:
  - Production healthchecks
  - Docker updates
  - Verification script
  - Integration tests

  **Acceptance Criteria**:
  - [ ] Production-ready
  - [ ] All tests pass

---

## Success Criteria

### Verification Commands
```bash
# Find all AI call sites
grep -rn "generate\|invoke\|execute" backend/ai/ backend/agents/ --include="*.py" | grep -v "__pycache__"

# Verify no direct backend calls
grep -rn "backend.generate\|VertexAI\|genai" backend/ai/ --include="*.py" | grep -v "raptor_core\|proxy"

# Run tests
cd backend && pytest tests/test_brain.py -v
```

### Final Checklist
- [ ] All "Must Have" present
- [ ] All "Must NOT Have" absent
- [ ] All existing tests pass
- [ ] Backward compatibility maintained
- [ ] Production HA verified

---

## Notes for RHUDHRESH

1. **Research Agent**: The `research_agent` you mentioned is NOT in the current codebase. Options:
   - It exists in a separate repository (please provide link)
   - It needs to be implemented from scratch
   - The existing Muse orchestrator can serve similar purposes

2. **BCM Already Exists**: The `backend/bcm/` directory already has a solid BCM implementation with `BCMManifest` class. This will be the foundation for RaptorCore's BCM keeper.

3. **Muse is Already LangGraph**: The `LangGraphMuseOrchestrator` in `backend/agents/muse/orchestrator.py` is already using LangGraph. We'll refactor it into the specialist pattern.

4. **Dependencies**: No new runtime dependencies needed - LangGraph is likely already available or can be added to requirements.

5. **Next Steps**: Confirm research_agent location, then begin Phase 0 mapping.
