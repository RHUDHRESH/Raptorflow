# Scripts

Scripts are grouped around setup, validation, contract maintenance, smoke checks,
and deployment.

## Pre-Commit

`.githooks/pre-commit` runs:

```bash
pnpm lint-staged
```

The `lint-staged` script is intentionally repo-wide despite the name:

```bash
pnpm lint
pnpm typecheck
pnpm docs:check
pnpm scaffold:check
pnpm smoke
```

## Local Verification

```bash
pnpm verify
```

Runs the main local confidence chain:

- `pnpm lint`
- `pnpm typecheck`
- `pnpm docs:check`
- `pnpm contracts:check`
- `pnpm scaffold:check`
- `pnpm structural:check`
- `pnpm smoke`

CI also runs Rust formatting, clippy, and `cargo check --workspace`.

## Contract Scripts

### `pnpm contracts:sync`

Regenerates Rust and TypeScript contract code from `schemas/`. Run this after
changing any schema.

### `pnpm contracts:check`

Verifies the committed contract files still match the schema expectations.

## Documentation Check

```bash
pnpm docs:check
```

Validates the source corpus and prompt-contract docs:

- `Uploads/` matches `docs/canonical/source-manifest.json`
- SHA-256 checksums match
- source digest files exist and are non-empty
- prompt contract files exist and are non-empty
- the duplicate Vol. 3 source is recorded correctly

## Scaffold Checks

```bash
pnpm scaffold:check
```

Runs:

- `scripts/check-foundation-screens.mjs`
- `scripts/check-office-events.mjs`
- `scripts/check-job-registry.mjs`

These checks protect expected route, event, and job registry coverage.

## Structural Checks

```bash
pnpm structural:check
```

Runs:

- `scripts/check-no-prisma-product-runtime.mjs`
- `scripts/check-route-parity.mjs`

Current known Prisma gaps are reported as warnings unless
`ALLOW_PRISMA_GAPS=0` is set.

## Smoke Check

```bash
pnpm smoke
```

The smoke check is intentionally fast. It verifies:

- app route metadata maps to real Next.js page files
- sidebar navigation renders from `routeGroups`
- sidebar icon coverage matches the route metadata
- auth middleware and protected router markers exist
- root `vercel.json` is the only Vercel config
- Vercel cron paths map to real route handlers

## Bootstrap

```bash
./scripts/bootstrap.sh
# or
./scripts/bootstrap.ps1
```

Bootstraps a new machine with Corepack, dependencies, git hooks, scaffold checks,
the smoke check, and Docker image pulls.

## Frontend Deploy

```bash
./scripts/deploy-frontend.sh
./scripts/deploy-frontend.sh --production
```

Requires `VERCEL_TOKEN`, `VERCEL_ORG_ID`, and `VERCEL_PROJECT_ID`. The script
builds `@raptorflow/web` and deploys from the repository root so it uses the root
`vercel.json`.
