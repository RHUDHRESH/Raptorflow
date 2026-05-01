use sqlx::postgres::{PgPool as SqlxPgPool, PgPoolOptions, Postgres};
use std::time::Duration;
use uuid::Uuid;

pub type PgPool = SqlxPgPool;

/// Build the application database pool (goes through PgBouncer).
/// Uses RAPTORFLOW_DATABASE_URL — port 6432 in production, 6432 locally.
pub async fn create_app_pool(database_url: &str) -> Result<PgPool, sqlx::Error> {
    PgPoolOptions::new()
        .max_connections(20)
        .min_connections(2)
        .acquire_timeout(Duration::from_secs(5))
        .connect(database_url)
        .await
}

/// Build a direct pool for migrations only.
/// Uses RAPTORFLOW_DIRECT_DATABASE_URL — port 5432 always.
pub async fn create_migration_pool(direct_database_url: &str) -> Result<PgPool, sqlx::Error> {
    PgPoolOptions::new()
        .max_connections(2)
        .connect(direct_database_url)
        .await
}

/// Verify the pool is reachable. Used in health checks.
pub async fn ping(pool: &PgPool) -> Result<(), sqlx::Error> {
    sqlx::query("SELECT 1").execute(pool).await?;
    Ok(())
}

pub async fn create_pool(database_url: &str) -> Result<PgPool, sqlx::Error> {
    PgPoolOptions::new()
        .max_connections(20)
        .min_connections(2)
        .acquire_timeout(Duration::from_secs(30))
        .idle_timeout(Duration::from_secs(600))
        .connect(database_url)
        .await
}

#[derive(Clone)]
pub struct TenantDbPool {
    inner: PgPool,
}

impl TenantDbPool {
    pub fn new(pool: PgPool) -> Self {
        Self { inner: pool }
    }

    pub async fn acquire_for_tenant(
        &self,
        org_id: Uuid,
    ) -> Result<sqlx::pool::PoolConnection<Postgres>, sqlx::Error> {
        let mut conn = self.inner.acquire().await?;
        sqlx::query("SET SESSION app.current_org_id = $1")
            .bind(org_id)
            .execute(&mut *conn)
            .await?;
        Ok(conn)
    }

    pub fn pool(&self) -> &PgPool {
        &self.inner
    }
}

impl std::fmt::Debug for TenantDbPool {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        f.debug_struct("TenantDbPool").finish()
    }
}
