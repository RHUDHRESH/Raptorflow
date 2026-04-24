use crate::error::AuthError;
use jsonwebtoken::{Algorithm, DecodingKey, Validation, decode, decode_header};
use sha2::{Digest, Sha256};
use serde::{Deserialize, Serialize};
use std::collections::HashMap;
use std::sync::Arc;
use tokio::sync::RwLock;
use uuid::Uuid;

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct Claims {
    pub iss: String,
    pub sub: String,
    pub iat: u64,
    pub exp: u64,
    pub org_id: Option<Uuid>,
    pub org_role: Option<String>,
    pub user_id: Option<String>,
    pub email: Option<String>,
    #[serde(rename = "o")]
    pub organization: Option<ClerkOrganizationClaim>,
}

#[derive(Debug, Clone)]
pub struct TenantContext {
    pub org_id: Uuid,
    pub clerk_org_id: String,
    pub user_id: String,
    pub role: String,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct ClerkOrganizationClaim {
    pub id: String,
    #[serde(default)]
    pub slg: Option<String>,
    #[serde(default)]
    pub rol: Option<String>,
    #[serde(default)]
    pub per: Option<Vec<String>>,
}

pub struct JwtValidator {
    decoding_keys: Arc<RwLock<HashMap<String, DecodingKey>>>,
    issuer: String,
    jwks_url: String,
    audience: Option<String>,
}

impl JwtValidator {
    pub fn new(issuer: String, jwks_url: String, audience: Option<String>) -> Self {
        let issuer = issuer.trim_end_matches('/').to_string();
        Self {
            decoding_keys: Arc::new(RwLock::new(HashMap::new())),
            issuer,
            jwks_url,
            audience,
        }
    }

    pub fn issuer(&self) -> String {
        self.issuer.clone()
    }

    pub async fn validate(&self, token: &str) -> Result<Claims, AuthError> {
        let header = decode_header(token)?;
        let kid = header.kid.clone().ok_or(AuthError::InvalidToken)?;

        let decoding_key = self.get_decoding_key(&kid).await?;

        let mut validation = Validation::new(Algorithm::RS256);
        validation.set_issuer(&[self.issuer.as_str()]);
        if let Some(aud) = &self.audience {
            validation.set_audience(&[aud.as_str()]);
        }

        let token_data = decode::<Claims>(token, &decoding_key, &validation)?;
        Ok(token_data.claims)
    }

    async fn get_decoding_key(&self, kid: &str) -> Result<DecodingKey, AuthError> {
        {
            let keys = self.decoding_keys.read().await;
            if let Some(key) = keys.get(kid) {
                return Ok(key.clone());
            }
        }

        self.fetch_and_cache_jwks(kid).await
    }

    async fn fetch_and_cache_jwks(&self, kid: &str) -> Result<DecodingKey, AuthError> {
        let response = reqwest::get(&self.jwks_url).await?.json::<Jwks>().await?;

        let mut keys = self.decoding_keys.write().await;
        for key in &response.keys {
            if let Ok(decoding_key) = DecodingKey::from_rsa_components(&key.n, &key.e) {
                keys.insert(key.kid.clone(), decoding_key);
            }
        }

        keys.get(kid).cloned().ok_or(AuthError::InvalidToken)
    }
}

pub fn derive_internal_org_id(clerk_org_id: &str) -> Uuid {
    let mut hasher = Sha256::new();
    hasher.update(b"raptorflow-clerk-org:");
    hasher.update(clerk_org_id.as_bytes());
    let digest = hasher.finalize();

    let mut bytes = [0u8; 16];
    bytes.copy_from_slice(&digest[..16]);
    bytes[6] = (bytes[6] & 0x0f) | 0x50;
    bytes[8] = (bytes[8] & 0x3f) | 0x80;
    Uuid::from_bytes(bytes)
}

#[derive(Debug, Deserialize)]
struct Jwks {
    keys: Vec<Jwk>,
}

#[derive(Debug, Deserialize)]
struct Jwk {
    kid: String,
    n: String,
    e: String,
}

pub fn extract_bearer_token(auth_header: &str) -> Option<&str> {
    if auth_header.starts_with("Bearer ") {
        Some(&auth_header[7..])
    } else {
        None
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_issuer_normalization_no_double_prepend() {
        let validator = JwtValidator::new(
            "https://example.clerk.accounts.dev".to_string(),
            "https://example.clerk.accounts.dev/.well-known/jwks.json".to_string(),
            None,
        );
        assert_eq!(validator.issuer(), "https://example.clerk.accounts.dev");
        assert_eq!(
            validator.jwks_url,
            "https://example.clerk.accounts.dev/.well-known/jwks.json"
        );
    }

    #[test]
    fn test_issuer_trims_trailing_slash() {
        let validator = JwtValidator::new(
            "https://example.clerk.accounts.dev/".to_string(),
            "https://example.clerk.accounts.dev/.well-known/jwks.json".to_string(),
            None,
        );
        assert_eq!(validator.issuer(), "https://example.clerk.accounts.dev");
    }

    #[test]
    fn test_jwks_url_unchanged() {
        let url = "https://funky-scorpion-21.clerk.accounts.dev/.well-known/jwks.json";
        let validator = JwtValidator::new(
            "https://funky-scorpion-21.clerk.accounts.dev".to_string(),
            url.to_string(),
            None,
        );
        assert_eq!(validator.jwks_url, url);
    }

    #[test]
    fn test_full_url_issuer_not_double_prepended() {
        let issuer = "https://funky-scorpion-21.clerk.accounts.dev";
        let jwks = "https://funky-scorpion-21.clerk.accounts.dev/.well-known/jwks.json";
        let validator = JwtValidator::new(issuer.to_string(), jwks.to_string(), None);
        let iss = validator.issuer();
        assert!(!iss.starts_with("https://https://"));
    }
}
