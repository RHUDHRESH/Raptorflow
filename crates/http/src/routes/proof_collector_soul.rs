use axum::{Json, Router, extract::Extension, routing::post};
use serde::{Deserialize, Serialize};
use std::sync::Arc;

use crate::error::{AppResult, bad_request, internal_route_error};
use crate::middleware::AppState;
use raptorflow_auth::TenantContext;
use raptorflow_db::TenantDbPool;

#[derive(Debug, Deserialize)]
pub struct ProofCollectorDryRunRequest {
    pub task_summary: String,
    pub context_summary: String,
}

#[derive(Debug, Serialize)]
pub struct ProofCollectorSoulResponse {
    pub avatar_id: String,
    pub soul_id: String,
    pub created: bool,
    pub updated: bool,
}

#[derive(Debug, Serialize)]
pub struct ProofCollectorDryRunResponse {
    pub avatar_id: String,
    pub soul_id: String,
    pub embodiment_pack: raptorflow_harness::avatar_soul::AvatarEmbodimentPack,
    pub role_lock_prompt: String,
    pub instinct_frame: raptorflow_harness::avatar_soul::DerivedInstinctFrame,
    pub presence_state: Option<ProofCollectorPresenceResponse>,
    pub debate_event: Option<ProofCollectorDebateEventResponse>,
    pub proof_map: Option<ProofMapResponse>,
}

#[derive(Debug, Serialize)]
pub struct ProofCollectorPresenceResponse {
    pub presence_id: String,
    pub state: String,
    pub current_focus: String,
    pub current_concern: String,
    pub visible_summary: String,
    pub confidence: f64,
}

#[derive(Debug, Serialize)]
pub struct ProofCollectorDebateEventResponse {
    pub debate_event_id: String,
    pub event_type: String,
    pub stance: String,
    pub content: serde_json::Value,
    pub confidence: f64,
}

#[derive(Debug, Serialize)]
pub struct ProofMapResponse {
    pub known_facts: Vec<String>,
    pub claims: Vec<ClaimProofAssessmentResponse>,
    pub proof_gaps: Vec<String>,
    pub assets_to_collect: Vec<String>,
    pub unsafe_claims: Vec<String>,
    pub legal_review_flags: Vec<String>,
    pub ripple_candidates: Vec<String>,
}

#[derive(Debug, Serialize)]
pub struct ClaimProofAssessmentResponse {
    pub claim: String,
    pub proof_available: String,
    pub proof_type: String,
    pub proof_strength: String,
    pub source: String,
    pub permission_status: String,
    pub metric_context: MetricContextResponse,
    pub risk: String,
    pub recommended_action: String,
    pub safer_wording: String,
}

#[derive(Debug, Serialize)]
pub struct MetricContextResponse {
    pub source: String,
    pub time_window: String,
    pub baseline: String,
    pub sample_size: String,
}

pub fn router(state: Arc<AppState>) -> Router {
    Router::new()
        .route(
            "/api/v1/avatars/proof-collector/default",
            post(ensure_proof_collector_default),
        )
        .route(
            "/api/v1/avatars/proof-collector/dry-run",
            post(run_proof_collector_dry_run),
        )
        .layer(Extension(state))
}

pub async fn ensure_proof_collector_default(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
) -> AppResult<Json<serde_json::Value>> {
    let org_id = tenant.org_id;
    let pool = tenant_pool.pool();

    let result =
        raptorflow_harness::proof_collector_soul::ensure_proof_collector_soul(pool, org_id)
            .await
            .map_err(|e| {
                internal_route_error(
                    "ProofCollectorSoul route error",
                    "proof_collector_soul_internal_error",
                    e,
                )
            })?;

    Ok(Json(serde_json::json!({
        "avatar_id": result.avatar_id,
        "soul_id": result.soul_id,
        "created": result.created,
        "updated": result.updated
    })))
}

pub async fn run_proof_collector_dry_run(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Json(body): Json<ProofCollectorDryRunRequest>,
) -> AppResult<Json<serde_json::Value>> {
    let org_id = tenant.org_id;
    let pool = tenant_pool.pool();

    if body.task_summary.is_empty() {
        return Err(bad_request("task_summary is required"));
    }

    if body.context_summary.is_empty() {
        return Err(bad_request("context_summary is required"));
    }

    let input = raptorflow_harness::proof_collector_soul::ProofCollectorDryRunInput {
        task_summary: body.task_summary,
        context_summary: body.context_summary,
    };

    let result =
        raptorflow_harness::proof_collector_soul::run_proof_collector_dry_run(pool, org_id, input)
            .await
            .map_err(|e| {
                internal_route_error(
                    "ProofCollectorSoul route error",
                    "proof_collector_soul_internal_error",
                    e,
                )
            })?;

    let presence_state = result
        .presence_state
        .map(|p| ProofCollectorPresenceResponse {
            presence_id: p.presence_id,
            state: p.state,
            current_focus: p.current_focus,
            current_concern: p.current_concern,
            visible_summary: p.visible_summary,
            confidence: p.confidence,
        });

    let debate_event = result
        .debate_event
        .map(|e| ProofCollectorDebateEventResponse {
            debate_event_id: e.debate_event_id,
            event_type: e.event_type,
            stance: e.stance,
            content: e.content,
            confidence: e.confidence,
        });

    let proof_map = result.proof_map.map(|p| ProofMapResponse {
        known_facts: p.known_facts,
        claims: p
            .claims
            .into_iter()
            .map(|c| ClaimProofAssessmentResponse {
                claim: c.claim,
                proof_available: c.proof_available,
                proof_type: c.proof_type,
                proof_strength: c.proof_strength,
                source: c.source,
                permission_status: c.permission_status,
                metric_context: MetricContextResponse {
                    source: c.metric_context.source,
                    time_window: c.metric_context.time_window,
                    baseline: c.metric_context.baseline,
                    sample_size: c.metric_context.sample_size,
                },
                risk: c.risk,
                recommended_action: c.recommended_action,
                safer_wording: c.safer_wording,
            })
            .collect(),
        proof_gaps: p.proof_gaps,
        assets_to_collect: p.assets_to_collect,
        unsafe_claims: p.unsafe_claims,
        legal_review_flags: p.legal_review_flags,
        ripple_candidates: p.ripple_candidates,
    });

    Ok(Json(serde_json::json!({
        "avatar_id": result.avatar_id,
        "soul_id": result.soul_id,
        "embodiment_pack": result.embodiment_pack,
        "role_lock_prompt": result.role_lock_prompt,
        "instinct_frame": result.instinct_frame,
        "presence_state": presence_state,
        "debate_event": debate_event,
        "proof_map": proof_map,
    })))
}
