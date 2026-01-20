# Implementation Plan: System-Wide Backend Verification & Redis Caching

## Phase 1: Global Backend Audit & Verification
*Goal: Ensure every module is fully functional before adding the caching layer.*

- [ ] Task: Audit Foundation & Cohorts Services
    - [ ] Write integration tests for Brand Kit synthesis and RICP generation
    - [ ] Verify Supabase RLS and data integrity for Foundation module
- [ ] Task: Audit Moves & Campaigns Logic
    - [ ] Write integration tests for "Absolute Infinity" Move generation
    - [ ] Verify hierarchical graph integrity for Campaign Arcs
- [ ] Task: Audit Matrix & Blackbox Engines
    - [ ] Write integration tests for Matrix metric aggregation
    - [ ] Verify Blackbox "Experimental Move" generation and risk assessment
- [ ] Task: Audit Titan Intelligence Spine
    - [ ] Write integration tests for Search Multiplexer and Scraper Pool
    - [ ] Verify parallel search result synthesis and semantic ranking
- [ ] Task: Conductor - User Manual Verification 'Global Backend Audit & Verification' (Protocol in workflow.md)

## Phase 2: Redis Infrastructure & Global Caching Wrapper
*Goal: Establish the high-performance plumbing for the cache layer.*

- [ ] Task: Configure Upstash Redis Client
    - [ ] Implement connection pooling and error handling in `src/lib/redis.ts`
    - [ ] Add Redis environment variables to `.env.production` and GCP Secret Manager
- [ ] Task: Implement Global `withCache` Utility
    - [ ] Write unit tests for `withCache` (hit/miss logic, TTL enforcement)
    - [ ] Implement the wrapper with generic typing for all service domains
- [ ] Task: Conductor - User Manual Verification 'Redis Infrastructure & Global Caching Wrapper' (Protocol in workflow.md)

## Phase 3: Module-Specific Caching Implementation
*Goal: Systematically apply caching to eliminate redundant costs.*

- [ ] Task: Implement AI Inference Caching (Blackbox/Muse)
    - [ ] Write tests for semantic prompt hashing and cache retrieval
    - [ ] Apply `withCache` to expensive Gemini LLM calls
- [ ] Task: Implement Titan Research Caching
    - [ ] Write tests for URL/Query-based result caching
    - [ ] Apply `withCache` to Search Multiplexer and Scraper Pool results
- [ ] Task: Implement Strategic State Caching (Foundation/Cohorts)
    - [ ] Write tests for positioning and segment caching
    - [ ] Apply `withCache` to computed strategic objects
- [ ] Task: Implement Matrix Metric Caching
    - [ ] Write tests for dashboard metric caching with 1h TTL
    - [ ] Apply `withCache` to Matrix aggregation services
- [ ] Task: Conductor - User Manual Verification 'Module-Specific Caching Implementation' (Protocol in workflow.md)

## Phase 4: Cache Invalidation & Management
*Goal: Ensure data integrity and provide surgical control over the cache.*

- [ ] Task: Implement Surgical Cache Purge Skill
    - [ ] Write tests for namespace-specific key deletion
    - [ ] Integrate "Cache Purge" skill into the Universal Agent and Matrix Dashboard
- [ ] Task: Implement Dependency-Based Invalidation
    - [ ] Write tests for "Cascade Purge" (e.g., Brand Kit update -> clear Moves cache)
    - [ ] Implement event-driven invalidation logic
- [ ] Task: Conductor - User Manual Verification 'Cache Invalidation & Management' (Protocol in workflow.md)

## Phase 5: Final Optimization & Economy Audit
*Goal: Verify the performance gains and cost reduction targets.*

- [ ] Task: Execute Performance Benchmark
    - [ ] Compare response times for Cache-Hit vs Cache-Miss across all modules
    - [ ] Verify sub-100ms retrieval for cached data
- [ ] Task: Conduct Economy & Billing Audit
    - [ ] Verify that redundant workflows trigger zero external API calls
    - [ ] Document estimated cost savings based on cache hit rates
- [ ] Task: Conductor - User Manual Verification 'Final Optimization & Economy Audit' (Protocol in workflow.md)
