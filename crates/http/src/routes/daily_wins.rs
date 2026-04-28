use axum::{
    Json, Router,
    extract::{Extension, Path},
    http::StatusCode,
    routing::{get, post},
};
use serde::{Deserialize, Serialize};
use serde_json::{Value, json};
use ulid::Ulid;

use crate::routes::office::handlers::emit_office_event;
use raptorflow_auth::TenantContext;
use raptorflow_db::models::DailyWin;
use raptorflow_db::{TenantDbPool, queries};

pub fn router() -> Router {
    Router::new()
        .route("/", get(list_daily_wins).post(create_daily_win))
        .route("/today", get(get_today_daily_win))
        .route("/{id}/viewed", post(mark_viewed))
        .route("/{id}/acted", post(mark_acted))
}

type AppResult<T> = Result<T, (StatusCode, Json<Value>)>;

fn internal_error<E: std::fmt::Display>(e: E) -> (StatusCode, Json<Value>) {
    tracing::error!("Daily wins route error: {e}");
    (
        StatusCode::INTERNAL_SERVER_ERROR,
        Json(json!({ "error": "daily_wins_internal_error" })),
    )
}

fn not_found() -> (StatusCode, Json<Value>) {
    (
        StatusCode::NOT_FOUND,
        Json(json!({ "error": "daily_win_not_found" })),
    )
}

#[derive(Debug, Serialize)]
pub struct DailyWinResponse {
    pub briefing_id: String,
    pub briefing_date: String,
    pub generated_at: String,
    pub lead_summary: String,
    pub full_briefing: String,
    pub recommended_action: String,
    pub recommended_action_type: String,
    pub recommended_action_data: serde_json::Value,
    pub viewed_at: Option<String>,
    pub acted_on_at: Option<String>,
    pub action_outcome: Option<String>,
}

impl From<DailyWin> for DailyWinResponse {
    fn from(d: DailyWin) -> Self {
        Self {
            briefing_id: d.briefing_id,
            briefing_date: d.briefing_date.to_string(),
            generated_at: d.generated_at.to_rfc3339(),
            lead_summary: d.lead_summary,
            full_briefing: d.full_briefing,
            recommended_action: d.recommended_action,
            recommended_action_type: d.recommended_action_type,
            recommended_action_data: d.recommended_action_data,
            viewed_at: d.viewed_at.map(|t| t.to_rfc3339()),
            acted_on_at: d.acted_on_at.map(|t| t.to_rfc3339()),
            action_outcome: d.action_outcome,
        }
    }
}

#[derive(Debug, Deserialize)]
pub struct CreateDailyWinRequest {
    pub briefing_date: String,
    pub lead_summary: String,
    pub full_briefing: String,
    pub recommended_action: String,
    pub recommended_action_type: String,
    pub recommended_action_data: Option<serde_json::Value>,
}

pub async fn list_daily_wins(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;

    let wins = queries::list_daily_wins(tenant_pool.pool(), org_id)
        .await
        .map_err(internal_error)?;

    let list: Vec<DailyWinResponse> = wins.into_iter().map(Into::into).collect();

    Ok(Json(json!({
        "daily_wins": list,
        "total": list.len(),
        "status": "ok"
    })))
}

pub async fn get_today_daily_win(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;
    let today = chrono::Utc::now().date_naive();

    let win = queries::get_today_daily_win(tenant_pool.pool(), org_id, today)
        .await
        .map_err(internal_error)?;

    match win {
        Some(w) => Ok(Json(json!({
            "daily_win": DailyWinResponse::from(w),
            "status": "ok"
        }))),
        None => Ok(Json(json!({
            "daily_win": null,
            "status": "ok"
        }))),
    }
}

pub async fn create_daily_win(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Json(req): Json<CreateDailyWinRequest>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;
    let briefing_id = Ulid::new().to_string();

    let briefing_date =
        chrono::NaiveDate::parse_from_str(&req.briefing_date, "%Y-%m-%d").map_err(|_| {
            (
                StatusCode::BAD_REQUEST,
                Json(json!({ "error": "invalid_date_format" })),
            )
        })?;

    queries::create_daily_win(
        tenant_pool.pool(),
        &briefing_id,
        org_id,
        briefing_date,
        &req.lead_summary,
        &req.full_briefing,
        &req.recommended_action,
        &req.recommended_action_type,
        req.recommended_action_data
            .as_ref()
            .unwrap_or(&serde_json::json!({})),
    )
    .await
    .map_err(internal_error)?;

    emit_office_event(
        "daily_win_available",
        org_id,
        json!({"briefing_id": briefing_id, "briefing_date": &req.briefing_date}),
    );

    Ok(Json(json!({
        "briefing_id": briefing_id,
        "status": "created"
    })))
}

pub async fn mark_viewed(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(briefing_id): Path<String>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;

    let existing =
        queries::get_today_daily_win(tenant_pool.pool(), org_id, chrono::Utc::now().date_naive())
            .await
            .map_err(internal_error)?;

    if existing.is_none() {
        return Err(not_found());
    }

    queries::update_daily_win_viewed(tenant_pool.pool(), &briefing_id, org_id)
        .await
        .map_err(internal_error)?;

    Ok(Json(json!({ "status": "updated" })))
}

pub async fn mark_acted(
    Extension(tenant): Extension<TenantContext>,
    Extension(tenant_pool): Extension<TenantDbPool>,
    Path(briefing_id): Path<String>,
    Json(req): Json<serde_json::Value>,
) -> AppResult<Json<Value>> {
    let org_id = tenant.org_id;

    let outcome = req
        .get("outcome")
        .and_then(|v| v.as_str())
        .unwrap_or("completed");

    let pool = tenant_pool.pool();
    sqlx::query(
        r#"
        UPDATE daily_wins
        SET acted_on_at = now(), action_outcome = $1
        WHERE briefing_id = $2 AND org_id = $3 AND acted_on_at IS NULL
        "#,
    )
    .bind(outcome)
    .bind(&briefing_id)
    .bind(org_id)
    .execute(pool)
    .await
    .map_err(internal_error)?;

    Ok(Json(json!({ "status": "updated" })))
}
