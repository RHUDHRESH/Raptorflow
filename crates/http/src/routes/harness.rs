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
    tracing::error!("Harness route error: {e}");
    (
        StatusCode::INTERNAL_SERVER_ERROR,
        Json(json!({ "error": "harness_internal_error" })),
    )
}

fn not_found(msg: &str) -> (StatusCode, Json<Value>) {
    (StatusCode::NOT_FOUND, Json(json!({ "error": msg })))
}

fn not_implemented(msg: &str) -> (StatusCode, Json<Value>) {
    (StatusCode::NOT_IMPLEMENTED, Json(json!({ "error": msg })))
}

#[derive(Debug, Serialize)]
pub struct HarnessRunResponse {
    pub run_id: String,
    pub run_type: String,
    pub status: String,
    pub input: Value,
    pub output: Option<Value>,
    pub error_message: Option<String>,
    pub created_by: Option<String>,
    pub started_at: Option<String>,
    pub completed_at: Option<String>,
    pub created_at: String,
    pub updated_at: String,
}

impl From<raptorflow_db::models::HarnessRun> for HarnessRunResponse {
    fn from(r: raptorflow_db::models::HarnessRun) -> Self {
        Self {
            run_id: r.run_id,
            run_type: r.run_type,
            status: r.status,
            input: r.input,
            output: r.output,
            error_message: r.error_message,
            created_by: r.created_by,
            started_at: r.started_at.map(|t| t.to_rfc3339()),
            completed_at: r.completed_at.map(|t| t.to_rfc3339()),
            created_at: r.created_at.to_rfc3339(),
            updated_at: r.updated_at.to_rfc3339(),
        }
    }
}

#[derive(Debug, Serialize)]
pub struct HarnessStepResponse {
    pub step_id: String,
    pub run_id: String,
    pub avatar_id: Option<String>,
    pub step_type: String,
    pub status: String,
    pub input: Value,
    pub output: Option<Value>,
    pub error_message: Option<String>,
    pub sequence_number: i32,
    pub started_at: Option<String>,
    pub completed_at: Option<String>,
    pub created_at: String,
    pub updated_at: String,
}

impl From<raptorflow_db::models::HarnessStep> for HarnessStepResponse {
    fn from(s: raptorflow_db::models::HarnessStep) -> Self {
        Self {
            step_id: s.step_id,
            run_id: s.run_id,
            avatar_id: s.avatar_id,
            step_type: s.step_type,
            status: s.status,
            input: s.input,
            output: s.output,
            error_message: s.error_message,
            sequence_number: s.sequence_number,
            started_at: s.started_at.map(|t| t.to_rfc3339()),
            completed_at: s.completed_at.map(|t| t.to_rfc3339()),
            created_at: s.created_at.to_rfc3339(),
            updated_at: s.updated_at.to_rfc3339(),
        }
    }
}

#[derive(Debug, Deserialize)]
pub struct CreateHarnessRunRequest {
    pub run_type: String,
    pub input: Value,
    #[serde(default)]
    pub avatar_keys: Vec<String>,
    #[serde(default)]
    pub execute_now: bool,
}

pub fn router(state: Arc<AppState>) -> Router {
    Router::new()
        .route("/runs", get(list_runs).post(create_run))
        .route("/runs/{id}", get(get_run))
        .route("/runs/{id}/cancel", post(cancel_run))
        .route("/runs/{id}/steps", get(list_steps))
        .layer(Extension(state))
}

pub async fn list_runs(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;
    let pool = tenant_pool.pool();

    let runs = db::list_harness_runs(pool, org_id)
        .await
        .map_err(internal_error)?;

    let response: Vec<HarnessRunResponse> = runs.into_iter().map(HarnessRunResponse::from).collect();
    Ok(Json(json!({ "runs": response })))
}

pub async fn get_run(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(run_id): Path<String>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;
    let pool = tenant_pool.pool();

    let run = db::get_harness_run(pool, &run_id, org_id)
        .await
        .map_err(internal_error)?
        .ok_or_else(|| not_found("harness_run_not_found"))?;

    Ok(Json(json!({ "run": HarnessRunResponse::from(run) })))
}

pub async fn create_run(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Json(body): Json<CreateHarnessRunRequest>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;
    let pool = tenant_pool.pool();

    if body.run_type.is_empty() {
        return Err((
            StatusCode::BAD_REQUEST,
            Json(json!({ "error": "run_type is required" })),
        ));
    }

    if body.execute_now {
        return Err(not_implemented("harness_execution_not_implemented"));
    }

    let run_id = uuid::Uuid::new_v4().to_string();
    let input = body.input.as_object().cloned().unwrap_or_default().into();

    db::create_harness_run(pool, &run_id, org_id, &body.run_type, &input, None)
        .await
        .map_err(internal_error)?;

    let steps_created = if !body.avatar_keys.is_empty() {
        let mut steps = Vec::new();
        for (seq, key) in body.avatar_keys.iter().enumerate() {
            if let Some(avatar) = db::get_avatar_by_key(pool, org_id, key).await.map_err(internal_error)? {
                let step_id = uuid::Uuid::new_v4().to_string();
                let step_input = json!({ "avatar_key": key });
                db::create_harness_step(
                    pool,
                    &step_id,
                    &run_id,
                    org_id,
                    Some(&avatar.avatar_id),
                    "avatar_delegation",
                    (seq + 1) as i32,
                    &step_input,
                )
                .await
                .map_err(internal_error)?;
                steps.push(json!({
                    "step_id": step_id,
                    "avatar_key": key,
                    "status": "queued"
                }));
            }
        }
        steps
    } else {
        Vec::new()
    };

    let run = db::get_harness_run(pool, &run_id, org_id)
        .await
        .map_err(internal_error)?
        .ok_or_else(|| internal_error("run not found after create"))?;

    Ok(Json(json!({
        "run": HarnessRunResponse::from(run),
        "steps": steps_created
    })))
}

pub async fn cancel_run(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(run_id): Path<String>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;
    let pool = tenant_pool.pool();

    let existing = db::get_harness_run(pool, &run_id, org_id)
        .await
        .map_err(internal_error)?
        .ok_or_else(|| not_found("harness_run_not_found"))?;

    if existing.status == "completed" || existing.status == "failed" {
        return Err((
            StatusCode::BAD_REQUEST,
            Json(json!({ "error": "cannot cancel a run that is already completed or failed" })),
        ));
    }

    db::cancel_harness_run(pool, &run_id, org_id)
        .await
        .map_err(internal_error)?;

    let run = db::get_harness_run(pool, &run_id, org_id)
        .await
        .map_err(internal_error)?
        .ok_or_else(|| not_found("harness_run_not_found"))?;

    Ok(Json(json!({ "run": HarnessRunResponse::from(run) })))
}

pub async fn list_steps(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(run_id): Path<String>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;
    let pool = tenant_pool.pool();

    let steps = db::list_harness_steps(pool, &run_id, org_id)
        .await
        .map_err(internal_error)?;

    let response: Vec<HarnessStepResponse> = steps.into_iter().map(HarnessStepResponse::from).collect();
    Ok(Json(json!({ "steps": response })))
}
