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
use raptorflow_db::models::{MuseConversation, MuseMessage};

pub fn router() -> Router {
    Router::new()
        .route("/", post(submit_prompt).get(list_conversations))
        .route("/{conversation_id}", get(get_conversation))
        .route("/{conversation_id}/messages", get(get_messages))
}

type AppResult<T> = Result<T, (StatusCode, Json<Value>)>;

fn internal_error<E: std::fmt::Display>(e: E) -> (StatusCode, Json<Value>) {
    tracing::error!("Muse route error: {e}");
    (
        StatusCode::INTERNAL_SERVER_ERROR,
        Json(json!({ "error": "muse_internal_error" })),
    )
}

fn bad_request(msg: &str) -> (StatusCode, Json<Value>) {
    (StatusCode::BAD_REQUEST, Json(json!({ "error": msg })))
}

fn not_found(msg: &str) -> (StatusCode, Json<Value>) {
    (StatusCode::NOT_FOUND, Json(json!({ "error": msg })))
}

#[derive(Debug, Deserialize)]
pub struct SubmitPromptRequest {
    pub prompt: String,
    pub route: Option<String>,
    pub conversation_id: Option<String>,
}

#[derive(Debug, Serialize)]
pub struct ConversationResponse {
    pub conversation_id: String,
    pub route: String,
    pub created_at: String,
}

impl From<MuseConversation> for ConversationResponse {
    fn from(c: MuseConversation) -> Self {
        Self {
            conversation_id: c.conversation_id,
            route: c.route,
            created_at: c.created_at.to_rfc3339(),
        }
    }
}

#[derive(Debug, Serialize)]
pub struct MessageResponse {
    pub message_id: String,
    pub role: String,
    pub body: String,
    pub created_at: String,
}

impl From<MuseMessage> for MessageResponse {
    fn from(m: MuseMessage) -> Self {
        Self {
            message_id: m.message_id,
            role: m.role,
            body: m.body,
            created_at: m.created_at.to_rfc3339(),
        }
    }
}

pub async fn submit_prompt(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Json(req): Json<SubmitPromptRequest>,
) -> AppResult<Json<Value>> {
    if req.prompt.trim().is_empty() {
        return Err(bad_request("prompt_required"));
    }

    let org_id = tenant.org_id;
    let conversation_id = req.conversation_id.unwrap_or_else(|| Ulid::new().to_string());
    let route = req.route.as_deref().unwrap_or("strategic");
    let user_message_id = Ulid::new().to_string();
    let assistant_message_id = Ulid::new().to_string();

    let existing = queries::get_muse_conversation(&tenant_pool.pool(), &conversation_id, org_id)
        .await
        .map_err(internal_error)?;

    if existing.is_none() {
        queries::create_muse_conversation(&tenant_pool.pool(), &conversation_id, org_id, route)
            .await
            .map_err(internal_error)?;
    }

    queries::create_muse_message(
        &tenant_pool.pool(),
        &user_message_id,
        &conversation_id,
        org_id,
        "user",
        &req.prompt,
    )
    .await
    .map_err(internal_error)?;

    queries::create_muse_message(
        &tenant_pool.pool(),
        &assistant_message_id,
        &conversation_id,
        org_id,
        "assistant",
        "Response generation is asynchronous. Check messages for current state.",
    )
    .await
    .map_err(internal_error)?;

    Ok(Json(json!({
        "conversation_id": conversation_id,
        "message_id": user_message_id,
        "assistant_message_id": assistant_message_id,
        "status": "submitted"
    })))
}

pub async fn list_conversations(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;

    let conversations = queries::list_muse_conversations(&tenant_pool.pool(), org_id)
        .await
        .map_err(internal_error)?;

    let list: Vec<ConversationResponse> = conversations.into_iter().map(Into::into).collect();

    Ok(Json(json!({
        "conversations": list,
        "total": list.len(),
        "status": "ok"
    })))
}

pub async fn get_conversation(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(conversation_id): Path<String>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;

    let conversation = queries::get_muse_conversation(&tenant_pool.pool(), &conversation_id, org_id)
        .await
        .map_err(internal_error)?;

    match conversation {
        Some(c) => {
            let messages = queries::list_muse_messages(&tenant_pool.pool(), &conversation_id, org_id)
                .await
                .map_err(internal_error)?;

            Ok(Json(json!({
                "conversation": ConversationResponse::from(c),
                "messages": messages.into_iter().map(Into::into).collect::<Vec<MessageResponse>>(),
                "status": "ok"
            })))
        }
        None => Err(not_found("conversation_not_found")),
    }
}

pub async fn get_messages(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(conversation_id): Path<String>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;

    let conversation = queries::get_muse_conversation(&tenant_pool.pool(), &conversation_id, org_id)
        .await
        .map_err(internal_error)?;

    if conversation.is_none() {
        return Err(not_found("conversation_not_found"));
    }

    let messages = queries::list_muse_messages(&tenant_pool.pool(), &conversation_id, org_id)
        .await
        .map_err(internal_error)?;

    Ok(Json(json!({
        "conversation_id": conversation_id,
        "messages": messages.into_iter().map(Into::into).collect::<Vec<MessageResponse>>(),
        "status": "ok"
    })))
}
