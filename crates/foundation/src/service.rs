use crate::models::FoundationData;
use anyhow::Result;
use chrono::Utc;
use raptorflow_avatars::seeding::seed_org_avatars;
use raptorflow_db::PgPool;
use raptorflow_db::models::FoundationSnapshot;
use uuid::Uuid;

pub struct FoundationService;

impl FoundationService {
    pub async fn get_current(
        pool: &PgPool,
        org_id: Uuid,
    ) -> Result<Option<FoundationSnapshot>, sqlx::Error> {
        let snapshots = raptorflow_db::queries::get_foundation_snapshots(pool, org_id).await?;
        Ok(snapshots.into_iter().next())
    }

    pub async fn create_initial(
        pool: &PgPool,
        org_id: Uuid,
        data: FoundationData,
    ) -> anyhow::Result<String> {
        let snapshot_id = format!("found-{}-{}", org_id, 1);
        let sections = serde_json::to_value(&data).unwrap_or(serde_json::json!({}));
        let now = Utc::now();

        raptorflow_db::queries::create_foundation_snapshot(
            pool,
            &snapshot_id,
            org_id,
            1,
            &sections,
            "manual",
        )
        .await?;

        let foundation_snapshot = FoundationSnapshot {
            foundation_snapshot_id: snapshot_id.clone(),
            org_id,
            foundation_version: 1,
            sections,
            source: "manual".to_string(),
            created_at: now,
            updated_at: now,
        };

        match seed_org_avatars(pool, org_id, Some(&foundation_snapshot)).await {
            Ok(report) => {
                tracing::info!(
                    org_id = %org_id,
                    avatar_count = report.seeded.len(),
                    "avatar seeding complete"
                );
            }
            Err(e) => {
                tracing::error!(org_id = %org_id, error = %e, "avatar seeding failed");
                return Err(anyhow::anyhow!("avatar seeding failed: {}", e));
            }
        }

        Ok(snapshot_id)
    }

    pub async fn update_section(
        pool: &PgPool,
        org_id: Uuid,
        section: &str,
        section_data: serde_json::Value,
    ) -> Result<i32, sqlx::Error> {
        let current = Self::get_current(pool, org_id).await?;
        let new_version = current
            .as_ref()
            .map(|s| s.foundation_version + 1)
            .unwrap_or(1);
        let snapshot_id = format!("found-{}-{}", org_id, new_version);

        let mut sections: serde_json::Value = current
            .as_ref()
            .and_then(|s| s.sections.as_object())
            .map(|obj| serde_json::to_value(obj).unwrap_or(serde_json::json!({})))
            .unwrap_or(serde_json::json!({}));

        if let Some(obj) = sections.as_object_mut() {
            obj.insert(section.to_string(), section_data);
        }

        raptorflow_db::queries::create_foundation_snapshot(
            pool,
            &snapshot_id,
            org_id,
            new_version,
            &sections,
            "manual",
        )
        .await?;

        Ok(new_version)
    }

    pub async fn get_section(
        pool: &PgPool,
        org_id: Uuid,
        section: &str,
    ) -> Result<Option<serde_json::Value>, sqlx::Error> {
        let current = Self::get_current(pool, org_id).await?;
        Ok(current.and_then(|s| {
            s.sections
                .get(section)
                .cloned()
        }))
    }
}
