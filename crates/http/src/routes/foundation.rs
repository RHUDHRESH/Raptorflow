use axum::{
    extract::{Extension, Path},
    Json,
};
use serde::{Deserialize, Serialize};
use uuid::Uuid;

use crate::middleware::auth::AuthContext;

#[derive(Debug, Serialize, Deserialize)]
pub struct FoundationResponse {
    pub id: String,
    pub org_id: Uuid,
    pub version: i32,
    pub sections: serde_json::Value,
    pub updated_at: String,
}

#[derive(Debug, Deserialize)]
pub struct UpdateSectionRequest {
    pub data: serde_json::Value,
}

#[derive(Debug, Deserialize)]
pub struct CreateSnapshotRequest {
    pub source: Option<String>,
}

#[derive(Debug, Deserialize)]
pub struct ScanRequest {
    pub mode: String,
}

pub async fn get_foundation(
    Extension(auth): Extension<AuthContext>,
) -> Json<FoundationResponse> {
    Json(FoundationResponse {
        id: "stub".to_string(),
        org_id: auth.tenant.org_id,
        version: 1,
        sections: serde_json::json!({}),
        updated_at: chrono::Utc::now().to_rfc3339(),
    })
}

pub async fn create_foundation(
    Extension(auth): Extension<AuthContext>,
    Json(payload): Json<serde_json::Value>,
) -> Json<FoundationResponse> {
    Json(FoundationResponse {
        id: "stub".to_string(),
        org_id: auth.tenant.org_id,
        version: 1,
        sections: payload,
        updated_at: chrono::Utc::now().to_rfc3339(),
    })
}

pub async fn update_section(
    Extension(auth): Extension<AuthContext>,
    Path(section): Path<String>,
    Json(payload): Json<UpdateSectionRequest>,
) -> Json<FoundationResponse> {
    Json(FoundationResponse {
        id: "stub".to_string(),
        org_id: auth.tenant.org_id,
        version: 1,
        sections: serde_json::json!({ section: payload.data }),
        updated_at: chrono::Utc::now().to_rfc3339(),
    })
}

pub async fn list_snapshots(
    Extension(auth): Extension<AuthContext>,
) -> Json<Vec<FoundationResponse>> {
    Json(vec![FoundationResponse {
        id: "stub".to_string(),
        org_id: auth.tenant.org_id,
        version: 1,
        sections: serde_json::json!({}),
        updated_at: chrono::Utc::now().to_rfc3339(),
    }])
}

pub async fn create_snapshot(
    Extension(auth): Extension<AuthContext>,
    Json(_payload): Json<CreateSnapshotRequest>,
) -> Json<FoundationResponse> {
    Json(FoundationResponse {
        id: "stub".to_string(),
        org_id: auth.tenant.org_id,
        version: 1,
        sections: serde_json::json!({}),
        updated_at: chrono::Utc::now().to_rfc3339(),
    })
}

pub async fn restore_snapshot(
    Extension(auth): Extension<AuthContext>,
    Path(_id): Path<String>,
) -> Json<FoundationResponse> {
    Json(FoundationResponse {
        id: "stub".to_string(),
        org_id: auth.tenant.org_id,
        version: 2,
        sections: serde_json::json!({}),
        updated_at: chrono::Utc::now().to_rfc3339(),
    })
}

pub async fn get_snapshot(
    Extension(auth): Extension<AuthContext>,
    Path(_id): Path<String>,
) -> Json<FoundationResponse> {
    Json(FoundationResponse {
        id: "stub".to_string(),
        org_id: auth.tenant.org_id,
        version: 1,
        sections: serde_json::json!({}),
        updated_at: chrono::Utc::now().to_rfc3339(),
    })
}

#[derive(Debug, Serialize)]
pub struct ScanResponse {
    pub job_id: String,
    pub status: String,
}

pub async fn trigger_scan(
    Extension(_auth): Extension<AuthContext>,
    Json(_payload): Json<ScanRequest>,
) -> Json<ScanResponse> {
    Json(ScanResponse {
        job_id: format!("scan-{}", Uuid::new_v4()),
        status: "pending".to_string(),
    })
}

pub async fn get_scan_status(
    Extension(_auth): Extension<AuthContext>,
    Path(_job_id): Path<String>,
) -> Json<ScanResponse> {
    Json(ScanResponse {
        job_id: "stub".to_string(),
        status: "running".to_string(),
    })
}
