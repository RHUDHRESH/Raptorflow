# Local Setup

## Prerequisites

- Docker Desktop
- Node 22 with Corepack
- pnpm 10.33.0
- Rust 1.94.0 from `rust-toolchain.toml`
- `sqlx-cli` for local database migrations

## Environment

1. Copy `.env.example` to `.env`.
2. Fill Clerk, Bedrock, Qdrant, S3/SQS, Resend, Razorpay, Sentry, and `CRON_SECRET` values as needed.
3. For frontend-only work, copy `apps/web/.env.example` to `apps/web/.env.local`.

Never commit `.env`, `.env.local`, Playwright auth state, test results, or local
logs.

Local AWS writes are opt-in. Keep `ALLOW_LIVE_AWS_WRITES=0` unless you are
intentionally testing live S3/SQS behavior with a least-privileged IAM principal.
Root AWS principals are refused by `scripts/guard-aws-root.mjs`; missing AWS
credentials or a missing AWS CLI only produce a local warning.

Docker Compose does not forward `AWS_ACCESS_KEY_ID` or
`AWS_SECRET_ACCESS_KEY`. If a local container must call AWS, set the
`RAPTORFLOW_LOCAL_AWS_*` variables in `.env` and keep
`ALLOW_LIVE_AWS_WRITES=0` unless live S3/SQS writes are the test target.

## Services

```bash
docker compose up -d postgres pgbouncer qdrant
sqlx migrate run --database-url $RAPTORFLOW_DIRECT_DATABASE_URL
pnpm dev
```

Use PgBouncer on port `6432` for runtime traffic. Run migrations against direct
Postgres on port `5432`.

## Checks

```bash
pnpm verify
docker compose config
cargo check --workspace
```

`pnpm smoke` is the fast local wiring check. It verifies navigation route files,
cron route files, auth middleware markers, and the root Vercel config.

## Active Rules

- Auth is Clerk-only.
- AI inference is AWS Bedrock only.
- There is no active offline mock mode.
- `schemas/` is the contract source of truth.
