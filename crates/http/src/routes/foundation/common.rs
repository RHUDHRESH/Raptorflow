pub(super) use axum::{
    Json,
    extract::{Extension, Path, Query},
    http::StatusCode,
};
pub(super) use chrono::Utc;
pub(super) use raptorflow_acquisition::{HtmlParser, HttpFetcher, UrlNormalizer};
pub(super) use raptorflow_avatars::seeding::seed_org_avatars;
pub(super) use raptorflow_db::models::FoundationSnapshot;
pub(super) use raptorflow_db::queries as db;
pub(super) use raptorflow_foundation::{FoundationData, FoundationService};
pub(super) use serde::{Deserialize, Serialize};
pub(super) use sqlx::FromRow;
pub(super) use std::sync::Arc;
pub(super) use ulid::Ulid;
pub(super) use uuid::Uuid;

pub(super) use crate::middleware::{AppState, auth::AuthContext};

pub type AppResult<T> = Result<T, (StatusCode, Json<serde_json::Value>)>;

#[derive(Debug, Serialize, Deserialize)]
pub struct FoundationResponse {
    pub id: String,
    pub org_id: Uuid,
    pub version: i32,
    pub sections: serde_json::Value,
    pub updated_at: String,
    pub source: String,
}

#[derive(Debug, Deserialize)]
pub struct UpdateSectionRequest {
    pub data: serde_json::Value,
}

#[derive(Debug, Deserialize)]
pub struct CreateSnapshotRequest {
    pub source: Option<String>,
}

#[derive(Debug, FromRow)]
pub(super) struct SnapshotRow {
    pub(super) foundation_snapshot_id: String,
    pub(super) org_id: Uuid,
    pub(super) foundation_version: i32,
    pub(super) sections: serde_json::Value,
    pub(super) source: String,
    pub(super) updated_at: chrono::DateTime<chrono::Utc>,
}

pub(super) fn internal_error<E: std::fmt::Display>(e: E) -> (StatusCode, Json<serde_json::Value>) {
    tracing::error!("Foundation route error: {e}");
    (
        StatusCode::INTERNAL_SERVER_ERROR,
        Json(serde_json::json!({ "error": "foundation_internal_error" })),
    )
}

pub(super) fn bad_request(message: &str) -> (StatusCode, Json<serde_json::Value>) {
    (
        StatusCode::BAD_REQUEST,
        Json(serde_json::json!({ "error": message })),
    )
}

pub(super) fn not_found(message: &str) -> (StatusCode, Json<serde_json::Value>) {
    (
        StatusCode::NOT_FOUND,
        Json(serde_json::json!({ "error": message })),
    )
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub(super) struct PositioningTemplateComponents {
    pub(super) for_who: String,
    pub(super) who_problem: String,
    pub(super) brand: String,
    pub(super) category: String,
    pub(super) differentiation: String,
    pub(super) because: String,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
pub(super) struct PositioningDraftResponse {
    pub(super) statement: String,
    pub(super) template_components: PositioningTemplateComponents,
    pub(super) quality_score: f64,
    pub(super) quality_feedback: String,
}

pub(super) fn db_pool(state: &Arc<AppState>) -> AppResult<&sqlx::PgPool> {
    state.db_pool.as_deref().ok_or_else(|| {
        (
            StatusCode::SERVICE_UNAVAILABLE,
            Json(serde_json::json!({ "error": "database_unavailable" })),
        )
    })
}

pub(super) fn map_snapshot(snapshot: &FoundationSnapshot) -> FoundationResponse {
    FoundationResponse {
        id: snapshot.foundation_snapshot_id.clone(),
        org_id: snapshot.org_id,
        version: snapshot.foundation_version,
        sections: snapshot.sections.clone(),
        updated_at: snapshot.updated_at.to_rfc3339(),
        source: snapshot.source.clone(),
    }
}

pub(super) async fn update_org_foundation_version(
    pool: &sqlx::PgPool,
    org_id: Uuid,
    version: i32,
) -> Result<(), sqlx::Error> {
    sqlx::query(
        r#"
        UPDATE organizations
        SET foundation_version = $1, updated_at = NOW()
        WHERE org_id = $2
        "#,
    )
    .bind(version)
    .bind(org_id)
    .execute(pool)
    .await?;

    Ok(())
}

pub(super) async fn get_snapshot_row(
    pool: &sqlx::PgPool,
    org_id: Uuid,
    snapshot_id: &str,
) -> Result<Option<SnapshotRow>, sqlx::Error> {
    sqlx::query_as::<_, SnapshotRow>(
        r#"
        SELECT foundation_snapshot_id, org_id, foundation_version, sections, source, created_at, updated_at
        FROM foundation_snapshots
        WHERE org_id = $1 AND foundation_snapshot_id = $2
        "#,
    )
    .bind(org_id)
    .bind(snapshot_id)
    .fetch_optional(pool)
    .await
}

pub(super) async fn create_snapshot_from_sections(
    pool: &sqlx::PgPool,
    org_id: Uuid,
    sections: &serde_json::Value,
    source: &str,
) -> Result<FoundationSnapshot, sqlx::Error> {
    let current = FoundationService::get_current(pool, org_id).await?;
    let version = current
        .as_ref()
        .map(|snapshot| snapshot.foundation_version + 1)
        .unwrap_or(1);
    let snapshot_id = format!("found-{org_id}-{version}");

    raptorflow_db::queries::create_foundation_snapshot(
        pool,
        &snapshot_id,
        org_id,
        version,
        sections,
        source,
    )
    .await?;

    update_org_foundation_version(pool, org_id, version).await?;

    Ok(FoundationSnapshot {
        foundation_snapshot_id: snapshot_id,
        org_id,
        foundation_version: version,
        sections: sections.clone(),
        source: source.to_string(),
        created_at: Utc::now(),
        updated_at: Utc::now(),
    })
}
