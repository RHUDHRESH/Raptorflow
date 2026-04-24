//! Competitor intelligence for RaptorFlow.
//!
//! ## Status
//!
//! Routes exist for listing intel artifacts and research overview.

use axum::{
    Json, Router, extract::{Extension, Path, Query}, http::StatusCode,
    routing::{get, patch, post},
};
use raptorflow_auth::TenantContext;
use raptorflow_db::TenantDbPool;
use serde::Deserialize;
use serde_json::{Value, json};
use ulid::Ulid;

pub fn router() -> Router {
    Router::new()
        .route("/", get(list_intel_overview))
        .route("/runs", get(list_research_runs))
        .route("/documents", get(list_documents))
        .route("/signals", get(list_signals).post(create_signal))
        .route("/signals/:signal_id", get(get_signal).patch(update_signal))
        .route("/competitors", get(list_competitor_snapshots).post(create_competitor_snapshot))
}

type AppResult<T> = Result<T, (StatusCode, Json<Value>)>;

fn internal_error<E: std::fmt::Display>(e: E) -> (StatusCode, Json<Value>) {
    tracing::error!("Intel route error: {e}");
    (
        StatusCode::INTERNAL_SERVER_ERROR,
        Json(json!({ "error": "intel_internal_error" })),
    )
}

pub async fn list_intel_overview(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;
    let clerk_user_id = &tenant.user_id;
    let mut conn: sqlx::pool::PoolConnection<sqlx::postgres::Postgres> = tenant_pool
        .acquire_for_tenant(org_id)
        .await
        .map_err(internal_error)?;

    let total_runs: (i64,) =
        sqlx::query_as("SELECT COUNT(*)::bigint FROM research.research_runs WHERE org_id = $1")
            .bind(org_id)
            .fetch_one(&mut *conn)
            .await
            .map_err(internal_error)?;

    let total_documents: (i64,) = sqlx::query_as(
        "SELECT COUNT(*)::bigint FROM research.research_documents WHERE org_id = $1",
    )
    .bind(org_id)
    .fetch_one(&mut *conn)
    .await
    .map_err(internal_error)?;

    let signal_rows: Vec<(
        String,
        String,
        String,
        String,
        String,
        Option<String>,
        String,
        bool,
        bool,
        Option<String>,
        chrono::DateTime<chrono::Utc>,
    )> = sqlx::query_as(
        r#"
        SELECT id, user_id, type, source, title, detail, summary, is_read, is_archived, related_to, created_at
        FROM intel_signals
        WHERE user_id = $1
        ORDER BY created_at DESC
        LIMIT 50
        "#,
    )
    .bind(clerk_user_id)
    .fetch_all(&mut *conn)
    .await
    .map_err(internal_error)?;

    let signals: Vec<Value> = signal_rows
        .into_iter()
        .map(|r| {
            json!({
                "id": r.0,
                "userId": r.1,
                "type": r.2,
                "source": r.3,
                "title": r.4,
                "detail": r.5,
                "summary": r.6,
                "isRead": r.7,
                "isArchived": r.8,
                "relatedTo": r.9,
                "createdAt": r.10.to_rfc3339()
            })
        })
        .collect();

    Ok(Json(json!({
        "total_runs": total_runs.0,
        "total_documents": total_documents.0,
        "signals": signals,
        "status": "ok"
    })))
}

pub async fn list_research_runs(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;
    let mut conn: sqlx::pool::PoolConnection<sqlx::postgres::Postgres> = tenant_pool
        .acquire_for_tenant(org_id)
        .await
        .map_err(internal_error)?;

    let rows: Vec<(
        uuid::Uuid,
        String,
        String,
        chrono::DateTime<chrono::Utc>,
        bool,
    )> = sqlx::query_as(
        r#"
        SELECT run_id, request_kind, query, created_at, cache_hit
        FROM research.research_runs
        WHERE org_id = $1
        ORDER BY created_at DESC
        LIMIT 20
        "#,
    )
    .bind(org_id)
    .fetch_all(&mut *conn)
    .await
    .map_err(internal_error)?;

    let runs: Vec<Value> = rows
        .into_iter()
        .map(|r| {
            json!({
                "run_id": r.0.to_string(),
                "request_kind": r.1,
                "query": r.2,
                "created_at": r.3.to_rfc3339(),
                "cache_hit": r.4
            })
        })
        .collect();

    Ok(Json(json!({ "runs": runs, "status": "ok" })))
}

