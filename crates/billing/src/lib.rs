//! Razorpay payment integration for RaptorFlow.
//!
//! Handles India-market payment processing via Razorpay. Supports order creation,
//! subscription management, and webhook signature verification.
//!
//! ## Webhook security
//!
//! All Razorpay webhooks are verified using HMAC-SHA256 before processing.
//! The [`RazorpayWebhookRuntime::verify()`] method performs constant-time
//! signature comparison to prevent timing attacks.
//!
//! ## Key types
//!
//! - [`RazorpayClient`] — direct Razorpay API client (orders, subscriptions, cancel)
//! - [`RazorpayWebhookRuntime`] — webhook verification + parsing
//! - [`RazorpayError`] — typed error enum for config, signature, parse, and API failures
//!
//! ## Routes registered
//!
//! - `POST /api/v1/webhooks/razorpay` — webhook receiver (wire in `webhook_router()`)
//! - `GET /billing/status` — subscription state (stub; wire to DB when subscriptions exist)

use axum::{
    Json, Router,
    body::Bytes,
    extract::Extension,
    http::{HeaderMap, StatusCode},
    response::IntoResponse,
    routing::{get, post},
};
use hmac::{Hmac, Mac};
use serde::{Deserialize, Serialize};
use serde_json::{Value, json};
use sha2::Sha256;
use std::sync::Arc;

type HmacSha256 = Hmac<Sha256>;

#[derive(Clone)]
pub struct RazorpayWebhookRuntime {
    pub settings: Arc<raptorflow_config::Settings>,
}

impl RazorpayWebhookRuntime {
    pub fn from_settings(settings: Arc<raptorflow_config::Settings>) -> Self {
        Self { settings }
    }

    pub fn verify(&self, payload: &Bytes, signature: &str) -> Result<RazorpayWebhookVerified, RazorpayError> {
        let secret = self.settings.razorpay_webhook_secret
            .as_ref()
            .ok_or_else(|| RazorpayError::Configuration("Missing webhook secret".to_string()))?;

        let mut mac = HmacSha256::new_from_slice(secret.as_bytes())
            .map_err(|_| RazorpayError::Configuration("HMAC error".to_string()))?;
        mac.update(payload);

        let expected_bytes = mac.finalize().into_bytes();
        let signature_bytes = hex::decode(signature)
            .map_err(|_| RazorpayError::SignatureMismatch)?;

        let mut diff = 0u8;
        if expected_bytes.len() != signature_bytes.len() {
            return Err(RazorpayError::SignatureMismatch);
        }

        for (a, b) in expected_bytes.iter().zip(signature_bytes.iter()) {
            diff |= a ^ b;
        }

        if diff == 0 {
            let parsed = self.parse_webhook(payload)?;
            Ok(RazorpayWebhookVerified {
                webhook_id: parsed.event.clone(),
                event: parsed.event,
                payload: serde_json::json!({
                    "payment": parsed.payload.payment,
                    "subscription": parsed.payload.subscription,
                }),
            })
        } else {
            Err(RazorpayError::SignatureMismatch)
        }
    }

    pub fn parse_webhook(&self, payload: &Bytes) -> Result<razorpay_webhook::WebhookPayload, RazorpayError> {
        serde_json::from_slice(payload)
            .map_err(|e| RazorpayError::ParseError(e.to_string()))
    }
}

pub mod razorpay_webhook {
    use serde::{Deserialize, Serialize};

    #[derive(Debug, Deserialize, Serialize)]
    pub struct WebhookPayload {
        pub event: String,
        pub payload: WebhookEvent,
    }

    #[derive(Debug, Deserialize, Serialize)]
    pub struct WebhookEvent {
        pub payment: Option<PaymentEvent>,
        pub subscription: Option<SubscriptionEvent>,
    }

    #[derive(Debug, Deserialize, Serialize)]
    pub struct PaymentEvent {
        pub entity: PaymentEntity,
    }

    #[derive(Debug, Deserialize, Serialize)]
    pub struct PaymentEntity {
        pub id: String,
        pub amount: i64,
        pub currency: String,
        pub status: String,
        pub order_id: Option<String>,
    }

    #[derive(Debug, Deserialize, Serialize)]
    pub struct SubscriptionEvent {
        pub entity: SubscriptionEntity,
    }

    #[derive(Debug, Deserialize, Serialize)]
    pub struct SubscriptionEntity {
        pub id: String,
        pub status: String,
        pub plan_id: Option<String>,
    }
}

#[derive(Debug)]
pub struct RazorpayWebhookVerified {
    pub webhook_id: String,
    pub event: String,
    pub payload: serde_json::Value,
}

#[derive(Debug)]
pub enum RazorpayError {
    Configuration(String),
    SignatureMismatch,
    ParseError(String),
    ApiError(String),
}

impl std::fmt::Display for RazorpayError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            RazorpayError::Configuration(msg) => write!(f, "Configuration error: {}", msg),
            RazorpayError::SignatureMismatch => write!(f, "Webhook signature mismatch"),
            RazorpayError::ParseError(msg) => write!(f, "Parse error: {}", msg),
            RazorpayError::ApiError(msg) => write!(f, "API error: {}", msg),
        }
    }
}

