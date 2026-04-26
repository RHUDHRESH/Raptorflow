use axum::{Json, Router, extract::Extension, http::StatusCode, routing::post};
use serde::{Deserialize, Serialize};
use serde_json::{Value, json};
use std::sync::Arc;

use crate::middleware::AppState;
use raptorflow_auth::TenantContext;
use raptorflow_db::TenantDbPool;

type AppResult<T> = Result<T, (StatusCode, Json<Value>)>;

fn internal_error<E: std::fmt::Display>(e: E) -> (StatusCode, Json<Value>) {
    tracing::error!("GrowthOperatorSoul route error: {e}");
    (
        StatusCode::INTERNAL_SERVER_ERROR,
        Json(json!({ "error": "growth_operator_soul_internal_error" })),
    )
}

fn bad_request(msg: &str) -> (StatusCode, Json<Value>) {
    (StatusCode::BAD_REQUEST, Json(json!({ "error": msg })))
}

#[derive(Debug, Deserialize)]
pub struct GrowthOperatorDryRunRequest {
    pub task_summary: String,
    pub context_summary: String,
    pub move_draft: Option<String>,
}

#[derive(Debug, Serialize)]
pub struct GrowthOperatorSoulResponse {
    pub avatar_id: String,
    pub soul_id: String,
    pub created: bool,
    pub updated: bool,
}

#[derive(Debug, Serialize)]
pub struct GrowthOperatorDryRunResponse {
    pub avatar_id: String,
    pub soul_id: String,
    pub embodiment_pack: raptorflow_harness::avatar_soul::AvatarEmbodimentPack,
    pub role_lock_prompt: String,
    pub instinct_frame: raptorflow_harness::avatar_soul::DerivedInstinctFrame,
    pub presence_state: Option<GrowthOperatorPresenceResponse>,
    pub debate_event: Option<GrowthOperatorDebateEventResponse>,
    pub execution_audit: Option<GrowthOperatorExecutionAuditResponse>,
}

#[derive(Debug, Serialize)]
pub struct GrowthOperatorPresenceResponse {
    pub presence_id: String,
    pub state: String,
    pub current_focus: String,
    pub current_concern: String,
    pub visible_summary: String,
    pub confidence: f64,
}

#[derive(Debug, Serialize)]
pub struct GrowthOperatorDebateEventResponse {
    pub debate_event_id: String,
    pub event_type: String,
    pub stance: String,
    pub content: Value,
    pub confidence: f64,
}

#[derive(Debug, Serialize)]
pub struct GrowthOperatorExecutionAuditResponse {
    pub move_analysis: Vec<MoveAnalysisResponse>,
    pub cadence_assessment: CadenceAssessmentResponse,
    pub channel_coordination: ChannelCoordinationAssessmentResponse,
    pub feedback_loops: FeedbackLoopAssessmentResponse,
    pub velocity_signals: VelocityAssessmentResponse,
    pub open_questions: Vec<String>,
}

#[derive(Debug, Serialize)]
pub struct MoveAnalysisResponse {
    pub move_name: String,
    pub has_owner: bool,
    pub has_deadline: bool,
    pub has_success_signal: bool,
    pub sequencing_justified: bool,
    pub risk_level: String,
    pub recommended_action: String,
}

#[derive(Debug, Serialize)]
pub struct CadenceAssessmentResponse {
    pub has_rhythm: bool,
    pub cadence_quality: String,
    pub consistency_score: f64,
    pub risk_flags: Vec<String>,
}

#[derive(Debug, Serialize)]
pub struct ChannelCoordinationAssessmentResponse {
    pub multi_channel: bool,
    pub coordination_quality: String,
    pub handoff_explicit: bool,
    pub risk_flags: Vec<String>,
}

#[derive(Debug, Serialize)]
pub struct FeedbackLoopAssessmentResponse {
    pub has_feedback_tracking: bool,
    pub adaptation_triggers_defined: bool,
    pub loop_quality: String,
    pub risk_flags: Vec<String>,
}

