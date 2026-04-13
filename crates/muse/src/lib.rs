//! Conversational AI (Muse) stubs for RaptorFlow.
//!
//! ## Current status
//!
//! This crate is a scaffold. Muse routes prompts to different AI tiers
//! (strategic, content, tactical, foundation_update) but routing logic
//! is not yet implemented.
//!
//! ## Routes (stub)
//!
//! - `POST /` — submit prompt (returns `accepted`)
//! - `GET /history` — list conversations (stub: empty array)
//!
//! ## When implementing
//!
//! Wire to `muse_conversations`, `muse_messages` tables. Use
//! `GcpInferenceService` for AI calls. Muse is the conversational interface
//! that sits alongside the council — it routes user prompts to the
//! appropriate avatar tier.

use axum::{
    Json, Router,
    routing::{get, post},
};
use serde_json::{Value, json};

pub fn router() -> Router {
    Router::new()
        .route("/", post(submit_prompt))
        .route("/history", get(list_conversations))
}

async fn submit_prompt() -> Json<Value> {
    Json(json!({
        "status": "accepted",
        "resource": "muse.prompt",
        "routes": ["strategic", "content", "tactical", "foundation_update"],
    }))
}

async fn list_conversations() -> Json<Value> {
    Json(json!({
        "status": "stub",
        "conversations": [],
    }))
}
