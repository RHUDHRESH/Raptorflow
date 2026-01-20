# Track Specification: System-Wide Backend Verification & Redis Caching

## 1. Overview
This track focuses on two critical objectives:
1.  **Verification:** Validating that the entire RaptorFlow backend (Module > Service > Domain) is fully operational and reliable.
2.  **Optimization:** Implementing a comprehensive Redis-based caching layer to maximize performance and minimize operational costs (specifically AI inference and Titan research expenses).

## 2. Scope
- **Modules:** Foundation, Cohorts, Moves, Campaigns, Muse, Matrix, Blackbox, and Titan.
- **Infrastructure:** Upstash (Redis) integration via the `withCache` global wrapper.

## 3. Functional Requirements

### 3.1 Backend System Verification
- Execute a full-suite audit of all existing backend services.
- Ensure 1-1 connectivity between services and the Supabase persistence layer.
- Verify global error handling and "RaptorFlow" Bespoke API standards across all endpoints.

### 3.2 Comprehensive Caching Strategy
- **AI Inference Caching:** Implement semantic/exact-match caching for Gemini LLM responses to prevent redundant strategic generation costs.
- **Titan Intelligence Caching:** Cache results from the Search Multiplexer and Scraper Pool to avoid repeated network, proxy, and compute overhead.
- **Strategic State Caching:** Store pre-computed RICP profiles, Positioning Soundbites, and Campaign Arcs in high-speed memory.
- **Dashboard Optimization:** Cache Matrix metrics to ensure the "Boardroom View" remains responsive and expensive analytics queries are minimized.

### 3.3 Cache Invalidation & Management
- **Manual Purge:** Integration with the Matrix Dashboard for surgical, namespace-specific cache clearing.
- **Smart TTLs:** Implementation of cost-optimized expiration windows (e.g., 24h for research, 1h for metrics).
- **Dependency Chaining:** Automated invalidation of downstream strategic assets when primary "Source of Truth" (e.g., Foundation Brand Kit) is updated.

## 4. Non-Functional Requirements
- **Economy:** Reduce external API billing (Vertex AI, Search APIs, Proxies) by at least 40% for repeated workflows.
- **Performance:** Achieve sub-100ms response times for cached strategic data retrieval.
- **Integrity:** Ensure the "Blackbox" engine and "Titan" researcher always have access to a "Cache Purge" skill for real-time bypass when required.

## 5. Acceptance Criteria
- [ ] All backend modules pass a comprehensive integration test suite.
- [ ] Redis `withCache` wrapper is implemented and verified across all service domains.
- [ ] Redundant LLM calls are demonstrably intercepted by the cache layer.
- [ ] Matrix Dashboard reflects "Cache Status" and provides a working purge mechanism.
- [ ] System remains stable under "Cache-Miss" scenarios (graceful degradation).

## 6. Out of Scope
- Migrating core persistence from Supabase to Redis (Redis is for transient cache/messaging only).
- Frontend UI redesign (caching is a backend/infrastructure optimization).
