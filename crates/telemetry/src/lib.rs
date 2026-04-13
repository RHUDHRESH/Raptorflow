//! Tracing/telemetry initialisation for RaptorFlow services.
//!
//! Sets up [`tracing_subscriber`] with JSON formatting, target visibility,
//! thread IDs, and thread names. Called once at service startup.
//!
//! ## Output
//!
//! JSON logs to stdout, filterable by `RUST_LOG` env var.

use anyhow::Result;
use tracing_subscriber::{EnvFilter, fmt};

pub fn init(service_name: &str) -> Result<()> {
    let filter = EnvFilter::try_from_default_env().unwrap_or_else(|_| EnvFilter::new("info"));

    let _ = fmt()
        .with_env_filter(filter)
        .with_target(true)
        .with_thread_ids(true)
        .with_thread_names(true)
        .try_init();

    tracing::info!(service = service_name, "telemetry initialized");
    Ok(())
}
