# Phase 1: Auth & Foundation - Research

**Phase:** 1  
**Researched:** 2026-04-11  
**Requirements:** AUTH-01, AUTH-02, AUTH-03, AUTH-04, AUTH-05, AUTH-06, FOUND-01, FOUND-02, FOUND-03, FOUND-04, FOUND-05, PRL-01, PRL-02, PRL-03, PRL-04

---

## Domain Analysis

### Authentication (Clerk-based)

- Clerk handles email/password signup, verification, password reset
- Backend needs JWT validation middleware to extract `org_id` for multi-tenancy
- Clerk webhooks (`user.created`, `user.updated`, `organizationMembership.created`) sync users/orgs to PostgreSQL
- Frontend uses `@clerk/nextjs` for SSR-compatible auth

### Multi-Tenant Isolation

- **Constraint:** All data filtered by `org_id` via PostgreSQL Row-Level Security (RLS)
- RLS policies must be defined on ALL tables that store tenant-scoped data
- `org_id` extracted from Clerk JWT and injected into request context
- Axum middleware extracts and validates JWT, populates request extensions

### Foundation Data Management

- 21-screen structured onboarding captures company information
- Foundation data includes: company_info, target_audience, value_proposition, competitive_positioning, etc.
- **Versioning:** `foundation_snapshots` table stores immutable snapshots; active snapshot referenced by `foundations.current_snapshot_id`
- **Scanning:** Quick mode (external data only) vs Deep mode (external + manual review)
- Foundation sections embeddable into campaigns via ID reference

### Predictive Ripple Memory (PRL)

- **Ripple:** An idea/action/outcome with lifecycle (created → active → realized/decayed)
- **Ripple Edge:** Directed connection between ripples (causality, support, conflict)
- **Agent Essence:** Persistent AI agent personality/memory that persists across sessions
- **Decay Policies:** Rules that age out stale ripples (e.g., unrealized ideas decay after N days)

---

## Technical Approach

### Backend Architecture (Rust/Axum)

```
raptorflow-api/
├── src/
│   ├── main.rs                 # Server entry, routes
│   ├── http/
│   │   ├── mod.rs
│   │   ├── router.rs           # Route aggregation
│   │   ├── middleware/
│   │   │   ├── mod.rs
│   │   │   ├── auth.rs         # Clerk JWT validation
│   │   │   └── tenant.rs       # org_id injection
│   │   └── routes/
│   │       ├── mod.rs
│   │       ├── health.rs
│   │       ├── auth.rs          # Clerk webhook handler
│   │       ├── foundation.rs
│   │       └── prl.rs
│   ├── auth/
│   │   ├── mod.rs
│   │   ├── clerk.rs            # Clerk API client
│   │   └── jwt.rs             # JWT parsing/validation
│   ├── db/
│   │   ├── mod.rs
│   │   ├── pool.rs             # SQLx connection pool
│   │   ├── models/             # sqlx row types
│   │   └── queries/           # Prepared statements
│   ├── foundation/
│   │   ├── mod.rs
│   │   ├── service.rs
│   │   ├── scan.rs            # Quick/deep scanning
│   │   └── versioning.rs      # Snapshot management
│   ├── prl/
│   │   ├── mod.rs
│   │   ├── ripple.rs
│   │   ├── edge.rs
│   │   ├── essence.rs
│   │   └── decay.rs           # Decay policy engine
│   └── config.rs
├── Cargo.toml
└── sqlx-data.json             # Compile-time query checking
```

### Database Schema

