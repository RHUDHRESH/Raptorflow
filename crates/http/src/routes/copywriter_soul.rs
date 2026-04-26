use axum::{Json, Router, extract::Extension, http::StatusCode, routing::post};
use serde::{Deserialize, Serialize};
use serde_json::{Value, json};
use std::sync::Arc;

use crate::middleware::AppState;
use raptorflow_auth::TenantContext;
use raptorflow_db::TenantDbPool;

type AppResult<T> = Result<T, (StatusCode, Json<Value>)>;

fn internal_error<E: std::fmt::Display>(e: E) -> (StatusCode, Json<Value>) {
    tracing::error!("CopywriterSoul route error: {e}");
    (
        StatusCode::INTERNAL_SERVER_ERROR,
        Json(json!({ "error": "copywriter_soul_internal_error" })),
    )
}

fn bad_request(msg: &str) -> (StatusCode, Json<Value>) {
    (StatusCode::BAD_REQUEST, Json(json!({ "error": msg })))
}

#[derive(Debug, Deserialize)]
pub struct CopywriterDryRunRequest {
    pub task_summary: String,
    pub context_summary: String,
    pub copy_draft: Option<String>,
}

#[derive(Debug, Serialize)]
pub struct CopywriterSoulResponse {
    pub avatar_id: String,
    pub soul_id: String,
    pub created: bool,
    pub updated: bool,
}

#[derive(Debug, Serialize)]
pub struct CopywriterDryRunResponse {
    pub avatar_id: String,
    pub soul_id: String,
    pub embodiment_pack: raptorflow_harness::avatar_soul::AvatarEmbodimentPack,
    pub role_lock_prompt: String,
    pub instinct_frame: raptorflow_harness::avatar_soul::DerivedInstinctFrame,
    pub presence_state: Option<CopywriterPresenceResponse>,
    pub debate_event: Option<CopywriterDebateEventResponse>,
    pub copy_audit: Option<CopywriterCopyAuditResponse>,
}

#[derive(Debug, Serialize)]
pub struct CopywriterPresenceResponse {
    pub presence_id: String,
    pub state: String,
    pub current_focus: String,
    pub current_concern: String,
    pub visible_summary: String,
    pub confidence: f64,
}

#[derive(Debug, Serialize)]
pub struct CopywriterDebateEventResponse {
    pub debate_event_id: String,
    pub event_type: String,
    pub stance: String,
    pub content: Value,
    pub confidence: f64,
}

#[derive(Debug, Serialize)]
pub struct CopywriterCopyAuditResponse {
    pub copy_elements: Vec<CopyElementAnalysisResponse>,
    pub proof_claims: Vec<ProofClaimAnalysisResponse>,
    pub generic_risk_flags: Vec<String>,
    pub hook_assessment: HookAssessmentResponse,
    pub cta_assessment: CtaAssessmentResponse,
    pub voice_assessment: VoiceAssessmentResponse,
    pub open_questions: Vec<String>,
}

#[derive(Debug, Serialize)]
pub struct CopyElementAnalysisResponse {
    pub element: String,
    pub element_type: String,
    pub assessment: String,
    pub risk_level: String,
    pub recommended_action: String,
}

#[derive(Debug, Serialize)]
pub struct ProofClaimAnalysisResponse {
    pub claim: String,
    pub has_evidence: bool,
    pub evidence_quality: String,
    pub safer_language: String,
}

#[derive(Debug, Serialize)]
pub struct HookAssessmentResponse {
    pub has_hook: bool,
    pub hook_clarity: String,
    pub icp_specific: bool,
    pub risk_flags: Vec<String>,
}

#[derive(Debug, Serialize)]
pub struct CtaAssessmentResponse {
    pub has_cta: bool,
    pub cta_specificity: String,
    pub cta_actionability: String,
    pub risk_flags: Vec<String>,
}

#[derive(Debug, Serialize)]
pub struct VoiceAssessmentResponse {
    pub voice_consistent: bool,
    pub icp_voice_match: bool,
    pub tone: String,
    pub risk_flags: Vec<String>,
}

pub fn router(state: Arc<AppState>) -> Router {
    Router::new()
        .route(
            "/api/v1/avatars/copywriter/default",
            post(ensure_copywriter_default),
        )
        .route(
            "/api/v1/avatars/copywriter/dry-run",
            post(run_copywriter_dry_run),
        )
        .layer(Extension(state))
}

pub async fn ensure_copywriter_default(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;
    let pool = tenant_pool.pool();

    let result = raptorflow_harness::copywriter_soul::ensure_copywriter_soul(pool, org_id)
        .await
        .map_err(internal_error)?;

    Ok(Json(json!({
        "avatar_id": result.avatar_id,
        "soul_id": result.soul_id,
        "created": result.created,
        "updated": result.updated
    })))
}

pub async fn run_copywriter_dry_run(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Json(body): Json<CopywriterDryRunRequest>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;
    let pool = tenant_pool.pool();

    if body.task_summary.is_empty() {
        return Err(bad_request("task_summary is required"));
    }

    if body.context_summary.is_empty() {
        return Err(bad_request("context_summary is required"));
    }

    let input = raptorflow_harness::copywriter_soul::CopywriterDryRunInput {
        task_summary: body.task_summary,
        context_summary: body.context_summary,
        copy_draft: body.copy_draft,
    };

    let result = raptorflow_harness::copywriter_soul::run_copywriter_dry_run(pool, org_id, input)
        .await
        .map_err(internal_error)?;

    let presence_state = result.presence_state.map(|p| CopywriterPresenceResponse {
        presence_id: p.presence_id,
        state: p.state,
        current_focus: p.current_focus,
        current_concern: p.current_concern,
        visible_summary: p.visible_summary,
        confidence: p.confidence,
    });

    let debate_event = result.debate_event.map(|e| CopywriterDebateEventResponse {
        debate_event_id: e.debate_event_id,
        event_type: e.event_type,
        stance: e.stance,
        content: e.content,
        confidence: e.confidence,
    });

    let copy_audit = result.copy_audit.map(|a| CopywriterCopyAuditResponse {
        copy_elements: a
            .copy_elements
            .into_iter()
            .map(|c| CopyElementAnalysisResponse {
                element: c.element,
                element_type: c.element_type,
                assessment: c.assessment,
                risk_level: c.risk_level,
                recommended_action: c.recommended_action,
            })
            .collect(),
        proof_claims: a
            .proof_claims
            .into_iter()
            .map(|c| ProofClaimAnalysisResponse {
                claim: c.claim,
                has_evidence: c.has_evidence,
                evidence_quality: c.evidence_quality,
                safer_language: c.safer_language,
            })
            .collect(),
        generic_risk_flags: a.generic_risk_flags,
        hook_assessment: HookAssessmentResponse {
            has_hook: a.hook_assessment.has_hook,
            hook_clarity: a.hook_assessment.hook_clarity,
            icp_specific: a.hook_assessment.icp_specific,
            risk_flags: a.hook_assessment.risk_flags,
        },
        cta_assessment: CtaAssessmentResponse {
            has_cta: a.cta_assessment.has_cta,
            cta_specificity: a.cta_assessment.cta_specificity,
            cta_actionability: a.cta_assessment.cta_actionability,
            risk_flags: a.cta_assessment.risk_flags,
        },
        voice_assessment: VoiceAssessmentResponse {
            voice_consistent: a.voice_assessment.voice_consistent,
            icp_voice_match: a.voice_assessment.icp_voice_match,
            tone: a.voice_assessment.tone,
            risk_flags: a.voice_assessment.risk_flags,
        },
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
        "copy_audit": copy_audit
    })))
}
