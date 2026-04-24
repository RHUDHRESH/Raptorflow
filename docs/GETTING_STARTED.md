# Getting Started

This repo is a monorepo with:

- `apps/web`: Next.js frontend
- `crates/*`: Rust backend and internal services
- `packages/contracts`: shared TypeScript contracts
- `packages/database`: Prisma 7 package for TypeScript-side data access
- `schemas/`: source of truth for cross-service types
- `database/migrations/`: SQL migrations for the Rust stack

## Local bootstrap

1. `corepack enable`
2. `pnpm install --frozen-lockfile`
3. `docker compose up -d postgres pgbouncer qdrant`
4. `sqlx migrate run --database-url $RAPTORFLOW_DIRECT_DATABASE_URL`
5. `pnpm dev`

## What matters

- Auth is Clerk.
- API health is `GET /api/v1/health`.
- Public liveness is `GET /health/live`.
- AI inference is AWS Bedrock only.
- The tenant key is `org_id`.