impl IntoResponse for RazorpayError {
    fn into_response(self) -> axum::response::Response {
        let status = match &self {
            RazorpayError::SignatureMismatch => StatusCode::UNAUTHORIZED,
            RazorpayError::Configuration(_) => StatusCode::INTERNAL_SERVER_ERROR,
            _ => StatusCode::BAD_REQUEST,
        };
        (status, Json(json!({ "error": self.to_string() }))).into_response()
    }
}

pub fn router() -> Router {
    Router::new().route("/", get(billing_state))
}

pub fn webhook_router(settings: Arc<raptorflow_config::Settings>) -> Router {
    let runtime = Arc::new(RazorpayWebhookRuntime::from_settings(settings));
    Router::new()
        .route("/", post(razorpay_webhook))
        .layer(Extension(runtime))
}

async fn billing_state() -> Json<Value> {
    Json(json!({
        "status": "stub",
        "provider": "razorpay",
        "currency": "INR",
        "plans": [
            {
                "tier": "ascend",
                "name": "Ascend",
                "price_inr_monthly": 5000,
                "description": "Perfect for small businesses starting with AI marketing"
            },
            {
                "tier": "glide",
                "name": "Glide",
                "price_inr_monthly": 7000,
                "description": "For growing businesses needing advanced AI insights"
            },
            {
                "tier": "soar",
                "name": "Soar",
                "price_inr_monthly": 10000,
                "description": "Enterprise-grade AI marketing for scaleups"
            },
            {
                "tier": "enterprise",
                "name": "Enterprise",
                "price_inr_monthly": "talk_to_us",
                "description": "Custom solution for large organizations"
            }
        ],
        "grace_period_days": 2,
        "note": "All prices in INR (Indian Rupees)"
    }))
}

async fn razorpay_webhook(
    headers: HeaderMap,
    Extension(runtime): Extension<Arc<RazorpayWebhookRuntime>>,
    body: Bytes,
) -> impl IntoResponse {
    let signature = headers
        .get("x-razorpay-signature")
        .and_then(|v| v.to_str().ok())
        .unwrap_or("");

    match runtime.verify(&body, signature) {
        Ok(verified) => {
            tracing::info!(
                event = verified.event,
                webhook_id = verified.webhook_id,
                "Razorpay webhook verified and received"
            );
            (
                StatusCode::ACCEPTED,
                Json(json!({
                    "status": "accepted",
                    "resource": "razorpay.webhook",
                    "verified": true,
                })),
            ).into_response()
        }
        Err(error) => {
            tracing::warn!(error = ?error, "Razorpay webhook verification failed");
            error.into_response()
        }
    }
}

pub struct RazorpayClient {
    pub key_id: String,
    pub key_secret: String,
    pub base_url: String,
}

impl RazorpayClient {
    pub fn new(key_id: String, key_secret: String) -> Self {
        Self {
            key_id,
            key_secret,
            base_url: "https://api.razorpay.com/v1".to_string(),
        }
    }

    pub async fn create_order(&self, amount: i64, currency: &str) -> Result<OrderCreated, RazorpayError> {
        let client = reqwest::Client::new();
        
        let response = client
            .post(&format!("{}/orders", self.base_url))
            .basic_auth(&self.key_id, Some(&self.key_secret))
            .json(&OrderRequest {
                amount,
                currency: currency.to_string(),
                receipt: None,
            })
            .send()
            .await
            .map_err(|e| RazorpayError::ApiError(e.to_string()))?;

        if response.status().is_success() {
            response
                .json()
                .await
                .map_err(|e| RazorpayError::ApiError(e.to_string()))
        } else {
            Err(RazorpayError::ApiError(format!("Order creation failed: {}", response.status())))
        }
    }

    pub async fn get_subscription(&self, subscription_id: &str) -> Result<serde_json::Value, RazorpayError> {
        let client = reqwest::Client::new();
        
        let response = client
            .get(&format!("{}/subscriptions/{}", self.base_url, subscription_id))
            .basic_auth(&self.key_id, Some(&self.key_secret))
            .send()
            .await
            .map_err(|e| RazorpayError::ApiError(e.to_string()))?;

        if response.status().is_success() {
            response
                .json()
                .await
                .map_err(|e| RazorpayError::ApiError(e.to_string()))
        } else {
            Err(RazorpayError::ApiError(format!("Get subscription failed: {}", response.status())))
        }
    }

    pub async fn cancel_subscription(&self, subscription_id: &str) -> Result<serde_json::Value, RazorpayError> {
        let client = reqwest::Client::new();
        
        let response = client
            .post(&format!("{}/subscriptions/{}/cancel", self.base_url, subscription_id))
            .basic_auth(&self.key_id, Some(&self.key_secret))
            .send()
            .await
            .map_err(|e| RazorpayError::ApiError(e.to_string()))?;

        if response.status().is_success() {
            response
                .json()
                .await
                .map_err(|e| RazorpayError::ApiError(e.to_string()))
        } else {
            Err(RazorpayError::ApiError(format!("Cancel subscription failed: {}", response.status())))
        }
    }
}

#[derive(Debug, Serialize)]
struct OrderRequest {
    amount: i64,
    currency: String,
    receipt: Option<String>,
}

#[derive(Debug, Deserialize)]
pub struct OrderCreated {
    pub id: String,
    pub entity: String,
    pub amount: i64,
    pub currency: String,
    pub status: String,
}
