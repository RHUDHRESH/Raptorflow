# Council War Room — Verification Report

## Steps Completed

- [x] Step 15: War Room UI ↔ Council API contract
- [x] Step 16: Council synthesis → `generated_content` artifact
- [x] Step 17: Schema-aware content renderers
- [x] Step 18: Smoke checklist + docs

## What Was Tested

| Area               | Scope                                             | Status |
| ------------------ | ------------------------------------------------- | ------ |
| War Room page load | `/council/war-room` renders without errors        |        |
| Create council run | Form submission → API → run created               |        |
| Run list           | Existing runs appear in sidebar                   |        |
| Polling            | Turns, presence, debate events refresh every 2.5s |        |
| Timeline           | Debate events render chronologically              |        |
| Presence grid      | Avatar states shown correctly                     |        |
| Synthesis card     | Post-completion synthesis rendered                |        |
| Content page       | `council-synthesis` artifact renders as cards     |        |
| URL hydration      | `?run=<id>` loads correct run                     |        |
| Error state        | Invalid input produces graceful error             |        |
| Empty state        | No runs → empty state message                     |        |

## Command Results

### TypeScript / Structural Checks

| Command                        | Status |
| ------------------------------ | ------ |
| `pnpm typecheck`               |        |
| `pnpm lint`                    |        |
| `pnpm structural:check`        |        |
| `pnpm route-parity:check`      |        |
| `pnpm runtime-authority:check` |        |

### Rust Checks

| Command                                    | Status |
| ------------------------------------------ | ------ |
| `cargo fmt --all --check`                  |        |
| `cargo check --workspace`                  |        |
| `cargo clippy --all-features --lib --bins` |        |

### Infrastructure

| Command                 | Status |
| ----------------------- | ------ |
| `docker compose config` |        |

## Scripts Availability (package.json)

| Script                         | Exists | Command                                                                                   |
| ------------------------------ | ------ | ----------------------------------------------------------------------------------------- |
| `pnpm typecheck`               | ✅     | `turbo run typecheck`                                                                     |
| `pnpm lint`                    | ✅     | `turbo run lint`                                                                          |
| `pnpm structural:check`        | ✅     | `node scripts/check-no-prisma-product-runtime.mjs && node scripts/check-route-parity.mjs` |
| `pnpm route-parity:check`      | ✅     | `node scripts/check-route-parity.mjs`                                                     |
| `pnpm runtime-authority:check` | ✅     | `node scripts/check-no-prisma-product-runtime.mjs`                                        |

All 5 verification scripts exist in `package.json`. No missing scripts.

## CI Workflow Status

| Workflow         | File                                     | Notes                                                                                  |
| ---------------- | ---------------------------------------- | -------------------------------------------------------------------------------------- |
| CI               | `.github/workflows/ci.yml`               | Pre-existing `web-and-docs` failure (DATABASE_URL build issue documented in gaps §1.6) |
| Structural Spine | `.github/workflows/structural-spine.yml` | Runs structural checks + DB transaction tests                                          |
| Runtime Reality  | `.github/workflows/runtime-reality.yml`  | DB + Qdrant smoke; Bedrock smoke gated behind manual dispatch                          |
| Deploy Backend   | `.github/workflows/deploy-backend.yml`   | Production deploy only — requires AWS credentials                                      |

## Remaining Known Issues

- CI `web-and-docs` job pre-existing failure: `DATABASE_URL` required during Next.js build (see §1.6 in gaps report)
- `avatar_roster` cast on war-room page line 41 still uses `as string[]` — minor type narrowing, not an `unknown` cast
- Council AI mode requires AWS Bedrock setup — deterministic fallback works without it
