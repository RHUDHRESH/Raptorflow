use axum::{
    extract::{Extension, Path},
    http::StatusCode,
    Json, Router,
    routing::{get, patch, post},
};
use serde::{Deserialize, Serialize};
use serde_json::{Value, json};
use std::sync::Arc;
use ulid::Ulid;

use raptorflow_auth::TenantContext;
use raptorflow_aws::bedrock::BedrockInferenceClient;
use raptorflow_db::{queries, TenantDbPool};
use raptorflow_db::models::{Campaign, CampaignMove, CampaignTask, CampaignBrief};
use crate::routes::office::handlers::emit_office_event;
use crate::routes::ai_helpers::{json_error, parse_ai_json, truncate_context};

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
        .route("/{id}/evaluate", post(evaluate_campaign))
        .route("/{id}/moves/generate", post(generate_campaign_moves))
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

fn service_unavailable() -> (StatusCode, Json<Value>) {
    (StatusCode::SERVICE_UNAVAILABLE, Json(json_error("ai_inference_unavailable")))
}

const VALID_MOVE_TYPES: &[&str] = &[
    "positioning",
    "content",
    "proof",
    "distribution",
    "offer",
    "analysis",
];

fn validate_generated_moves(moves: &[AiGeneratedMove], max_moves: usize) -> Result<(), Vec<String>> {
    let mut errors = Vec::new();

    if moves.is_empty() {
        errors.push("moves: empty generated move list".to_string());
    }

    if moves.len() > max_moves {
        errors.push(format!("moves: count {} exceeds max_moves {}", moves.len(), max_moves));
    }

    for (idx, m) in moves.iter().enumerate() {
        if !VALID_MOVE_TYPES.contains(&m.move_type.as_str()) {
            errors.push(format!("move[{}]: invalid move_type '{}'", idx, m.move_type));
        }
        if m.description.trim().len() < 5 {
            errors.push(format!("move[{}]: description too short (min 5 chars)", idx));
        }
        if m.expected_impact.trim().len() < 10 {
            errors.push(format!("move[{}]: expected_impact too short (min 10 chars)", idx));
        }
        if m.confidence < 0.0 || m.confidence > 1.0 {
            errors.push(format!("move[{}]: confidence out of range (0.0-1.0)", idx));
        }
    }

    if errors.is_empty() {
        Ok(())
    } else {
        Err(errors)
    }
}

fn build_generated_move_inserts(
    generated_moves: Vec<AiGeneratedMove>,
    next_seq: i32,
) -> Vec<queries::GeneratedCampaignMoveInsert> {
    generated_moves
        .into_iter()
        .enumerate()
        .map(|(idx, m)| {
            let move_id = Ulid::new().to_string();
            let content_id = Ulid::new().to_string();
            let move_body = serde_json::json!({
                "move_id": move_id,
                "description": m.description.trim(),
                "expected_impact": m.expected_impact.trim(),
                "confidence": m.confidence.clamp(0.0, 1.0),
                "sequence_number": next_seq + idx as i32,
            });
            queries::GeneratedCampaignMoveInsert {
                move_id,
                content_id,
                move_type: m.move_type,
                sequence_number: next_seq + idx as i32,
                content_body: move_body,
            }
        })
        .collect()
}

fn build_move_response_from_created(created: Vec<queries::GeneratedCampaignMoveCreated>) -> Vec<serde_json::Value> {
    created
        .into_iter()
        .map(|c| {
            let description = c.content_body
                .get("description")
                .and_then(|v| v.as_str())
                .unwrap_or("")
                .to_string();
            let expected_impact = c.content_body
                .get("expected_impact")
                .and_then(|v| v.as_str())
                .unwrap_or("")
                .to_string();
            let confidence = c.content_body
                .get("confidence")
                .and_then(|v| v.as_f64())
                .unwrap_or(0.0);
            let move_id = c.content_body
                .get("move_id")
                .and_then(|v| v.as_str())
                .unwrap_or(&c.move_id)
                .to_string();
            json!({
                "move_id": move_id,
                "move_type": c.move_type,
                "description": description,
                "expected_impact": expected_impact,
                "confidence": confidence,
                "sequence_number": c.sequence_number,
            })
        })
        .collect()
}

#[derive(Debug, Deserialize)]
pub struct EvaluateCampaignRequest {
    pub focus: Option<String>,
}

#[derive(Debug, Deserialize)]
pub struct GenerateMovesRequest {
    pub context: Option<String>,
    pub max_moves: Option<i32>,
}

