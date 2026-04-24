use axum::{
    Json,
    extract::{Extension, Path, Query},
    http::StatusCode,
};
use chrono::Utc;
use raptorflow_acquisition::{HtmlParser, HttpFetcher, UrlNormalizer};
use raptorflow_avatars::seeding::seed_org_avatars;
use raptorflow_db::models::FoundationSnapshot;
use raptorflow_db::queries as db;
use raptorflow_foundation::{FoundationData, FoundationService};
use serde::{Deserialize, Serialize};
use sqlx::FromRow;
use std::sync::Arc;
use ulid::Ulid;
use uuid::Uuid;

use crate::middleware::{AppState, auth::AuthContext};

type AppResult<T> = Result<T, (StatusCode, Json<serde_json::Value>)>;

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
struct SnapshotRow {
    foundation_snapshot_id: String,
    org_id: Uuid,
    foundation_version: i32,
    sections: serde_json::Value,
    source: String,
    updated_at: chrono::DateTime<chrono::Utc>,
}

fn internal_error<E: std::fmt::Display>(e: E) -> (StatusCode, Json<serde_json::Value>) {
    tracing::error!("Foundation route error: {e}");
    (
        StatusCode::INTERNAL_SERVER_ERROR,
        Json(serde_json::json!({ "error": "foundation_internal_error" })),
    )
}

fn bad_request(message: &str) -> (StatusCode, Json<serde_json::Value>) {
    (
        StatusCode::BAD_REQUEST,
        Json(serde_json::json!({ "error": message })),
    )
}

