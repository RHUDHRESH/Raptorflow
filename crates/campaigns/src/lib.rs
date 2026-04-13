//! Campaign management stubs for RaptorFlow.
//!
//! ## Current status
//!
//! This crate is a scaffold — router and handlers exist but all return stub
//! responses. Full campaign orchestration (create, move tracking, task
//! hierarchy, replanning) is not yet implemented.
//!
//! ## Routes (stub)
//!
//! - `GET /` — list campaigns (stub)
//! - `POST /` — create campaign (returns `accepted`)
//! - `POST /replanning` — trigger replanning (returns `accepted`)
//!
//! ## When implementing
//!
//! Wire to `campaigns`, `campaign_moves`, `campaign_tasks` tables in DB.
//! See `database/migrations/0003_campaigns.sql` for the schema.

use axum::{
    Json, Router,
    routing::{get, post},
};
use serde_json::{Value, json};

pub fn router() -> Router {
    Router::new()
        .route("/", get(list_campaigns).post(create_campaign))
        .route("/replanning", post(trigger_replanning))
}

async fn list_campaigns() -> Json<Value> {
    Json(json!({
        "status": "stub",
        "resource": "campaigns",
        "includes": ["moves", "tasks", "generated_content"],
    }))
}

async fn create_campaign() -> Json<Value> {
    Json(json!({
        "status": "accepted",
        "resource": "campaign.create",
    }))
}

async fn trigger_replanning() -> Json<Value> {
    Json(json!({
        "status": "accepted",
        "resource": "campaign.replanning",
    }))
}
