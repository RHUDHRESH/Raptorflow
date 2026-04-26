use axum::{
    Json, Router,
    extract::{Extension, Path, Query},
    http::StatusCode,
    routing::{get, post},
};
use serde::{Deserialize, Serialize};
use serde_json::{Value, json};
use std::sync::Arc;

use crate::middleware::AppState;
use raptorflow_auth::TenantContext;
use raptorflow_db::TenantDbPool;

type AppResult<T> = Result<T, (StatusCode, Json<Value>)>;

fn internal_error<E: std::fmt::Display>(e: E) -> (StatusCode, Json<Value>) {
    tracing::error!("CouncilOrchestration route error: {e}");
    (
        StatusCode::INTERNAL_SERVER_ERROR,
        Json(json!({ "error": "council_orchestration_internal_error" })),
    )
}

fn bad_request(msg: &str) -> (StatusCode, Json<Value>) {
    (StatusCode::BAD_REQUEST, Json(json!({ "error": msg })))
}

fn not_found(msg: &str) -> (StatusCode, Json<Value>) {
    (StatusCode::NOT_FOUND, Json(json!({ "error": msg })))
}

#[derive(Debug, Deserialize)]
pub struct CreateOrchestrationRequest {
    pub request_summary: String,
    pub context_summary: String,
    pub mode: Option<String>,
    pub requested_avatar_keys: Option<Vec<String>>,
    pub max_challenge_rounds: Option<usize>,
}

#[derive(Debug, Deserialize)]
pub struct ListOrchestrationsQuery {
    pub limit: Option<i64>,
}

#[derive(Debug, Serialize)]
pub struct CouncilOrchestrationResponse {
    pub council_run_id: String,
    pub harness_run_id: Option<String>,
    pub status: String,
    pub avatar_roster: Vec<String>,
    pub presence_states: Vec<PresenceStateResponse>,
    pub debate_events: Vec<DebateEventResponse>,
    pub synthesis: Value,
    pub turns: Vec<TurnResponse>,
}

#[derive(Debug, Serialize)]
pub struct PresenceStateResponse {
    pub presence_id: String,
    pub avatar_key: String,
    pub state: String,
    pub current_focus: String,
    pub current_concern: String,
    pub visible_summary: String,
    pub confidence: f64,
}

#[derive(Debug, Serialize)]
pub struct DebateEventResponse {
    pub debate_event_id: String,
    pub org_id: String,
    pub harness_run_id: Option<String>,
    pub speaker_avatar_id: Option<String>,
    pub target_avatar_id: Option<String>,
    pub event_type: String,
    pub stance: Option<String>,
    pub content: Value,
    pub confidence: f64,
    pub created_at: String,
}

#[derive(Debug, Serialize)]
pub struct TurnResponse {
    pub turn_id: String,
    pub avatar_key: String,
    pub turn_type: String,
    pub sequence_number: i32,
    pub status: String,
    pub instinct_frame: Option<Value>,
    pub debate_event: Option<DebateEventResponse>,
}

pub fn router(state: Arc<AppState>) -> Router {
    Router::new()
        .route("/", post(create_orchestration).get(list_orchestrations))
        .route("/{id}", get(get_orchestration))
        .route("/{id}/turns", get(list_orchestration_turns))
        .route("/{id}/presence", get(list_orchestration_presence))
        .route("/{id}/debate-events", get(list_orchestration_debate_events))
        .layer(Extension(state))
}

