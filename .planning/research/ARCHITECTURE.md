# Architecture Research: Marketing Intelligence & Campaign Orchestration

**Domain:** Marketing Intelligence / Campaign Orchestration Platforms  
**Researched:** 2026-04-11  
**Confidence:** MEDIUM-HIGH  
**Sources:** Existing RaptorFlow codebase analysis + industry architecture patterns

---

## Executive Summary

Marketing intelligence and campaign orchestration platforms share common architectural patterns despite surface-level differences. These systems typically combine **event-driven orchestration**, **multi-agent collaboration**, **real-time state management**, and **analytics/intel gathering**. RaptorFlow's architecture aligns well with industry patterns, with its Rust-based monorepo, event-driven job processing, and clear domain separation being structurally sound for the domain.

---

## Industry Architecture Patterns

### Marketing Intelligence Platform Architecture

Marketing intelligence platforms typically follow a **layered event-driven architecture**:

| Layer             | Responsibility                                     | Industry Pattern                   |
| ----------------- | -------------------------------------------------- | ---------------------------------- |
| **Ingestion**     | Data collection from competitors, SEO, ads, market | Batch + real-time hybrid           |
| **Processing**    | Transformation, enrichment, embedding              | Stream processing or job queues    |
| **Storage**       | Analytics data, time-series, vectors               | Multi-model (SQL + Vector + Cache) |
| **Orchestration** | Campaign workflows, agent coordination             | Event-driven with sagas            |
| **Presentation**  | Dashboards, real-time collaboration                | WebSocket + CDN                    |

**Key Insight:** Marketing intelligence systems are inherently _event-heavy_ — intelligence changes, competitor moves, market shifts all emit events that must propagate to campaigns, alerts, and dashboards.

### Campaign Orchestration Platform Architecture

Campaign orchestration extends this with **workflow orchestration** patterns:

| Component      | Purpose                             | Common Implementation          |
| -------------- | ----------------------------------- | ------------------------------ |
| **Foundation** | Brand/entity context                | Versioned document store       |
| **Campaign**   | Strategic container for initiatives | State machine                  |
| **Move**       | Discrete action within campaign     | Workflow step                  |
| **Task**       | Atomic execution unit               | Job/background task            |
| **Council**    | Multi-agent decision making         | Consensus/debate orchestration |
| **Brief**      | Generated output/artifacts          | Template + AI generation       |

**Key Pattern:** The _campaign council pattern_ — where multiple AI agents with different perspectives debate and synthesize strategy — is a distinctive pattern seen in advanced orchestration platforms. This requires long-running session state, position tracking, and synthesis algorithms.

---

## RaptorFlow Architecture Assessment

### Component Map

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              FRONTEND (Next.js 15)                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────┐│
│  │ Marketing   │  │ App Shell   │  │ Office      │  │ API Integration     ││
│  │ (RSC)       │  │ (Client)    │  │ Canvas      │  │ (TanStack Query)    ││
│  └─────────────┘  └─────────────┘  └─────────────┘  └─────────────────────┘│
└─────────────────────────────────────────────────────────────────────────────┘
                                      │ REST + WebSocket
                                      ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                           BACKEND (Rust 1.94 + Axum 0.8)                    │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                        HTTP Layer (crates/http)                       │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────────────┐ │  │
