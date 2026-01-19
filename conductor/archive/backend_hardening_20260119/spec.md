# Specification: Backend Infrastructure Hardening (Track: BACKEND_HARDENING_20260119)

## Overview
This track focuses on transforming RaptorFlow's data layer into an industrial-grade foundation. We will optimize Supabase (PostgreSQL), implement a high-performance Redis (Upstash) caching and sync layer, and harden background worker reliability. The goal is to ensure the "Cognitive Engine" operates with near-zero latency and absolute data integrity.

## Functional Requirements

### 1. Supabase & PostgreSQL Hardening
- **Schema Audit:** Review all tables for proper primary keys, foreign key constraints, and performance-critical indexes.
- **RLS Tightening:** Audit and enforce strict Row Level Security (RLS) policies to ensure absolute tenant isolation between user workspaces.
- **Transaction Integrity:** Refactor critical write operations (Moves, Campaigns, Onboarding) to use PostgreSQL transactions to prevent partial data states.
- **Connection Management:** Optimize connection pooling settings to prevent exhaustion during peak AI agent activity.

### 2. Redis (Upstash) Optimization
- **Standard Result Caching:** Cache final AI outputs (Brand Kits, Moves, etc.) for 24 hours to minimize database load and costs.
- **Real-time State Sync (Pub/Sub):** Implement Redis Pub/Sub to synchronize state between long-running backend agents and the frontend UI instantly.
- **Session Persistence:** Migrate transient session data to Redis for faster access than traditional DB-backed sessions.

### 3. Background Worker & Task Reliability
- **Job Queueing Layer:** Implement a Redis-backed job queue for heavy AI generation tasks to ensure they are processed reliably even if a request times out.
- **Error Recovery:** Implement automatic retries with exponential backoff for all database and Redis operations.
- **Migration Versioning:** Standardize the SQL migration workflow to ensure predictable rollouts and rollbacks.

## Non-Functional Requirements
- **Latency:** Aim for sub-100ms response times for cached data.
- **Scalability:** The infrastructure must support 100+ concurrent AI agent "thoughts" without database locking issues.
- **Security:** Zero-trust architecture between services; every DB query must be scoped by `user_id`.

## Acceptance Criteria
- [ ] All primary tables have appropriate indexes for common query paths.
- [ ] RLS policies prevent any user from accessing data outside their `workspace_id`.
- [ ] Redis caching reduces Supabase read operations for the Foundation module by >50%.
- [ ] Long-running AI tasks resume correctly after a simulated service restart.
- [ ] Multi-table updates are atomic (all-or-nothing) via SQL transactions.

## Out of Scope
- Frontend UI changes (handled in UX Polish track).
- Third-party API cost management (Vertex AI).
- Persistent file storage optimization (GCS).
