use axum::{
    extract::{Extension, Path},
    http::StatusCode,
    Json, Router,
    routing::{get, patch},
};
use serde::{Deserialize, Serialize};
use serde_json::{Value, json};
use ulid::Ulid;

use raptorflow_auth::TenantContext;
use raptorflow_db::{queries, TenantDbPool};
use raptorflow_db::models::{Campaign, CampaignMove, CampaignTask, CampaignBrief};
use crate::routes::office::handlers::emit_office_event;

pub fn router() -> Router {
    Router::new()
        .route("/", get(list_campaigns).post(create_campaign))
        .route("/{id}", get(get_campaign))
        .route("/{id}/status", patch(update_campaign_status))
        .route("/{id}/moves", get(list_moves).post(create_move))
        .route("/{id}/moves/{move_id}/status", patch(update_move_status))
        .route("/{id}/tasks", get(list_tasks).post(create_task))
        .route("/{id}/tasks/{task_id}/status", patch(update_task_status))
        .route("/{id}/brief", get(get_brief).post(create_brief))
        .route("/{id}/brief/status", patch(update_brief_status))
}

type AppResult<T> = Result<T, (StatusCode, Json<Value>)>;

fn internal_error<E: std::fmt::Display>(e: E) -> (StatusCode, Json<Value>) {
    tracing::error!("Campaign route error: {e}");
    (
        StatusCode::INTERNAL_SERVER_ERROR,
        Json(json!({ "error": "campaign_internal_error" })),
    )
}

fn bad_request(msg: &str) -> (StatusCode, Json<Value>) {
    (StatusCode::BAD_REQUEST, Json(json!({ "error": msg })))
}

fn not_found(msg: &str) -> (StatusCode, Json<Value>) {
    (StatusCode::NOT_FOUND, Json(json!({ "error": msg })))
}

#[derive(Debug, Deserialize)]
pub struct CreateCampaignRequest {
    pub name: String,
    pub goal: String,
}

#[derive(Debug, Serialize)]
pub struct CampaignResponse {
    pub campaign_id: String,
    pub org_id: String,
    pub name: String,
    pub goal: String,
    pub status: String,
    pub active_move_id: Option<String>,
    pub created_at: String,
    pub updated_at: String,
}

impl From<Campaign> for CampaignResponse {
    fn from(c: Campaign) -> Self {
        Self {
            campaign_id: c.campaign_id,
            org_id: c.org_id.to_string(),
            name: c.name,
            goal: c.goal,
            status: c.status,
            active_move_id: c.active_move_id,
            created_at: c.created_at.to_rfc3339(),
            updated_at: c.updated_at.to_rfc3339(),
        }
    }
}

#[derive(Debug, Deserialize)]
pub struct UpdateStatusRequest {
    pub status: String,
}

#[derive(Debug, Serialize)]
pub struct MoveResponse {
    pub move_id: String,
    pub campaign_id: String,
    pub move_type: String,
    pub sequence_number: i32,
    pub status: String,
    pub created_at: String,
}

impl From<CampaignMove> for MoveResponse {
    fn from(m: CampaignMove) -> Self {
        Self {
            move_id: m.move_id,
            campaign_id: m.campaign_id,
            move_type: m.move_type,
            sequence_number: m.sequence_number,
            status: m.status,
            created_at: m.created_at.to_rfc3339(),
        }
    }
}

#[derive(Debug, Deserialize)]
pub struct CreateMoveRequest {
    pub move_type: String,
    pub sequence_number: i32,
}

#[derive(Debug, Serialize)]
pub struct TaskResponse {
    pub task_id: String,
    pub move_id: String,
    pub campaign_id: String,
    pub title: String,
    pub status: String,
    pub scheduled_date: Option<String>,
    pub created_at: String,
}

impl From<CampaignTask> for TaskResponse {
    fn from(t: CampaignTask) -> Self {
        Self {
            task_id: t.task_id,
            move_id: t.move_id,
            campaign_id: t.campaign_id,
            title: t.title,
            status: t.status,
            scheduled_date: t.scheduled_date.map(|d| d.to_string()),
            created_at: t.created_at.to_rfc3339(),
        }
    }
}

#[derive(Debug, Deserialize)]
pub struct CreateTaskRequest {
    pub move_id: String,
    pub title: String,
    pub scheduled_date: Option<String>,
}

#[derive(Debug, Deserialize)]
pub struct CreateBriefRequest {
    pub original_text: String,
}

#[derive(Debug, Serialize)]
pub struct BriefResponse {
    pub brief_id: String,
    pub campaign_id: Option<String>,
    pub status: String,
    pub original_text: String,
    pub created_at: String,
}

