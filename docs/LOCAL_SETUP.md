# Local Setup

## Prerequisites

- Docker Desktop
- Rust 1.94+
- Node 22+
- pnpm via Corepack

## Steps

1. `corepack enable`
2. `pnpm install --frozen-lockfile`
3. Copy `.env.example` to `.env` and fill Clerk, database, Bedrock, Qdrant, Razorpay, and Sentry values.
4. Start local services: `docker compose up -d postgres pgbouncer qdrant`
5. Run migrations directly against Postgres: `sqlx migrate run --database-url $RAPTORFLOW_DIRECT_DATABASE_URL`
6. Start the app: `pnpm dev`

## Important rules

- Run migrations through `RAPTORFLOW_DIRECT_DATABASE_URL`, not PgBouncer.
- Do not use offline mock mode in the active stack.
- Auth is Clerk-only.