```sql
-- Organizations (synced from Clerk)
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clerk_org_id TEXT UNIQUE NOT NULL,
    name TEXT NOT NULL,
    slug TEXT UNIQUE NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Users (synced from Clerk)
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    clerk_user_id TEXT UNIQUE NOT NULL,
    email TEXT NOT NULL,
    name TEXT,
    org_id UUID NOT NULL REFERENCES organizations(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Foundation snapshots (immutable)
CREATE TABLE foundation_snapshots (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id),
    version INTEGER NOT NULL,
    data JSONB NOT NULL,  -- Full foundation data as JSON
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Active foundation reference
CREATE TABLE foundations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID UNIQUE NOT NULL REFERENCES organizations(id),
    current_snapshot_id UUID NOT NULL REFERENCES foundation_snapshots(id),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Ripples
CREATE TABLE ripples (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id),
    title TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'active', -- active, realized, decayed
    category TEXT,  -- idea, action, outcome
    created_by UUID REFERENCES users(id),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    realized_at TIMESTAMPTZ,
    decayed_at TIMESTAMPTZ
);

-- Ripple edges
CREATE TABLE ripple_edges (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id),
    source_ripple_id UUID NOT NULL REFERENCES ripples(id),
    target_ripple_id UUID NOT NULL REFERENCES ripples(id),
    relationship TEXT NOT NULL, -- causes, supports, conflicts, relates
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Agent essences
CREATE TABLE agent_essences (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    org_id UUID NOT NULL REFERENCES organizations(id),
    name TEXT NOT NULL,
    personality JSONB NOT NULL,
    memory JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- RLS policies (required on ALL tenant tables)
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE foundation_snapshots ENABLE ROW LEVEL SECURITY;
ALTER TABLE foundations ENABLE ROW LEVEL SECURITY;
ALTER TABLE ripples ENABLE ROW LEVEL SECURITY;
ALTER TABLE ripple_edges ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_essences ENABLE ROW LEVEL SECURITY;

-- RLS policy template
CREATE POLICY tenant_isolation ON {table}
    USING (org_id = current_setting('app.current_org_id')::UUID);
```

### Clerk Webhook Integration

1. **Endpoint:** `POST /api/v1/webhooks/clerk`
2. **Events handled:**
   - `user.created` → Insert into `users` table
   - `user.updated` → Update `users` table
   - `organization.created` → Insert into `organizations` table
   - `organizationMembership.created` → Link user to org
3. **Signature verification:** HMAC-SHA256 using Clerk signing key

### API Endpoints

| Method | Path                                        | Description                         |
| ------ | ------------------------------------------- | ----------------------------------- |
| POST   | `/api/v1/webhooks/clerk`                    | Clerk webhook handler               |
| GET    | `/api/v1/foundation`                        | Get current foundation              |
| POST   | `/api/v1/foundation`                        | Create foundation (after org setup) |
| PUT    | `/api/v1/foundation/sections/{section}`     | Update specific section             |
| POST   | `/api/v1/foundation/snapshots`              | Create snapshot                     |
| GET    | `/api/v1/foundation/snapshots`              | List snapshots                      |
| POST   | `/api/v1/foundation/snapshots/{id}/restore` | Restore snapshot                    |
| POST   | `/api/v1/foundation/scan`                   | Trigger quick/deep scan             |
| GET    | `/api/v1/ripples`                           | List ripples (filterable)           |
| POST   | `/api/v1/ripples`                           | Create ripple                       |
| GET    | `/api/v1/ripples/{id}`                      | Get ripple details                  |
| PUT    | `/api/v1/ripples/{id}`                      | Update ripple                       |
| DELETE | `/api/v1/ripples/{id}`                      | Delete ripple                       |
| GET    | `/api/v1/ripples/{id}/edges`                | Get connected ripples               |
| POST   | `/api/v1/ripples/{id}/edges`                | Create edge                         |
| DELETE | `/api/v1/ripples/edges/{id}`                | Delete edge                         |
| GET    | `/api/v1/essences`                          | List agent essences                 |
| POST   | `/api/v1/essences`                          | Create essence                      |
| GET    | `/api/v1/essences/{id}`                     | Get essence                         |
| PUT    | `/api/v1/essences/{id}`                     | Update essence                      |
| POST   | `/api/v1/prl/decay`                         | Run decay policy engine             |

---

## Frontend Architecture (Next.js 15)

