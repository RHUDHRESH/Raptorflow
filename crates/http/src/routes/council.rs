use axum::{
    Json, Router,
    extract::{Extension, Path},
    http::StatusCode,
    response::sse::{Event, Sse},
    routing::{get, post},
};
use futures_util::stream;
use serde::{Deserialize, Serialize};
use serde_json::{Value, json};
use std::sync::Arc;
use ulid::Ulid;

use raptorflow_auth::TenantContext;
use raptorflow_aws::bedrock::BedrockInferenceClient;
use raptorflow_db::models::{CouncilAgentPosition, CouncilSession};
use raptorflow_db::{TenantDbPool, queries};

use super::ai_helpers::{json_error, parse_ai_json, truncate_context};

pub fn router() -> Router {
    Router::new()
        .route("/", post(start_session).get(list_sessions))
        .route("/{session_id}", get(get_session))
        .route("/{session_id}/messages", get(get_session_messages))
}

type AppResult<T> = Result<T, (StatusCode, Json<Value>)>;
type CouncilSseResponse =
    Sse<stream::Iter<std::vec::IntoIter<Result<Event, std::convert::Infallible>>>>;

fn internal_error<E: std::fmt::Display>(e: E) -> (StatusCode, Json<Value>) {
    tracing::error!("Council route error: {e}");
    (
        StatusCode::INTERNAL_SERVER_ERROR,
        Json(json!({ "error": "council_internal_error" })),
    )
}

fn bad_request(msg: &str) -> (StatusCode, Json<Value>) {
    (StatusCode::BAD_REQUEST, Json(json!({ "error": msg })))
}

fn not_found(msg: &str) -> (StatusCode, Json<Value>) {
    (StatusCode::NOT_FOUND, Json(json!({ "error": msg })))
}

#[derive(Debug, Deserialize)]
pub struct StartSessionRequest {
    pub campaign_id: Option<String>,
    pub agent_roster: Vec<String>,
    pub question: String,
    pub session_type: Option<String>,
}

#[derive(Debug, Serialize)]
pub struct SessionResponse {
    pub session_id: String,
    pub org_id: String,
    pub campaign_id: Option<String>,
    pub session_type: String,
    pub status: String,
    pub question: String,
    pub total_cost_usd: f64,
    pub created_at: String,
}

impl From<CouncilSession> for SessionResponse {
    fn from(s: CouncilSession) -> Self {
        Self {
            session_id: s.session_id,
            org_id: s.org_id.to_string(),
            campaign_id: s.campaign_id,
            session_type: s.session_type,
            status: s.status,
            question: s.question,
            total_cost_usd: s.total_cost_usd,
            created_at: s.created_at.to_rfc3339(),
        }
    }
}

#[derive(Debug, Serialize)]
pub struct PositionResponse {
    pub position_id: String,
    pub avatar_key: String,
    pub round_number: i32,
    pub content: String,
    pub extracted_ripple_data: serde_json::Value,
    pub created_at: String,
}

impl From<CouncilAgentPosition> for PositionResponse {
    fn from(p: CouncilAgentPosition) -> Self {
        Self {
            position_id: p.position_id,
            avatar_key: p.avatar_key,
            round_number: p.round_number,
            content: p.content,
            extracted_ripple_data: p.extracted_ripple_data,
            created_at: p.created_at.to_rfc3339(),
        }
    }
}

pub async fn start_session(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Json(req): Json<StartSessionRequest>,
) -> AppResult<Json<Value>> {
    if req.question.trim().is_empty() {
        return Err(bad_request("question_required"));
    }

    let org_id = tenant.org_id;
    let session_id = Ulid::new().to_string();
    let session_type = req.session_type.as_deref().unwrap_or("deliberation");

    queries::create_council_session(
        &tenant_pool.pool(),
        &session_id,
        org_id,
        req.campaign_id.as_deref(),
        session_type,
        &req.question,
    )
    .await
    .map_err(internal_error)?;

    let session = queries::get_council_session(&tenant_pool.pool(), &session_id, org_id)
        .await
        .map_err(internal_error)?;

    match session {
        Some(s) => Ok(Json(json!({
            "session": SessionResponse::from(s),
            "status": "created"
        }))),
        None => Err(internal_error("session_not_found_after_create")),
    }
}

pub async fn list_sessions(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;

    let sessions = queries::list_council_sessions(&tenant_pool.pool(), org_id)
        .await
        .map_err(internal_error)?;

    let list: Vec<SessionResponse> = sessions.into_iter().map(Into::into).collect();

    Ok(Json(json!({
        "sessions": list,
        "total": list.len(),
        "status": "ok"
    })))
}

