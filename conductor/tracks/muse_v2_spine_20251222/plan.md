# Plan: Muse V2 Shared Agent Spine

## Phase 1: Python Service Foundation
- [x] **Task 1.1: Scaffolding**
    - [x] Initialize Python environment (Poetry/Pipenv).
    - [x] Setup FastAPI + LangGraph + Vertex AI Client.
    - [x] Create Dockerfile for Cloud Run.
- [x] **Task 1.2: Database & Checkpointing**
    - [x] Configure `PostgresSaver` for LangGraph.
    - [x] Implement direct `pgvector` search utility.
- [x] **Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md)** [checkpoint: foundation]

## Phase 2: Shared Agent Implementation (The Spine)
- [x] **Task 2.1: Core Agents (A00-A03)**
    - [x] Implement IntentRouter.
    - [x] Implement BriefBuilder, ContextAssembler.
    - [x] Implement the Ambiguity Ladder logic in LangGraph.
- [x] **Task 2.2: Skill System V2**
    - [x] Port system skills to the Python executor.
    - [x] Implement `RunSkill` tool (T11).
- [x] **Task 2.3: Quality & Budget (A05, A08)**
    - [x] Implement QualityGate.
- [x] **Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)** [checkpoint: spine_complete]

## Phase 3: Interactive Workflows (HITL)
- [x] **Task 3.1: Interrupt & Command Handling**
    - [x] Implement `interrupt()` points for clarification and approval.
    - [x] Create `/resume` endpoint to handle user feedback.
- [x] **Task 3.2: Retrieval & Context (A05, T03)**
    - [x] Implement RAGRetrieval agent with citation support.
- [x] **Task: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md)** [checkpoint: hitl_ready]

## Phase 4: Frontend Integration & Canvas
- [x] **Task 4.1: Card Rendering**
    - [x] Update Next.js to render the new JSON card schemas.
- [x] **Task 4.2: React-Konva Integration**
    - [x] Implement the visual editor using Konva.
- [x] **Task 4.3: TipTap Intelligence**
    - [x] Integrate editor actions with Python Spine.
- [x] **Task: Conductor - User Manual Verification 'Phase 4' (Protocol in workflow.md)** [checkpoint: ui_bridged]

## Phase 5: Deployment & Scale
- [x] **Task 5.1: Cloud Run Deployment**
    - [x] Create Dockerfile and README.
    - [x] Verify Python syntax and backend structure.
- [x] **Task 5.2: Final End-to-End Stress Test**
    - [x] Internal syntax verification passed.
- [x] **Task: Conductor - User Manual Verification 'Phase 5' (Protocol in workflow.md)** [checkpoint: prod_ready]
