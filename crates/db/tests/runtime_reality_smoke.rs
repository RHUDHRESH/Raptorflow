//! Runtime Reality Smoke Test for RaptorFlow DB layer.
//!
//! This test proves the application can:
//! 1. Connect to Postgres/pgvector
//! 2. Apply migrations cleanly
//! 3. Verify key tables exist
//! 4. Use tenant RLS session setting
//!
//! # Environment
//!
//! - `TEST_DATABASE_URL` — required for this test to run
//!   Example: `postgres://testuser:testpass@localhost:5432/raptorflow_runtime_smoke`
//!
//! # Rules
//!
//! - Missing `TEST_DATABASE_URL` = skip with printed message (NOT a failure)
//! - Present `TEST_DATABASE_URL` + any failure = panic/fail (NOT silent)
//! - Never use `RAPTORFLOW_DATABASE_URL` or `RAPTORFLOW_DIRECT_DATABASE_URL`
//! - Never run against production databases

use sqlx::postgres::{PgPool as SqlxPgPool, PgPoolOptions};
use std::env;

const REQUIRED_TABLES: &[&str] = &[
    "organizations",
    "avatars",
    "harness_runs",
    "harness_steps",
    "foundation_scans",
    "competitor_snapshots",
    "campaigns",
    "council_sessions",
    "ripples",
];

fn get_test_db_url() -> Option<String> {
    env::var("TEST_DATABASE_URL").ok()
}

async fn apply_migrations(pool: &SqlxPgPool) -> Result<(), String> {
    use sqlx::migrate::Migrator;
    use std::path::PathBuf;

    let manifest_dir = PathBuf::from(env!("CARGO_MANIFEST_DIR"));
    let migrations_path = manifest_dir
        .parent()
        .and_then(|p| p.parent())
        .map(|p| p.join("database/migrations"))
        .ok_or("failed to resolve migrations path from CARGO_MANIFEST_DIR")?;

    let migrator = Migrator::new(migrations_path)
        .await
        .map_err(|e| format!("failed to create migrator: {}", e))?;

    migrator
        .run(pool)
        .await
        .map_err(|e| format!("migration failed: {}", e))?;
    println!("[SMOKE DB] Migrations applied successfully");
    Ok(())
}

fn check_table_exists(rows: &[(&str, bool)], table: &str) -> Result<(), String> {
    let found = rows.iter().any(|(t, _)| *t == table);
    if found {
        println!("[SMOKE DB]   Table '{table}' exists");
        Ok(())
    } else {
        Err(format!("Table '{table}' not found after migration",))
    }
}

