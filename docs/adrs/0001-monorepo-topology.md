# ADR 0001: Monorepo Topology

## Status

Accepted

## Decision

Use a pnpm + Turborepo monorepo with:

- one Next.js app in `apps/web`
- one Rust Cargo workspace rooted at the repository root
- shared TS contracts in `packages/contracts`
- language-neutral schemas in `schemas`

## Rationale

- Frontend and backend deploy from the same repository
- Contract drift becomes visible in CI
- Vercel supports Turborepo monorepos directly
- Backend crates remain independently testable without fragmenting the repository
