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
//! - `RAPTORFLOW_QDRANT_URL` — Qdrant for vector search
//! - `RAPTORFLOW_QDRANT_API_KEY` — Qdrant Cloud auth key when using hosted clusters
//! - `RAPTORFLOW_S3_BUCKET` + SQS queues — storage and async jobs
//! - `RAPTORFLOW_BEDROCK_REGION` — AWS region for Bedrock (defaults to ap-south-1)
//! - `RAPTORFLOW_BEDROCK_MODEL_STRATEGIST` — Bedrock model ID for strategist tasks (Mistral Large 3)
//! - `RAPTORFLOW_BEDROCK_MODEL_FAST` — Bedrock model ID for fast/council tasks (Ministral 3 8B)
//! - Clerk, Razorpay, Resend — auth, payments, email
//! - `RAPTORFLOW_SENTRY_DSN` / `SENTRY_DSN` — error reporting

use anyhow::{Result, anyhow};
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
    pub qdrant_url: String,
    pub qdrant_api_key: Option<String>,
    pub s3_bucket: String,
    pub sqs_base_url: String,
    pub sqs_embedding_queue: String,
    pub sqs_content_queue: String,
    pub bedrock_region: String,
    pub bedrock_model_strategist: String,
    pub bedrock_model_fast: String,
    pub clerk_jwks_url: String,
    pub clerk_issuer: String,
    pub clerk_audience: Option<String>,
    pub clerk_webhook_secret: Option<String>,
    pub razorpay_key_id: String,
    pub razorpay_key_secret: String,
    pub razorpay_webhook_secret: Option<String>,
    pub resend_api_key: String,
    pub resend_from_email: String,
    pub resend_webhook_secret: Option<String>,
    pub webhook_timestamp_tolerance_seconds: u64,
    pub sentry_dsn: String,
    pub searxng_url: String,
    pub search_cache_ttl_secs: u64,
    pub search_max_results: usize,
}

impl Settings {
    pub fn validate(&self) -> Result<()> {
        if self.app_env != "prod" {
            return Ok(());
        }

        fn nonempty(name: &str, value: &str) -> Result<()> {
            if value.is_empty() {
                return Err(anyhow!("{} must be non-empty in prod", name));
            }
            Ok(())
        }

        fn valid_url(name: &str, value: &str) -> Result<()> {
            if value.is_empty() {
                return Err(anyhow!("{} must be non-empty in prod", name));
            }
            if !value.starts_with("https://") {
                return Err(anyhow!("{} must be a valid https URL in prod", name));
            }
            Ok(())
        }

        nonempty("RAPTORFLOW_FRONTEND_URL", &self.frontend_url)?;
        nonempty("RAPTORFLOW_DATABASE_URL", &self.database_url)?;
        if !self.database_url.starts_with("postgres") {
            return Err(anyhow!(
                "RAPTORFLOW_DATABASE_URL must be a postgres URL in prod"
            ));
        }
        nonempty("RAPTORFLOW_DIRECT_DATABASE_URL", &self.direct_database_url)?;
        if !self.direct_database_url.starts_with("postgres") {
            return Err(anyhow!(
                "RAPTORFLOW_DIRECT_DATABASE_URL must be a postgres URL in prod"
            ));
        }

        let example_issuer = "https://example.clerk.accounts.dev";
        if self.clerk_issuer.is_empty() || self.clerk_issuer == example_issuer {
            return Err(anyhow!(
                "RAPTORFLOW_CLERK_ISSUER must be set to a real Clerk issuer in prod"
            ));
        }
        valid_url("RAPTORFLOW_CLERK_JWKS_URL", &self.clerk_jwks_url)?;
        nonempty("RAPTORFLOW_BEDROCK_REGION", &self.bedrock_region)?;
        nonempty(
            "RAPTORFLOW_BEDROCK_MODEL_STRATEGIST",
            &self.bedrock_model_strategist,
        )?;
        nonempty("RAPTORFLOW_BEDROCK_MODEL_FAST", &self.bedrock_model_fast)?;
        nonempty("RAPTORFLOW_RAZORPAY_KEY_ID", &self.razorpay_key_id)?;
        nonempty("RAPTORFLOW_RAZORPAY_KEY_SECRET", &self.razorpay_key_secret)?;
        nonempty("RAPTORFLOW_RESEND_API_KEY", &self.resend_api_key)?;
        nonempty("RAPTORFLOW_S3_BUCKET", &self.s3_bucket)?;
        nonempty("RAPTORFLOW_SQS_BASE_URL", &self.sqs_base_url)?;

        Ok(())
    }

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
            qdrant_url: read("RAPTORFLOW_QDRANT_URL", "http://localhost:6333"),
            qdrant_api_key: optional("RAPTORFLOW_QDRANT_API_KEY")
                .or_else(|| optional("QDRANT_API_KEY")),
            s3_bucket: read("RAPTORFLOW_S3_BUCKET", "raptorflow-dev"),
            sqs_base_url: read(
                "RAPTORFLOW_SQS_BASE_URL",
                "https://sqs.ap-south-1.amazonaws.com",
            ),
            sqs_embedding_queue: read("RAPTORFLOW_SQS_EMBEDDING_QUEUE", "raptorflow-dev-embedding"),
            sqs_content_queue: read(
                "RAPTORFLOW_SQS_CONTENT_QUEUE",
                "raptorflow-dev-content-pregeneration",
            ),
            bedrock_region: read("RAPTORFLOW_BEDROCK_REGION", "ap-south-1"),
            bedrock_model_strategist: read(
                "RAPTORFLOW_BEDROCK_MODEL_STRATEGIST",
                "mistral.mistral-large-3-675b-instruct",
            ),
            bedrock_model_fast: read(
                "RAPTORFLOW_BEDROCK_MODEL_FAST",
                "mistral.ministral-3-8b-instruct",
            ),
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
            sentry_dsn: optional("RAPTORFLOW_SENTRY_DSN")
                .or_else(|| optional("SENTRY_DSN"))
                .unwrap_or_default(),
            searxng_url: read(
                "RAPTORFLOW_SEARXNG_URL",
                "http://localhost:8081",
            ),
            search_cache_ttl_secs: read("RAPTORFLOW_SEARCH_CACHE_TTL_SECS", "300")
                .parse()
                .unwrap_or(300),
            search_max_results: read("RAPTORFLOW_SEARCH_MAX_RESULTS", "10")
                .parse()
                .unwrap_or(10),
        })
    }
}

fn read(name: &str, default: &str) -> String {
    env::var(name).unwrap_or_else(|_| default.to_string())
}

fn optional(name: &str) -> Option<String> {
    env::var(name).ok().filter(|value| !value.trim().is_empty())
}
