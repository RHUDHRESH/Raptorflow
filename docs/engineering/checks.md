# Engineering Checks

## Purpose

This file defines the safety baseline for all architecture refactor branches in the Raptorflow monorepo. Every PR must validate against these checks before merging.

Session 1 (CI safety baseline) established this harness so that every future branch can answer one question:

> Did this refactor break the repo, or was the repo already broken?

## Local Prerequisites

| Requirement       | Version                          | Notes                                                                                |
| ----------------- | -------------------------------- | ------------------------------------------------------------------------------------ |
| Node.js           | >= 22.0.0 (via .nvmrc)           | Use `nvm use` or `corepack enable`                                                   |
| pnpm              | 10.33.0                          | Managed via Corepack (`corepack enable`, `corepack prepare pnpm@10.33.0 --activate`) |
| Rust              | 1.94.0 (via rust-toolchain.toml) | `rustup install 1.94.0`                                                              |
| Docker            | Latest                           | Required only for full integration tests, not basic checks                           |
| Postgres / Qdrant | -                                | Required only for DB-backed integration and smoke tests                              |

Environment variables required only for full app runtime (not basic checks):

- `DATABASE_URL` / `RAPTORFLOW_DIRECT_DATABASE_URL` — Postgres
- `QDRANT_URL` — Qdrant
- `CLERK_SECRET_KEY` — Clerk auth
- `AWS_*` — Bedrock / S3
- `SENTRY_*` — Error tracking

None of these are required for the fast local check or CI.

## Fast Local Check

Run these before every PR:

```bash
pnpm install --frozen-lockfile
pnpm format
pnpm typecheck
cargo fmt --all -- --check
cargo check --workspace --all-targets
```

This verifies:

- Dependencies are consistent with lockfile
- Prettier formatting
- TypeScript compiles without errors
- Rust code is formatted correctly
- Rust code compiles

## Full Local Check

Run after making changes, before pushing:

```bash
pnpm test
pnpm build
cargo clippy --workspace --all-targets
cargo test --workspace --lib
```

Additional optional checks:

```bash
pnpm contracts:check
pnpm docs:check
pnpm route-parity:check
pnpm structural:check
```

## GitHub Actions

CI runs automatically on:

- **Pull requests** against `main`
- **Push** to `main`

The CI workflow (`ci.yml`) has four jobs:

### Web job

Runs on `ubuntu-latest`:

1. Setup Node 22 + pnpm 10.33.0 with cache
2. `pnpm install --frozen-lockfile`
3. `pnpm format` (Prettier formatting check)
4. Generate Prisma client
5. `pnpm lint` (Turbo pipeline — TypeScript strict checks)
6. `pnpm typecheck` (Turbo pipeline — TypeScript type checks)
7. `pnpm test` (Turbo pipeline — Vitest unit tests)
8. `pnpm build` (Turbo pipeline — Next.js + packages build)
9. `pnpm contracts:check` (Schema contract coverage)
10. `pnpm docs:check` (Documentation integrity)

### Rust job

Runs on `ubuntu-latest`:

1. Setup Rust 1.94.0 with rustfmt + clippy, cached
2. `cargo fmt --all -- --check`
3. `cargo check --workspace --all-targets`
4. `cargo clippy --workspace --all-targets`
5. `cargo test --workspace --lib` (library unit tests only)

### Structural Integrity job

Runs on `ubuntu-latest`:

1. Setup Node + pnpm + Rust
2. `pnpm install --frozen-lockfile`
3. Generate Prisma client
4. `pnpm route-parity:check` — validates frontend API routes exist in Rust router
5. `pnpm runtime-authority:check` — validates no Prisma leaks in product runtime
6. `pnpm scaffold:check` — validates all expected scaffold screens exist

### Docker Compose job

Runs `docker compose config` to validate compose file syntax.

### Additional workflow: Structural Spine (`structural-spine.yml`)

A separate workflow runs on `fix/**` branches and PRs to main. It duplicates some CI checks but additionally runs DB-backed integration tests using a Postgres service container:

- `cargo test -p raptorflow-db --test generated_moves_transaction`

This is kept separate because it requires a live Postgres service container in CI.

### Additional workflow: Runtime Reality Smoke (`runtime-reality.yml`)

Runs DB and Qdrant smoke tests with service containers. The Bedrock smoke test requires manual dispatch with AWS credentials.

