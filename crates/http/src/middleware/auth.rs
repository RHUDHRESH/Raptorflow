use axum::{
    body::Body,
    extract::Extension,
    http::{Request as HttpRequest, StatusCode, header::AUTHORIZATION},
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
    request: HttpRequest<Body>,
    next: Next,
) -> Result<Response, StatusCode> {
    let state = request
        .extensions()
        .get::<Arc<AppState>>()
        .cloned()
        .ok_or(StatusCode::INTERNAL_SERVER_ERROR)?;

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

    let tenant = super::tenant::extract_tenant(&claims)
        .map_err(|_| StatusCode::FORBIDDEN)?;

    let auth_context = AuthContext::new(claims, tenant);

    let mut request = request;
    request.extensions_mut().insert(auth_context);

    Ok(next.run(request).await)
}

pub async fn require_auth(
    Extension(auth): Extension<AuthContext>,
) -> Result<AuthContext, StatusCode> {
    Ok(auth)
}
