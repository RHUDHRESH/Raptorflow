//! RaptorFlow API server entry point.
//!
//! This binary initialises the Axum HTTP server with all route modules wired in
//! via `raptorflow_http::create_router`. It bootstraps:
//!
//! - `Settings` from environment variables (via `raptorflow_config`)
//! - PostgreSQL connection pool (via `raptorflow_db`)
//! - AWS Bedrock inference client (via `raptorflow_aws`)
//! - Web search client (via `raptorflow_search`)
//! - Clerk JWT validation middleware (issuer + JWKS URL read from settings)
//! - The main router built in the `http` crate
//!
//! The server binds to the address configured via `RAPTORFLOW_BIND_ADDR`.

use raptorflow_aws::bedrock::BedrockInferenceClient;
use raptorflow_config::Settings;
use raptorflow_db::PgPool;
use raptorflow_http::create_router;
use raptorflow_http::middleware::AppState;
use raptorflow_search::SearchClient;
use std::sync::Arc;

#[tokio::main]
async fn main() -> anyhow::Result<()> {
    eprintln!("[raptorflow-api] boot: start");
    tracing::info!("Starting RaptorFlow API server");

    dotenvy::dotenv().ok();
    eprintln!("[raptorflow-api] boot: env loaded");

    let settings = Arc::new(Settings::from_env()?);
    eprintln!("[raptorflow-api] boot: settings loaded");

    if settings.app_env == "prod" {
        settings.validate()?;
        eprintln!("[raptorflow-api] boot: settings validated");
    }

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

    let bedrock_client = match BedrockInferenceClient::from_settings(settings.as_ref()).await {
        Ok(client) => {
            tracing::info!(
                region = %client.region(),
                model_strategist = %client.strategist_model(),
                model_fast = %client.fast_model(),
                "Bedrock inference client ready"
            );
            Some(Arc::new(client))
        }
        Err(e) => {
            tracing::warn!("Bedrock client init failed: {e} — running without AI inference");
            None
        }
    };

    let search_client = if !settings.searxng_url.is_empty()
        && settings.searxng_url != "http://localhost:8081"
    {
        let ttl = std::time::Duration::from_secs(settings.search_cache_ttl_secs);
        let client = SearchClient::searxng_with_ddg_fallback(settings.searxng_url.clone(), ttl)
            .expect("Failed to create SearchClient");
        tracing::info!(
            searxng_url = %settings.searxng_url,
            cache_ttl_secs = settings.search_cache_ttl_secs,
            "Web search client ready (SearXNG + DuckDuckGo fallback)"
        );
        Some(Arc::new(client))
    } else {
        let ttl = std::time::Duration::from_secs(settings.search_cache_ttl_secs);
        let client = SearchClient::duckduckgo_only(ttl).expect("Failed to create SearchClient");
        tracing::info!(
            "Web search client ready (DuckDuckGo only — set RAPTORFLOW_SEARXNG_URL for unlimited SearXNG)"
        );
        Some(Arc::new(client))
    };

    let state = AppState::new(db_pool, bedrock_client, search_client, settings.clone());
    eprintln!("[raptorflow-api] boot: state ready");

    let app = create_router(state);
    eprintln!("[raptorflow-api] boot: router ready");

    let listener = tokio::net::TcpListener::bind(settings.bind_addr.as_str())
        .await
        .expect("Failed to bind to configured address");
    eprintln!("[raptorflow-api] boot: listener bound");

    tracing::info!("API server listening on {}", settings.bind_addr);
    eprintln!("[raptorflow-api] boot: serving");

    axum::serve(listener, app).await?;

    Ok(())
}
