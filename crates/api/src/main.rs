//! RaptorFlow API server entry point.
//!
//! This binary initialises the Axum HTTP server with all route modules wired in
//! via `raptorflow_http::create_router`. It bootstraps:
//!
//! - `Settings` from environment variables (via `raptorflow_config`)
//! - PostgreSQL connection pool (via `raptorflow_db`)
//! - AWS Bedrock inference client (via `raptorflow_aws`)
//! - Clerk JWT validation middleware (domain read from settings)
//! - The main router built in the `http` crate
//!
//! The server binds to `0.0.0.0:8080` in all environments. Configure the port
//! via the `APP_PORT` environment variable if needed.

use raptorflow_aws::bedrock::BedrockInferenceClient;
use raptorflow_config::Settings;
use raptorflow_db::PgPool;
use raptorflow_http::create_router;
use raptorflow_http::middleware::AppState;
use std::sync::Arc;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    eprintln!("[raptorflow-api] boot: start");
    tracing::info!("Starting RaptorFlow API server");

    dotenvy::dotenv().ok();
    eprintln!("[raptorflow-api] boot: env loaded");

    let settings = Arc::new(Settings::from_env()?);
    eprintln!("[raptorflow-api] boot: settings loaded");

    let _sentry_guard = raptorflow_telemetry::init(
        "raptorflow-api",
        Some(settings.sentry_dsn.as_str()),
        Some(settings.app_env.as_str()),
    )?;
    eprintln!("[raptorflow-api] boot: sentry ready");

    let db_pool = if settings.database_url.starts_with("postgres") {
        eprintln!("[raptorflow-api] boot: connecting database");
        let pool = PgPool::connect(&settings.database_url).await?;
        eprintln!("[raptorflow-api] boot: database connected");
        Some(Arc::new(pool))
    } else {
        tracing::warn!("Database URL not configured, running without database");
        None
    };

    let bedrock_client = match BedrockInferenceClient::new(&settings.bedrock_region).await {
        Ok(client) => {
            tracing::info!(
                region = %settings.bedrock_region,
                model_strategist = %settings.bedrock_model_strategist,
                model_fast = %settings.bedrock_model_fast,
                "Bedrock inference client ready"
            );
            Some(Arc::new(client))
        }
        Err(e) => {
            tracing::warn!("Bedrock client init failed: {e} — running without AI inference");
            None
        }
    };

    let clerk_domain = settings.clerk_issuer.clone();
    let state = AppState::new(db_pool, bedrock_client, clerk_domain, settings);
    eprintln!("[raptorflow-api] boot: state ready");

    let app = create_router(state);
    eprintln!("[raptorflow-api] boot: router ready");

    let listener = tokio::net::TcpListener::bind("0.0.0.0:8080")
        .await
        .expect("Failed to bind to port 8080");
    eprintln!("[raptorflow-api] boot: listener bound");

    tracing::info!("API server listening on 0.0.0.0:8080");
    eprintln!("[raptorflow-api] boot: serving");

    axum::serve(listener, app).await?;

    Ok(())
}