impl From<CampaignBrief> for BriefResponse {
    fn from(b: CampaignBrief) -> Self {
        Self {
            brief_id: b.brief_id,
            campaign_id: b.campaign_id,
            status: b.status,
            original_text: b.original_text,
            created_at: b.created_at.to_rfc3339(),
        }
    }
}

pub async fn list_campaigns(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;
    let campaigns = queries::list_campaigns(&tenant_pool.pool(), org_id)
        .await
        .map_err(internal_error)?;

    let list: Vec<CampaignResponse> = campaigns.into_iter().map(Into::into).collect();

    Ok(Json(json!({
        "campaigns": list,
        "total": list.len(),
        "status": "ok"
    })))
}

pub async fn create_campaign(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Json(req): Json<CreateCampaignRequest>,
) -> AppResult<Json<Value>> {
    if req.name.trim().is_empty() {
        return Err(bad_request("campaign_name_required"));
    }
    if req.goal.trim().is_empty() {
        return Err(bad_request("campaign_goal_required"));
    }

    let org_id = tenant.org_id;
    let campaign_id = Ulid::new().to_string();

    queries::create_campaign(&tenant_pool.pool(), &campaign_id, org_id, &req.name, &req.goal)
        .await
        .map_err(internal_error)?;

    let campaign = queries::get_campaign(&tenant_pool.pool(), &campaign_id, org_id)
        .await
        .map_err(internal_error)?;

    match campaign {
        Some(c) => {
            emit_office_event("campaign_created", org_id, json!({"campaign_id": &c.campaign_id, "name": &c.name}));
            Ok(Json(json!({
                "campaign": CampaignResponse::from(c),
                "status": "created"
            })))
        }
        None => Err(internal_error("campaign_not_found_after_create")),
    }
}

pub async fn get_campaign(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(campaign_id): Path<String>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;

    let campaign = queries::get_campaign(&tenant_pool.pool(), &campaign_id, org_id)
        .await
        .map_err(internal_error)?;

    match campaign {
        Some(c) => {
            let moves = queries::list_campaign_moves(&tenant_pool.pool(), &campaign_id, org_id)
                .await
                .map_err(internal_error)?;
            let tasks = queries::list_campaign_tasks(&tenant_pool.pool(), &campaign_id, org_id)
                .await
                .map_err(internal_error)?;

            Ok(Json(json!({
                "campaign": CampaignResponse::from(c),
                "moves": moves.into_iter().map(Into::into).collect::<Vec<MoveResponse>>(),
                "tasks": tasks.into_iter().map(Into::into).collect::<Vec<TaskResponse>>(),
                "status": "ok"
            })))
        }
        None => Err(not_found("campaign_not_found")),
    }
}

pub async fn update_campaign_status(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(campaign_id): Path<String>,
    Json(req): Json<UpdateStatusRequest>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;

    let valid_statuses = ["draft", "active", "paused", "completed", "archived"];
    if !valid_statuses.contains(&req.status.as_str()) {
        return Err(bad_request("invalid_status"));
    }

    let existing = queries::get_campaign(&tenant_pool.pool(), &campaign_id, org_id)
        .await
        .map_err(internal_error)?;
    if existing.is_none() {
        return Err(not_found("campaign_not_found"));
    }

    queries::update_campaign_status(&tenant_pool.pool(), &campaign_id, org_id, &req.status)
        .await
        .map_err(internal_error)?;

    Ok(Json(json!({ "status": "updated" })))
}

pub async fn list_moves(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(campaign_id): Path<String>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;

    let existing = queries::get_campaign(&tenant_pool.pool(), &campaign_id, org_id)
        .await
        .map_err(internal_error)?;
    if existing.is_none() {
        return Err(not_found("campaign_not_found"));
    }

    let moves = queries::list_campaign_moves(&tenant_pool.pool(), &campaign_id, org_id)
        .await
        .map_err(internal_error)?;

    Ok(Json(json!({
        "moves": moves.into_iter().map(Into::into).collect::<Vec<MoveResponse>>(),
        "status": "ok"
    })))
}

pub async fn create_move(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(campaign_id): Path<String>,
    Json(req): Json<CreateMoveRequest>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;

    let existing = queries::get_campaign(&tenant_pool.pool(), &campaign_id, org_id)
        .await
        .map_err(internal_error)?;
    if existing.is_none() {
        return Err(not_found("campaign_not_found"));
    }

    let move_id = Ulid::new().to_string();
    queries::create_campaign_move(
        &tenant_pool.pool(),
        &move_id,
        &campaign_id,
        org_id,
        &req.move_type,
        req.sequence_number,
    )
    .await
    .map_err(internal_error)?;

    Ok(Json(json!({
        "move_id": move_id,
        "status": "created"
    })))
}

