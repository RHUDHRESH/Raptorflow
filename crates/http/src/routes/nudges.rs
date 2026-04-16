use axum::{extract::Extension, Json};
use serde_json::{Value, json};

use crate::middleware::auth::AuthContext;

pub fn router() -> axum::Router {
    use axum::routing::get;
    axum::Router::new()
        .route("/", get(list_nudges))
}

pub async fn list_nudges(
    Extension(_auth): Extension<AuthContext>,
) -> Json<Value> {
    Json(json!({
        "status": "stub",
        "resource": "nudges",
        "message": "Nudges endpoint - full implementation pending"
    }))
}