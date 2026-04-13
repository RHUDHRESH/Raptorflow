use axum::{
    extract::{Extension, Path},
    routing::{get, post},
    Json, Router,
};
use serde::{Deserialize, Serialize};
use serde_json::{Value, json};

use crate::middleware::auth::AuthContext;

#[derive(Debug, Deserialize)]
pub struct StartSessionRequest {
    pub campaign_id: String,
    pub agent_roster: Vec<String>,
}

#[derive(Debug, Serialize)]
pub struct SessionResponse {
    pub session_id: String,
    pub status: String,
    pub agent_count: usize,
    pub org_id: String,
}

#[derive(Debug, Serialize)]
pub struct SessionListResponse {
    pub sessions: Vec<SessionSummary>,
}

#[derive(Debug, Serialize)]
pub struct SessionSummary {
    pub session_id: String,
    pub campaign_id: String,
    pub status: String,
    pub created_at: String,
}

pub fn router() -> Router {
    Router::new()
        .route("/", post(start_session))
        .route("/history", get(list_sessions))
        .route("/{session_id}", get(get_session))
        .route("/{session_id}/messages", get(get_session_messages))
}

pub async fn start_session(
    Extension(auth): Extension<AuthContext>,
    Json(req): Json<StartSessionRequest>,
) -> Json<Value> {
    tracing::info!(
        org_id = %auth.tenant.org_id,
        campaign_id = %req.campaign_id,
        agent_count = req.agent_roster.len(),
        "Starting council session"
    );

    Json(json!({
        "status": "accepted",
        "resource": "council.session",
        "session_id": ulid::Ulid::new().to_string(),
        "org_id": auth.tenant.org_id.to_string(),
        "notes": ["roster selection", "streaming", "synthesis"],
    }))
}

pub async fn list_sessions(
    Extension(auth): Extension<AuthContext>,
) -> Json<Value> {
    Json(json!({
        "status": "stub",
        "org_id": auth.tenant.org_id.to_string(),
        "sessions": [],
    }))
}

pub async fn get_session(
    Extension(auth): Extension<AuthContext>,
    Path(session_id): Path<String>,
) -> Json<Value> {
    Json(json!({
        "session_id": session_id,
        "org_id": auth.tenant.org_id.to_string(),
        "status": "active",
        "agents": [],
        "messages": [],
    }))
}

pub async fn get_session_messages(
    Extension(auth): Extension<AuthContext>,
    Path(session_id): Path<String>,
) -> Json<Value> {
    Json(json!({
        "session_id": session_id,
        "org_id": auth.tenant.org_id.to_string(),
        "messages": [],
    }))
}