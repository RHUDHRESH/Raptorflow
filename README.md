# RaptorFlow

**Marketing intelligence and campaign orchestration powered by AI agent councils.**

RaptorFlow helps marketing teams plan campaigns, generate moves, produce content,
and keep market memory attached to the work. The frontend is a Next.js app with
an Office canvas. The backend is a Rust Axum API backed by Postgres, Qdrant,
SQS, S3, and AWS Bedrock.

## Stack

| Layer         | Current choice                                                              |
| ------------- | --------------------------------------------------------------------------- |
| Frontend      | Next.js 15, TypeScript, Clerk, Zustand, TanStack Query, Tailwind, PixiJS v8 |
| Backend       | Rust, Axum 0.8, Tokio, SQLx                                                 |
| Database      | PostgreSQL 16, pgvector, PgBouncer                                          |
| Memory        | Qdrant                                                                      |
| Queue/storage | AWS SQS and S3                                                              |
| Inference     | AWS Bedrock Mistral via `crates/aws`                                        |
| Deployment    | Vercel frontend, ECS Fargate backend                                        |

## Quick Start

```bash
corepack enable
pnpm install --frozen-lockfile
pnpm setup:hooks
docker compose up -d postgres pgbouncer qdrant
pnpm dev
```

Open `http://localhost:3000`. The Rust API runs at `http://localhost:8080`.

For full local setup, use [docs/GETTING_STARTED.md](./docs/GETTING_STARTED.md)
and [docs/LOCAL_SETUP.md](./docs/LOCAL_SETUP.md).

## Repository Structure

```text
apps/web/             Next.js frontend
crates/               25 Rust crates: API, domain, infra, integrations
packages/contracts/   TypeScript contracts generated from schemas
packages/database/    Prisma 7 package for TypeScript-side database access
schemas/              JSON schema source of truth for service contracts
database/migrations/  SQL migrations for the Rust stack
infra/docker/         Local Postgres, PgBouncer, Qdrant, API, web, search stack
infra/tofu/           Production AWS infrastructure
docs/                 Active docs, ADRs, runbooks, prompt contracts
docs/archive/         Historical reports, old specs, and PR notes
scripts/              Validation, smoke checks, bootstrap, deploy helpers
```

Types that cross the frontend/backend boundary start in `schemas/`, then generate
Rust and TypeScript contract code with `pnpm contracts:sync`.

## Commands

```bash
pnpm dev              # local development
pnpm verify           # full local JS/docs/contracts/scaffold/structural/smoke check
pnpm smoke            # fast route, cron, auth, and deploy wiring check
pnpm build            # production web/contracts/database builds through Turborepo
pnpm contracts:sync   # regenerate contracts after schema changes
pnpm contracts:check  # verify generated contracts match schemas

cargo fmt --check
cargo check --workspace
```

## Rules

- `schemas/` is the contract authority.
- Run migrations through `RAPTORFLOW_DIRECT_DATABASE_URL` on port `5432`, not PgBouncer.
- `packages/contracts/dist/` and `packages/database/dist/` are generated.
- Root `vercel.json` is the only Vercel deploy config.
- `docs/archive/` is historical context, not operational truth.

## Documentation

| Guide                                                | When to read                              |
| ---------------------------------------------------- | ----------------------------------------- |
| [Getting Started](./docs/GETTING_STARTED.md)         | First-day setup and command flow          |
| [Local Setup](./docs/LOCAL_SETUP.md)                 | Local services, env vars, migration rules |
| [Repo topology](./docs/canonical/repo-topology.md)   | Current monorepo structure                |
| [Stack spec](./docs/canonical/stack.md)              | Current technology choices                |
| [Rust crates](./crates/README.md)                    | Current backend crate map                 |
| [Repository map](./docs/scaffold-file-by-file.md)    | Practical file and folder orientation     |
| [Deployment runbook](./docs/runbooks/deployments.md) | Production deploy and rollback flow       |
