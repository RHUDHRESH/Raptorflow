//! Competitor intelligence for RaptorFlow.
//!
//! ## Status
//!
//! Routes exist for listing intel artifacts and research overview.

use axum::{extract::Extension, http::StatusCode, Json, Router, routing::get};
use raptorflow_auth::TenantContext;
use serde_json::{Value, json};
use sqlx::PgPool;
use std::sync::Arc;

pub fn router() -> Router {
    Router::new()
        .route("/", get(list_intel_overview))
        .route("/runs", get(list_research_runs))
        .route("/documents", get(list_documents))
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
    Extension(pool): Extension<Arc<PgPool>>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;
    
    let total_runs: (i64,) = sqlx::query_as(
        "SELECT COUNT(*)::bigint FROM research.research_runs WHERE org_id = $1"
    )
    .bind(org_id)
    .fetch_one(pool.as_ref())
    .await
    .map_err(internal_error)?;

    let total_documents: (i64,) = sqlx::query_as(
        "SELECT COUNT(*)::bigint FROM research.research_documents WHERE org_id = $1"
    )
    .bind(org_id)
    .fetch_one(pool.as_ref())
    .await
    .map_err(internal_error)?;

    Ok(Json(json!({
        "total_runs": total_runs.0,
        "total_documents": total_documents.0,
        "status": "ok"
    })))
}

pub async fn list_research_runs(
    Extension(tenant): Extension<TenantContext>,
    Extension(pool): Extension<Arc<PgPool>>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;
    
    let rows: Vec<(uuid::Uuid, String, String, chrono::DateTime<chrono::Utc>, bool)> = sqlx::query_as(
        r#"
        SELECT run_id, request_kind, query, created_at, cache_hit
        FROM research.research_runs
        WHERE org_id = $1
        ORDER BY created_at DESC
        LIMIT 20
        "#
    )
    .bind(org_id)
    .fetch_all(pool.as_ref())
    .await
    .map_err(internal_error)?;

    let runs: Vec<Value> = rows.into_iter().map(|r| json!({
        "run_id": r.0.to_string(),
        "request_kind": r.1,
        "query": r.2,
        "created_at": r.3.to_rfc3339(),
        "cache_hit": r.4
    })).collect();

    Ok(Json(json!({ "runs": runs, "status": "ok" })))
}

pub async fn list_documents(
    Extension(tenant): Extension<TenantContext>,
    Extension(pool): Extension<Arc<PgPool>>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;
    
    let rows: Vec<(uuid::Uuid, String, String, chrono::DateTime<chrono::Utc>)> = sqlx::query_as(
        r#"
        SELECT document_id, url, domain, fetched_at
        FROM research.research_documents
        WHERE org_id = $1
        ORDER BY fetched_at DESC
        LIMIT 50
        "#
    )
    .bind(org_id)
    .fetch_all(pool.as_ref())
    .await
    .map_err(internal_error)?;

    let documents: Vec<Value> = rows.into_iter().map(|d| json!({
        "document_id": d.0.to_string(),
        "url": d.1,
        "domain": d.2,
        "fetched_at": d.3.to_rfc3339()
    })).collect();

    Ok(Json(json!({ "documents": documents, "status": "ok" })))
}
