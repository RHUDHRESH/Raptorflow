# Implementation Plan: System Audit, Infrastructure Completion, and Model Integration

This plan outlines the steps to audit the infrastructure, implement intelligent model routing, build a free search tool, and verify system-wide connectivity using TDD principles.

## Phase 1: Infrastructure Security & Environment Hardening
*Goal: Audit and secure all cloud services (GCP, Supabase, Upstash) and centralize secrets.*

- [x] **Task 1: Supabase Security Audit & RLS Enforcement** (cce6daa)
    - [ ] Audit all tables for existing RLS policies.
    - [ ] Write SQL migrations to enforce "Least Privilege" access.
    - [ ] Verify Auth flows and session handling security.
- [x] **Task 2: GCP Storage & Cloud Run Hardening** (bed3712)
    - [ ] Configure GCS CORS policies for `raptorflow-app` domains.
    - [ ] Implement GCS lifecycle rules for temporary asset cleanup.
    - [ ] Audit Cloud Run service account permissions (IAM).
- [ ] **Task 3: Secret Management Centralization**
    - [ ] Identify all hardcoded or plain-text keys in `backend/` and `raptorflow-app/`.
    - [ ] Migrate all keys to GCP Secret Manager.
    - [ ] Implement backend logic to fetch secrets from ENV/Secret Manager at runtime.
- [ ] **Task 4: Environment Standardization**
    - [ ] Create a master `.env.example` covering all modules.
    - [ ] Audit and fix the PhonePe webhook and redirect configuration.
- [ ] **Task: Conductor - User Manual Verification 'Infrastructure Security & Environment Hardening' (Protocol in workflow.md)**

## Phase 2: Vertex AI Intelligent Routing & Resilience
*Goal: Implement the weighted model distribution and task-specific intelligence routing.*

- [ ] **Task 1: Task-to-Model Mapping Logic**
    - [ ] Define the `IntelligenceTier` enum (High, Mid, Base).
    - [ ] Write failing tests for the router (verifying correct model selection based on task type).
    - [ ] Implement the routing logic in `backend/core/vertex_setup.py`.
- [ ] **Task 2: Resilience & Fallback Implementation**
    - [ ] Write failing tests for model failure scenarios.
    - [ ] Implement cascading fallback logic (e.g., if Gemini 3 fails, try Gemini 2.5).
    - [ ] Ensure all routing uses ENV-sourced API keys exclusively.
- [ ] **Task: Conductor - User Manual Verification 'Vertex AI Intelligent Routing & Resilience' (Protocol in workflow.md)**

## Phase 3: Native Zero-Cost Search Tool
*Goal: Build and integrate a 100% free search tool to replace paid APIs.*

- [ ] **Task 1: Search Tool Core Development**
    - [ ] Prototype a DuckDuckGo/Brave Search-based scraper/aggregator.
    - [ ] Write unit tests for search result parsing and metadata extraction.
    - [ ] Implement the search tool as a native module in `backend/core/`.
- [ ] **Task 2: API Replacement & Integration**
    - [ ] Locate all instances of Tavily/Perplexity usage.
    - [ ] Replace with the new native search tool.
    - [ ] Optimize for Cloud Run memory/CPU footprints to ensure economic viability.
- [ ] **Task: Conductor - User Manual Verification 'Native Zero-Cost Search Tool' (Protocol in workflow.md)**

## Phase 4: Full-Stack Connectivity & State Integrity
*Goal: Verify every button push and ensure data propagates correctly across modules.*

- [ ] **Task 1: Onboarding & ICP Data Flow Audit**
    - [ ] Audit the "thorough JSON" generation from Onboarding.
    - [ ] Verify schema consistency when JSON is used by Cohorts, Muse, and Matrix.
    - [ ] Implement schema validation checks at module entry points.
- [ ] **Task 2: Module Connectivity Verification (E2E)**
    - [ ] Implement Playwright E2E tests for Muse (grammar check, asset generation).
    - [ ] Implement Playwright E2E tests for Matrix (dashboard loading, RAG status updates).
    - [ ] Implement Playwright E2E tests for Blackbox (telemetry ingest).
- [ ] **Task 3: Upstash Redis & Performance Audit**
    - [ ] Verify Redis caching is functional and doesn't lead to stale data.
    - [ ] Audit backend for optimal "operator view" responsiveness.
- [ ] **Task: Conductor - User Manual Verification 'Full-Stack Connectivity & Verification' (Protocol in workflow.md)**
