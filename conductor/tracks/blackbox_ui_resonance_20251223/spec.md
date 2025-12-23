# Specification: Blackbox Backend-Frontend Resonance

## 1. Overview
The goal of this track is to integrate the backend "Blackbox" industrial engine with the frontend UI. This ensures that the "Marketing Experiment" components move beyond placeholders and accurately reflect the engine's intricate logic (telemetry, outcomes, and learnings) while strictly adhering to the "RaptorFlow Look": calm, expensive, and decisive.

## 2. Functional Requirements

### 2.1 Evidence & Outcome Integration
- **Outcome to Evidence:** Connect the `BlackboxOutcome` model to the `EvidenceLog.tsx` and `ResultsStrip.tsx` components.
- **Data Source:** Fetch real performance data (conversion, engagement, value) from the backend database (Supabase) instead of using mock data.

### 2.2 Telemetry & "The Reasoning"
- **Chain of Thought:** Map `BlackboxTelemetry` traces to the `TelemetryFeed.tsx` and `AgentAuditLog.tsx` components.
- **Decisive Visuals:** Show the "Why" behind an experiment's progress—specifically, which agent made what decision and why it matters.

### 2.3 Surgical Learning Surface
- **Learning to Strategy:** Map `BlackboxLearning` content directly to `ExperimentDetail.tsx`.
- **Impact:** Surface the mathematical confidence and specific tactical/strategic learnings (e.g., "Audience A responded better to tone X") to provide a "Boardroom" level of insight.

### 2.4 Functional Interactions
- **Live Agent Triggering:** Ensure primary actions (e.g., "Run Experiment", "Verify Check-in") trigger real backend Agent runs via the `BlackboxSpecialist` and `CognitiveSupervisor`.
- **Status Syncing:** Update `ExperimentCard` and `ExperimentList` statuses (pending, running, completed) based on the actual backend state.

## 3. Visual & UX Standards (RaptorFlow Look)
- **Audit & Refine:** Review all Blackbox components (`StatsBar`, `MetricDelta`, `RiskSlider`) to ensure they align with backend data ranges.
- **Restraint:** Remove any UI elements that lack corresponding backend logic to maintain the "one primary decision per screen" rule.
- **Style Preservation:** Maintain existing typography (Playfair/Inter) and color tokens (Ivory Paper/Graphite) while adding functional depth.

## 4. Acceptance Criteria
- [ ] `EvidenceLog` displays real data fetched from the `blackbox_outcomes` table.
- [ ] `TelemetryFeed` shows live agent execution traces from `blackbox_telemetry`.
- [ ] `ExperimentDetail` displays structured learnings from `blackbox_learnings`.
- [ ] Clicking "Run" or "Verify" initiates a backend process that completes and updates the UI status.
- [ ] No placeholder data remains in the core Blackbox experiment flow.
