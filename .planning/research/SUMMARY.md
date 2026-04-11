# Project Research Summary

**Project:** RaptorFlow
**Domain:** Marketing Intelligence / Campaign Orchestration
**Researched:** 2026-04-11
**Confidence:** MEDIUM-HIGH

## Executive Summary

RaptorFlow is an AI-native marketing intelligence and campaign orchestration platform that differentiates through multi-agent council debates, persistent memory systems, and real-time collaborative visualization. The platform aligns well with industry architecture patterns—event-driven processing, multi-tenant isolation via RLS, and polyglot backends—while using Rust (unusual but valid) for performance-critical workloads. The core stack is modern and competitive: Next.js 15 frontend, Aurora PostgreSQL 16 with pgvector, Qdrant for vector search, and Vertex AI for generative features.

Key risks center on three areas: **tenant isolation** (RLS must be applied consistently across all queries), **AI council convergence** (agents must synthesize rather than contradict), and **real-time state management** (WebSocket desynchronization erodes trust). The feature roadmap should prioritize Foundation → Campaigns → Council/Muse → Intel pipeline based on dependency analysis from ARCHITECTURE.md. Multi-user collaboration and social publishing should be deferred to v2.

## Key Findings

### Recommended Stack

**From STACK.md**

The marketing intelligence platform landscape has converged on React/Next.js frontends with polyglot backends. RaptorFlow's stack is modern and aligned with industry patterns:

| Layer     | RaptorFlow               | Industry Standard         | Assessment            |
| --------- | ------------------------ | ------------------------- | --------------------- |
| Frontend  | Next.js 15 + React 19    | Next.js 14/15 ✓           | Matches               |
| State     | Zustand + TanStack Query | Same ✓                    | Matches               |
| Backend   | Rust/Axum                | Node.js/Rails (typical)   | **Unusual but valid** |
| Database  | Aurora PG 16 + pgvector  | PostgreSQL 15/16 ✓        | Matches               |
| Vector DB | Qdrant                   | pgvector or Qdrant ✓      | Matches               |
| Cache     | DragonflyDB              | Redis/Dragonfly ✓         | Matches               |
| Queue     | AWS SQS                  | SQS or Kafka ✓            | Matches               |
| AI        | Vertex AI (Gemini)       | OpenAI/Anthropic/Gemini ✓ | Matches               |
| Auth      | Clerk                    | Clerk/Auth0 ✓             | Matches               |

**Core technologies:**

- **Next.js 15 + React 19**: Industry standard for marketing platforms with SSR/SSG for marketing pages
- **Rust/Axum backend**: Unusual in martech (typically Node.js/Rails/Go) but valid for performance-critical workloads
- **PostgreSQL 16 + pgvector**: Universal OLTP store with embedded vector support
- **Qdrant**: Dedicated vector search for RAG and similarity search at scale
- **SQS**: Event-driven job processing for decoupling inference from request handling
- **Clerk**: JWT-based auth with org_id extraction for multi-tenant isolation

### Expected Features

**From FEATURES.md**

**Must have (table stakes):**

- Campaign CRUD with moves and tasks — core workflow
- Foundation onboarding (21 screens) — brand/entity context
- Basic competitive intelligence — website monitoring minimum
- Muse conversational AI — chat-based marketing advisor
- Daily Wins briefing — proactive AI-generated insights
- Multi-tenant authentication and billing

**Should have (competitive differentiation):**

- Multi-agent council sessions — distinctive debate pattern
- PRL persistent memory — remembers client history across sessions
- Content Engine — ad copy and social captions generation
- Brand voice compliance — auto-check against guidelines
- Real-time Office canvas — AI avatar collaboration environment

**Defer (v2+):**

- Full 21-agent Council — build core 3-5 first
- EEL skill evolution — requires performance data to work
- Dynamic Replanning Engine — requires mature campaign system
- Advanced PRL (SWR consolidation) — works basic, enhance later
- Multi-user collaboration — single-user MVP first
- Social publishing — integration vs native not decided

### Architecture Approach

**From ARCHITECTURE.md**

RaptorFlow uses a **modular monolith in Rust** with 19 internal crates organized by domain. The architecture follows a clear dependency tiers:

```
Tier 1 (Foundation):     config → telemetry → db → contracts
Tier 2 (Infrastructure): auth → jobs → integrations
Tier 3 (Domain Core):    foundation → prl → muse
Tier 4 (Orchestration):  campaigns → council → intel
Tier 5 (Application):    office → billing → http → api
```

**Major components:**

1. **Foundation crate** — Brand/entity context storage, versioning, semantic scanning
2. **Campaigns crate** — Campaign lifecycle, moves, tasks, briefs, state machine
3. **Council crate** — Multi-agent debate orchestration, position tracking, synthesis
4. **Muse crate** — Conversational interface, 7-layer context routing
5. **Office crate** — Real-time canvas state, WebSocket broadcasting via DragonflyDB pub/sub
6. **PRL crate** — Predictive ripple memory, ripple/edge tracking for agent essences
7. **Intel crate** — Competitor tracking, SEO/ads monitoring, change detection

**Key patterns validated:**

- Event-driven jobs via SQS for embedding/content generation
- Multi-agent council pattern (distinctive)
- Real-time canvas via WebSocket + PixiJS (standard)
- Row-Level Security via `app.current_org_id()` + RLS (defense in depth)
- Single Rust binary with internal crate composition (simpler ops than microservices)

### Critical Pitfalls

**From PITFALLS.md**

1. **Tenant Isolation Failures** — RLS policies must be applied consistently; JOIN operations can bypass context. Prevention: `org_id` filters at connection level, tenant-specific test suites, query pattern reviews in CI/CD.

