# Implementation Plan: Backend Infrastructure Hardening (Track: BACKEND_HARDENING_20260119)

## Phase 1: Supabase & PostgreSQL Hardening
Focuses on schema integrity, security (RLS), and performance (indexes).

- [x] Task: Audit and Refactor RLS Policies.
    - [x] Write tests to verify cross-tenant access is blocked.
    - [x] Implement strict `workspace_id` and `user_id` checks on all tables.
- [x] Task: Database Indexing & Schema Cleanup.
    - [x] Identify high-latency query paths from logs.
    - [x] Add B-tree and GIN indexes for common filters and JSONB fields.
- [x] Task: Implement SQL Transaction Wrappers.
    - [x] Audit critical write operations in the codebase.
    - [x] Refactor multi-step updates to use `supabase.rpc()` or service-side transactions.
- [x] Task: Conductor - User Manual Verification 'Phase 1: Supabase & PostgreSQL Hardening' (Protocol in workflow.md)

## Phase 2: Redis (Upstash) Caching & Sync
Focuses on speed and reducing Supabase read pressure.

- [x] Task: Implement Global Caching Layer.
    - [x] Write tests for cache hit/miss and invalidation logic.
    - [x] Implement `getOrSet` pattern for AI results and Foundation data.
- [x] Task: Redis Pub/Sub for Real-time State Sync.
    - [x] Create a message bus for agent progress updates.
    - [x] Connect frontend listeners to Redis channels.
- [x] Task: Session Migration to Redis.
    - [x] Benchmarking current session latency.
    - [x] Migrate transient UI state to Redis KV pairs.
- [x] Task: Conductor - User Manual Verification 'Phase 2: Redis (Upstash) Caching & Sync' (Protocol in workflow.md)

## Phase 3: Task Reliability & Worker Hardening
Focuses on background jobs and error recovery.

- [x] Task: Redis-backed Job Queue.
    - [x] Implement a simple queue pattern (e.g., BullMQ or custom) for AI tasks.
    - [x] Write worker logic to process tasks from the queue.
- [x] Task: Implement Exponential Backoff Retries.
    - [x] Add a global retry utility for DB and external API calls.
    - [x] Integrate with existing agent logic.
- [x] Task: Migration Versioning System.
    - [x] Set up a structured migration folder (`/migrations`).
    - [x] Create a CLI utility to apply and track migrations via Supabase.
- [x] Task: Conductor - User Manual Verification 'Phase 3: Task Reliability & Worker Hardening' (Protocol in workflow.md)

## Phase 4: Benchmarking & Final Audit
Final verification of performance gains and security.

- [x] Task: Performance Benchmarking.
    - [x] Run load tests simulating concurrent AI agent activity.
    - [x] Verify latency improvements (>50% faster for cached paths).
- [x] Task: Security Red-Team Audit.
    - [x] Attempt unauthorized access to verify RLS effectiveness.
    - [x] Verify SQL transaction atomicity under failure conditions.
- [x] Task: Conductor - User Manual Verification 'Phase 4: Benchmarking & Final Audit' (Protocol in workflow.md)
