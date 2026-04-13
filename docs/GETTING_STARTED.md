# Getting Started with RaptorFlow

**From zero to oriented in 10 minutes.**

This guide assumes you're a competent developer who's never seen this codebase. By the end, you'll know where to put your code, how to run the stack, and why it's arranged the way it is.

---

## What RaptorFlow actually does

Before anything else — understand the product.

RaptorFlow is a **marketing intelligence platform** that helps teams build campaigns faster using AI. Here's the core loop:

```
Marketing brief
    ↓
AI Strategist reviews the brief (foundation data)
    ↓
AI Council debates the approach (12 avatars, different perspectives)
    ↓
Consensus synthesized → Campaign created
    ↓
Moves planned → Tasks executed → Content generated
    ↓
Results fed back into the AI memory system (PRL)
```

The **office canvas** is the UI — a PixiJS-rendered room where AI avatars represent different strategic roles. It's both a visualization and a debug surface: you can see what each AI agent is "thinking" based on their position in the room.

The **Rust backend** does all the heavy lifting: API routing, database access, AI inference calls (Gemini via GCP), SQS job queues, WebSocket coordination, and the PRL memory system.

The **Next.js frontend** is a standard React app that calls the Rust API.

---

## The directory structure in one page

```
apps/                  ← Next.js frontend (UI, routes, components)
    └── web/

crates/                ← Rust backend (27 crates — API + all services)
    ├── api/           ← The binary that starts the server
    ├── http/          ← Axum router — mounts all route modules
    ├── auth/          ← Clerk JWT validation
    ├── db/            ← SQLx database access
    ├── config/         ← All environment variables
    ├── contracts/     ← Shared domain types (THE most important crate)
    ├── avatars/       ← 21 AI avatar templates
    ├── eel/           ← Avatar registry + context enrichment
    ├── harness/       ← Session management + context assembly
    ├── foundation/     ← Foundation data (the 21 screens of brand context)
    ├── campaigns/      ← Campaign → Move → Task workflow
    ├── council/       ← Multi-agent debate sessions
    ├── prl/           ← Predictive Ripple Memory (AI memory system)
    └── [18 more...]   ← Jobs, queues, cache, telemetry, etc.

packages/
    └── contracts/     ← TypeScript types (generated from schemas/)

schemas/               ← JSON schemas — THE SOURCE OF TRUTH for all domain types
    ├── domain/        ← Campaign, Nudge, IntelAlert, etc.
    ├── queues/        ← SQS job messages
    └── ws/            ← WebSocket events

database/
    └── migrations/    ← PostgreSQL schema (the only migration directory)

infra/
    ├── docker/        ← Local dev: Postgres, PgBouncer, Dragonfly, Qdrant
    └── tofu/          ← Production: AWS ECS, Aurora, VPC (OpenTofu)

docs/                  ← Architecture decisions, runbooks, prompt contracts
scripts/               ← Validation helpers (pre-commit hooks, contract sync)
```

**The three rules to never forget:**

1. **Types that cross service boundaries start in `schemas/`** — not in Rust, not in TypeScript
2. **Migrations live in `database/migrations/`** — nowhere else
3. **Every query, cache key, and queue message includes `org_id`** — tenant isolation is not optional

---

## Setup (10 minutes)

### Prerequisites

- **Docker Desktop** (or OrbStack on macOS) — running
- **Rust 1.94** — `rustup install 1.94 && rustup default 1.94`
- **Node 22** — via `nvm` or fnm

### Step 1 — install dependencies

```bash
# Use the pinned pnpm version (not your system npm)
corepack enable

# Install everything (takes ~2-3 minutes first time)
pnpm install --frozen-lockfile

# Set up git hooks (from repo root — not inside a crate)
pnpm setup:hooks
```

The `setup:hooks` step links `.githooks/pre-commit`. After this, every `git commit` automatically runs lint + docs checks. If a check fails, the commit is rejected.

### Step 2 — start the databases

```bash
docker compose up postgres pgbouncer dragonfly qdrant
```

This starts four containers: PostgreSQL (with pgvector), PgBouncer (connection pooler), DragonflyDB (cache), and Qdrant (vector search). Takes ~30 seconds.

### Step 3 — start the app

In a new terminal:

```bash
pnpm dev
```

This runs the Next.js frontend (`localhost:3000`) and the Rust API (`localhost:8080`) concurrently. The first run takes ~2 minutes to compile Rust.

When you see `Application listening on 0.0.0.0:8080`, it's ready. Open `http://localhost:3000`.

### Step 4 — verify it works

The home page should load without errors. The API health check:

```bash
curl http://localhost:8080/health
```

Should return `200 OK`.

---

## The schemas-to-code flow (critical)

This is the most important architectural pattern in the entire codebase.

```
schemas/domain/campaign.json   ← You write the schema here
         ↓
pnpm contracts:sync            ← Run this after any schema change
         ↓
crates/contracts/src/lib.rs    ← Rust types GENERATED from the schema
packages/contracts/src/        ← TypeScript types GENERATED from the schema
         ↓
apps/web/ uses them            ← Frontend and backend always agree on types
```

