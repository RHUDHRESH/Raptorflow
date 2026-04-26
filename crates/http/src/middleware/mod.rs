pub mod auth;
pub mod rate_limit;
pub mod role_guard;
pub mod tenant;
pub mod trace;

use raptorflow_auth::JwtValidator;
use raptorflow_aws::bedrock::BedrockInferenceClient;
use raptorflow_db::TenantDbPool;
use raptorflow_search::SearchClient;
use std::sync::Arc;

pub use auth::AuthContext;

#[derive(Clone)]
pub struct AppState {
    pub db_pool: Option<Arc<sqlx::PgPool>>,
    pub tenant_pool: Option<TenantDbPool>,
    pub bedrock: Option<Arc<BedrockInferenceClient>>,
    pub search: Option<Arc<SearchClient>>,
    pub auth_validator: Arc<JwtValidator>,
    pub settings: Arc<raptorflow_config::Settings>,
}

impl AppState {
    pub fn new(
        db_pool: Option<Arc<sqlx::PgPool>>,
        bedrock: Option<Arc<BedrockInferenceClient>>,
        search: Option<Arc<SearchClient>>,
        settings: Arc<raptorflow_config::Settings>,
    ) -> Self {
        let tenant_pool = db_pool.as_ref().map(|p| TenantDbPool::new((**p).clone()));
        Self {
            db_pool,
            tenant_pool,
            bedrock,
            search,
            auth_validator: Arc::new(JwtValidator::new(
                settings.clerk_issuer.clone(),
                settings.clerk_jwks_url.clone(),
                settings.clerk_audience.clone(),
            )),
            settings,
        }
    }
}

impl axum::extract::FromRef<AppState> for TenantDbPool {
    fn from_ref(state: &AppState) -> Self {
        state
            .tenant_pool
            .clone()
            .expect("tenant_pool not configured")
    }
}
