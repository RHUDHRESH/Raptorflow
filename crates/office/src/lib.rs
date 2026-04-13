//! Office canvas coordination stubs for RaptorFlow.
//!
//! The "Office Canvas" is the real-time collaborative workspace visualised
//! with PixiJS. This crate defines the event catalog that drives avatar
//! movement and UI updates in the office.
//!
//! ## Current status
//!
//! [`OFFICE_EVENT_TYPES`] catalog (29 event types) is defined. The WebSocket
//! transport and DragonflyDB pub/sub for real-time event broadcasting are
//! not yet implemented.
//!
//! ## Event catalog
//!
//! Covers the full campaign lifecycle: file delivery, brief reading, agent walks,
//! council debates, synthesis presenting, snark speech bubbles, task
//! notifications, and intel alerts. See [`office_event_catalog()`].
//!
//! ## Routes (stub)
//!
//! - `GET /` — office metadata + event catalog (stub)

use axum::{Json, Router, routing::get};
use serde_json::{Value, json};

pub const OFFICE_EVENT_TYPES: &[&str] = &[
    "file_delivery_start",
    "file_delivered_to_maya",
    "file_delivered_to_strategist",
    "brief_reading",
    "brief_accepted",
    "brief_clarification_needed",
    "pager_notification",
    "agent_walk_start",
    "agent_seated_conference",
    "debate_agent_speaking",
    "debate_agent_reacting",
    "synthesis_presenting",
    "conference_break",
    "move_completed_celebration",
    "task_missed_notification",
    "intel_alert_received",
    "morning_meeting_start",
    "speech_bubble",
    "agent_working",
    "council_pager",
    "council_walk",
    "council_debate",
    "council_synthesis",
    "snark_refresh",
    "campaign_task_ready",
    "file_delivery_complete",
];

pub fn router() -> Router {
    Router::new().route("/", get(office_metadata))
}

pub fn office_event_catalog() -> &'static [&'static str] {
    OFFICE_EVENT_TYPES
}

async fn office_metadata() -> Json<Value> {
    Json(json!({
        "status": "stub",
        "resource": "office",
        "event_types": OFFICE_EVENT_TYPES,
    }))
}
