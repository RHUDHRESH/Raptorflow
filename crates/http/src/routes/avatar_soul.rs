use axum::{
    Json, Router,
    extract::{Extension, Path},
    http::StatusCode,
    routing::{delete, get, post},
};
use serde::{Deserialize, Serialize};
use serde_json::{Value, json};
use std::sync::Arc;

use crate::middleware::AppState;
use raptorflow_auth::TenantContext;
use raptorflow_db::TenantDbPool;
use raptorflow_db::queries as db;

type AppResult<T> = Result<T, (StatusCode, Json<Value>)>;

fn internal_error<E: std::fmt::Display>(e: E) -> (StatusCode, Json<Value>) {
    tracing::error!("AvatarSoul route error: {e}");
    (
        StatusCode::INTERNAL_SERVER_ERROR,
        Json(json!({ "error": "avatar_soul_internal_error" })),
    )
}

fn not_found(msg: &str) -> (StatusCode, Json<Value>) {
    (StatusCode::NOT_FOUND, Json(json!({ "error": msg })))
}

fn bad_request(msg: &str) -> (StatusCode, Json<Value>) {
    (StatusCode::BAD_REQUEST, Json(json!({ "error": msg })))
}

fn validate_salience(salience: f64) -> AppResult<()> {
    if !(0.0..=1.0).contains(&salience) {
        return Err(bad_request("salience must be between 0.0 and 1.0"));
    }
    Ok(())
}

fn validate_confidence(confidence: f64) -> AppResult<()> {
    if !(0.0..=1.0).contains(&confidence) {
        return Err(bad_request("confidence must be between 0.0 and 1.0"));
    }
    Ok(())
}

fn validate_json_size(value: &Value, max_bytes: usize, field_name: &str) -> AppResult<()> {
    let serialized = serde_json::to_string(value).map_err(|_| bad_request("invalid json"))?;
    if serialized.len() > max_bytes {
        return Err(bad_request(&format!(
            "{} exceeds max size of {} bytes",
            field_name, max_bytes
        )));
    }
    Ok(())
}

const VALID_RELATIONSHIP_TYPES: [&str; 5] = [
    "preference",
    "learned",
    "contextual",
    "critical",
    "structural",
];
const VALID_DECAY_POLICIES: [&str; 4] = ["none", "normal", "exponential", "linear"];
const VALID_EVENT_TYPES: [&str; 7] = [
    "position",
    "challenge",
    "evidence",
    "refinement",
    "support",
    "oppose",
    "question",
];
const VALID_STATES: [&str; 7] = [
    "idle",
    "thinking",
    "posing",
    "challenging",
    "responding",
    "done",
    "blocked",
];
const VALID_EMBODIMENT_LEVELS: [&str; 4] = ["minimal", "partial", "deep", "full"];

#[derive(Debug, Serialize)]
pub struct AvatarSoulResponse {
    pub soul_id: String,
    pub avatar_id: String,
    pub identity_kernel: Value,
    pub worldview: Value,
    pub obsessions: Value,
    pub reflexes: Value,
    pub taboos: Value,
    pub debate_style: Value,
    pub embodiment_level: String,
    pub operating_principles: Value,
    pub evaluation_bias: Value,
    pub is_active: bool,
    pub created_at: String,
    pub updated_at: String,
}

impl From<raptorflow_db::models::AvatarSoul> for AvatarSoulResponse {
    fn from(s: raptorflow_db::models::AvatarSoul) -> Self {
        Self {
            soul_id: s.soul_id,
            avatar_id: s.avatar_id,
            identity_kernel: s.identity_kernel,
            worldview: s.worldview,
            obsessions: s.obsessions,
            reflexes: s.reflexes,
            taboos: s.taboos,
            debate_style: s.debate_style,
            embodiment_level: s.embodiment_level,
            operating_principles: s.operating_principles,
            evaluation_bias: s.evaluation_bias,
            is_active: s.is_active,
            created_at: s.created_at.to_rfc3339(),
            updated_at: s.updated_at.to_rfc3339(),
        }
    }
}

#[derive(Debug, Serialize)]
pub struct AvatarMemoryEdgeResponse {
    pub memory_edge_id: String,
    pub avatar_id: String,
    pub ripple_id: String,
    pub relationship_type: String,
    pub salience: f64,
    pub decay_policy: String,
    pub use_when: String,
    pub last_used_at: Option<String>,
    pub created_at: String,
}

