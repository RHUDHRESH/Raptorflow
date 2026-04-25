//! Competitor intelligence for RaptorFlow.
//!
//! ## Status
//!
//! Routes exist for listing intel artifacts and research overview.

use axum::{
    Json, Router,
    extract::{Extension, Path, Query},
    http::StatusCode,
    routing::get,
};
use raptorflow_auth::TenantContext;
use raptorflow_db::TenantDbPool;
use serde::{Deserialize, Serialize};
use serde_json::{Value, json};

type SignalRow = (
    String,
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
);
type SignalRowOpt = Option<(
    String,
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
)>;
type CompetitorRow = (
    String,
    String,
    String,
    Option<String>,
    Value,
    chrono::DateTime<chrono::Utc>,
    chrono::DateTime<chrono::Utc>,
);

#[allow(dead_code)]
pub fn router() -> Router {
    Router::new()
        .route("/", get(list_intel_overview))
        .route("/runs", get(list_research_runs))
        .route("/documents", get(list_documents))
        .route("/signals", get(list_signals))
        .route("/signals/:id", get(get_signal).patch(update_signal))
        .route(
            "/competitors",
            get(list_competitor_snapshots).post(create_competitor_snapshot),
        )
}

type AppResult<T> = Result<T, (StatusCode, Json<Value>)>;

fn internal_error<E: std::fmt::Display>(e: E) -> (StatusCode, Json<Value>) {
    tracing::error!("Intel route error: {e}");
    (
        StatusCode::INTERNAL_SERVER_ERROR,
        Json(json!({ "error": "intel_internal_error" })),
    )
}

#[derive(Debug, Deserialize)]
pub struct SignalsQuery {
    #[serde(rename = "type")]
    pub signal_type: Option<String>,
}

#[derive(Debug, Serialize)]
pub struct IntelSignalResponse {
    pub id: String,
    pub user_id: String,
    #[serde(rename = "type")]
    pub signal_type: String,
    pub source: String,
    pub title: String,
    pub summary: String,
    pub detail: Option<String>,
    pub severity: String,
    pub is_read: bool,
    pub is_archived: bool,
    pub related_to: Option<String>,
    pub created_at: String,
}

impl
    From<(
        String,
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
    )> for IntelSignalResponse
{
    fn from(
        row: (
            String,
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
        ),
    ) -> Self {
        IntelSignalResponse {
            id: row.0,
            user_id: row.1,
            signal_type: row.2,
            source: row.3,
            title: row.4,
            summary: row.5,
            detail: row.6,
            severity: row.7,
            is_read: row.8,
            is_archived: row.9,
            related_to: row.10,
            created_at: row.11.to_rfc3339(),
        }
    }
}

