# Getting Started

RaptorFlow is a pnpm + Cargo monorepo with:

- `apps/web`: Next.js frontend
- `crates/*`: Rust backend and internal services
- `packages/contracts`: shared TypeScript contracts
- `packages/database`: Prisma 7 package for TypeScript-side data access
- `schemas/`: source of truth for cross-service types
- `database/migrations/`: SQL migrations for the Rust stack

## First-Time Setup

1. `corepack enable`
2. `pnpm install --frozen-lockfile`
3. `pnpm setup:hooks`
4. Copy `.env.example` to `.env` and fill required local values, including `CRON_SECRET` if you will exercise scheduled routes.
5. `docker compose up -d postgres pgbouncer qdrant`
6. `sqlx migrate run --database-url $RAPTORFLOW_DIRECT_DATABASE_URL`
7. `pnpm dev`

The frontend runs at `http://localhost:3000`. The Rust API runs at
`http://localhost:8080`.

Local AWS writes are disabled by default with `ALLOW_LIVE_AWS_WRITES=0`.
Do not use root AWS access keys; the bootstrap guard refuses root principals and
only warns when AWS credentials or the AWS CLI are absent. Docker Compose uses
`RAPTORFLOW_LOCAL_AWS_*` variables for container AWS credentials so ordinary
host AWS variables are not forwarded by default.

## Validation

Run these before pushing changes:

```bash
pnpm verify
cargo fmt --check
cargo check --workspace
```

Use `pnpm smoke` for a fast route, cron, auth, and deploy wiring check.

## What Matters

- Auth is Clerk.
- API health is `GET /api/v1/health`; public liveness is `GET /health/live`.
- AI inference is AWS Bedrock only.
- The tenant key is `org_id`.