pub async fn get_session(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(session_id): Path<String>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;

    let session = queries::get_council_session(&tenant_pool.pool(), &session_id, org_id)
        .await
        .map_err(internal_error)?;

    match session {
        Some(s) => {
            let positions = queries::list_agent_positions(&tenant_pool.pool(), &session_id, org_id)
                .await
                .map_err(internal_error)?;

            Ok(Json(json!({
                "session": SessionResponse::from(s),
                "positions": positions.into_iter().map(Into::into).collect::<Vec<PositionResponse>>(),
                "status": "ok"
            })))
        }
        None => Err(not_found("session_not_found")),
    }
}

pub async fn get_session_messages(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(session_id): Path<String>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;

    let session = queries::get_council_session(&tenant_pool.pool(), &session_id, org_id)
        .await
        .map_err(internal_error)?;

    if session.is_none() {
        return Err(not_found("session_not_found"));
    }

    let positions = queries::list_agent_positions(&tenant_pool.pool(), &session_id, org_id)
        .await
        .map_err(internal_error)?;

    Ok(Json(json!({
        "session_id": session_id,
        "positions": positions.into_iter().map(Into::into).collect::<Vec<PositionResponse>>(),
        "status": "ok"
    })))
}

fn service_unavailable() -> (StatusCode, Json<Value>) {
    (
        StatusCode::SERVICE_UNAVAILABLE,
        Json(json_error("ai_inference_unavailable")),
    )
}

#[derive(Debug, Deserialize)]
pub struct StartCouncilRequest {
    pub agent_roster: Option<Vec<String>>,
    pub max_agents: Option<i32>,
}

const DEFAULT_ROSTER: &[&str] = &[
    "strategist",
    "growth_operator",
    "copywriter",
    "researcher",
    "analyst",
];

#[derive(Debug, Deserialize, Serialize)]
struct AiPosition {
    position: String,
    confidence: f64,
    key_risks: Vec<String>,
    recommended_next_move: String,
    ripple_candidates: Vec<RippleCandidate>,
}

#[derive(Debug, Deserialize, Serialize)]
struct RippleCandidate {
    summary: String,
    salience: f64,
    r#type: String,
}

