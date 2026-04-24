# Documentation

Use the current-stack docs below.

## Start here

- `GETTING_STARTED.md`
- `LOCAL_SETUP.md`
- `canonical/stack.md`
- `canonical/repo-topology.md`
- `canonical/data-platform.md`
- `canonical/deployment-topology.md`

## Current stack

- Frontend: Next.js 15 App Router, Clerk, TanStack Query, Zustand, Tailwind, shadcn/ui, PixiJS
- Backend: Rust, Axum, Tokio, SQLx
- Database: Aurora PostgreSQL 16 + PgBouncer
- Vector: Qdrant
- AI: AWS Bedrock only
- Cache/query acceleration: Prisma Accelerate
- Realtime DB events: Prisma Pulse
- Payments: Razorpay
- Observability: Sentry, tracing, CloudWatch

## Notes

- `LOCAL_MODE.md` is removed from the active setup.
- Old removed-provider references should not appear in active operational docs.
