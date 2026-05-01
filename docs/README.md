# Documentation

This directory separates active operational docs from historical material.

## Active Docs

- `GETTING_STARTED.md` - first-day setup and command flow
- `LOCAL_SETUP.md` - local services, environment variables, and startup steps
- `scaffold-file-by-file.md` - practical repository map
- `canonical/stack.md` - current technology stack
- `canonical/repo-topology.md` - current monorepo layout
- `canonical/data-platform.md` - database, vector, cache, and eventing shape
- `canonical/deployment-topology.md` - production deployment shape
- `runbooks/` - deployment and operations procedures
- `prompt-contracts/` - prompt contract files validated by `pnpm docs:check`

## Historical Docs

Old phase reports, PR bodies, audit reports, PDFs, and aspirational specs live in
`docs/archive/`. Those files are preserved for context, but they are not the
source of truth for build, deploy, or runtime behavior.

## Current Stack

- Frontend: Next.js 15 App Router, Clerk, TanStack Query, Zustand, Tailwind, shadcn/ui, PixiJS
- Backend: Rust, Axum, Tokio, SQLx
- Database: PostgreSQL 16 locally, Aurora PostgreSQL 16 in production
- Pooling: PgBouncer
- Vector memory: Qdrant
- AI inference: AWS Bedrock
- TypeScript-side data tooling: Prisma 7 package in `packages/database`
- Queue/storage: SQS and S3
- Observability: Sentry, tracing, CloudWatch

Run `pnpm docs:check` to verify the source corpus and prompt-contract docs.
