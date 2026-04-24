use crate::error::AuthError;
use base64::{Engine as _, engine::general_purpose::STANDARD};
use hmac::{Hmac, Mac};
use serde::Deserialize;
use sha2::Sha256;
use std::time::{SystemTime, UNIX_EPOCH};
use subtle::ConstantTimeEq;

type HmacSha256 = Hmac<Sha256>;

#[derive(Debug, Clone)]
pub struct ClerkClient {
    webhook_secret: String,
}

#[derive(Debug, Deserialize)]
pub struct ClerkWebhookEvent {
    pub id: String,
    #[serde(rename = "type")]
    pub event_type: String,
    pub data: serde_json::Value,
}

#[derive(Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ClerkUserData {
    pub id: String,
    pub email_addresses: Vec<ClerkEmail>,
    pub first_name: Option<String>,
    pub last_name: Option<String>,
    #[serde(default)]
    pub unsafe_metadata: Option<serde_json::Value>,
}

#[derive(Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ClerkEmail {
    pub email_address: String,
}

#[derive(Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ClerkOrgData {
    pub id: String,
    pub name: String,
    pub slug: Option<String>,
}

#[derive(Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ClerkMembershipData {
    pub id: String,
    pub role: String,
    pub organization: Option<ClerkOrgRef>,
    pub public_user_data: Option<ClerkPublicUserData>,
}

#[derive(Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ClerkOrgRef {
    pub id: String,
    pub name: Option<String>,
}

#[derive(Debug, Deserialize)]
#[serde(rename_all = "camelCase")]
pub struct ClerkPublicUserData {
    pub user_id: String,
    pub email_addresses: Vec<ClerkEmail>,
}

impl ClerkClient {
    pub fn new(webhook_secret: String) -> Self {
        Self { webhook_secret }
    }

    pub fn verify_webhook_signature(
        &self,
        payload: &[u8],
        message_id: &str,
        timestamp: &str,
        signature_header: &str,
        tolerance_seconds: u64,
    ) -> Result<(), AuthError> {
        let mut mac = HmacSha256::new_from_slice(self.webhook_secret.as_bytes())
            .map_err(|_| AuthError::InvalidWebhookSignature)?;

        let timestamp_value = timestamp
            .parse::<u64>()
            .map_err(|_| AuthError::InvalidWebhookSignature)?;
        let now = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .map_err(|_| AuthError::InvalidWebhookSignature)?
            .as_secs();

        let skew = now.abs_diff(timestamp_value);
        if skew > tolerance_seconds {
            return Err(AuthError::InvalidWebhookSignature);
        }

        let mut signed_payload = format!("{message_id}.{timestamp}.").into_bytes();
        signed_payload.extend_from_slice(payload);
        mac.update(&signed_payload);

        let expected = STANDARD.encode(mac.finalize().into_bytes());

        for candidate in signature_header.split_whitespace() {
            let candidate = candidate
                .strip_prefix("v1,")
                .or_else(|| candidate.strip_prefix("v1="))
                .unwrap_or(candidate);

            if expected.as_bytes().ct_eq(candidate.as_bytes()).unwrap_u8() == 1 {
                return Ok(());
            }
        }

        Err(AuthError::InvalidWebhookSignature)
    }

    pub fn parse_webhook_event(&self, payload: &[u8]) -> Result<ClerkWebhookEvent, AuthError> {
        serde_json::from_slice(payload).map_err(|e| AuthError::ClerkApiError(e.to_string()))
    }
}
