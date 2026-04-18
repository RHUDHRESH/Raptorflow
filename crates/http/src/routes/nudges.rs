use axum::{
    extract::{Extension, Path},
    http::StatusCode,
    Json, Router,
    routing::{get, post},
};
use serde::{Deserialize, Serialize};
use serde_json::{Value, json};
use uuid::Uuid;

use raptorflow_auth::TenantContext;
use raptorflow_db::{queries, TenantDbPool};
use crate::routes::office::handlers::emit_office_event;

pub fn router() -> Router {
    Router::new()
        .route("/", get(list_nudges).post(create_nudge))
        .route("/{id}", get(get_nudge))
        .route("/{id}/viewed", post(mark_viewed))
        .route("/{id}/dismissed", post(mark_dismissed))
}

type AppResult<T> = Result<T, (StatusCode, Json<Value>)>;

fn internal_error<E: std::fmt::Display>(e: E) -> (StatusCode, Json<Value>) {
    tracing::error!("Nudges route error: {e}");
    (
        StatusCode::INTERNAL_SERVER_ERROR,
        Json(json!({ "error": "nudges_internal_error" })),
    )
}

fn bad_request(msg: &str) -> (StatusCode, Json<Value>) {
    (StatusCode::BAD_REQUEST, Json(json!({ "error": msg })))
}

fn not_found() -> (StatusCode, Json<Value>) {
    (StatusCode::NOT_FOUND, Json(json!({ "error": "nudge_not_found" })))
}

#[derive(Debug, Deserialize)]
pub struct CreateNudgeRequest {
    pub user_id: Uuid,
    pub nudge_type: String,
    pub priority: String,
    pub title: String,
    pub body: String,
    pub action_type: Option<String>,
    pub action_data: Option<serde_json::Value>,
    pub source_type: String,
    pub source_id: String,
}

#[derive(Debug, Serialize)]
pub struct NudgeResponse {
    pub nudge_id: String,
    pub org_id: String,
    pub user_id: String,
    pub nudge_type: String,
    pub priority: String,
    pub title: String,
    pub body: String,
    pub action_type: Option<String>,
    pub action_data: serde_json::Value,
    pub source_type: String,
    pub source_id: String,
    pub created_at: String,
    pub delivered_at: Option<String>,
    pub viewed_at: Option<String>,
    pub acted_on_at: Option<String>,
    pub dismissed_at: Option<String>,
    pub suppressed: bool,
}

pub async fn list_nudges(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;

    let nudges = queries::list_nudges(&tenant_pool.pool(), org_id)
        .await
        .map_err(internal_error)?;

    let list: Vec<NudgeResponse> = nudges
        .into_iter()
        .map(|n| NudgeResponse {
            nudge_id: n.nudge_id,
            org_id: n.org_id.to_string(),
            user_id: n.user_id.to_string(),
            nudge_type: n.nudge_type,
            priority: n.priority,
            title: n.title,
            body: n.body,
            action_type: n.action_type,
            action_data: n.action_data,
            source_type: n.source_type,
            source_id: n.source_id,
            created_at: n.created_at.to_rfc3339(),
            delivered_at: n.delivered_at.map(|t| t.to_rfc3339()),
            viewed_at: n.viewed_at.map(|t| t.to_rfc3339()),
            acted_on_at: n.acted_on_at.map(|t| t.to_rfc3339()),
            dismissed_at: n.dismissed_at.map(|t| t.to_rfc3339()),
            suppressed: n.suppressed,
        })
        .collect();

    Ok(Json(json!({
        "nudges": list,
        "total": list.len(),
        "status": "ok"
    })))
}

pub async fn create_nudge(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Json(input): Json<CreateNudgeRequest>,
) -> AppResult<Json<Value>> {
    if input.title.trim().is_empty() {
        return Err(bad_request("title_required"));
    }
    if input.body.trim().is_empty() {
        return Err(bad_request("body_required"));
    }

    let org_id = tenant.org_id;
    let nudge_id = format!("nudge_{}", Uuid::new_v4());

    let priority = if input.nudge_type == "foundation_update" {
        "1".to_string()
    } else {
        input.priority
    };

    let action_type = input.action_type.clone();
    let action_data = if input.nudge_type == "foundation_update" {
        if let Some(data) = &input.action_data {
            let field = data.get("field").and_then(|f| f.as_str()).unwrap_or("");
            let value = data.get("suggestedValue").and_then(|v| v.as_str()).unwrap_or("");
            let action_url = format!("/foundation?edit={}&value={}", field, value.replace(' ', "%20"));
            Some(serde_json::json!({ "action_url": action_url }))
        } else {
            None
        }
    } else {
        input.action_data
    };

    queries::create_nudge(
        &tenant_pool.pool(),
        &nudge_id,
        org_id,
        input.user_id,
        &input.nudge_type,
        &priority,
        &input.title,
        &input.body,
        action_type.as_deref(),
        action_data.as_ref().unwrap_or(&serde_json::json!({})),
        &input.source_type,
        &input.source_id,
    )
    .await
    .map_err(internal_error)?;

    emit_office_event("nudge_created", org_id, json!({"nudge_id": nudge_id, "title": &input.title, "nudge_type": &input.nudge_type}));

    Ok(Json(json!({
        "nudge_id": nudge_id,
        "status": "created"
    })))
}

pub async fn get_nudge(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(nudge_id): Path<String>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;

    let nudge = queries::get_nudge(&tenant_pool.pool(), &nudge_id, org_id)
        .await
        .map_err(internal_error)?;

    match nudge {
        Some(n) => Ok(Json(json!({
            "nudge": NudgeResponse {
                nudge_id: n.nudge_id,
                org_id: n.org_id.to_string(),
                user_id: n.user_id.to_string(),
                nudge_type: n.nudge_type,
                priority: n.priority,
                title: n.title,
                body: n.body,
                action_type: n.action_type,
                action_data: n.action_data,
                source_type: n.source_type,
                source_id: n.source_id,
                created_at: n.created_at.to_rfc3339(),
                delivered_at: n.delivered_at.map(|t| t.to_rfc3339()),
                viewed_at: n.viewed_at.map(|t| t.to_rfc3339()),
                acted_on_at: n.acted_on_at.map(|t| t.to_rfc3339()),
                dismissed_at: n.dismissed_at.map(|t| t.to_rfc3339()),
                suppressed: n.suppressed,
            },
            "status": "ok"
        }))),
        None => Err(not_found()),
    }
}

pub async fn mark_viewed(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(nudge_id): Path<String>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;

    let existing = queries::get_nudge(&tenant_pool.pool(), &nudge_id, org_id)
        .await
        .map_err(internal_error)?;
    if existing.is_none() {
        return Err(not_found());
    }

    queries::update_nudge_viewed(&tenant_pool.pool(), &nudge_id, org_id)
        .await
        .map_err(internal_error)?;

    Ok(Json(json!({ "status": "updated" })))
}

pub async fn mark_dismissed(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(nudge_id): Path<String>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;

    let existing = queries::get_nudge(&tenant_pool.pool(), &nudge_id, org_id)
        .await
        .map_err(internal_error)?;
    if existing.is_none() {
        return Err(not_found());
    }

    queries::update_nudge_dismissed(&tenant_pool.pool(), &nudge_id, org_id)
        .await
        .map_err(internal_error)?;

    Ok(Json(json!({ "status": "updated" })))
}
