use axum::{
    Json, Router,
    extract::{
        Extension, Query,
        ws::{Message, WebSocket, WebSocketUpgrade},
    },
    http::StatusCode,
    routing::get,
};
use futures_util::{SinkExt, StreamExt};
use serde::{Deserialize, Serialize};
use serde_json::{Value, json};
use std::sync::Arc;
use std::sync::LazyLock;
use tokio::sync::broadcast;

use super::events::{EventBus, OfficeEvent};
use crate::middleware::AppState;
use raptorflow_auth::TenantContext;
use raptorflow_db::TenantDbPool;

static EVENT_BUS: LazyLock<Arc<EventBus>> = LazyLock::new(|| Arc::new(EventBus::new()));

fn get_event_bus() -> Arc<EventBus> {
    EVENT_BUS.clone()
}

pub fn router(state: Arc<AppState>) -> Router {
    Router::new()
        .route("/", get(get_office_state))
        .route("/ws", get(ws_office))
        .layer(Extension(state))
}

type AppResult<T> = Result<T, (StatusCode, Json<Value>)>;

fn internal_error<E: std::fmt::Display>(e: E) -> (StatusCode, Json<Value>) {
    tracing::error!("Office route error: {e}");
    (
        StatusCode::INTERNAL_SERVER_ERROR,
        Json(json!({ "error": "office_internal_error" })),
    )
}

#[derive(Debug, Serialize)]
pub struct OfficeStateResponse {
    pub active_campaigns: i64,
    pub active_council_sessions: i64,
    pub open_nudges: i64,
    pub recent_muse_conversations: i64,
    pub event_types: Vec<&'static str>,
}

pub async fn get_office_state(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;
    let pool = tenant_pool.pool();

    let active_campaigns: (i64,) = sqlx::query_as(
        "SELECT COUNT(*)::bigint FROM campaigns WHERE org_id = $1 AND status IN ('active', 'draft')",
    )
    .bind(org_id)
    .fetch_one(pool)
    .await
    .map_err(internal_error)?;

    let active_sessions: (i64,) = sqlx::query_as(
        "SELECT COUNT(*)::bigint FROM council_sessions WHERE org_id = $1 AND status = 'active'",
    )
    .bind(org_id)
    .fetch_one(pool)
    .await
    .map_err(internal_error)?;

    let open_nudges: (i64,) = sqlx::query_as(
        "SELECT COUNT(*)::bigint FROM nudges WHERE org_id = $1 AND suppressed = false AND dismissed_at IS NULL",
    )
    .bind(org_id)
    .fetch_one(pool)
    .await
    .map_err(internal_error)?;

    let recent_convs: (i64,) = sqlx::query_as(
        "SELECT COUNT(*)::bigint FROM muse_conversations WHERE org_id = $1 AND created_at > now() - interval '7 days'",
    )
    .bind(org_id)
    .fetch_one(pool)
    .await
    .map_err(internal_error)?;

    Ok(Json(json!({
        "active_campaigns": active_campaigns.0,
        "active_council_sessions": active_sessions.0,
        "open_nudges": open_nudges.0,
        "recent_muse_conversations": recent_convs.0,
        "event_types": super::events::OFFICE_EVENT_TYPES,
        "status": "ok"
    })))
}

#[derive(Deserialize)]
pub struct WsQuery {
    token: String,
}

pub async fn ws_office(
    Extension(state): Extension<Arc<AppState>>,
    Query(query): Query<WsQuery>,
    ws: WebSocketUpgrade,
) -> AppResult<axum::response::Response> {
    let token = &query.token;

    let claims = match state.auth_validator.validate(token).await {
        Ok(c) => c,
        Err(_) => {
            return Err((
                StatusCode::UNAUTHORIZED,
                Json(json!({ "error": "invalid_token" })),
            ));
        }
    };

    let org_id = claims.org_id.map(|id| id.to_string()).unwrap_or_default();

    let response = ws.on_upgrade(move |socket| handle_socket(socket, org_id));

    Ok(response.into())
}

async fn handle_socket(socket: WebSocket, org_id: String) {
    let event_bus = get_event_bus();
    let mut event_rx: broadcast::Receiver<OfficeEvent> = match event_bus.get_receiver(&org_id).await
    {
        Some(rx) => rx,
        None => {
            return;
        }
    };

    let (mut sender, mut receiver) = socket.split();

    loop {
        tokio::select! {
            result = receiver.next() => {
                match result {
                    Some(Ok(Message::Ping(data))) => {
                        if sender.send(Message::Pong(data)).await.is_err() {
                            break;
                        }
                    }
                    Some(Ok(Message::Close(_))) | Some(Err(_)) | None => {
                        break;
                    }
                    _ => {}
                }
            }
            result = event_rx.recv() => {
                match result {
                    Ok(event) => {
                        let msg = Message::Text(serde_json::to_string(&event).unwrap_or_default().into());
                        if sender.send(msg).await.is_err() {
                            break;
                        }
                    }
                    Err(_) => break,
                }
            }
        }
    }
}

pub fn emit_office_event(event_type: &str, org_id: uuid::Uuid, payload: serde_json::Value) {
    let event = OfficeEvent {
        event_type: event_type.to_string(),
        org_id: org_id.to_string(),
        payload,
        timestamp: chrono::Utc::now().to_rfc3339(),
    };
    get_event_bus().publish_sync(event);
}
