use thiserror::Error;

#[derive(Error, Debug)]
pub enum AuthError {
    #[error("Missing authorization header")]
    MissingAuthHeader,

    #[error("Invalid authorization header format")]
    InvalidAuthHeaderFormat,

    #[error("Invalid or expired token")]
    InvalidToken,

    #[error("Token validation failed: {0}")]
    TokenValidationFailed(String),

    #[error("Missing organization context")]
    MissingOrgContext,

    #[error("Insufficient permissions: {0}")]
    InsufficientPermissions(String),

    #[error("Clerk API error: {0}")]
    ClerkApiError(String),

    #[error("Webhook signature verification failed")]
    InvalidWebhookSignature,
}

impl From<jsonwebtoken::errors::Error> for AuthError {
    fn from(err: jsonwebtoken::errors::Error) -> Self {
        AuthError::TokenValidationFailed(err.to_string())
    }
}

impl From<reqwest::Error> for AuthError {
    fn from(err: reqwest::Error) -> Self {
        AuthError::ClerkApiError(err.to_string())
    }
}
