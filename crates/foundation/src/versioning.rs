use raptorflow_db::{FoundationSnapshot, PgPool};
use uuid::Uuid;

pub struct VersioningService;

impl VersioningService {
    pub async fn list_snapshots(
        pool: &PgPool,
        org_id: Uuid,
    ) -> Result<Vec<FoundationSnapshot>, sqlx::Error> {
        let snapshots = raptorflow_db::queries::get_foundation_snapshots(pool, org_id).await?;
        Ok(snapshots)
    }

    pub async fn get_snapshot(
        pool: &PgPool,
        org_id: Uuid,
        snapshot_id: &str,
    ) -> Result<Option<FoundationSnapshot>, sqlx::Error> {
        let snapshots = raptorflow_db::queries::get_foundation_snapshots(pool, org_id).await?;
        Ok(snapshots
            .into_iter()
            .find(|s| s.foundation_snapshot_id == snapshot_id))
    }

    pub async fn restore_snapshot(
        pool: &PgPool,
        org_id: Uuid,
        snapshot_id: &str,
    ) -> Result<String, sqlx::Error> {
        let source = Self::get_snapshot(pool, org_id, snapshot_id)
            .await?
            .ok_or_else(|| sqlx::Error::RowNotFound)?;

        let new_version = source.foundation_version + 1;
        let new_snapshot_id = format!("found-{}-{}", org_id, new_version);

        raptorflow_db::queries::create_foundation_snapshot(
            pool,
            &new_snapshot_id,
            org_id,
            new_version,
            &source.sections,
            "restored",
        )
        .await?;

        Ok(new_snapshot_id)
    }
}
