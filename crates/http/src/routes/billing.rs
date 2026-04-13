use axum::{
    extract::{Extension, Path},
    http::{HeaderMap, Request, StatusCode},
    routing::{get, post},
    Json, Router,
};
use raptorflow_billing::{RazorpayClient, RazorpayWebhookRuntime, razorpay_webhook};
use raptorflow_db::queries;
use serde::{Deserialize, Serialize};
use std::sync::Arc;
use uuid::Uuid;

use crate::middleware::{AppState, auth::AuthContext};

#[derive(Debug, Deserialize)]
pub struct CreateOrderRequest {
    pub amount: i64,
    pub currency: String,
}

#[derive(Debug, Serialize)]
pub struct BillingStatusResponse {
    pub provider: String,
    pub monthly_price_inr: i64,
    pub grace_period_days: i32,
    pub subscription_status: Option<String>,
    pub org_id: String,
}

pub fn router() -> Router {
    Router::new()
        .route("/", get(billing_status))
        .route("/orders", post(create_order))
        .route("/subscriptions/{id}", get(get_subscription))
        .route("/subscriptions/{id}/cancel", post(cancel_subscription))
}

pub async fn billing_status(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
) -> Result<Json<BillingStatusResponse>, StatusCode> {
    let subscription_status = if let Some(ref pool) = state.db_pool {
        match raptorflow_db::queries::get_subscription_status(pool, auth.tenant.org_id).await {
            Ok(status) => Some(status),
            Err(e) => {
                tracing::error!(error = %e, org_id = %auth.tenant.org_id, "Failed to get subscription status");
                return Err(StatusCode::INTERNAL_SERVER_ERROR);
            }
        }
    } else {
        None
    };

    Ok(Json(BillingStatusResponse {
        provider: "razorpay".to_string(),
        monthly_price_inr: 5000,
        grace_period_days: 2,
        subscription_status,
        org_id: auth.tenant.org_id.to_string(),
    }))
}

pub async fn create_order(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
    Json(req): Json<CreateOrderRequest>,
) -> Result<Json<serde_json::Value>, StatusCode> {
    let razorpay_client = RazorpayClient::new(
        state.settings.razorpay_key_id.clone(),
        state.settings.razorpay_key_secret.clone(),
    );

    let amount_in_paise = req.amount * 100;

    match razorpay_client.create_order(amount_in_paise, &req.currency).await {
        Ok(order) => {
            tracing::info!(
                order_id = %order.id,
                org_id = %auth.tenant.org_id,
                "Created Razorpay order"
            );
            Ok(Json(serde_json::json!({
                "order_id": order.id,
                "amount": order.amount,
                "currency": order.currency,
                "status": order.status,
                "org_id": auth.tenant.org_id.to_string(),
            })))
        }
        Err(e) => {
            tracing::error!(error = %e, "Failed to create Razorpay order");
            Err(StatusCode::INTERNAL_SERVER_ERROR)
        }
    }
}

pub async fn get_subscription(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
    Path(subscription_id): Path<String>,
) -> Result<Json<serde_json::Value>, StatusCode> {
    if let Some(ref pool) = state.db_pool {
        match queries::get_subscription_by_razorpay_id(pool, auth.tenant.org_id, &subscription_id).await {
            Ok(Some(_)) => {}
            Ok(None) => {
                tracing::warn!(
                    subscription_id = %subscription_id,
                    org_id = %auth.tenant.org_id,
                    "Subscription not found for org"
                );
                return Err(StatusCode::NOT_FOUND);
            }
            Err(e) => {
                tracing::error!(error = %e, "Failed to verify subscription ownership");
                return Err(StatusCode::INTERNAL_SERVER_ERROR);
            }
        }
    }

    let razorpay_client = RazorpayClient::new(
        state.settings.razorpay_key_id.clone(),
        state.settings.razorpay_key_secret.clone(),
    );

    match razorpay_client.get_subscription(&subscription_id).await {
        Ok(subscription) => Ok(Json(subscription)),
        Err(e) => {
            tracing::error!(error = %e, "Failed to get subscription");
            Err(StatusCode::INTERNAL_SERVER_ERROR)
        }
    }
}

