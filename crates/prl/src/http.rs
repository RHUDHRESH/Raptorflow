use axum::{
    extract::{Extension, Path, Query},
    http::StatusCode,
    response::IntoResponse,
    routing::{delete, get, post},
    Json, Router,
};
use chrono::{DateTime, Utc};
use raptorflow_auth::TenantContext;
use serde::{Deserialize, Serialize};
use sqlx::{FromRow, PgPool};
use std::sync::Arc;
use tracing::error;
use uuid::Uuid;

use crate::PrlTopology;

type AppResult<T> = Result<T, (StatusCode, Json<serde_json::Value>)>;

fn internal_error<E: std::fmt::Display>(e: E) -> (StatusCode, Json<serde_json::Value>) {
    error!("Internal error: {}", e);
    (StatusCode::INTERNAL_SERVER_ERROR, Json(serde_json::json!({"error": "internal_error"})))
}

fn not_found(msg: &str) -> (StatusCode, Json<serde_json::Value>) {
    (StatusCode::NOT_FOUND, Json(serde_json::json!({"error": msg})))
}

fn forbidden(msg: &str) -> (StatusCode, Json<serde_json::Value>) {
    (StatusCode::FORBIDDEN, Json(serde_json::json!({"error": msg})))
}

pub fn router() -> Router {
    Router::new()
        .route("/ripples", get(list_ripples).post(create_ripple))
        .route("/ripples/:id", get(get_ripple).put(update_ripple).delete(delete_ripple))
        .route("/ripples/:id/edges", get(get_ripple_edges).post(create_ripple_edge))
        .route("/ripples/edges/:edge_id", delete(delete_ripple_edge))
        .route("/essences", get(list_essences).post(create_essence))
        .route("/essences/:id", get(get_essence).put(update_essence))
        .route("/decay", post(run_decay))
}

#[derive(Debug, Deserialize)]
struct CreateRipple {
    title: String,
    description: Option<String>,
    category: Option<String>,
}

#[derive(Debug, Deserialize)]
struct UpdateRipple {
    title: Option<String>,
    description: Option<String>,
    category: Option<String>,
    status: Option<String>,
}

#[derive(Debug, Deserialize)]
struct ListRipplesQuery {
    status: Option<String>,
    category: Option<String>,
}

#[derive(Debug, Serialize, FromRow)]
struct RippleRow {
    id: Uuid,
    title: String,
    description: Option<String>,
    category: Option<String>,
    status: String,
    created_at: DateTime<Utc>,
    updated_at: DateTime<Utc>,
}

async fn create_ripple(
    Extension(_auth): Extension<TenantContext>,
    Extension(tenant): Extension<TenantContext>,
    Extension(pool): Extension<Arc<PgPool>>,
    Json(input): Json<CreateRipple>,
) -> AppResult<impl IntoResponse> {
    let ripple_id: Uuid = sqlx::query_scalar(
        r#"INSERT INTO ripples (org_id, title, description, category, status, created_by)
           VALUES ($1, $2, $3, $4, 'active', $5)
           RETURNING id"#,
    )
    .bind(tenant.org_id)
    .bind(&input.title)
    .bind(&input.description)
    .bind(&input.category)
    .bind(_auth.user_id)
    .fetch_one(&*pool)
    .await
    .map_err(internal_error)?;

    Ok(Json(serde_json::json!({"id": ripple_id, "status": "created"})).into_response())
}

async fn list_ripples(
    Extension(_auth): Extension<TenantContext>,
    Extension(tenant): Extension<TenantContext>,
    Extension(pool): Extension<Arc<PgPool>>,
    Query(query): Query<ListRipplesQuery>,
) -> AppResult<impl IntoResponse> {
    let ripples = sqlx::query_as::<_, RippleRow>(
        r#"
        SELECT id, title, description, category, status, created_at, updated_at
        FROM ripples
        WHERE org_id = $1
          AND ($2::text IS NULL OR status = $2)
          AND ($3::text IS NULL OR category = $3)
        ORDER BY created_at DESC
        LIMIT 100
        "#,
    )
    .bind(tenant.org_id)
    .bind(&query.status)
    .bind(&query.category)
    .fetch_all(&*pool)
    .await
    .map_err(internal_error)?;

    Ok(Json(serde_json::json!({"ripples": ripples})).into_response())
}

async fn get_ripple(
    Extension(_auth): Extension<TenantContext>,
    Extension(tenant): Extension<TenantContext>,
    Extension(pool): Extension<Arc<PgPool>>,
    Path(id): Path<Uuid>,
) -> AppResult<impl IntoResponse> {
    let ripple = sqlx::query_as::<_, RippleRow>(
        r#"SELECT id, title, description, category, status, created_at, updated_at
           FROM ripples WHERE id = $1 AND org_id = $2"#,
    )
    .bind(id)
    .bind(tenant.org_id)
    .fetch_optional(&*pool)
    .await
    .map_err(internal_error)?;

    match ripple {
        Some(r) => Ok(Json(serde_json::json!(r)).into_response()),
        None => Err(not_found("not_found")),
    }
}