fn not_found(message: &str) -> (StatusCode, Json<serde_json::Value>) {
    (
        StatusCode::NOT_FOUND,
        Json(serde_json::json!({ "error": message })),
    )
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
struct PositioningTemplateComponents {
    for_who: String,
    who_problem: String,
    brand: String,
    category: String,
    differentiation: String,
    because: String,
}

#[derive(Debug, Serialize, Deserialize)]
#[serde(rename_all = "camelCase")]
struct PositioningDraftResponse {
    statement: String,
    template_components: PositioningTemplateComponents,
    quality_score: f64,
    quality_feedback: String,
}

fn db_pool(state: &Arc<AppState>) -> AppResult<&sqlx::PgPool> {
    state.db_pool.as_deref().ok_or_else(|| {
        (
            StatusCode::SERVICE_UNAVAILABLE,
            Json(serde_json::json!({ "error": "database_unavailable" })),
        )
    })
}

fn map_snapshot(snapshot: &FoundationSnapshot) -> FoundationResponse {
    FoundationResponse {
        id: snapshot.foundation_snapshot_id.clone(),
        org_id: snapshot.org_id,
        version: snapshot.foundation_version,
        sections: snapshot.sections.clone(),
        updated_at: snapshot.updated_at.to_rfc3339(),
        source: snapshot.source.clone(),
    }
}

async fn update_org_foundation_version(
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

async fn get_snapshot_row(
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

async fn create_snapshot_from_sections(
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

pub async fn get_foundation(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
) -> AppResult<Json<FoundationResponse>> {
    let pool = db_pool(&state)?;
    let snapshot = FoundationService::get_current(pool, auth.tenant.org_id)
        .await
        .map_err(internal_error)?;

    match snapshot {
        Some(snapshot) => Ok(Json(map_snapshot(&snapshot))),
        None => Err(not_found("foundation_not_found")),
    }
}

pub async fn create_foundation(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
    Json(payload): Json<serde_json::Value>,
) -> AppResult<Json<FoundationResponse>> {
    let pool = db_pool(&state)?;
    let foundation_data: FoundationData =
        serde_json::from_value(payload.clone()).map_err(|e| bad_request(&e.to_string()))?;

    let org_name = foundation_data
        .company_info
        .name
        .clone()
        .filter(|value| !value.trim().is_empty())
        .unwrap_or_else(|| format!("Organization {}", auth.tenant.org_id));

    raptorflow_db::queries::create_organization(pool, auth.tenant.org_id, &org_name)
        .await
        .map_err(internal_error)?;

    let existing = FoundationService::get_current(pool, auth.tenant.org_id)
        .await
        .map_err(internal_error)?;

    let snapshot = match existing {
        None => {
            let snapshot_id =
                FoundationService::create_initial(pool, auth.tenant.org_id, foundation_data)
                    .await
                    .map_err(internal_error)?;
            update_org_foundation_version(pool, auth.tenant.org_id, 1)
                .await
                .map_err(internal_error)?;
            get_snapshot_row(pool, auth.tenant.org_id, &snapshot_id)
                .await
                .map_err(internal_error)?
                .ok_or_else(|| not_found("foundation_not_found"))?
        }
        Some(_current) => {
            let next = create_snapshot_from_sections(pool, auth.tenant.org_id, &payload, "manual")
                .await
                .map_err(internal_error)?;
            SnapshotRow {
                foundation_snapshot_id: next.foundation_snapshot_id,
                org_id: next.org_id,
                foundation_version: next.foundation_version,
                sections: next.sections,
                source: next.source,
                updated_at: next.updated_at,
            }
        }
    };

    let response = FoundationResponse {
        id: snapshot.foundation_snapshot_id,
        org_id: snapshot.org_id,
        version: snapshot.foundation_version,
        sections: snapshot.sections,
        updated_at: snapshot.updated_at.to_rfc3339(),
        source: snapshot.source,
    };

    Ok(Json(response))
}

pub async fn update_section(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
    Path(section): Path<String>,
    Json(payload): Json<UpdateSectionRequest>,
) -> AppResult<Json<FoundationResponse>> {
    let pool = db_pool(&state)?;

    let previous_value = FoundationService::get_section(pool, auth.tenant.org_id, &section)
        .await
        .map_err(internal_error)?;

    let version =
        FoundationService::update_section(pool, auth.tenant.org_id, &section, payload.data)
            .await
            .map_err(internal_error)?;

    if let Some(prev) = previous_value {
        let latest =
            raptorflow_db::queries::get_latest_foundation_version(pool, auth.tenant.org_id)
                .await
                .map_err(internal_error)?;

        let next_version = latest.map(|v| v.foundation_version + 1).unwrap_or(1);

        let _ = raptorflow_db::queries::create_foundation_version(
            pool,
            &format!("fv-{}-{}", auth.tenant.org_id, ulid::Ulid::new()),
            auth.tenant.org_id,
            next_version,
            Some(&format!("Updated {}", section)),
            &serde_json::json!([section]),
            &prev,
            None,
        )
        .await;
    }

    update_org_foundation_version(pool, auth.tenant.org_id, version)
        .await
        .map_err(internal_error)?;

    let snapshot = FoundationService::get_current(pool, auth.tenant.org_id)
        .await
        .map_err(internal_error)?
        .ok_or_else(|| not_found("foundation_not_found"))?;

    Ok(Json(map_snapshot(&snapshot)))
}

pub async fn list_foundation_versions(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
) -> AppResult<Json<Vec<serde_json::Value>>> {
    let pool = db_pool(&state)?;
    let versions = raptorflow_db::queries::get_foundation_versions(pool, auth.tenant.org_id)
        .await
        .map_err(internal_error)?;

    let response: Vec<serde_json::Value> = versions
        .iter()
        .map(|v| {
            serde_json::json!({
                "version_id": v.version_id,
                "version": v.foundation_version,
                "change_description": v.change_description,
                "changed_fields": v.changed_fields,
                "previous_values": v.previous_values,
                "impact_assessment": v.impact_assessment,
                "created_at": v.created_at.to_rfc3339(),
            })
        })
        .collect();

    Ok(Json(response))
}

pub async fn list_snapshots(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
) -> AppResult<Json<Vec<FoundationResponse>>> {
    let pool = db_pool(&state)?;
    let snapshots = raptorflow_db::queries::get_foundation_snapshots(pool, auth.tenant.org_id)
        .await
        .map_err(internal_error)?;

    let response = snapshots.iter().map(map_snapshot).collect();
    Ok(Json(response))
}

pub async fn create_snapshot(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
    Json(payload): Json<CreateSnapshotRequest>,
) -> AppResult<Json<FoundationResponse>> {
    let pool = db_pool(&state)?;
    let current = FoundationService::get_current(pool, auth.tenant.org_id)
        .await
        .map_err(internal_error)?
        .ok_or_else(|| not_found("foundation_not_found"))?;

    let snapshot = create_snapshot_from_sections(
        pool,
        auth.tenant.org_id,
        &current.sections,
        payload
            .source
            .as_deref()
            .filter(|value| !value.trim().is_empty())
            .unwrap_or("manual_snapshot"),
    )
    .await
    .map_err(internal_error)?;

    Ok(Json(map_snapshot(&snapshot)))
}

pub async fn restore_snapshot(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
    Path(id): Path<String>,
) -> AppResult<Json<FoundationResponse>> {
    let pool = db_pool(&state)?;
    let snapshot = get_snapshot_row(pool, auth.tenant.org_id, &id)
        .await
        .map_err(internal_error)?
        .ok_or_else(|| not_found("foundation_snapshot_not_found"))?;

    let restored = create_snapshot_from_sections(
        pool,
        auth.tenant.org_id,
        &snapshot.sections,
        &format!("restore:{id}"),
    )
    .await
    .map_err(internal_error)?;

    Ok(Json(map_snapshot(&restored)))
}

pub async fn get_snapshot(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
    Path(id): Path<String>,
) -> AppResult<Json<FoundationResponse>> {
    let pool = db_pool(&state)?;
    let snapshot = get_snapshot_row(pool, auth.tenant.org_id, &id)
        .await
        .map_err(internal_error)?
        .ok_or_else(|| not_found("foundation_snapshot_not_found"))?;

    Ok(Json(FoundationResponse {
        id: snapshot.foundation_snapshot_id,
        org_id: snapshot.org_id,
        version: snapshot.foundation_version,
        sections: snapshot.sections,
        updated_at: snapshot.updated_at.to_rfc3339(),
        source: snapshot.source,
    }))
}

#[derive(Debug, Deserialize)]
pub struct ScanStartRequest {
    pub url: Option<String>,
}

#[derive(Debug, Serialize)]
pub struct ScanStartResponse {
    pub scan_id: String,
    pub status: String,
}

#[derive(Debug, Serialize)]
pub struct ScanStatusResponse {
    pub scan_id: Option<String>,
    pub status: String,
    pub data: Option<serde_json::Value>,
    pub error_message: Option<String>,
}

async fn resolve_scan_url(
    pool: &sqlx::PgPool,
    org_id: Uuid,
) -> Result<Option<String>, sqlx::Error> {
    let row = sqlx::query_as::<_, (Option<String>,)>(
        r#"
        SELECT value::text as url
        FROM foundation_sections
        WHERE org_id = $1 AND section_key IN ('company_url', 'url', 'website')
        ORDER BY updated_at DESC
        LIMIT 1
        "#,
    )
    .bind(org_id)
    .fetch_optional(pool)
    .await?;

    Ok(row.and_then(|(url,)| {
        if url.as_ref().is_some_and(|u| !u.is_empty()) {
            url
        } else {
            None
        }
    }))
}

pub async fn start_scan(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
    Json(payload): Json<ScanStartRequest>,
) -> AppResult<Json<ScanStartResponse>> {
    let pool = db_pool(&state)?;

    let url = match &payload.url {
        Some(u) if !u.is_empty() => u.clone(),
        _ => {
            let resolved = resolve_scan_url(pool, auth.tenant.org_id)
                .await
                .map_err(internal_error)?
                .ok_or_else(|| bad_request("scan_url_required"))?;
            resolved
        }
    };

    let scan_id = format!("scan-{}-{}", auth.tenant.org_id, ulid::Ulid::new());

    sqlx::query(
        r#"
        INSERT INTO foundation_scans (scan_id, org_id, url, status, started_at)
        VALUES ($1, $2, $3, 'running', now())
        "#,
    )
    .bind(&scan_id)
    .bind(auth.tenant.org_id)
    .bind(&url)
    .execute(pool)
    .await
    .map_err(internal_error)?;

    let pool_clone = pool.clone();
    let scan_id_clone = scan_id.clone();

    tokio::spawn(async move {
        let _scan_data = match quick_scan(&url).await {
            Ok(data) => {
                let is_failed = data
                    .get("confidence")
                    .and_then(|c: &serde_json::Value| c.as_str())
                    .map(|s| s == "failed")
                    .unwrap_or(false);

                let final_status = if is_failed { "failed" } else { "completed" };

                let error_msg = if is_failed {
                    data.get("error")
                        .and_then(|e: &serde_json::Value| e.as_str())
                        .map(String::from)
                } else {
                    None
                };

                if let Err(e) = sqlx::query(
                    r#"
                    UPDATE foundation_scans
                    SET status = $1, quick_scan_data = $2, completed_at = now(),
                        error_message = $3
                    WHERE scan_id = $4
                    "#,
                )
                .bind(final_status)
                .bind(&data)
                .bind(&error_msg)
                .bind(&scan_id_clone)
                .execute(&pool_clone)
                .await
                {
                    tracing::error!("Failed to update scan status: {}", e);
                }
                data
            }
            Err(e) => {
                let err_msg = e.to_string();
                tracing::error!("Quick scan failed for {}: {}", scan_id_clone, err_msg);
                if let Err(e) = sqlx::query(
                    r#"
                    UPDATE foundation_scans
                    SET status = 'failed', error_message = $1, completed_at = now()
                    WHERE scan_id = $2
                    "#,
                )
                .bind(&err_msg)
                .bind(&scan_id_clone)
                .execute(&pool_clone)
                .await
                {
                    tracing::error!("Failed to update scan failed status: {}", e);
                }
                serde_json::json!({ "error": err_msg, "confidence": "failed" })
            }
        };
    });

    Ok(Json(ScanStartResponse {
        scan_id,
        status: "queued".to_string(),
    }))
}

pub async fn start_quick_scan(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
    Json(payload): Json<ScanStartRequest>,
) -> AppResult<Json<ScanStartResponse>> {
    let pool = db_pool(&state)?;

    let url = match &payload.url {
        Some(u) if !u.is_empty() => u.clone(),
        _ => {
            let resolved = resolve_scan_url(pool, auth.tenant.org_id)
                .await
                .map_err(internal_error)?
                .ok_or_else(|| bad_request("scan_url_required"))?;
            resolved
        }
    };

    let scan_id = format!("scan-quick-{}-{}", auth.tenant.org_id, ulid::Ulid::new());

    sqlx::query(
        r#"
        INSERT INTO foundation_scans (scan_id, org_id, url, status, started_at)
        VALUES ($1, $2, $3, 'running', now())
        "#,
    )
    .bind(&scan_id)
    .bind(auth.tenant.org_id)
    .bind(&url)
    .execute(pool)
    .await
    .map_err(internal_error)?;

    let pool_clone = pool.clone();
    let scan_id_clone = scan_id.clone();

    tokio::spawn(async move {
        let _scan_data = match quick_scan(&url).await {
            Ok(data) => {
                let is_failed = data
                    .get("confidence")
                    .and_then(|c: &serde_json::Value| c.as_str())
                    .map(|s| s == "failed")
                    .unwrap_or(false);

                let final_status = if is_failed { "failed" } else { "completed" };

                let error_msg = if is_failed {
                    data.get("error")
                        .and_then(|e: &serde_json::Value| e.as_str())
                        .map(String::from)
                } else {
                    None
                };

                if let Err(e) = sqlx::query(
                    r#"
                    UPDATE foundation_scans
                    SET status = $1, quick_scan_data = $2, completed_at = now(),
                        error_message = $3
                    WHERE scan_id = $4
                    "#,
                )
                .bind(final_status)
                .bind(&data)
                .bind(&error_msg)
                .bind(&scan_id_clone)
                .execute(&pool_clone)
                .await
                {
                    tracing::error!("Failed to update scan status: {}", e);
                }
                data
            }
            Err(e) => {
                let err_msg = e.to_string();
                tracing::error!("Quick scan failed for {}: {}", scan_id_clone, err_msg);
                if let Err(e) = sqlx::query(
                    r#"
                    UPDATE foundation_scans
                    SET status = 'failed', error_message = $1, completed_at = now()
                    WHERE scan_id = $2
                    "#,
                )
                .bind(&err_msg)
                .bind(&scan_id_clone)
                .execute(&pool_clone)
                .await
                {
                    tracing::error!("Failed to update scan failed status: {}", e);
                }
                serde_json::json!({ "error": err_msg, "confidence": "failed" })
            }
        };
    });

    Ok(Json(ScanStartResponse {
        scan_id,
        status: "queued".to_string(),
    }))
}

pub async fn start_deep_scan(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
    Json(payload): Json<ScanStartRequest>,
) -> AppResult<Json<ScanStartResponse>> {
    let pool = db_pool(&state)?;

    let url = match &payload.url {
        Some(u) if !u.is_empty() => u.clone(),
        _ => {
            let resolved = resolve_scan_url(pool, auth.tenant.org_id)
                .await
                .map_err(internal_error)?
                .ok_or_else(|| bad_request("scan_url_required"))?;
            resolved
        }
    };

    let scan_id = format!("scan-deep-{}-{}", auth.tenant.org_id, ulid::Ulid::new());

    sqlx::query(
        r#"
        INSERT INTO foundation_scans (scan_id, org_id, url, status, started_at)
        VALUES ($1, $2, $3, 'running', now())
        "#,
    )
    .bind(&scan_id)
    .bind(auth.tenant.org_id)
    .bind(&url)
    .execute(pool)
    .await
    .map_err(internal_error)?;

    let pool_clone = pool.clone();
    let scan_id_clone = scan_id.clone();

    tokio::spawn(async move {
        let _scan_data = match deep_scan(&url).await {
            Ok(data) => {
                let is_failed = data
                    .get("confidence")
                    .and_then(|c: &serde_json::Value| c.as_str())
                    .map(|s| s == "failed")
                    .unwrap_or(false);

                let final_status = if is_failed { "failed" } else { "completed" };

                let error_msg = if is_failed {
                    data.get("error")
                        .and_then(|e: &serde_json::Value| e.as_str())
                        .map(String::from)
                } else {
                    None
                };

                if let Err(e) = sqlx::query(
                    r#"
                    UPDATE foundation_scans
                    SET status = $1, deep_scan_data = $2, completed_at = now(),
                        error_message = $3
                    WHERE scan_id = $4
                    "#,
                )
                .bind(final_status)
                .bind(&data)
                .bind(&error_msg)
                .bind(&scan_id_clone)
                .execute(&pool_clone)
                .await
                {
                    tracing::error!("Failed to update scan status: {}", e);
                }
                data
            }
            Err(e) => {
                let err_msg = e.to_string();
                tracing::error!("Deep scan failed for {}: {}", scan_id_clone, err_msg);
                if let Err(e) = sqlx::query(
                    r#"
                    UPDATE foundation_scans
                    SET status = 'failed', error_message = $1, completed_at = now()
                    WHERE scan_id = $2
                    "#,
                )
                .bind(&err_msg)
                .bind(&scan_id_clone)
                .execute(&pool_clone)
                .await
                {
                    tracing::error!("Failed to update scan failed status: {}", e);
                }
                serde_json::json!({ "error": err_msg, "confidence": "failed" })
            }
        };
    });

    Ok(Json(ScanStartResponse {
        scan_id,
        status: "queued".to_string(),
    }))
}

#[derive(Debug, Deserialize)]
pub struct UpdateScanRequest {
    pub scan_id: String,
    pub deep_scan_data: Option<serde_json::Value>,
}

pub async fn update_scan(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
    Json(payload): Json<UpdateScanRequest>,
) -> AppResult<Json<serde_json::Value>> {
    let pool = db_pool(&state)?;

    sqlx::query(
        r#"
        UPDATE foundation_scans
        SET deep_scan_data = $1, status = 'completed', completed_at = now()
        WHERE scan_id = $2 AND org_id = $3
        "#,
    )
    .bind(payload.deep_scan_data)
    .bind(&payload.scan_id)
    .bind(auth.tenant.org_id)
    .execute(pool)
    .await
    .map_err(internal_error)?;

    Ok(Json(serde_json::json!({ "ok": true })))
}

pub async fn get_scan_by_id(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
    Path(scan_id): Path<String>,
) -> AppResult<Json<ScanStatusResponse>> {
    let pool = db_pool(&state)?;

    let row = sqlx::query_as::<
        _,
        (
            String,
            Option<serde_json::Value>,
            Option<serde_json::Value>,
            Option<String>,
        ),
    >(
        r#"
        SELECT status, quick_scan_data, deep_scan_data, error_message
        FROM foundation_scans
        WHERE scan_id = $1 AND org_id = $2
        "#,
    )
    .bind(&scan_id)
    .bind(auth.tenant.org_id)
    .fetch_optional(pool)
    .await
    .map_err(internal_error)?;

    match row {
        Some((status, quick_data, deep_data, error_message)) => {
            let data = if status == "completed" {
                if deep_data.is_some() {
                    deep_data
                } else {
                    quick_data
                }
            } else {
                None
            };
            Ok(Json(ScanStatusResponse {
                scan_id: Some(scan_id),
                status,
                data,
                error_message,
            }))
        }
        None => Err(not_found("scan_not_found")),
    }
}

#[derive(Debug, Deserialize)]
pub struct CreateCompetitorSnapshotRequest {
    pub competitor_url: String,
}

#[derive(Debug, Serialize)]
pub struct CreateCompetitorSnapshotResponse {
    pub snapshot_id: String,
}

pub async fn create_competitor_snapshot(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
    Json(payload): Json<CreateCompetitorSnapshotRequest>,
) -> AppResult<Json<CreateCompetitorSnapshotResponse>> {
    let pool = db_pool(&state)?;

    let snapshot_id = format!("comp-snap-{}-{}", auth.tenant.org_id, ulid::Ulid::new());

    raptorflow_db::queries::create_competitor_snapshot(
        pool,
        &snapshot_id,
        auth.tenant.org_id,
        &payload.competitor_url,
    )
    .await
    .map_err(internal_error)?;

    Ok(Json(CreateCompetitorSnapshotResponse { snapshot_id }))
}

#[derive(Debug, Deserialize)]
pub struct UpdateCompetitorSnapshotRequest {
    pub hash: Option<String>,
    pub status: String,
    pub scrape_data: Option<serde_json::Value>,
}

pub async fn update_competitor_snapshot(
    Extension(_auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
    Path(snapshot_id): Path<String>,
    Json(payload): Json<UpdateCompetitorSnapshotRequest>,
) -> AppResult<Json<serde_json::Value>> {
    let pool = db_pool(&state)?;

    raptorflow_db::queries::update_competitor_snapshot(
        pool,
        &snapshot_id,
        payload.hash.as_deref(),
        &payload.status,
        payload.scrape_data.as_ref(),
    )
    .await
    .map_err(internal_error)?;

    Ok(Json(serde_json::json!({ "ok": true })))
}

#[derive(Debug, Deserialize)]
pub struct GetLatestCompetitorSnapshotQuery {
    pub competitor_url: String,
}

pub async fn get_latest_competitor_snapshot(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
    Query(query): Query<GetLatestCompetitorSnapshotQuery>,
) -> AppResult<Json<Option<serde_json::Value>>> {
    let pool = db_pool(&state)?;

    let snapshot = raptorflow_db::queries::get_latest_competitor_snapshot(
        pool,
        auth.tenant.org_id,
        &query.competitor_url,
    )
    .await
    .map_err(internal_error)?;

    match snapshot {
        Some(snap) => Ok(Json(Some(serde_json::json!({
            "snapshot_id": snap.snapshot_id,
            "hash": snap.hash,
            "status": snap.status,
            "scrape_data": snap.scrape_data,
            "created_at": snap.created_at
        })))),
        None => Ok(Json(None)),
    }
}

pub async fn get_scan_status(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
) -> AppResult<Json<ScanStatusResponse>> {
    let pool = db_pool(&state)?;

    let row = sqlx::query_as::<
        _,
        (
            String,
            Option<serde_json::Value>,
            Option<serde_json::Value>,
            Option<String>,
        ),
    >(
        r#"
        SELECT status, quick_scan_data, deep_scan_data, error_message
        FROM foundation_scans
        WHERE org_id = $1
        ORDER BY started_at DESC
        LIMIT 1
        "#,
    )
    .bind(auth.tenant.org_id)
    .fetch_optional(pool)
    .await
    .map_err(internal_error)?;

    match row {
        Some((status, quick_data, deep_data, error_message)) => {
            let data = if status == "completed" {
                if deep_data.is_some() {
                    deep_data
                } else {
                    quick_data
                }
            } else {
                None
            };
            Ok(Json(ScanStatusResponse {
                scan_id: None,
                status,
                data,
                error_message,
            }))
        }
        None => Ok(Json(ScanStatusResponse {
            scan_id: None,
            status: "not_found".to_string(),
            data: None,
            error_message: None,
        })),
    }
}

#[derive(Debug, Serialize)]
pub struct SnapshotFullResponse {
    pub status: String,
    pub completed_sections: Vec<String>,
    pub missing_sections: Vec<String>,
    pub last_updated_section: Option<String>,
    pub version: i32,
    pub sections: serde_json::Value,
}

const ALL_SECTIONS: [&str; 21] = [
    "company_url",
    "company_info",
    "company_stage",
    "product_catalog",
    "problem_statement",
    "target_audience",
    "secondary_icps",
    "competitors",
    "differentiation",
    "positioning",
    "brand_personality",
    "voice_practice",
    "content_territories",
    "channels",
    "goals",
    "seo_keywords",
    "asset_inventory",
    "frustrations",
    "tools",
    "reference_brands",
    "strategist",
];

fn canonical_section_key(section: &str) -> &str {
    match section {
        // Legacy aliases retained for older snapshots and old clients.
        "url" | "scan_results" => "company_url",
        "business_stage" => "company_stage",
        "primary_product" | "pricing_model" => "product_catalog",
        "customer_problem" => "problem_statement",
        "icp" => "target_audience",
        "transformation" => "secondary_icps",
        "differentiation" => "differentiation",
        "keywords" => "seo_keywords",
        "content_channels" | "content_history" => "channels",
        "primary_goal" | "budget" => "goals",
        "existing_assets" => "asset_inventory",
        "analytics_tracking" => "frustrations",
        other => other,
    }
}

pub async fn get_snapshot_full(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
) -> AppResult<Json<SnapshotFullResponse>> {
    let pool = db_pool(&state)?;

    let rows = sqlx::query_as::<_, (String, serde_json::Value, chrono::DateTime<chrono::Utc>)>(
        r#"
        SELECT section_key, value, updated_at
        FROM foundation_sections
        WHERE org_id = $1
        ORDER BY updated_at DESC
        "#,
    )
    .bind(auth.tenant.org_id)
    .fetch_all(pool)
    .await
    .map_err(internal_error)?;

    if rows.is_empty() {
        return Ok(Json(SnapshotFullResponse {
            status: "not_started".to_string(),
            completed_sections: vec![],
            missing_sections: ALL_SECTIONS.iter().map(|s| s.to_string()).collect(),
            last_updated_section: None,
            version: 0,
            sections: serde_json::json!({}),
        }));
    }

    let mut sections_map = serde_json::Map::new();
    let mut latest_by_section: std::collections::HashMap<
        String,
        (serde_json::Value, chrono::DateTime<chrono::Utc>),
    > = std::collections::HashMap::new();
    let mut last_updated = None;
    let mut last_updated_at =
        chrono::DateTime::<chrono::Utc>::from_timestamp(0, 0).unwrap_or_else(Utc::now);

    for (raw_key, value, updated_at) in rows {
        let key = canonical_section_key(&raw_key).to_string();
        match latest_by_section.get(&key) {
            Some((_, existing_at)) if *existing_at >= updated_at => {}
            _ => {
                latest_by_section.insert(key.clone(), (value, updated_at));
            }
        }
    }

    let mut completed = Vec::new();
    for key in ALL_SECTIONS {
        if let Some((value, updated_at)) = latest_by_section.get(key) {
            sections_map.insert(key.to_string(), value.clone());
            completed.push(key.to_string());
            if *updated_at > last_updated_at {
                last_updated_at = *updated_at;
                last_updated = Some(key.to_string());
            }
        }
    }

    let missing: Vec<String> = ALL_SECTIONS
        .iter()
        .filter(|s| !completed.iter().any(|completed_key| completed_key == *s))
        .map(|s| s.to_string())
        .collect();

    let status = if missing.is_empty() {
        "completed"
    } else {
        "in_progress"
    };

    let current_version = FoundationService::get_current(pool, auth.tenant.org_id)
        .await
        .map_err(internal_error)?
        .map(|snapshot| snapshot.foundation_version)
        .unwrap_or(completed.len() as i32);

    Ok(Json(SnapshotFullResponse {
        status: status.to_string(),
        completed_sections: completed.clone(),
        missing_sections: missing,
        last_updated_section: last_updated,
        version: current_version,
        sections: serde_json::to_value(sections_map).unwrap_or(serde_json::json!({})),
    }))
}

#[derive(Debug, Serialize)]
pub struct CompleteResponse {
    pub ok: bool,
    pub office_ready: bool,
    pub strategist_name: String,
    pub first_nudge_id: Option<String>,
}

pub async fn complete_foundation(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
) -> AppResult<Json<CompleteResponse>> {
    let pool = db_pool(&state)?;
    let org_id = auth.tenant.org_id;

    let rows = sqlx::query_as::<_, (String, serde_json::Value)>(
        r#"
        SELECT section_key, value
        FROM foundation_sections
        WHERE org_id = $1
        "#,
    )
    .bind(org_id)
    .fetch_all(pool)
    .await
    .map_err(internal_error)?;

    let mut sections = serde_json::Map::new();
    for (key, value) in rows {
        sections.insert(key, value);
    }

    let foundation_json = serde_json::json!({ "sections": sections });

    let avatar_check =
        sqlx::query_as::<_, (i64,)>("SELECT COUNT(*) FROM agent_essences WHERE org_id = $1")
            .bind(org_id)
            .fetch_optional(pool)
            .await
            .map_err(internal_error)?;

    let needs_seeding = avatar_check.map(|row| row.0 == 0).unwrap_or(true);

    if needs_seeding {
        let foundation_snapshot = FoundationSnapshot {
            foundation_snapshot_id: format!("found-{}-complete", org_id),
            org_id,
            foundation_version: 1,
            sections: foundation_json.clone(),
            source: "completion".to_string(),
            created_at: Utc::now(),
            updated_at: Utc::now(),
        };
        if let Err(e) = seed_org_avatars(pool, org_id, Some(&foundation_snapshot)).await {
            tracing::warn!(org_id = %org_id, error = %e, "avatar seeding failed during completion");
        }
    }

    let company_name = foundation_json
        .get("sections")
        .and_then(|s| s.get("company_info"))
        .and_then(|ci| ci.get("name"))
        .and_then(|v| v.as_str())
        .unwrap_or("there");

    let (nudge_title, nudge_body) = {
        (
            "Your Strategist is ready!".to_string(),
            format!(
                "Welcome {}! Your Strategist is now active and ready to help craft campaigns that truly resonate with your audience. Head to your Office to meet your team and get started!",
                company_name
            ),
        )
    };

    let first_user = sqlx::query_as::<_, (Uuid,)>(
        "SELECT org_user_id FROM org_users WHERE org_id = $1 ORDER BY created_at ASC LIMIT 1",
    )
    .bind(org_id)
    .fetch_optional(pool)
    .await
    .map_err(internal_error)?;

    let nudge_id = Ulid::new().to_string();
    let mut first_nudge_id: Option<String> = None;

    if let Some((user_id,)) = first_user {
        let nudge_type = "foundation_complete";
        let priority = "high";
        let action_data = serde_json::json!({ "action": "open_office" });

        if let Err(e) = db::create_nudge(
            pool,
            &nudge_id,
            org_id,
            user_id,
            nudge_type,
            priority,
            &nudge_title,
            &nudge_body,
            Some("navigate"),
            &action_data,
            "foundation",
            &format!("found-{}", org_id),
        )
        .await
        {
            tracing::warn!(org_id = %org_id, error = %e, "failed to create nudge record");
        } else {
            first_nudge_id = Some(nudge_id.clone());
            tracing::info!(org_id = %org_id, nudge_id = %nudge_id, "first strategist nudge created");
        }
    }

    Ok(Json(CompleteResponse {
        ok: true,
        office_ready: true,
        strategist_name: "Strategist".to_string(),
        first_nudge_id,
    }))
}

pub async fn content_strategy_create(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
) -> AppResult<Json<serde_json::Value>> {
    let pool = db_pool(&state)?;
    let strategy_id = format!(
        "content-strategy-{}-{}",
        auth.tenant.org_id,
        ulid::Ulid::new()
    );

    raptorflow_db::queries::create_content_strategy(pool, &strategy_id, auth.tenant.org_id)
        .await
        .map_err(internal_error)?;

    Ok(Json(serde_json::json!({
        "strategy_id": strategy_id,
        "status": "created"
    })))
}

pub async fn content_strategy_get(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
) -> AppResult<Json<serde_json::Value>> {
    let pool = db_pool(&state)?;
    let strategy = raptorflow_db::queries::get_content_strategy(pool, auth.tenant.org_id)
        .await
        .map_err(internal_error)?;

    match strategy {
        Some(s) => Ok(Json(serde_json::json!({
            "strategy_id": s.strategy_id,
            "territories": s.territories,
            "pillar_pages": s.pillar_pages,
            "editorial_calendar": s.editorial_calendar,
            "created_at": s.created_at,
            "updated_at": s.updated_at
        }))),
        None => Ok(Json(serde_json::json!({
            "territories": [],
            "pillar_pages": [],
            "editorial_calendar": []
        }))),
    }
}

pub async fn content_strategy_update_territories(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
    Json(territories): Json<serde_json::Value>,
) -> AppResult<Json<serde_json::Value>> {
    let pool = db_pool(&state)?;

    // Ensure strategy exists
    let existing = raptorflow_db::queries::get_content_strategy(pool, auth.tenant.org_id)
        .await
        .map_err(internal_error)?;

    if existing.is_none() {
        raptorflow_db::queries::create_content_strategy(
            pool,
            &format!(
                "content-strategy-{}-{}",
                auth.tenant.org_id,
                ulid::Ulid::new()
            ),
            auth.tenant.org_id,
        )
        .await
        .map_err(internal_error)?;
    }

    raptorflow_db::queries::update_content_strategy_territories(
        pool,
        auth.tenant.org_id,
        &territories,
    )
    .await
    .map_err(internal_error)?;

    Ok(Json(serde_json::json!({ "success": true })))
}

pub async fn content_strategy_generate_calendar(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
) -> AppResult<Json<serde_json::Value>> {
    let pool = db_pool(&state)?;

    let strategy = raptorflow_db::queries::get_content_strategy(pool, auth.tenant.org_id)
        .await
        .map_err(internal_error)?
        .ok_or_else(|| not_found("content_strategy_not_found"))?;

    let territories: Vec<serde_json::Value> =
        serde_json::from_value(strategy.territories).unwrap_or_default();
    let pillar_pages: Vec<serde_json::Value> =
        serde_json::from_value(strategy.pillar_pages).unwrap_or_default();

    let calendar = generate_fallback_calendar(&territories, &pillar_pages);

    raptorflow_db::queries::update_content_strategy_calendar(
        pool,
        auth.tenant.org_id,
        &serde_json::to_value(&calendar).unwrap_or(serde_json::json!([])),
    )
    .await
    .map_err(internal_error)?;

    Ok(Json(serde_json::json!({ "calendar": calendar })))
}

fn generate_fallback_calendar(
    territories: &[serde_json::Value],
    pillar_pages: &[serde_json::Value],
) -> Vec<serde_json::Value> {
    let mut calendar = Vec::new();
    let mut content_id = 1;
    let today = chrono::Utc::now();

    for territory in territories {
        if let Some(territory_name) = territory.get("name").and_then(|v| v.as_str()) {
            for week in 0..12 {
                let date = today + chrono::Duration::days(week * 7);
                calendar.push(serde_json::json!({
                    "id": content_id,
                    "title": format!("{} Content - Week {}", territory_name, week + 1),
                    "territory": territory_name,
                    "date": date.format("%Y-%m-%d").to_string(),
                    "status": "planned",
                    "content_type": "blog_post"
                }));
                content_id += 1;
            }
        }
    }

    for pillar in pillar_pages {
        if let Some(pillar_title) = pillar.get("title").and_then(|v| v.as_str()) {
            for (i, month) in [1, 4, 7, 10].iter().enumerate() {
                let date = chrono::NaiveDate::from_ymd_opt(2026, *month, 1)
                    .unwrap_or(today.naive_utc().date());
                calendar.push(serde_json::json!({
                    "id": content_id,
                    "title": format!("{} Update - Q{}", pillar_title, i + 1),
                    "pillar_page": pillar_title,
                    "date": date.format("%Y-%m-%d").to_string(),
                    "status": "planned",
                    "content_type": "pillar_update"
                }));
                content_id += 1;
            }
        }
    }

    calendar
}

pub async fn add_secondary_icp(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
    Json(payload): Json<serde_json::Value>,
) -> AppResult<Json<serde_json::Value>> {
    let pool = db_pool(&state)?;

    let mode = payload
        .get("mode")
        .and_then(|v| v.as_str())
        .ok_or_else(|| bad_request("mode is required (b2b or b2c)"))?;
    let icp_data = payload
        .get("icp")
        .ok_or_else(|| bad_request("icp data is required"))?;

    // Validate B2B structure
    fn validate_b2b_icp(icp: &serde_json::Value) -> Result<(), &'static str> {
        if icp
            .get("name")
            .and_then(|v| v.as_str())
            .map(|s| !s.is_empty())
            .unwrap_or(false)
        {
            return Err("B2B ICP requires non-empty name");
        }
        if icp
            .get("persona_name")
            .and_then(|v| v.as_str())
            .map(|s| !s.is_empty())
            .unwrap_or(false)
        {
            return Err("B2B ICP requires non-empty persona_name");
        }
        if icp
            .get("role_identity")
            .and_then(|v| v.as_str())
            .map(|s| !s.is_empty())
            .unwrap_or(false)
        {
            return Err("B2B ICP requires non-empty role_identity");
        }
        Ok(())
    }

    // Validate B2C structure
    fn validate_b2c_icp(icp: &serde_json::Value) -> Result<(), &'static str> {
        if icp
            .get("name")
            .and_then(|v| v.as_str())
            .map(|s| !s.is_empty())
            .unwrap_or(false)
        {
            return Err("B2C ICP requires non-empty name");
        }
        if icp
            .get("persona_name")
            .and_then(|v| v.as_str())
            .map(|s| !s.is_empty())
            .unwrap_or(false)
        {
            return Err("B2C ICP requires non-empty persona_name");
        }
        if icp
            .get("life_situation")
            .and_then(|v| v.as_str())
            .map(|s| !s.is_empty())
            .unwrap_or(false)
        {
            return Err("B2C ICP requires non-empty life_situation");
        }
        Ok(())
    }

    match mode {
        "b2b" => validate_b2b_icp(icp_data).map_err(|e| bad_request(e))?,
        "b2c" => validate_b2c_icp(icp_data).map_err(|e| bad_request(e))?,
        _ => return Err(bad_request("mode must be 'b2b' or 'b2c'")),
    }

    let foundation_data = FoundationService::get_current(pool, auth.tenant.org_id)
        .await
        .map_err(internal_error)?
        .ok_or_else(|| not_found("foundation_not_found"))?;

    let mut foundation_json: serde_json::Value = foundation_data.sections;

    if !foundation_json.get("secondary_icps").is_some() {
        foundation_json["secondary_icps"] = serde_json::json!([]);
    }

    let secondary_icps_count = {
        let secondary_icps = foundation_json
            .get_mut("secondary_icps")
            .and_then(|v| v.as_array_mut())
            .ok_or_else(|| bad_request("secondary_icps must be an array"))?;

        if secondary_icps.len() >= 3 {
            return Err(bad_request("Maximum 3 secondary ICPs allowed"));
        }

        let secondary_icp = serde_json::json!({
            "mode": mode,
            "icp": icp_data
        });

        secondary_icps.push(secondary_icp);
        secondary_icps.len()
    };

    let new_version = create_snapshot_from_sections(
        pool,
        auth.tenant.org_id,
        &foundation_json,
        "add_secondary_icp",
    )
    .await
    .map_err(internal_error)?;

    Ok(Json(serde_json::json!({
        "success": true,
        "secondary_icps_count": secondary_icps_count,
        "new_version": new_version.foundation_version
    })))
}

pub async fn update_secondary_icp(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
    Path(icp_index): Path<usize>,
    Json(payload): Json<serde_json::Value>,
) -> AppResult<Json<serde_json::Value>> {
    let pool = db_pool(&state)?;

    // Validate payload has mode and icp data
    let mode = payload
        .get("mode")
        .and_then(|v| v.as_str())
        .ok_or_else(|| bad_request("mode is required (b2b or b2c)"))?;
    let icp_data = payload
        .get("icp")
        .ok_or_else(|| bad_request("icp data is required"))?;

    // Get current foundation
    let foundation_data = FoundationService::get_current(pool, auth.tenant.org_id)
        .await
        .map_err(internal_error)?
        .ok_or_else(|| not_found("foundation_not_found"))?;

    let mut foundation_json: serde_json::Value = foundation_data.sections;

    // Get secondary_icps array
    if !foundation_json.get("secondary_icps").is_some() {
        foundation_json["secondary_icps"] = serde_json::json!([]);
    }
    let _secondary_icps_len = {
        let secondary_icps = foundation_json
            .get_mut("secondary_icps")
            .and_then(|v| v.as_array_mut())
            .ok_or_else(|| bad_request("secondary_icps must be an array"))?;

        // Validate index
        if icp_index >= secondary_icps.len() {
            return Err(bad_request("invalid icp index"));
        }

        // Update secondary ICP entry
        secondary_icps[icp_index] = serde_json::json!({
            "mode": mode,
            "icp": icp_data
        });

        secondary_icps.len()
    };

    // Create new foundation version
    let new_version = create_snapshot_from_sections(
        pool,
        auth.tenant.org_id,
        &foundation_json,
        "update_secondary_icp",
    )
    .await
    .map_err(internal_error)?;

    Ok(Json(serde_json::json!({
        "success": true,
        "updated_index": icp_index,
        "new_version": new_version.foundation_version
    })))
}

pub async fn delete_secondary_icp(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
    Path(icp_index): Path<usize>,
) -> AppResult<Json<serde_json::Value>> {
    let pool = db_pool(&state)?;

    // Get current foundation
    let foundation_data = FoundationService::get_current(pool, auth.tenant.org_id)
        .await
        .map_err(internal_error)?
        .ok_or_else(|| not_found("foundation_not_found"))?;

    let mut foundation_json: serde_json::Value = foundation_data.sections;

    // Get secondary_icps array
    if !foundation_json.get("secondary_icps").is_some() {
        foundation_json["secondary_icps"] = serde_json::json!([]);
    }
    let remaining_count = {
        let secondary_icps = foundation_json
            .get_mut("secondary_icps")
            .and_then(|v| v.as_array_mut())
            .ok_or_else(|| bad_request("secondary_icps must be an array"))?;

        // Validate index
        if icp_index >= secondary_icps.len() {
            return Err(bad_request("invalid icp index"));
        }

        // Remove secondary ICP
        secondary_icps.remove(icp_index);
        secondary_icps.len()
    };

    // Create new foundation version
    let new_version = create_snapshot_from_sections(
        pool,
        auth.tenant.org_id,
        &foundation_json,
        "delete_secondary_icp",
    )
    .await
    .map_err(internal_error)?;

    Ok(Json(serde_json::json!({
        "success": true,
        "deleted_index": icp_index,
        "remaining_count": remaining_count,
        "new_version": new_version.foundation_version
    })))
}

pub async fn generate_positioning_draft(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
) -> AppResult<Json<serde_json::Value>> {
    let pool = db_pool(&state)?;
    let bedrock = state.bedrock.as_ref().ok_or_else(|| {
        (
            StatusCode::SERVICE_UNAVAILABLE,
            Json(serde_json::json!({ "error": "bedrock_unavailable" })),
        )
    })?;

    let foundation_data = FoundationService::get_current(pool, auth.tenant.org_id)
        .await
        .map_err(internal_error)?
        .ok_or_else(|| not_found("foundation_not_found"))?;

    let foundation_json: serde_json::Value = foundation_data.sections;

    let icp = foundation_json
        .get("target_audience")
        .and_then(|ta| ta.get("primary_icp"));
    let _competitors = foundation_json.get("competitors");
    let differentiation = foundation_json.get("differentiation");
    let _product = foundation_json
        .get("product_catalog")
        .and_then(|pc| pc.get("primary_product"));
    let problem = foundation_json.get("problem_statement");

    let company_name = foundation_json
        .get("company_info")
        .and_then(|ci| ci.get("name"))
        .and_then(|n| n.as_str())
        .unwrap_or("our brand");
    let category = foundation_json
        .get("company_info")
        .and_then(|ci| ci.get("industry"))
        .and_then(|n| n.as_str())
        .unwrap_or("solution provider");
    let for_who = icp
        .and_then(|i| i.get("name"))
        .and_then(|n| n.as_str())
        .unwrap_or("our target customers");
    let who_problem = problem
        .and_then(|p| p.as_str())
        .unwrap_or("face challenges");
    let differentiation_text = differentiation
        .and_then(|d| d.as_array())
        .and_then(|arr| arr.first())
        .and_then(|v| v.as_str())
        .unwrap_or("unique value");
    let because = "we deliver proven results";

    let prompt = format!(
        r#"You are RaptorFlow's positioning strategist.
Return only valid JSON. No markdown, no code fences, no explanation.

Use this exact schema:
{{
  "statement": string,
  "templateComponents": {{
    "forWho": string,
    "whoProblem": string,
    "brand": string,
    "category": string,
    "differentiation": string,
    "because": string
  }},
  "qualityScore": number,
  "qualityFeedback": string
}}

Requirements:
- Write one concise positioning statement.
- qualityScore must be a number from 0 to 1.
- qualityFeedback must be one short sentence with the most important improvement.

Context:
- forWho: {for_who}
- whoProblem: {who_problem}
- brand: {company_name}
- category: {category}
- differentiation: {differentiation_text}
- because: {because}
"#
    );

    let raw = bedrock
        .converse_large(&prompt, 768)
        .await
        .map_err(internal_error)?;

    let trimmed = raw.trim();
    let json_text = if let Ok(value) = serde_json::from_str::<serde_json::Value>(trimmed) {
        value
    } else {
        let start = trimmed.find('{').ok_or_else(|| {
            (
                StatusCode::BAD_GATEWAY,
                Json(serde_json::json!({ "error": "bedrock_response_missing_json" })),
            )
        })?;
        let end = trimmed.rfind('}').ok_or_else(|| {
            (
                StatusCode::BAD_GATEWAY,
                Json(serde_json::json!({ "error": "bedrock_response_missing_json" })),
            )
        })?;
        serde_json::from_str::<serde_json::Value>(&trimmed[start..=end]).map_err(|e| {
            (
                StatusCode::BAD_GATEWAY,
                Json(serde_json::json!({
                    "error": "bedrock_response_invalid_json",
                    "details": e.to_string()
                })),
            )
        })?
    };

    let response: PositioningDraftResponse = serde_json::from_value(json_text).map_err(|e| {
        (
            StatusCode::BAD_GATEWAY,
            Json(serde_json::json!({
                "error": "bedrock_positioning_schema_mismatch",
                "details": e.to_string()
            })),
        )
    })?;

    Ok(Json(
        serde_json::to_value(response).map_err(internal_error)?,
    ))
}

pub async fn lock_positioning(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
    Json(payload): Json<serde_json::Value>,
) -> AppResult<Json<serde_json::Value>> {
    let pool = db_pool(&state)?;

    // Get active campaigns that might be affected
    // Note: This assumes there's a campaigns table and API to get active campaigns
    // For now, we'll return a placeholder impact assessment
    let downstream_impact = vec![serde_json::json!({
        "campaignId": "placeholder-campaign-1",
        "campaignName": "Q1 Growth Campaign",
        "impactDescription": "Campaign messaging may need alignment with new positioning statement."
    })];

    // Update foundation positioning with isLocked: true
    let positioning_data = payload
        .get("positioning")
        .ok_or_else(|| bad_request("positioning data required"))?;

    let mut locked_positioning = positioning_data.clone();
    if let Some(obj) = locked_positioning.as_object_mut() {
        obj.insert("is_locked".to_string(), serde_json::json!(true));
        obj.insert(
            "locked_at".to_string(),
            serde_json::json!(chrono::Utc::now().to_rfc3339()),
        );
    }

    // Update foundation section
    raptorflow_db::queries::upsert_foundation_section(
        pool,
        auth.tenant.org_id,
        "positioning",
        &locked_positioning,
    )
    .await
    .map_err(internal_error)?;

    // Create FoundationVersion record
    let foundation_data = FoundationService::get_current(pool, auth.tenant.org_id)
        .await
        .map_err(internal_error)?
        .ok_or_else(|| not_found("foundation_not_found"))?;

    let version_id = format!("version-{}-{}", auth.tenant.org_id, ulid::Ulid::new());
    raptorflow_db::queries::create_foundation_version(
        pool,
        &version_id,
        auth.tenant.org_id,
        foundation_data.foundation_version + 1,
        Some("positioning_locked"),
        &serde_json::json!({}),
        &serde_json::json!({}),
        Some(&serde_json::json!(downstream_impact)),
    )
    .await
    .map_err(internal_error)?;

    Ok(Json(serde_json::json!({
        "success": true,
        "downstreamImpact": downstream_impact,
        "newVersion": foundation_data.foundation_version + 1
    })))
}

async fn deep_scan(url: &str) -> Result<serde_json::Value, String> {
    let fetcher = HttpFetcher::new();
    let (body, final_url) = fetcher
        .fetch(url)
        .await
        .map_err(|e| format!("fetch_failed: {}", e))?;

    let html = String::from_utf8_lossy(&body).to_string();
    let parsed = HtmlParser::parse(&html).map_err(|e| format!("parse_failed: {}", e))?;

    let title = parsed.title;
    let description = parsed.language.clone();

    let json_ld: Option<serde_json::Value> = scraper::Html::parse_document(&html)
        .select(
            &scraper::Selector::parse("script[type=\"application/ld+json\"]")
                .ok()
                .unwrap(),
        )
        .next()
        .map(|el| el.text().collect::<String>())
        .and_then(|text| serde_json::from_str::<serde_json::Value>(&text).ok());

    let social_links = extract_social_links(&html);

    let business_name = json_ld
        .as_ref()
        .and_then(|j| j.get("name").and_then(|n| n.as_str()))
        .map(String::from)
        .or_else(|| title.clone());

    let canonical = UrlNormalizer::canonical_url(url, &final_url).ok();
    let domain = UrlNormalizer::extract_domain(&final_url).ok();
    let logo_url = json_ld
        .as_ref()
        .and_then(|j| j.get("logo").and_then(|l| l.as_str()).map(String::from));

    let primary_offering = json_ld.as_ref().and_then(|j| {
        j.get("description")
            .and_then(|d| d.as_str())
            .map(String::from)
    });

    let industry = infer_industry(title.as_ref().or(description.as_ref()));

    let confidence = if business_name.is_some() {
        "medium"
    } else {
        "low"
    };

    Ok(serde_json::json!({
        "business_name": business_name,
        "industry": industry,
        "description": description,
        "primary_offering": primary_offering,
        "competitor_suggestions": [],
        "keyword_suggestions": [],
        "confidence": confidence,
        "social_links": social_links,
        "logo_url": logo_url,
        "domain": domain,
        "raw": {
            "title": title,
            "url": final_url,
            "canonical": canonical,
            "json_ld": json_ld
        }
    }))
}

async fn quick_scan(url: &str) -> Result<serde_json::Value, String> {
    let fetcher = HttpFetcher::new();
    let (body, final_url) = fetcher
        .fetch(url)
        .await
        .map_err(|e| format!("fetch_failed: {}", e))?;

    let html = String::from_utf8_lossy(&body).to_string();
    let parsed = HtmlParser::parse(&html).map_err(|e| format!("parse_failed: {}", e))?;

    let title = parsed.title;
    let description = parsed.language.clone();
    let og_image = scraper::Html::parse_document(&html)
        .select(
            &scraper::Selector::parse("meta[property=\"og:image\"]")
                .ok()
                .unwrap(),
        )
        .next()
        .and_then(|el| el.value().attr("content"))
        .map(String::from);

    let json_ld: Option<serde_json::Value> = scraper::Html::parse_document(&html)
        .select(
            &scraper::Selector::parse("script[type=\"application/ld+json\"]")
                .ok()
                .unwrap(),
        )
        .next()
        .map(|el| el.text().collect::<String>())
        .and_then(|text| serde_json::from_str::<serde_json::Value>(&text).ok());

    let social_links = extract_social_links(&html);

    let business_name = json_ld
        .as_ref()
        .and_then(|j| j.get("name").and_then(|n| n.as_str()))
        .map(String::from)
        .or_else(|| title.clone());

    let canonical = UrlNormalizer::canonical_url(url, &final_url).ok();
    let domain = UrlNormalizer::extract_domain(&final_url).ok();
    let logo_url = json_ld
        .as_ref()
        .and_then(|j| j.get("logo").and_then(|l| l.as_str()).map(String::from))
        .or_else(|| og_image);

    let primary_offering = json_ld.as_ref().and_then(|j| {
        j.get("description")
            .and_then(|d| d.as_str())
            .map(String::from)
    });

    let industry = infer_industry(title.as_ref().or(description.as_ref()));

    let confidence = if business_name.is_some() {
        "medium"
    } else {
        "low"
    };

    Ok(serde_json::json!({
        "business_name": business_name,
        "industry": industry,
        "description": description,
        "primary_offering": primary_offering,
        "competitor_suggestions": [],
        "keyword_suggestions": [],
        "confidence": confidence,
        "social_links": social_links,
        "logo_url": logo_url,
        "domain": domain,
        "raw": {
            "title": title,
            "url": final_url,
            "canonical": canonical,
            "json_ld": json_ld
        }
    }))
}

fn extract_social_links(html: &str) -> Vec<String> {
    let mut links = Vec::new();
    let domains = [
        "twitter.com",
        "linkedin.com",
        "facebook.com",
        "instagram.com",
        "youtube.com",
        "github.com",
    ];

    let document = scraper::Html::parse_document(html);

    for domain in &domains {
        if let Ok(selector) = scraper::Selector::parse(&format!("a[href*=\"{}\"]", domain)) {
            for el in document.select(&selector) {
                if let Some(href) = el.value().attr("href") {
                    let href = href.to_string();
                    if !links.contains(&href) {
                        links.push(href);
                    }
                }
            }
        }
    }
    links
}

fn infer_industry(text: Option<&String>) -> Option<String> {
    let desc = text?.to_lowercase();
    if desc.contains("software")
        || desc.contains("tech")
        || desc.contains("saas")
        || desc.contains("cloud")
    {
        Some("SaaS / Technology".to_string())
    } else if desc.contains("finance")
        || desc.contains("bank")
        || desc.contains("payment")
        || desc.contains("fintech")
    {
        Some("Financial Services".to_string())
    } else if desc.contains("health")
        || desc.contains("medical")
        || desc.contains("wellness")
        || desc.contains("healthcare")
    {
        Some("Healthcare & Wellness".to_string())
    } else if desc.contains("retail")
        || desc.contains("ecommerce")
        || desc.contains("e-commerce")
        || desc.contains("shop")
    {
        Some("D2C / E-commerce".to_string())
    } else if desc.contains("education")
        || desc.contains("learning")
        || desc.contains("training")
        || desc.contains("course")
    {
        Some("Education & Training".to_string())
    } else if desc.contains("real estate") || desc.contains("property") {
        Some("Real Estate".to_string())
    } else if desc.contains("food") || desc.contains("restaurant") || desc.contains("beverage") {
        Some("Food & Beverage".to_string())
    } else if desc.contains("logistics")
        || desc.contains("supply chain")
        || desc.contains("shipping")
    {
        Some("Logistics & Supply Chain".to_string())
    } else {
        None
    }
}
