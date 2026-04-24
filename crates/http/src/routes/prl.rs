use axum::{
    Json, Router,
    extract::{Extension, Path, Query},
    http::StatusCode,
    response::IntoResponse,
    routing::{delete, get, post},
};
use chrono::Utc;
use raptorflow_auth::TenantContext;
use raptorflow_db::TenantDbPool;
use serde::{Deserialize, Serialize};
use sqlx::FromRow;
use tracing::error;
use uuid::Uuid;

use raptorflow_prl::PrlTopology;
use crate::routes::office::handlers::emit_office_event;

type AppResult<T> = Result<T, (StatusCode, Json<serde_json::Value>)>;

fn internal_error<E: std::fmt::Display>(e: E) -> (StatusCode, Json<serde_json::Value>) {
    error!("Internal error: {}", e);
    (
        StatusCode::INTERNAL_SERVER_ERROR,
        Json(serde_json::json!({"error": "internal_error"})),
    )
}

fn not_found(msg: &str) -> (StatusCode, Json<serde_json::Value>) {
    (
        StatusCode::NOT_FOUND,
        Json(serde_json::json!({"error": msg})),
    )
}

fn bad_request(msg: &str) -> (StatusCode, Json<serde_json::Value>) {
    (
        StatusCode::BAD_REQUEST,
        Json(serde_json::json!({"error": msg})),
    )
}

pub fn router() -> Router {
    Router::new()
        .route("/ripples", get(list_ripples).post(create_ripple))
        .route(
            "/ripples/:id",
            get(get_ripple).put(update_ripple).delete(delete_ripple),
        )
        .route(
            "/ripples/:id/edges",
            get(get_ripple_edges).post(create_ripple_edge),
        )
        .route("/ripples/edges/:edge_id", delete(delete_ripple_edge))
        .route("/essences", get(list_essences).post(create_essence))
        .route("/essences/:id", get(get_essence).put(update_essence))
        .route("/decay", post(run_decay))
}

#[derive(Debug, Deserialize)]
pub struct CreateRippleRequest {
    scope: String,
    hierarchy_level: i32,
    memory_class: String,
    source: String,
    trigger_text: String,
    raw_text: String,
    summary_text: String,
    salience: f64,
    confidence: f64,
    importance_band: String,
    campaign_id: Option<String>,
    agent_id: Option<Uuid>,
}

impl CreateRippleRequest {
    fn validate(&self) -> Result<(), String> {
        if self.scope.trim().is_empty() {
            return Err("scope is required and cannot be empty".to_string());
        }
        if self.hierarchy_level < 0 || self.hierarchy_level > 10 {
            return Err("hierarchy_level must be between 0 and 10".to_string());
        }
        if self.memory_class.trim().is_empty() {
            return Err("memory_class is required and cannot be empty".to_string());
        }
        if self.source.trim().is_empty() {
            return Err("source is required and cannot be empty".to_string());
        }
        if self.trigger_text.trim().is_empty() {
            return Err("trigger_text is required and cannot be empty".to_string());
        }
        if self.raw_text.trim().is_empty() {
            return Err("raw_text is required and cannot be empty".to_string());
        }
        if self.summary_text.trim().is_empty() {
            return Err("summary_text is required and cannot be empty".to_string());
        }
        if !(0.0..=1.0).contains(&self.salience) {
            return Err("salience must be between 0.0 and 1.0".to_string());
        }
        if !(0.0..=1.0).contains(&self.confidence) {
            return Err("confidence must be between 0.0 and 1.0".to_string());
        }
        let valid_bands = ["protected", "important", "normal", "disposable"];
        if !valid_bands.contains(&self.importance_band.as_str()) {
            return Err(format!("importance_band must be one of: {}", valid_bands.join(", ")));
        }
        Ok(())
    }
}

#[derive(Debug, Deserialize)]
pub struct UpdateRippleRequest {
    scope: Option<String>,
    memory_class: Option<String>,
    trigger_text: Option<String>,
    raw_text: Option<String>,
    summary_text: Option<String>,
    salience: Option<f64>,
    confidence: Option<f64>,
    importance_band: Option<String>,
}