│  │  │Auth     │ │Foundation│ │Campaigns│ │Council  │ │Office/Billing   │ │  │
│  │  │Middleware│ │Routes   │ │Routes   │ │Routes   │ │Routes           │ │  │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────────────┘ │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                         Domain Crates                                  │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────────────┐ │  │
│  │  │Foundation│ │Campaigns│ │Council  │ │Muse     │ │Intel            │ │  │
│  │  │(Data)    │ │(State)  │ │(Debate) │ │(Chat)   │ │(Competitor)     │ │  │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────────────┘ │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────────────────────────┐ │  │
│  │  │Office   │ │PRL      │ │Billing  │ │Integrations                │ │  │
│  │  │(Canvas) │ │(Memory) │ │(PhonePe)│ │(S3/SQS/Vertex)             │ │  │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
│                                                                             │
│  ┌───────────────────────────────────────────────────────────────────────┐  │
│  │                      Infrastructure Crates                            │  │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────────────┐ │  │
│  │  │DB       │ │Config   │ │Jobs     │ │Telemetry│ │Auth             │ │  │
│  │  │(SQLx)   │ │(Env)    │ │(SQS)    │ │(Tracing)│ │(Clerk JWT)      │ │  │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘ └─────────────────┘ │  │
│  └───────────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────────┘
                                      │
         ┌────────────────────────────┼────────────────────────────┐
         ▼                            ▼                            ▼
┌─────────────────┐        ┌─────────────────┐        ┌─────────────────┐
│   Aurora PG     │        │   DragonflyDB   │        │    Qdrant       │
│   (SQL + RLS)   │        │   (Cache/Pub)   │        │   (Vectors)     │
└─────────────────┘        └─────────────────┘        └─────────────────┘
         │                            │
         └────────────┬───────────────┘
                      ▼
              ┌─────────────────┐
              │      SQS        │
              │   (Jobs)        │
              └─────────────────┘
```

### Component Responsibilities

| Component        | Responsibility                                          | Boundary          | Communicates With    |
| ---------------- | ------------------------------------------------------- | ----------------- | -------------------- |
| **Frontend**     | UI rendering, user interaction, real-time canvas        | Browser           | API (REST/WebSocket) |
| **HTTP Layer**   | Route dispatch, middleware chain, WebSocket upgrade     | API boundary      | All domain crates    |
| **Auth**         | JWT validation, org_id extraction, webhook verification | Security boundary | HTTP layer, Clerk    |
| **Foundation**   | Brand/entity context storage, versioning, scanning      | Domain            | DB, Qdrant           |
| **Campaigns**    | Campaign lifecycle, moves, tasks, briefs                | Domain            | DB, Jobs, Council    |
| **Council**      | Multi-agent debate orchestration, synthesis             | Domain            | DB, Muse, Vertex AI  |
| **Muse**         | Conversational interface, message persistence           | Domain            | DB, Foundation       |
| **Intel**        | Competitor tracking, SEO/ads monitoring                 | Domain            | DB, Integrations     |
| **Office**       | Real-time canvas state, event broadcasting              | Domain            | DragonflyDB (Pub)    |
| **PRL**          | Predictive ripple memory, agent essences                | Domain            | DB, Qdrant           |
| **Billing**      | Subscription management, payment processing             | Domain            | DB, PhonePe          |
| **Integrations** | S3 uploads, SQS jobs, Vertex AI calls                   | External boundary | Foundation, Jobs     |
| **Jobs**         | Background task registry, embedding/content generation  | Async             | SQS, Integrations    |
| **DB**           | Connection pooling, SQLx operations, migrations         | Data boundary     | PostgreSQL           |
| **Config**       | Environment variable management                         | Runtime           | All crates           |

---

## Data Flow

### Primary Flow: Campaign Creation

```
User Request
      │
      ▼
┌─────────────────────────────────────────────────────────────────┐
│                     TENANT ISOLATION FLOW                        │
│  Clerk JWT ──▶ Auth Middleware ──▶ Extract org_id ──▶ RLS Policy │
└─────────────────────────────────────────────────────────────────┘
      │
      ▼
