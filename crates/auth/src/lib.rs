//! Clerk JWT authentication and webhook verification for RaptorFlow.
//!
//! Handles auth on the Axum HTTP layer. Validates Clerk-issued JWTs using
//! JWKS and extracts tenant context (`org_id`) from JWT claims.
//!
//! ## Key types
//!
//! - [`ClerkClient`] — Clerk API client for user/org lookup
//! - [`JwtValidator`] — JWT validation using Clerk's JWKS endpoint
//! - [`Claims`] — JWT claims with `org_id` extraction
//! - [`TenantContext`] — extracted from JWT `org_slug` or `org_id` claim
//! - [`OrgContext`] — runtime tenant context (`org_id` + role)
//!
//! ## Auth flow
//!
//! 1. Clerk issues JWT with `org_id` / `org_slug` in `public_metadata`
//! 2. `JwtValidator::validate()` fetches JWKS and verifies signature + expiry
//! 3. `Claims::org_context()` extracts `OrgContext` for the request
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
pub use jwt::{Claims, JwtValidator, TenantContext};

use uuid::Uuid;

#[derive(Debug, Clone)]
pub struct OrgContext {
    pub org_id: Uuid,
    pub org_role: String,
}

impl Claims {
    pub fn org_context(&self) -> Option<OrgContext> {
        self.org_id.and_then(|org_id| {
            self.org_role.as_ref().map(|role| OrgContext {
                org_id,
                org_role: role.clone(),
            })
        })
    }
}