pub async fn list_documents(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;
    let mut conn: sqlx::pool::PoolConnection<sqlx::postgres::Postgres> = tenant_pool
        .acquire_for_tenant(org_id)
        .await
        .map_err(internal_error)?;

    let rows: Vec<(uuid::Uuid, String, String, chrono::DateTime<chrono::Utc>)> = sqlx::query_as(
        r#"
        SELECT document_id, url, domain, fetched_at
        FROM research.research_documents
        WHERE org_id = $1
        ORDER BY fetched_at DESC
        LIMIT 50
        "#,
    )
    .bind(org_id)
    .fetch_all(&mut *conn)
    .await
    .map_err(internal_error)?;

    let documents: Vec<Value> = rows
        .into_iter()
        .map(|d| {
            json!({
                "document_id": d.0.to_string(),
                "url": d.1,
                "domain": d.2,
                "fetched_at": d.3.to_rfc3339()
            })
        })
        .collect();

    Ok(Json(json!({ "documents": documents, "status": "ok" })))
}

#[derive(Debug, Deserialize)]
pub struct ListSignalsQuery {
    #[serde(default)]
    pub type_: Option<String>,
}

pub async fn list_signals(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Query(query): Query<ListSignalsQuery>,
) -> AppResult<Json<Value>> {
    let clerk_user_id = &tenant.user_id;
    let mut conn: sqlx::pool::PoolConnection<sqlx::postgres::Postgres> = tenant_pool
        .acquire_for_tenant(tenant.org_id)
        .await
        .map_err(internal_error)?;

    let type_filter = query.type_.as_deref();

    let rows: Vec<(
        String,
        String,
        String,
        String,
        String,
        Option<String>,
        String,
        bool,
        bool,
        Option<String>,
        chrono::DateTime<chrono::Utc>,
    )> = if let Some(type_filter) = type_filter {
        sqlx::query_as(
            r#"
            SELECT id, user_id, type, source, title, detail, summary, is_read, is_archived, related_to, created_at
            FROM intel_signals
            WHERE user_id = $1 AND type = $2
            ORDER BY created_at DESC
            LIMIT 50
            "#,
        )
        .bind(clerk_user_id)
        .bind(type_filter)
        .fetch_all(&mut *conn)
        .await
        .map_err(internal_error)?
    } else {
        sqlx::query_as(
            r#"
            SELECT id, user_id, type, source, title, detail, summary, is_read, is_archived, related_to, created_at
            FROM intel_signals
            WHERE user_id = $1
            ORDER BY created_at DESC
            LIMIT 50
            "#,
        )
        .bind(clerk_user_id)
        .fetch_all(&mut *conn)
        .await
        .map_err(internal_error)?
    };

    let signals: Vec<Value> = rows
        .into_iter()
        .map(|r| {
            json!({
                "id": r.0,
                "userId": r.1,
                "type": r.2,
                "source": r.3,
                "title": r.4,
                "detail": r.5,
                "summary": r.6,
                "isRead": r.7,
                "isArchived": r.8,
                "relatedTo": r.9,
                "createdAt": r.10.to_rfc3339()
            })
        })
        .collect();

    Ok(Json(json!({ "signals": signals, "status": "ok" })))
}

#[derive(Debug, Deserialize)]
pub struct CreateSignalRequest {
    #[serde(rename = "type")]
    pub signal_type: String,
    pub source: String,
    pub title: String,
    pub summary: String,
    pub detail: Option<String>,
    pub severity: Option<String>,
    pub related_to: Option<String>,
}

pub async fn create_signal(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Json(payload): Json<CreateSignalRequest>,
) -> AppResult<Json<Value>> {
    let clerk_user_id = &tenant.user_id;
    let mut conn: sqlx::pool::PoolConnection<sqlx::postgres::Postgres> = tenant_pool
        .acquire_for_tenant(tenant.org_id)
        .await
        .map_err(internal_error)?;

    let signal_id = format!("sig-{}-{}", clerk_user_id, Ulid::new());

    let severity = payload.severity.unwrap_or_else(|| "medium".to_string());

    sqlx::query(
        r#"
        INSERT INTO intel_signals (id, user_id, type, source, title, summary, detail, severity, is_read, is_archived, related_to)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8, false, false, $9)
        "#,
    )
    .bind(&signal_id)
    .bind(clerk_user_id)
    .bind(&payload.signal_type)
    .bind(&payload.source)
    .bind(&payload.title)
    .bind(&payload.summary)
    .bind(&payload.detail)
    .bind(&severity)
    .bind(&payload.related_to)
    .execute(&mut *conn)
    .await
    .map_err(internal_error)?;

    Ok(Json(json!({
        "id": signal_id,
        "status": "created"
    })))
}

#[derive(Debug, Deserialize)]
pub struct UpdateSignalRequest {
    #[serde(default)]
    pub is_read: Option<bool>,
    #[serde(default)]
    pub is_archived: Option<bool>,
}

