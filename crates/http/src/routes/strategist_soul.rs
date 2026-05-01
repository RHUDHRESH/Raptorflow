use axum::{Json, Router, extract::Extension, routing::post};
use serde::{Deserialize, Serialize};
use serde_json::{Value, json};
use std::sync::Arc;

use crate::error::{AppResult, bad_request, internal_route_error};
use crate::middleware::AppState;
use raptorflow_auth::TenantContext;
use raptorflow_db::TenantDbPool;

#[derive(Debug, Deserialize)]
pub struct StrategistDryRunRequest {
    pub task_summary: String,
    pub context_summary: String,
}

#[derive(Debug, Serialize)]
pub struct StrategistSoulResponse {
    pub avatar_id: String,
    pub soul_id: String,
    pub created: bool,
    pub updated: bool,
}

#[derive(Debug, Serialize)]
pub struct StrategistDryRunResponse {
    pub avatar_id: String,
    pub soul_id: String,
    pub embodiment_pack: raptorflow_harness::avatar_soul::AvatarEmbodimentPack,
    pub role_lock_prompt: String,
    pub instinct_frame: raptorflow_harness::avatar_soul::DerivedInstinctFrame,
    pub presence_state: Option<StrategistPresenceResponse>,
    pub debate_event: Option<StrategistDebateEventResponse>,
}

#[derive(Debug, Serialize)]
pub struct StrategistPresenceResponse {
    pub presence_id: String,
    pub state: String,
    pub current_focus: String,
    pub current_concern: String,
    pub visible_summary: String,
    pub confidence: f64,
}

#[derive(Debug, Serialize)]
pub struct StrategistDebateEventResponse {
    pub debate_event_id: String,
    pub event_type: String,
    pub stance: String,
    pub content: Value,
    pub confidence: f64,
}

pub fn router(state: Arc<AppState>) -> Router {
    Router::new()
        .route(
            "/api/v1/avatars/strategist/default",
            post(ensure_strategist_default),
        )
        .route(
            "/api/v1/avatars/strategist/dry-run",
            post(run_strategist_dry_run),
        )
        .layer(Extension(state))
}

pub async fn ensure_strategist_default(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;
    let pool = tenant_pool.pool();

    let result = raptorflow_harness::strategist_soul::ensure_strategist_soul(pool, org_id)
        .await
        .map_err(|e| {
            internal_route_error(
                "StrategistSoul route error",
                "strategist_soul_internal_error",
                e,
            )
        })?;

    Ok(Json(json!({
        "avatar_id": result.avatar_id,
        "soul_id": result.soul_id,
        "created": result.created,
        "updated": result.updated
    })))
}

pub async fn run_strategist_dry_run(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Json(body): Json<StrategistDryRunRequest>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;
    let pool = tenant_pool.pool();

    if body.task_summary.is_empty() {
        return Err(bad_request("task_summary is required"));
    }

    if body.context_summary.is_empty() {
        return Err(bad_request("context_summary is required"));
    }

    let input = raptorflow_harness::strategist_soul::StrategistDryRunInput {
        task_summary: body.task_summary,
        context_summary: body.context_summary,
    };

    let result = raptorflow_harness::strategist_soul::run_strategist_dry_run(pool, org_id, input)
        .await
        .map_err(|e| {
            internal_route_error(
                "StrategistSoul route error",
                "strategist_soul_internal_error",
                e,
            )
        })?;

    let presence_state = result.presence_state.map(|p| StrategistPresenceResponse {
        presence_id: p.presence_id,
        state: p.state,
        current_focus: p.current_focus,
        current_concern: p.current_concern,
        visible_summary: p.visible_summary,
        confidence: p.confidence,
    });

    let debate_event = result.debate_event.map(|e| StrategistDebateEventResponse {
        debate_event_id: e.debate_event_id,
        event_type: e.event_type,
        stance: e.stance,
        content: e.content,
        confidence: e.confidence,
    });

    Ok(Json(json!({
        "avatar_id": result.avatar_id,
        "soul_id": result.soul_id,
        "embodiment_pack": result.embodiment_pack,
        "role_lock_prompt": result.role_lock_prompt,
        "instinct_frame": result.instinct_frame,
        "presence_state": presence_state,
        "debate_event": debate_event
    })))
}
