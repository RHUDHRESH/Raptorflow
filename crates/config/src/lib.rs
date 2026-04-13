//! Environment configuration for the RaptorFlow backend.
//!
//! All environment variables are parsed into the [`Settings`] struct. No global
//! state — call [`Settings::from_env()`] and pass the resulting `Arc<Settings>`
//! into Axum extensions or service constructors.
//!
//! ## Variable source
//!
//! Variables are read from the process environment at startup. Defaults exist for
//! all development variables so the service starts without a `.env` file in dev
//! mode. Production deployments MUST supply real values via environment variables
//! or a secret manager (AWS Secrets Manager in the ECS task definition).
//!
//! ## Structure
//!
//! - `APP_ENV` / `AWS_REGION` — environment and region
//! - `RAPTORFLOW_DATABASE_URL` / `RAPTORFLOW_DIRECT_DATABASE_URL` — PgBouncer (port 6432) and direct PG (5432)
//! - `RAPTORFLOW_DRAGONFLY_URL` — DragonflyDB for cache
//! - `RAPTORFLOW_QDRANT_URL` — Qdrant for vector search
//! - `RAPTORFLOW_S3_BUCKET` + SQS queues — storage and async jobs
//! - `RAPTORFLOW_GCP_API_KEY` — Gemini AI inference
//! - Clerk, Razorpay, Resend — auth, payments, email
//! - `RAPTORFLOW_SENTRY_DSN` — error reporting

use anyhow::Result;
use serde::Serialize;
use std::env;

#[derive(Debug, Clone, Serialize)]
pub struct Settings {
    pub app_env: String,
    pub frontend_url: String,
    pub bind_addr: String,
    pub aws_region: String,
    pub database_url: String,
    pub direct_database_url: String,
    pub dragonfly_url: String,
    pub qdrant_url: String,
    pub s3_bucket: String,
    pub sqs_base_url: String,
    pub sqs_embedding_queue: String,
    pub sqs_content_queue: String,
    pub gcp_api_key: String,
    pub clerk_jwks_url: String,
    pub clerk_issuer: String,
    pub clerk_audience: Option<String>,
    pub clerk_webhook_secret: Option<String>,
    pub allow_insecure_dev_auth: bool,
    pub dev_bearer_token: String,
    pub razorpay_key_id: String,
    pub razorpay_key_secret: String,
    pub razorpay_webhook_secret: Option<String>,
    pub resend_api_key: String,
    pub resend_from_email: String,
    pub resend_webhook_secret: Option<String>,
    pub webhook_timestamp_tolerance_seconds: u64,
    pub sentry_dsn: String,
}

impl Settings {
    pub fn from_env() -> Result<Self> {
        Ok(Self {
            app_env: read("APP_ENV", "dev"),
            frontend_url: read("RAPTORFLOW_FRONTEND_URL", "http://localhost:3000"),
            bind_addr: read("RAPTORFLOW_BIND_ADDR", "0.0.0.0:8080"),
            aws_region: read("AWS_REGION", "ap-south-1"),
            database_url: read(
                "RAPTORFLOW_DATABASE_URL",
                "postgres://raptorflow:raptorflow@localhost:6432/raptorflow",
            ),
            direct_database_url: read(
                "RAPTORFLOW_DIRECT_DATABASE_URL",
                "postgres://raptorflow:raptorflow@localhost:5432/raptorflow",
            ),
            dragonfly_url: read("RAPTORFLOW_DRAGONFLY_URL", "redis://localhost:6379"),
            qdrant_url: read("RAPTORFLOW_QDRANT_URL", "http://localhost:6333"),
            s3_bucket: read("RAPTORFLOW_S3_BUCKET", "raptorflow-dev"),
            sqs_base_url: read("RAPTORFLOW_SQS_BASE_URL", "https://sqs.ap-south-1.amazonaws.com"),
            sqs_embedding_queue: read("RAPTORFLOW_SQS_EMBEDDING_QUEUE", "raptorflow-dev-embedding"),
            sqs_content_queue: read(
                "RAPTORFLOW_SQS_CONTENT_QUEUE",
                "raptorflow-dev-content-pregeneration",
            ),
            gcp_api_key: read("RAPTORFLOW_GCP_API_KEY", ""),
            clerk_jwks_url: read(
                "RAPTORFLOW_CLERK_JWKS_URL",
                "https://example.clerk.accounts.dev/.well-known/jwks.json",
            ),
            clerk_issuer: read(
                "RAPTORFLOW_CLERK_ISSUER",
                "https://example.clerk.accounts.dev",
            ),
            clerk_audience: optional("RAPTORFLOW_CLERK_AUDIENCE"),
            clerk_webhook_secret: optional("RAPTORFLOW_CLERK_WEBHOOK_SECRET"),
            allow_insecure_dev_auth: read("RAPTORFLOW_ALLOW_INSECURE_DEV_AUTH", "true")
                .parse()
                .unwrap_or(true),
            dev_bearer_token: read("RAPTORFLOW_DEV_BEARER_TOKEN", "raptorflow-dev-token"),
            razorpay_key_id: read("RAPTORFLOW_RAZORPAY_KEY_ID", ""),
            razorpay_key_secret: read("RAPTORFLOW_RAZORPAY_KEY_SECRET", ""),
            razorpay_webhook_secret: optional("RAPTORFLOW_RAZORPAY_WEBHOOK_SECRET"),
            resend_api_key: read("RAPTORFLOW_RESEND_API_KEY", ""),
            resend_from_email: read("RAPTORFLOW_RESEND_FROM_EMAIL", "onboarding@resend.dev"),
            resend_webhook_secret: optional("RAPTORFLOW_RESEND_WEBHOOK_SECRET"),
            webhook_timestamp_tolerance_seconds: read(
                "RAPTORFLOW_WEBHOOK_TIMESTAMP_TOLERANCE_SECONDS",
                "300",
            )
            .parse()
            .unwrap_or(300),
            sentry_dsn: read("RAPTORFLOW_SENTRY_DSN", ""),
        })
    }
}

fn read(name: &str, default: &str) -> String {
    env::var(name).unwrap_or_else(|_| default.to_string())
}

fn optional(name: &str) -> Option<String> {
    env::var(name).ok().filter(|value| !value.trim().is_empty())
}