pub async fn get_signal(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(signal_id): Path<String>,
) -> AppResult<Json<Value>> {
    let clerk_user_id = &tenant.user_id;
    let mut conn: sqlx::pool::PoolConnection<sqlx::postgres::Postgres> = tenant_pool
        .acquire_for_tenant(tenant.org_id)
        .await
        .map_err(internal_error)?;

    let row: Option<(
        String,
        String,
        String,
        String,
        String,
        Option<String>,
        String,
        bool,
        bool,
        Option<String>,
        chrono::DateTime<chrono::Utc>,
    )> = sqlx::query_as(
        r#"
        SELECT id, user_id, type, source, title, detail, summary, is_read, is_archived, related_to, created_at
        FROM intel_signals
        WHERE id = $1 AND user_id = $2
        "#,
    )
    .bind(&signal_id)
    .bind(clerk_user_id)
    .fetch_optional(&mut *conn)
    .await
    .map_err(internal_error)?;

    match row {
        Some(r) => Ok(Json(json!({
            "id": r.0,
            "userId": r.1,
            "type": r.2,
            "source": r.3,
            "title": r.4,
            "detail": r.5,
            "summary": r.6,
            "isRead": r.7,
            "isArchived": r.8,
            "relatedTo": r.9,
            "createdAt": r.10.to_rfc3339()
        }))),
        None => Err((
            StatusCode::NOT_FOUND,
            Json(json!({ "error": "not_found" })),
        )),
    }
}

pub async fn update_signal(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(signal_id): Path<String>,
    Json(payload): Json<UpdateSignalRequest>,
) -> AppResult<Json<Value>> {
    let clerk_user_id = &tenant.user_id;
    let mut conn: sqlx::pool::PoolConnection<sqlx::postgres::Postgres> = tenant_pool
        .acquire_for_tenant(tenant.org_id)
        .await
        .map_err(internal_error)?;

    let existing: Option<(bool, bool)> = sqlx::query_as(
        r#"
        SELECT is_read, is_archived
        FROM intel_signals
        WHERE id = $1 AND user_id = $2
        "#,
    )
    .bind(&signal_id)
    .bind(clerk_user_id)
    .fetch_optional(&mut *conn)
    .await
    .map_err(internal_error)?;

    let Some((current_is_read, current_is_archived)) = existing else {
        return Err((
            StatusCode::NOT_FOUND,
            Json(json!({ "error": "not_found" })),
        ));
    };

    let new_is_read = payload.is_read.unwrap_or(current_is_read);
    let new_is_archived = payload.is_archived.unwrap_or(current_is_archived);

    sqlx::query(
        r#"
        UPDATE intel_signals
        SET is_read = $1, is_archived = $2
        WHERE id = $3 AND user_id = $4
        "#,
    )
    .bind(new_is_read)
    .bind(new_is_archived)
    .bind(&signal_id)
    .bind(clerk_user_id)
    .execute(&mut *conn)
    .await
    .map_err(internal_error)?;

    Ok(Json(json!({
        "id": signal_id,
        "isRead": new_is_read,
        "isArchived": new_is_archived
    })))
}

#[derive(Debug, Deserialize)]
pub struct CreateCompetitorSnapshotRequest {
    pub competitor_name: String,
    pub website: Option<String>,
}

pub async fn list_competitor_snapshots(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;
    let mut conn: sqlx::pool::PoolConnection<sqlx::postgres::Postgres> = tenant_pool
        .acquire_for_tenant(org_id)
        .await
        .map_err(internal_error)?;

    let rows: Vec<(String, String, String, chrono::DateTime<chrono::Utc>)> = sqlx::query_as(
        r#"
        SELECT snapshot_id, competitor_name, status, captured_at
        FROM competitor_snapshots
        WHERE org_id = $1
        ORDER BY captured_at DESC
        LIMIT 50
        "#,
    )
    .bind(org_id)
    .fetch_all(&mut *conn)
    .await
    .map_err(internal_error)?;

    let snapshots: Vec<Value> = rows
        .into_iter()
        .map(|r| {
            json!({
                "snapshot_id": r.0,
                "competitor_name": r.1,
                "status": r.2,
                "captured_at": r.3.to_rfc3339()
            })
        })
        .collect();

    Ok(Json(json!({ "snapshots": snapshots, "status": "ok" })))
}

pub async fn create_competitor_snapshot(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Json(payload): Json<CreateCompetitorSnapshotRequest>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;
    let mut conn: sqlx::pool::PoolConnection<sqlx::postgres::Postgres> = tenant_pool
        .acquire_for_tenant(org_id)
        .await
        .map_err(internal_error)?;

    let snapshot_id = format!("comp-snap-{}-{}", org_id, ulid::Ulid::new());

    sqlx::query(
        r#"
        INSERT INTO competitor_snapshots (snapshot_id, org_id, competitor_name, snapshot_type, payload, captured_at)
        VALUES ($1, $2, $3, $4, $5, now())
        "#,
    )
    .bind(&snapshot_id)
    .bind(org_id)
    .bind(&payload.competitor_name)
    .bind("manual")
    .bind(serde_json::json!({ "website": payload.website }))
    .execute(&mut *conn)
    .await
    .map_err(internal_error)?;

    Ok(Json(json!({
        "snapshot_id": snapshot_id,
        "status": "created"
    })))
}
