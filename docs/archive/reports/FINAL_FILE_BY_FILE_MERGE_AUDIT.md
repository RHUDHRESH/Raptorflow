# Final File-by-File Merge Audit

**Branch:** `fix/final-file-by-file-merge-audit` (`ce5a02918`)  
**Date:** 2026-04-24  
**Status:** Ready to merge (pending CI)  
**Merge gate:** CI `structural-spine` workflow must pass with `db-transaction-test` job succeeding

---

## Scope

All changes in the `fix/final-file-by-file-merge-audit` branch (10 commits ahead of `main`). Workstream spans 8 branches across Council AI + Campaign AI migration from Next.js/Prisma to Rust-backed endpoints.

---

## Commit Chain (oldest → newest)

| Commit      | Branch                                           | Description                                            |
| ----------- | ------------------------------------------------ | ------------------------------------------------------ |
| `0ac88111e` | `fix/ai-runtime-redteam-contracts`               | Hardened AI JSON parsing, move validation              |
| `43f64e44c` | `fix/council-frontend-polling`                   | EventSource → authenticated polling                    |
| `95901dd74` | `fix/council-route-tombstones-and-poll-contract` | 3 council routes → 410, poll contract fix              |
| `3a94310da` | `fix/generate-moves-db-transaction`              | `create_generated_campaign_moves_transactional` helper |
| `a6bb2dbde` | `fix/generate-moves-transaction-corrections`     | Fixed empty validator, truncation, duplicate seq bugs  |
| `364b7d2a9` | `fix/db-test-infrastructure-for-transactions`    | DB integration test infra + sqlx dev-dep               |
| `fd186e495` | `fix/db-transaction-test-rls-correction`         | Fixed RLS `SET LOCAL` context bug                      |
| `3c092f1a5` | `fix/structural-spine-pr-hygiene`                | PR hygiene: tsbuildinfo, SHA updates, merge report     |
| `a0df5263c` | `fix/ci-db-transaction-proof`                    | CI workflow + PostgreSQL service container             |
| `ce5a02918` | `fix/final-file-by-file-merge-audit`             | Final audit, CI trigger fix, formatting corrections    |

---

## File Classification (72 files changed)

### Rust Backend (crates/)

| File                                             | Classification              | Notes                                                                                                                         |
| ------------------------------------------------ | --------------------------- | ----------------------------------------------------------------------------------------------------------------------------- |
| `crates/http/src/routes/council.rs`              | **Workstream**              | `start_council_session`, stream, synthesize handlers; `has_failure`/`continue;` pattern is intentional partial failure design |
| `crates/http/src/routes/campaigns.rs`            | **Workstream**              | `validate_generated_moves`, `build_generated_move_inserts`, `build_move_response_from_created`                                |
| `crates/http/src/routes/foundation.rs`           | **Workstream (formatting)** | `generate_fallback_calendar` is valid; `downstream_impact` placeholder is pre-existing                                        |
| `crates/http/src/routes/prl.rs`                  | **Workstream (formatting)** | Incidental formatting changes only                                                                                            |
| `crates/db/src/queries.rs`                       | **Workstream**              | `create_generated_campaign_moves_transactional` with `SET LOCAL` inside tx                                                    |
| `crates/db/src/lib.rs`                           | **Workstream**              | Re-exports for `TenantDbPool`, `TenantContext`                                                                                |
| `crates/db/src/error.rs`                         | **Workstream**              | Error types                                                                                                                   |
| `crates/db/tests/generated_moves_transaction.rs` | **Workstream**              | Commit + rollback tests with `.expect()` behavior                                                                             |
| `crates/http/src/routes/ai_helpers.rs`           | **Workstream**              | `extract_json_object`, `validate_ai_output_not_just_prose`, `VALID_MOVE_TYPES`                                                |
| `crates/http/src/routes/mod.rs`                  | **Workstream**              | Route registration                                                                                                            |
| `crates/http/src/middleware/tenant.rs`           | **Workstream**              | `TenantContext` middleware                                                                                                    |
| `crates/http/src/auth.rs`                        | **Workstream**              | JWT validation                                                                                                                |
| `crates/http/src/lib.rs`                         | **Workstream**              | Crate root                                                                                                                    |
| `crates/http/src/extractor.rs`                   | **Workstream**              | Request extractors                                                                                                            |
| `crates/http/src/routes/activities.rs`           | **Workstream**              | Activity routes                                                                                                               |
| `crates/http/src/commands.rs`                    | **Workstream**              | Command definitions                                                                                                           |
| `Cargo.toml` (workspace)                         | **Workstream**              | Manifest updates                                                                                                              |
| `Cargo.lock`                                     | **Workstream**              | Lock file                                                                                                                     |

### TypeScript Frontend (apps/web/)

