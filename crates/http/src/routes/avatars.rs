use axum::{
    Json, Router,
    extract::{Extension, Path},
    http::StatusCode,
    routing::{get, post},
};
use serde::{Deserialize, Serialize};
use serde_json::{Value, json};
use std::sync::Arc;

use crate::middleware::AppState;
use raptorflow_auth::TenantContext;
use raptorflow_db::TenantDbPool;
use raptorflow_db::queries as db;

type AppResult<T> = Result<T, (StatusCode, Json<Value>)>;

fn internal_error<E: std::fmt::Display>(e: E) -> (StatusCode, Json<Value>) {
    tracing::error!("Avatar route error: {e}");
    (
        StatusCode::INTERNAL_SERVER_ERROR,
        Json(json!({ "error": "avatar_internal_error" })),
    )
}

fn bad_request<E: std::fmt::Display>(e: E) -> (StatusCode, Json<Value>) {
    (
        StatusCode::BAD_REQUEST,
        Json(json!({ "error": e.to_string() })),
    )
}

fn not_found(msg: &str) -> (StatusCode, Json<Value>) {
    (StatusCode::NOT_FOUND, Json(json!({ "error": msg })))
}

fn conflict(msg: &str) -> (StatusCode, Json<Value>) {
    (StatusCode::CONFLICT, Json(json!({ "error": msg })))
}

#[derive(Debug, Serialize)]
pub struct AvatarResponse {
    pub avatar_id: String,
    pub avatar_key: String,
    pub display_name: String,
    pub role: String,
    pub archetype: String,
    pub personality: Value,
    pub system_prompt: String,
    pub tool_permissions: Value,
    pub memory_scope: String,
    pub is_active: bool,
    pub created_at: String,
    pub updated_at: String,
}

impl From<raptorflow_db::models::Avatar> for AvatarResponse {
    fn from(a: raptorflow_db::models::Avatar) -> Self {
        Self {
            avatar_id: a.avatar_id,
            avatar_key: a.avatar_key,
            display_name: a.display_name,
            role: a.role,
            archetype: a.archetype,
            personality: a.personality,
            system_prompt: a.system_prompt,
            tool_permissions: a.tool_permissions,
            memory_scope: a.memory_scope,
            is_active: a.is_active,
            created_at: a.created_at.to_rfc3339(),
            updated_at: a.updated_at.to_rfc3339(),
        }
    }
}

#[derive(Debug, Deserialize)]
pub struct CreateAvatarRequest {
    pub avatar_key: String,
    pub display_name: String,
    pub role: String,
    pub archetype: String,
    #[serde(default = "default_personality")]
    pub personality: Value,
    #[serde(default)]
    pub system_prompt: String,
    #[serde(default = "default_tool_permissions")]
    pub tool_permissions: Value,
    #[serde(default = "default_memory_scope")]
    pub memory_scope: String,
}

fn default_personality() -> Value {
    json!({
        "tone": "direct",
        "risk_tolerance": "medium",
        "creativity": 0.7,
        "skepticism": 0.6,
        "detail_level": "high"
    })
}

fn default_tool_permissions() -> Value {
    json!({
        "can_use_bedrock": true,
        "can_read_foundation": true,
        "can_read_intel": true,
        "can_write_artifacts": false,
        "can_trigger_jobs": false,
        "requires_approval_for_external_actions": true
    })
}

fn default_memory_scope() -> String {
    "org".to_string()
}

#[derive(Debug, Deserialize)]
pub struct UpdateAvatarRequest {
    pub display_name: Option<String>,
    pub personality: Option<Value>,
    pub system_prompt: Option<String>,
    pub tool_permissions: Option<Value>,
    pub is_active: Option<bool>,
}

pub fn router(state: Arc<AppState>) -> Router {
    Router::new()
        .route("/", get(list_avatars).post(create_avatar))
        .route("/defaults", post(ensure_defaults))
        .route(
            "/{id}",
            get(get_avatar).patch(update_avatar).delete(delete_avatar),
        )
        .layer(Extension(state))
}

pub async fn list_avatars(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;
    let pool = tenant_pool.pool();

    let avatars = db::list_avatars(pool, org_id)
        .await
        .map_err(internal_error)?;

    let response: Vec<AvatarResponse> = avatars.into_iter().map(AvatarResponse::from).collect();
    Ok(Json(json!({ "avatars": response })))
}

pub async fn get_avatar(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(avatar_id): Path<String>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;
    let pool = tenant_pool.pool();

    let avatar = db::get_avatar(pool, org_id, &avatar_id)
        .await
        .map_err(internal_error)?
        .ok_or_else(|| not_found("avatar_not_found"))?;

    Ok(Json(json!({ "avatar": AvatarResponse::from(avatar) })))
}

pub async fn create_avatar(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Json(body): Json<CreateAvatarRequest>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;
    let pool = tenant_pool.pool();

    if body.avatar_key.is_empty() {
        return Err(bad_request("avatar_key is required"));
    }
    if body.display_name.is_empty() {
        return Err(bad_request("display_name is required"));
    }

    let avatar_id = uuid::Uuid::new_v4().to_string();

    let existing = db::get_avatar_by_key(pool, org_id, &body.avatar_key)
        .await
        .map_err(internal_error)?;
    if existing.is_some() {
        return Err(conflict("avatar_key already exists"));
    }

    db::create_avatar(
        pool,
        &avatar_id,
        org_id,
        &body.avatar_key,
        &body.display_name,
        &body.role,
        &body.archetype,
        &body.personality,
        &body.system_prompt,
        &body.tool_permissions,
        &body.memory_scope,
    )
    .await
    .map_err(internal_error)?;

    let avatar = db::get_avatar(pool, org_id, &avatar_id)
        .await
        .map_err(internal_error)?
        .ok_or_else(|| internal_error("avatar not found after create"))?;

    Ok(Json(json!({ "avatar": AvatarResponse::from(avatar) })))
}

pub async fn update_avatar(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(avatar_id): Path<String>,
    Json(body): Json<UpdateAvatarRequest>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;
    let pool = tenant_pool.pool();

    db::update_avatar(
        pool,
        org_id,
        &avatar_id,
        body.display_name.as_deref(),
        body.personality.as_ref(),
        body.system_prompt.as_deref(),
        body.tool_permissions.as_ref(),
        body.is_active,
    )
    .await
    .map_err(internal_error)?;

    let avatar = db::get_avatar(pool, org_id, &avatar_id)
        .await
        .map_err(internal_error)?
        .ok_or_else(|| not_found("avatar_not_found"))?;

    Ok(Json(json!({ "avatar": AvatarResponse::from(avatar) })))
}

pub async fn delete_avatar(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(avatar_id): Path<String>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;
    let pool = tenant_pool.pool();

    db::soft_delete_avatar(pool, org_id, &avatar_id)
        .await
        .map_err(internal_error)?;

    Ok(Json(json!({ "deleted": true, "avatar_id": avatar_id })))
}

pub async fn ensure_defaults(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;
    let pool = tenant_pool.pool();

    let avatars = db::ensure_default_avatars(pool, org_id)
        .await
        .map_err(internal_error)?;

    let response: Vec<AvatarResponse> = avatars.into_iter().map(AvatarResponse::from).collect();
    Ok(Json(json!({ "avatars": response })))
}
