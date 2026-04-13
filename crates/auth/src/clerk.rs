use crate::error::AuthError;
use hmac::{Hmac, Mac};
use serde::Deserialize;
use sha2::Sha256;

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
        Self {
            webhook_secret,
        }
    }

    pub fn verify_webhook_signature(&self, payload: &[u8], signature: &str) -> Result<(), AuthError> {
        let mut mac = HmacSha256::new_from_slice(self.webhook_secret.as_bytes())
            .map_err(|_| AuthError::InvalidWebhookSignature)?;
        mac.update(payload);

        let expected = hex::encode(mac.finalize().into_bytes());
        let signature_base = signature.trim_start_matches("v1=");

        if signature_base.eq_ignore_ascii_case(&expected) {
            Ok(())
        } else {
            Err(AuthError::InvalidWebhookSignature)
        }
    }

    pub fn parse_webhook_event(&self, payload: &[u8]) -> Result<ClerkWebhookEvent, AuthError> {
        serde_json::from_slice(payload).map_err(|e| AuthError::ClerkApiError(e.to_string()))
    }
}