**Why this matters:** The frontend (TypeScript) and backend (Rust) can be on different release cycles. The schema is the contract between them. As long as the schema hasn't changed, a new frontend build won't break against an old backend, and vice versa.

**The rule:** If a type crosses the frontend↔backend boundary, it MUST start as a JSON schema. If you're adding a type that only the Rust backend uses (never sent to the frontend), you can add it directly to `crates/contracts/src/lib.rs`.

### Example: adding a new domain type

**1. Write the schema:**

```json
// schemas/domain/my-entity.json
{
  "$schema": "https://json-schema.org/draft/2020-12/schema",
  "$id": "https://raptorflow.dev/schemas/domain/my-entity.json",
  "title": "MyEntity",
  "type": "object",
  "required": ["org_id", "name"],
  "properties": {
    "org_id": { "type": "string", "format": "uuid" },
    "name": { "type": "string" }
  }
}
```

**2. Generate code:**

```bash
pnpm contracts:sync
```

**3. Use it:**

```rust
// Rust
use raptorflow_contracts::MyEntity;
```

```typescript
// TypeScript
import type { MyEntity } from "@raptorflow/contracts";
```

**4. Verify:**

```bash
pnpm contracts:check
```

---

## Common tasks

### Adding a database migration

```bash
# 1. Write the migration
# Edit database/migrations/000X_name.sql

# 2. Run it (connects to PostgreSQL DIRECTLY — port 5432)
sqlx migrate run
```

> ⚠️ **Never route migrations through PgBouncer (port 6432).** PgBouncer is in transaction mode — it silently drops `CREATE EXTENSION` and DDL statements. Always use `RAPTORFLOW_DIRECT_DATABASE_URL` for migrations.

### Adding an API route

1. Add the route handler to the relevant domain crate (e.g. `crates/campaigns/src/lib.rs`)
2. Mount it in the router (`crates/http/src/lib.rs`)
3. If it's a new domain type, add the JSON schema first (above)

### Running tests

```bash
# Frontend
pnpm test

# Core Rust (avatars + EEL — 11 tests)
cargo test -p raptorflow-eel

# Full Rust workspace (excludes testing crate on Windows due to AWS SDK linking)
cargo test --workspace --exclude raptorflow-testing

# One specific crate
cargo test -p raptorflow-harness
```

### Adding a background job

1. Add the job type to `crates/jobs/src/lib.rs` in the `registry()` function
2. Implement the handler (currently all return `accepted` — stubs)
3. Wire it into the SQS consumer in the `api` binary

### Adding a prompt contract

Prompts live in `docs/prompt-contracts/`. Each file is a structured contract that defines the input schema, output schema, and behavioral expectations for one AI model call. See `council-position.md` for a good example.

---

## Navigating the codebase

| You want to...                        | Go here                                                        |
| ------------------------------------- | -------------------------------------------------------------- |
| Understand what a specific crate does | `crates/<name>/src/lib.rs` — all crates have module-level docs |
| See the router structure              | `crates/http/src/lib.rs`                                       |
| Understand the avatar system          | `crates/avatars/src/lib.rs` + `crates/eel/src/lib.rs`          |
| Find the database schema              | `database/migrations/`                                         |
| Understand the PRL memory system      | `crates/prl/src/lib.rs`                                        |
| See how AI inference works            | `crates/gcp/src/lib.rs`                                        |
| Understand office canvas events       | `crates/office/src/lib.rs`                                     |
| See all environment variables         | `crates/config/src/lib.rs`                                     |

---

## Troubleshooting

**`pnpm dev` fails with "Cannot connect to Docker"**
→ Docker Desktop isn't running. Start it and try again.

**`sqlx migrate run` fails with "relation does not exist"**
→ You're connected through PgBouncer. Use `RAPTORFLOW_DIRECT_DATABASE_URL` pointing to `localhost:5432`, not `localhost:6432`.

**Rust compilation is very slow**
→ The `cargo-target/` volume isn't mounted. Rebuild: `docker compose up --build api`. Or run Rust locally with `cargo run -p raptorflow-api`.

**Frontend shows "Failed to fetch" errors**
→ The Rust API isn't running. `pnpm dev` should have started it. Check `localhost:8080/health` directly.

**`pnpm contracts:sync` doesn't generate types**
→ The schema has an error. Check the output for validation errors. Common issue: `$id` doesn't match the filename pattern.

---

## After your first session

You've run the stack, understood the directory structure, and seen the schemas-to-code flow. Here's what to explore next:

1. **Read `crates/README.md`** — understand all 27 crates and the dependency graph
2. **Read `crates/contracts/src/lib.rs`** — see every domain type in the system
3. **Pick a `/// STUB` or `/// TODO` in any crate** — trace back to understand how the pieces connect
4. **Read `docs/canonical/repo-topology.md`** — understand the "why" behind the structure