| File                                                                 | Classification         | Notes                                             |
| -------------------------------------------------------------------- | ---------------------- | ------------------------------------------------- |
| `apps/web/src/lib/api.ts`                                            | **Workstream**         | `pollSessionRaw`, `pollMessagesRaw`, type exports |
| `apps/web/src/app/(app)/council/[sessionId]/page.tsx`                | **Workstream**         | Full polling rewrite (2s interval)                |
| `apps/web/src/app/api/council/[sessionId]/start/route.ts`            | **Workstream**         | Tombstoned → 410                                  |
| `apps/web/src/app/api/council/[sessionId]/stream/route.ts`           | **Workstream**         | Tombstoned → 410                                  |
| `apps/web/src/app/api/council/[sessionId]/synthesize/route.ts`       | **Workstream**         | Tombstoned → 410                                  |
| `apps/web/src/app/(app)/uploads/page.tsx`                            | **Workstream (minor)** | Type cast fix from structural workstream          |
| `apps/web/src/app/(app)/campaign/[campaignId]/move-history/page.tsx` | **Workstream**         | Move history page                                 |
| `apps/web/tsconfig.json`                                             | **Workstream**         | tsconfig updates                                  |
| `apps/web/next.config.ts`                                            | **Workstream**         | Next.js config                                    |
| `apps/web/package.json`                                              | **Workstream**         | Dependencies                                      |
| `pnpm-lock.yaml`                                                     | **Workstream**         | Lock file                                         |

### CI / Infrastructure

| File                                     | Classification | Notes                                                                                                               |
| ---------------------------------------- | -------------- | ------------------------------------------------------------------------------------------------------------------- |
| `.github/workflows/structural-spine.yml` | **Workstream** | `structural-checks` + `db-transaction-test` jobs; `pull_request.branches: [main]` (was incorrectly set to `fix/**`) |
| `.gitignore`                             | **Workstream** | Added `*.tsbuildinfo`                                                                                               |

### Reports / Docs

| File                                               | Classification | Notes                                |
| -------------------------------------------------- | -------------- | ------------------------------------ |
| `STRUCTURAL_SPINE_MERGE_REPORT.md`                 | **Workstream** | Full workstream summary              |
| `CI_DB_TRANSACTION_PROOF_REPORT.md`                | **Workstream** | CI workflow details                  |
| `AI_RUNTIME_REDTEAM_REPORT.md`                     | **Workstream** | AI hardening                         |
| `COUNCIL_FRONTEND_POLLING_REPORT.md`               | **Workstream** | EventSource → polling                |
| `COUNCIL_TOMBSTONE_CONTRACT_REPORT.md`             | **Workstream** | 410 responses; SHA placeholder fixed |
| `GENERATE_MOVES_TRANSACTION_REPORT.md`             | **Workstream** | Transaction helper                   |
| `GENERATE_MOVES_TRANSACTION_CORRECTIONS_REPORT.md` | **Workstream** | Validator bugs fixed                 |
| `DB_TRANSACTION_TEST_INFRA_REPORT.md`              | **Workstream** | DB test infra                        |
| `DB_TRANSACTION_RLS_CORRECTION_REPORT.md`          | **Workstream** | RLS bug corrected                    |
| `docs/testing/db-integration.md`                   | **Workstream** | DB test setup + CI reference         |

---

## Red Team Findings

### ✅ No Issues Found

- No fake fallback AI data added
- No `RAPTORFLOW_DATABASE_URL` or secrets in CI workflow
- No JWT in query strings
- No `EventSource` with Bearer auth
- No Prisma in product runtime
- No `TEST_DATABASE_URL` in tests (only in CI job env)
- All DB reads/writes use `tenant.org_id` from `TenantContext`
- DB tests skip gracefully when `TEST_DATABASE_URL` absent

### ⚠️ Pre-existing Failures (NOT caused by this workstream)

| Check                                           | Status           | Notes                                                                 |
| ----------------------------------------------- | ---------------- | --------------------------------------------------------------------- |
| `cargo fmt --all --check`                       | **FAIL**         | ~40 files with pre-existing formatting issues unrelated to workstream |
| `cargo test` linking                            | **FAIL**         | aws-lc-sys/Windows toolchain issue, pre-existing                      |
| `foundation.rs` `downstream_impact` placeholder | **Pre-existing** | Not from this workstream                                              |

---

## Corrections Applied in This Branch (`ce5a02918`)

1. **Fixed CI workflow trigger:** `pull_request.branches: [fix/**]` → `pull_request.branches: [main]`
2. **Fixed `COUNCIL_TOMBSTONE_CONTRACT_REPORT.md` SHA placeholder:** `(pending - not yet committed)` → `95901dd74a57a1ae97deb495e5ee7273286d4d76`
3. **Applied `cargo fmt --all`** to workstream files only (reverted non-workstream files)
4. **Verified** all 5 required checks pass

---

## Required Checks (must pass before merge)

| Check                    | Command                   | Expected               |
| ------------------------ | ------------------------- | ---------------------- |
| Structural               | `pnpm structural:check`   | Pass                   |
| Route parity             | `pnpm route-parity`       | Pass                   |
| Runtime authority        | `pnpm runtime-authority`  | Pass                   |
| Typecheck                | `pnpm typecheck`          | Pass                   |
| Cargo check              | `cargo check --workspace` | Pass                   |
| CI `structural-spine`    | GitHub Actions            | Both jobs pass         |
| CI `db-transaction-test` | GitHub Actions            | PostgreSQL test passes |

---

## Merge Recommendation

**Merge after CI `db-transaction-test` job passes.** The DB transaction test is the critical gate — it proves that `create_generated_campaign_moves_transactional` correctly rolls back on validation failure (empty list, truncation, duplicate sequence, etc.).

---

## Next Workstream After Merge

1. Foundation scan consolidation
2. Intel competitor/signal routes