### Additional workflow: Deploy Backend (`deploy-backend.yml`)

Deploys the Rust API to AWS ECS on push to `main`. Requires AWS IAM credentials.

## Deferred Checks

These checks are intentionally not enforced in CI yet:

| Check                           | Reason                                                                              | Tracking                                                          |
| ------------------------------- | ----------------------------------------------------------------------------------- | ----------------------------------------------------------------- |
| DB-backed integration tests     | Require Postgres + Qdrant service containers; too heavy for per-PR CI               | Separate workflow: `structural-spine.yml`, `runtime-reality.yml`  |
| AWS/Bedrock integration tests   | Require AWS credentials                                                             | Manual workflow dispatch only                                     |
| Frontend E2E tests (Playwright) | Test files exist (`@playwright/test` configured) but no stable test suite yet       | Not wired                                                         |
| End-to-end API tests            | Require running API + Postgres + Qdrant + Clerk                                     | Not wired                                                         |
| `cargo clippy -- -D warnings`   | Existing warnings in the workspace would cause failure; needs gradual cleanup first | Run `cargo clippy --workspace --all-targets` without deny for now |
| Schema drift detection          | No tooling wired to detect schema/contract drift automatically                      | Future session                                                    |
| Bundle size / perf budgets      | Not configured                                                                      | Future session                                                    |
| Security audit (SAST/DAST)      | Not configured in CI                                                                | Covered by `SECURITY.md` manually                                 |

## Rules for Future Refactor Agents

1. **Every branch must start from latest `main`.**

   ```bash
   git checkout main
   git pull --ff-only
   git checkout -b arch/NNN-description
   ```

2. **Every PR must pass CI before merge.** No bypassing failing checks.

3. **If a check is flaky**, document the failure and fix it or quarantine it intentionally with a tracking issue. Do not ignore flaky checks.

4. **Do not add architecture changes to CI baseline PRs.** This file is the safety harness, not a refactor target.

5. **Keep future PRs small.** Each refactor branch should touch one concern (auth extraction, route dedup, query splitting, etc.).

6. **Run the fast local check before every commit.** It takes under a minute for TypeScript and 2–3 minutes for Rust.

7. **If you introduce new generated files**, update `.gitignore` and add the generation step to CI if it needs to run per-environment.

8. **Adding new dependencies**: If a new check requires a new tool (e.g., `cargo-deny`, `eslint`, `knip`), confirm it's compatible with the existing `pnpm`/`turbo`/`cargo` workflows before wiring into CI.

## CI Workflow Decisions

- **Separate jobs for web, rust, structural, compose** allows parallel execution and clear failure attribution.
- **Prisma client regenerated in CI** because the checked-in generated client includes a Windows query engine binary; CI on Linux needs the native engine.
- **`cargo test --workspace --lib` only** — integration tests in `crates/*/tests/` depend on external services and environment variables. Unit tests in `#[cfg(test)]` modules are self-contained.
- **No `-D warnings` on clippy** yet — existing warnings need cleanup in a dedicated refactor session.
- **`docker compose config`** validates the compose file is syntactically valid without starting services.

## Interpreting CI Failures

| CI Job                        | Common Failure                 | Likely Cause                                        |
| ----------------------------- | ------------------------------ | --------------------------------------------------- |
| Web: `pnpm format`            | Formatting diff                | Run `pnpm format:write` locally                     |
| Web: `pnpm typecheck`         | TypeScript error               | Add missing types, fix imports                      |
| Web: `pnpm build`             | Build error                    | Check build logs; often Prisma or Sentry related    |
| Rust: `cargo fmt`             | Formatting diff                | Run `cargo fmt` locally                             |
| Rust: `cargo check`           | Compilation error              | Fix Rust type errors                                |
| Rust: `cargo test`            | Test failure                   | Run `cargo test --workspace --lib` locally          |
| Structural: route-parity      | Frontend calls unmounted route | Add route to Rust router or fix API call            |
| Structural: runtime-authority | Prisma leak in product code    | Remove `@raptorflow/database` import from API route |

## What Not To Bypass

- Do not skip `pnpm format` — formatting consistency is non-negotiable.
- Do not add `// eslint-disable-next-line` or `#[allow(...)]` without strong justification.
- Do not commit `.env` files or real secrets.
- Do not change PR CI workflows in a product/refactor PR. CI changes belong in dedicated CI baseline PRs.
