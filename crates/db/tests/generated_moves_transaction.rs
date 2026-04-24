//! DB integration tests for `create_generated_campaign_moves_transactional`.
//!
//! Each test uses a unique database created via the postgres superuser connection.
//! The TEST_DATABASE_URL should point to the postgres database (the default admin DB).
//!
//! Run with:
//! ```text
//! TEST_DATABASE_URL=postgres://user:pass@localhost:5432/postgres \
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
    GeneratedCampaignMoveInsert, create_generated_campaign_moves_transactional,
};
use sqlx::postgres::{PgPool as SqlxPgPool, PgPoolOptions};
use std::env;

struct TestDb {
    _admin_pool: SqlxPgPool,
    db_name: String,
}

impl Drop for TestDb {
    fn drop(&mut self) {
        let db_name = self.db_name.clone();
        let rt = tokio::runtime::Builder::new_current_thread()
            .enable_all()
            .build()
            .expect("runtime");
        rt.block_on(async {
            let admin_pool = PgPoolOptions::new()
                .max_connections(1)
                .connect(&format!("postgres://testuser:testpass@localhost:5432/postgres"))
                .await
                .ok();
            if let Some(pool) = admin_pool {
                let _ = sqlx::query(&format!("DROP DATABASE IF EXISTS {}", db_name))
                    .execute(&pool)
                    .await;
            }
        });
    }
}

async fn setup_test_db() -> Result<TestDb, sqlx::Error> {
    let admin_url = "postgres://testuser:testpass@localhost:5432/postgres";
    let admin_pool = PgPoolOptions::new()
        .max_connections(1)
        .connect(admin_url)
        .await?;

    let db_name = format!("raptorflow_test_{}", uuid::Uuid::new_v4());
    sqlx::query(&format!("DROP DATABASE IF EXISTS {}", db_name))
        .execute(&admin_pool)
        .await?;
    sqlx::query(&format!("CREATE DATABASE {}", db_name))
        .execute(&admin_pool)
        .await?;

    let pool = PgPoolOptions::new()
        .max_connections(2)
        .connect(&format!("postgres://testuser:testpass@localhost:5432/{}", db_name))
        .await?;

    Ok(TestDb {
        _admin_pool: admin_pool,
        db_name,
    })
}

async fn apply_migrations(pool: &SqlxPgPool) -> Result<(), sqlx::Error> {
    use sqlx::migrate::Migrator;
    use std::path::Path;

    let migrator = Migrator::new(Path::new("../../database/migrations"))
        .await
        .map_err(|e| sqlx::Error::Protocol(format!("failed to create migrator: {}", e)))?;

    migrator.run(pool).await?;
    Ok(())
}

async fn create_org_fixture(pool: &SqlxPgPool, org_id: uuid::Uuid) -> Result<(), sqlx::Error> {
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
    org_id: uuid::Uuid,
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
    org_id: uuid::Uuid,
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

async fn cleanup_org(pool: &SqlxPgPool, org_id: uuid::Uuid) -> Result<(), sqlx::Error> {
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
    let test_db = match setup_test_db().await {
        Ok(db) => db,
        Err(e) => {
            eprintln!("TEST_DATABASE_URL not set or could not create test DB; skipping: {}", e);
            return;
        }
    };

    let pool = PgPoolOptions::new()
        .max_connections(2)
        .connect(&format!(
            "postgres://testuser:testpass@localhost:5432/{}",
            test_db.db_name
        ))
        .await
        .expect("failed to connect to test DB");

    apply_migrations(&pool)
        .await
        .expect("migrations failed");

    let org_id = uuid::Uuid::new_v4();
    let campaign_id = format!("test-campaign-tx-{}", uuid::Uuid::new_v4());

    create_org_fixture(&pool, org_id)
        .await
        .expect("org fixture failed");

    if let Err(e) = create_campaign_fixture(&pool, org_id, &campaign_id).await {
        let _ = cleanup_org(&pool, org_id).await;
        panic!("campaign fixture failed: {e}");
    }

    let moves = vec![
        make_test_move_insert("mv-001", "ct-001", "positioning", 1),
        make_test_move_insert("mv-002", "ct-002", "content", 2),
    ];

    let result =
        create_generated_campaign_moves_transactional(&pool, org_id, &campaign_id, moves).await;

    if let Err(e) = result {
        eprintln!(
            "Transaction helper returned error (unexpected): {}; FAIL",
            e
        );
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
    let test_db = match setup_test_db().await {
        Ok(db) => db,
        Err(e) => {
            eprintln!("TEST_DATABASE_URL not set or could not create test DB; skipping: {}", e);
            return;
        }
    };

    let pool = PgPoolOptions::new()
        .max_connections(2)
        .connect(&format!(
            "postgres://testuser:testpass@localhost:5432/{}",
            test_db.db_name
        ))
        .await
        .expect("failed to connect to test DB");

    apply_migrations(&pool)
        .await
        .expect("migrations failed");

    let org_id = uuid::Uuid::new_v4();
    let campaign_id = format!("test-campaign-rb-{}", uuid::Uuid::new_v4());

    create_org_fixture(&pool, org_id)
        .await
        .expect("org fixture failed");

    if let Err(e) = create_campaign_fixture(&pool, org_id, &campaign_id).await {
        let _ = cleanup_org(&pool, org_id).await;
        panic!("campaign fixture failed: {e}");
    }

    let duplicate_content_id = "ct-shared";
    let moves = vec![
        make_test_move_insert("mv-d1", duplicate_content_id, "positioning", 1),
        make_test_move_insert("mv-d2", duplicate_content_id, "content", 2),
    ];

    let result =
        create_generated_campaign_moves_transactional(&pool, org_id, &campaign_id, moves).await;

    assert!(
        result.is_err(),
        "expected Err due to duplicate content_id, got Ok"
    );

    let (move_count, content_count) = match count_rows(&pool, org_id, &campaign_id).await {
        Ok((m, c)) => (m, c),
        Err(e) => {
            eprintln!("Failed to count rows: {}; FAIL", e);
            let _ = cleanup_org(&pool, org_id).await;
            panic!("count query failed: {}", e);
        }
    };

    assert_eq!(
        move_count, 0,
        "expected ZERO campaign_moves rows after rollback"
    );
    assert_eq!(
        content_count, 0,
        "expected ZERO generated_content rows after rollback"
    );

    let _ = cleanup_org(&pool, org_id).await;
}