#[derive(Debug, Deserialize, Serialize)]
struct AiCampaignEvaluation {
    overall_score: f64,
    strengths: Vec<String>,
    weaknesses: Vec<String>,
    opportunities: Vec<String>,
    threats: Vec<String>,
    recommendations: Vec<String>,
}

#[derive(Debug, Deserialize, Serialize)]
struct AiGeneratedMove {
    move_type: String,
    description: String,
    expected_impact: String,
    confidence: f64,
}

pub async fn evaluate_campaign(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Extension(bedrock): Extension<Option<Arc<BedrockInferenceClient>>>,
    Path(campaign_id): Path<String>,
    Json(req): Json<EvaluateCampaignRequest>,
) -> AppResult<Json<Value>> {
    let bedrock = bedrock.ok_or_else(service_unavailable)?;
    let org_id = tenant.org_id;

    let campaign = queries::get_campaign(&tenant_pool.pool(), &campaign_id, org_id)
        .await
        .map_err(internal_error)?;
    let campaign = campaign.ok_or_else(|| not_found("campaign_not_found"))?;

    let moves = queries::list_campaign_moves(&tenant_pool.pool(), &campaign_id, org_id)
        .await
        .map_err(internal_error)?;
    let tasks = queries::list_campaign_tasks(&tenant_pool.pool(), &campaign_id, org_id)
        .await
        .map_err(internal_error)?;

    let moves_text: String = moves
        .iter()
        .map(|m| format!("- {} ({}): {}", m.move_type, m.status, m.sequence_number))
        .collect::<Vec<_>>()
        .join("\n");

    let tasks_text: String = tasks
        .iter()
        .map(|t| format!("- {} ({})", t.title, t.status))
        .collect::<Vec<_>>()
        .join("\n");

    let prompt = format!(
        "Evaluate this campaign:\nName: {}\nGoal: {}\n\nMoves:\n{}\n\nTasks:\n{}\n\n\
        Provide your evaluation as JSON:\n{{\"overall_score\": 0.0-1.0, \"strengths\": [\"s1\", \"s2\"], \
        \"weaknesses\": [\"w1\", \"w2\"], \"opportunities\": [\"o1\", \"o2\"], \
        \"threats\": [\"t1\", \"t2\"], \"recommendations\": [\"r1\", \"r2\"]}}\n\
        Return ONLY valid JSON.",
        campaign.name,
        truncate_context(&campaign.goal, 500),
        truncate_context(&moves_text, 1000),
        truncate_context(&tasks_text, 1000)
    );

    let output = bedrock.converse_large(&prompt, 600).await.map_err(|e| {
        tracing::error!("Campaign evaluation Bedrock call failed: {}", e);
        (StatusCode::BAD_GATEWAY, Json(json_error("ai_inference_failed")))
    })?;

    let evaluation: AiCampaignEvaluation = parse_ai_json(&output).map_err(|e| {
        tracing::error!("Campaign evaluation parse failed: {}", e);
        (StatusCode::BAD_GATEWAY, Json(json_error("invalid_ai_output")))
    })?;

    if evaluation.overall_score < 0.0 || evaluation.overall_score > 1.0 {
        return Err((StatusCode::BAD_GATEWAY, Json(json_error("invalid_ai_output"))));
    }

    let eval_body = serde_json::json!({
        "campaign_id": campaign_id,
        "overall_score": evaluation.overall_score.clamp(0.0, 1.0),
        "strengths": evaluation.strengths,
        "weaknesses": evaluation.weaknesses,
        "opportunities": evaluation.opportunities,
        "threats": evaluation.threats,
        "recommendations": evaluation.recommendations,
        "focus": req.focus,
    });

    let content_id = Ulid::new().to_string();
    queries::create_generated_content(
        &tenant_pool.pool(),
        &content_id,
        org_id,
        Some(&campaign_id),
        None,
        "campaign_evaluation",
        "generated",
        &eval_body,
    )
    .await
    .map_err(internal_error)?;

    Ok(Json(json!({
        "campaign_id": campaign_id,
        "evaluation": {
            "overall_score": evaluation.overall_score.clamp(0.0, 1.0),
            "strengths": evaluation.strengths,
            "weaknesses": evaluation.weaknesses,
            "opportunities": evaluation.opportunities,
            "threats": evaluation.threats,
            "recommendations": evaluation.recommendations,
        }
    })))
}