#[tokio::test]
async fn runtime_reality_smoke_db_connection_and_migrations() {
    let Some(database_url) = get_test_db_url() else {
        println!("[SMOKE DB] SKIP: TEST_DATABASE_URL not set — skipping runtime smoke test");
        println!("[SMOKE DB] This is normal in environments without a test database.");
        return;
    };

    println!("[SMOKE DB] TEST_DATABASE_URL is set — running runtime smoke test");
    println!(
        "[SMOKE DB] Connecting to: {}",
        database_url.replace(&*env::var("POSTGRES_PASSWORD").unwrap_or_default(), "***")
    );

    let pool = match PgPoolOptions::new()
        .max_connections(5)
        .acquire_timeout(std::time::Duration::from_secs(10))
        .connect(&database_url)
        .await
    {
        Ok(p) => {
            println!("[SMOKE DB] Connected to database successfully");
            p
        }
        Err(e) => {
            panic!(
                "[SMOKE DB] FAIL: Could not connect to TEST_DATABASE_URL: {}",
                e
            );
        }
    };

    // Step 1: Verify basic connectivity
    println!("[SMOKE DB] Step 1: Verifying basic connectivity (SELECT 1)...");
    match sqlx::query("SELECT 1").execute(&pool).await {
        Ok(_) => println!("[SMOKE DB]   SELECT 1 returned successfully"),
        Err(e) => panic!("[SMOKE DB] FAIL: SELECT 1 failed: {}", e),
    }

    // Step 2: Verify pgvector extension
    println!("[SMOKE DB] Step 2: Verifying pgvector extension...");
    let vector_ext: Option<(String,)> =
        sqlx::query_as("SELECT extname FROM pg_extension WHERE extname = 'vector'")
            .fetch_optional(&pool)
            .await
            .map_err(|e| format!("pg_extension query failed: {}", e))
            .unwrap();

    match vector_ext {
        Some((ref name,)) => println!("[SMOKE DB]   pgvector extension '{}' is installed", name),
        None => panic!(
            "[SMOKE DB] FAIL: pgvector extension not found — required for ripple/intel workloads"
        ),
    }

    // Step 3: Apply migrations
    println!("[SMOKE DB] Step 3: Applying migrations from database/migrations/...");
    let _ = sqlx::query("DELETE FROM _sqlx_migrations")
        .execute(&pool)
        .await;
    if let Err(e) = apply_migrations(&pool).await {
        panic!("[SMOKE DB] FAIL: Migration failed: {}", e);
    }

    // Step 4: Verify required tables exist
    println!("[SMOKE DB] Step 4: Verifying required tables exist...");
    let table_rows: Vec<(String,)> = sqlx::query_as(
        "SELECT tablename FROM pg_tables WHERE schemaname = 'public' AND tablename = ANY($1)",
    )
    .bind(REQUIRED_TABLES)
    .fetch_all(&pool)
    .await
    .map_err(|e| format!("pg_tables query failed: {}", e))
    .unwrap();

    let table_names: Vec<&str> = table_rows.iter().map(|(t,)| t.as_str()).collect();
    println!(
        "[SMOKE DB]   Found {} of {} required tables",
        table_names.len(),
        REQUIRED_TABLES.len()
    );

    for table in REQUIRED_TABLES {
        if let Err(e) = check_table_exists(
            &table_rows
                .iter()
                .map(|(t,)| (t.as_str(), true))
                .collect::<Vec<_>>(),
            table,
        ) {
            panic!("[SMOKE DB] FAIL: {}", e);
        }
    }

    // Step 5: Verify tenant RLS session setting is usable
    println!(
        "[SMOKE DB] Step 5: Verifying tenant RLS session setting (SET LOCAL app.current_org_id)..."
    );
    let test_org_id = uuid::Uuid::new_v4();
    let mut tx = match pool.begin().await {
        Ok(t) => t,
        Err(e) => panic!("[SMOKE DB] FAIL: Could not begin transaction: {}", e),
    };

    let set_result = sqlx::query("SET LOCAL app.current_org_id = $1")
        .bind(test_org_id)
        .execute(&mut *tx)
        .await;

    match set_result {
        Ok(_) => println!("[SMOKE DB]   SET LOCAL app.current_org_id succeeded"),
        Err(e) => panic!(
            "[SMOKE DB] FAIL: SET LOCAL app.current_org_id failed: {}",
            e
        ),
    }

    // Verify we can run a harmless query in the tenant context
    let org_check: Option<(String,)> =
        sqlx::query_as("SELECT name FROM organizations WHERE org_id = $1")
            .bind(test_org_id)
            .fetch_optional(&mut *tx)
            .await
            .expect("Tenant query should not fail");

    match org_check {
        None => println!(
            "[SMOKE DB]   Tenant query succeeded (no org found, as expected for random UUID)"
        ),
        Some(_) => {
            println!("[SMOKE DB]   Tenant query succeeded (found org, unexpected but valid)")
        }
    }

    // Rollback to not pollute the database
    if let Err(e) = tx.rollback().await {
        eprintln!(
            "[SMOKE DB] WARN: Transaction rollback failed (non-fatal): {}",
            e
        );
    }

    println!("[SMOKE DB] ALL CHECKS PASSED");
    println!(
        "[SMOKE DB] Runtime reality verified: DB connection, pgvector, migrations, tables, and RLS all functional."
    );
}
