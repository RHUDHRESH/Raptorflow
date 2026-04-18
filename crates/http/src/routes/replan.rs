use axum::{
    extract::{Extension, Path},
    http::StatusCode,
    Json,
};
use serde::{Deserialize, Serialize};
use serde_json::{Value, json};
use ulid::Ulid;

use raptorflow_auth::TenantContext;
use raptorflow_db::{queries, TenantDbPool};
use raptorflow_db::models::ReplanSession;
use crate::routes::office::handlers::emit_office_event;

type AppResult<T> = Result<T, (StatusCode, Json<Value>)>;

fn internal_error<E: std::fmt::Display>(e: E) -> (StatusCode, Json<Value>) {
    tracing::error!("Replan route error: {e}");
    (
        StatusCode::INTERNAL_SERVER_ERROR,
        Json(json!({ "error": "replan_internal_error" })),
    )
}

fn bad_request(msg: &str) -> (StatusCode, Json<Value>) {
    (StatusCode::BAD_REQUEST, Json(json!({ "error": msg })))
}

fn not_found() -> (StatusCode, Json<Value>) {
    (StatusCode::NOT_FOUND, Json(json!({ "error": "replan_not_found" })))
}

#[derive(Debug, Deserialize)]
pub struct TriggerReplanRequest {
    pub trigger_type: String,
}

#[derive(Debug, Serialize)]
pub struct ReplanResponse {
    pub replan_session_id: String,
    pub campaign_id: String,
    pub trigger_type: String,
    pub status: String,
    pub created_at: String,
}

impl From<ReplanSession> for ReplanResponse {
    fn from(r: ReplanSession) -> Self {
        Self {
            replan_session_id: r.replan_session_id,
            campaign_id: r.campaign_id,
            trigger_type: r.trigger_type,
            status: r.status,
            created_at: r.created_at.to_rfc3339(),
        }
    }
}

pub async fn trigger_replan(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(campaign_id): Path<String>,
    Json(req): Json<TriggerReplanRequest>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;

    if req.trigger_type.trim().is_empty() {
        return Err(bad_request("trigger_type_required"));
    }

    let valid_triggers = ["manual", "automatic", "milestone", "performance"];
    if !valid_triggers.contains(&req.trigger_type.as_str()) {
        return Err(bad_request("invalid_trigger_type"));
    }

    let existing = queries::get_campaign(&tenant_pool.pool(), &campaign_id, org_id)
        .await
        .map_err(internal_error)?;
    if existing.is_none() {
        return Err(not_found());
    }

    let replan_session_id = Ulid::new().to_string();

    queries::create_replan_session(
        &tenant_pool.pool(),
        &replan_session_id,
        org_id,
        &campaign_id,
        &req.trigger_type,
    )
    .await
    .map_err(internal_error)?;

    let session = queries::get_replan_session(&tenant_pool.pool(), &replan_session_id, org_id)
        .await
        .map_err(internal_error)?;

    match session {
        Some(s) => {
            emit_office_event("replan_triggered", org_id, json!({"campaign_id": campaign_id, "replan_session_id": &s.replan_session_id, "trigger_type": &s.trigger_type}));
            Ok(Json(json!({
                "replan": ReplanResponse::from(s),
                "status": "created"
            })))
        }
        None => Err(internal_error("replan_not_found_after_create")),
    }
}

pub async fn list_replans(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(campaign_id): Path<String>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;

    let existing = queries::get_campaign(&tenant_pool.pool(), &campaign_id, org_id)
        .await
        .map_err(internal_error)?;
    if existing.is_none() {
        return Err(not_found());
    }

    let sessions = queries::list_replan_sessions(&tenant_pool.pool(), &campaign_id, org_id)
        .await
        .map_err(internal_error)?;

    let list: Vec<ReplanResponse> = sessions.into_iter().map(Into::into).collect();

    Ok(Json(json!({
        "replans": list,
        "total": list.len(),
        "status": "ok"
    })))
}