impl From<raptorflow_db::models::AvatarMemoryEdge> for AvatarMemoryEdgeResponse {
    fn from(e: raptorflow_db::models::AvatarMemoryEdge) -> Self {
        Self {
            memory_edge_id: e.memory_edge_id,
            avatar_id: e.avatar_id,
            ripple_id: e.ripple_id,
            relationship_type: e.relationship_type,
            salience: e.salience,
            decay_policy: e.decay_policy,
            use_when: e.use_when,
            last_used_at: e.last_used_at.map(|t| t.to_rfc3339()),
            created_at: e.created_at.to_rfc3339(),
        }
    }
}

#[derive(Debug, Serialize)]
pub struct AvatarInstinctFrameResponse {
    pub instinct_frame_id: String,
    pub avatar_id: String,
    pub harness_run_id: Option<String>,
    pub capability_run_id: Option<String>,
    pub trigger_kind: String,
    pub dominant_concern: String,
    pub risk_flags: Value,
    pub recommended_posture: String,
    pub visible_summary: String,
    pub created_at: String,
}

impl From<raptorflow_db::models::AvatarInstinctFrame> for AvatarInstinctFrameResponse {
    fn from(f: raptorflow_db::models::AvatarInstinctFrame) -> Self {
        Self {
            instinct_frame_id: f.instinct_frame_id,
            avatar_id: f.avatar_id,
            harness_run_id: f.harness_run_id,
            capability_run_id: f.capability_run_id,
            trigger_kind: f.trigger_kind,
            dominant_concern: f.dominant_concern,
            risk_flags: f.risk_flags,
            recommended_posture: f.recommended_posture,
            visible_summary: f.visible_summary,
            created_at: f.created_at.to_rfc3339(),
        }
    }
}

#[derive(Debug, Serialize)]
pub struct AvatarPresenceStateResponse {
    pub presence_id: String,
    pub avatar_id: String,
    pub harness_run_id: Option<String>,
    pub state: String,
    pub current_focus: String,
    pub current_concern: String,
    pub confidence: f64,
    pub visible_summary: String,
    pub last_event_id: Option<String>,
    pub updated_at: String,
}

impl From<raptorflow_db::models::AvatarPresenceState> for AvatarPresenceStateResponse {
    fn from(p: raptorflow_db::models::AvatarPresenceState) -> Self {
        Self {
            presence_id: p.presence_id,
            avatar_id: p.avatar_id,
            harness_run_id: p.harness_run_id,
            state: p.state,
            current_focus: p.current_focus,
            current_concern: p.current_concern,
            confidence: p.confidence,
            visible_summary: p.visible_summary,
            last_event_id: p.last_event_id,
            updated_at: p.updated_at.to_rfc3339(),
        }
    }
}

#[derive(Debug, Serialize)]
pub struct AvatarDebateEventResponse {
    pub debate_event_id: String,
    pub harness_run_id: String,
    pub speaker_avatar_id: Option<String>,
    pub target_avatar_id: Option<String>,
    pub event_type: String,
    pub stance: Option<String>,
    pub content: Value,
    pub confidence: f64,
    pub created_at: String,
}

impl From<raptorflow_db::models::AvatarDebateEvent> for AvatarDebateEventResponse {
    fn from(e: raptorflow_db::models::AvatarDebateEvent) -> Self {
        Self {
            debate_event_id: e.debate_event_id,
            harness_run_id: e.harness_run_id,
            speaker_avatar_id: e.speaker_avatar_id,
            target_avatar_id: e.target_avatar_id,
            event_type: e.event_type,
            stance: e.stance,
            content: e.content,
            confidence: e.confidence,
            created_at: e.created_at.to_rfc3339(),
        }
    }
}

#[derive(Debug, Serialize)]
pub struct AvatarArtifactTrailResponse {
    pub trail_id: String,
    pub avatar_id: String,
    pub artifact_id: String,
    pub harness_run_id: Option<String>,
    pub contribution_type: String,
    pub summary: String,
    pub created_at: String,
}

impl From<raptorflow_db::models::AvatarArtifactTrail> for AvatarArtifactTrailResponse {
    fn from(t: raptorflow_db::models::AvatarArtifactTrail) -> Self {
        Self {
            trail_id: t.trail_id,
            avatar_id: t.avatar_id,
            artifact_id: t.artifact_id,
            harness_run_id: t.harness_run_id,
            contribution_type: t.contribution_type,
            summary: t.summary,
            created_at: t.created_at.to_rfc3339(),
        }
    }
}

