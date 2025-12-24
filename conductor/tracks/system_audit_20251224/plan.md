# Implementation Plan: System Audit, Infrastructure Completion, and Model Integration

This plan outlines the steps to audit the infrastructure, implement intelligent model routing, build a free search tool, and verify system-wide connectivity using TDD principles.

## Phase 1: Infrastructure Security & Environment Hardening [checkpoint: 67c86fe]
*Goal: Audit and secure all cloud services (GCP, Supabase, Upstash) and centralize secrets.*

- [x] **Task 1: Supabase Security Audit & RLS Enforcement** (cce6daa)
- [x] **Task 2: GCP Storage & Cloud Run Hardening** (bed3712)
- [x] **Task 3: Secret Management Centralization** (077d5ee)
- [x] **Task 4: Environment Standardization** (e30dea9)
- [x] **Task: Conductor - User Manual Verification 'Infrastructure Security & Environment Hardening' (Protocol in workflow.md)** (67c86fe)

## Phase 2: Vertex AI Intelligent Routing & Resilience [checkpoint: 99a5645]
*Goal: Implement the weighted model distribution and task-specific intelligence routing.*

- [x] **Task 1: Task-to-Model Mapping Logic** (8f29e74)
    - [ ] Define the `IntelligenceTier` enum (High, Mid, Base).
    - [ ] Write failing tests for the router (verifying correct model selection based on task type).
    - [ ] Implement the routing logic in `backend/core/vertex_setup.py`.
- [x] **Task 2: Resilience & Fallback Implementation** (6f1bc81)
    - [ ] Write failing tests for model failure scenarios.
    - [ ] Implement cascading fallback logic (e.g., if Gemini 3 fails, try Gemini 2.5).
    - [ ] Ensure all routing uses ENV-sourced API keys exclusively.
- [x] **Task: Conductor - User Manual Verification 'Vertex AI Intelligent Routing & Resilience' (Protocol in workflow.md)** (99a5645)

## Phase 3: Native Zero-Cost Search Tool [checkpoint: 96770ff]
*Goal: Build and integrate a 100% free search tool to replace paid APIs.*

- [x] **Task 1: Search Tool Core Development** (6ef8cac)
- [x] **Task 2: API Replacement & Integration** (1d23193)
- [x] **Task: Conductor - User Manual Verification 'Native Zero-Cost Search Tool' (Protocol in workflow.md)** (96770ff)

## Phase 4: Full-Stack Connectivity & State Integrity [checkpoint: 94f8a20]
*Goal: Verify every button push and ensure data propagates correctly across modules.*

- [x] **Task 1: Onboarding & ICP Data Flow Audit** (e12f31a)
- [x] **Task 2: Module Connectivity Verification (E2E)** (f67dc1a)
- [x] **Task 3: Upstash Redis & Performance Audit** (f67dc1a)
- [x] **Task: Conductor - User Manual Verification 'Full-Stack Connectivity & Verification' (Protocol in workflow.md)** (94f8a20)
