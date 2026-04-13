use raptorflow_auth::TenantContext;

pub fn check_role(tenant: &TenantContext, required_roles: &[&str]) -> bool {
    required_roles.iter().any(|role| tenant.role == **role)
}

pub fn require_admin(tenant: &TenantContext) -> bool {
    check_role(tenant, &["org:admin"])
}

pub fn require_member(tenant: &TenantContext) -> bool {
    check_role(tenant, &["org:admin", "org:member"])
}
