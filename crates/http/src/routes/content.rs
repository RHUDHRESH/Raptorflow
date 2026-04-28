use axum::{
    Json,
    extract::{Extension, Path},
    http::StatusCode,
};
use serde::{Deserialize, Serialize};
use serde_json::{Value, json};
use ulid::Ulid;

use raptorflow_auth::TenantContext;
use raptorflow_db::models::GeneratedContent;
use raptorflow_db::{TenantDbPool, queries};

type AppResult<T> = Result<T, (StatusCode, Json<Value>)>;

fn internal_error<E: std::fmt::Display>(e: E) -> (StatusCode, Json<Value>) {
    tracing::error!("Content route error: {e}");
    (
        StatusCode::INTERNAL_SERVER_ERROR,
        Json(json!({ "error": "content_internal_error" })),
    )
}

fn bad_request(msg: &str) -> (StatusCode, Json<Value>) {
    (StatusCode::BAD_REQUEST, Json(json!({ "error": msg })))
}

fn not_found() -> (StatusCode, Json<Value>) {
    (
        StatusCode::NOT_FOUND,
        Json(json!({ "error": "content_not_found" })),
    )
}

#[derive(Debug, Deserialize)]
pub struct CreateContentRequest {
    pub campaign_id: Option<String>,
    pub task_id: Option<String>,
    pub content_type: String,
    pub body: serde_json::Value,
}

#[derive(Debug, Serialize)]
pub struct ContentResponse {
    pub content_id: String,
    pub org_id: String,
    pub campaign_id: Option<String>,
    pub task_id: Option<String>,
    pub content_type: String,
    pub status: String,
    pub body: serde_json::Value,
    pub created_at: String,
}

impl From<GeneratedContent> for ContentResponse {
    fn from(c: GeneratedContent) -> Self {
        Self {
            content_id: c.content_id,
            org_id: c.org_id.to_string(),
            campaign_id: c.campaign_id,
            task_id: c.task_id,
            content_type: c.content_type,
            status: c.status,
            body: c.body,
            created_at: c.created_at.to_rfc3339(),
        }
    }
}

pub async fn list_content(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;

    let content = queries::list_generated_content(tenant_pool.pool(), org_id)
        .await
        .map_err(internal_error)?;

    let list: Vec<ContentResponse> = content.into_iter().map(Into::into).collect();

    Ok(Json(json!({
        "content": list,
        "total": list.len(),
        "status": "ok"
    })))
}

pub async fn create_content(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Json(req): Json<CreateContentRequest>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;

    if req.content_type.trim().is_empty() {
        return Err(bad_request("content_type_required"));
    }

    if let Err(errors) = crate::routes::validation::validate_content(&req.content_type, &req.body) {
        return Err((
            StatusCode::UNPROCESSABLE_ENTITY,
            Json(json!({
                "error": "content_validation_failed",
                "details": errors,
                "content_type": req.content_type,
            })),
        ));
    }

    let content_id = Ulid::new().to_string();

    queries::create_generated_content(
        tenant_pool.pool(),
        &content_id,
        org_id,
        req.campaign_id.as_deref(),
        req.task_id.as_deref(),
        &req.content_type,
        "generated",
        &req.body,
    )
    .await
    .map_err(internal_error)?;

    let content = queries::get_generated_content(tenant_pool.pool(), &content_id, org_id)
        .await
        .map_err(internal_error)?;

    match content {
        Some(c) => Ok(Json(json!({
            "content": ContentResponse::from(c),
            "status": "created"
        }))),
        None => Err(internal_error("content_not_found_after_create")),
    }
}

pub async fn get_content(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(content_id): Path<String>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;

    let content = queries::get_generated_content(tenant_pool.pool(), &content_id, org_id)
        .await
        .map_err(internal_error)?;

    match content {
        Some(c) => Ok(Json(json!({
            "content": ContentResponse::from(c),
            "status": "ok"
        }))),
        None => Err(not_found()),
    }
}
