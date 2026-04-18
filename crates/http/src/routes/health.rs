use axum::{Json, extract::Extension, http::StatusCode, response::IntoResponse};
use std::sync::Arc;

use crate::middleware::AppState;

pub async fn liveness() -> StatusCode {
    StatusCode::OK
}

pub async fn readiness(Extension(state): Extension<Arc<AppState>>) -> impl IntoResponse {
    let mut checks = serde_json::json!({
        "status": "ready",
        "checks": {}
    });

    if let Some(ref pool) = state.db_pool {
        match sqlx::query("SELECT 1").fetch_one(pool.as_ref()).await {
            Ok(_) => {
                checks["checks"]["database"] = serde_json::json!({"status": "ok"});
            }
            Err(e) => {
                checks["status"] = serde_json::json!("degraded");
                checks["checks"]["database"] = serde_json::json!({
                    "status": "error",
                    "message": e.to_string()
                });
            }
        }
    } else {
        checks["status"] = serde_json::json!("degraded");
        checks["checks"]["database"] = serde_json::json!({"status": "not_configured"});
    }

    if let Some(ref cache) = state.cache_service {
        match cache.ping().await {
            Ok(_) => {
                checks["checks"]["cache"] = serde_json::json!({"status": "ok"});
            }
            Err(e) => {
                checks["status"] = serde_json::json!("degraded");
                checks["checks"]["cache"] = serde_json::json!({
                    "status": "error",
                    "message": e.to_string()
                });
            }
        }
    } else {
        checks["status"] = serde_json::json!("degraded");
        checks["checks"]["cache"] = serde_json::json!({"status": "not_configured"});
    }

    if checks["status"] == "ready" {
        (StatusCode::OK, Json(checks)).into_response()
    } else {
        (StatusCode::SERVICE_UNAVAILABLE, Json(checks)).into_response()
    }
}
