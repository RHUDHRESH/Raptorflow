//! DB integration tests for `create_generated_campaign_moves_transactional`.
//!
//! Requires `TEST_DATABASE_URL` environment variable pointing at a live PostgreSQL DB.
//! Migrations are auto-applied from `database/migrations/` before tests run.
//!
//! Run with:
//! ```text
//! TEST_DATABASE_URL=postgres://user:pass@localhost:5432/test_db \
//!   cargo test -p raptorflow-db --test generated_moves_transaction -- --nocapture --test-threads=1
//! ```
//!
//! ## RLS note
//! Tenant-scoped tables use `app.current_org_id()` via RLS WITH CHECK policies.
//! The helper (`create_generated_campaign_moves_transactional`) sets `SET LOCAL app.current_org_id`
//! at the start of its own transaction before performing tenant-scoped inserts.
//!
//! Setup and verification use separate transactions with their own `SET LOCAL` calls.

use raptorflow_db::queries::{
    create_generated_campaign_moves_transactional, GeneratedCampaignMoveInsert,
};
use sqlx::postgres::{PgPool as SqlxPgPool, PgPoolOptions};
use std::env;
use uuid::Uuid;

fn get_test_db_url() -> Option<String> {
    env::var("TEST_DATABASE_URL").ok()
}

async fn setup_test_pool(database_url: &str) -> Result<SqlxPgPool, sqlx::Error> {
    PgPoolOptions::new()
        .max_connections(2)
        .connect(database_url)
        .await
}

async fn apply_migrations(pool: &SqlxPgPool) -> Result<(), sqlx::Error> {
    use sqlx::migrate::Migrator;
    use std::path::Path;

    let migrator = Migrator::new(Path::new("../../database/migrations"))
        .await
        .map_err(|e| {
            sqlx::Error::Protocol(format!("failed to create migrator: {}", e))
        })?;

    migrator.run(pool).await?;
    Ok(())
}

async fn create_org_fixture(pool: &SqlxPgPool, org_id: Uuid) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        INSERT INTO organizations (org_id, name, subscription_status, foundation_version, foundation_complete, created_at, updated_at)
        VALUES ($1, 'Test Org', 'active', 1, false, now(), now())
        ON CONFLICT (org_id) DO NOTHING
        "#,
    )
    .bind(org_id)
    .execute(pool)
    .await?;
    Ok(())
}

async fn create_campaign_fixture(
    pool: &SqlxPgPool,
    org_id: Uuid,
    campaign_id: &str,
) -> Result<(), sqlx::Error> {
    let mut tx = pool.begin().await?;

    sqlx::query("SET LOCAL app.current_org_id = $1")
        .bind(org_id)
        .execute(&mut *tx)
        .await?;

    sqlx::query(
        r#"
        INSERT INTO campaigns (campaign_id, org_id, name, goal, status, created_at, updated_at)
        VALUES ($1, $2, 'Test Campaign', 'Test Goal', 'draft', now(), now())
        "#,
    )
    .bind(campaign_id)
    .bind(org_id)
    .execute(&mut *tx)
    .await?;

    tx.commit().await?;
    Ok(())
}

async fn count_rows(
    pool: &SqlxPgPool,
    org_id: Uuid,
    campaign_id: &str,
) -> Result<(i64, i64), sqlx::Error> {
    let mut tx = pool.begin().await?;

    sqlx::query("SET LOCAL app.current_org_id = $1")
        .bind(org_id)
        .execute(&mut *tx)
        .await?;

    let move_count: (i64,) = sqlx::query_as(
        "SELECT COUNT(*) FROM campaign_moves WHERE campaign_id = $1 AND org_id = $2",
    )
    .bind(campaign_id)
    .bind(org_id)
    .fetch_one(&mut *tx)
    .await?;

    let content_count: (i64,) = sqlx::query_as(
        "SELECT COUNT(*) FROM generated_content WHERE campaign_id = $1 AND org_id = $2 AND content_type = 'move_generation'",
    )
    .bind(campaign_id)
    .bind(org_id)
    .fetch_one(&mut *tx)
    .await?;

    tx.rollback().await?;
    Ok((move_count.0, content_count.0))
}

async fn cleanup_org(pool: &SqlxPgPool, org_id: Uuid) -> Result<(), sqlx::Error> {
    let mut tx = pool.begin().await?;

    sqlx::query("SET LOCAL app.current_org_id = $1")
        .bind(org_id)
        .execute(&mut *tx)
        .await?;

    sqlx::query("DELETE FROM organizations WHERE org_id = $1")
        .bind(org_id)
        .execute(&mut *tx)
        .await?;

    tx.commit().await?;
    Ok(())
}

