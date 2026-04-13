//! Multi-agent council session stubs for RaptorFlow.
//!
//! ## Current status
//!
//! This crate is a scaffold — router and handlers exist but all return stub
//! responses. The multi-agent debate/orchestration logic is not yet implemented.
//!
//! ## Routes (stub)
//!
//! - `POST /` — start council session (returns `accepted`)
//! - `GET /history` — list past sessions (returns empty array)
//!
//! ## When implementing
//!
//! Wire to `council_sessions`, `council_agent_positions`, `council_messages` tables.
//! Use `harness::SessionManager` for session lifecycle and `eel::enrich_context`
//! for per-avatar context stamping.

use axum::{
    Json, Router,
    routing::{get, post},
};
use serde_json::{Value, json};

pub fn router() -> Router {
    Router::new()
        .route("/", post(start_session))
        .route("/history", get(list_sessions))
}

async fn start_session() -> Json<Value> {
    Json(json!({
        "status": "accepted",
        "resource": "council.session",
        "notes": ["roster selection", "streaming", "synthesis"],
    }))
}

async fn list_sessions() -> Json<Value> {
    Json(json!({
        "status": "stub",
        "sessions": [],
    }))
}