```
apps/web/
├── src/
│   ├── app/
│   │   ├── (auth)/
│   │   │   ├── sign-in/[[...sign-in]]/page.tsx
│   │   │   └── sign-up/[[...sign-up]]/page.tsx
│   │   ├── (app)/
│   │   │   ├── layout.tsx           # Authenticated shell
│   │   │   ├── dashboard/page.tsx
│   │   │   ├── foundation/
│   │   │   │   ├── page.tsx         # Foundation overview
│   │   │   │   ├── onboarding/
│   │   │   │   │   └── [step]/page.tsx  # 21-screen onboarding
│   │   │   │   ├── scan/page.tsx
│   │   │   │   └── snapshots/page.tsx
│   │   │   ├── prl/
│   │   │   │   ├── page.tsx         # Ripple list
│   │   │   │   ├── [id]/page.tsx    # Ripple detail
│   │   │   │   └── canvas/page.tsx  # PRL visualization
│   │   │   └── settings/
│   │   │       └── page.tsx
│   │   └── api/
│   │       └── webhooks/
│   │           └── clerk/route.ts   # Clerk webhook handler
│   ├── components/
│   │   ├── ui/                      # shadcn/ui components
│   │   ├── foundation/
│   │   │   ├── onboarding-wizard.tsx
│   │   │   ├── foundation-editor.tsx
│   │   │   ├── snapshot-list.tsx
│   │   │   └── scan-dialog.tsx
│   │   └── prl/
│   │       ├── ripple-card.tsx
│   │       ├── ripple-graph.tsx      # D3 or similar
│   │       └── essence-editor.tsx
│   ├── lib/
│   │   ├── api.ts                   # API client
│   │   └── clerk.ts                 # Clerk client
│   └── store/
│       ├── foundation-store.ts      # Zustand
│       └── prl-store.ts
└── package.json
```

---

## Implementation Risks

| Risk                             | Severity | Mitigation                                                                 |
| -------------------------------- | -------- | -------------------------------------------------------------------------- |
| RLS performance overhead         | High     | Test with realistic data volumes; consider connection pooling optimization |
| Clerk webhook reliability        | Medium   | Implement idempotency; Clerk retries failed deliveries                     |
| Foundation versioning complexity | Medium   | Keep snapshots immutable; treat current as read-only                       |
| PRL decay scheduling             | Low      | Use DragonflyDB scheduled tasks; avoid cron dependencies                   |

---

## Patterns Established

1. **Tenant context injection:** Axum middleware extracts `org_id` from JWT, sets `app.current_org_id` PostgreSQL setting
2. **RLS everywhere:** All tenant-scoped tables have RLS enabled; no exceptions
3. **Immutable snapshots:** Foundation snapshots are write-once; restoration creates new current
4. **API versioning:** `/api/v1/` prefix for all REST endpoints
5. **Webhook signature verification:** HMAC-SHA256 on all incoming webhooks

---

## Validation Architecture

| Dimension           | What to Validate                                       |
| ------------------- | ------------------------------------------------------ |
| 1. Functional       | All 12 success criteria from roadmap                   |
| 2. Integration      | Clerk webhook → DB sync; API → DB queries              |
| 3. Tenant Isolation | Cross-tenant data access attempts blocked by RLS       |
| 4. API Contract     | All endpoints return correct status codes, shapes      |
| 5. Data Integrity   | Snapshots are immutable; restoration preserves history |
| 6. PRL Lifecycle    | Ripple state machine: active → realized/decayed        |
| 7. UI/UX            | Onboarding wizard flows through all 21 screens         |
| 8. Performance      | RLS queries use indexes; no full table scans           |

---

## Done Criteria

- [ ] Clerk JWT validation middleware extracts `org_id`
- [ ] All tenant tables have RLS policies
- [ ] Webhook handler processes `user.created` and syncs to DB
- [ ] Foundation 21-screen onboarding completes and stores data
- [ ] Foundation snapshots are immutable after creation
- [ ] Snapshot restore updates `foundations.current_snapshot_id`
- [ ] Scan endpoint accepts `quick` or `deep` mode
- [ ] Ripples CRUD operations work with RLS filtering
- [ ] Ripple edges connect ripples correctly
- [ ] Agent essences persist and can be updated
- [ ] Decay policy endpoint marks stale ripples as `decayed`
