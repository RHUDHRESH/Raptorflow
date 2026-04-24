# DB Integration Testing

This document describes how to run DB integration tests for RaptorFlow.

## Overview

DB integration tests prove that query helpers work correctly against a real PostgreSQL database, including:

- Row-level security (RLS) via `app.current_org_id()`
- Transaction commit and rollback behavior
- Foreign key cascades

## Prerequisites

### 1. Local PostgreSQL Instance

You need a running PostgreSQL 15+ instance (not PgBouncer — direct connection).

```bash
# Example: start postgres via docker
docker run \
  -e POSTGRES_DB=raptorflow_test \
  -e POSTGRES_USER=testuser \
  -e POSTGRES_PASSWORD=testpass \
  -p 5432:5432 \
  -d postgres:16
```

### 2. Create Database

```sql
CREATE DATABASE raptorflow_test;
```

### 3. Apply Migrations

Migrations live in `database/migrations/` (the authoritative source). They are auto-applied by the test harness, but you can also apply them manually:

```bash
psql "postgres://testuser:testpass@localhost:5432/raptorflow_test" \
  -f database/migrations/0001_initial.sql

psql "postgres://testuser:testpass@localhost:5432/raptorflow_test" \
  -f database/migrations/0002_something.sql

# ... etc
```

### 4. Set Environment Variable

```bash
export TEST_DATABASE_URL="postgres://testuser:testpass@localhost:5432/raptorflow_test"
```

## Running DB Integration Tests

### Run All DB Tests

```bash
TEST_DATABASE_URL=postgres://testuser:testpass@localhost:5432/raptorflow_test \
  cargo test -p raptorflow-db --test generated_moves_transaction -- --nocapture
```

### Run with Detailed Output

```bash
TEST_DATABASE_URL=postgres://testuser:testpass@localhost:5432/raptorflow_test \
  cargo test -p raptorflow-db --test generated_moves_transaction \
  -- --nocapture --test-threads=1
```

## Tests Available

### `generated_moves_transaction_commits_all_rows`

Proves that `create_generated_campaign_moves_transactional` correctly:

1. Inserts all campaign_moves rows
2. Inserts all generated_content rows with correct content_type
3. Returns created rows with correct sequence numbers

### `generated_moves_transaction_rolls_back_on_failure`

Proves that the transaction rolls back correctly when a DB-level constraint violation occurs (duplicate `content_id`).

**Expected behavior:**

- Helper returns `Err`
- Zero rows in `campaign_moves` for the test campaign
- Zero rows in `generated_content` for the test campaign

This is the key proof that partial inserts cannot survive a failure.

## How RLS Is Handled

Tenant-scoped tables use RLS policies like:

```sql
CREATE POLICY campaign_moves_tenant_isolation ON campaign_moves
  USING (org_id = app.current_org_id())
  WITH CHECK (org_id = app.current_org_id());
```

**The helper sets RLS context itself.** Inside `create_generated_campaign_moves_transactional`:

```rust
let mut tx = pool.begin().await?;
sqlx::query("SET LOCAL app.current_org_id = $1")
    .bind(org_id)
    .execute(&mut *tx)
    .await?;
```

This ensures the tenant context is set in the same transaction that performs the inserts. The helper commits only after all inserts succeed; if any insert fails, the transaction rolls back when `tx` is dropped.

**Test setup and verification** use separate transactions with their own `SET LOCAL` calls:

```rust
// Setup: org and campaign fixtures
let mut tx = pool.begin().await?;
sqlx::query("SET LOCAL app.current_org_id = $1").bind(org_id).execute(&mut *tx).await?;
// ... inserts ...
tx.commit().await?;

// Verification: count rows with RLS
let mut tx = pool.begin().await?;
sqlx::query("SET LOCAL app.current_org_id = $1").bind(org_id).execute(&mut *tx).await?;
// ... selects ...
tx.rollback().await?;
```

If you see RLS errors when running tests locally, ensure:

- The migrations have been applied (including RLS policies)
- The test role is not a superuser (which bypasses RLS)
- `SET LOCAL` was called before any tenant-scoped query

## Test Fixtures and Cleanup

Each test:

1. Generates unique org_id and campaign_id via `Uuid::new_v4()`
2. Inserts an org fixture
3. Inserts a campaign fixture
4. Runs the test
5. Deletes the org (cascades to campaigns, moves, content)

If a test panics/fails before cleanup, unique IDs prevent collisions with subsequent runs.

## Warnings

**NEVER** point `TEST_DATABASE_URL` at production or staging. Always use an isolated test database.

**Do not use PgBouncer** for `TEST_DATABASE_URL`. The tests use `SET LOCAL` which requires a direct PostgreSQL connection, not a connection pooler in transaction mode.

## CI Integration

In CI, a GitHub Actions workflow runs the DB transaction tests. See `.github/workflows/structural-spine.yml`.

The workflow:

1. Starts a `postgres:16` service container
2. Waits for `pg_isready` to confirm DB is ready
3. Sets `TEST_DATABASE_URL` environment variable
4. Runs `cargo test -p raptorflow-db --test generated_moves_transaction -- --nocapture --test-threads=1`

### Test Behavior in CI

**If `TEST_DATABASE_URL` is absent** (local dev without DB): test skips gracefully.

**If `TEST_DATABASE_URL` is present but connection/migration/fixtures fail** (broken CI setup): test **fails loudly** (panics), not silently skips.

This ensures CI catches broken test infrastructure immediately.
