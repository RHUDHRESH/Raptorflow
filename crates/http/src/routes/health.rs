use axum::{Json, extract::Extension, http::StatusCode, response::IntoResponse};
use serde::Serialize;
use std::sync::Arc;

use crate::middleware::AppState;

#[derive(Serialize)]
pub struct HealthResponse {
    pub status: &'static str,
    pub version: &'static str,
    pub db: &'static str,
}

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

    if checks["status"] == "ready" {
        (StatusCode::OK, Json(checks)).into_response()
    } else {
        (StatusCode::SERVICE_UNAVAILABLE, Json(checks)).into_response()
    }
}

pub async fn api_health(
    Extension(state): Extension<Arc<AppState>>,
) -> Json<HealthResponse> {
    let db_ok = match &state.db_pool {
        Some(pool) => sqlx::query("SELECT 1").fetch_one(pool.as_ref()).await.is_ok(),
        None => false,
    };

    Json(HealthResponse {
        status: if db_ok { "ok" } else { "degraded" },
        version: env!("CARGO_PKG_VERSION"),
        db: if db_ok { "ok" } else { "unreachable" },
    })
}