#[derive(Debug, Deserialize)]
pub struct UpdateAvatarSoulRequest {
    pub identity_kernel: Option<Value>,
    pub worldview: Option<Value>,
    pub obsessions: Option<Value>,
    pub reflexes: Option<Value>,
    pub taboos: Option<Value>,
    pub debate_style: Option<Value>,
    pub embodiment_level: Option<String>,
    pub operating_principles: Option<Value>,
    pub evaluation_bias: Option<Value>,
    pub is_active: Option<bool>,
}

#[derive(Debug, Deserialize)]
pub struct CreateMemoryEdgeRequest {
    pub ripple_id: String,
    pub relationship_type: String,
    pub salience: f64,
    #[serde(default = "default_decay_policy")]
    pub decay_policy: String,
    pub use_when: String,
}

fn default_decay_policy() -> String {
    "exponential".to_string()
}

#[derive(Debug, Deserialize)]
pub struct CreateInstinctFrameRequest {
    pub avatar_id: String,
    pub harness_run_id: Option<String>,
    pub capability_run_id: Option<String>,
    pub trigger_kind: String,
    pub dominant_concern: String,
    pub risk_flags: Value,
    pub recommended_posture: String,
    pub visible_summary: String,
    #[serde(default)]
    pub private_notes: Value,
}

#[derive(Debug, Deserialize)]
pub struct UpsertPresenceStateRequest {
    pub avatar_id: String,
    pub state: String,
    pub current_focus: String,
    pub current_concern: String,
    pub confidence: f64,
    pub visible_summary: String,
    pub last_event_id: Option<String>,
}

#[derive(Debug, Deserialize)]
pub struct CreateDebateEventRequest {
    pub speaker_avatar_id: Option<String>,
    pub target_avatar_id: Option<String>,
    pub event_type: String,
    pub stance: Option<String>,
    pub content: Value,
    pub confidence: f64,
}

pub fn router(state: Arc<AppState>) -> Router {
    Router::new()
        .route(
            "/api/v1/avatars/{id}/soul",
            get(get_avatar_soul).put(update_avatar_soul),
        )
        .route(
            "/api/v1/avatars/{id}/memory/edges",
            get(list_memory_edges).post(create_memory_edge),
        )
        .route(
            "/api/v1/avatars/{id}/memory/edges/{edge_id}",
            delete(delete_memory_edge),
        )
        .route(
            "/api/v1/avatars/{id}/instinct-frame",
            post(create_instinct_frame),
        )
        .route(
            "/api/v1/harness/runs/{id}/presence",
            get(list_presence_states).post(upsert_presence_state),
        )
        .route(
            "/api/v1/harness/runs/{id}/debate-events",
            get(list_debate_events).post(create_debate_event),
        )
        .route(
            "/api/v1/avatars/{id}/artifact-trail",
            get(get_artifact_trail),
        )
        .layer(Extension(state))
}

pub async fn get_avatar_soul(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(avatar_id): Path<String>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;
    let pool = tenant_pool.pool();

    let soul = db::get_avatar_soul(pool, org_id, &avatar_id)
        .await
        .map_err(internal_error)?
        .ok_or_else(|| not_found("avatar_soul_not_found"))?;

    Ok(Json(json!({ "soul": AvatarSoulResponse::from(soul) })))
}