pub async fn start_council_session(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Extension(bedrock): Extension<Option<Arc<BedrockInferenceClient>>>,
    Path(session_id): Path<String>,
    Json(req): Json<StartCouncilRequest>,
) -> AppResult<Json<Value>> {
    let bedrock = bedrock.ok_or_else(service_unavailable)?;
    let org_id = tenant.org_id;

    let session = queries::get_council_session(&tenant_pool.pool(), &session_id, org_id)
        .await
        .map_err(internal_error)?;
    let session = session.ok_or_else(|| not_found("session_not_found"))?;

    if session.question.is_empty() {
        return Err(bad_request("session_question_empty"));
    }

    queries::update_council_session_status(&tenant_pool.pool(), &session_id, org_id, "running")
        .await
        .map_err(internal_error)?;

    let mut roster: Vec<String> = req.agent_roster.unwrap_or_default();
    if roster.is_empty() {
        roster = DEFAULT_ROSTER.iter().map(|s| s.to_string()).collect();
    }
    let max_agents = req.max_agents.unwrap_or(5).min(6).max(1);
    roster.truncate(max_agents as usize);

    let mut positions = Vec::new();
    let mut has_failure = false;

    for avatar_key in &roster {
        let prompt = format!(
            "You are the {} avatar in a strategic council session.\n\
            Session topic: {}\n\
            Provide your position as a JSON object with:\n\
            {{\"position\": \"your detailed position (min 20 chars)\", \"confidence\": 0.0-1.0, \"key_risks\": [\"risk1\", \"risk2\"], \"recommended_next_move\": \"concrete next step\", \"ripple_candidates\": [{{\"summary\": \"observation\", \"salience\": 0.0-1.0, \"type\": \"observation|insight|concern\"}}]}}\n\
            Return ONLY valid JSON, no markdown fences or explanation.",
            avatar_key,
            truncate_context(&session.question, 500)
        );

        let output = match bedrock.converse_large(&prompt, 600).await {
            Ok(o) => o,
            Err(e) => {
                tracing::warn!("Bedrock call failed for avatar {}: {}", avatar_key, e);
                has_failure = true;
                continue;
            }
        };

        let ai_pos: AiPosition = match parse_ai_json(&output) {
            Ok(p) => p,
            Err(e) => {
                tracing::warn!("Failed to parse AI output for avatar {}: {}", avatar_key, e);
                has_failure = true;
                continue;
            }
        };

        if ai_pos.position.len() < 20 {
            tracing::warn!("Position too short for avatar {}", avatar_key);
            has_failure = true;
            continue;
        }

        if ai_pos.key_risks.len() > 10 {
            tracing::warn!("Too many key_risks for avatar {}", avatar_key);
            has_failure = true;
            continue;
        }

        if ai_pos.ripple_candidates.len() > 10 {
            tracing::warn!("Too many ripple_candidates for avatar {}", avatar_key);
            has_failure = true;
            continue;
        }

        for rc in &ai_pos.ripple_candidates {
            if rc.summary.trim().is_empty() {
                tracing::warn!("Empty ripple_candidate summary for avatar {}", avatar_key);
                has_failure = true;
                continue;
            }
        }

        let _confidence = ai_pos.confidence.clamp(0.0, 1.0);
        let ripple_data = serde_json::json!({
            "key_risks": ai_pos.key_risks,
            "recommended_next_move": ai_pos.recommended_next_move,
            "ripple_candidates": ai_pos.ripple_candidates,
        });

        let position_id = Ulid::new().to_string();
        if let Err(e) = queries::create_agent_position(
            &tenant_pool.pool(),
            &position_id,
            org_id,
            &session_id,
            avatar_key,
            1,
            &ai_pos.position,
            &ripple_data,
        )
        .await
        {
            tracing::error!("Failed to store position for {}: {}", avatar_key, e);
            has_failure = true;
            continue;
        }

        positions.push(json!({
            "position_id": position_id,
            "avatar_key": avatar_key,
            "round_number": 1,
            "content": ai_pos.position,
            "extracted_ripple_data": ripple_data,
            "created_at": chrono::Utc::now().to_rfc3339(),
        }));
    }

    if positions.is_empty() {
        queries::update_council_session_status(&tenant_pool.pool(), &session_id, org_id, "failed")
            .await
            .map_err(internal_error)?;
        return Err((
            StatusCode::BAD_GATEWAY,
            Json(json_error("all_avatar_generation_failed")),
        ));
    }

    let final_status = if has_failure {
        "partial"
    } else {
        "positions_ready"
    };
    queries::update_council_session_status(&tenant_pool.pool(), &session_id, org_id, final_status)
        .await
        .map_err(internal_error)?;

    Ok(Json(json!({
        "session_id": session_id,
        "status": final_status,
        "positions": positions,
    })))
}

pub async fn stream_council_session(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(session_id): Path<String>,
) -> AppResult<CouncilSseResponse> {
    let org_id = tenant.org_id;

    let session = queries::get_council_session(&tenant_pool.pool(), &session_id, org_id)
        .await
        .map_err(internal_error)?;

    if session.is_none() {
        return Err(not_found("session_not_found"));
    }
    let session = session.unwrap();

    let positions = queries::list_agent_positions(&tenant_pool.pool(), &session_id, org_id)
        .await
        .map_err(internal_error)?;

    let mut events: Vec<Result<Event, std::convert::Infallible>> = Vec::new();

    events.push(Ok(Event::default().event("session").data(
        serde_json::to_string(&json!({
            "session_id": session_id,
            "status": session.status,
        }))
        .unwrap_or_default(),
    )));

    for pos in &positions {
        events.push(Ok(Event::default().event("position").data(
            serde_json::to_string(&json!({
                "position_id": pos.position_id,
                "avatar_key": pos.avatar_key,
                "content": pos.content,
            }))
            .unwrap_or_default(),
        )));
    }

    events.push(Ok(Event::default().event("done").data(
        serde_json::to_string(&json!({
            "session_id": session_id,
            "status": session.status,
        }))
        .unwrap_or_default(),
    )));

    Ok(Sse::new(stream::iter(events)))
}

#[derive(Debug, Deserialize)]
pub struct SynthesizeRequest {
    pub focus: Option<String>,
}

#[derive(Debug, Deserialize, Serialize)]
struct AiSynthesis {
    decision: String,
    rationale: String,
    risks: Vec<String>,
    next_actions: Vec<String>,
    participating_agents: Vec<String>,
    confidence: f64,
}

