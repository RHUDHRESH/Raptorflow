use axum::{
    extract::{Extension, Path},
    http::StatusCode,
    Json, Router,
    routing::{get, post},
};
use serde::{Deserialize, Serialize};
use serde_json::{Value, json};
use ulid::Ulid;

use raptorflow_auth::TenantContext;
use raptorflow_db::{queries, TenantDbPool};
use raptorflow_db::models::{CouncilSession, CouncilAgentPosition};

pub fn router() -> Router {
    Router::new()
        .route("/", post(start_session).get(list_sessions))
        .route("/{session_id}", get(get_session))
        .route("/{session_id}/messages", get(get_session_messages))
}

type AppResult<T> = Result<T, (StatusCode, Json<Value>)>;

fn internal_error<E: std::fmt::Display>(e: E) -> (StatusCode, Json<Value>) {
    tracing::error!("Council route error: {e}");
    (
        StatusCode::INTERNAL_SERVER_ERROR,
        Json(json!({ "error": "council_internal_error" })),
    )
}

fn bad_request(msg: &str) -> (StatusCode, Json<Value>) {
    (StatusCode::BAD_REQUEST, Json(json!({ "error": msg })))
}

fn not_found(msg: &str) -> (StatusCode, Json<Value>) {
    (StatusCode::NOT_FOUND, Json(json!({ "error": msg })))
}

#[derive(Debug, Deserialize)]
pub struct StartSessionRequest {
    pub campaign_id: Option<String>,
    pub agent_roster: Vec<String>,
    pub question: String,
    pub session_type: Option<String>,
}

#[derive(Debug, Serialize)]
pub struct SessionResponse {
    pub session_id: String,
    pub org_id: String,
    pub campaign_id: Option<String>,
    pub session_type: String,
    pub status: String,
    pub question: String,
    pub total_cost_usd: f64,
    pub created_at: String,
}

impl From<CouncilSession> for SessionResponse {
    fn from(s: CouncilSession) -> Self {
        Self {
            session_id: s.session_id,
            org_id: s.org_id.to_string(),
            campaign_id: s.campaign_id,
            session_type: s.session_type,
            status: s.status,
            question: s.question,
            total_cost_usd: s.total_cost_usd,
            created_at: s.created_at.to_rfc3339(),
        }
    }
}

#[derive(Debug, Serialize)]
pub struct PositionResponse {
    pub position_id: String,
    pub avatar_key: String,
    pub round_number: i32,
    pub content: String,
    pub extracted_ripple_data: serde_json::Value,
    pub created_at: String,
}

impl From<CouncilAgentPosition> for PositionResponse {
    fn from(p: CouncilAgentPosition) -> Self {
        Self {
            position_id: p.position_id,
            avatar_key: p.avatar_key,
            round_number: p.round_number,
            content: p.content,
            extracted_ripple_data: p.extracted_ripple_data,
            created_at: p.created_at.to_rfc3339(),
        }
    }
}

pub async fn start_session(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Json(req): Json<StartSessionRequest>,
) -> AppResult<Json<Value>> {
    if req.question.trim().is_empty() {
        return Err(bad_request("question_required"));
    }

    let org_id = tenant.org_id;
    let session_id = Ulid::new().to_string();
    let session_type = req.session_type.as_deref().unwrap_or("deliberation");

    queries::create_council_session(
        &tenant_pool.pool(),
        &session_id,
        org_id,
        req.campaign_id.as_deref(),
        session_type,
        &req.question,
    )
    .await
    .map_err(internal_error)?;

    let session = queries::get_council_session(&tenant_pool.pool(), &session_id, org_id)
        .await
        .map_err(internal_error)?;

    match session {
        Some(s) => Ok(Json(json!({
            "session": SessionResponse::from(s),
            "status": "created"
        }))),
        None => Err(internal_error("session_not_found_after_create")),
    }
}

pub async fn list_sessions(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;

    let sessions = queries::list_council_sessions(&tenant_pool.pool(), org_id)
        .await
        .map_err(internal_error)?;

    let list: Vec<SessionResponse> = sessions.into_iter().map(Into::into).collect();

    Ok(Json(json!({
        "sessions": list,
        "total": list.len(),
        "status": "ok"
    })))
}

pub async fn get_session(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(session_id): Path<String>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;

    let session = queries::get_council_session(&tenant_pool.pool(), &session_id, org_id)
        .await
        .map_err(internal_error)?;

    match session {
        Some(s) => {
            let positions = queries::list_agent_positions(&tenant_pool.pool(), &session_id, org_id)
                .await
                .map_err(internal_error)?;

            Ok(Json(json!({
                "session": SessionResponse::from(s),
                "positions": positions.into_iter().map(Into::into).collect::<Vec<PositionResponse>>(),
                "status": "ok"
            })))
        }
        None => Err(not_found("session_not_found")),
    }
}

pub async fn get_session_messages(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(session_id): Path<String>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;

    let session = queries::get_council_session(&tenant_pool.pool(), &session_id, org_id)
        .await
        .map_err(internal_error)?;

    if session.is_none() {
        return Err(not_found("session_not_found"));
    }

    let positions = queries::list_agent_positions(&tenant_pool.pool(), &session_id, org_id)
        .await
        .map_err(internal_error)?;

    Ok(Json(json!({
        "session_id": session_id,
        "positions": positions.into_iter().map(Into::into).collect::<Vec<PositionResponse>>(),
        "status": "ok"
    })))
}