async fn update_ripple(
    Extension(_auth): Extension<TenantContext>,
    Extension(tenant): Extension<TenantContext>,
    Extension(pool): Extension<Arc<PgPool>>,
    Path(id): Path<Uuid>,
    Json(input): Json<UpdateRipple>,
) -> AppResult<impl IntoResponse> {
    let existing: Option<(Uuid,)> = sqlx::query_as(
        "SELECT org_id FROM ripples WHERE id = $1 AND org_id = $2",
    )
    .bind(id)
    .bind(tenant.org_id)
    .fetch_optional(&*pool)
    .await
    .map_err(internal_error)?;

    if existing.is_none() {
        return Err(not_found("not_found"));
    }

    sqlx::query(
        r#"UPDATE ripples
           SET title = COALESCE($1, title),
               description = COALESCE($2, description),
               category = COALESCE($3, category),
               status = COALESCE($4, status),
               updated_at = NOW()
           WHERE id = $5 AND org_id = $6"#,
    )
    .bind(&input.title)
    .bind(&input.description)
    .bind(&input.category)
    .bind(&input.status)
    .bind(id)
    .bind(tenant.org_id)
    .execute(&*pool)
    .await
    .map_err(internal_error)?;

    Ok(Json(serde_json::json!({"status": "updated"})).into_response())
}

async fn delete_ripple(
    Extension(_auth): Extension<TenantContext>,
    Extension(tenant): Extension<TenantContext>,
    Extension(pool): Extension<Arc<PgPool>>,
    Path(id): Path<Uuid>,
) -> AppResult<impl IntoResponse> {
    sqlx::query("DELETE FROM ripples WHERE id = $1 AND org_id = $2")
        .bind(id)
        .bind(tenant.org_id)
        .execute(&*pool)
        .await
        .map_err(internal_error)?;

    Ok(Json(serde_json::json!({"status": "deleted"})).into_response())
}

#[derive(Debug, Deserialize)]
struct CreateEdge {
    target_ripple_id: Uuid,
    relationship: String,
}

#[derive(Debug, Serialize, FromRow)]
struct EdgeRow {
    id: Uuid,
    source_ripple_id: Uuid,
    target_ripple_id: Uuid,
    relationship: String,
    created_at: DateTime<Utc>,
}

async fn create_ripple_edge(
    Extension(_auth): Extension<TenantContext>,
    Extension(tenant): Extension<TenantContext>,
    Extension(pool): Extension<Arc<PgPool>>,
    Path(source_id): Path<Uuid>,
    Json(input): Json<CreateEdge>,
) -> AppResult<impl IntoResponse> {
    let source_org: Option<(Uuid,)> = sqlx::query_as(
        "SELECT org_id FROM ripples WHERE id = $1",
    )
    .bind(source_id)
    .fetch_optional(&*pool)
    .await
    .map_err(internal_error)?;

    let source_org = match source_org {
        Some((o,)) => o,
        None => return Err(not_found("source_not_found")),
    };

    if source_org != tenant.org_id {
        return Err(not_found("source_not_found"));
    }

    let target_org: Option<(Uuid,)> = sqlx::query_as(
        "SELECT org_id FROM ripples WHERE id = $1",
    )
    .bind(input.target_ripple_id)
    .fetch_optional(&*pool)
    .await
    .map_err(internal_error)?;

    let target_org = match target_org {
        Some((o,)) => o,
        None => return Err(not_found("target_not_found")),
    };

    if target_org != tenant.org_id {
        return Err(forbidden("cross_tenant_edge_not_allowed"));
    }

    let edge_id: Uuid = sqlx::query_scalar(
        r#"INSERT INTO ripple_edges (org_id, source_ripple_id, target_ripple_id, relationship)
           VALUES ($1, $2, $3, $4)
           RETURNING id"#,
    )
    .bind(tenant.org_id)
    .bind(source_id)
    .bind(input.target_ripple_id)
    .bind(&input.relationship)
    .fetch_one(&*pool)
    .await
    .map_err(internal_error)?;

    Ok(Json(serde_json::json!({"id": edge_id})).into_response())
}

async fn get_ripple_edges(
    Extension(_auth): Extension<TenantContext>,
    Extension(tenant): Extension<TenantContext>,
    Extension(pool): Extension<Arc<PgPool>>,
    Path(id): Path<Uuid>,
) -> AppResult<impl IntoResponse> {
    let ripple_org: Option<(Uuid,)> = sqlx::query_as(
        "SELECT org_id FROM ripples WHERE id = $1",
    )
    .bind(id)
    .fetch_optional(&*pool)
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
        r#"SELECT id, source_ripple_id, target_ripple_id, relationship, created_at
           FROM ripple_edges
           WHERE org_id = $1 AND (source_ripple_id = $2 OR target_ripple_id = $2)
           ORDER BY created_at DESC"#,
    )
    .bind(tenant.org_id)
    .bind(id)
    .fetch_all(&*pool)
    .await
    .map_err(internal_error)?;

    Ok(Json(serde_json::json!({"edges": edges})).into_response())
}

