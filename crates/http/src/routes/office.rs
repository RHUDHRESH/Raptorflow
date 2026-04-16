use axum::{extract::Extension, Json};
use serde_json::{Value, json};

use crate::middleware::auth::AuthContext;

pub fn router() -> axum::Router {
    use axum::routing::get;
    axum::Router::new()
        .route("/", get(office_metadata))
}

pub async fn office_metadata(
    Extension(_auth): Extension<AuthContext>,
) -> Json<Value> {
    Json(json!({
        "status": "stub",
        "resource": "office",
        "event_types": [
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
            "file_delivery_complete"
        ]
    }))
}