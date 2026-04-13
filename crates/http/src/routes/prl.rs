use axum::{
    extract::{Extension, Path, Query},
    http::StatusCode,
    Json,
};
use serde::{Deserialize, Serialize};
use uuid::Uuid;

use crate::middleware::auth::AuthContext;

#[derive(Debug, Serialize, Deserialize)]
pub struct RippleResponse {
    pub id: String,
    pub org_id: Uuid,
    pub title: String,
    pub description: Option<String>,
    pub status: String,
    pub category: Option<String>,
    pub salience: f64,
    pub confidence: f64,
    pub created_at: String,
}

#[derive(Debug, Deserialize)]
pub struct CreateRippleRequest {
    pub title: String,
    pub description: Option<String>,
    pub category: Option<String>,
}

#[derive(Debug, Deserialize)]
pub struct UpdateRippleRequest {
    pub title: Option<String>,
    pub description: Option<String>,
    pub status: Option<String>,
}

#[derive(Debug, Serialize)]
pub struct EdgeResponse {
    pub id: Uuid,
    pub source_ripple_id: String,
    pub target_ripple_id: String,
    pub edge_type: String,
    pub weight: f64,
}

#[derive(Debug, Deserialize)]
pub struct CreateEdgeRequest {
    pub target_ripple_id: String,
    pub relationship: String,
}

#[derive(Debug, Serialize)]
pub struct EssenceResponse {
    pub id: Uuid,
    pub org_id: Uuid,
    pub name: String,
    pub avatar_key: String,
    pub personality: serde_json::Value,
}

#[derive(Debug, Deserialize)]
pub struct CreateEssenceRequest {
    pub name: String,
    pub personality: serde_json::Value,
}

#[derive(Debug, Deserialize)]
pub struct RippleQuery {
    pub status: Option<String>,
}

pub async fn list_ripples(
    Extension(auth): Extension<AuthContext>,
    Query(_query): Query<RippleQuery>,
) -> Json<Vec<RippleResponse>> {
    Json(vec![RippleResponse {
        id: "stub".to_string(),
        org_id: auth.tenant.org_id,
        title: "Sample Ripple".to_string(),
        description: Some("A sample ripple for testing".to_string()),
        status: "active".to_string(),
        category: Some("idea".to_string()),
        salience: 0.7,
        confidence: 0.8,
        created_at: chrono::Utc::now().to_rfc3339(),
    }])
}

pub async fn create_ripple(
    Extension(auth): Extension<AuthContext>,
    Json(payload): Json<CreateRippleRequest>,
) -> Json<RippleResponse> {
    Json(RippleResponse {
        id: format!("ripple-{}", Uuid::new_v4()),
        org_id: auth.tenant.org_id,
        title: payload.title,
        description: payload.description,
        status: "active".to_string(),
        category: payload.category,
        salience: 0.5,
        confidence: 0.7,
        created_at: chrono::Utc::now().to_rfc3339(),
    })
}

pub async fn get_ripple(
    Extension(auth): Extension<AuthContext>,
    Path(_id): Path<String>,
) -> Json<RippleResponse> {
    Json(RippleResponse {
        id: "stub".to_string(),
        org_id: auth.tenant.org_id,
        title: "Sample Ripple".to_string(),
        description: Some("A sample ripple for testing".to_string()),
        status: "active".to_string(),
        category: Some("idea".to_string()),
        salience: 0.7,
        confidence: 0.8,
        created_at: chrono::Utc::now().to_rfc3339(),
    })
}

pub async fn update_ripple(
    Extension(auth): Extension<AuthContext>,
    Path(_id): Path<String>,
    Json(payload): Json<UpdateRippleRequest>,
) -> Json<RippleResponse> {
    Json(RippleResponse {
        id: "stub".to_string(),
        org_id: auth.tenant.org_id,
        title: payload.title.unwrap_or_default(),
        description: payload.description,
        status: payload.status.unwrap_or_else(|| "active".to_string()),
        category: None,
        salience: 0.7,
        confidence: 0.8,
        created_at: chrono::Utc::now().to_rfc3339(),
    })
}

