# NEXT Rust Migration Report

**Branch:** `fix/next-rust-migration`  
**Base:** `fix/structural-eight-before-capabilities`  
**Context:** Previous commit `d4e61892a` tombstoned council and content groups. This patch continues the migration.

## Baseline State (Pre-Patch)

| Check                     | Result                     |
| ------------------------- | -------------------------- |
| `pnpm structural:check`   | PASS (warns only, exits 0) |
| `pnpm typecheck`          | PASS                       |
| `cargo check --workspace` | PASS                       |
| `pnpm route-parity:check` | PASS                       |

## Goals

1. Harden route parity script to catch all `apiFetch` variants
2. Make Prisma guard strict for Rust-equivalent violations
3. Tombstone all remaining dual-backend routes (campaigns, daily-wins, nudges, intel, muse, prl)
4. Update `api.ts` and hooks to use Rust for all migrated groups
5. Handle lib helpers (replace Prisma usage with throwing stubs)
6. Document no-equivalent gaps in ledger
7. Ensure `pnpm structural:check` fails on future drift

## Tasks Completed

- [x] Task 1: Harden route parity script
- [x] Task 2: Harden Prisma guard to fail on Rust-equivalent violations
- [x] Task 3: Tombstone campaigns routes
- [x] Task 4: Tombstone daily-wins routes
- [x] Task 5: Tombstone nudges routes
- [x] Task 6: Tombstone intel routes
- [x] Task 7: Tombstone muse routes
- [x] Task 8: Tombstone prl routes
- [x] Task 9: Update api.ts and hooks for all migrated groups
- [x] Task 10: Handle lib helpers with Prisma (throwing stubs)
- [x] Task 11: Create RUST_API_GAP_LEDGER.md
- [x] Task 12: Red team tests

## Red Team Results

| Check                               | Result                               |
| ----------------------------------- | ------------------------------------ |
| `pnpm structural:check`             | PASS (0 violations, 34 gap warnings) |
| `pnpm route-parity:check`           | PASS                                 |
| `pnpm typecheck`                    | PASS                                 |
| `cargo check --workspace`           | PASS                                 |
| No old Next API calls in frontend   | PASS (grep found 0 matches)          |
| No appFetch misuse for product APIs | PASS                                 |

## Files Changed

### Tombstoned Routes (12 files)

- `apps/web/src/app/api/campaigns/route.ts` - GET, POST
- `apps/web/src/app/api/campaigns/[id]/route.ts` - GET, PATCH, DELETE
- `apps/web/src/app/api/campaigns/[id]/moves/route.ts` - GET, POST
- `apps/web/src/app/api/campaigns/[id]/moves/[moveId]/tasks/route.ts` - GET, POST
- `apps/web/src/app/api/daily-wins/route.ts` - GET, POST
- `apps/web/src/app/api/daily-wins/[id]/route.ts` - GET, PATCH
- `apps/web/src/app/api/intel/route.ts` - GET, POST
- `apps/web/src/app/api/muse/conversations/route.ts` - GET, POST
- `apps/web/src/app/api/muse/conversations/[id]/route.ts` - GET, PATCH
- `apps/web/src/app/api/muse/conversations/[id]/chat/route.ts` - POST
- `apps/web/src/app/api/nudges/route.ts` - GET, POST
- `apps/web/src/app/api/nudges/[id]/route.ts` - PATCH
- `apps/web/src/app/api/prl/decay/route.ts` - POST

### Updated Frontend Hooks

- `apps/web/src/features/campaigns/hooks/index.ts` - uses apiFetch + /api/v1/\*
- `apps/web/src/features/muse/hooks/index.ts` - uses apiFetch + /api/v1/\*
- `apps/web/src/hooks/use-intel.ts` - uses apiFetch + /api/v1/\*
- `apps/web/src/hooks/use-nudges.ts` - uses apiFetch + /api/v1/\*

### Lib Helper Stubs (14 files)

- `apps/web/src/lib/campaigns/evaluateBrief.ts`
- `apps/web/src/lib/campaigns/generateMoves.ts`
- `apps/web/src/lib/council/generatePositions.ts`
- `apps/web/src/lib/council/synthesize.ts`
- `apps/web/src/lib/eel/egoState.ts`
- `apps/web/src/lib/eel/enrich.ts`
- `apps/web/src/lib/intel/analyzeCompetitor.ts`
- `apps/web/src/lib/intel/generateIntelBrief.ts`
- `apps/web/src/lib/muse/handlers/index.ts`
- `apps/web/src/lib/nudges/generateNudges.ts`
- `apps/web/src/lib/prl/cortex.ts`
- `apps/web/src/lib/prl/decay.ts`
- `apps/web/src/lib/prl/ingest.ts`
- `apps/web/src/lib/wins/generateDailyWin.ts`

### Scripts Hardened

- `scripts/check-route-parity.mjs` - now catches all apiFetch variants, detects appFetch misuse
- `scripts/check-no-prisma-product-runtime.mjs` - now fails on Rust-equivalent violations

### Documentation Created

- `RUST_API_GAP_LEDGER.md` - 17 gap routes documented
- `NEXT_RUST_MIGRATION_REPORT.md` - this file

## Test Pass/Fail Table

| Test                      | Status | Notes                         |
| ------------------------- | ------ | ----------------------------- |
| `pnpm structural:check`   | PASS   | 0 violations, 34 gap warnings |
| `pnpm route-parity:check` | PASS   | No unmounted routes           |
| `pnpm typecheck`          | PASS   | 3/3 packages                  |
| `cargo check --workspace` | PASS   | Dev profile                   |
| Old API route grep        | PASS   | 0 matches                     |
| appFetch grep             | PASS   | No product API misuse         |

## Known Pre-Existing Issues

- `cargo fmt --all --check` - may fail due to pre-existing formatting issues (not caused by this patch)
- `cargo test --workspace` - may fail due to Windows `aws-lc-sys` linker errors (pre-existing)

## Remaining Gap Buckets (from RUST_API_GAP_LEDGER.md)

1. **Auth/account flows** - forgot-password, reset-password
2. **Avatars** - avatar CRUD
3. **Dashboard** - office summary
4. **Foundation scan** - quick scan route
5. **Council streaming** - start, stream, synthesize (HIGH priority)
6. **Campaign AI features** - evaluate, generate moves (HIGH priority)
7. **Cron jobs** - daily-wins, nudges, intel, prl crons
8. **Intel analysis** - signal routes, competitors

## Recommended Next Patch

`fix/council-streaming-and-campaign-ai` - Implement the two highest-risk gap buckets:

1. Council streaming endpoints (start, stream, synthesize)
2. Campaign AI features (evaluate, generate moves)
