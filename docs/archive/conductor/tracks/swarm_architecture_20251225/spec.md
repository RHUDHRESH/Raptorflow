# Specification: SOTA Economical Swarm Agentic Architecture

## 1. Overview
The goal of this track is to implement a high-performance, cost-efficient "Swarm" architecture for RaptorFlow. This architecture enables multiple specialized agents to collaborate, share a unified memory space, and evolve their collective intelligence through automated retrospectives and human-in-the-loop feedback. It prioritizes "Quiet Luxury" by being invisible but surgical in its execution.

## 2. Functional Requirements

### 2.1. Swarm Orchestration & Delegation
- **Supervisor-Led Delegation:** Implement a "Supervisor" node (using high-reasoning models) that decomposes complex prompts into sub-tasks.
- **Specialist Registry:** Initialize the swarm with four core specialists:
    - **Researcher:** High-velocity websearch and source extraction.
    - **Architect:** Planning and hierarchical task breakdown.
    - **Quality/Critic:** Auditing outputs and enforcing brand/logic constraints.
    - **Memory Manager:** Summarizing and indexing shared context to prevent bloat.
- **Unified Toolbelt:** All swarm members must have access to the RaptorFlow Toolbelt (Search, Storage, Assets).

### 2.2. Multimodal & Shared Memory
- **Real-time Shared State (L1):** Use Upstash Redis for volatile, high-speed context sharing between active agents in a thread.
- **Persistent Learning Layer (L2/L3):** Use Supabase (PostgreSQL + pgvector) to store "Learned Patterns" and a Cross-Agent Knowledge Graph.
- **Automated Retrospectives:** A post-run node that extracts strategic learnings and saves them to the persistent layer.

### 2.3. Economy & Governance
- **Static Model Tiering:** Force specialists to use "Nano/Fast" models (Gemini 2.5 Flash Image/Lite) while reserving "Ultra/Pro" for the Supervisor.
- **Dynamic Cost Governor:** Upgrade the existing governor to audit delegation requests and block high-cost calls without justification.
- **Hard Token Budgeting:** Implement per-run budget enforcement that halts execution if limits are exceeded.

### 2.4. Human-in-the-Loop (RLHF)
- **Quality Gate Feedback:** Convert human critiques into systemic "Preferences" that are injected into the context of future swarm runs.

## 3. Non-Functional Requirements
- **Latency:** Inter-agent communication in Redis must be <50ms.
- **Resilience:** If a specialist fails, the Supervisor must be able to retry or reassign the task.
- **Security:** Strict workspace isolation for all shared memory and knowledge graph entries.

## 4. Acceptance Criteria
- [ ] A multi-agent LangGraph workflow can successfully delegate a complex marketing task to at least 2 specialists.
- [ ] The "Economical" constraint is proven: total run cost is significantly lower than a single monolithic "Ultra" model run for the same task.
- [ ] Learnings from Run A are successfully retrieved and applied in Run B via the persistent memory layer.
- [ ] Human feedback provided at a checkpoint is correctly persisted as a brand preference.

## 5. Out of Scope
- Automated agent creation (agents must be from the predefined registry).
- Real-time collaborative UI for humans to watch the swarm "chat" (backend implementation only).