pub async fn create_orchestration(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Json(body): Json<CreateOrchestrationRequest>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;
    let pool = tenant_pool.pool();

    if body.request_summary.len() < 10 {
        return Err(bad_request(
            "request_summary must be at least 10 characters",
        ));
    }

    if body.request_summary.len() > 2000 {
        return Err(bad_request(
            "request_summary must be at most 2000 characters",
        ));
    }

    if body.context_summary.len() > 8000 {
        return Err(bad_request(
            "context_summary must be at most 8000 characters",
        ));
    }

    let mode = body.mode.unwrap_or_else(|| "dry_run".to_string());
    if mode != "dry_run" && mode != "draft" {
        return Err(bad_request("mode must be 'dry_run' or 'draft'"));
    }

    let max_challenge_rounds = body.max_challenge_rounds.unwrap_or(1);
    if max_challenge_rounds > 2 {
        return Err(bad_request("max_challenge_rounds must be 0, 1, or 2"));
    }

    let requested_avatar_keys = body.requested_avatar_keys.unwrap_or_default();
    let allowed_keys = [
        "strategist",
        "researcher",
        "copywriter",
        "growth_operator",
        "analyst",
        "creative_director",
        "proof_collector",
    ];
    for key in &requested_avatar_keys {
        if !allowed_keys.contains(&key.as_str()) {
            return Err(bad_request(&format!("Unknown avatar key: {}", key)));
        }
    }

    let input = raptorflow_harness::council_orchestrator::CouncilRunRequest {
        org_id,
        request_summary: body.request_summary,
        context_summary: body.context_summary,
        mode,
        requested_avatar_keys,
        max_challenge_rounds,
    };

    let result = raptorflow_harness::council_orchestrator::run_council_dry_run(pool, input)
        .await
        .map_err(|e| {
            tracing::error!("Council orchestration failed: {}", e);
            (
                StatusCode::INTERNAL_SERVER_ERROR,
                Json(json!({ "error": e.to_string() })),
            )
        })?;

    let debate_events: Vec<DebateEventResponse> = result
        .debate_events
        .into_iter()
        .map(|e| DebateEventResponse {
            debate_event_id: e.debate_event_id,
            org_id: e.org_id.to_string(),
            harness_run_id: Some(e.harness_run_id),
            speaker_avatar_id: e.speaker_avatar_id,
            target_avatar_id: e.target_avatar_id,
            event_type: e.event_type,
            stance: e.stance,
            content: e.content,
            confidence: e.confidence,
            created_at: e.created_at.to_rfc3339(),
        })
        .collect();

    let turns: Vec<TurnResponse> = result
        .turns
        .into_iter()
        .map(|t| TurnResponse {
            turn_id: t.turn_id,
            avatar_key: t.avatar_key,
            turn_type: t.turn_type,
            sequence_number: t.sequence_number,
            status: t.status,
            instinct_frame: t
                .instinct_frame
                .map(|f| serde_json::to_value(f).unwrap_or_default()),
            debate_event: None,
        })
        .collect();

    Ok(Json(json!({
        "council_run_id": result.council_run_id,
        "harness_run_id": result.harness_run_id,
        "status": result.status,
        "avatar_roster": result.avatar_roster,
        "presence_states": result.presence_states,
        "debate_events": debate_events,
        "synthesis": result.synthesis,
        "turns": turns,
    })))
}

pub async fn list_orchestrations(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Query(query): Query<ListOrchestrationsQuery>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;
    let pool = tenant_pool.pool();
    let limit = query.limit.unwrap_or(50).min(100);

    let runs = raptorflow_db::queries::list_council_orchestration_runs(pool, org_id, limit)
        .await
        .map_err(internal_error)?;

    Ok(Json(json!(runs)))
}

pub async fn get_orchestration(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(id): Path<String>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;
    let pool = tenant_pool.pool();

    let run = raptorflow_db::queries::get_council_orchestration_run(pool, &id, org_id)
        .await
        .map_err(internal_error)?
        .ok_or_else(|| not_found("Council orchestration run not found"))?;

    Ok(Json(json!(run)))
}

pub async fn list_orchestration_turns(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(id): Path<String>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;
    let pool = tenant_pool.pool();

    let _run = raptorflow_db::queries::get_council_orchestration_run(pool, &id, org_id)
        .await
        .map_err(internal_error)?
        .ok_or_else(|| not_found("Council orchestration run not found"))?;

    let turns = raptorflow_db::queries::list_council_avatar_turns(pool, &id, org_id)
        .await
        .map_err(internal_error)?;

    Ok(Json(json!(turns)))
}

pub async fn list_orchestration_presence(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(id): Path<String>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;
    let pool = tenant_pool.pool();

    let run = raptorflow_db::queries::get_council_orchestration_run(pool, &id, org_id)
        .await
        .map_err(internal_error)?
        .ok_or_else(|| not_found("Council orchestration run not found"))?;

    let harness_run_id = run.harness_run_id.unwrap_or_default();
    if harness_run_id.is_empty() {
        return Ok(Json(json!([])));
    }

    let presence = raptorflow_db::queries::list_harness_presence(pool, org_id, &harness_run_id)
        .await
        .map_err(internal_error)?;

    Ok(Json(json!(presence)))
}

pub async fn list_orchestration_debate_events(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(id): Path<String>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;
    let pool = tenant_pool.pool();

    let run = raptorflow_db::queries::get_council_orchestration_run(pool, &id, org_id)
        .await
        .map_err(internal_error)?
        .ok_or_else(|| not_found("Council orchestration run not found"))?;

    let harness_run_id = run.harness_run_id.unwrap_or_default();
    if harness_run_id.is_empty() {
        return Ok(Json(json!([])));
    }

    let events = raptorflow_db::queries::list_debate_events(pool, org_id, &harness_run_id)
        .await
        .map_err(internal_error)?;

    Ok(Json(json!(events)))
}
