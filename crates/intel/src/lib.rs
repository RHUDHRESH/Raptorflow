//! Competitor intelligence stubs for RaptorFlow.
//!
//! ## Current status
//!
//! This crate is a scaffold. The full intel pipeline (source management,
//! web scraping, embedding ingestion, artifact storage) is not yet implemented.
//!
//! ## Routes (stub)
//!
//! - `GET /` — list intel artifacts (stub)
//!
//! ## When implementing
//!
//! Wire to `intel_sources`, `intel_artifacts`, `intel_observations` tables.
//! See `database/migrations/0006_muse_intel_daily_wins.sql` for the schema.
//! Embeddings should be stored in `intel_artifacts.embeddings` (vector(1536)).

use axum::{Json, Router, routing::get};
use serde_json::{Value, json};

pub fn router() -> Router {
    Router::new().route("/", get(list_artifacts))
}

async fn list_artifacts() -> Json<Value> {
    Json(json!({
        "status": "stub",
        "resource": "intel",
        "feeds": ["website", "social", "ad_library", "serp"],
    }))
}
