# Implementation Plan: Growth Engine Modernization

## Phase 1: Matrix Operator UI & Skill Integration
Goal: Transform the Matrix dashboard into an actionable operator view.

- [~] Task: Create `OperatorActionsPanel` component in Matrix module.
- [ ] Task: Implement `InferenceThrottling` UI (slider/input) and connect to `InferenceThrottlingSkill`.
- [ ] Task: Implement `CachePurge` and `ArchiveLogs` one-click triggers.
- [ ] Task: Implement `ResourceScaling` and `RetrainTrigger` controls with status feedback.
- [ ] Task: Refactor Matrix layout to integrate the new Panel using the "Integrated Management" design.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Matrix Operator UI & Skill Integration' (Protocol in workflow.md)

## Phase 2: Black Box Hypothesis-Driven Engine
Goal: Revamp the experiment generator to use real marketing heuristics and structured hypotheses.

- [ ] Task: Design and implement the new `ExperimentBuilder` form (Hypothesis, Variables, Stats).
- [ ] Task: Create the `MarketerTemplateLibrary` data structure and UI selection component.
- [ ] Task: Integrate `BlackboxService` ROI and win-rate analytics into the experiment detail view.
- [ ] Task: Update the experiment creation flow to prioritize the builder over random generation.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Black Box Hypothesis-Driven Engine' (Protocol in workflow.md)

## Phase 3: Campaign Wizard Refactor & Interactive Previews
Goal: Redesign the Campaign wizard for transparency and human-in-the-loop control.

- [ ] Task: Deconstruct `NewCampaignWizard` into a multi-step component (Objective -> ICP -> Messaging -> Channels).
- [ ] Task: Implement the side-by-side `ArcPreview` (Gantt-style) that updates dynamically.
- [ ] Task: Integrate LangGraph interrupt points in the frontend for human-in-the-loop approvals.
- [ ] Task: Implement the "Review & Refine" final step for campaign and move approval.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Campaign Wizard Refactor & Interactive Previews' (Protocol in workflow.md)

## Phase 4: Polish & Growth Hooks
Goal: Ensure the new features align with the "Quiet Luxury" design and incorporate engagement triggers.

- [ ] Task: Audit all new components for "Quiet Luxury" adherence (typography, spacing, borders).
- [ ] Task: Implement asynchronous status feedback for orchestrator tasks using `get_arc_generation_status`.
- [ ] Task: Add progress streaks and variable reward notifications for completed experiments/moves.
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Polish & Growth Hooks' (Protocol in workflow.md)
