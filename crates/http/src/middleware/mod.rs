pub mod auth;
pub mod dev_bypass;
pub mod rate_limit;
pub mod role_guard;
pub mod tenant;
pub mod trace;

use raptorflow_auth::JwtValidator;
use raptorflow_cache::CacheService;
use std::sync::Arc;

pub use auth::AuthContext;

#[derive(Clone)]
pub struct AppState {
    pub db_pool: Option<Arc<sqlx::PgPool>>,
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
        Self {
            db_pool,
            auth_validator: Arc::new(JwtValidator::new(clerk_domain.clone())),
            clerk_domain,
            settings,
            cache_service,
        }
    }
}
