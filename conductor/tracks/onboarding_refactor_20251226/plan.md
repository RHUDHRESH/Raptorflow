# Implementation Plan: Refactor Onboarding & Implement Precision Soundbite Framework 3.0

## Phase 1: Foundation, State Management & Backend Setup [checkpoint: ae278e1]
*Goal: Ensure the data structure can support the 7-soundbite framework and the multi-phase onboarding state.*

- [x] **Task 1.1: Define Data Schemas (Supabase)** (2155a81)
  - Create/Update tables for `framework_foundation` (JTBD, Hierarchy), `proof_vault`, and `precision_soundbites`.
  - Ensure relational integrity between users and their framework data.
- [x] **Task 1.2: Implement State Sync Logic** (54e918a)
  - Update the "Foundation" module state to support real-time syncing of onboarding progress.
  - Implement a `useOnboarding` hook to manage phase-to-phase transitions and data persistence.
- [x] **Task 1.3: Backend Logic for AI Synthesis** (474420f)
  - Implement Gemini-powered prompts in the backend to transform Phase 3-5 inputs into draft soundbites.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Foundation & Backend' (Protocol in workflow.md)

## Phase 2: Onboarding Flow Refactoring (The Fix) [checkpoint: 8543fcf]
*Goal: Remove redundant steps and establish the new high-fidelity phase structure in `src/app/foundation/`.*

- [x] **Task 2.1: Audit and Prune Existing Onboarding** (9d77138)
  - Identify and remove duplicate ICP/Question components in `raptorflow-app/src/app/foundation` and related components.
- [x] **Task 2.2: Implement Phase Navigation & UI Scaffold** (fc76a0f)
  - Establish the route structure for `foundation/phase3`, `phase4`, `phase5`, and `phase6`.
  - Create the layout for transitions using Framer Motion, adhering to "Quiet Luxury" style.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: UI Refactoring' (Protocol in workflow.md)

## Phase 3: Phase 3 Implementation (JTBD & Hierarchy)
*Goal: Create the foundation-building interface at `foundation/phase3`.*

- [ ] **Task 3.1: JTBD Canvas Component**
  - Build the interactive canvas for Functional, Emotional, and Social jobs.
  - Write tests for input validation and state persistence.
- [ ] **Task 3.2: Message Hierarchy Pyramid UI**
  - Implement the "Pyramid" visualization for Essence, Core Message, and Pillars.
- [ ] **Task 3.3: Customer Awareness Matrix Tool**
  - Create the segmentation UI for mapping awareness tiers.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: JTBD & Hierarchy' (Protocol in workflow.md)

## Phase 4: Phase 4 & 5 Implementation (Agitation, Mechanism & Proof Vault)
*Goal: Build the research and differentiation tools at `foundation/phase4` and `foundation/phase5`.*

- [ ] **Task 4.1: Research Boards & Agitation Logic (Phase 4)**
  - Create the "Digital Whiteboard" for pain-point aggregation.
- [ ] **Task 4.2: Technical Differentiation Auditor (Phase 5)**
  - Build the side-by-side mechanism auditor.
- [ ] **Task 4.3: Evidence & Proof Vault**
  - Implement the centralized sidebar/modal for storing and linking evidence (stats, testimonials).
- [ ] Task: Conductor - User Manual Verification 'Phase 4/5: Research & Proof' (Protocol in workflow.md)

## Phase 5: Phase 6 Implementation (Precision Soundbite Studio)
*Goal: The final engine at `foundation/phase6` that generates and validates the 7 soundbites.*

- [ ] **Task 5.1: Hybrid Draft & Refine Studio**
  - Implement the AI-drafting engine that pulls from previous phases.
- [ ] **Task 5.2: Sequential Soundbite Finalization**
  - Create the "Sequential Builder" flow with mandatory Clarity & Proof Audits.
- [ ] **Task 5.3: Comparison Playground**
  - Build the variation comparison UI for fine-tuning outputs.
- [ ] Task: Conductor - User Manual Verification 'Phase 6: Soundbite Studio' (Protocol in workflow.md)

## Phase 6: Final Integration & Quality Gate
*Goal: End-to-end testing and styling polish.*

- [ ] **Task 6.1: End-to-End Onboarding Validation**
  - Verify data flows correctly from Phase 3 through Phase 6 and updates the "Foundation" module.
- [ ] **Task 6.2: Visual Polish & Accessibility Audit**
  - Final pass on spacing, typography hierarchy, and motion easing.
- [ ] Task: Conductor - User Manual Verification 'Final Integration' (Protocol in workflow.md)