#[derive(Debug, Deserialize)]
pub struct ListRipplesQuery {
    scope: Option<String>,
    memory_class: Option<String>,
    importance_band: Option<String>,
}

#[derive(Debug, Serialize, FromRow)]
struct RippleRow {
    ripple_id: String,
    org_id: Uuid,
    agent_id: Uuid,
    campaign_id: Option<String>,
    scope: String,
    hierarchy_level: i32,
    memory_class: String,
    source: String,
    trigger_text: String,
    raw_text: String,
    summary_text: String,
    embedding: Option<Vec<f32>>,
    simhash: Option<Vec<i64>>,
    emotion_vector: Option<Vec<f64>>,
    salience: f64,
    confidence: f64,
    importance_band: String,
    prediction_json: Option<serde_json::Value>,
    created_at: chrono::DateTime<Utc>,
}

#[derive(Debug, Serialize)]
struct RippleResponse {
    ripple_id: String,
    org_id: Uuid,
    agent_id: Uuid,
    campaign_id: Option<String>,
    scope: String,
    hierarchy_level: i32,
    memory_class: String,
    source: String,
    trigger_text: String,
    raw_text: String,
    summary_text: String,
    embedding: Option<Vec<f32>>,
    simhash: Option<Vec<i64>>,
    emotion_vector: Option<Vec<f64>>,
    salience: f64,
    confidence: f64,
    importance_band: String,
    prediction_json: Option<serde_json::Value>,
    created_at: chrono::DateTime<Utc>,
}

impl From<RippleRow> for RippleResponse {
    fn from(row: RippleRow) -> Self {
        Self {
            ripple_id: row.ripple_id,
            org_id: row.org_id,
            agent_id: row.agent_id,
            campaign_id: row.campaign_id,
            scope: row.scope,
            hierarchy_level: row.hierarchy_level,
            memory_class: row.memory_class,
            source: row.source,
            trigger_text: row.trigger_text,
            raw_text: row.raw_text,
            summary_text: row.summary_text,
            embedding: row.embedding,
            simhash: row.simhash,
            emotion_vector: row.emotion_vector,
            salience: row.salience,
            confidence: row.confidence,
            importance_band: row.importance_band,
            prediction_json: row.prediction_json,
            created_at: row.created_at,
        }
    }
}

pub async fn create_ripple(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Json(input): Json<CreateRippleRequest>,
) -> AppResult<impl IntoResponse> {
    if let Err(msg) = input.validate() {
        return Err(bad_request(&msg));
    }

    let mut conn = tenant_pool
        .acquire_for_tenant(tenant.org_id)
        .await
        .map_err(internal_error)?;
    let ripple_id = format!("ripple_{}", Uuid::new_v4());
    let agent_id = input.agent_id.unwrap_or_else(Uuid::nil);

    sqlx::query(
        r#"INSERT INTO ripples
           (ripple_id, org_id, agent_id, campaign_id, scope, hierarchy_level, memory_class,
            source, trigger_text, raw_text, summary_text, salience, confidence, importance_band)
           VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14)"#,
    )
    .bind(&ripple_id)
    .bind(tenant.org_id)
    .bind(agent_id)
    .bind(&input.campaign_id)
    .bind(&input.scope)
    .bind(input.hierarchy_level)
    .bind(&input.memory_class)
    .bind(&input.source)
    .bind(&input.trigger_text)
    .bind(&input.raw_text)
    .bind(&input.summary_text)
    .bind(input.salience)
    .bind(input.confidence)
    .bind(&input.importance_band)
    .execute(&mut *conn)
    .await
    .map_err(internal_error)?;

    emit_office_event(
        "ripple_created",
        tenant.org_id,
        serde_json::json!({
            "ripple_id": ripple_id,
            "scope": input.scope,
            "importance_band": input.importance_band,
            "memory_class": input.memory_class,
        }),
    );

    Ok(Json(serde_json::json!({
        "ripple_id": ripple_id,
        "status": "created"
    }))
    .into_response())
}

