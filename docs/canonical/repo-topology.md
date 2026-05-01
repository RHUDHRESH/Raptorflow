# Repo Topology

## Principles

- Contracts before implementation
- Canonical docs before subsystem logic
- Shared schemas in language-neutral form
- One deployable backend binary with internal crates
- Frontend structured around route groups and feature shells

## Top-level layout

- `apps/web`: Next.js frontend
- `packages/contracts`: shared TypeScript contracts
- `packages/database`: Prisma 7 package for TS-side data access
- `schemas`: source of truth for cross-service types
- `crates/api`: deployable Axum binary
- `crates/*`: internal domain, infra, and integration crates
- `database/migrations`: PostgreSQL schema
- `infra/tofu`: production infrastructure
- `docs`: canonical specs, ADRs, runbooks, prompt contracts
- `docs/archive`: historical reports and old specs, not operational truth
- `scripts`: validation and bootstrap helpers

## Naming rules

- Tenant-bearing resources must include `org_id`.
- External event names use dotted domains.
- Queue names and S3 prefixes are environment-prefixed.