pub async fn cancel_subscription(
    Extension(auth): Extension<AuthContext>,
    Extension(state): Extension<Arc<AppState>>,
    Path(subscription_id): Path<String>,
) -> Result<Json<serde_json::Value>, StatusCode> {
    if let Some(ref pool) = state.db_pool {
        match queries::get_subscription_by_razorpay_id(pool, auth.tenant.org_id, &subscription_id).await {
            Ok(Some(_)) => {}
            Ok(None) => {
                tracing::warn!(
                    subscription_id = %subscription_id,
                    org_id = %auth.tenant.org_id,
                    "Subscription not found for org"
                );
                return Err(StatusCode::NOT_FOUND);
            }
            Err(e) => {
                tracing::error!(error = %e, "Failed to verify subscription ownership");
                return Err(StatusCode::INTERNAL_SERVER_ERROR);
            }
        }
    }

    let razorpay_client = RazorpayClient::new(
        state.settings.razorpay_key_id.clone(),
        state.settings.razorpay_key_secret.clone(),
    );

    match razorpay_client.cancel_subscription(&subscription_id).await {
        Ok(result) => {
            tracing::info!(
                subscription_id = %subscription_id,
                org_id = %auth.tenant.org_id,
                "Cancelled subscription"
            );
            Ok(Json(result))
        }
        Err(e) => {
            tracing::error!(error = %e, "Failed to cancel subscription");
            Err(StatusCode::INTERNAL_SERVER_ERROR)
        }
    }
}

pub async fn razorpay_webhook(
    headers: HeaderMap,
    Extension(state): Extension<Arc<AppState>>,
    request: Request<axum::body::Body>,
) -> Result<Json<serde_json::Value>, StatusCode> {
    let signature = headers
        .get("x-razorpay-signature")
        .and_then(|v| v.to_str().ok())
        .unwrap_or_default()
        .to_string();

    let body = axum::body::to_bytes(request.into_body(), 10 * 1024 * 1024)
        .await
        .map_err(|_| StatusCode::BAD_REQUEST)?;

    // # FIXED: use RazorpayWebhookRuntime::verify() instead of duplicating signature verification + parsing
    let runtime = RazorpayWebhookRuntime::from_settings(state.settings.clone());
    let verified = match runtime.verify(&body, &signature) {
        Ok(v) => v,
        Err(e) => {
            tracing::warn!(error = %e, "Razorpay webhook verification failed");
            return Err(StatusCode::UNAUTHORIZED);
        }
    };

    tracing::info!(event = %verified.event, webhook_id = %verified.webhook_id, "Processing Razorpay webhook");

    if let Some(ref pool) = state.db_pool {
        // Re-parse payload for event processing since we need the full payload
        let payload: razorpay_webhook::WebhookPayload = serde_json::from_slice(&body)
            .map_err(|e| {
                tracing::warn!(error = %e, "Failed to parse Razorpay webhook payload");
                StatusCode::BAD_REQUEST
            })?;
        if let Err(e) = process_razorpay_event(pool, &payload).await {
            tracing::error!(error = %e, "Failed to process Razorpay event");
        }
    }

    Ok(Json(serde_json::json!({
        "status": "accepted"
    })))
}

// # FIXED: removed duplicate verify_razorpay_signature - now using RazorpayWebhookRuntime::verify()

async fn process_razorpay_event(
    pool: &sqlx::PgPool,
    payload: &razorpay_webhook::WebhookPayload,
) -> Result<(), String> {
    match payload.event.as_str() {
        "payment.authorized" => {
            if let Some(ref payment) = payload.payload.payment {
                let entity = &payment.entity;
                match extract_org_id_from_metadata(&entity.order_id) {
                    Ok(org_id) => {
                        queries::create_payment_event(
                            pool,
                            Uuid::new_v4(),
                            org_id,
                            &format!("pay_{}", entity.id),
                            "payment.authorized",
                            Some(&entity.id),
                            entity.order_id.as_deref(),
                            Some(entity.amount),
                            Some(&entity.currency),
                            Some(&entity.status),
                        ).await.map_err(|e| e.to_string())?;
                    }
                    Err(e) => {
                        tracing::warn!(
                            order_id = ?entity.order_id,
                            error = %e,
                            "Failed to extract org_id from order, dropping event"
                        );
                    }
                }
            }
        }
        "subscription.activated" | "subscription.updated" => {
            if let Some(ref sub) = payload.payload.subscription {
                let entity = &sub.entity;
                if let Some(ref plan_id) = entity.plan_id {
                    tracing::info!(
                        subscription_id = %entity.id,
                        plan_id = %plan_id,
                        status = %entity.status,
                        "Processing subscription event"
                    );
                }
            }
        }
        "subscription.cancelled" => {
            if let Some(ref sub) = payload.payload.subscription {
                let entity = &sub.entity;
                queries::update_subscription_status(pool, &entity.id, "cancelled")
                    .await
                    .map_err(|e| e.to_string())?;
            }
        }
        _ => {
            tracing::debug!(event = %payload.event, "Unhandled Razorpay event type");
        }
    }
    Ok(())
}

fn extract_org_id_from_metadata(order_id: &Option<String>) -> Result<uuid::Uuid, String> {
    let oid = order_id.as_ref()
        .ok_or_else(|| "No order_id in payment event".to_string())?;
    
    if oid.len() < 38 || !oid.starts_with("order_") {
        return Err(format!("Invalid order_id format: {}", oid));
    }
    
    let uuid_part = &oid[6..];
    Uuid::parse_str(uuid_part)
        .map_err(|e| format!("Invalid UUID in order_id: {}", e))
}