pub async fn generate_campaign_moves(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Extension(bedrock): Extension<Option<Arc<BedrockInferenceClient>>>,
    Path(campaign_id): Path<String>,
    Json(req): Json<GenerateMovesRequest>,
) -> AppResult<Json<Value>> {
    let bedrock = bedrock.ok_or_else(service_unavailable)?;
    let org_id = tenant.org_id;

    let campaign = queries::get_campaign(&tenant_pool.pool(), &campaign_id, org_id)
        .await
        .map_err(internal_error)?;
    let campaign = campaign.ok_or_else(|| not_found("campaign_not_found"))?;

    let existing_moves = queries::list_campaign_moves(&tenant_pool.pool(), &campaign_id, org_id)
        .await
        .map_err(internal_error)?;

    let max_moves = req.max_moves.unwrap_or(3).min(5).max(1);

    let existing_moves_text: String = existing_moves
        .iter()
        .map(|m| format!("- {} ({})", m.move_type, m.status))
        .collect::<Vec<_>>()
        .join("\n");

    let prompt = format!(
        "Generate strategic moves for this campaign:\nName: {}\nGoal: {}\n\nExisting moves:\n{}\n\n\
        Context: {}\n\n\
        Generate {} move(s) as JSON array:\n[{{\"move_type\": \"type\", \"description\": \"desc\", \"expected_impact\": \"impact\", \"confidence\": 0.0-1.0}}]\n\
        Return ONLY valid JSON array, no markdown fences.",
        campaign.name,
        truncate_context(&campaign.goal, 300),
        truncate_context(&existing_moves_text, 500),
        truncate_context(req.context.as_deref().unwrap_or("general strategic expansion"), 200),
        max_moves
    );

    let output = bedrock.converse_large(&prompt, 600).await.map_err(|e| {
        tracing::error!("Move generation Bedrock call failed: {}", e);
        (StatusCode::BAD_GATEWAY, Json(json_error("ai_inference_failed")))
    })?;

    let generated_moves: Vec<AiGeneratedMove> = parse_ai_json(&output).map_err(|e| {
        tracing::error!("Move generation parse failed: {}", e);
        (StatusCode::BAD_GATEWAY, Json(json_error("invalid_ai_output")))
    })?;

    if let Err(validation_errors) = validate_generated_moves(&generated_moves, max_moves as usize) {
        tracing::warn!("Move generation validation failed: {} errors: {:?}", validation_errors.len(), validation_errors);
        return Err((StatusCode::BAD_GATEWAY, Json(json!({
            "error": "invalid_ai_output",
            "validation_errors": validation_errors.len()
        }))));
    }

    let next_seq = existing_moves.len() as i32 + 1;
    let inserts = build_generated_move_inserts(generated_moves, next_seq);

    let created = queries::create_generated_campaign_moves_transactional(
        &tenant_pool.pool(),
        org_id,
        &campaign_id,
        inserts,
    )
    .await
    .map_err(|e| {
        tracing::error!("Transaction failed for move generation: {}", e);
        (StatusCode::INTERNAL_SERVER_ERROR, Json(json_error("move_generation_transaction_failed")))
    })?;

    let results = build_move_response_from_created(created);

    Ok(Json(json!({
        "campaign_id": campaign_id,
        "generated_moves": results,
        "total": results.len(),
        "status": "created"
    })))
}

#[cfg(test)]
mod tests {
    use super::*;

    fn make_move(move_type: &str, description: &str, expected_impact: &str, confidence: f64) -> AiGeneratedMove {
        AiGeneratedMove {
            move_type: move_type.to_string(),
            description: description.to_string(),
            expected_impact: expected_impact.to_string(),
            confidence,
        }
    }

    #[test]
    fn test_validate_generated_moves_valid() {
        let moves = vec![
            make_move("positioning", "A good description here", "This is a long expected impact string", 0.85),
            make_move("content", "Another valid description", "Another long expected impact string", 0.72),
        ];
        assert!(validate_generated_moves(&moves, 5).is_ok());
    }

    #[test]
    fn test_validate_generated_moves_empty_rejects() {
        let moves: Vec<AiGeneratedMove> = vec![];
        let result = validate_generated_moves(&moves, 5);
        assert!(result.is_err());
        let errors = result.unwrap_err();
        assert!(errors.iter().any(|e| e.contains("empty generated move list")));
    }