async fn delete_ripple_edge(
    Extension(_auth): Extension<TenantContext>,
    Extension(tenant): Extension<TenantContext>,
    Extension(pool): Extension<Arc<PgPool>>,
    Path(edge_id): Path<Uuid>,
) -> AppResult<impl IntoResponse> {
    sqlx::query("DELETE FROM ripple_edges WHERE id = $1 AND org_id = $2")
        .bind(edge_id)
        .bind(tenant.org_id)
        .execute(&*pool)
        .await
        .map_err(internal_error)?;

    Ok(Json(serde_json::json!({"status": "deleted"})).into_response())
}

#[derive(Debug, Deserialize)]
struct CreateEssence {
    name: String,
    personality: serde_json::Value,
}

#[derive(Debug, Deserialize)]
struct UpdateEssence {
    name: Option<String>,
    personality: Option<serde_json::Value>,
}

#[derive(Debug, Serialize, FromRow)]
struct EssenceRow {
    id: Uuid,
    name: String,
    personality: serde_json::Value,
    memory: serde_json::Value,
    created_at: DateTime<Utc>,
    updated_at: DateTime<Utc>,
}

async fn create_essence(
    Extension(_auth): Extension<TenantContext>,
    Extension(tenant): Extension<TenantContext>,
    Extension(pool): Extension<Arc<PgPool>>,
    Json(input): Json<CreateEssence>,
) -> AppResult<impl IntoResponse> {
    let essence_id: Uuid = sqlx::query_scalar(
        r#"INSERT INTO agent_essences (org_id, name, personality, memory)
           VALUES ($1, $2, $3, '[]'::jsonb)
           RETURNING id"#,
    )
    .bind(tenant.org_id)
    .bind(&input.name)
    .bind(&input.personality)
    .fetch_one(&*pool)
    .await
    .map_err(internal_error)?;

    Ok(Json(serde_json::json!({"id": essence_id})).into_response())
}

async fn list_essences(
    Extension(_auth): Extension<TenantContext>,
    Extension(tenant): Extension<TenantContext>,
    Extension(pool): Extension<Arc<PgPool>>,
) -> AppResult<impl IntoResponse> {
    let essences = sqlx::query_as::<_, EssenceRow>(
        "SELECT id, name, personality, memory, created_at, updated_at FROM agent_essences WHERE org_id = $1",
    )
    .bind(tenant.org_id)
    .fetch_all(&*pool)
    .await
    .map_err(internal_error)?;

    Ok(Json(serde_json::json!({"essences": essences})).into_response())
}

async fn get_essence(
    Extension(_auth): Extension<TenantContext>,
    Extension(tenant): Extension<TenantContext>,
    Extension(pool): Extension<Arc<PgPool>>,
    Path(id): Path<Uuid>,
) -> AppResult<impl IntoResponse> {
    let essence = sqlx::query_as::<_, EssenceRow>(
        "SELECT id, name, personality, memory, created_at, updated_at FROM agent_essences WHERE id = $1 AND org_id = $2",
    )
    .bind(id)
    .bind(tenant.org_id)
    .fetch_optional(&*pool)
    .await
    .map_err(internal_error)?;

    match essence {
        Some(e) => Ok(Json(serde_json::json!(e)).into_response()),
        None => Err(not_found("not_found")),
    }
}

async fn update_essence(
    Extension(_auth): Extension<TenantContext>,
    Extension(tenant): Extension<TenantContext>,
    Extension(pool): Extension<Arc<PgPool>>,
    Path(id): Path<Uuid>,
    Json(input): Json<UpdateEssence>,
) -> AppResult<impl IntoResponse> {
    sqlx::query(
        r#"UPDATE agent_essences
           SET name = COALESCE($1, name),
               personality = COALESCE($2, personality),
               updated_at = NOW()
           WHERE id = $3 AND org_id = $4"#,
    )
    .bind(&input.name)
    .bind(&input.personality)
    .bind(id)
    .bind(tenant.org_id)
    .execute(&*pool)
    .await
    .map_err(internal_error)?;

    Ok(Json(serde_json::json!({"status": "updated"})).into_response())
}

async fn run_decay(
    Extension(_auth): Extension<TenantContext>,
    Extension(tenant): Extension<TenantContext>,
    Extension(pool): Extension<Arc<PgPool>>,
) -> AppResult<impl IntoResponse> {
    let topology = PrlTopology::default();
    let mut total_decayed = 0i32;

    for policy in &topology.decay_policies {
        let result = sqlx::query(
            r#"
            UPDATE ripples
            SET status = 'decayed', updated_at = NOW()
            WHERE org_id = $1
              AND status = 'active'
              AND created_at < NOW() - (($2 || ' hours')::interval)
              AND category = $3
            "#,
        )
        .bind(tenant.org_id)
        .bind(policy.decay_half_life_hours as i64)
        .bind(&policy.memory_class)
        .execute(&*pool)
        .await
        .map_err(internal_error)?;

        total_decayed += result.rows_affected() as i32;
    }

    Ok(Json(serde_json::json!({
        "decayed_count": total_decayed,
        "status": "complete"
    })).into_response())
}