fn make_test_move_insert(
    move_id: &str,
    content_id: &str,
    move_type: &str,
    seq: i32,
) -> GeneratedCampaignMoveInsert {
    GeneratedCampaignMoveInsert {
        move_id: move_id.to_string(),
        content_id: content_id.to_string(),
        move_type: move_type.to_string(),
        sequence_number: seq,
        content_body: serde_json::json!({
            "move_id": move_id,
            "description": "Test strategic move description",
            "expected_impact": "Test expected impact that is long enough",
            "confidence": 0.85,
            "sequence_number": seq,
        }),
    }
}

#[tokio::test]
async fn generated_moves_transaction_commits_all_rows() {
    let Some(database_url) = get_test_db_url() else {
        eprintln!("TEST_DATABASE_URL not set; skipping DB integration test");
        return;
    };

    let pool = match setup_test_pool(&database_url).await {
        Ok(p) => p,
        Err(e) => {
            eprintln!("Failed to connect to test DB: {}; skipping test", e);
            return;
        }
    };

    if let Err(e) = apply_migrations(&pool).await {
        eprintln!("Failed to apply migrations: {}; skipping test", e);
        return;
    }

    let org_id = Uuid::new_v4();
    let campaign_id = format!("test-campaign-tx-{}", Uuid::new_v4());

    if let Err(e) = create_org_fixture(&pool, org_id).await {
        eprintln!("Failed to create org fixture: {}; skipping test", e);
        return;
    }

    if let Err(e) = create_campaign_fixture(&pool, org_id, &campaign_id).await {
        eprintln!("Failed to create campaign fixture: {}; skipping test", e);
        let _ = cleanup_org(&pool, org_id).await;
        return;
    }

    let moves = vec![
        make_test_move_insert("mv-001", "ct-001", "positioning", 1),
        make_test_move_insert("mv-002", "ct-002", "content", 2),
    ];

    let result = create_generated_campaign_moves_transactional(&pool, org_id, &campaign_id, moves).await;

    if let Err(e) = result {
        eprintln!("Transaction helper returned error (unexpected): {}; FAIL", e);
        let _ = cleanup_org(&pool, org_id).await;
        panic!("expected Ok but got Err: {}", e);
    }

    let created = result.unwrap();
    assert_eq!(created.len(), 2, "expected 2 created moves");
    assert_eq!(created[0].sequence_number, 1);
    assert_eq!(created[1].sequence_number, 2);

    let (move_count, content_count) = match count_rows(&pool, org_id, &campaign_id).await {
        Ok((m, c)) => (m, c),
        Err(e) => {
            eprintln!("Failed to count rows: {}; FAIL", e);
            let _ = cleanup_org(&pool, org_id).await;
            panic!("count query failed: {}", e);
        }
    };

    assert_eq!(move_count, 2, "expected 2 campaign_moves rows");
    assert_eq!(content_count, 2, "expected 2 generated_content rows");

    let _ = cleanup_org(&pool, org_id).await;
}

#[tokio::test]
async fn generated_moves_transaction_rolls_back_on_failure() {
    let Some(database_url) = get_test_db_url() else {
        eprintln!("TEST_DATABASE_URL not set; skipping DB integration test");
        return;
    };

    let pool = match setup_test_pool(&database_url).await {
        Ok(p) => p,
        Err(e) => {
            eprintln!("Failed to connect to test DB: {}; skipping test", e);
            return;
        }
    };

    if let Err(e) = apply_migrations(&pool).await {
        eprintln!("Failed to apply migrations: {}; skipping test", e);
        return;
    }

    let org_id = Uuid::new_v4();
    let campaign_id = format!("test-campaign-rb-{}", Uuid::new_v4());

    if let Err(e) = create_org_fixture(&pool, org_id).await {
        eprintln!("Failed to create org fixture: {}; skipping test", e);
        return;
    }

    if let Err(e) = create_campaign_fixture(&pool, org_id, &campaign_id).await {
        eprintln!("Failed to create campaign fixture: {}; skipping test", e);
        let _ = cleanup_org(&pool, org_id).await;
        return;
    }

    let duplicate_content_id = "ct-shared";
    let moves = vec![
        make_test_move_insert("mv-d1", duplicate_content_id, "positioning", 1),
        make_test_move_insert("mv-d2", duplicate_content_id, "content", 2),
    ];

    let result = create_generated_campaign_moves_transactional(&pool, org_id, &campaign_id, moves).await;

    assert!(result.is_err(), "expected Err due to duplicate content_id, got Ok");

    let (move_count, content_count) = match count_rows(&pool, org_id, &campaign_id).await {
        Ok((m, c)) => (m, c),
        Err(e) => {
            eprintln!("Failed to count rows: {}; FAIL", e);
            let _ = cleanup_org(&pool, org_id).await;
            panic!("count query failed: {}", e);
        }
    };

    assert_eq!(move_count, 0, "expected ZERO campaign_moves rows after rollback");
    assert_eq!(content_count, 0, "expected ZERO generated_content rows after rollback");

    let _ = cleanup_org(&pool, org_id).await;
}
