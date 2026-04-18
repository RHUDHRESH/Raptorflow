use axum::{
    body::Body,
    extract::{Extension, State},
    http::{Method, Request as HttpRequest, StatusCode, header::AUTHORIZATION},
    middleware::Next,
    response::Response,
};
use std::sync::Arc;

use raptorflow_auth::{Claims, TenantContext};

use super::AppState;

#[derive(Clone)]
pub struct AuthContext {
    pub claims: Claims,
    pub tenant: TenantContext,
}

impl AuthContext {
    pub fn new(claims: Claims, tenant: TenantContext) -> Self {
        Self { claims, tenant }
    }
}

pub async fn auth_middleware(
    State(state): State<Arc<AppState>>,
    request: HttpRequest<Body>,
    next: Next,
) -> Result<Response, StatusCode> {
    if request.method() == Method::OPTIONS {
        return Ok(next.run(request).await);
    }

    // Use dev bypass if enabled (for local development only)
    if state.settings.allow_insecure_dev_auth {
        return crate::middleware::dev_bypass::dev_auth_middleware(state, request, next).await;
    }

    let auth_header = request
        .headers()
        .get(AUTHORIZATION)
        .and_then(|v| v.to_str().ok());

    let token = auth_header
        .and_then(|h| h.strip_prefix("Bearer "))
        .ok_or(StatusCode::UNAUTHORIZED)?;

    let claims = state
        .auth_validator
        .validate(token)
        .await
        .map_err(|_| StatusCode::UNAUTHORIZED)?;

    let tenant = super::tenant::extract_tenant(&claims).map_err(|_| StatusCode::FORBIDDEN)?;

    let auth_context = AuthContext::new(claims, tenant);
    let tenant_context = auth_context.tenant.clone();

    let mut request = request;
    request.extensions_mut().insert(auth_context);
    request.extensions_mut().insert(tenant_context);

    Ok(next.run(request).await)
}

pub async fn require_auth(
    Extension(auth): Extension<AuthContext>,
) -> Result<AuthContext, StatusCode> {
    Ok(auth)
}