pub async fn synthesize_council_session(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Extension(bedrock): Extension<Option<Arc<BedrockInferenceClient>>>,
    Path(session_id): Path<String>,
    Json(_req): Json<SynthesizeRequest>,
) -> AppResult<Json<Value>> {
    let bedrock = bedrock.ok_or_else(service_unavailable)?;
    let org_id = tenant.org_id;

    let session = queries::get_council_session(&tenant_pool.pool(), &session_id, org_id)
        .await
        .map_err(internal_error)?;
    let session = session.ok_or_else(|| not_found("session_not_found"))?;

    let positions = queries::list_agent_positions(&tenant_pool.pool(), &session_id, org_id)
        .await
        .map_err(internal_error)?;

    if positions.len() < 2 {
        return Err(bad_request("not_enough_positions"));
    }

    let positions_text: String = positions
        .iter()
        .map(|p| {
            format!(
                "- {} ({}): {}\n  Risks: {:?}\n  Next: {}\n",
                p.avatar_key,
                p.round_number,
                p.content,
                p.extracted_ripple_data
                    .get("key_risks")
                    .and_then(|v| v.as_array())
                    .map(|arr| arr.iter().filter_map(|x| x.as_str()).collect::<Vec<_>>())
                    .unwrap_or_default(),
                p.extracted_ripple_data
                    .get("recommended_next_move")
                    .and_then(|v| v.as_str())
                    .unwrap_or("N/A")
            )
        })
        .collect::<Vec<_>>()
        .join("\n\n");

    let prompt = format!(
        "Council session topic: {}\n\nAgent positions:\n{}\n\n\
        Synthesize these positions into a strategic decision as JSON:\n\
        {{\"decision\": \"clear strategic decision\", \"rationale\": \"why this decision\", \
        \"risks\": [\"risk1\", \"risk2\"], \"next_actions\": [\"action1\", \"action2\"], \
        \"participating_agents\": [\"agent1\", \"agent2\"], \"confidence\": 0.0-1.0}}\n\
        Return ONLY valid JSON.",
        truncate_context(&session.question, 300),
        truncate_context(&positions_text, 2000)
    );

    let output = bedrock.converse_large(&prompt, 800).await.map_err(|e| {
        tracing::error!("Synthesis Bedrock call failed: {}", e);
        (
            StatusCode::BAD_GATEWAY,
            Json(json_error("ai_inference_failed")),
        )
    })?;

    let ai_synth: AiSynthesis = parse_ai_json(&output).map_err(|e| {
        tracing::error!("Synthesis parse failed: {}", e);
        (
            StatusCode::BAD_GATEWAY,
            Json(json_error("invalid_ai_output")),
        )
    })?;

    if ai_synth.decision.len() < 10 || ai_synth.rationale.len() < 20 {
        return Err((
            StatusCode::BAD_GATEWAY,
            Json(json_error("invalid_ai_output")),
        ));
    }

    if ai_synth.risks.len() > 10 {
        tracing::warn!("Synthesis has too many risks: {}", ai_synth.risks.len());
        return Err((
            StatusCode::BAD_GATEWAY,
            Json(json_error("invalid_ai_output")),
        ));
    }

    if ai_synth.next_actions.len() > 10 {
        tracing::warn!(
            "Synthesis has too many next_actions: {}",
            ai_synth.next_actions.len()
        );
        return Err((
            StatusCode::BAD_GATEWAY,
            Json(json_error("invalid_ai_output")),
        ));
    }

    if ai_synth.confidence < 0.0 || ai_synth.confidence > 1.0 {
        tracing::warn!("Synthesis confidence out of range: {}", ai_synth.confidence);
        return Err((
            StatusCode::BAD_GATEWAY,
            Json(json_error("invalid_ai_output")),
        ));
    }

    let synthesis_body = serde_json::json!({
        "session_id": session_id,
        "decision": ai_synth.decision,
        "rationale": ai_synth.rationale,
        "risks": ai_synth.risks,
        "next_actions": ai_synth.next_actions,
        "participating_agents": ai_synth.participating_agents,
        "confidence": ai_synth.confidence.clamp(0.0, 1.0),
    });

    let content_id = Ulid::new().to_string();
    queries::create_generated_content(
        &tenant_pool.pool(),
        &content_id,
        org_id,
        session.campaign_id.as_deref(),
        None,
        "council_synthesis",
        "generated",
        &synthesis_body,
    )
    .await
    .map_err(internal_error)?;

    queries::update_council_session_status(&tenant_pool.pool(), &session_id, org_id, "synthesized")
        .await
        .map_err(internal_error)?;

    Ok(Json(json!({
        "session_id": session_id,
        "status": "synthesized",
        "synthesis": {
            "decision": ai_synth.decision,
            "rationale": ai_synth.rationale,
            "risks": ai_synth.risks,
            "next_actions": ai_synth.next_actions,
            "participating_agents": ai_synth.participating_agents,
        }
    })))
}
