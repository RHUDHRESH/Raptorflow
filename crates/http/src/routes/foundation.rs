use axum::{
    extract::{Extension, Path},
    http::StatusCode,
    Json,
};
use chrono::Utc;
use raptorflow_db::models::FoundationSnapshot;
use raptorflow_foundation::{FoundationData, FoundationService};
use scraper::{Html, Selector};
use serde::{Deserialize, Serialize};
use sqlx::FromRow;
use std::sync::Arc;
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

fn db_pool(state: &Arc<AppState>) -> AppResult<&sqlx::PgPool> {
    state
        .db_pool
        .as_deref()
        .ok_or_else(|| {
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
            let snapshot_id = FoundationService::create_initial(pool, auth.tenant.org_id, foundation_data)
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
    let version = FoundationService::update_section(pool, auth.tenant.org_id, &section, payload.data)
        .await
        .map_err(internal_error)?;
    update_org_foundation_version(pool, auth.tenant.org_id, version)
        .await
        .map_err(internal_error)?;

    let snapshot = FoundationService::get_current(pool, auth.tenant.org_id)
        .await
        .map_err(internal_error)?
        .ok_or_else(|| not_found("foundation_not_found"))?;

    Ok(Json(map_snapshot(&snapshot)))
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
    pub url: String,
}

#[derive(Debug, Serialize)]
pub struct ScanStartResponse {
    pub scan_id: String,
    pub status: String,
}

#[derive(Debug, Serialize)]
pub struct ScanStatusResponse {
    pub status: String,
    pub data: Option<serde_json::Value>,
}

pub async fn start_scan(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
    Json(payload): Json<ScanStartRequest>,
) -> AppResult<Json<ScanStartResponse>> {
    let pool = db_pool(&state)?;

    if payload.url.is_empty() {
        return Err(bad_request("URL is required"));
    }

    let scan_id = format!("scan-{}-{}", auth.tenant.org_id, ulid::Ulid::new());

    sqlx::query(
        r#"
        INSERT INTO foundation_scans (scan_id, org_id, url, status, started_at)
        VALUES ($1, $2, $3, 'running', now())
        "#,
    )
    .bind(&scan_id)
    .bind(auth.tenant.org_id)
    .bind(&payload.url)
    .execute(pool)
    .await
    .map_err(internal_error)?;

    let pool_clone = pool.clone();
    let scan_id_clone = scan_id.clone();
    let url = payload.url.clone();

    tokio::spawn(async move {
        tokio::time::sleep(tokio::time::Duration::from_secs(2)).await;

        let scan_data = quick_scan(&url).await;

        sqlx::query(
            r#"
            UPDATE foundation_scans
            SET status = 'complete', quick_scan_data = $1, completed_at = now()
            WHERE scan_id = $2
            "#,
        )
        .bind(&scan_data)
        .bind(&scan_id_clone)
        .execute(&pool_clone)
        .await
        .ok();
    });

    Ok(Json(ScanStartResponse {
        scan_id,
        status: "started".to_string(),
    }))
}

pub async fn get_scan_status(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
) -> AppResult<Json<ScanStatusResponse>> {
    let pool = db_pool(&state)?;

    let row = sqlx::query_as::<_, (String, Option<serde_json::Value>, Option<serde_json::Value>)>(
        r#"
        SELECT status, quick_scan_data, deep_scan_data
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
        Some((status, quick_data, deep_data)) => {
            let data = if status == "complete" {
                quick_data.or(deep_data)
            } else {
                None
            };
            Ok(Json(ScanStatusResponse { status, data }))
        }
        None => Ok(Json(ScanStatusResponse {
            status: "not_found".to_string(),
            data: None,
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
    "url",
    "scan_results",
    "business_stage",
    "primary_product",
    "customer_problem",
    "icp",
    "transformation",
    "competitors",
    "pricing_model",
    "positioning",
    "brand_personality",
    "keywords",
    "content_channels",
    "content_history",
    "primary_goal",
    "budget",
    "existing_assets",
    "frustrations",
    "analytics_tracking",
    "reference_brands",
    "strategist",
];

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
    let mut completed = Vec::new();
    let mut last_updated = None;
    let mut last_updated_at = chrono::DateTime::<chrono::Utc>::from_timestamp(0, 0)
        .unwrap_or_else(Utc::now);

    for (key, value, updated_at) in rows {
        sections_map.insert(key.clone(), value);
        completed.push(key.clone());
        if updated_at > last_updated_at {
            last_updated_at = updated_at;
            last_updated = Some(key);
        }
    }

    let missing: Vec<String> = ALL_SECTIONS
        .iter()
        .filter(|s| !completed.contains(&s.to_string()))
        .map(|s| s.to_string())
        .collect();

    let status = if missing.is_empty() {
        "complete"
    } else {
        "in_progress"
    };

    Ok(Json(SnapshotFullResponse {
        status: status.to_string(),
        completed_sections: completed.clone(),
        missing_sections: missing,
        last_updated_section: last_updated,
        version: completed.len() as i32,
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

    let rows = sqlx::query_as::<_, (String, serde_json::Value)>(
        r#"
        SELECT section_key, value
        FROM foundation_sections
        WHERE org_id = $1
        "#,
    )
    .bind(auth.tenant.org_id)
    .fetch_all(pool)
    .await
    .map_err(internal_error)?;

    let mut sections = serde_json::Map::new();
    for (key, value) in rows {
        sections.insert(key, value);
    }

    let foundation_json = serde_json::json!({ "sections": sections });

    sqlx::query(
        r#"
        UPDATE organizations
        SET foundation_complete = true,
            foundation_json = $2,
            foundation_completed_at = now(),
            foundation_version = foundation_version + 1,
            updated_at = now()
        WHERE org_id = $1
        "#,
    )
    .bind(auth.tenant.org_id)
    .bind(&foundation_json)
    .execute(pool)
    .await
    .map_err(internal_error)?;

    Ok(Json(CompleteResponse {
        ok: true,
        office_ready: true,
        strategist_name: "Strategist".to_string(),
        first_nudge_id: None,
    }))
}

async fn quick_scan(url: &str) -> serde_json::Value {
    let client = reqwest::Client::builder()
        .timeout(std::time::Duration::from_secs(10))
        .build()
        .unwrap_or_default();

    match client.get(url).send().await {
        Ok(response) => {
            let html = response.text().await.unwrap_or_default();
            let title = extract_title(&html);
            let description = extract_meta(&html, "description");
            let og_title = extract_og(&html, "og:title");
            let og_description = extract_og(&html, "og:description");

            let description_for_raw = description.clone();
            let description_combined = og_description.or(description);
            serde_json::json!({
                "business_name": og_title.or(title.clone()),
                "industry": null,
                "description": description_combined,
                "primary_offering": null,
                "competitor_suggestions": [],
                "keyword_suggestions": [],
                "confidence": "low",
                "raw": {
                    "title": title,
                    "description": description_for_raw,
                    "url": url
                }
            })
        }
        Err(_) => serde_json::json!({
            "business_name": null,
            "industry": null,
            "description": null,
            "primary_offering": null,
            "competitor_suggestions": [],
            "keyword_suggestions": [],
            "confidence": "failed",
            "error": "Could not fetch URL"
        }),
    }
}

fn extract_title(html: &str) -> Option<String> {
    Html::parse_document(html)
        .select(&Selector::parse("title").ok()?)
        .next()
        .map(|el: scraper::ElementRef| el.text().collect::<String>().trim().to_string())
        .filter(|t: &String| !t.is_empty())
        .map(|t| t.clone())
}

fn extract_meta(html: &str, name: &str) -> Option<String> {
    let selector = Selector::parse(&format!("meta[name=\"{}\"]", name)).ok()?;
    Html::parse_document(html)
        .select(&selector)
        .next()
        .and_then(|el: scraper::ElementRef| el.value().attr("content"))
        .map(|s: &str| s.to_string())
}

fn extract_og(html: &str, property: &str) -> Option<String> {
    let selector = Selector::parse(&format!("meta[property=\"{}\"]", property)).ok()?;
    Html::parse_document(html)
        .select(&selector)
        .next()
        .and_then(|el: scraper::ElementRef| el.value().attr("content"))
        .map(|s: &str| s.to_string())
}
