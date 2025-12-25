# Implementation Plan - SOTA Economical Swarm Architecture

This plan implements a multi-agent swarm architecture with shared memory, persistent learning, and strict cost governance, following the "Quiet Luxury" design philosophy.

## Phase 1: Foundation & Shared State (L1)
*Focus: Setting up the underlying infrastructure for inter-agent communication.*

- [~] **Task 1.1: Implement Shared State Schema**
    - Write tests for a thread-safe `SwarmState` using LangGraph `TypedDict` and Redis.
    - Implement `SwarmState` to handle cross-agent message passing and shared context.
- [ ] **Task 1.2: Upstash Redis Shared Memory Adapter**
    - Write tests for L1 volatile memory storage/retrieval.
    - Implement a Redis-backed `L1MemoryManager` for real-time inter-agent state sync.
- [ ] **Task: Conductor - User Manual Verification 'Phase 1: Foundation & Shared State (L1)' (Protocol in workflow.md)**

## Phase 2: Swarm Orchestration (Supervisor & Delegation)
*Focus: Building the central intelligence that manages the swarm.*

- [ ] **Task 2.1: Supervisor Agent Node**
    - Write tests for task decomposition logic (Complex Prompt -> Sub-tasks).
    - Implement `SwarmSupervisor` using `MODEL_REASONING_ULTRA`.
- [ ] **Task 2.2: Delegation Router**
    - Write tests for routing sub-tasks to correct specialist types based on intent.
    - Implement a dynamic router that handles `__call__` handoffs to specialists.
- [ ] **Task: Conductor - User Manual Verification 'Phase 2: Swarm Orchestration (Supervisor & Delegation)' (Protocol in workflow.md)**

## Phase 3: Specialist Registry & Toolbelt Integration
*Focus: Implementing the core workforce of the swarm.*

- [ ] **Task 3.1: Base Swarm Specialist Class**
    - Write tests for a lightweight, fast specialist base class.
    - Implement `BaseSwarmSpecialist` with forced `MODEL_GENERAL` (Nano/Fast) tiering.
- [ ] **Task 3.2: Implement Core Specialists (Researcher, Architect, Quality)**
    - Implement `ResearcherAgent`, `ArchitectAgent`, and `QualityCriticAgent` with Toolbelt access.
- [ ] **Task 3.3: Memory Manager Agent**
    - Write tests for automated context summarization (preventing context window bloat).
    - Implement `ContextMemoryManager` to prune and summarize L1 Redis state.
- [ ] **Task: Conductor - User Manual Verification 'Phase 3: Specialist Registry & Toolbelt Integration' (Protocol in workflow.md)**

## Phase 4: Economy & Governance
*Focus: Enforcing the "Economical" mandate.*

- [ ] **Task 4.1: Enhanced Cost Governor**
    - Write tests for budget auditing and delegation blocking.
    - Upgrade `CostGovernor` to intercept inter-agent calls and validate against `MONTHLY_IMAGE_QUOTA` and token budgets.
- [ ] **Task 4.2: Hard Token Budgeting Hook**
    - Implement a LangGraph `interrupt` or middleware that halts the swarm if the run cost exceeds a threshold.
- [ ] **Task: Conductor - User Manual Verification 'Phase 4: Economy & Governance' (Protocol in workflow.md)**

## Phase 5: Persistent Learning Flywheel (L2/L3)
*Focus: Enabling the system to learn from every run.*

- [ ] **Task 5.1: Automated Retrospective Node**
    - Write tests for extraction of 'Learned Patterns' from execution traces.
    - Implement `RetrospectiveNode` to summarize runs and store findings in Supabase pgvector.
- [ ] **Task 5.2: Knowledge Graph Integration**
    - Write tests for cross-agent fact contribution.
    - Implement a shared `KnowledgeGraphConnector` for L3 semantic memory.
- [ ] **Task 5.3: RLHF Preference Loop**
    - Implement logic to convert human approval/critique from `approve_assets` into long-term brand preferences.
- [ ] **Task: Conductor - User Manual Verification 'Phase 5: Persistent Learning Flywheel (L2/L3)' (Protocol in workflow.md)**

## Phase 6: Integration & Final Validation
*Focus: End-to-end swarm execution and quality gates.*

- [ ] **Task 6.1: End-to-End Swarm Test Suite**
    - Write integration tests for a multi-step marketing task (Research -> Strategy -> Asset Gen -> Critique).
    - Verify that costs are <50% of a monolithic model run.
- [ ] **Task 6.2: Final Audit & Performance Tuning**
    - Optimize inter-agent latency and ensure >80% code coverage.
- [ ] **Task: Conductor - User Manual Verification 'Phase 6: Integration & Final Validation' (Protocol in workflow.md)**
