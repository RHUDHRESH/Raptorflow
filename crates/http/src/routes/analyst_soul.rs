use axum::{Json, Router, extract::Extension, http::StatusCode, routing::post};
use serde::{Deserialize, Serialize};
use std::sync::Arc;

use crate::middleware::AppState;
use raptorflow_auth::TenantContext;
use raptorflow_db::TenantDbPool;

type AppResult<T> = Result<T, (StatusCode, Json<serde_json::Value>)>;

fn internal_error<E: std::fmt::Display>(e: E) -> (StatusCode, Json<serde_json::Value>) {
    tracing::error!("AnalystSoul route error: {e}");
    (
        StatusCode::INTERNAL_SERVER_ERROR,
        Json(serde_json::json!({ "error": "analyst_soul_internal_error" })),
    )
}

fn bad_request(msg: &str) -> (StatusCode, Json<serde_json::Value>) {
    (
        StatusCode::BAD_REQUEST,
        Json(serde_json::json!({ "error": msg })),
    )
}

#[derive(Debug, Deserialize)]
pub struct AnalystDryRunRequest {
    pub task_summary: String,
    pub context_summary: String,
}

#[derive(Debug, Serialize)]
pub struct AnalystSoulResponse {
    pub avatar_id: String,
    pub soul_id: String,
    pub created: bool,
    pub updated: bool,
}

#[derive(Debug, Serialize)]
pub struct AnalystDryRunResponse {
    pub avatar_id: String,
    pub soul_id: String,
    pub embodiment_pack: raptorflow_harness::avatar_soul::AvatarEmbodimentPack,
    pub role_lock_prompt: String,
    pub instinct_frame: raptorflow_harness::avatar_soul::DerivedInstinctFrame,
    pub presence_state: Option<AnalystPresenceResponse>,
    pub debate_event: Option<AnalystDebateEventResponse>,
    pub signal_quality_review: Option<AnalystSignalQualityReviewResponse>,
}

#[derive(Debug, Serialize)]
pub struct AnalystPresenceResponse {
    pub presence_id: String,
    pub state: String,
    pub current_focus: String,
    pub current_concern: String,
    pub visible_summary: String,
    pub confidence: f64,
}

#[derive(Debug, Serialize)]
pub struct AnalystDebateEventResponse {
    pub debate_event_id: String,
    pub event_type: String,
    pub stance: String,
    pub content: serde_json::Value,
    pub confidence: f64,
}

#[derive(Debug, Serialize)]
pub struct AnalystSignalQualityReviewResponse {
    pub known_facts: Vec<String>,
    pub metrics: Vec<MetricAnalysisResponse>,
    pub vanity_metrics: Vec<String>,
    pub missing_metrics: Vec<String>,
    pub attribution_limits: Vec<String>,
    pub recommended_decision: String,
    pub next_test: String,
    pub open_questions: Vec<String>,
}

#[derive(Debug, Serialize)]
pub struct MetricAnalysisResponse {
    pub metric_name: String,
    pub metric_type: String,
    pub value_summary: String,
    pub source: String,
    pub baseline: String,
    pub sample_size: String,
    pub signal_strength: String,
    pub decision_usefulness: String,
    pub risk: String,
}

pub fn router(state: Arc<AppState>) -> Router {
    Router::new()
        .route(
            "/api/v1/avatars/analyst/default",
            post(ensure_analyst_default),
        )
        .route("/api/v1/avatars/analyst/dry-run", post(run_analyst_dry_run))
        .layer(Extension(state))
}

pub async fn ensure_analyst_default(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
) -> AppResult<Json<serde_json::Value>> {
    let org_id = tenant.org_id;
    let pool = tenant_pool.pool();

    let result = raptorflow_harness::analyst_soul::ensure_analyst_soul(pool, org_id)
        .await
        .map_err(internal_error)?;

    Ok(Json(serde_json::json!({
        "avatar_id": result.avatar_id,
        "soul_id": result.soul_id,
        "created": result.created,
        "updated": result.updated
    })))
}

pub async fn run_analyst_dry_run(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Json(body): Json<AnalystDryRunRequest>,
) -> AppResult<Json<serde_json::Value>> {
    let org_id = tenant.org_id;
    let pool = tenant_pool.pool();

    if body.task_summary.is_empty() {
        return Err(bad_request("task_summary is required"));
    }

    if body.context_summary.is_empty() {
        return Err(bad_request("context_summary is required"));
    }

    let input = raptorflow_harness::analyst_soul::AnalystDryRunInput {
        task_summary: body.task_summary,
        context_summary: body.context_summary,
    };

    let result = raptorflow_harness::analyst_soul::run_analyst_dry_run(pool, org_id, input)
        .await
        .map_err(internal_error)?;

    let presence_state = result.presence_state.map(|p| AnalystPresenceResponse {
        presence_id: p.presence_id,
        state: p.state,
        current_focus: p.current_focus,
        current_concern: p.current_concern,
        visible_summary: p.visible_summary,
        confidence: p.confidence,
    });

    let debate_event = result.debate_event.map(|e| AnalystDebateEventResponse {
        debate_event_id: e.debate_event_id,
        event_type: e.event_type,
        stance: e.stance,
        content: e.content,
        confidence: e.confidence,
    });

    let signal_quality_review =
        result
            .signal_quality_review
            .map(|r| AnalystSignalQualityReviewResponse {
                known_facts: r.known_facts,
                metrics: r
                    .metrics
                    .into_iter()
                    .map(|m| MetricAnalysisResponse {
                        metric_name: m.metric_name,
                        metric_type: m.metric_type,
                        value_summary: m.value_summary,
                        source: m.source,
                        baseline: m.baseline,
                        sample_size: m.sample_size,
                        signal_strength: m.signal_strength,
                        decision_usefulness: m.decision_usefulness,
                        risk: m.risk,
                    })
                    .collect(),
                vanity_metrics: r.vanity_metrics,
                missing_metrics: r.missing_metrics,
                attribution_limits: r.attribution_limits,
                recommended_decision: r.recommended_decision,
                next_test: r.next_test,
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
        "signal_quality_review": signal_quality_review
    })))
}
