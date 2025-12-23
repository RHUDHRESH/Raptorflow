# Implementation Plan: Blackbox Backend-Frontend Resonance

This plan integrates the Blackbox industrial engine with the frontend UI, ensuring real data flows from Supabase/Vertex AI into the "expensive and decisive" components.

## Phase 1: Data Foundation & Outcome Integration [checkpoint: 6240d4a]
Goal: Replace mock data in the Evidence Log and Results Strip with real `BlackboxOutcome` data.

- [x] Task: Create Backend API Endpoints for Outcomes and Evidence [1ac1897]
- [x] Task: Write Tests for Outcome Data Fetching (Frontend) [11684d2]
- [x] Task: Implement Outcome Data Fetching and Integration in `EvidenceLog.tsx` and `ResultsStrip.tsx` [8cce2bd]
- [x] Task: Conductor - User Manual Verification 'Data Foundation & Outcome Integration' (Protocol in workflow.md)

## Phase 2: Telemetry & Reasoning Integration [checkpoint: 199433d]
Goal: Hook up the `TelemetryFeed` and `AgentAuditLog` to live backend execution traces.

- [x] Task: Create API Endpoint for `BlackboxTelemetry` stream/history [d9697cf]
- [x] Task: Write Tests for Telemetry Feed Integration (Frontend) [46d294e]
- [x] Task: Implement Live Telemetry Logic in `TelemetryFeed.tsx` and `AgentAuditLog.tsx` [6ef8318]
- [x] Task: Conductor - User Manual Verification 'Telemetry & Reasoning Integration' (Protocol in workflow.md)

## Phase 3: Surgical Learning Surface [checkpoint: cde26ff]
Goal: Map strategic learnings from the backend to the experiment detail view.

- [x] Task: Create API Endpoint for `BlackboxLearning` (Structured results) [7140614]
- [x] Task: Write Tests for Learning Detail Surface (Frontend) [545a570]
- [x] Task: Implement Learning Integration in `ExperimentDetail.tsx` (Confidence scores & Tactical notes) [545a570]
- [x] Task: Conductor - User Manual Verification 'Surgical Learning Surface' (Protocol in workflow.md)

## Phase 4: Functional Actions & Agent Triggering [checkpoint: e537309]
Goal: Ensure the "Run" and "Verify" buttons trigger the actual `BlackboxSpecialist` backend.

- [x] Task: Create Backend Service to trigger `BlackboxSpecialist` via API [8ec3932]
- [x] Task: Write Tests for Experiment Execution Trigger (Frontend) [021e1a1]
- [x] Task: Implement Interaction Logic in `BlackBoxWizard.tsx` and `ExperimentCard.tsx` [021e1a1]
- [x] Task: Conductor - User Manual Verification 'Functional Actions & Agent Triggering' (Protocol in workflow.md)

## Phase 5: UI Audit & Decisive Cleanup
Goal: Final polish, removing placeholders, and ensuring "RaptorFlow Look" compliance.

- [~] Task: Audit `StatsBar` and `RiskSlider` against real backend data ranges
- [ ] Task: Remove orphan UI elements lacking backend logic
- [ ] Task: Final Style & Motion Polish (Framer Motion check)
- [ ] Task: Conductor - User Manual Verification 'UI Audit & Decisive Cleanup' (Protocol in workflow.md)
