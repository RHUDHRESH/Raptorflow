# Implementation Plan - Backend Consolidation & System Audit

## Phase 1: Architecture & API Standardization [checkpoint: 4b4dea5]
Establish the foundation for the reorganization and standardized communication.

- [x] Task: Define Unified Backend Directory Structure (e082b91)
    - [x] Create directory structure template following Module > Service > Domain hierarchy.
    - [x] Document the structure in `docs/architecture/backend-structure.md`.
- [x] Task: Implement "RaptorFlow" Bespoke API Standard (92f31bc)
    - [x] Create a shared TypeScript/Node.js utility for standardized success/error responses.
    - [x] Implement a global error handler/middleware to enforce this standard.
- [ ] Task: Conductor - User Manual Verification 'Phase 1: Architecture & API Standardization' (Protocol in workflow.md)

## Phase 2: Backend Reorganization & TDD Implementation [checkpoint: 14f2823]
Refactor existing modules into the new structure while adding test coverage.

- [x] Task: Refactor Foundation Module (8ebb101)
    - [x] [RED] Write failing tests for Brand Kit and Positioning logic.
    - [x] [GREEN] Move logic to `src/modules/foundation/services` and `src/modules/foundation/domain`.
    - [x] [REFACTOR] Clean up legacy script references and imports.
- [x] Task: Refactor Intelligence Modules (Titan & Blackbox) (cf5f78a)
    - [x] [RED] Write failing tests for scraping and volatility engine logic.
    - [x] [GREEN] Reorganize into `src/modules/titan` and `src/modules/blackbox`.
    - [x] [REFACTOR] Optimize common utilities and agent orchestration.
- [x] Task: Refactor Operations Modules (Cohorts, Moves, Campaigns) (1b85bcf)
    - [x] [RED] Write failing tests for RICP and Breathing Arcs logic.
    - [x] [GREEN] Reorganize into their respective module directories.
    - [x] [REFACTOR] Ensure strict decoupling from Next.js route handlers.
- [ ] Task: Conductor - User Manual Verification 'Phase 2: Backend Reorganization & TDD Implementation' (Protocol in workflow.md)

## Phase 3: Security, Performance & Infrastructure Audit
Verify the "Cognitive Spine" and data integrity.

- [x] Task: Comprehensive Security & RLS Audit (43aaf0c)
    - [x] Review all Supabase RLS policies against the "Identity Standard."
    - [x] [RED] Write failing integration tests that attempt unauthorized data access.
    - [x] [GREEN] Fix any RLS gaps and confirm tests pass.
- [x] Task: Performance Benchmarking (46cb0fd)
    - [x] Set up benchmark suites for Titan (Search Multiplexer) and Blackbox (Engine).
    - [x] Document current latencies and identify optimization bottlenecks.
- [ ] Task: Secret Management Review
    - [ ] Verify all hardcoded secrets are moved to GCP Secret Manager.
- [ ] Task: Conductor - User Manual Verification 'Phase 3: Security, Performance & Infrastructure Audit' (Protocol in workflow.md)

## Phase 4: Frontend Alignment & UX Polish
Bring the user-facing side into sync with the new backend.

- [ ] Task: Update Frontend Service Layers
    - [ ] Audit all `fetch` or SDK calls in the frontend.
    - [ ] [RED] Write failing tests for frontend components expecting old API shapes.
    - [ ] [GREEN] Update components to consume the "RaptorFlow" standard response.
- [ ] Task: Implement Standardized Error UI
    - [ ] Create/Update Sonner toast components to handle bespoke error codes.
    - [ ] Ensure all forms and actions provide consistent feedback.
- [ ] Task: UX Polish Audit
    - [ ] Audit loading states and Framer Motion transitions across all pages.
    - [ ] Refine responsive behavior for strictly "Editorial restraint."
- [ ] Task: Conductor - User Manual Verification 'Phase 4: Frontend Alignment & UX Polish' (Protocol in workflow.md)

## Phase 5: Final System Verification & Cleanup
Ensure the entire OS is "ready to go."

- [ ] Task: End-to-End Integration Testing
    - [ ] Execute full user journey tests (Onboarding -> RICP -> Moves -> Matrix).
- [ ] Task: Final Coverage Verification
    - [ ] Generate system-wide coverage report and ensure >80% coverage.
- [ ] Task: Legacy Script Cleanup
    - [ ] Remove or archive all `apply_fix.py`, `execute_migration.py`, and other temporary scripts.
- [ ] Task: Conductor - User Manual Verification 'Phase 5: Final System Verification & Cleanup' (Protocol in workflow.md)
