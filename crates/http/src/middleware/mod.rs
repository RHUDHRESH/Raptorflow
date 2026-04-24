pub mod auth;
pub mod rate_limit;
pub mod role_guard;
pub mod tenant;
pub mod trace;

use raptorflow_aws::bedrock::BedrockInferenceClient;
use raptorflow_auth::JwtValidator;
use raptorflow_db::TenantDbPool;
use std::sync::Arc;

pub use auth::AuthContext;

#[derive(Clone)]
pub struct AppState {
    pub db_pool: Option<Arc<sqlx::PgPool>>,
    pub tenant_pool: Option<TenantDbPool>,
    pub bedrock: Option<Arc<BedrockInferenceClient>>,
    pub auth_validator: Arc<JwtValidator>,
    pub clerk_domain: String,
    pub settings: Arc<raptorflow_config::Settings>,
}

impl AppState {
    pub fn new(
        db_pool: Option<Arc<sqlx::PgPool>>,
        bedrock: Option<Arc<BedrockInferenceClient>>,
        clerk_domain: String,
        settings: Arc<raptorflow_config::Settings>,
    ) -> Self {
        let tenant_pool = db_pool.as_ref().map(|p| TenantDbPool::new((**p).clone()));
        Self {
            db_pool,
            tenant_pool,
            bedrock,
            auth_validator: Arc::new(JwtValidator::new(clerk_domain.clone())),
            clerk_domain,
            settings,
        }
    }
}

impl axum::extract::FromRef<AppState> for TenantDbPool {
    fn from_ref(state: &AppState) -> Self {
        state.tenant_pool.clone().expect("tenant_pool not configured")
    }
}