#[derive(Debug, Serialize)]
pub struct VelocityAssessmentResponse {
    pub has_velocity_tracking: bool,
    pub velocity_defined: bool,
    pub measurement_quality: String,
    pub risk_flags: Vec<String>,
}

pub fn router(state: Arc<AppState>) -> Router {
    Router::new()
        .route(
            "/api/v1/avatars/growth-operator/default",
            post(ensure_growth_operator_default),
        )
        .route(
            "/api/v1/avatars/growth-operator/dry-run",
            post(run_growth_operator_dry_run),
        )
        .layer(Extension(state))
}

pub async fn ensure_growth_operator_default(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;
    let pool = tenant_pool.pool();

    let result =
        raptorflow_harness::growth_operator_soul::ensure_growth_operator_soul(pool, org_id)
            .await
            .map_err(internal_error)?;

    Ok(Json(json!({
        "avatar_id": result.avatar_id,
        "soul_id": result.soul_id,
        "created": result.created,
        "updated": result.updated
    })))
}

pub async fn run_growth_operator_dry_run(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Json(body): Json<GrowthOperatorDryRunRequest>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;
    let pool = tenant_pool.pool();

    if body.task_summary.is_empty() {
        return Err(bad_request("task_summary is required"));
    }

    if body.context_summary.is_empty() {
        return Err(bad_request("context_summary is required"));
    }

    let input = raptorflow_harness::growth_operator_soul::GrowthOperatorDryRunInput {
        task_summary: body.task_summary,
        context_summary: body.context_summary,
        move_draft: body.move_draft,
    };

    let result =
        raptorflow_harness::growth_operator_soul::run_growth_operator_dry_run(pool, org_id, input)
            .await
            .map_err(internal_error)?;

    let presence_state = result
        .presence_state
        .map(|p| GrowthOperatorPresenceResponse {
            presence_id: p.presence_id,
            state: p.state,
            current_focus: p.current_focus,
            current_concern: p.current_concern,
            visible_summary: p.visible_summary,
            confidence: p.confidence,
        });

    let debate_event = result
        .debate_event
        .map(|e| GrowthOperatorDebateEventResponse {
            debate_event_id: e.debate_event_id,
            event_type: e.event_type,
            stance: e.stance,
            content: e.content,
            confidence: e.confidence,
        });

    let execution_audit = result
        .execution_audit
        .map(|a| GrowthOperatorExecutionAuditResponse {
            move_analysis: a
                .move_analysis
                .into_iter()
                .map(|m| MoveAnalysisResponse {
                    move_name: m.move_name,
                    has_owner: m.has_owner,
                    has_deadline: m.has_deadline,
                    has_success_signal: m.has_success_signal,
                    sequencing_justified: m.sequencing_justified,
                    risk_level: m.risk_level,
                    recommended_action: m.recommended_action,
                })
                .collect(),
            cadence_assessment: CadenceAssessmentResponse {
                has_rhythm: a.cadence_assessment.has_rhythm,
                cadence_quality: a.cadence_assessment.cadence_quality,
                consistency_score: a.cadence_assessment.consistency_score,
                risk_flags: a.cadence_assessment.risk_flags,
            },
            channel_coordination: ChannelCoordinationAssessmentResponse {
                multi_channel: a.channel_coordination.multi_channel,
                coordination_quality: a.channel_coordination.coordination_quality,
                handoff_explicit: a.channel_coordination.handoff_explicit,
                risk_flags: a.channel_coordination.risk_flags,
            },
            feedback_loops: FeedbackLoopAssessmentResponse {
                has_feedback_tracking: a.feedback_loops.has_feedback_tracking,
                adaptation_triggers_defined: a.feedback_loops.adaptation_triggers_defined,
                loop_quality: a.feedback_loops.loop_quality,
                risk_flags: a.feedback_loops.risk_flags,
            },
            velocity_signals: VelocityAssessmentResponse {
                has_velocity_tracking: a.velocity_signals.has_velocity_tracking,
                velocity_defined: a.velocity_signals.velocity_defined,
                measurement_quality: a.velocity_signals.measurement_quality,
                risk_flags: a.velocity_signals.risk_flags,
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
        "execution_audit": execution_audit
    })))
}
