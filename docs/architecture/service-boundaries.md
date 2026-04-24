# Service Boundaries

## Backend

- `crates/api` owns process startup and routing.
- `crates/http` owns Axum HTTP wiring.
- `crates/auth` owns Clerk JWT validation.
- `crates/db` owns SQLx access.
- `crates/aws` owns AWS Bedrock and S3 helpers.

## Frontend

- `apps/web` owns the Next.js App Router, Clerk provider, and typed API hooks.
- `packages/contracts` owns shared TypeScript contracts.
- `packages/database` owns Prisma 7 for TypeScript-side direct data access.

## Rule

- `org_id` is the tenant boundary everywhere.
