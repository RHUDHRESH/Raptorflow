use axum::{Json, Router, extract::Extension, http::StatusCode, routing::post};
use serde::{Deserialize, Serialize};
use std::sync::Arc;

use crate::middleware::AppState;
use raptorflow_auth::TenantContext;
use raptorflow_db::TenantDbPool;

type AppResult<T> = Result<T, (StatusCode, Json<serde_json::Value>)>;

fn internal_error<E: std::fmt::Display>(e: E) -> (StatusCode, Json<serde_json::Value>) {
    tracing::error!("CreativeDirectorSoul route error: {e}");
    (
        StatusCode::INTERNAL_SERVER_ERROR,
        Json(serde_json::json!({ "error": "creative_director_soul_internal_error" })),
    )
}

fn bad_request(msg: &str) -> (StatusCode, Json<serde_json::Value>) {
    (
        StatusCode::BAD_REQUEST,
        Json(serde_json::json!({ "error": msg })),
    )
}

#[derive(Debug, Deserialize)]
pub struct CreativeDirectorDryRunRequest {
    pub task_summary: String,
    pub context_summary: String,
}

#[derive(Debug, Serialize)]
pub struct CreativeDirectorSoulResponse {
    pub avatar_id: String,
    pub soul_id: String,
    pub created: bool,
    pub updated: bool,
}

#[derive(Debug, Serialize)]
pub struct CreativeDirectorDryRunResponse {
    pub avatar_id: String,
    pub soul_id: String,
    pub embodiment_pack: raptorflow_harness::avatar_soul::AvatarEmbodimentPack,
    pub role_lock_prompt: String,
    pub instinct_frame: raptorflow_harness::avatar_soul::DerivedInstinctFrame,
    pub presence_state: Option<CreativeDirectorPresenceResponse>,
    pub debate_event: Option<CreativeDirectorDebateEventResponse>,
    pub creative_review: Option<CreativeQualityReviewResponse>,
}

#[derive(Debug, Serialize)]
pub struct CreativeDirectorPresenceResponse {
    pub presence_id: String,
    pub state: String,
    pub current_focus: String,
    pub current_concern: String,
    pub visible_summary: String,
    pub confidence: f64,
}

#[derive(Debug, Serialize)]
pub struct CreativeDirectorDebateEventResponse {
    pub debate_event_id: String,
    pub event_type: String,
    pub stance: String,
    pub content: serde_json::Value,
    pub confidence: f64,
}

#[derive(Debug, Serialize)]
pub struct CreativeQualityReviewResponse {
    pub aesthetic_quality: AestheticQualityResponse,
    pub brand_consistency: BrandConsistencyResponse,
    pub emotional_resonance: EmotionalResonanceResponse,
    pub message_clarity: MessageClarityResponse,
    pub creative_risk: CreativeRiskResponse,
    pub overall_verdict: String,
    pub recommended_action: String,
    pub open_questions: Vec<String>,
}

#[derive(Debug, Serialize)]
pub struct AestheticQualityResponse {
    pub visual_hierarchy_clear: bool,
    pub design_unity: bool,
    pub first_impression_score: u8,
    pub quality_concerns: Vec<String>,
    pub strengths: Vec<String>,
}

#[derive(Debug, Serialize)]
pub struct BrandConsistencyResponse {
    pub voice_consistent: bool,
    pub tone_appropriate: bool,
    pub brand_values_aligned: bool,
    pub consistency_score: u8,
    pub deviations: Vec<String>,
}

#[derive(Debug, Serialize)]
pub struct EmotionalResonanceResponse {
    pub has_emotional_hook: bool,
    pub audience_empathy_present: bool,
    pub resonance_level: String,
    pub emotional_tone: String,
    pub concerns: Vec<String>,
}

#[derive(Debug, Serialize)]
pub struct MessageClarityResponse {
    pub primary_message_clear: bool,
    pub cta_visible: bool,
    pub cta_compelling: bool,
    pub hierarchy_clarity_score: u8,
    pub confusion_points: Vec<String>,
}

#[derive(Debug, Serialize)]
pub struct CreativeRiskResponse {
    pub risk_level: String,
    pub audience_tolerance_appropriate: bool,
    pub differentiation_achieved: bool,
    pub risk_concerns: Vec<String>,
}

pub fn router(state: Arc<AppState>) -> Router {
    Router::new()
        .route(
            "/api/v1/avatars/creative-director/default",
            post(ensure_creative_director_default),
        )
        .route(
            "/api/v1/avatars/creative-director/dry-run",
            post(run_creative_director_dry_run),
        )
        .layer(Extension(state))
}