┌─────────────────────────────────────────────────────────────────┐
│                   CAMPAIGN CREATION FLOW                         │
│                                                                  │
│  POST /api/v1/campaigns                                          │
│       │                                                          │
│       ▼                                                          │
│  Foundation Context ◀─────────────────────────────────────────▶ Qdrant
│       │                              (semantic search)            │
│       ▼                                                          │
│  Council Session Initiated ────────────────────────────────────▶ SQS
│       │                                        (embedding job)    │
│       ▼                                                          │
│  Multi-Agent Debate ───────────────────────────────────────────▶ Vertex AI
│       │ (Gemini Flash-Lite)     (council positions)             │
│       ▼                                                          │
│  Synthesis Generated ────────────────────────────────────────▶ Vertex AI
│       │ (Gemini Pro)             (final brief)                   │
│       ▼                                                          │
│  Moves/Tasks Created ◀───────────────────────────────────────── DB
│       │                                                         │
│       ▼                                                         │
│  Content Pregeneration ◀─────────────────────────────────────▶ SQS
│       │                                                         │
│       ▼                                                         │
│  Daily Wins Brief ◀──────────────────────────────────────────── DB
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Secondary Flow: Real-time Office Canvas

```
┌─────────────────────────────────────────────────────────────────┐
│                    REAL-TIME CANVAS FLOW                         │
│                                                                  │
│  Browser (PixiJS) ◀─────── WebSocket ────────▶ Axum Handler     │
│       │                                            │             │
│       │                                            ▼             │
│       │                                   ┌──────────────┐        │
│       │                                   │ Office Crate│        │
│       │                                   │ (Broadcast) │        │
│       │                                   └──────┬───────┘        │
│       │                                          │               │
│       │                    DragonflyDB ◀────────┘               │
│       │                      (Pub/Sub)                          │
│       │                         │                               │
│       │                         ▼                               │
│       │                   All Connected                          │
│       │                   Browser Clients                       │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Intel Collection Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                    COMPETITOR INTEL FLOW                        │
│                                                                  │
│  Scheduled Job ──▶ Intel Crate ──▶ Vertex AI ──▶ Embeddings   │
│       │                                    │                    │
│       │                                    ▼                    │
│       │                              Qdrant (store)             │
│       │                                                       │
│       ▼                                                       │
│  Alert Generation ◀─── Semantic Search ◀───────────────────── DB
│       │                                                       │
│       ▼                                                       │
│  Nudge Notification ◀─────────────────────────────────────── DragonflyDB
│       │                                                       │
│       ▼                                                       │
│  User Dashboard                                                │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## Build Order for Rust Crates

Based on dependency analysis:

### Tier 1: Foundation (No internal dependencies)

```
crates/config ──▶ crates/telemetry ──▶ crates/db ──▶ crates/contracts
```

| Crate       | Reason                           |
| ----------- | -------------------------------- |
| `config`    | All crates need configuration    |
| `telemetry` | Logging/tracing setup            |
| `db`        | Database access needed by domain |
| `contracts` | Shared types                     |

### Tier 2: Infrastructure (Depends on Tier 1)

```
crates/auth ──▶ crates/jobs ──▶ crates/integrations
```

| Crate          | Reason                              |
| -------------- | ----------------------------------- |
| `auth`         | Depends on config, db               |
| `jobs`         | Depends on config, db, integrations |
| `integrations` | Depends on config                   |

### Tier 3: Domain Core (Depends on Tier 1-2)

```
crates/foundation ──▶ crates/prl ──▶ crates/muse
```

| Crate        | Reason                                     |
| ------------ | ------------------------------------------ |
| `foundation` | Base domain entity                         |
| `prl`        | Depends on foundation, db                  |
| `muse`       | Chat interface, depends on foundation, prl |

### Tier 4: Domain Orchestration (Depends on Tier 1-3)

```
crates/campaigns ──▶ crates/council ──▶ crates/intel
```

| Crate       | Reason                            |
| ----------- | --------------------------------- |
| `campaigns` | Orchestrates foundation + council |
| `council`   | Multi-agent debates               |
| `intel`     | Competitor intelligence           |

### Tier 5: Application (Depends on Tier 1-4)

```
crates/office ──▶ crates/billing ──▶ crates/http ──▶ crates/api
```

| Crate     | Reason                                   |
| --------- | ---------------------------------------- |
| `office`  | Canvas, depends on office-related crates |
| `billing` | Payments                                 |
| `http`    | Routes all domain crates                 |
| `api`     | Entry point, combines all                |

**Build command:** `cargo build --workspace` (Turborepo handles topological ordering)

---

## Scalability Boundaries

| Component       | At 100 Users           | At 1,000 Users                       | At 10,000 Users                                        |
| --------------- | ---------------------- | ------------------------------------ | ------------------------------------------------------ |
| **PostgreSQL**  | Single Aurora instance | Aurora read replica                  | PgBouncer transaction pooling + sharding consideration |
| **DragonflyDB** | Single instance        | Multi-AZ for HA                      | Cluster mode for pub/sub fanout                        |
| **Qdrant**      | Single collection      | Collection per tenant or namespacing | Vector index partitioning                              |
| **SQS**         | Single queue           | Queue per job type                   | Dead letter queues + DLQ recycling                     |
| **ECS**         | Single task            | Auto-scaling based on queue depth    | Blue/green deployments                                 |
| **Next.js**     | Vercel hobby           | Vercel pro                           | Vercel enterprise + edge caching                       |

---

## Key Architectural Decisions Validated

| Decision                    | Industry Pattern              | RaptorFlow Implementation          | Assessment              |
| --------------------------- | ----------------------------- | ---------------------------------- | ----------------------- |
| **Event-driven jobs**       | Standard (SQS/EventBridge)    | SQS for embeddings + content gen   | ✓ Aligned               |
| **Multi-agent council**     | Distinctive (debate pattern)  | Rust crate with position tracking  | ✓ Aligned               |
| **Real-time canvas**        | Standard (WebSocket + PixiJS) | Office crate + DragonflyDB pub/sub | ✓ Aligned               |
| **Row-Level Security**      | Defense in depth              | `app.current_org_id()` + RLS       | ✓ Aligned               |
| **Single Rust binary**      | Microservices alternative     | 19 crates composed into one binary | ✓ Aligned (simpler ops) |
| **pgvector for embeddings** | Standard                      | Migration 0005                     | ✓ Aligned               |

---

## Gap Analysis

### Strengths

1. **Clean crate boundaries** — Domain separation is clear
2. **Explicit data flows** — Documented in ARCHITECTURE.md
3. **Multi-tenant isolation** — RLS is defense in depth
4. **Event-driven job processing** — SQS decouples inference

### Potential Gaps

| Gap                                            | Risk                              | Mitigation                                     |
| ---------------------------------------------- | --------------------------------- | ---------------------------------------------- |
| **No API versioning strategy**                 | Breaking changes hard to manage   | Consider URL versioning (v1 already)           |
| **Single write DB**                            | Aurora writer bottleneck          | Read replicas at scale                         |
| **No explicit event bus**                      | Implicit via SQS                  | Consider EventBridge for cross-domain events   |
| **PRL decay not tunable per tenant**           | May need tenant-specific policies | Add `decay_config` to organizations table      |
| **Office canvas state in-memory per instance** | State not shared across ECS tasks | Uses DragonflyDB pub/sub (already distributed) |

---

## Sources

- **Primary:** RaptorFlow codebase analysis (`.planning/codebase/ARCHITECTURE.md`, `.planning/codebase/COMPONENTS.md`)
- **Industry:** AWS Event-Driven Architecture patterns (aws.amazon.com/event-driven-architecture/)
- **Domain:** Akeneo PIM architecture (Product Information Management patterns)
- **Validation:** Martin Fowler CQRS/Event Sourcing patterns

---

## Confidence Assessment

| Area                        | Confidence | Notes                                                         |
| --------------------------- | ---------- | ------------------------------------------------------------- |
| Component definitions       | HIGH       | Directly observed from codebase                               |
| Data flow                   | HIGH       | Explicitly documented + code verified                         |
| Build order                 | MEDIUM     | Topological sort from Cargo.toml dependencies                 |
| Industry alignment          | MEDIUM     | Patterns from general architecture docs, not MarTech-specific |
| Scalability recommendations | MEDIUM     | Based on AWS best practices, not measured                     |