pub async fn update_avatar_soul(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(avatar_id): Path<String>,
    Json(body): Json<UpdateAvatarSoulRequest>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;
    let pool = tenant_pool.pool();

    let existing = db::get_avatar_soul(pool, org_id, &avatar_id)
        .await
        .map_err(internal_error)?;

    let soul_id = existing
        .map(|s| s.soul_id)
        .unwrap_or_else(|| uuid::Uuid::new_v4().to_string());

    let identity_kernel = body.identity_kernel.unwrap_or(json!({}));
    let worldview = body.worldview.unwrap_or(json!({}));
    let obsessions = body.obsessions.unwrap_or(json!({}));
    let reflexes = body.reflexes.unwrap_or(json!({}));
    let taboos = body.taboos.unwrap_or(json!({}));
    let debate_style = body.debate_style.unwrap_or(json!({}));
    let embodiment_level = body
        .embodiment_level
        .unwrap_or_else(|| "partial".to_string());
    let operating_principles = body.operating_principles.unwrap_or(json!({}));
    let evaluation_bias = body.evaluation_bias.unwrap_or(json!({}));

    if !VALID_EMBODIMENT_LEVELS.contains(&embodiment_level.as_str()) {
        return Err(bad_request(
            "embodiment_level must be one of: minimal, partial, deep, full",
        ));
    }

    validate_json_size(&identity_kernel, 10000, "identity_kernel")?;
    validate_json_size(&worldview, 5000, "worldview")?;
    validate_json_size(&obsessions, 5000, "obsessions")?;
    validate_json_size(&reflexes, 5000, "reflexes")?;
    validate_json_size(&taboos, 5000, "taboos")?;
    validate_json_size(&debate_style, 5000, "debate_style")?;
    validate_json_size(&operating_principles, 5000, "operating_principles")?;
    validate_json_size(&evaluation_bias, 5000, "evaluation_bias")?;

    db::upsert_avatar_soul(
        pool,
        &soul_id,
        org_id,
        &avatar_id,
        &identity_kernel,
        &worldview,
        &obsessions,
        &reflexes,
        &taboos,
        &debate_style,
        &embodiment_level,
        &operating_principles,
        &evaluation_bias,
    )
    .await
    .map_err(internal_error)?;

    let soul = db::get_avatar_soul(pool, org_id, &avatar_id)
        .await
        .map_err(internal_error)?
        .ok_or_else(|| internal_error("soul not found after upsert"))?;

    Ok(Json(json!({ "soul": AvatarSoulResponse::from(soul) })))
}

pub async fn list_memory_edges(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(avatar_id): Path<String>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;
    let pool = tenant_pool.pool();

    let edges = db::list_avatar_memory_edges(pool, org_id, &avatar_id)
        .await
        .map_err(internal_error)?;

    let response: Vec<AvatarMemoryEdgeResponse> = edges
        .into_iter()
        .map(AvatarMemoryEdgeResponse::from)
        .collect();

    Ok(Json(json!({ "memory_edges": response })))
}

pub async fn create_memory_edge(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(avatar_id): Path<String>,
    Json(body): Json<CreateMemoryEdgeRequest>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;
    let pool = tenant_pool.pool();

    if body.ripple_id.is_empty() {
        return Err(bad_request("ripple_id is required"));
    }

    if body.relationship_type.is_empty() {
        return Err(bad_request("relationship_type is required"));
    }

    validate_salience(body.salience)?;

    if !VALID_RELATIONSHIP_TYPES.contains(&body.relationship_type.as_str()) {
        return Err(bad_request(
            "relationship_type must be one of: preference, learned, contextual, critical, structural",
        ));
    }

    if !VALID_DECAY_POLICIES.contains(&body.decay_policy.as_str()) {
        return Err(bad_request(
            "decay_policy must be one of: none, normal, exponential, linear",
        ));
    }

    if body.use_when.len() > 1000 {
        return Err(bad_request(
            "use_when exceeds max length of 1000 characters",
        ));
    }

    let memory_edge_id = uuid::Uuid::new_v4().to_string();

    db::create_avatar_memory_edge(
        pool,
        &memory_edge_id,
        org_id,
        &avatar_id,
        &body.ripple_id,
        &body.relationship_type,
        body.salience,
        &body.decay_policy,
        &body.use_when,
    )
    .await
    .map_err(internal_error)?;

    let edges = db::list_avatar_memory_edges(pool, org_id, &avatar_id)
        .await
        .map_err(internal_error)?;

    let edge = edges
        .into_iter()
        .find(|e| e.memory_edge_id == memory_edge_id)
        .ok_or_else(|| internal_error("edge not found after create"))?;

    Ok(Json(
        json!({ "memory_edge": AvatarMemoryEdgeResponse::from(edge) }),
    ))
}

pub async fn delete_memory_edge(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path((avatar_id, edge_id)): Path<(String, String)>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;
    let pool = tenant_pool.pool();

    db::delete_avatar_memory_edge(pool, org_id, &avatar_id, &edge_id)
        .await
        .map_err(internal_error)?;

    Ok(Json(json!({ "deleted": true })))
}

