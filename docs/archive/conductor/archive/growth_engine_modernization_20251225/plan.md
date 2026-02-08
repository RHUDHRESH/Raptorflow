# Implementation Plan: Growth Engine Modernization

## Phase 1: Matrix Operator UI & Skill Integration [checkpoint: ffc8771]
Goal: Transform the Matrix dashboard into an actionable operator view.

- [x] Task: Create `OperatorActionsPanel` component in Matrix module. 96e65c3
- [x] Task: Implement `InferenceThrottling` UI (slider/input) and connect to `InferenceThrottlingSkill`. 96e65c3
- [x] Task: Implement `CachePurge` and `ArchiveLogs` one-click triggers. 96e65c3
- [x] Task: Implement `ResourceScaling` and `RetrainTrigger` controls with status feedback. 96e65c3
- [x] Task: Refactor Matrix layout to integrate the new Panel using the "Integrated Management" design. 96e65c3
- [x] Task: Conductor - User Manual Verification 'Phase 1: Matrix Operator UI & Skill Integration' (Protocol in workflow.md) 96e65c3

## Phase 2: Black Box Hypothesis-Driven Engine [checkpoint: 0d184db]
Goal: Revamp the experiment generator to use real marketing heuristics and structured hypotheses.

- [x] Task: Design and implement the new `ExperimentBuilder` form (Hypothesis, Variables, Stats). 0d184db
- [x] Task: Create the `MarketerTemplateLibrary` data structure and UI selection component. 0d184db
- [x] Task: Integrate `BlackboxService` ROI and win-rate analytics into the experiment detail view. 0d184db
- [x] Task: Update the experiment creation flow to prioritize the builder over random generation. 0d184db
- [x] Task: Conductor - User Manual Verification 'Phase 2: Black Box Hypothesis-Driven Engine' (Protocol in workflow.md) 0d184db
## Phase 3: Campaign Wizard Refactor & Interactive Previews [checkpoint: 0d184db]
Goal: Redesign the Campaign wizard for transparency and human-in-the-loop control.

- [x] Task: Deconstruct `NewCampaignWizard` into a multi-step component (Objective -> ICP -> Messaging -> Channels). 0d184db
- [x] Task: Implement the side-by-side `ArcPreview` (Gantt-style) that updates dynamically. 0d184db
- [x] Task: Integrate LangGraph interrupt points in the frontend for human-in-the-loop approvals. 0d184db
- [x] Task: Implement the "Review & Refine" final step for campaign and move approval. 0d184db
- [x] Task: Conductor - User Manual Verification 'Phase 3: Campaign Wizard Refactor & Interactive Previews' (Protocol in workflow.md) 0d184db

## Phase 4: Polish & Growth Hooks [checkpoint: 02aca44]
Goal: Ensure the new features align with the "Quiet Luxury" design and incorporate engagement triggers.

- [x] Task: Audit all new components for "Quiet Luxury" adherence (typography, spacing, borders). 02aca44
- [x] Task: Implement asynchronous status feedback for orchestrator tasks using `get_arc_generation_status`. 02aca44
- [x] Task: Add progress streaks and variable reward notifications for completed experiments/moves. 02aca44
- [x] Task: Conductor - User Manual Verification 'Phase 4: Polish & Growth Hooks' (Protocol in workflow.md) 02aca44

## Track Finalization [checkpoint: 53426e1]
- [x] Task: Synchronize Supabase schema with hypothesis-driven fields. 53426e1
- [x] Task: Update project documentation (product.md). 53426e1