pub async fn list_intel_overview(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;
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

    let rows: Vec<SignalRow> = sqlx::query_as(
        r#"
        SELECT id, user_id, type, source, title, summary, detail, severity, is_read, is_archived, related_to, created_at
        FROM intel_signals
        WHERE user_id = $1 AND is_archived = false
        ORDER BY created_at DESC
        LIMIT 20
        "#,
    )
    .bind(&tenant.user_id)
    .fetch_all(&mut *conn)
    .await
    .map_err(internal_error)?;

    let signals: Vec<Value> = rows
        .into_iter()
        .map(|r| {
            let sig: IntelSignalResponse = r.into();
            serde_json::to_value(sig).unwrap_or(json!({}))
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

pub async fn list_signals(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Query(query): Query<SignalsQuery>,
) -> AppResult<Json<Value>> {
    let mut conn: sqlx::pool::PoolConnection<sqlx::postgres::Postgres> = tenant_pool
        .acquire_for_tenant(tenant.org_id)
        .await
        .map_err(internal_error)?;

    let rows: Vec<SignalRow> = if let Some(ref signal_type) = query.signal_type {
        sqlx::query_as(
            r#"
            SELECT id, user_id, type, source, title, summary, detail, severity, is_read, is_archived, related_to, created_at
            FROM intel_signals
            WHERE user_id = $1 AND type = $2 AND is_archived = false
            ORDER BY created_at DESC
            LIMIT 50
            "#,
        )
        .bind(&tenant.user_id)
        .bind(signal_type)
        .fetch_all(&mut *conn)
        .await
        .map_err(internal_error)?
    } else {
        sqlx::query_as(
            r#"
            SELECT id, user_id, type, source, title, summary, detail, severity, is_read, is_archived, related_to, created_at
            FROM intel_signals
            WHERE user_id = $1 AND is_archived = false
            ORDER BY created_at DESC
            LIMIT 50
            "#,
        )
        .bind(&tenant.user_id)
        .fetch_all(&mut *conn)
        .await
        .map_err(internal_error)?
    };

    let signals: Vec<Value> = rows
        .into_iter()
        .map(|r| {
            let sig: IntelSignalResponse = r.into();
            serde_json::to_value(sig).unwrap_or(json!({}))
        })
        .collect();

    Ok(Json(json!({ "signals": signals, "status": "ok" })))
}

pub async fn get_signal(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(signal_id): Path<String>,
) -> AppResult<Json<Value>> {
    let mut conn: sqlx::pool::PoolConnection<sqlx::postgres::Postgres> = tenant_pool
        .acquire_for_tenant(tenant.org_id)
        .await
        .map_err(internal_error)?;

    let row: SignalRowOpt = sqlx::query_as(
        r#"
        SELECT id, user_id, type, source, title, summary, detail, severity, is_read, is_archived, related_to, created_at
        FROM intel_signals
        WHERE id = $1 AND user_id = $2
        "#,
    )
    .bind(&signal_id)
    .bind(&tenant.user_id)
    .fetch_optional(&mut *conn)
    .await
    .map_err(internal_error)?;

    match row {
        Some(r) => {
            let sig: IntelSignalResponse = r.into();
            Ok(Json(serde_json::to_value(sig).unwrap_or(json!({}))))
        }
        None => Err((
            StatusCode::NOT_FOUND,
            Json(json!({ "error": "signal_not_found" })),
        )),
    }
}

#[derive(Debug, Deserialize)]
pub struct UpdateSignalRequest {
    pub is_read: Option<bool>,
    pub is_archived: Option<bool>,
}

pub async fn update_signal(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(signal_id): Path<String>,
    Json(payload): Json<UpdateSignalRequest>,
) -> AppResult<Json<Value>> {
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
    .bind(&tenant.user_id)
    .fetch_optional(&mut *conn)
    .await
    .map_err(internal_error)?;

    let (current_read, current_archived) = match existing {
        Some((r, a)) => (r, a),
        None => {
            return Err((
                StatusCode::NOT_FOUND,
                Json(json!({ "error": "signal_not_found" })),
            ));
        }
    };

    let new_read = payload.is_read.unwrap_or(current_read);
    let new_archived = payload.is_archived.unwrap_or(current_archived);

    sqlx::query(
        r#"
        UPDATE intel_signals
        SET is_read = $1, is_archived = $2, updated_at = now()
        WHERE id = $3 AND user_id = $4
        "#,
    )
    .bind(new_read)
    .bind(new_archived)
    .bind(&signal_id)
    .bind(&tenant.user_id)
    .execute(&mut *conn)
    .await
    .map_err(internal_error)?;

    Ok(Json(json!({ "ok": true })))
}

#[derive(Debug, Serialize)]
pub struct CompetitorSnapshotResponse {
    pub id: String,
    pub user_id: String,
    pub competitor_name: String,
    pub website: Option<String>,
    pub snapshot: Value,
    pub last_analyzed_at: String,
    pub created_at: String,
}

impl
    From<(
        String,
        String,
        String,
        Option<String>,
        Value,
        chrono::DateTime<chrono::Utc>,
        chrono::DateTime<chrono::Utc>,
    )> for CompetitorSnapshotResponse
{
    fn from(
        row: (
            String,
            String,
            String,
            Option<String>,
            Value,
            chrono::DateTime<chrono::Utc>,
            chrono::DateTime<chrono::Utc>,
        ),
    ) -> Self {
        CompetitorSnapshotResponse {
            id: row.0,
            user_id: row.1,
            competitor_name: row.2,
            website: row.3,
            snapshot: row.4,
            last_analyzed_at: row.5.to_rfc3339(),
            created_at: row.6.to_rfc3339(),
        }
    }
}

pub async fn list_competitor_snapshots(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
) -> AppResult<Json<Value>> {
    let mut conn: sqlx::pool::PoolConnection<sqlx::postgres::Postgres> = tenant_pool
        .acquire_for_tenant(tenant.org_id)
        .await
        .map_err(internal_error)?;

    let rows: Vec<CompetitorRow> = sqlx::query_as(
        r#"
        SELECT id, user_id, competitor_name, website, snapshot, last_analyzed_at, created_at
        FROM competitor_snapshots
        WHERE user_id = $1
        ORDER BY last_analyzed_at DESC
        LIMIT 50
        "#,
    )
    .bind(&tenant.user_id)
    .fetch_all(&mut *conn)
    .await
    .map_err(internal_error)?;

    let snapshots: Vec<Value> = rows
        .into_iter()
        .map(|r| {
            let snap: CompetitorSnapshotResponse = r.into();
            serde_json::to_value(snap).unwrap_or(json!({}))
        })
        .collect();

    Ok(Json(
        json!({ "competitor_snapshots": snapshots, "status": "ok" }),
    ))
}

#[derive(Debug, Deserialize)]
pub struct CreateCompetitorSnapshotRequest {
    pub competitor_name: String,
    pub website: Option<String>,
}

pub async fn create_competitor_snapshot(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Json(payload): Json<CreateCompetitorSnapshotRequest>,
) -> AppResult<Json<Value>> {
    let mut conn: sqlx::pool::PoolConnection<sqlx::postgres::Postgres> = tenant_pool
        .acquire_for_tenant(tenant.org_id)
        .await
        .map_err(internal_error)?;

    let snapshot_id = uuid::Uuid::new_v4().to_string();

    sqlx::query(
        r#"
        INSERT INTO competitor_snapshots (id, user_id, competitor_name, website, snapshot, last_analyzed_at, created_at)
        VALUES ($1, $2, $3, $4, '{}', now(), now())
        "#,
    )
    .bind(&snapshot_id)
    .bind(&tenant.user_id)
    .bind(&payload.competitor_name)
    .bind(&payload.website)
    .execute(&mut *conn)
    .await
    .map_err(internal_error)?;

    Ok(Json(
        json!({ "snapshot_id": snapshot_id, "status": "created" }),
    ))
}
