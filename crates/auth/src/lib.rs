//! Clerk JWT authentication and webhook verification for RaptorFlow.
//!
//! Handles auth on the Axum HTTP layer. Validates Clerk-issued JWTs using
//! JWKS and extracts tenant context from Clerk org claims.
//!
//! ## Key types
//!
//! - [`ClerkClient`] — Clerk API client for user/org lookup
//! - [`JwtValidator`] — JWT validation using Clerk's JWKS endpoint
//! - [`Claims`] — JWT claims with Clerk org claim extraction
//! - [`TenantContext`] — extracted from JWT `o` claim and mapped to the internal org UUID
//! - [`OrgContext`] — runtime tenant context (`org_id` + role)
//!
//! ## Auth flow
//!
//! 1. Clerk issues JWT with the active org claim under `o`
//! 2. `JwtValidator::validate()` fetches JWKS and verifies signature + expiry
//! 3. `Claims::org_context()` maps the Clerk org id to the internal UUID tenant id
//! 4. `AuthMiddleware` in `http` attaches `TenantContext` to the request extension
//!
//! ## Webhooks
//!
//! Clerk webhook events are handled in `clerk.rs` — `user.created`, `user.updated`,
//! `session.created`, etc. update `org_users` table.

pub mod clerk;
pub mod error;
pub mod jwt;

pub use clerk::{ClerkClient, ClerkWebhookEvent};
pub use error::AuthError;
pub use jwt::{
    Claims, ClerkOrganizationClaim, JwtValidator, TenantContext, derive_internal_org_id,
};

use uuid::Uuid;

#[derive(Debug, Clone)]
pub struct OrgContext {
    pub org_id: Uuid,
    pub org_role: String,
}

impl Claims {
    pub fn org_context(&self) -> Option<OrgContext> {
        let org_id = self.org_id.or_else(|| {
            self.organization
                .as_ref()
                .map(|claim| derive_internal_org_id(&claim.id))
        })?;

        let org_role = self.org_role.clone().or_else(|| {
            self.organization.as_ref().and_then(|claim| {
                claim.rol.as_ref().map(|role| {
                    if role.starts_with("org:") {
                        role.clone()
                    } else {
                        format!("org:{role}")
                    }
                })
            })
        })?;

        Some(OrgContext { org_id, org_role })
    }
}