pub async fn list_ripples(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Query(query): Query<ListRipplesQuery>,
) -> AppResult<impl IntoResponse> {
    let mut conn = tenant_pool
        .acquire_for_tenant(tenant.org_id)
        .await
        .map_err(internal_error)?;
    let ripples = sqlx::query_as::<_, RippleRow>(
        r#"
        SELECT ripple_id, org_id, agent_id, campaign_id, scope, hierarchy_level, memory_class,
               source, trigger_text, raw_text, summary_text, embedding, simhash, emotion_vector,
               salience, confidence, importance_band, prediction_json, created_at
        FROM ripples
        WHERE org_id = $1
          AND ($2::text IS NULL OR scope = $2)
          AND ($3::text IS NULL OR memory_class = $3)
          AND ($4::text IS NULL OR importance_band = $4)
        ORDER BY created_at DESC
        LIMIT 100
        "#,
    )
    .bind(tenant.org_id)
    .bind(&query.scope)
    .bind(&query.memory_class)
    .bind(&query.importance_band)
    .fetch_all(&mut *conn)
    .await
    .map_err(internal_error)?;

    let responses: Vec<RippleResponse> = ripples.into_iter().map(|r| r.into()).collect();
    Ok(Json(serde_json::json!({"ripples": responses})).into_response())
}

pub async fn get_ripple(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(id): Path<String>,
) -> AppResult<impl IntoResponse> {
    let mut conn = tenant_pool
        .acquire_for_tenant(tenant.org_id)
        .await
        .map_err(internal_error)?;
    let ripple = sqlx::query_as::<_, RippleRow>(
        r#"SELECT ripple_id, org_id, agent_id, campaign_id, scope, hierarchy_level, memory_class,
                  source, trigger_text, raw_text, summary_text, embedding, simhash, emotion_vector,
                  salience, confidence, importance_band, prediction_json, created_at
           FROM ripples WHERE ripple_id = $1 AND org_id = $2"#,
    )
    .bind(&id)
    .bind(tenant.org_id)
    .fetch_optional(&mut *conn)
    .await
    .map_err(internal_error)?;

    match ripple {
        Some(r) => {
            let response: RippleResponse = r.into();
            Ok(Json(response).into_response())
        }
        None => Err(not_found("ripple_not_found")),
    }
}

pub async fn update_ripple(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(id): Path<String>,
    Json(input): Json<UpdateRippleRequest>,
) -> AppResult<impl IntoResponse> {
    let mut conn = tenant_pool
        .acquire_for_tenant(tenant.org_id)
        .await
        .map_err(internal_error)?;
    let existing: Option<(String,)> =
        sqlx::query_as("SELECT ripple_id FROM ripples WHERE ripple_id = $1 AND org_id = $2")
            .bind(&id)
            .bind(tenant.org_id)
            .fetch_optional(&mut *conn)
            .await
            .map_err(internal_error)?;

    if existing.is_none() {
        return Err(not_found("ripple_not_found"));
    }

    sqlx::query(
        r#"UPDATE ripples
           SET scope = COALESCE($1, scope),
               memory_class = COALESCE($2, memory_class),
               trigger_text = COALESCE($3, trigger_text),
               raw_text = COALESCE($4, raw_text),
               summary_text = COALESCE($5, summary_text),
               salience = COALESCE($6, salience),
               confidence = COALESCE($7, confidence),
               importance_band = COALESCE($8, importance_band)
           WHERE ripple_id = $9 AND org_id = $10"#,
    )
    .bind(&input.scope)
    .bind(&input.memory_class)
    .bind(&input.trigger_text)
    .bind(&input.raw_text)
    .bind(&input.summary_text)
    .bind(input.salience)
    .bind(input.confidence)
    .bind(&input.importance_band)
    .bind(&id)
    .bind(tenant.org_id)
    .execute(&mut *conn)
    .await
    .map_err(internal_error)?;

    Ok(Json(serde_json::json!({"status": "updated"})).into_response())
}