pub async fn create_instinct_frame(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(avatar_id): Path<String>,
    Json(body): Json<CreateInstinctFrameRequest>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;
    let pool = tenant_pool.pool();

    if body.trigger_kind.is_empty() {
        return Err(bad_request("trigger_kind is required"));
    }

    if body.dominant_concern.is_empty() {
        return Err(bad_request("dominant_concern is required"));
    }

    let instinct_frame_id = uuid::Uuid::new_v4().to_string();

    db::create_avatar_instinct_frame(
        pool,
        &instinct_frame_id,
        org_id,
        &avatar_id,
        body.harness_run_id.as_deref(),
        body.capability_run_id.as_deref(),
        &body.trigger_kind,
        &body.dominant_concern,
        &body.risk_flags,
        &body.recommended_posture,
        &body.visible_summary,
        &body.private_notes,
    )
    .await
    .map_err(internal_error)?;

    Ok(Json(json!({
        "instinct_frame_id": instinct_frame_id,
        "status": "created"
    })))
}

pub async fn list_presence_states(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(run_id): Path<String>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;
    let pool = tenant_pool.pool();

    let states = db::list_harness_presence(pool, org_id, &run_id)
        .await
        .map_err(internal_error)?;

    let response: Vec<AvatarPresenceStateResponse> = states
        .into_iter()
        .map(AvatarPresenceStateResponse::from)
        .collect();

    Ok(Json(json!({ "presence_states": response })))
}

pub async fn upsert_presence_state(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(run_id): Path<String>,
    Json(body): Json<UpsertPresenceStateRequest>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;
    let pool = tenant_pool.pool();

    if body.state.is_empty() {
        return Err(bad_request("state is required"));
    }

    if !VALID_STATES.contains(&body.state.as_str()) {
        return Err(bad_request(
            "state must be one of: idle, thinking, posing, challenging, responding, done, blocked",
        ));
    }

    validate_confidence(body.confidence)?;

    if body.visible_summary.len() > 500 {
        return Err(bad_request(
            "visible_summary exceeds max length of 500 characters",
        ));
    }

    if body.current_focus.len() > 500 {
        return Err(bad_request(
            "current_focus exceeds max length of 500 characters",
        ));
    }

    if body.current_concern.len() > 500 {
        return Err(bad_request(
            "current_concern exceeds max length of 500 characters",
        ));
    }

    let presence_id = uuid::Uuid::new_v4().to_string();

    db::upsert_avatar_presence_state(
        pool,
        &presence_id,
        org_id,
        &body.avatar_id,
        Some(&run_id),
        &body.state,
        &body.current_focus,
        &body.current_concern,
        body.confidence,
        &body.visible_summary,
        body.last_event_id.as_deref(),
    )
    .await
    .map_err(internal_error)?;

    Ok(Json(json!({
        "presence_id": presence_id,
        "status": "upserted"
    })))
}

pub async fn list_debate_events(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(run_id): Path<String>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;
    let pool = tenant_pool.pool();

    let events = db::list_debate_events(pool, org_id, &run_id)
        .await
        .map_err(internal_error)?;

    let response: Vec<AvatarDebateEventResponse> = events
        .into_iter()
        .map(AvatarDebateEventResponse::from)
        .collect();

    Ok(Json(json!({ "debate_events": response })))
}

pub async fn create_debate_event(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(run_id): Path<String>,
    Json(body): Json<CreateDebateEventRequest>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;
    let pool = tenant_pool.pool();

    if body.event_type.is_empty() {
        return Err(bad_request("event_type is required"));
    }

    if !VALID_EVENT_TYPES.contains(&body.event_type.as_str()) {
        return Err(bad_request(
            "event_type must be one of: position, challenge, evidence, refinement, support, oppose, question",
        ));
    }

    validate_confidence(body.confidence)?;

    validate_json_size(&body.content, 10000, "content")?;

    let debate_event_id = uuid::Uuid::new_v4().to_string();

    db::create_avatar_debate_event(
        pool,
        &debate_event_id,
        org_id,
        &run_id,
        body.speaker_avatar_id.as_deref(),
        body.target_avatar_id.as_deref(),
        &body.event_type,
        body.stance.as_deref(),
        &body.content,
        body.confidence,
    )
    .await
    .map_err(internal_error)?;

    Ok(Json(json!({
        "debate_event_id": debate_event_id,
        "status": "created"
    })))
}

pub async fn get_artifact_trail(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(avatar_id): Path<String>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;
    let pool = tenant_pool.pool();

    let trails = db::list_avatar_artifact_trail(pool, org_id, &avatar_id)
        .await
        .map_err(internal_error)?;

    let response: Vec<AvatarArtifactTrailResponse> = trails
        .into_iter()
        .map(AvatarArtifactTrailResponse::from)
        .collect();

    Ok(Json(json!({ "artifact_trail": response })))
}