pub async fn update_move_status(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path((_campaign_id, move_id)): Path<(String, String)>,
    Json(req): Json<UpdateStatusRequest>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;

    let valid_statuses = ["planned", "in_progress", "completed", "skipped"];
    if !valid_statuses.contains(&req.status.as_str()) {
        return Err(bad_request("invalid_move_status"));
    }

    queries::update_move_status(&tenant_pool.pool(), &move_id, org_id, &req.status)
        .await
        .map_err(internal_error)?;

    Ok(Json(json!({ "status": "updated" })))
}

pub async fn list_tasks(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(campaign_id): Path<String>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;

    let existing = queries::get_campaign(&tenant_pool.pool(), &campaign_id, org_id)
        .await
        .map_err(internal_error)?;
    if existing.is_none() {
        return Err(not_found("campaign_not_found"));
    }

    let tasks = queries::list_campaign_tasks(&tenant_pool.pool(), &campaign_id, org_id)
        .await
        .map_err(internal_error)?;

    Ok(Json(json!({
        "tasks": tasks.into_iter().map(Into::into).collect::<Vec<TaskResponse>>(),
        "status": "ok"
    })))
}

pub async fn create_task(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(campaign_id): Path<String>,
    Json(req): Json<CreateTaskRequest>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;

    if req.title.trim().is_empty() {
        return Err(bad_request("task_title_required"));
    }

    let existing = queries::get_campaign(&tenant_pool.pool(), &campaign_id, org_id)
        .await
        .map_err(internal_error)?;
    if existing.is_none() {
        return Err(not_found("campaign_not_found"));
    }

    let task_id = Ulid::new().to_string();
    queries::create_campaign_task(
        &tenant_pool.pool(),
        &task_id,
        &req.move_id,
        &campaign_id,
        org_id,
        &req.title,
    )
    .await
    .map_err(internal_error)?;

    Ok(Json(json!({
        "task_id": task_id,
        "status": "created"
    })))
}

pub async fn update_task_status(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path((_campaign_id, task_id)): Path<(String, String)>,
    Json(req): Json<UpdateStatusRequest>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;

    let valid_statuses = ["pending", "in_progress", "completed", "cancelled"];
    if !valid_statuses.contains(&req.status.as_str()) {
        return Err(bad_request("invalid_task_status"));
    }

    queries::update_task_status(&tenant_pool.pool(), &task_id, org_id, &req.status)
        .await
        .map_err(internal_error)?;

    Ok(Json(json!({ "status": "updated" })))
}

pub async fn get_brief(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(campaign_id): Path<String>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;

    let existing = queries::get_campaign(&tenant_pool.pool(), &campaign_id, org_id)
        .await
        .map_err(internal_error)?;
    if existing.is_none() {
        return Err(not_found("campaign_not_found"));
    }

    let brief = queries::get_campaign_brief(&tenant_pool.pool(), &campaign_id, org_id)
        .await
        .map_err(internal_error)?;

    match brief {
        Some(b) => Ok(Json(json!({
            "brief": BriefResponse::from(b),
            "status": "ok"
        }))),
        None => Ok(Json(json!({
            "brief": null,
            "status": "ok"
        }))),
    }
}

pub async fn create_brief(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(campaign_id): Path<String>,
    Json(req): Json<CreateBriefRequest>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;

    if req.original_text.trim().is_empty() {
        return Err(bad_request("brief_text_required"));
    }

    let existing = queries::get_campaign(&tenant_pool.pool(), &campaign_id, org_id)
        .await
        .map_err(internal_error)?;
    if existing.is_none() {
        return Err(not_found("campaign_not_found"));
    }

    let brief_id = Ulid::new().to_string();
    queries::create_campaign_brief(
        &tenant_pool.pool(),
        &brief_id,
        org_id,
        Some(&campaign_id),
        &req.original_text,
    )
    .await
    .map_err(internal_error)?;

    Ok(Json(json!({
        "brief_id": brief_id,
        "status": "created"
    })))
}

pub async fn update_brief_status(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(campaign_id): Path<String>,
    Json(req): Json<UpdateStatusRequest>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;

    let brief = queries::get_campaign_brief(&tenant_pool.pool(), &campaign_id, org_id)
        .await
        .map_err(internal_error)?;

    let brief_id = match brief {
        Some(b) => b.brief_id,
        None => return Err(not_found("brief_not_found")),
    };

    let valid_statuses = ["draft", "submitted", "approved", "rejected"];
    if !valid_statuses.contains(&req.status.as_str()) {
        return Err(bad_request("invalid_brief_status"));
    }

    queries::update_brief_status(&tenant_pool.pool(), &brief_id, org_id, &req.status)
        .await
        .map_err(internal_error)?;

    Ok(Json(json!({ "status": "updated" })))
}
