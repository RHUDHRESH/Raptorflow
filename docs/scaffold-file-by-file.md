# Repository Map

This is the current practical map of the repository. It replaces the older
scaffold-era file-by-file plan, which described routes and crates that no longer
exist.

## Root

- `package.json` - pnpm workspace scripts and shared JS tooling versions.
- `pnpm-workspace.yaml` - JS workspace packages under `apps/*` and `packages/*`.
- `Cargo.toml` - Rust workspace members and shared dependency versions.
- `docker-compose.yml` - local Postgres, PgBouncer, Qdrant, SearxNG, API, and web services.
- `vercel.json` - canonical frontend deploy config.
- `.github/workflows/` - CI and backend deployment workflows.
- `.githooks/pre-commit` - runs the local validation chain through `pnpm lint-staged`.

Historical reports and old PR bodies are archived under `docs/archive/`, not in
the repository root.

## Frontend

- `apps/web/src/app/` - Next.js App Router pages and API routes.
- `apps/web/src/brand/routes.ts` - single route metadata source for app navigation.
- `apps/web/src/components/layout/` - app shell, sidebar, page frame, and route chrome.
- `apps/web/src/components/office/` - Office canvas and related panels.
- `apps/web/src/features/` - feature-level hooks.
- `apps/web/src/hooks/` - cross-feature hooks.
- `apps/web/src/lib/` - API client, integration clients, inference helpers, and utilities.
- `apps/web/tests/e2e/` - Playwright live smoke tests.

Generated Playwright auth state and test output are ignored and must not be
committed.

## Rust Backend

- `crates/api` - deployable binary.
- `crates/http` - Axum routing and middleware.
- `crates/auth` - Clerk auth and tenant extraction.
- `crates/config` - typed settings.
- `crates/db` - SQLx data access.
- `crates/contracts` - generated Rust contracts.
- `crates/*` - domain, integration, telemetry, and test-support crates.

See [../crates/README.md](../crates/README.md) for the current crate list.

## Contracts and Data

- `schemas/` - JSON schema source of truth.
- `packages/contracts/` - generated TypeScript contracts.
- `packages/database/` - Prisma 7 package for TypeScript-side data access.
- `database/migrations/` - SQL migrations used by the Rust stack.
- `database/fixtures/` - platform fixture data.

Run `pnpm contracts:sync` after schema changes and commit the schema plus
generated contract files together.

## Infrastructure

- `infra/docker/` - Dockerfiles and local service config.
- `infra/tofu/` - OpenTofu modules and environment configs for production AWS.
- `scripts/deploy-frontend.sh` - Vercel CLI wrapper that deploys from repo root.

## Documentation

- `docs/canonical/` - current stack, topology, data, deployment, and decision docs.
- `docs/runbooks/` - operational procedures.
- `docs/prompt-contracts/` - prompt contracts validated by `pnpm docs:check`.
- `docs/source-digests/` - digests tied to the immutable `Uploads/` source corpus.
- `docs/archive/` - historical reports, old specs, PR bodies, and source PDFs.

Use active docs for build and deployment decisions. Use the archive only for
context.
