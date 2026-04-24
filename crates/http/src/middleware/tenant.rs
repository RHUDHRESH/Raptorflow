use raptorflow_auth::{Claims, TenantContext};

pub fn extract_tenant(claims: &Claims) -> Result<TenantContext, &'static str> {
    let org_ctx = claims.org_context().ok_or("No organization context")?;

    let user_id = claims
        .user_id
        .as_deref()
        .or(Some(claims.sub.as_str()))
        .filter(|s| !s.is_empty())
        .ok_or("Invalid or missing user_id in token")?
        .to_string();

    let clerk_org_id = claims
        .organization
        .as_ref()
        .map(|org| org.id.clone())
        .ok_or("Invalid or missing org claim in token")?;

    Ok(TenantContext {
        org_id: org_ctx.org_id,
        clerk_org_id,
        user_id,
        role: org_ctx.org_role,
    })
}

pub fn require_org(claims: &Claims) -> Result<TenantContext, &'static str> {
    extract_tenant(claims)
}