pub async fn delete_ripple(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(id): Path<String>,
) -> AppResult<impl IntoResponse> {
    let mut conn = tenant_pool
        .acquire_for_tenant(tenant.org_id)
        .await
        .map_err(internal_error)?;
    sqlx::query("DELETE FROM ripples WHERE ripple_id = $1 AND org_id = $2")
        .bind(&id)
        .bind(tenant.org_id)
        .execute(&mut *conn)
        .await
        .map_err(internal_error)?;

    Ok(Json(serde_json::json!({"status": "deleted"})).into_response())
}

#[derive(Debug, Deserialize)]
pub struct CreateEdgeRequest {
    target_ripple_id: String,
    relationship: String,
}

#[derive(Debug, Serialize, FromRow)]
struct EdgeRow {
    edge_id: Uuid,
    source_ripple_id: String,
    target_ripple_id: String,
    edge_type: String,
    weight: f64,
    created_at: chrono::DateTime<Utc>,
}

pub async fn create_ripple_edge(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(source_id): Path<String>,
    Json(input): Json<CreateEdgeRequest>,
) -> AppResult<impl IntoResponse> {
    let mut conn = tenant_pool
        .acquire_for_tenant(tenant.org_id)
        .await
        .map_err(internal_error)?;
    let source_org: Option<(Uuid,)> =
        sqlx::query_as("SELECT org_id FROM ripples WHERE ripple_id = $1")
            .bind(&source_id)
            .fetch_optional(&mut *conn)
            .await
            .map_err(internal_error)?;

    let source_org = match source_org {
        Some((o,)) => o,
        None => return Err(not_found("source_not_found")),
    };

    if source_org != tenant.org_id {
        return Err(not_found("source_not_found"));
    }

    let target_org: Option<(Uuid,)> =
        sqlx::query_as("SELECT org_id FROM ripples WHERE ripple_id = $1")
            .bind(&input.target_ripple_id)
            .fetch_optional(&mut *conn)
            .await
            .map_err(internal_error)?;

    let target_org = match target_org {
        Some((o,)) => o,
        None => return Err(not_found("target_not_found")),
    };

    if target_org != tenant.org_id {
        return Err(not_found("cross_tenant_not_allowed"));
    }

    let edge_id = Uuid::new_v4();
    sqlx::query(
        r#"INSERT INTO ripple_edges (edge_id, org_id, source_ripple_id, target_ripple_id, edge_type, weight)
           VALUES ($1, $2, $3, $4, $5, 0.5)"#,
    )
    .bind(edge_id)
    .bind(tenant.org_id)
    .bind(&source_id)
    .bind(&input.target_ripple_id)
    .bind(&input.relationship)
    .execute(&mut *conn)
    .await
    .map_err(internal_error)?;

    Ok(Json(serde_json::json!({"edge_id": edge_id})).into_response())
}

pub async fn get_ripple_edges(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(id): Path<String>,
) -> AppResult<impl IntoResponse> {
    let mut conn = tenant_pool
        .acquire_for_tenant(tenant.org_id)
        .await
        .map_err(internal_error)?;
    let ripple_org: Option<(Uuid,)> =
        sqlx::query_as("SELECT org_id FROM ripples WHERE ripple_id = $1")
            .bind(&id)
            .fetch_optional(&mut *conn)
            .await
            .map_err(internal_error)?;

    let ripple_org = match ripple_org {
        Some((o,)) => o,
        None => return Err(not_found("not_found")),
    };

    if ripple_org != tenant.org_id {
        return Err(not_found("not_found"));
    }

    let edges = sqlx::query_as::<_, EdgeRow>(
        r#"SELECT edge_id, source_ripple_id, target_ripple_id, edge_type, weight, created_at
           FROM ripple_edges
           WHERE org_id = $1 AND (source_ripple_id = $2 OR target_ripple_id = $2)
           ORDER BY created_at DESC"#,
    )
    .bind(tenant.org_id)
    .bind(&id)
    .fetch_all(&mut *conn)
    .await
    .map_err(internal_error)?;

    Ok(Json(serde_json::json!({"edges": edges})).into_response())
}

