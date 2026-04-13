use sqlx::postgres::{PgPool as SqlxPgPool, PgPoolOptions};
use std::time::Duration;

pub type PgPool = SqlxPgPool;

pub async fn create_pool(database_url: &str) -> Result<PgPool, sqlx::Error> {
    PgPoolOptions::new()
        .max_connections(20)
        .min_connections(2)
        .acquire_timeout(Duration::from_secs(30))
        .idle_timeout(Duration::from_secs(600))
        .connect(database_url)
        .await
}

pub async fn set_tenant_context(pool: &PgPool, org_id: uuid::Uuid) -> Result<(), sqlx::Error> {
    sqlx::query("SET LOCAL app.current_org_id = $1")
        .bind(org_id)
        .execute(pool)
        .await?;
    Ok(())
}
