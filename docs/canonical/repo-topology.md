# Repo Topology

## Principles

- Contracts before implementation
- Canonical docs before subsystem logic
- Shared schemas in language-neutral form
- One deployable backend binary with many internal crates
- Frontend structured around route groups and feature shells

## Top-level layout

- `apps/web`: Next.js product shell and marketing site
- `packages/contracts`: shared TypeScript contracts and schema helpers
- `schemas`: language-neutral contract source files
- `crates/api`: deployable Axum binary
- `crates/*`: internal domain, infra, and integration crates
- `database`: SQL migrations, seeds, and fixtures
- `infra/tofu`: AWS and Vercel infrastructure definition
- `docs`: source digests, canonical specs, ADRs, threat model, runbooks, prompt contracts
- `scripts`: validation, smoke, bootstrap, and sync scripts

## Naming rules

- Tenant-bearing resources must include `org_id` explicitly.
- External event names use dotted domains, such as `office.event`.
- Queue names, S3 prefixes, and Dragonfly keys are environment-prefixed.
- Crate and package names use the `raptorflow-*` prefix for external build clarity.
