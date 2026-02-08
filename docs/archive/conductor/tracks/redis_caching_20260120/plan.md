# Implementation Plan: System-Wide Backend Verification & Redis Caching

## Phase 1: Global Backend Audit & Verification [checkpoint: audit_complete]
*Goal: Ensure every module is fully functional before adding the caching layer.*

- [x] Task: Audit Foundation & Cohorts Services
    - [x] Write integration tests for Brand Kit synthesis and RICP generation
    - [x] Verify Supabase RLS and data integrity for Foundation module
- [x] Task: Audit Moves & Campaigns Logic
    - [x] Write integration tests for "Absolute Infinity" Move generation
    - [x] Verify hierarchical graph integrity for Campaign Arcs
- [x] Task: Audit Matrix & Blackbox Engines
    - [x] Write integration tests for Matrix metric aggregation
    - [x] Verify Blackbox "Experimental Move" generation and risk assessment
- [x] Task: Audit Titan Intelligence Spine
    - [x] Write integration tests for Search Multiplexer and Scraper Pool
    - [x] Verify parallel search result synthesis and semantic ranking
- [x] Task: Conductor - User Manual Verification 'Global Backend Audit & Verification' (Protocol in workflow.md)

## Phase 2: Redis Infrastructure & Global Caching Wrapper [checkpoint: infra_complete]
*Goal: Establish the high-performance plumbing for the cache layer.*

- [x] Task: Configure Upstash Redis Client
    - [x] Implement connection pooling and error handling in `src/lib/redis.ts` (Verified existing client)
    - [x] Add Redis environment variables to `.env.production` and GCP Secret Manager
- [x] Task: Implement Global `withCache` Utility
    - [x] Write unit tests for `withCache` (hit/miss logic, TTL enforcement)
    - [x] Implement the wrapper with generic typing for all service domains (Fixed `@cached` decorator for async)
- [x] Task: Conductor - User Manual Verification 'Redis Infrastructure & Global Caching Wrapper' (Protocol in workflow.md)

## Phase 3: Module-Specific Caching Implementation [checkpoint: module_cache_complete]
*Goal: Systematically apply caching to eliminate redundant costs.*

- [x] Task: Implement AI Inference Caching (Blackbox/Muse)
    - [x] Write tests for semantic prompt hashing and cache retrieval
    - [x] Apply `withCache` to expensive Gemini LLM calls
- [x] Task: Implement Titan Research Caching
    - [x] Write tests for URL/Query-based result caching
    - [x] Apply `withCache` to Search Multiplexer and Scraper Pool results
- [x] Task: Implement Strategic State Caching (Foundation/Cohorts)
    - [x] Write tests for positioning and segment caching
    - [x] Apply `withCache` to computed strategic objects
- [x] Task: Implement Matrix Metric Caching
    - [x] Write tests for dashboard metric caching with 1h TTL
    - [x] Apply `withCache` to Matrix aggregation services
- [x] Task: Conductor - User Manual Verification 'Module-Specific Caching Implementation' (Protocol in workflow.md)

## Phase 4: Cache Invalidation & Management [checkpoint: invalidation_complete]
*Goal: Ensure data integrity and provide surgical control over the cache.*

- [x] Task: Implement Surgical Cache Purge Skill
    - [x] Write tests for namespace-specific key deletion
    - [x] Integrate "Cache Purge" tool into the Universal Agent tool registry
- [x] Task: Implement Dependency-Based Invalidation
    - [x] Write tests for "Cascade Purge" (e.g., Brand Kit update -> clear whole workspace cache)
    - [x] Implement event-driven invalidation logic in Foundation/ICP services
- [x] Task: Conductor - User Manual Verification 'Cache Invalidation & Management' (Protocol in workflow.md)

## Phase 5: Final Optimization & Economy Audit [checkpoint: final_audit_complete]
*Goal: Verify the performance gains and cost reduction targets.*

- [x] Task: Execute Performance Benchmark
    - [x] Compare response times for Cache-Hit vs Cache-Miss across all modules
    - [x] Verify sub-1ms retrieval for cached data (Mocked verification)
- [x] Task: Conduct Economy & Billing Audit
    - [x] Verify that redundant workflows trigger zero external API calls
    - [x] Document estimated cost savings based on cache hit rates
- [x] Task: Conductor - User Manual Verification 'Final Optimization & Economy Audit' (Protocol in workflow.md)