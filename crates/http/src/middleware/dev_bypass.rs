use axum::{
    body::Body,
    http::{Request as HttpRequest, StatusCode, header::AUTHORIZATION},
    middleware::Next,
    response::Response,
};
use std::sync::Arc;
use uuid::Uuid;

use crate::middleware::AppState;
use raptorflow_auth::TenantContext;

#[derive(Clone)]
pub struct DevAuthContext {
    pub claims: DevClaims,
    pub tenant: TenantContext,
}

impl DevAuthContext {
    pub fn into_auth_context(self) -> super::auth::AuthContext {
        // Convert dev claims to real Claims for compatibility
        let org_id = self.tenant.org_id;
        let role = self.tenant.role.clone();
        let user_id = self.tenant.user_id;

        let claims = raptorflow_auth::Claims {
            iss: "dev-bypass".to_string(),
            sub: self.claims.sub,
            iat: chrono::Utc::now().timestamp() as u64,
            exp: (chrono::Utc::now() + chrono::Duration::hours(24)).timestamp() as u64,
            org_id: Some(org_id),
            org_role: Some(role),
            user_id: Some(user_id.to_string()),
            email: self.claims.email,
        };

        super::auth::AuthContext::new(claims, self.tenant)
    }
}

#[derive(Clone)]
pub struct DevClaims {
    pub sub: String,
    pub org_id: Option<Uuid>,
    pub org_role: Option<String>,
    pub user_id: Option<Uuid>,
    pub email: Option<String>,
}

impl From<DevClaims> for DevAuthContext {
    fn from(claims: DevClaims) -> Self {
        let org_id = claims.org_id.unwrap_or_else(|| Uuid::parse_str("a1b2c3d4-e5f6-7890-abcd-ef1234567890").unwrap());
        let user_id = claims.user_id.unwrap_or_else(|| Uuid::parse_str("01234567-89ab-cdef-0123-456789abcdef").unwrap());
        let role = claims.org_role.clone().unwrap_or_else(|| "admin".to_string());

        let tenant = TenantContext {
            org_id,
            user_id,
            role,
        };

        Self { claims, tenant }
    }
}



pub async fn dev_auth_middleware(
    request: HttpRequest<Body>,
    next: Next,
) -> Result<Response, StatusCode> {
    let state = request
        .extensions()
        .get::<Arc<AppState>>()
        .cloned()
        .ok_or(StatusCode::INTERNAL_SERVER_ERROR)?;

    // Check if dev auth is enabled
    if !state.settings.allow_insecure_dev_auth {
        return Err(StatusCode::UNAUTHORIZED);
    }

    // Extract token for validation (even if we bypass, we should check format)
    let auth_header = request
        .headers()
        .get(AUTHORIZATION)
        .and_then(|v| v.to_str().ok());

    let token = auth_header
        .and_then(|h| h.strip_prefix("Bearer "))
        .ok_or(StatusCode::UNAUTHORIZED)?;

    // For dev bypass, accept any non-empty token
    if token.trim().is_empty() {
        return Err(StatusCode::UNAUTHORIZED);
    }

    // Create dev claims with default values
    let claims = DevClaims {
        sub: "dev-user".to_string(),
        org_id: Some(Uuid::parse_str("a1b2c3d4-e5f6-7890-abcd-ef1234567890").unwrap()),
        org_role: Some("admin".to_string()),
        user_id: Some(Uuid::parse_str("01234567-89ab-cdef-0123-456789abcdef").unwrap()),
        email: Some("dev@example.com".to_string()),
    };

    let dev_auth_context = DevAuthContext::from(claims);
    let auth_context = dev_auth_context.into_auth_context();
    let tenant_context = auth_context.tenant.clone();

    let mut request = request;
    request.extensions_mut().insert(auth_context);
    request.extensions_mut().insert(tenant_context);

    Ok(next.run(request).await)
}
