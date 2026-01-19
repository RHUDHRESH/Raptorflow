# Implementation Plan: LangGraph Daily Wins Engine

## Phase 1: Engine Architecture & State Definition
- [x] Task: Define LangGraph State and Schema (20260119)
    - [x] Define the `DailyWinState` TypedDict for LangGraph
    - [x] Create schemas for the 7 skills' inputs and outputs
- [x] Task: Scaffold Backend API Endpoint (20260119)
    - [x] Create `POST /api/v1/daily_wins/generate-langgraph` endpoint
    - [x] Implement request/response validation using Pydantic
- [x] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md) (20260119)

## Phase 2: Skill Implementation (The 7 Nodes)
- [ ] Task: Implement Context Miner & Trend Mapper
    - [ ] **Red:** Write tests for BCM data extraction and SearXNG search integration
    - [ ] **Green:** Implement nodes to fetch internal wins and external trends
- [ ] Task: Implement Synthesizer & Voice Architect
    - [ ] **Red:** Write tests for narrative bridging and tone enforcement
    - [ ] **Green:** Implement nodes to merge data and apply "Editorial Restraint"
- [ ] Task: Implement Hook Specialist & Visualist
    - [ ] **Red:** Write tests for headline generation and image prompt formatting
    - [ ] **Green:** Implement nodes for viral hooks and editorial prompts
- [ ] Task: Implement Skeptic/Editor (Reflection Node)
    - [ ] **Red:** Write tests for "surprise" threshold validation and retry logic
    - [ ] **Green:** Implement the final reflection layer to filter generic output
- [ ] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md)

## Phase 3: LangGraph Orchestration & Integration
- [ ] Task: Assemble LangGraph Workflow
    - [ ] Define the graph edges, nodes, and conditional routing
    - [ ] Implement the "Surprise" retry loop in the graph
- [ ] Task: Integrate BCM (Cognitive Spine) Access
    - [ ] Connect Context Miner to Supabase tables (moves, campaigns, foundations)
- [ ] Task: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md)

## Phase 4: Frontend Integration (The "Surprise" Button)
- [ ] Task: Update Daily Wins Page UI
    - [ ] **Red:** Write Playwright tests for the new "Intelligence Brief" reveal
    - [ ] **Green:** Update `DailyWinsPage` to call the LangGraph endpoint
- [ ] Task: Implement "Intelligence Brief" Reveal Animation
    - [ ] Add GSAP animations for the synthesized content reveal
- [ ] Task: Conductor - User Manual Verification 'Phase 4' (Protocol in workflow.md)
