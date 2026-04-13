use raptorflow_auth::{Claims, TenantContext};
use uuid::Uuid;

pub fn extract_tenant(claims: &Claims) -> Result<TenantContext, &'static str> {
    let org_ctx = claims.org_context().ok_or("No organization context")?;

    let user_id = claims
        .user_id
        .as_ref()
        .and_then(|s| Uuid::parse_str(s).ok())
        .ok_or("Invalid or missing user_id in token")?;

    if user_id == Uuid::nil() {
        return Err("Invalid nil user_id in token");
    }

    Ok(TenantContext {
        org_id: org_ctx.org_id,
        user_id,
        role: org_ctx.org_role,
    })
}

pub fn require_org(claims: &Claims) -> Result<TenantContext, &'static str> {
    extract_tenant(claims)
}
