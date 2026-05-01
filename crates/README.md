# Rust Backend Crates

The Rust workspace currently contains 25 crates. The deployable backend binary
is `raptorflow-api`; the rest are libraries grouped by responsibility.

## API Entry Point

- `api` - starts telemetry, config, database pools, and the Axum HTTP server.

## Core Runtime

- `http` - Axum router, middleware, route modules, and request state.
- `auth` - Clerk JWT validation, tenant extraction, and Clerk webhook types.
- `config` - typed environment configuration.
- `db` - SQLx pool and database access helpers.
- `contracts` - Rust domain and transport types generated from `schemas/`.
- `telemetry` - tracing, structured logging, and observability setup.

## Product and Domain Logic

- `acquisition` - acquisition-oriented domain hooks.
- `avatars` - avatar registry and templates.
- `campaigns` - campaigns, moves, tasks, and campaign planning behavior.
- `council` - multi-agent council sessions and synthesis.
- `eel` - entity essence language and avatar context enrichment.
- `foundation` - brand foundation screens, snapshots, scans, and section data.
- `harness` - agent session orchestration and context-pack assembly.
- `intel` - market and competitor intelligence behavior.
- `jobs` - background job registry and job route surface.
- `office` - Office canvas event vocabulary and room state.
- `prl` - predictive ripple memory and retrieval primitives.
- `research` - research substrate support.

## Integrations

- `aws` - AWS Bedrock and S3 helpers.
- `integrations` - external service facade.
- `resend` - email delivery integration.
- `search` - search providers, including SearxNG and DuckDuckGo.
- `sqs` - SQS job queue helpers.

## Test Support

- `testing` - reusable fixtures and test helpers.

## Conventions

- Add cross-service types in `schemas/`, then run `pnpm contracts:sync`.
- Import shared domain types from `raptorflow_contracts`.
- Read configuration through `raptorflow_config::Settings`.
- Keep tenant-bearing database queries scoped by `org_id`.
- Run `cargo fmt --check` and `cargo check --workspace` before shipping Rust changes.

Billing is reserved in schema/config decisions for a later stage, but there is no
active `crates/billing` crate in the current workspace.
