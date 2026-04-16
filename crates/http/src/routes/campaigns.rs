use axum::{extract::Extension, Json};
use serde_json::{Value, json};

use crate::middleware::auth::AuthContext;

pub fn router() -> axum::Router {
    use axum::routing::{get, post};
    axum::Router::new()
        .route("/", get(list_campaigns).post(create_campaign))
        .route("/replanning", post(trigger_replanning))
}

pub async fn list_campaigns(
    Extension(_auth): Extension<AuthContext>,
) -> Json<Value> {
    Json(json!({
        "status": "stub",
        "resource": "campaigns",
        "message": "Campaigns endpoint - full implementation pending"
    }))
}

pub async fn create_campaign(
    Extension(_auth): Extension<AuthContext>,
) -> Json<Value> {
    Json(json!({
        "status": "accepted",
        "resource": "campaign.create"
    }))
}

pub async fn trigger_replanning(
    Extension(_auth): Extension<AuthContext>,
) -> Json<Value> {
    Json(json!({
        "status": "accepted",
        "resource": "campaign.replanning"
    }))
}