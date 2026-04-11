# RaptorFlow

## What This Is

RaptorFlow is a marketing intelligence and campaign orchestration platform that combines AI agents, real-time collaboration features, and automated content generation. The system enables marketing teams to create campaigns through multi-agent council debates, manage foundation data, track competitor intelligence, and collaborate in real-time through an AI avatar-powered office canvas.

## Core Value

Organizations can launch data-driven marketing campaigns faster by leveraging AI agent councils that debate and synthesize strategy, with real-time visualization through an interactive office canvas where AI avatars represent different strategic perspectives.

## Requirements

### Validated

- ✓ Multi-tenant authentication via Clerk JWT with org_id extraction — existing
- ✓ Tenant isolation via PostgreSQL Row-Level Security — existing
- ✓ Campaign CRUD with moves and tasks — existing
- ✓ Multi-agent council sessions with position tracking and synthesis — existing
- ✓ Foundation snapshot management with version control — existing
- ✓ Muse conversational AI interface with message persistence — existing
- ✓ Competitor intelligence tracking (snapshots, SEO, ads) — existing
- ✓ Real-time Office canvas with PixiJS and WebSocket broadcasting — existing
- ✓ Predictive Ripple Memory (PRL) with ripple/edge tracking — existing
- ✓ PhonePe payment integration with subscription management — existing
- ✓ File uploads via S3 — existing
- ✓ Background job processing via SQS — existing

### Active

(None yet — ship to validate)

### Out of Scope

- Mobile application — Web-first, mobile deferred
- Real-time chat between users — Office canvas is for AI collaboration, not user chat
- Video content support — Storage/bandwidth costs, defer to future
- OAuth social login — Email/password via Clerk sufficient for v1

## Context

### Technical Environment

- **Monorepo**: pnpm workspaces + Turborepo (frontend) and Cargo workspaces (backend)
- **Frontend**: Next.js 15 with App Router, React 19, Zustand, TanStack Query
- **Backend**: Rust 1.94 with Axum 0.8, single deployable binary
- **Database**: Aurora PostgreSQL 16 with pgvector, PgBouncer connection pooling
- **Cache/PubSub**: DragonflyDB (Redis-compatible)
- **Vector Search**: Qdrant 1.13.6
- **AI**: Vertex AI (Gemini Pro for strategist, Flash-Lite for council)
- **Infrastructure**: AWS ECS Fargate, Vercel frontend, OpenTofu IaC

### Existing Architecture

- **19 Rust crates** organized by domain (auth, campaigns, council, foundation, muse, intel, office, prl, billing, etc.)
- **REST API** at `/api/v1/{foundation,campaigns,council,muse,intel,billing,office,uploads}`
- **WebSocket** for real-time session, council, and office events
- **SQS queues** for embedding and content pregeneration jobs

### Database Schema

7 migrations covering: organizations/users, foundation data, campaigns/moves/tasks, council sessions, PRL (ripples/edges), muse conversations, intel/tracking, billing, and nudges.

## Constraints

- **Tech**: Rust 1.94+ required for backend — why: Type safety, performance
- **Multi-tenancy**: All data must be filtered by org_id via RLS — why: Tenant isolation is non-negotiable
- **AI Provider**: Vertex AI only — why: Context caching for cost optimization
- **Payments**: PhonePe only (India market) — why: Local payment provider

## Key Decisions

| Decision                                | Rationale                                          | Outcome |
| --------------------------------------- | -------------------------------------------------- | ------- |
| Single Rust binary with internal crates | Simplifies deployment, allows type sharing         | ✓ Good  |
| PixiJS for Office canvas                | High-performance 2D rendering for agent animations | ✓ Good  |
| Row-Level Security for tenant isolation | Defense in depth, centralized policy               | ✓ Good  |
| SQS for background jobs                 | Decouples inference from request handling          | ✓ Good  |
| Clerk for authentication                | Complete auth infrastructure with webhook support  | ✓ Good  |

## Evolution

This document evolves at phase transitions and milestone boundaries.

**After each phase transition** (via `/gsd-transition`):

1. Requirements invalidated? → Move to Out of Scope with reason
2. Requirements validated? → Move to Validated with phase reference
3. New requirements emerged? → Add to Active
4. Decisions to log? → Add to Key Decisions
5. "What This Is" still accurate? → Update if drifted

**After each milestone** (via `/gsd-complete-milestone`):

1. Full review of all sections
2. Core Value check — still the right priority?
3. Audit Out of Scope — reasons still valid?
4. Update Context with current state

---

_Last updated: 2026-04-11 after initial documentation from existing codebase_
