use axum::{
    extract::{Extension, Path},
    routing::{get, post},
    Json, Router,
};
use serde::{Deserialize, Serialize};
use serde_json::{Value, json};

use crate::middleware::auth::AuthContext;

#[derive(Debug, Deserialize)]
pub struct SubmitPromptRequest {
    pub prompt: String,
    pub route: Option<String>,
}

#[derive(Debug, Serialize)]
pub struct PromptResponse {
    pub conversation_id: String,
    pub message_id: String,
    pub status: String,
}

#[derive(Debug, Serialize)]
pub struct ConversationListResponse {
    pub conversations: Vec<ConversationSummary>,
}

#[derive(Debug, Serialize)]
pub struct ConversationSummary {
    pub conversation_id: String,
    pub last_message: String,
    pub updated_at: String,
}

pub fn router() -> Router {
    Router::new()
        .route("/", post(submit_prompt))
        .route("/history", get(list_conversations))
        .route("/{conversation_id}", get(get_conversation))
        .route("/{conversation_id}/messages", get(get_messages))
}

pub async fn submit_prompt(
    Extension(auth): Extension<AuthContext>,
    Json(req): Json<SubmitPromptRequest>,
) -> Json<Value> {
    tracing::info!(
        org_id = %auth.tenant.org_id,
        prompt_length = req.prompt.len(),
        route = req.route,
        "Muse prompt submitted"
    );

    let conversation_id = ulid::Ulid::new().to_string();
    let message_id = ulid::Ulid::new().to_string();

    Json(json!({
        "status": "accepted",
        "resource": "muse.prompt",
        "conversation_id": conversation_id,
        "message_id": message_id,
        "org_id": auth.tenant.org_id.to_string(),
        "routes": ["strategic", "content", "tactical", "foundation_update"],
    }))
}

pub async fn list_conversations(
    Extension(auth): Extension<AuthContext>,
) -> Json<Value> {
    Json(json!({
        "status": "stub",
        "org_id": auth.tenant.org_id.to_string(),
        "conversations": [],
    }))
}

pub async fn get_conversation(
    Extension(auth): Extension<AuthContext>,
    Path(conversation_id): Path<String>,
) -> Json<Value> {
    Json(json!({
        "conversation_id": conversation_id,
        "org_id": auth.tenant.org_id.to_string(),
        "messages": [],
        "status": "active",
    }))
}

pub async fn get_messages(
    Extension(auth): Extension<AuthContext>,
    Path(conversation_id): Path<String>,
) -> Json<Value> {
    Json(json!({
        "conversation_id": conversation_id,
        "org_id": auth.tenant.org_id.to_string(),
        "messages": [],
    }))
}