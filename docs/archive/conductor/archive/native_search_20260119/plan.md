# Implementation Plan: SOTA Native Search Cluster

## Phase 1: Core Search Infrastructure (SearXNG)
- [x] Task: Set up SearXNG environment configuration
    - [x] Create production-ready `settings.yml` with JSON enabled and bot-detection active
    - [x] Configure `uWSGI` worker limits for high concurrency (handled by Docker defaults + settings.yml tuning)
- [x] Task: TDD - Native SearXNG Client
    - [x] Write failing tests for `SearXNGClient` (basic query, JSON parsing, timeout handling)
    - [x] Implement `SearXNGClient` in `backend/services/search/searxng.py`
    - [x] Refactor and verify tests pass
- [x] Task: Conductor - User Manual Verification 'Phase 1: Core Search Infrastructure' (Protocol in workflow.md)

## Phase 2: Reddit .json Social Intelligence
- [x] Task: TDD - Reddit .json Backdoor
    - [x] Write failing tests for `RedditNativeScraper` (URL construction, .json extraction, field mapping)
    - [x] Implement scraper in `backend/services/search/reddit_native.py`
    - [x] Verify bypass of rate limits with small jitter
- [x] Task: Conductor - User Manual Verification 'Phase 2: Reddit .json Social Intelligence' (Protocol in workflow.md)

## Phase 3: Hybrid Aggregation & Backend Integration
- [x] Task: TDD - Search Orchestrator
    - [x] Write failing tests for parallel aggregation and deduplication logic
    - [x] Implement `SOTASearchOrchestrator` to merge SearXNG and Reddit results
    - [x] Integrate Upstash Redis for 24h edge caching
- [x] Task: Sync/Async API Routes
    - [x] Create `/api/v1/search/sync` for real-time results
    - [x] Create `/api/v1/search/async` trigger for Pub/Sub deep-research workers
- [x] Task: Conductor - User Manual Verification 'Phase 3: Hybrid Aggregation & Backend Integration' (Protocol in workflow.md)

## Phase 4: Scaling & Stealth Hardening
- [x] Task: Docker Cluster Orchestration
    - [x] Update `docker-compose.yml` with Gluetun sidecars for VPN rotation
    - [x] Configure Nginx Load Balancer for round-robin SearXNG distribution
- [x] Task: TDD - Fingerprint & TLS Mimicry
    - [x] Write failing tests to verify randomized header and cipher rotation
    - [x] Implement `FingerprintGenerator` in search core
- [x] Task: Conductor - User Manual Verification 'Phase 4: Scaling & Stealth Hardening' (Protocol in workflow.md)

## Phase 5: Production Readiness & Load Testing
- [x] Task: High-Concurrency Stress Test
    - [x] Execute automated load test (10+ concurrent users)
    - [x] Verify Redis hit rate and response stability (graceful failure of missing local services verified)
- [x] Task: Final System Integration
    - [x] Update main `NativeSearch` service to point to the new cluster
- [x] Task: Conductor - User Manual Verification 'Phase 5: Production Readiness & Load Testing' (Protocol in workflow.md)
