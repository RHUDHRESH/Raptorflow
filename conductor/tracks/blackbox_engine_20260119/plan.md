# Implementation Plan: Blackbox Strategy Engine Resurrection

This plan outlines the steps to fully integrate the Blackbox frontend with the backend AI engine, ensuring experimental and high-risk strategies are correctly generated, stored, and converted into actionable moves.

## Phase 1: API & Database Validation
Focuses on ensuring the communication path and data storage for Blackbox strategies are robust.

- [~] Task: Verify and update Supabase schema for `blackbox_strategies` and `strategy_reviews` tables.
- [ ] Task: Ensure RLS policies for `blackbox_strategies` allow users to see and create their own strategies.
- [ ] Task: Implement/Refine `POST /api/v1/blackbox/generate` endpoint to accept focus area and volatility.
- [ ] Task: Create unit tests for Blackbox API endpoints (Red Phase).
- [ ] Task: Conductor - User Manual Verification 'Phase 1: API & Database Validation' (Protocol in workflow.md)

## Phase 2: Cognitive Engine & Agent Alignment
Refines the `BlackboxStrategist` agent to truly deliver "experimental and risky" moves based on user input.

- [ ] Task: Update `BlackboxStrategist` system prompt to better handle the 1-10 "Volatility" scale.
- [ ] Task: Implement logic in `BlackboxWorkflow` to inject real workspace context (Foundations, ICPs) into the generation prompt.
- [ ] Task: Write failing tests for the `BlackboxWorkflow` to verify context-aware generation (Red Phase).
- [ ] Task: Implement the "Volatility" logic in the agent to vary the temperature and unconventionality of responses.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Cognitive Engine & Agent Alignment' (Protocol in workflow.md)

## Phase 3: Frontend Integration
Connects the React UI to the real backend service and handles the state transitions.

- [ ] Task: Update `useMovesStore` to support asynchronous `createMoveFromBlackBox` with real API calls.
- [ ] Task: Modify `frontend/src/app/(shell)/blackbox/page.tsx` to replace `setTimeout` with a call to `POST /api/v1/blackbox/generate`.
- [ ] Task: Implement real-time status updates in the "Processing" step (Analyzing -> Calculating -> Optimizing).
- [ ] Task: Map backend strategy output fields to the frontend "Output" display.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Frontend Integration' (Protocol in workflow.md)

## Phase 4: Move Conversion & Polish
Ensures the final step of creating a move from a strategy works seamlessly.

- [ ] Task: Implement the "Accept & Create Move" backend logic to correctly populate the `moves` table from a Blackbox strategy record.
- [ ] Task: Verify move relationships (sequence) are created if a strategy involves multiple steps.
- [ ] Task: Add error handling and toast notifications for failed strategy generations.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Move Conversion & Polish' (Protocol in workflow.md)
