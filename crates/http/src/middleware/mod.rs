pub mod auth;
pub mod dev_bypass;
pub mod rate_limit;
pub mod role_guard;
pub mod tenant;
pub mod trace;

use raptorflow_auth::JwtValidator;
use raptorflow_cache::CacheService;
use raptorflow_db::TenantDbPool;
use std::sync::Arc;

pub use auth::AuthContext;

#[derive(Clone)]
pub struct AppState {
    pub db_pool: Option<Arc<sqlx::PgPool>>,
    pub tenant_pool: Option<TenantDbPool>,
    pub auth_validator: Arc<JwtValidator>,
    pub clerk_domain: String,
    pub settings: Arc<raptorflow_config::Settings>,
    pub cache_service: Option<Arc<CacheService>>,
}

impl AppState {
    pub fn new(
        db_pool: Option<Arc<sqlx::PgPool>>,
        clerk_domain: String,
        settings: Arc<raptorflow_config::Settings>,
        cache_service: Option<Arc<CacheService>>,
    ) -> Self {
        let tenant_pool = db_pool.as_ref().map(|p| TenantDbPool::new((**p).clone()));
        Self {
            db_pool,
            tenant_pool,
            auth_validator: Arc::new(JwtValidator::new(clerk_domain.clone())),
            clerk_domain,
            settings,
            cache_service,
        }
    }
}

impl axum::extract::FromRef<AppState> for TenantDbPool {
    fn from_ref(state: &AppState) -> Self {
        state.tenant_pool.clone().expect("tenant_pool not configured")
    }
}
