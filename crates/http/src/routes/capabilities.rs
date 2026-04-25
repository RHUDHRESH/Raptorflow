use axum::{
    Json, Router,
    extract::{Extension, Path, Query},
    http::StatusCode,
    routing::{delete, get, post},
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
    tracing::error!("Capabilities route error: {e}");
    (
        StatusCode::INTERNAL_SERVER_ERROR,
        Json(json!({ "error": "capability_internal_error" })),
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

fn forbidden(msg: &str) -> (StatusCode, Json<Value>) {
    (StatusCode::FORBIDDEN, Json(json!({ "error": msg })))
}

fn service_unavailable(msg: &str) -> (StatusCode, Json<Value>) {
    (
        StatusCode::SERVICE_UNAVAILABLE,
        Json(json!({ "error": msg })),
    )
}

#[derive(Debug, Serialize)]
pub struct CapabilityDefinitionResponse {
    pub capability_id: String,
    pub capability_key: String,
    pub name: String,
    pub domain: String,
    pub description: String,
    pub input_schema: Value,
    pub output_schema: Value,
    pub required_context: Value,
    pub allowed_tools: Value,
    pub artifact_type: String,
    pub evaluator_key: String,
    pub ripple_policy: Value,
    pub risk_level: String,
    pub is_active: bool,
    pub created_at: String,
    pub updated_at: String,
}

impl From<raptorflow_db::models::CapabilityDefinition> for CapabilityDefinitionResponse {
    fn from(c: raptorflow_db::models::CapabilityDefinition) -> Self {
        Self {
            capability_id: c.capability_id,
            capability_key: c.capability_key,
            name: c.name,
            domain: c.domain,
            description: c.description,
            input_schema: c.input_schema,
            output_schema: c.output_schema,
            required_context: c.required_context,
            allowed_tools: c.allowed_tools,
            artifact_type: c.artifact_type,
            evaluator_key: c.evaluator_key,
            ripple_policy: c.ripple_policy,
            risk_level: c.risk_level,
            is_active: c.is_active,
            created_at: c.created_at.to_rfc3339(),
            updated_at: c.updated_at.to_rfc3339(),
        }
    }
}

#[derive(Debug, Serialize)]
pub struct CapabilityRunResponse {
    pub capability_run_id: String,
    pub org_id: String,
    pub avatar_id: Option<String>,
    pub capability_id: String,
    pub capability_key: Option<String>,
    pub status: String,
    pub input: Value,
    pub output: Option<Value>,
    pub error_message: Option<String>,
    pub model_id: Option<String>,
    pub token_usage: Value,
    pub started_at: Option<String>,
    pub completed_at: Option<String>,
    pub created_at: String,
    pub updated_at: String,
}

#[derive(Debug, Serialize)]
pub struct CapabilityArtifactResponse {
    pub artifact_id: String,
    pub org_id: String,
    pub capability_run_id: Option<String>,
    pub avatar_id: Option<String>,
    pub capability_id: Option<String>,
    pub artifact_type: String,
    pub title: String,
    pub body: Value,
    pub status: String,
    pub version: i32,
    pub evaluation: Value,
    pub created_at: String,
    pub updated_at: String,
}

impl From<raptorflow_db::models::CapabilityArtifact> for CapabilityArtifactResponse {
    fn from(a: raptorflow_db::models::CapabilityArtifact) -> Self {
        Self {
            artifact_id: a.artifact_id,
            org_id: a.org_id.to_string(),
            capability_run_id: a.capability_run_id,
            avatar_id: a.avatar_id,
            capability_id: a.capability_id,
            artifact_type: a.artifact_type,
            title: a.title,
            body: a.body,
            status: a.status,
            version: a.version,
            evaluation: a.evaluation,
            created_at: a.created_at.to_rfc3339(),
            updated_at: a.updated_at.to_rfc3339(),
        }
    }
}

#[derive(Debug, Deserialize)]
pub struct CreateCapabilityRunRequest {
    pub avatar_id: String,
    pub capability_key: String,
    #[serde(default)]
    pub campaign_id: Option<String>,
    pub input: Value,
    #[serde(default = "default_mode")]
    pub mode: String,
}

fn default_mode() -> String {
    "draft".to_string()
}

#[derive(Debug, Deserialize)]
pub struct ListArtifactsQuery {
    #[serde(default)]
    pub artifact_type: Option<String>,
    #[serde(default)]
    pub status: Option<String>,
    #[serde(default = "default_limit")]
    pub limit: i64,
}

fn default_limit() -> i64 {
    50
}

pub fn router(state: Arc<AppState>) -> Router {
    Router::new()
        .route("/capabilities", get(list_capabilities))
        .route("/capabilities/defaults", post(ensure_default_capabilities))
        .route("/capabilities/{id}", get(get_capability))
        .route("/capabilities/key/{key}", get(get_capability_by_key))
        .route("/avatars/{id}/capabilities", get(list_avatar_capabilities))
        .route(
            "/avatars/{id}/capabilities",
            post(grant_capability_to_avatar),
        )
        .route(
            "/avatars/{id}/capabilities/{capability_id}",
            delete(revoke_capability_from_avatar),
        )
        .route("/harness/context-packs", post(create_context_pack))
        .route("/harness/context-packs/{id}", get(get_context_pack))
        .route(
            "/capability-runs",
            get(list_capability_runs).post(create_capability_run),
        )
        .route("/capability-runs/{id}", get(get_capability_run))
        .route("/artifacts", get(list_artifacts))
        .route("/artifacts/{id}", get(get_artifact))
        .route("/artifacts/{id}/versions", post(create_artifact_version))
        .layer(Extension(state))
}

pub async fn list_capabilities(
    Extension(_tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
) -> AppResult<Json<Value>> {
    let pool = tenant_pool.pool();

    let capabilities = db::list_capabilities(pool).await.map_err(internal_error)?;

    let response: Vec<CapabilityDefinitionResponse> = capabilities
        .into_iter()
        .map(CapabilityDefinitionResponse::from)
        .collect();

    Ok(Json(json!({ "capabilities": response })))
}

pub async fn ensure_default_capabilities(
    Extension(_tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
) -> AppResult<Json<Value>> {
    let pool = tenant_pool.pool();

    raptorflow_harness::seeds::CapabilitySeeder::seed_default_capabilities(pool)
        .await
        .map_err(internal_error)?;

    let capabilities = db::list_capabilities(pool).await.map_err(internal_error)?;

    let response: Vec<CapabilityDefinitionResponse> = capabilities
        .into_iter()
        .map(CapabilityDefinitionResponse::from)
        .collect();

    Ok(Json(json!({ "capabilities": response })))
}

pub async fn get_capability(
    Extension(_tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(capability_id): Path<String>,
) -> AppResult<Json<Value>> {
    let pool = tenant_pool.pool();

    let capability = db::get_capability(pool, &capability_id)
        .await
        .map_err(internal_error)?
        .ok_or_else(|| not_found("capability_not_found"))?;

    Ok(Json(
        json!({ "capability": CapabilityDefinitionResponse::from(capability) }),
    ))
}

pub async fn get_capability_by_key(
    Extension(_tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(capability_key): Path<String>,
) -> AppResult<Json<Value>> {
    let pool = tenant_pool.pool();

    let capability = db::get_capability_by_key(pool, &capability_key)
        .await
        .map_err(internal_error)?
        .ok_or_else(|| not_found("capability_not_found"))?;

    Ok(Json(
        json!({ "capability": CapabilityDefinitionResponse::from(capability) }),
    ))
}

pub async fn list_avatar_capabilities(
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

    let capabilities = db::list_avatar_capabilities(pool, org_id, &avatar.avatar_id)
        .await
        .map_err(internal_error)?;

    let response: Vec<CapabilityDefinitionResponse> = capabilities
        .into_iter()
        .map(CapabilityDefinitionResponse::from)
        .collect();

    Ok(Json(json!({ "capabilities": response })))
}

#[derive(Debug, Deserialize)]
pub struct GrantCapabilityRequest {
    pub capability_id: String,
    #[serde(default = "default_grant_scope")]
    pub grant_scope: String,
    #[serde(default)]
    pub constraints: Value,
}

fn default_grant_scope() -> String {
    "org".to_string()
}

pub async fn grant_capability_to_avatar(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(avatar_id): Path<String>,
    Json(body): Json<GrantCapabilityRequest>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;
    let pool = tenant_pool.pool();

    let avatar = db::get_avatar(pool, org_id, &avatar_id)
        .await
        .map_err(internal_error)?
        .ok_or_else(|| not_found("avatar_not_found"))?;

    let capability = db::get_capability(pool, &body.capability_id)
        .await
        .map_err(internal_error)?
        .ok_or_else(|| not_found("capability_not_found"))?;

    let grant_id = uuid::Uuid::new_v4().to_string();

    db::grant_capability_to_avatar(
        pool,
        &grant_id,
        org_id,
        &avatar.avatar_id,
        &capability.capability_id,
        &body.grant_scope,
        &body.constraints,
    )
    .await
    .map_err(internal_error)?;

    Ok(Json(json!({
        "grant_id": grant_id,
        "avatar_id": avatar.avatar_id,
        "capability_id": capability.capability_id,
        "capability_key": capability.capability_key,
        "grant_scope": body.grant_scope
    })))
}

pub async fn revoke_capability_from_avatar(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path((avatar_id, capability_id)): Path<(String, String)>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;
    let pool = tenant_pool.pool();

    db::revoke_capability_from_avatar(pool, org_id, &avatar_id, &capability_id)
        .await
        .map_err(internal_error)?;

    Ok(Json(
        json!({ "revoked": true, "avatar_id": avatar_id, "capability_id": capability_id }),
    ))
}

#[derive(Debug, Deserialize)]
pub struct CreateContextPackRequest {
    #[serde(default)]
    pub avatar_id: Option<String>,
    #[serde(default)]
    pub capability_id: Option<String>,
    #[serde(default)]
    pub capability_key: Option<String>,
    #[serde(default)]
    pub campaign_id: Option<String>,
    #[serde(default = "default_token_budget")]
    pub token_budget: usize,
}

fn default_token_budget() -> usize {
    6000
}

pub async fn create_context_pack(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Json(body): Json<CreateContextPackRequest>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;
    let pool = tenant_pool.pool();

    let capability_id = if let Some(ref key) = body.capability_key {
        let cap = db::get_capability_by_key(pool, key)
            .await
            .map_err(internal_error)?;
        cap.map(|c| c.capability_id)
    } else {
        body.capability_id.clone()
    };

    let req = raptorflow_harness::cortex::CortexContextRequest {
        org_id,
        avatar_id: body.avatar_id.clone(),
        capability_id: capability_id.clone(),
        capability_key: body.capability_key.clone(),
        campaign_id: body.campaign_id.clone(),
        run_id: None,
        token_budget: body.token_budget,
    };

    let (stored, _) = raptorflow_harness::cortex::Cortex::build_and_store_context_pack(pool, req)
        .await
        .map_err(|e| internal_error(e.to_string()))?;

    Ok(Json(json!({
        "context_pack_id": stored.context_pack_id,
        "org_id": stored.org_id.to_string(),
        "scope": stored.scope,
        "token_budget": stored.token_budget,
        "created_at": stored.created_at.to_rfc3339()
    })))
}

pub async fn get_context_pack(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(context_pack_id): Path<String>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;
    let pool = tenant_pool.pool();

    let pack = db::get_context_pack(pool, org_id, &context_pack_id)
        .await
        .map_err(internal_error)?
        .ok_or_else(|| not_found("context_pack_not_found"))?;

    Ok(Json(json!({
        "context_pack_id": pack.context_pack_id,
        "org_id": pack.org_id.to_string(),
        "run_id": pack.run_id,
        "capability_id": pack.capability_id,
        "avatar_id": pack.avatar_id,
        "scope": pack.scope,
        "token_budget": pack.token_budget,
        "foundation_context": pack.foundation_context,
        "intel_context": pack.intel_context,
        "campaign_context": pack.campaign_context,
        "office_context": pack.office_context,
        "ripple_context": pack.ripple_context,
        "compressed_context": pack.compressed_context,
        "created_at": pack.created_at.to_rfc3339()
    })))
}

pub async fn list_capability_runs(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Query(query): Query<ListArtifactsQuery>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;
    let pool = tenant_pool.pool();

    let limit = query.limit.clamp(1, 100);

    let runs = db::list_capability_runs(pool, org_id, limit)
        .await
        .map_err(internal_error)?;

    let capabilities: std::collections::HashMap<String, String> = db::list_capabilities(pool)
        .await
        .map_err(internal_error)?
        .into_iter()
        .map(|c| (c.capability_id.clone(), c.capability_key))
        .collect();

    let response: Vec<Value> = runs
        .into_iter()
        .map(|r| {
            json!({
                "capability_run_id": r.capability_run_id,
                "org_id": r.org_id.to_string(),
                "avatar_id": r.avatar_id,
                "capability_id": r.capability_id,
                "capability_key": capabilities.get(&r.capability_id),
                "status": r.status,
                "input": r.input,
                "output": r.output,
                "error_message": r.error_message,
                "model_id": r.model_id,
                "token_usage": r.token_usage,
                "started_at": r.started_at.map(|t| t.to_rfc3339()),
                "completed_at": r.completed_at.map(|t| t.to_rfc3339()),
                "created_at": r.created_at.to_rfc3339(),
                "updated_at": r.updated_at.to_rfc3339()
            })
        })
        .collect();

    Ok(Json(json!({ "capability_runs": response })))
}

pub async fn create_capability_run(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Extension(state): Extension<Arc<AppState>>,
    Json(body): Json<CreateCapabilityRunRequest>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;
    let pool = tenant_pool.pool();

    let avatar = db::get_avatar(pool, org_id, &body.avatar_id)
        .await
        .map_err(internal_error)?
        .ok_or_else(|| not_found("avatar_not_found"))?;

    let capability = db::get_capability_by_key(pool, &body.capability_key)
        .await
        .map_err(internal_error)?
        .ok_or_else(|| not_found("capability_not_found"))?;

    let grant_exists = db::check_avatar_capability_grant(
        pool,
        org_id,
        &avatar.avatar_id,
        &capability.capability_id,
    )
    .await
    .map_err(internal_error)?;

    if !grant_exists {
        let msg = format!(
            "Avatar {} does not have grant for capability {}",
            avatar.avatar_key, body.capability_key
        );
        return Err(forbidden(&msg));
    }

    let mode = match body.mode.as_str() {
        "dry_run" => raptorflow_harness::execution::ExecutionMode::DryRun,
        "draft" => raptorflow_harness::execution::ExecutionMode::Draft,
        _ => return Err(bad_request("mode must be 'draft' or 'dry_run'")),
    };

    let bedrock = state.bedrock.clone();

    if mode == raptorflow_harness::execution::ExecutionMode::Draft && bedrock.is_none() {
        return Err(service_unavailable(
            "Bedrock is unavailable. Use mode 'dry_run' instead.",
        ));
    }

    let input = raptorflow_harness::execution::ExecutionInput {
        org_id,
        avatar,
        capability: capability.clone(),
        capability_key: body.capability_key.clone(),
        input: body.input,
        campaign_id: body.campaign_id.clone(),
        mode,
    };

    let result = raptorflow_harness::execution::ExecutionEngine::execute(
        pool,
        bedrock.as_ref().map(|b| b.clone()),
        input,
    )
    .await
    .map_err(|e| {
        tracing::error!("Capability execution failed: {}", e);
        let err_str = e.to_string();
        match &e {
            raptorflow_harness::execution::ExecutionError::NoCapabilityGrant(_, _) => {
                forbidden(&err_str)
            }
            raptorflow_harness::execution::ExecutionError::BedrockUnavailable => {
                service_unavailable(&err_str)
            }
            _ => internal_error(&err_str),
        }
    })?;

    Ok(Json(json!({
        "capability_run_id": result.capability_run_id,
        "artifact_id": result.artifact_id,
        "status": result.status,
        "output": result.output,
        "error": result.error,
        "model_id": result.model_id,
        "token_usage": result.token_usage
    })))
}

pub async fn get_capability_run(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(capability_run_id): Path<String>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;
    let pool = tenant_pool.pool();

    let run = db::get_capability_run(pool, org_id, &capability_run_id)
        .await
        .map_err(internal_error)?
        .ok_or_else(|| not_found("capability_run_not_found"))?;

    let capability = db::get_capability(pool, &run.capability_id)
        .await
        .map_err(internal_error)?;

    Ok(Json(json!({
        "capability_run_id": run.capability_run_id,
        "org_id": run.org_id.to_string(),
        "avatar_id": run.avatar_id,
        "capability_id": run.capability_id,
        "capability_key": capability.map(|c| c.capability_key),
        "status": run.status,
        "input": run.input,
        "output": run.output,
        "error_message": run.error_message,
        "model_id": run.model_id,
        "token_usage": run.token_usage,
        "started_at": run.started_at.map(|t| t.to_rfc3339()),
        "completed_at": run.completed_at.map(|t| t.to_rfc3339()),
        "created_at": run.created_at.to_rfc3339(),
        "updated_at": run.updated_at.to_rfc3339()
    })))
}

pub async fn list_artifacts(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Query(query): Query<ListArtifactsQuery>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;
    let pool = tenant_pool.pool();

    let limit = query.limit.clamp(1, 100);

    let artifacts = db::list_artifacts(
        pool,
        org_id,
        query.artifact_type.as_deref(),
        query.status.as_deref(),
        limit,
    )
    .await
    .map_err(internal_error)?;

    let response: Vec<CapabilityArtifactResponse> = artifacts
        .into_iter()
        .map(CapabilityArtifactResponse::from)
        .collect();

    Ok(Json(json!({ "artifacts": response })))
}

pub async fn get_artifact(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(artifact_id): Path<String>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;
    let pool = tenant_pool.pool();

    let artifact = db::get_capability_artifact(pool, org_id, &artifact_id)
        .await
        .map_err(internal_error)?
        .ok_or_else(|| not_found("artifact_not_found"))?;

    Ok(Json(
        json!({ "artifact": CapabilityArtifactResponse::from(artifact) }),
    ))
}

#[derive(Debug, Deserialize)]
pub struct CreateArtifactVersionRequest {
    pub body: Value,
    #[serde(default = "default_change_reason")]
    pub change_reason: String,
}

fn default_change_reason() -> String {
    "Updated version".to_string()
}

pub async fn create_artifact_version(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(artifact_id): Path<String>,
    Json(body): Json<CreateArtifactVersionRequest>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;
    let pool = tenant_pool.pool();

    let artifact = db::get_capability_artifact(pool, org_id, &artifact_id)
        .await
        .map_err(internal_error)?
        .ok_or_else(|| not_found("artifact_not_found"))?;

    let new_version = artifact.version + 1;

    let version_id = uuid::Uuid::new_v4().to_string();

    db::create_artifact_version(
        pool,
        &version_id,
        &artifact_id,
        org_id,
        new_version,
        &body.body,
        &body.change_reason,
    )
    .await
    .map_err(internal_error)?;

    sqlx::query(
        r#"
        UPDATE capability_artifacts
        SET body = $1, version = $2, updated_at = now()
        WHERE artifact_id = $3 AND org_id = $4
        "#,
    )
    .bind(&body.body)
    .bind(new_version)
    .bind(&artifact_id)
    .bind(org_id)
    .execute(pool)
    .await
    .map_err(internal_error)?;

    let updated = db::get_capability_artifact(pool, org_id, &artifact_id)
        .await
        .map_err(internal_error)?
        .ok_or_else(|| not_found("artifact_not_found"))?;

    Ok(Json(
        json!({ "artifact": CapabilityArtifactResponse::from(updated) }),
    ))
}
