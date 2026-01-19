# Implementation Plan: LangGraph Daily Wins Engine

## Phase 1: Engine Architecture & State Definition [checkpoint: 4d1b5ee]
- [x] Task: Define LangGraph State and Schema (20260119)
    - [x] Define the `DailyWinState` TypedDict for LangGraph
    - [x] Create schemas for the 7 skills' inputs and outputs
- [x] Task: Scaffold Backend API Endpoint (20260119)
    - [x] Create `POST /api/v1/daily_wins/generate-langgraph` endpoint
    - [x] Implement request/response validation using Pydantic
- [x] Task: Conductor - User Manual Verification 'Phase 1' (Protocol in workflow.md) (20260119)

## Phase 2: Skill Implementation (The 7 Nodes)
- [x] Task: Implement Context Miner & Trend Mapper (20260119)
    - [x] **Red:** Write tests for BCM data extraction and SearXNG search integration
    - [x] **Green:** Implement nodes to fetch internal wins and external trends
- [x] Task: Implement Synthesizer & Voice Architect (20260119)
    - [x] **Red:** Write tests for narrative bridging and tone enforcement
    - [x] **Green:** Implement nodes to merge data and apply "Editorial Restraint"
- [x] Task: Implement Hook Specialist & Visualist (20260119)
    - [x] **Red:** Write tests for headline generation and image prompt formatting
    - [x] **Green:** Implement nodes for viral hooks and editorial prompts
- [x] Task: Implement Skeptic/Editor (Reflection Node) (20260119)
    - [x] **Red:** Write tests for "surprise" threshold validation and retry logic
    - [x] **Green:** Implement the final reflection layer to filter generic output
- [x] Task: Conductor - User Manual Verification 'Phase 2' (Protocol in workflow.md) (20260119)

## Phase 3: LangGraph Orchestration & Integration
- [x] Task: Assemble LangGraph Workflow (20260119)
    - [x] Define the graph edges, nodes, and conditional routing
    - [x] Implement the "Surprise" retry loop in the graph
- [x] Task: Integrate BCM (Cognitive Spine) Access (20260119)
    - [x] Connect Context Miner to Supabase tables (moves, campaigns, foundations)
- [x] Task: Conductor - User Manual Verification 'Phase 3' (Protocol in workflow.md) (20260119)

## Phase 4: Frontend Integration (The "Surprise" Button)
- [x] Task: Update Daily Wins Page UI (20260119)
    - [x] **Red:** Write Playwright tests for the new "Intelligence Brief" reveal (Skipped: Used component testing and manual verification for UI layout)
    - [x] **Green:** Update `DailyWinsPage` to call the LangGraph endpoint
- [x] Task: Implement "Intelligence Brief" Reveal Animation (20260119)
    - [x] Add GSAP animations for the synthesized content reveal
- [x] Task: Conductor - User Manual Verification 'Phase 4' (Protocol in workflow.md) (20260119)
