# CI DB Transaction Proof Report

**Branch:** `fix/ci-db-transaction-proof`
**Commit SHA:** (to be committed with this branch)
**Date:** 2026-04-24

---

## 1. Branch Name

`fix/ci-db-transaction-proof`

---

## 2. Mission

Add a minimal CI workflow to run the existing DB transaction integration test with a real PostgreSQL service container, proving the rollback proof works in CI.

**Constraints:**

- Do NOT add marketing capabilities
- Do NOT add UI
- Do NOT change product behavior
- Do NOT reintroduce Prisma
- Only about proving the existing DB integration test in CI

---

## 3. Files Changed

| File                                             | Change                                                                       |
| ------------------------------------------------ | ---------------------------------------------------------------------------- |
| `.github/workflows/structural-spine.yml`         | New - CI workflow for structural spine                                       |
| `crates/db/tests/generated_moves_transaction.rs` | Fixed to fail (not skip) when `TEST_DATABASE_URL` is present but setup fails |
| `STRUCTURAL_SPINE_MERGE_REPORT.md`               | Updated with CI workflow info                                                |
| `DB_TRANSACTION_TEST_INFRA_REPORT.md`            | Updated with CI info                                                         |
| `DB_TRANSACTION_RLS_CORRECTION_REPORT.md`        | Updated with CI info                                                         |
| `docs/testing/db-integration.md`                 | Updated with CI workflow reference                                           |
| `CI_DB_TRANSACTION_PROOF_REPORT.md`              | New - this report                                                            |

---

## 4. Workflow Added

**File:** `.github/workflows/structural-spine.yml`

### Trigger

```yaml
on:
  push:
    branches:
      - fix/**
  pull_request:
    branches:
      - fix/**
```

### Jobs

#### Job 1: `structural-checks`

| Step              | Command                                                  |
| ----------------- | -------------------------------------------------------- |
| Checkout          | `actions/checkout@v4`                                    |
| pnpm setup        | `pnpm/action-setup@v4` with `version: 10.33.0`           |
| Node setup        | `actions/setup-node@v4` with `node-version: 22`          |
| Rust setup        | `dtolnay/rust-toolchain@stable` with `toolchain: 1.94.0` |
| Install           | `pnpm install --frozen-lockfile`                         |
| Structural check  | `pnpm structural:check`                                  |
| Route parity      | `pnpm route-parity:check`                                |
| Runtime authority | `pnpm runtime-authority:check`                           |
| Type check        | `pnpm typecheck`                                         |
| Rust check        | `cargo check --workspace`                                |

#### Job 2: `db-transaction-test`

| Component           | Value                                                                                            |
| ------------------- | ------------------------------------------------------------------------------------------------ |
| Runs on             | `ubuntu-latest`                                                                                  |
| Service             | `postgres:16`                                                                                    |
| `POSTGRES_DB`       | `raptorflow_test`                                                                                |
| `POSTGRES_USER`     | `testuser`                                                                                       |
| `POSTGRES_PASSWORD` | `testpass`                                                                                       |
| Port                | `5432:5432`                                                                                      |
| Health check        | `pg_isready`                                                                                     |
| `TEST_DATABASE_URL` | `postgres://testuser:testpass@localhost:5432/raptorflow_test`                                    |
| Test command        | `cargo test -p raptorflow-db --test generated_moves_transaction -- --nocapture --test-threads=1` |

---

## 5. DB Test CI-Friendly Fix

### Problem

The test silently skipped when `TEST_DATABASE_URL` was present but:

- Connection failed
- Migrations failed
- Fixtures failed

This meant CI could pass with a broken test setup.

### Fix

Changed test behavior:

| Condition                                      | Old Behavior | New Behavior   |
| ---------------------------------------------- | ------------ | -------------- |
| `TEST_DATABASE_URL` absent                     | Skip         | Skip (correct) |
| `TEST_DATABASE_URL` present + connection fails | Skip         | **Panic/fail** |
| `TEST_DATABASE_URL` present + migrations fail  | Skip         | **Panic/fail** |
| `TEST_DATABASE_URL` present + fixture fails    | Skip         | **Panic/fail** |

The only skip condition is missing `TEST_DATABASE_URL` (local dev without DB).

---

## 6. Local Checks

| Check                            | Result                        |
| -------------------------------- | ----------------------------- |
| `pnpm structural:check`          | ✅ PASS                       |
| `pnpm route-parity:check`        | ✅ PASS                       |
| `pnpm runtime-authority:check`   | ✅ PASS                       |
| `pnpm typecheck`                 | ✅ PASS                       |
| `cargo check --workspace`        | ✅ PASS                       |
| DB test (no `TEST_DATABASE_URL`) | ⏭️ SKIPPED (expected locally) |

---

## 7. Red Team Checks

### Production DB env vars in workflow/test/docs

```bash
rg "RAPTORFLOW_DATABASE_URL|RAPTORFLOW_DIRECT_DATABASE_URL" .github/workflows crates/db/tests docs/testing
```

**Result:** ✅ None found. Only `docker-compose.yml` has them (expected).

### `TEST_DATABASE_URL` usage

```bash
rg "TEST_DATABASE_URL" .github/workflows crates/db/tests docs/testing
```

**Result:** ✅ Used only in:

- `.github/workflows/structural-spine.yml` (DB test job)
- `crates/db/tests/generated_moves_transaction.rs` (test code)
- `docs/testing/db-integration.md` (documentation)

### Skip behavior

```bash
rg "return;|skipping test|skip" crates/db/tests/generated_moves_transaction.rs
```

**Result:** ✅ Skipping only when `TEST_DATABASE_URL` is absent. All other failures now panic.

---

## 8. What Remains Unproven Locally

The DB transaction rollback proof test cannot run locally without a PostgreSQL instance. It will skip with:

```
TEST_DATABASE_URL not set; skipping DB integration test
```

**This is expected.** CI will prove it with the PostgreSQL service container.

---

## 9. CI Proof Expectation

When this branch is merged and CI runs:

1. `structural-checks` job: all 5 checks must pass
2. `db-transaction-test` job:
   - PostgreSQL service starts
   - `pg_isready` confirms DB is ready
   - Tests connect using `TEST_DATABASE_URL`
   - Migrations applied
   - Both tests pass:
     - `generated_moves_transaction_commits_all_rows` ✅
     - `generated_moves_transaction_rolls_back_on_failure` ✅

If any step fails, CI fails loudly (no silent skips when `TEST_DATABASE_URL` is set).

---

## 10. Merge Recommendation

**Merge after CI passes.**

The branch is clean:

- No product behavior changes
- No Prisma reintroduced
- Only CI infrastructure added
- Test behavior fixed to fail properly in CI

Once CI proves the DB transaction rollback proof works, the `fix/structural-spine-pr-hygiene` branch (and this branch) can be merged.
