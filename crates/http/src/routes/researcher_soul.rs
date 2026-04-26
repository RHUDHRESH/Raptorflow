use axum::{Json, Router, extract::Extension, http::StatusCode, routing::post};
use serde::{Deserialize, Serialize};
use serde_json::{Value, json};
use std::sync::Arc;

use crate::middleware::AppState;
use raptorflow_auth::TenantContext;
use raptorflow_db::TenantDbPool;

type AppResult<T> = Result<T, (StatusCode, Json<Value>)>;

fn internal_error<E: std::fmt::Display>(e: E) -> (StatusCode, Json<Value>) {
    tracing::error!("ResearcherSoul route error: {e}");
    (
        StatusCode::INTERNAL_SERVER_ERROR,
        Json(json!({ "error": "researcher_soul_internal_error" })),
    )
}

fn bad_request(msg: &str) -> (StatusCode, Json<Value>) {
    (StatusCode::BAD_REQUEST, Json(json!({ "error": msg })))
}

#[derive(Debug, Deserialize)]
pub struct ResearcherDryRunRequest {
    pub task_summary: String,
    pub context_summary: String,
}

#[derive(Debug, Serialize)]
pub struct ResearcherSoulResponse {
    pub avatar_id: String,
    pub soul_id: String,
    pub created: bool,
    pub updated: bool,
}

#[derive(Debug, Serialize)]
pub struct ResearcherDryRunResponse {
    pub avatar_id: String,
    pub soul_id: String,
    pub embodiment_pack: raptorflow_harness::avatar_soul::AvatarEmbodimentPack,
    pub role_lock_prompt: String,
    pub instinct_frame: raptorflow_harness::avatar_soul::DerivedInstinctFrame,
    pub presence_state: Option<ResearcherPresenceResponse>,
    pub debate_event: Option<ResearcherDebateEventResponse>,
    pub claim_audit: Option<ResearcherClaimAuditResponse>,
}

#[derive(Debug, Serialize)]
pub struct ResearcherPresenceResponse {
    pub presence_id: String,
    pub state: String,
    pub current_focus: String,
    pub current_concern: String,
    pub visible_summary: String,
    pub confidence: f64,
}

#[derive(Debug, Serialize)]
pub struct ResearcherDebateEventResponse {
    pub debate_event_id: String,
    pub event_type: String,
    pub stance: String,
    pub content: Value,
    pub confidence: f64,
}

#[derive(Debug, Serialize)]
pub struct ResearcherClaimAuditResponse {
    pub known_facts: Vec<String>,
    pub claims: Vec<ClaimAnalysisResponse>,
    pub unsupported_claims: Vec<String>,
    pub assumptions: Vec<String>,
    pub needed_sources: Vec<String>,
    pub competitor_notes: Vec<String>,
    pub open_questions: Vec<String>,
}

#[derive(Debug, Serialize)]
pub struct ClaimAnalysisResponse {
    pub claim: String,
    pub evidence_level: String,
    pub source: String,
    pub risk: String,
    pub recommended_action: String,
    pub safer_rewrite: String,
}

pub fn router(state: Arc<AppState>) -> Router {
    Router::new()
        .route(
            "/api/v1/avatars/researcher/default",
            post(ensure_researcher_default),
        )
        .route(
            "/api/v1/avatars/researcher/dry-run",
            post(run_researcher_dry_run),
        )
        .layer(Extension(state))
}

pub async fn ensure_researcher_default(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;
    let pool = tenant_pool.pool();

    let result = raptorflow_harness::researcher_soul::ensure_researcher_soul(pool, org_id)
        .await
        .map_err(internal_error)?;

    Ok(Json(json!({
        "avatar_id": result.avatar_id,
        "soul_id": result.soul_id,
        "created": result.created,
        "updated": result.updated
    })))
}

pub async fn run_researcher_dry_run(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Json(body): Json<ResearcherDryRunRequest>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;
    let pool = tenant_pool.pool();

    if body.task_summary.is_empty() {
        return Err(bad_request("task_summary is required"));
    }

    if body.context_summary.is_empty() {
        return Err(bad_request("context_summary is required"));
    }

    let input = raptorflow_harness::researcher_soul::ResearcherDryRunInput {
        task_summary: body.task_summary,
        context_summary: body.context_summary,
    };

    let result = raptorflow_harness::researcher_soul::run_researcher_dry_run(pool, org_id, input)
        .await
        .map_err(internal_error)?;

    let presence_state = result.presence_state.map(|p| ResearcherPresenceResponse {
        presence_id: p.presence_id,
        state: p.state,
        current_focus: p.current_focus,
        current_concern: p.current_concern,
        visible_summary: p.visible_summary,
        confidence: p.confidence,
    });

    let debate_event = result.debate_event.map(|e| ResearcherDebateEventResponse {
        debate_event_id: e.debate_event_id,
        event_type: e.event_type,
        stance: e.stance,
        content: e.content,
        confidence: e.confidence,
    });

    let claim_audit = result.claim_audit.map(|a| ResearcherClaimAuditResponse {
        known_facts: a.known_facts,
        claims: a
            .claims
            .into_iter()
            .map(|c| ClaimAnalysisResponse {
                claim: c.claim,
                evidence_level: c.evidence_level,
                source: c.source,
                risk: c.risk,
                recommended_action: c.recommended_action,
                safer_rewrite: c.safer_rewrite,
            })
            .collect(),
        unsupported_claims: a.unsupported_claims,
        assumptions: a.assumptions,
        needed_sources: a.needed_sources,
        competitor_notes: a.competitor_notes,
        open_questions: a.open_questions,
    });

    Ok(Json(json!({
        "avatar_id": result.avatar_id,
        "soul_id": result.soul_id,
        "embodiment_pack": result.embodiment_pack,
        "role_lock_prompt": result.role_lock_prompt,
        "instinct_frame": result.instinct_frame,
        "presence_state": presence_state,
        "debate_event": debate_event,
        "claim_audit": claim_audit
    })))
}
