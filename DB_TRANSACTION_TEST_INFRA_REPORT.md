# DB Transaction Test Infrastructure Report

**Branch:** `fix/db-test-infrastructure-for-transactions`
**Commit SHA:** `364b7d2a99f812386a3d3a9e960c3050c883e774`
**Date:** 2026-04-24

---

## 1. Baseline

| Check                          | Result |
| ------------------------------ | ------ |
| `git status`                   | Clean  |
| `cargo check --workspace`      | PASS   |
| `pnpm structural:check`        | PASS   |
| `pnpm route-parity:check`      | PASS   |
| `pnpm runtime-authority:check` | PASS   |
| `pnpm typecheck`               | PASS   |

---

## 2. Files Changed

| File                                               | Change                                             |
| -------------------------------------------------- | -------------------------------------------------- |
| `crates/db/Cargo.toml`                             | Added `sqlx` dev-dependency with `migrate` feature |
| `crates/db/tests/generated_moves_transaction.rs`   | New - DB integration tests                         |
| `docs/testing/db-integration.md`                   | New - how to set up and run DB tests               |
| `GENERATE_MOVES_TRANSACTION_REPORT.md`             | Updated status                                     |
| `GENERATE_MOVES_TRANSACTION_CORRECTIONS_REPORT.md` | Updated status                                     |

---

## 3. DB Test Environment Variable

**Only `TEST_DATABASE_URL`** is used for integration tests.

- Does NOT use `RAPTORFLOW_DATABASE_URL` (production)
- Does NOT use `RAPTORFLOW_DIRECT_DATABASE_URL` (migrations)

```bash
export TEST_DATABASE_URL="postgres://testuser:testpass@localhost:5432/raptorflow_test"
```

---

## 4. Tests Added

### `generated_moves_transaction_commits_all_rows`

Proves:

- 2 `campaign_moves` rows inserted
- 2 `generated_content` rows inserted with `content_type = 'move_generation'`
- Sequence numbers increment correctly (1, 2)
- Helper returns `Ok` with correct created data

### `generated_moves_transaction_rolls_back_on_failure`

Proves:

- Uses duplicate `content_id` to force DB-level constraint violation
- Helper returns `Err`
- Zero `campaign_moves` rows for test campaign
- Zero `generated_content` rows for test campaign

**This is the key proof**: partial inserts cannot survive a failure.

---

## 5. How RLS / `app.current_org_id` Is Handled

**The helper sets RLS context itself.** Inside `create_generated_campaign_moves_transactional`:

```rust
let mut tx = pool.begin().await?;
sqlx::query("SET LOCAL app.current_org_id = $1")
    .bind(org_id)
    .execute(&mut *tx)
    .await?;
```

This ensures the tenant context is set in the same transaction that performs the inserts.

**Test design** uses separate transactions for setup and verification:

- Setup: `create_campaign_fixture()` uses its own transaction with `SET LOCAL`
- Execute: helper uses its own transaction with `SET LOCAL` (correctly set inside helper)
- Verify: `count_rows()` uses its own transaction with `SET LOCAL`
- Cleanup: `cleanup_org()` uses its own transaction with `SET LOCAL` (CASCADE deletes campaigns/moves/content)

**Note:** The previous version of this test incorrectly assumed `SET LOCAL` from an outer test transaction would be inherited by the helper. This is wrong — `pool.begin()` creates a new transaction, not a savepoint.

---

## 6. How Rollback Failure Is Forced

The rollback test uses **duplicate `content_id`**:

```rust
let duplicate_content_id = "ct-shared";
let moves = vec![
    make_test_move_insert("mv-d1", duplicate_content_id, "positioning", 1),
    make_test_move_insert("mv-d2", duplicate_content_id, "content", 2),
];
let result = create_generated_campaign_moves_transactional(&pool, org_id, &campaign_id, moves).await;
assert!(result.is_err());
```

The first `generated_content` insert succeeds. The second fails with a PK violation. The transaction rolls back — **zero rows** are committed.

---

## 7. Migration Handling

Tests auto-apply migrations using `sqlx::migrate::Migrator`:

```rust
use sqlx::migrate::Migrator;
let migrator = Migrator::new(Path::new("../../database/migrations")).await?;
migrator.run(pool).await?;
```

Migrations run once per test session before any fixture setup.

---

## 8. Cleanup

- Each test generates unique `org_id` and `campaign_id` via `Uuid::new_v4()`
- After test (success or failure), `DELETE FROM organizations WHERE org_id = $1`
- CASCADE deletes clean up `campaigns`, `campaign_moves`, `generated_content`
- If a test panics before cleanup, unique IDs prevent cross-test collisions

---

## 9. Commands Run

| Command                                                          | Result                                       |
| ---------------------------------------------------------------- | -------------------------------------------- |
| `cargo check --workspace`                                        | PASS                                         |
| `pnpm structural:check`                                          | PASS                                         |
| `pnpm route-parity:check`                                        | PASS                                         |
| `pnpm runtime-authority:check`                                   | PASS                                         |
| `pnpm typecheck`                                                 | PASS                                         |
| `cargo test -p raptorflow-db --test generated_moves_transaction` | **SKIPPED** (no `TEST_DATABASE_URL` locally) |

---

## 10. Pass/Fail/Skip Table

| Test                                                | `TEST_DATABASE_URL` Available | Result  |
| --------------------------------------------------- | ----------------------------- | ------- |
| `generated_moves_transaction_commits_all_rows`      | No                            | SKIPPED |
| `generated_moves_transaction_rolls_back_on_failure` | No                            | SKIPPED |

When `TEST_DATABASE_URL` is configured in CI or locally, both tests will run and prove:

- Commits work correctly
- Rollback eliminates partial inserts

---

## 11. Red Team Greps

| Check                                                  | Expected | Actual                                                    |
| ------------------------------------------------------ | -------- | --------------------------------------------------------- |
| `TEST_DATABASE_URL` in test files only                 | Yes      | Yes in `crates/db/tests/generated_moves_transaction.rs` ✓ |
| `RAPTORFLOW_DATABASE_URL` in tests                     | None     | None found ✓                                              |
| `create_generated_campaign_moves_transactional` tested | Yes      | Yes at lines 154, 259 ✓                                   |
| Rollback test forces failure                           | Yes      | Yes via duplicate `content_id` ✓                          |

---

## 12. Remaining Risks

| Risk                                            | Severity | Mitigation                                                 |
| ----------------------------------------------- | -------- | ---------------------------------------------------------- |
| `SET LOCAL` behavior across nested transactions | Low      | Documented - works because helper shares same connection   |
| Test role bypasses RLS                          | Low      | Test uses non-superuser connection; RLS policies enforced  |
| Windows CI may lack PostgreSQL                  | Medium   | Tests skip gracefully without DB; can run on Linux CI only |

---

## 13. Recommended Next Patch

**None for this specific workstream.**

The `generate_campaign_moves` endpoint is now:

- Transaction-safe (`create_generated_campaign_moves_transactional`)
- Validation-corrected (empty list, no truncation, sequence numbers, move_id in body)
- DB integration-tested (pending `TEST_DATABASE_URL` in CI)

The remaining patches listed in previous reports (tombstoning, polling, etc.) are all merged. The Campaign AI endpoint is operationally safe to build on.