pub async fn ensure_creative_director_default(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
) -> AppResult<Json<serde_json::Value>> {
    let org_id = tenant.org_id;
    let pool = tenant_pool.pool();

    let result =
        raptorflow_harness::creative_director_soul::ensure_creative_director_soul(pool, org_id)
            .await
            .map_err(internal_error)?;

    Ok(Json(serde_json::json!({
        "avatar_id": result.avatar_id,
        "soul_id": result.soul_id,
        "created": result.created,
        "updated": result.updated
    })))
}

pub async fn run_creative_director_dry_run(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Json(body): Json<CreativeDirectorDryRunRequest>,
) -> AppResult<Json<serde_json::Value>> {
    let org_id = tenant.org_id;
    let pool = tenant_pool.pool();

    if body.task_summary.is_empty() {
        return Err(bad_request("task_summary is required"));
    }

    if body.context_summary.is_empty() {
        return Err(bad_request("context_summary is required"));
    }

    let input = raptorflow_harness::creative_director_soul::CreativeDirectorDryRunInput {
        task_summary: body.task_summary,
        context_summary: body.context_summary,
    };

    let result = raptorflow_harness::creative_director_soul::run_creative_director_dry_run(
        pool, org_id, input,
    )
    .await
    .map_err(internal_error)?;

    let presence_state = result
        .presence_state
        .map(|p| CreativeDirectorPresenceResponse {
            presence_id: p.presence_id,
            state: p.state,
            current_focus: p.current_focus,
            current_concern: p.current_concern,
            visible_summary: p.visible_summary,
            confidence: p.confidence,
        });

    let debate_event = result
        .debate_event
        .map(|e| CreativeDirectorDebateEventResponse {
            debate_event_id: e.debate_event_id,
            event_type: e.event_type,
            stance: e.stance,
            content: e.content,
            confidence: e.confidence,
        });

    let creative_review = result
        .creative_review
        .map(|r| CreativeQualityReviewResponse {
            aesthetic_quality: AestheticQualityResponse {
                visual_hierarchy_clear: r.aesthetic_quality.visual_hierarchy_clear,
                design_unity: r.aesthetic_quality.design_unity,
                first_impression_score: r.aesthetic_quality.first_impression_score,
                quality_concerns: r.aesthetic_quality.quality_concerns,
                strengths: r.aesthetic_quality.strengths,
            },
            brand_consistency: BrandConsistencyResponse {
                voice_consistent: r.brand_consistency.voice_consistent,
                tone_appropriate: r.brand_consistency.tone_appropriate,
                brand_values_aligned: r.brand_consistency.brand_values_aligned,
                consistency_score: r.brand_consistency.consistency_score,
                deviations: r.brand_consistency.deviations,
            },
            emotional_resonance: EmotionalResonanceResponse {
                has_emotional_hook: r.emotional_resonance.has_emotional_hook,
                audience_empathy_present: r.emotional_resonance.audience_empathy_present,
                resonance_level: r.emotional_resonance.resonance_level,
                emotional_tone: r.emotional_resonance.emotional_tone,
                concerns: r.emotional_resonance.concerns,
            },
            message_clarity: MessageClarityResponse {
                primary_message_clear: r.message_clarity.primary_message_clear,
                cta_visible: r.message_clarity.cta_visible,
                cta_compelling: r.message_clarity.cta_compelling,
                hierarchy_clarity_score: r.message_clarity.hierarchy_clarity_score,
                confusion_points: r.message_clarity.confusion_points,
            },
            creative_risk: CreativeRiskResponse {
                risk_level: r.creative_risk.risk_level,
                audience_tolerance_appropriate: r.creative_risk.audience_tolerance_appropriate,
                differentiation_achieved: r.creative_risk.differentiation_achieved,
                risk_concerns: r.creative_risk.risk_concerns,
            },
            overall_verdict: r.overall_verdict,
            recommended_action: r.recommended_action,
            open_questions: r.open_questions,
        });

    Ok(Json(serde_json::json!({
        "avatar_id": result.avatar_id,
        "soul_id": result.soul_id,
        "embodiment_pack": result.embodiment_pack,
        "role_lock_prompt": result.role_lock_prompt,
        "instinct_frame": result.instinct_frame,
        "presence_state": presence_state,
        "debate_event": debate_event,
        "creative_review": creative_review
    })))
}