    #[test]
    fn test_validate_generated_moves_invalid_move_type_rejects() {
        let moves = vec![
            make_move("positioning", "Valid description here", "Valid expected impact string", 0.8),
            make_move("invalid_type", "Valid description here", "Valid expected impact string", 0.8),
        ];
        let result = validate_generated_moves(&moves, 5);
        assert!(result.is_err());
        let errors = result.unwrap_err();
        assert!(errors.iter().any(|e| e.contains("invalid move_type")));
    }

    #[test]
    fn test_validate_generated_moves_short_description_rejects() {
        let moves = vec![
            make_move("positioning", "hi", "Valid expected impact string", 0.8),
        ];
        let result = validate_generated_moves(&moves, 5);
        assert!(result.is_err());
        let errors = result.unwrap_err();
        assert!(errors.iter().any(|e| e.contains("description too short")));
    }

    #[test]
    fn test_validate_generated_moves_short_expected_impact_rejects() {
        let moves = vec![
            make_move("positioning", "Valid description here", "short", 0.8),
        ];
        let result = validate_generated_moves(&moves, 5);
        assert!(result.is_err());
        let errors = result.unwrap_err();
        assert!(errors.iter().any(|e| e.contains("expected_impact too short")));
    }

    #[test]
    fn test_validate_generated_moves_confidence_low_rejects() {
        let moves = vec![
            make_move("positioning", "Valid description here", "Valid expected impact string", -0.1),
        ];
        let result = validate_generated_moves(&moves, 5);
        assert!(result.is_err());
        let errors = result.unwrap_err();
        assert!(errors.iter().any(|e| e.contains("confidence out of range")));
    }

    #[test]
    fn test_validate_generated_moves_confidence_high_rejects() {
        let moves = vec![
            make_move("positioning", "Valid description here", "Valid expected impact string", 1.5),
        ];
        let result = validate_generated_moves(&moves, 5);
        assert!(result.is_err());
        let errors = result.unwrap_err();
        assert!(errors.iter().any(|e| e.contains("confidence out of range")));
    }

    #[test]
    fn test_validate_generated_moves_mixed_valid_invalid_rejects_all() {
        let moves = vec![
            make_move("positioning", "Valid description here", "Valid expected impact string", 0.8),
            make_move("invalid_type", "Valid description here", "Valid expected impact string", 0.8),
        ];
        let result = validate_generated_moves(&moves, 5);
        assert!(result.is_err());
        let errors = result.unwrap_err();
        assert!(errors.len() == 1);
        assert!(errors[0].contains("invalid_type"));
    }

    #[test]
    fn test_validate_generated_moves_too_many_rejects() {
        let moves = vec![
            make_move("positioning", "Valid description here", "Valid expected impact string", 0.8),
            make_move("content", "Another valid description", "Another long expected impact string", 0.7),
            make_move("proof", "Yet another valid move", "This is a valid impact string", 0.6),
        ];
        let result = validate_generated_moves(&moves, 2);
        assert!(result.is_err());
        let errors = result.unwrap_err();
        assert!(errors.iter().any(|e| e.contains("exceeds max_moves")));
    }

    #[test]
    fn test_build_generated_move_inserts_sequence_numbers_increment() {
        let moves = vec![
            make_move("positioning", "First move description", "First expected impact string here", 0.8),
            make_move("content", "Second move description", "Second expected impact string here", 0.7),
            make_move("proof", "Third move description", "Third expected impact string here", 0.6),
        ];
        let inserts = build_generated_move_inserts(moves, 4);

        assert_eq!(inserts.len(), 3);
        assert_eq!(inserts[0].sequence_number, 4);
        assert_eq!(inserts[1].sequence_number, 5);
        assert_eq!(inserts[2].sequence_number, 6);
    }

    #[test]
    fn test_build_generated_move_inserts_body_contains_move_id_and_sequence() {
        let moves = vec![
            make_move("positioning", "Valid description here", "Valid expected impact string", 0.8),
        ];
        let inserts = build_generated_move_inserts(moves, 1);

        assert_eq!(inserts.len(), 1);
        let body = &inserts[0].content_body;
        assert!(body.get("move_id").is_some());
        assert!(body.get("sequence_number").is_some());
        assert!(body.get("description").is_some());
        assert!(body.get("expected_impact").is_some());
        assert!(body.get("confidence").is_some());

        let seq_in_body = body.get("sequence_number").and_then(|v| v.as_i64()).unwrap();
        assert_eq!(seq_in_body, 1);
    }
}