pub async fn delete_ripple_edge(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(edge_id): Path<Uuid>,
) -> AppResult<impl IntoResponse> {
    let mut conn = tenant_pool
        .acquire_for_tenant(tenant.org_id)
        .await
        .map_err(internal_error)?;
    sqlx::query("DELETE FROM ripple_edges WHERE edge_id = $1 AND org_id = $2")
        .bind(edge_id)
        .bind(tenant.org_id)
        .execute(&mut *conn)
        .await
        .map_err(internal_error)?;

    Ok(Json(serde_json::json!({"status": "deleted"})).into_response())
}

#[derive(Debug, Deserialize)]
pub struct CreateEssenceRequest {
    avatar_key: String,
    essence_core: serde_json::Value,
    ego_baseline: Vec<f64>,
}

impl CreateEssenceRequest {
    fn validate(&self) -> Result<(), String> {
        if self.avatar_key.trim().is_empty() {
            return Err("avatar_key is required and cannot be empty".to_string());
        }
        if self.ego_baseline.len() != 8 {
            return Err("ego_baseline must have exactly 8 elements (Plutchik emotions)".to_string());
        }
        for (i, val) in self.ego_baseline.iter().enumerate() {
            if !(0.0..=1.0).contains(val) {
                return Err(format!("ego_baseline[{}] must be between 0.0 and 1.0", i));
            }
        }
        Ok(())
    }
}

#[derive(Debug, Serialize, FromRow)]
struct EssenceRow {
    agent_id: Uuid,
    org_id: Uuid,
    avatar_key: String,
    display_name: Option<String>,
    essence_core: serde_json::Value,
    ego_baseline: Vec<f64>,
    ego_state: Vec<f64>,
    skill_atoms: serde_json::Value,
    created_at: chrono::DateTime<Utc>,
}

pub async fn create_essence(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Json(input): Json<CreateEssenceRequest>,
) -> AppResult<impl IntoResponse> {
    if let Err(msg) = input.validate() {
        return Err(bad_request(&msg));
    }

    let mut conn = tenant_pool
        .acquire_for_tenant(tenant.org_id)
        .await
        .map_err(internal_error)?;
    let agent_id = Uuid::new_v4();

    sqlx::query(
        r#"INSERT INTO agent_essences
           (agent_id, org_id, avatar_key, essence_core, ego_baseline, ego_state, skill_atoms)
           VALUES ($1, $2, $3, $4, $5, $5, '[]'::jsonb)"#,
    )
    .bind(agent_id)
    .bind(tenant.org_id)
    .bind(&input.avatar_key)
    .bind(&input.essence_core)
    .bind(&input.ego_baseline)
    .execute(&mut *conn)
    .await
    .map_err(internal_error)?;

    Ok(Json(serde_json::json!({"agent_id": agent_id})).into_response())
}

pub async fn list_essences(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
) -> AppResult<impl IntoResponse> {
    let mut conn = tenant_pool
        .acquire_for_tenant(tenant.org_id)
        .await
        .map_err(internal_error)?;
    let essences = sqlx::query_as::<_, EssenceRow>(
        r#"SELECT agent_id, org_id, avatar_key, display_name, essence_core,
                  ego_baseline, ego_state, skill_atoms, created_at
           FROM agent_essences WHERE org_id = $1"#,
    )
    .bind(tenant.org_id)
    .fetch_all(&mut *conn)
    .await
    .map_err(internal_error)?;

    Ok(Json(serde_json::json!({"essences": essences})).into_response())
}

pub async fn get_essence(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(id): Path<Uuid>,
) -> AppResult<impl IntoResponse> {
    let mut conn = tenant_pool
        .acquire_for_tenant(tenant.org_id)
        .await
        .map_err(internal_error)?;
    let essence = sqlx::query_as::<_, EssenceRow>(
        r#"SELECT agent_id, org_id, avatar_key, display_name, essence_core,
                  ego_baseline, ego_state, skill_atoms, created_at
           FROM agent_essences WHERE agent_id = $1 AND org_id = $2"#,
    )
    .bind(id)
    .bind(tenant.org_id)
    .fetch_optional(&mut *conn)
    .await
    .map_err(internal_error)?;

    match essence {
        Some(e) => Ok(Json(serde_json::json!(e)).into_response()),
        None => Err(not_found("essence_not_found")),
    }
}