2. **AI Agent Council Divergence** — Agents produce conflicting recommendations without clear role boundaries. Prevention: Define explicit non-overlapping decision domains, implement voting/consensus mechanisms, minimum token budgets per agent.

3. **Real-Time State Desynchronization** — Office canvas shows stale state across clients. Prevention: Vector clocks for causality, operation transforms for conflict resolution, heartbeat/ping-pong for connection health.

4. **Competitor Intelligence Staleness** — Decisions based on obsolete data. Prevention: Automated change detection, freshness SLAs per data type, staleness indicators in UI.

5. **Campaign Orchestration Over-Automation** — Automated campaigns cause fatigue. Prevention: Hard frequency caps per customer per channel, timezone-aware send time optimization, "do not disturb" windows.

## Implications for Roadmap

Based on research, suggested phase structure:

### Phase 1: Foundation & Core Infrastructure

**Rationale:** All other features depend on foundation data. Build Tier 1-2 crates first (config, db, auth, jobs). Establish tenant isolation patterns before adding user data.

**Delivers:**

- Foundation onboarding completion
- PRL core (ripple/edge tracking)
- Tenant isolation validation
- EEL core (essence injection)

**Avoids:** Foundation Data Version Conflicts (implement locking, snapshots early)

### Phase 2: Campaign & Council Foundation

**Rationale:** Campaigns orchestrate foundation + council. Must establish state machine patterns and multi-agent debate infrastructure before adding intelligence features.

**Delivers:**

- Campaign CRUD with moves/tasks
- Basic Council sessions (3-5 agents)
- Muse conversational interface
- Daily Wins briefings

**Avoids:** AI Agent Council Divergence (define clear roles from start)

### Phase 3: Intelligence Pipeline & Content

**Rationale:** Intel feeds into campaigns via nudges. Content Engine depends on brand voice from foundation.

**Delivers:**

- Competitor intelligence (website, SEO, ads monitoring)
- Content Engine (ad copy, social captions)
- Brand voice compliance system
- Nudges notification system

**Avoids:** Competitor Intelligence Staleness (implement change detection early)

### Phase 4: Real-Time Collaboration & Polish

**Rationale:** Office canvas depends on all other systems. Requires stable WebSocket infrastructure.

**Delivers:**

- Office canvas with PixiJS rendering
- WebSocket presence and broadcasting
- Council visual in Office
- Basic multi-user awareness

**Avoids:** Real-Time State Desynchronization (implement version vectors, heartbeat monitoring)

### Phase 5: Advanced AI & Growth Features

**Rationale:** Skill evolution, dynamic replanning, full 21-agent council require mature base system.

**Delivers:**

- EEL skill evolution
- Dynamic Replanning Engine
- Advanced PRL (SWR consolidation)
- Multi-user collaboration

### Phase Ordering Rationale

- **Foundation first**: All features depend on brand/entity context
- **Campaigns before Intel**: Campaigns consume intelligence, not vice versa
- **Council early**: Multi-agent debate is the core differentiator, needs iteration
- **Office last**: Most complex, depends on stable API/event infrastructure
- **AI evolution last**: Requires performance data to work effectively

### Research Flags

Phases likely needing deeper research during planning:

- **Phase 3 (Intelligence Pipeline):** Legal boundaries for competitor scraping vary by jurisdiction and are evolving
- **Phase 4 (Office Canvas):** Real-time collaboration patterns well-documented, but PixiJS-specific implementation has limited references
- **Phase 5 (Advanced AI):** AI agent skill evolution is an emerging area with limited documented post-mortems

Phases with standard patterns (skip research-phase):

- **Phase 1:** Multi-tenant RLS patterns well-documented in PostgreSQL docs
- **Phase 2:** Campaign state machine patterns established in workflow orchestration domain

## Confidence Assessment

| Area         | Confidence  | Notes                                                                         |
| ------------ | ----------- | ----------------------------------------------------------------------------- |
| Stack        | HIGH        | Verified across Segment, Amplitude, Mixpanel, Braze documentation             |
| Features     | HIGH        | Confirmed against existing codebase; category patterns well-established       |
| Architecture | MEDIUM-HIGH | Directly observed from codebase; industry alignment based on general patterns |
| Pitfalls     | MEDIUM      | Emerging AI patterns (council, PRL) less documented in public sources         |

**Overall confidence:** MEDIUM-HIGH

### Gaps to Address

- **Multi-user collaboration timing:** Single-user MVP assumed, but team functionality not documented for v2
- **Social publishing strategy:** Native vs integration-only not decided
- **Content approval workflow:** Who approves before publishing not documented
- **API versioning:** No explicit strategy, but v1 prefix already in place
- **Event bus:** Implicit via SQS, consider EventBridge for cross-domain events at scale

## Sources

### Primary (HIGH confidence)

- **Segment Documentation** (segment.com/docs/) — Connection patterns, Reverse ETL
- **Braze Documentation** (braze.com/docs/) — Event streaming, SDK integration
- **RaptorFlow codebase** — Component definitions, data flows, build order
- **PostgreSQL RLS documentation** — Tenant isolation patterns

### Secondary (MEDIUM confidence)

- **Hightouch Documentation** (docs.hightouch.io) — Reverse ETL patterns
- **Mixpanel Documentation** (mixpanel.com/docs/) — Event tracking, warehousing
- **AWS Event-Driven Architecture patterns** — Scalability boundaries
- **Martin Fowler CQRS/Event Sourcing** — Architecture pattern validation

### Tertiary (LOW confidence)

- **AI Agent Council coordination** — Academic literature limited for marketing domain
- **Real-time canvas collaboration failures** — Few documented post-mortems
- **Competitor intelligence legal boundaries** — Jurisdiction-dependent, evolving

---

_Research completed: 2026-04-11_
_Ready for roadmap: yes_
