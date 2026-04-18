use crate::error::AuthError;
use jsonwebtoken::{Algorithm, DecodingKey, Validation, decode, decode_header};
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
}

#[derive(Debug, Clone)]
pub struct TenantContext {
    pub org_id: Uuid,
    pub user_id: Uuid,
    pub role: String,
}

pub struct JwtValidator {
    decoding_keys: Arc<RwLock<HashMap<String, DecodingKey>>>,
    clerk_domain: String,
}

impl JwtValidator {
    pub fn new(clerk_domain: String) -> Self {
        Self {
            decoding_keys: Arc::new(RwLock::new(HashMap::new())),
            clerk_domain,
        }
    }

    pub fn clerk_domain(&self) -> String {
        self.clerk_domain.clone()
    }

    pub async fn validate(&self, token: &str) -> Result<Claims, AuthError> {
        let header = decode_header(token)?;
        let kid = header.kid.clone().ok_or(AuthError::InvalidToken)?;

        let decoding_key = self.get_decoding_key(&kid).await?;

        let mut validation = Validation::new(Algorithm::RS256);
        validation.set_issuer(&[&format!("https://{}/", self.clerk_domain)]);

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
        let jwks_url = format!("https://{}/.well-known/jwks.json", self.clerk_domain);
        let response = reqwest::get(&jwks_url).await?.json::<Jwks>().await?;

        let mut keys = self.decoding_keys.write().await;
        for key in &response.keys {
            if let Ok(decoding_key) = DecodingKey::from_rsa_components(&key.n, &key.e) {
                keys.insert(key.kid.clone(), decoding_key);
            }
        }

        keys.get(kid).cloned().ok_or(AuthError::InvalidToken)
    }
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