pub async fn update_essence(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(id): Path<Uuid>,
    Json(input): Json<CreateEssenceRequest>,
) -> AppResult<impl IntoResponse> {
    let mut conn = tenant_pool
        .acquire_for_tenant(tenant.org_id)
        .await
        .map_err(internal_error)?;
    sqlx::query(
        r#"UPDATE agent_essences
           SET avatar_key = COALESCE($1, avatar_key),
               essence_core = COALESCE($2, essence_core),
               ego_baseline = COALESCE($3, ego_baseline),
               updated_at = NOW()
           WHERE agent_id = $4 AND org_id = $5"#,
    )
    .bind(&input.avatar_key)
    .bind(&input.essence_core)
    .bind(&input.ego_baseline)
    .bind(id)
    .bind(tenant.org_id)
    .execute(&mut *conn)
    .await
    .map_err(internal_error)?;

    Ok(Json(serde_json::json!({"status": "updated"})).into_response())
}

pub async fn run_decay(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
) -> AppResult<impl IntoResponse> {
    let mut conn = tenant_pool
        .acquire_for_tenant(tenant.org_id)
        .await
        .map_err(internal_error)?;
    let topology = PrlTopology::default();
    let mut total_processed = 0i32;
    let mut total_decayed = 0i32;
    let mut total_deleted = 0i32;

    #[derive(Debug, sqlx::FromRow)]
    struct RippleForDecay {
        ripple_id: String,
        salience: f64,
        confidence: f64,
        created_at: chrono::DateTime<chrono::Utc>,
    }

    for policy in &topology.decay_policies {
        let band_name = serde_json::to_string(&policy.protection_band)
            .map(|s| s.trim_matches('"').to_string())
            .unwrap_or_default();

        let ripples: Vec<RippleForDecay> = sqlx::query_as(
            r#"
            SELECT ripple_id, salience, confidence, created_at
            FROM ripples
            WHERE org_id = $1
              AND memory_class = $2
              AND importance_band = $3
            "#,
        )
        .bind(tenant.org_id)
        .bind(&policy.memory_class)
        .bind(band_name)
        .fetch_all(&mut *conn)
        .await
        .map_err(internal_error)?;

        for ripple in ripples {
            total_processed += 1;
            let elapsed_hours = ripple
                .created_at
                .signed_duration_since(chrono::Utc::now())
                .num_seconds() as f64
                / 3600.0;
            let elapsed_hours = elapsed_hours.abs();

            let exponent = elapsed_hours / policy.decay_half_life_hours as f64;
            let decay_factor = 0.5_f64.powf(exponent);

            let new_salience = (ripple.salience * decay_factor * 100.0).round() / 100.0;
            let new_confidence = (ripple.confidence * decay_factor * 100.0).round() / 100.0;

            if new_salience < policy.consolidation_threshold {
                sqlx::query("DELETE FROM ripples WHERE ripple_id = $1 AND org_id = $2")
                    .bind(&ripple.ripple_id)
                    .bind(tenant.org_id)
                    .execute(&mut *conn)
                    .await
                    .map_err(internal_error)?;
                total_deleted += 1;
                total_decayed += 1;
            } else if (new_salience - ripple.salience).abs() > 0.001
                      || (new_confidence - ripple.confidence).abs() > 0.001 {
                sqlx::query(
                    r#"
                    UPDATE ripples
                    SET salience = $1, confidence = $2
                    WHERE ripple_id = $3 AND org_id = $4
                    "#,
                )
                .bind(new_salience)
                .bind(new_confidence)
                .bind(&ripple.ripple_id)
                .bind(tenant.org_id)
                .execute(&mut *conn)
                .await
                .map_err(internal_error)?;
                total_decayed += 1;
            }
        }
    }

    Ok(Json(serde_json::json!({
        "ripples_processed": total_processed,
        "decayed": total_decayed,
        "deleted": total_deleted,
        "status": "completed"
    }))
    .into_response())
}
