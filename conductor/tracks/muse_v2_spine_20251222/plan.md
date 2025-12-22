# Plan: Muse V2 Shared Agent Spine

## Phase 1: Python Service Foundation
- [ ] **Task 1.1: Scaffolding**
    - [ ] Initialize Python environment (Poetry/Pipenv).
    - [ ] Setup FastAPI + LangGraph + Vertex AI Client.
    - [ ] Create Dockerfile for Cloud Run.
- [ ] **Task 1.2: Database & Checkpointing**
    - [ ] Configure `PostgresSaver` for LangGraph.
    - [ ] Implement direct `pgvector` search utility.
- [ ] **Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)**

## Phase 2: Shared Agent Implementation (The Spine)
- [ ] **Task 2.1: Core Agents (A00-A03)**
    - [ ] Implement IntentRouter, BriefBuilder, ContextAssembler.
    - [ ] Implement the Ambiguity Ladder logic.
- [ ] **Task 2.2: Skill System V2**
    - [ ] Port system skills to the Python executor.
    - [ ] Implement `RunSkill` tool (T11).
- [ ] **Task 2.3: Quality & Budget (A05, A08)**
    - [ ] Implement BrandLint and CostGovernor.
- [ ] **Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)**

## Phase 3: Interactive Workflows (HITL)
- [ ] **Task 3.1: Interrupt & Command Handling**
    - [ ] Implement `interrupt()` points for clarification and approval.
    - [ ] Create `/resume` endpoint to handle user feedback.
- [ ] **Task 3.2: Retrieval & Context (A05, T03)**
    - [ ] Implement RAGRetrieval agent with citation support.
- [ ] **Task: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md)**

## Phase 4: Frontend Integration & Canvas
- [ ] **Task 4.1: Card Rendering**
    - [ ] Update Next.js to render the new JSON card schemas.
- [ ] **Task 4.2: React-Konva Integration**
    - [ ] Implement the visual editor using Konva.
    - [ ] Bind MemeDirector (M3) output to the canvas state.
- [ ] **Task 4.3: TipTap Intelligence**
    - [ ] Bind editor actions (Improve/Shorten) to Python Toolbelt.
- [ ] **Task: Conductor - User Manual Verification 'Phase 4' (Protocol in workflow.md)**

## Phase 5: Deployment & Scale
- [ ] **Task 5.1: Cloud Run Deployment**
    - [ ] Deploy service to GCP.
    - [ ] Configure IAP/Auth between Next.js and Python.
- [ ] **Task 5.2: Final End-to-End Stress Test**
- [ ] **Task: Conductor - User Manual Verification 'Phase 5' (Protocol in workflow.md)**
