# Specification: Growth Engine Modernization

## 1. Overview
This track transforms RaptorFlow from a passive observation dashboard into a proactive growth engine. It focuses on exposing existing backend "skills" in the Matrix module, revamping the Black Box experiment generator to be hypothesis-driven, and redesigning the Campaign wizard for transparency and human-in-the-loop control.

## 2. Functional Requirements

### 2.1 Matrix Module: Operator Controls
- **Skill Exposure:** Implement UI components (sliders, buttons, toggles) to trigger existing backend skills:
    - `InferenceThrottlingSkill`: Slider for global/per-agent token caps.
    - `CachePurgeSkill`: One-click cache clearing.
    - `ResourceScalingSkill`: Controls for compute scaling.
    - `RetrainTriggerSkill`: Manual trigger for model retraining based on drift.
    - `EmergencyHaltSkill`: Global kill-switch (enhance existing implementation with feedback).
- **Integrated Management Panel:** A dedicated dashboard section that combines these controls with their relevant metrics for an "Operator View."

### 2.2 Black Box: Hypothesis-Driven Experiments
- **Experiment Builder:** Replace random template selection with a structured form requiring:
    - **Hypothesis Statement:** Structured input (Action + Metric + Expected Change + Rationale).
    - **Variables:** Explicit definition of Control vs. Treatment variables.
    - **Statistical Targets:** Fields for sample size, confidence levels, and duration.
- **Marketer Template Library:** Integrate a library of proven heuristics (e.g., "Subject Line Question Test") that users can select to pre-populate the builder.
- **ROI Integration:** Surface forecasted ROI and historical win rates (leveraging `BlackboxService`).

### 2.3 Campaign Wizard: Transparent & Interactive
- **Step-by-Step Wizard:** Refactor `NewCampaignWizard` into discrete steps:
    1. Objective & KPI Definition.
    2. ICP & Segmentation.
    3. Offer & Messaging.
    4. Channel Selection & Budget.
- **Dynamic Previews:** A side-by-side split view showing a live Gantt-style 90-day arc preview that updates as steps are completed.
- **Human-in-the-Loop Approvals:** Use LangGraph interrupt points to pause for user approval/refinement after critical steps (e.g., after the 90-day arc is drafted).
- **Final Review:** A comprehensive "Review & Refine" screen before persistence.

## 3. Non-Functional Requirements
- **Quiet Luxury UI:** Adhere strictly to the RaptorFlow design system (borders > shadows, Playfair/Inter typography, neutral palette).
- **Asynchronous Feedback:** Provide clear loading states and status updates for long-running orchestrator tasks.
- **High Reliability:** Ensure all skill executions log audit entries to Supabase.

## 4. Acceptance Criteria
- Users can throttle token consumption and purge caches directly from the Matrix UI.
- New experiments created in Black Box have a structured hypothesis and statistical targets.
- The Campaign wizard allows users to preview the 90-day arc and approve/edit moves before finalization.
- All new UI components pass visual and functional testing in the RaptorFlow environment.

## 5. Out of Scope
- Integration with external 3rd-party marketing tools (beyond existing search/storage).
- Real-time collaborative editing within the wizard.
