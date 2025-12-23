# Implementation Plan: SOTA Muse Backend

This plan outlines the steps to upgrade the Muse backend to a production-grade, SOTA system using LangGraph, Supabase, and Upstash.

## Phase 1: Core Infrastructure & Persistence
*Goal: Establish the robust base for stateful agentic flows.*

- [x] **Task: Infrastructure - Setup Supabase pgvector and Checkpointer**
  - Initialize Supabase migrations for `checkpoints` and `embeddings` tables.
  - Implement `SupabaseSaver` (LangGraph checkpointer) to persist graph state.
- [x] **Task: Infrastructure - Integrate Upstash Redis for Caching**
  - Set up Upstash connection and implement a global caching layer for tool outputs and research results.
- [x] **Task: Conductor - User Manual Verification 'Phase 1: Core Infrastructure' (Protocol in workflow.md)**

## Phase 2: Memory & Context Engine
*Goal: Implement long-term learning and efficient context management.*

- [x] **Task: Memory - Implement Episodic & Semantic Memory**
  - Write tests for memory retrieval based on "event" vs "fact" types.
  - Implement logic to store and query brand-specific facts (Semantic) and past interactions (Episodic) in Supabase.
- [x] **Task: Memory - Recursive Summarization System**
  - Write tests for processing large text blobs (>10k words).
  - Implement a sliding-window summarization loop to condense research data for the LLM context window.
- [x] **Task: Conductor - User Manual Verification 'Phase 2: Memory & Context Engine' (Protocol in workflow.md)**

## Phase 3: Cognitive Spine & Dynamic Re-planning
*Goal: Enhance the LangGraph architecture for autonomy and reliability.*

- [x] **Task: Logic - Dynamic Re-planning Nodes**
  - Write tests for a graph that pivots its path based on a "search_failure" or "new_insight" signal.
  - Implement the "Planning" node that updates the internal state's `next_steps` dynamically.
- [x] **Task: Logic - Human-in-the-loop (HITL) Interupts**
  - Implement LangGraph `interrupt_before` for high-stakes nodes (e.g., `finalize_positioning`).
  - Create an API endpoint/hook for the UI to "resume" the graph after approval.
- [x] **Task: Conductor - User Manual Verification 'Phase 3: Cognitive Spine' (Protocol in workflow.md)**

## Phase 4: Operational Excellence & Observability
*Goal: Optimize for speed, cost, and traceability.*

- [x] **Task: Optimization - Parallel Execution & Model Routing**
  - Refactor the graph to run Specialist nodes in parallel.
  - Implement routing logic to use Gemini Flash for "cheap" tasks and Pro/o1 for "reasoning" tasks.
- [~] **Task: Monitoring - LangSmith Integration & Performance Audit**
  - Configure LangSmith tracing for all production flows.
  - Verify that latency and cost metrics are being captured for every run.
- [ ] **Task: Conductor - User Manual Verification 'Phase 4: Operational Excellence' (Protocol in workflow.md)**

## Phase 5: Payment Gateway Integration (PhonePe)
*Goal: Enable financial transactions for marketing execution.*

- [ ] **Task: Payments - Implement PhonePe SDK & Webhook Handler**
  - Write tests for secure signature verification and status polling.
  - Implement API endpoints for initiating payments and receiving asynchronous status updates.
- [ ] **Task: Payments - Integrate Payment Gates into LangGraph**
  - Implement an "Execution Guard" node that pauses the graph until a `PAYMENT_SUCCESS` event is received.
- [ ] **Task: Conductor - User Manual Verification 'Phase 5: Payment Integration' (Protocol in workflow.md)**

## Definition of Done
- All LangGraph nodes have unit tests with >80% coverage.
- State is persisted in Supabase and resumable after manual interrupts.
- Caching effectively reduces external tool latency by >40%.
- LangSmith traces are available for every major graph execution.