pub async fn delete_ripple(
    Extension(_auth): Extension<AuthContext>,
    Path(_id): Path<String>,
) -> StatusCode {
    StatusCode::NO_CONTENT
}

pub async fn realize_ripple(
    Extension(auth): Extension<AuthContext>,
    Path(_id): Path<String>,
) -> Json<RippleResponse> {
    Json(RippleResponse {
        id: "stub".to_string(),
        org_id: auth.tenant.org_id,
        title: "Realized Ripple".to_string(),
        description: None,
        status: "realized".to_string(),
        category: None,
        salience: 0.9,
        confidence: 0.9,
        created_at: chrono::Utc::now().to_rfc3339(),
    })
}

pub async fn get_ripple_edges(
    Extension(_auth): Extension<AuthContext>,
    Path(_id): Path<String>,
) -> Json<Vec<EdgeResponse>> {
    Json(vec![EdgeResponse {
        id: Uuid::new_v4(),
        source_ripple_id: "stub".to_string(),
        target_ripple_id: "stub".to_string(),
        edge_type: "supports".to_string(),
        weight: 0.5,
    }])
}

pub async fn create_ripple_edge(
    Extension(_auth): Extension<AuthContext>,
    Path(_id): Path<String>,
    Json(payload): Json<CreateEdgeRequest>,
) -> Json<EdgeResponse> {
    Json(EdgeResponse {
        id: Uuid::new_v4(),
        source_ripple_id: "stub".to_string(),
        target_ripple_id: payload.target_ripple_id,
        edge_type: payload.relationship,
        weight: 0.1,
    })
}

pub async fn delete_ripple_edge(
    Extension(_auth): Extension<AuthContext>,
    Path(_edge_id): Path<String>,
) -> StatusCode {
    StatusCode::NO_CONTENT
}

pub async fn list_essences(
    Extension(auth): Extension<AuthContext>,
) -> Json<Vec<EssenceResponse>> {
    Json(vec![EssenceResponse {
        id: Uuid::new_v4(),
        org_id: auth.tenant.org_id,
        name: "Strategist".to_string(),
        avatar_key: "strategist".to_string(),
        personality: serde_json::json!({}),
    }])
}

pub async fn create_essence(
    Extension(auth): Extension<AuthContext>,
    Json(payload): Json<CreateEssenceRequest>,
) -> Json<EssenceResponse> {
    let name = payload.name.clone();
    Json(EssenceResponse {
        id: Uuid::new_v4(),
        org_id: auth.tenant.org_id,
        name,
        avatar_key: payload.name.to_lowercase().replace(' ', "_"),
        personality: payload.personality,
    })
}

pub async fn get_essence(
    Extension(auth): Extension<AuthContext>,
    Path(_id): Path<String>,
) -> Json<EssenceResponse> {
    Json(EssenceResponse {
        id: Uuid::new_v4(),
        org_id: auth.tenant.org_id,
        name: "Strategist".to_string(),
        avatar_key: "strategist".to_string(),
        personality: serde_json::json!({}),
    })
}

pub async fn update_essence(
    Extension(auth): Extension<AuthContext>,
    Path(_id): Path<String>,
    Json(payload): Json<CreateEssenceRequest>,
) -> Json<EssenceResponse> {
    let name = payload.name.clone();
    Json(EssenceResponse {
        id: Uuid::new_v4(),
        org_id: auth.tenant.org_id,
        name,
        avatar_key: payload.name.to_lowercase().replace(' ', "_"),
        personality: payload.personality,
    })
}

#[derive(Debug, Serialize)]
pub struct DecayReport {
    pub ripples_processed: i32,
    pub decayed: i32,
}

pub async fn run_decay(
    Extension(_auth): Extension<AuthContext>,
) -> Json<DecayReport> {
    Json(DecayReport {
        ripples_processed: 10,
        decayed: 2,
    })
}
