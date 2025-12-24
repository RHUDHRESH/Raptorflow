# Specification: System Audit, Infrastructure Completion, and Model Integration

## Overview
This track focuses on a comprehensive audit and technical completion of the RaptorFlow platform. The goal is to ensure end-to-end functionality, secure infrastructure, a zero-cost search engine, and task-specific AI intelligence routing. We are moving from "prototype" to a hardened "Production" state across Supabase, GCP, Vercel, and internal modules (Muse, Matrix, Blackbox).

## Functional Requirements

### 1. Infrastructure Hardening & Configuration
- **Supabase Audit:**
    - Verify and implement Row Level Security (RLS) policies for all tables.
    - Audit Authentication flows (email/social) and ensure secure token handling.
- **GCP Storage (GCS):**
    - Configure CORS policies for frontend access.
    - Set up Lifecycle management (e.g., auto-deletion of temporary assets).
    - Hardened bucket permissions (Least Privilege).
- **Cloud Run & CI/CD:**
    - Secure the deployment pipeline in GitHub Workflows.
    - Integrate GCP Secret Manager for all sensitive keys.
- **Upstash Redis:**
    - Audit caching logic for performance and data consistency.
    - Ensure Redis is utilized correctly as a transient database for high-frequency state.
- **PhonePe Integration:**
    - End-to-end verification of the payment webhook and success/failure redirects.

### 2. Intelligent Inference Routing (Vertex AI)
- **Intelligence-to-Task Mapping:**
    - **High Tier (Gemini 3 Flash Preview):** Complex Campaign creation, strategic positioning, and deep analysis.
    - **Mid Tier (Gemini 2.5/2.0 Flash):** Standard ICP generation, move execution, and Blackbox analysis.
    - **Base Tier (Gemini 1.5 Flash):** Simple UI helpers, Muse grammar checks, and routine formatting.
- **Security:** Inference must strictly use Vertex API keys sourced from ENV/Secret Manager. No hardcoding.
- **Fallback Logic:** Implement a robust fallback system (Cascading or ENV-based) to ensure service continuity if a specific model or key fails.

### 3. Zero-Cost Native Search Engine
- **Search Tool Development:**
    - Build a native search tool using DuckDuckGo or Brave Search to replace paid APIs (Tavily/Perplexity).
    - Ensure the tool is "economical and viable" for Cloud Run deployment.
    - Tool must provide structured metadata for downstream AI consumption.

### 4. Onboarding & Data Core Audit
- **Core JSON Audit:**
    - Verify that Onboarding produces a "thorough JSON" source of truth.
    - Ensure this JSON correctly feeds the **Cohorts (ICPs)** and **Comparator** modules.
- **State Integrity:**
    - Validate schema consistency across the JSON lifecycle.

### 5. System-Wide Verification (Muse, Matrix, Blackbox)
- **Button-to-Backend Audit:** Every interaction in the UI must be traced to its backend endpoint.
- **E2E Testing:** Implement Playwright/Vitest tests for core user journeys.
- **Network Path Verification:** Confirm all modules (Muse, Matrix, etc.) are reachable and functional in the production environment.

## Non-Functional Requirements
- **Cost Efficiency:** 100% free search; economical Cloud Run footprint.
- **Security:** Zero hardcoded secrets; GCP Secret Manager integration; hardened IAM.
- **Performance:** Optimized Redis caching for "calm" UI responsiveness.

## Acceptance Criteria
- [ ] `env.example` created with all necessary infrastructure variables.
- [ ] Infrastructure Audit Report completed for Supabase, GCP, and Upstash.
- [ ] Vertex AI Routing logic implemented and tested across task types.
- [ ] Native, free search tool functional and integrated into the "Moves" and "Campaigns" engines.
- [ ] E2E tests pass for Onboarding, Muse, and Matrix modules.
- [ ] All paid search API keys (Tavily/Perplexity) removed and replaced.

## Out of Scope
- Frontend UI "polishing" (User will handle later).
- Creating new marketing frameworks (Existing ones will be used).
