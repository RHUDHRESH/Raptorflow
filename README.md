# RaptorFlow

**Marketing intelligence and campaign orchestration — powered by AI agent councils.**

RaptorFlow helps marketing teams build data-driven campaigns faster. An AI Strategist reviews briefs. An AI Council (12 avatars with different perspectives) debates the approach. Moves get planned, tasks get executed, content gets generated — all fed back into a memory system that makes the AI smarter over time.

The frontend is a Next.js app with a PixiJS-rendered office canvas where you can watch the AI avatars work.

---

## The stack at a glance

| Layer         | What                                                                        | Why                                                      |
| ------------- | --------------------------------------------------------------------------- | -------------------------------------------------------- |
| **Frontend**  | Next.js 15, TypeScript, Clerk, Zustand, TanStack Query, Tailwind, PixiJS v8 | Fast iteration, great DX, real-time canvas               |
| **Backend**   | Rust, Axum 0.8, Tokio, SQLx                                                 | Type safety, async performance, small memory footprint   |
| **Database**  | Aurora PostgreSQL 16, pgvector, PgBouncer                                   | ACID transactions, vector similarity, connection pooling |
| **Memory**    | Qdrant (vectors)                                                            | Fast retrieval and vector similarity                     |
| **Queue**     | AWS SQS                                                                     | Background job processing without blocking requests      |
| **Inference** | AWS Bedrock Mistral (via `crates/aws`)                                      | Mistral Large 3 (large) / Ministral 3 8B (fast)          |
| **Infra**     | ECS Fargate + Vercel                                                        | No servers to manage, scales automatically               |

---

## Quick start

```bash
corepack enable && pnpm install --frozen-lockfile && pnpm setup:hooks
docker compose up postgres pgbouncer qdrant   # terminal 1
pnpm dev                                               # terminal 2
```

Open **http://localhost:3000**. The API runs at **http://localhost:8080**.

Full setup guide: **[docs/GETTING_STARTED.md](./docs/GETTING_STARTED.md)**

For local development, use **[docs/LOCAL_SETUP.md](./docs/LOCAL_SETUP.md)** and set the Clerk, database, Bedrock, and S3/SQS variables described there.

---

## Repository structure

```
apps/web/               Next.js frontend
crates/                 27 Rust crates (API server + all services)
packages/contracts/      TypeScript types (generated from schemas/)
schemas/                JSON schemas — the API contract source of truth
database/migrations/    PostgreSQL schema
infra/docker/           Local dev stack (Postgres, PgBouncer, Qdrant)
infra/tofu/             Production AWS infrastructure (ECS, Aurora, S3)
docs/                   Canonical specs, ADRs, runbooks, prompt contracts
scripts/                Pre-commit hooks, contract sync, scaffold validation
```

The single most important pattern: **types that cross the frontend↔backend boundary start as JSON schemas in `schemas/`, then generate both Rust and TypeScript types via `pnpm contracts:sync`.**

---

## Key commands

```bash
# Start everything
pnpm dev

# Validation (runs automatically on commit via pre-commit hooks)
pnpm lint-staged        # lint + typecheck + docs checks

# Contract management
pnpm contracts:sync     # schema → Rust + TypeScript
pnpm contracts:check   # verify code matches schemas

# Rust
cargo check --workspace
cargo test -p raptorflow-eel   # avatar system tests (11 tests)
```

---

## Important rules

**`schemas/` is the authority.** Rust and TypeScript types are generated from it. Never write types by hand where a schema should be.

**Migrations: port 5432 only.** Use `RAPTORFLOW_DIRECT_DATABASE_URL` for `sqlx migrate run`. PgBouncer (port 6432) is transaction-mode only — it breaks DDL.

**`packages/contracts/dist/` is generated.** Edit schemas, not this directory.

**`infra/tofu/` is production infrastructure.** Changes here apply to real AWS resources.

---

## Documentation

| Guide                                                        | When to read                                  |
| ------------------------------------------------------------ | --------------------------------------------- |
| [Getting Started](./docs/GETTING_STARTED.md)                 | First day — setup, orientation, core patterns |
| [Repo topology](./docs/canonical/repo-topology.md)           | Understanding why the structure is this way   |
| [Stack spec](./docs/canonical/stack.md)                      | Why each technology was chosen                |
| [All 27 crates](./crates/README.md)                          | Deep dive on the Rust backend                 |
| [Scaffold reference](./docs/scaffold-file-by-file.md)        | "What is this file?" — exhaustive             |
| [Decision register](./docs/canonical/decision-register.json) | Every major decision, machine-readable        |
