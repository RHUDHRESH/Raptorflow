use axum::{
    Json, Router,
    body::Body,
    extract::Extension,
    http::{Request, StatusCode},
    routing::post,
};
use hmac::{Hmac, Mac};
use serde::Serialize;
use serde_json::Value;
use sha2::Sha256;
use std::sync::Arc;

use crate::middleware::AppState;

type HmacSha256 = Hmac<Sha256>;

#[derive(Debug, Serialize)]
pub struct RazorpayWebhookResponse {
    pub received: bool,
    pub processed: bool,
    pub message: String,
}

pub fn router() -> Router {
    Router::new().route("/webhooks/razorpay", post(razorpay_webhook))
}

pub async fn razorpay_webhook(
    Extension(state): Extension<Arc<AppState>>,
    request: Request<Body>,
) -> Result<Json<RazorpayWebhookResponse>, StatusCode> {
    let signature = request
        .headers()
        .get("x-razorpay-signature")
        .and_then(|value| value.to_str().ok())
        .unwrap_or_default()
        .to_string();

    if signature.trim().is_empty() {
        return Err(StatusCode::UNAUTHORIZED);
    }

    let body = axum::body::to_bytes(request.into_body(), 10 * 1024 * 1024)
        .await
        .map_err(|_| StatusCode::BAD_REQUEST)?;

    let webhook_secret = state
        .settings
        .razorpay_webhook_secret
        .clone()
        .ok_or_else(|| {
            tracing::error!("Missing Razorpay webhook secret in settings");
            StatusCode::INTERNAL_SERVER_ERROR
        })?;

    if !verify_razorpay_signature(&body, &signature, &webhook_secret) {
        return Err(StatusCode::UNAUTHORIZED);
    }

    let payload: Value = serde_json::from_slice(&body).map_err(|_| StatusCode::BAD_REQUEST)?;
    let event_id =
        extract_str(&payload, &["id", "event_id"]).unwrap_or_else(|| payload_hash_id(&body));
    let event_type = extract_str(&payload, &["event"]).unwrap_or_else(|| "unknown".to_string());
    let subscription_id = nested_str(&payload, &["payload", "subscription", "entity", "id"]);
    let payment_id = nested_str(&payload, &["payload", "payment", "entity", "id"]);
    let order_id = nested_str(&payload, &["payload", "payment", "entity", "order_id"]);
    let status = nested_str(&payload, &["payload", "subscription", "entity", "status"])
        .or_else(|| nested_str(&payload, &["payload", "payment", "entity", "status"]));

    if let Some(ref pool) = state.db_pool {
        let inserted = sqlx::query(
            r#"
            INSERT INTO razorpay_events (
                event_id, event_type, subscription_id, payment_id, order_id, signature, payload
            )
            VALUES ($1, $2, $3, $4, $5, $6, $7)
            ON CONFLICT (event_id) DO NOTHING
            "#,
        )
        .bind(&event_id)
        .bind(&event_type)
        .bind(subscription_id.as_deref())
        .bind(payment_id.as_deref())
        .bind(order_id.as_deref())
        .bind(&signature)
        .bind(&payload)
        .execute(&**pool)
        .await
        .map_err(|error| {
            tracing::error!(%error, "Failed to record Razorpay webhook event");
            StatusCode::INTERNAL_SERVER_ERROR
        })?
        .rows_affected()
            == 1;

        if !inserted {
            return Ok(Json(RazorpayWebhookResponse {
                received: true,
                processed: false,
                message: "Duplicate event skipped".to_string(),
            }));
        }

        if let (Some(subscription_id), Some(status)) =
            (subscription_id.as_deref(), status.as_deref())
        {
            sqlx::query(
                r#"
                UPDATE subscriptions
                SET status = $1, updated_at = NOW()
                WHERE subscription_id::text = $2
                "#,
            )
            .bind(status)
            .bind(subscription_id)
            .execute(&**pool)
            .await
            .map_err(|error| {
                tracing::error!(%error, "Failed to update Razorpay subscription status");
                StatusCode::INTERNAL_SERVER_ERROR
            })?;
        }

        sqlx::query(
            r#"
            UPDATE razorpay_events
            SET processed = true, processed_at = NOW()
            WHERE event_id = $1
            "#,
        )
        .bind(&event_id)
        .execute(&**pool)
        .await
        .map_err(|error| {
            tracing::error!(%error, "Failed to mark Razorpay event processed");
            StatusCode::INTERNAL_SERVER_ERROR
        })?;
    }

    Ok(Json(RazorpayWebhookResponse {
        received: true,
        processed: true,
        message: "Event processed successfully".to_string(),
    }))
}

fn verify_razorpay_signature(body: &[u8], signature: &str, secret: &str) -> bool {
    let mut mac =
        HmacSha256::new_from_slice(secret.as_bytes()).expect("HMAC accepts any key length");
    mac.update(body);
    let Ok(provided) = hex::decode(signature) else {
        return false;
    };
    mac.verify_slice(&provided).is_ok()
}

fn extract_str(payload: &Value, keys: &[&str]) -> Option<String> {
    keys.iter()
        .find_map(|key| payload.get(*key)?.as_str().map(ToString::to_string))
}

fn nested_str(payload: &Value, path: &[&str]) -> Option<String> {
    let mut value = payload;
    for key in path {
        value = value.get(*key)?;
    }
    value.as_str().map(ToString::to_string)
}

fn payload_hash_id(body: &[u8]) -> String {
    use sha2::Digest;
    let digest = Sha256::digest(body);
    format!("rzp_{}", hex::encode(digest))
}
